import os
import tempfile
from typing import List, AsyncGenerator
from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.services.vector_store import get_vector_store
from app.utils.config import settings

def get_llm(streaming: bool = False):
    if settings.MISTRAL_API_KEY:
        return ChatMistralAI(
            mistral_api_key=settings.MISTRAL_API_KEY,
            model=settings.LLM_MODEL,
            temperature=0.0, # low temperature for facts
            streaming=streaming
        )
    elif settings.GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_LLM_MODEL,
            temperature=0.0,
            streaming=streaming
        )
    else:
        raise ValueError("No LLM API key configured.")

async def process_pdf(file: UploadFile) -> int:
    """Process a PDF file, extract text, chunk, embed, and store in vector db."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Save uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file uploaded.")
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        if not docs:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")

        # Update metadata to include filename
        for doc in docs:
            doc.metadata["filename"] = file.filename
            
        # Chunking Strategy: RecursiveCharacterTextSplitter for logical splits
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)

        # Basic deduplication (in real production, we'd hash content or use doc IDs)
        # Here we just inject a chunk_id
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{file.filename}_p{chunk.metadata.get('page', 0)}_{i}"

        # Store in VectorDB
        vector_store = get_vector_store()
        vector_store.add_documents(chunks)
        
        return len(chunks)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(f"Source: {doc.metadata.get('filename')} (Page {doc.metadata.get('page', 'unknown')})\nContent: {doc.page_content}" for doc in docs)

def get_rag_chain(streaming: bool = False, filter_doc: str = None):
    vector_store = get_vector_store()
    
    search_kwargs = {"k": settings.RETRIEVAL_K}
    if filter_doc:
        search_kwargs["filter"] = {"filename": filter_doc}
        
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    
    # Prompt template with reasoning guidelines
    template = """You are a senior technical assistant. Use the following pieces of retrieved context to answer the question.
If you don't know the answer or the context doesn't contain the answer, say "I don't know based on the provided documents." Do not try to make up an answer.
Explain your reasoning clearly and concisely based ONLY on the provided sources.

Context:
{context}

Question: {question}

Answer:"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm(streaming=streaming)
    
    # We want to return both answer and sources, so we'll construct the chain manually
    # or return retriever output alongside llm output.
    return retriever, prompt, llm

async def query_rag(question: str, filter_doc: str = None) -> tuple[str, List[Document]]:
    retriever, prompt, llm = get_rag_chain(streaming=False, filter_doc=filter_doc)
    
    # Retrieve documents
    docs = retriever.invoke(question)
    
    # Create the chain for generation
    chain = (
        {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    answer = chain.invoke(question)
    return answer, docs

async def stream_query_rag(question: str, filter_doc: str = None) -> AsyncGenerator[str, None]:
    retriever, prompt, llm = get_rag_chain(streaming=True, filter_doc=filter_doc)
    
    docs = retriever.invoke(question)
    
    # First yield the sources as a JSON-like chunk if needed, or we can just stream text.
    # To keep the SSE simple, we stream the answer text. Sources might be handled via a custom format
    # but let's stick to standard text streaming. We'll prepend the sources info.
    
    sources_info = "SOURCES:\n"
    for d in docs:
         sources_info += f"- {d.metadata.get('filename')} (Page {d.metadata.get('page', 'N/A')})\n"
    
    # We can stream the source info first
    yield sources_info + "\nANSWER:\n"
    
    chain = (
        {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    async for chunk in chain.astream(question):
        yield chunk

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import time
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_astradb import AstraDBVectorStore
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import Document
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import json

load_dotenv()

app = FastAPI(title="PDF Q&A API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://10.21.3.66:8501"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configurations ---
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# --- Pydantic Models ---
class QuestionRequest(BaseModel):
    question: str
    collection_name: str = "pdf_docs"
    session_id: str = "default"

class DocumentUploadResponse(BaseModel):
    message: str
    collection_name: str
    chunks_count: int
    files_count: int

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- Global state for chat history ---
chat_histories = {}

# --- Retry Configuration ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError, TimeoutError))
)
def create_astra_db_connection(collection_name: str, embeddings_model: MistralAIEmbeddings):
    """Create AstraDB connection with retry logic for hibernation handling"""
    try:
        vector_store = AstraDBVectorStore(
            collection_name=collection_name,
            embedding=embeddings_model,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            token=ASTRA_DB_APPLICATION_TOKEN,   
        )
        # Test the connection by trying to access the collection
        vector_store.as_retriever()
        return vector_store
    except Exception as e:
        if "hibernate" in str(e).lower() or "connection" in str(e).lower():
            raise  # This will trigger the retry
        else:
            raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError, TimeoutError))
)
def add_documents_with_retry(vector_store: AstraDBVectorStore, documents: List[Document], ids: List[str]):
    """Add documents to AstraDB with retry logic"""
    try:
        vector_store.add_documents(documents=documents, ids=ids)
    except Exception as e:
        if "hibernate" in str(e).lower() or "connection" in str(e).lower():
            raise  # This will trigger the retry
        else:
            raise

# --- Helper Functions ---
def ensure_upload_dir() -> str:
    upload_dir = Path("/tmp/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    return str(upload_dir)

def load_docs_from_path(path: str) -> List[Document]:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        loader = PyPDFLoader(path)
        return loader.load()
    if suffix in (".docx",):
        loader = Docx2txtLoader(path)
        return loader.load()
    if suffix in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
        # Skip images on deployment environments where Tesseract isn't available
        return []
    return []

def intelligent_chunk_documents(documents: List[Document], strategy: str, embeddings_model: MistralAIEmbeddings, chunk_size: int, chunk_overlap: int) -> List[Document]:
    if strategy == "Semantic":
        try:
            from langchain.text_splitter import SemanticChunker
            semantic_splitter = SemanticChunker(embeddings_model, breakpoint_threshold_type="percentile")
            return semantic_splitter.split_documents(documents)
        except Exception:
            pass  # Fall back to recursive chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    )
    return splitter.split_documents(documents)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "PDF Q&A API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/upload-documents", response_model=DocumentUploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: str = "pdf_docs",
    chunk_strategy: str = "Recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """Upload and process documents"""
    try:
        upload_dir = ensure_upload_dir()
        saved_paths = []
        
        # Save uploaded files
        for file in files:
            filename = f"{uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_paths.append(file_path)
        
        # Clean up old files
        try:
            for old_file in Path(upload_dir).glob("*"):
                if old_file.is_file() and old_file.stat().st_mtime < (time.time() - 3600):
                    old_file.unlink()
        except Exception:
            pass

        # Load all documents
        all_docs = []
        for path in saved_paths:
            docs = load_docs_from_path(path)
            for doc in docs:
                doc.metadata = {**(doc.metadata or {}), "source": doc.metadata.get("source", path), "file_name": Path(path).name}
            all_docs.extend(docs)

        if not all_docs:
            raise HTTPException(status_code=400, detail="No text extracted from the uploaded files.")

        embeddings_model = MistralAIEmbeddings(model="mistral-embed")

        # Intelligent chunking
        chunked_docs = intelligent_chunk_documents(all_docs, chunk_strategy, embeddings_model, chunk_size, chunk_overlap)

        # Create AstraDB connection and add documents
        vector_store = create_astra_db_connection(collection_name, embeddings_model)
        uuids = [str(uuid4()) for _ in range(len(chunked_docs))]
        add_documents_with_retry(vector_store, chunked_docs, uuids)

        return DocumentUploadResponse(
            message=f"Successfully indexed {len(chunked_docs)} chunks from {len(files)} file(s)",
            collection_name=collection_name,
            chunks_count=len(chunked_docs),
            files_count=len(files)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about uploaded documents"""
    try:
        model = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0.4,
            max_retries=2,
        )
        embeddings_model = MistralAIEmbeddings(model="mistral-embed")
        
        # Create AstraDB connection
        vector_store = AstraDBVectorStore(
            collection_name="pdf_docs",
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            token=ASTRA_DB_APPLICATION_TOKEN,
            embedding=embeddings_model
        )
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4})

        # Create history-aware retriever
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(
            model, retriever, contextualize_q_prompt
        )

        # Create QA chain
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Keep answers concise and cite key phrases if helpful.\

        {context}"""
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

        # Create RAG chain
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # Create conversational chain
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        # Get response
        response = conversational_rag_chain.invoke(
            {"input": request.question}, 
            config={"configurable": {"session_id": request.session_id}}
        )

        # Extract sources from retrieved documents
        sources = []
        if "context" in response:
            # This would need to be implemented based on how you want to extract sources
            pass

        return QuestionResponse(
            answer=response["answer"],
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

@app.get("/collections")
async def list_collections():
    """List available collections"""
    try:
        embeddings_model = MistralAIEmbeddings(model="mistral-embed")
        # This would need to be implemented based on your AstraDB setup
        # For now, return a placeholder
        return {"collections": ["pdf_docs"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

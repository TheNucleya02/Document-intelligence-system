from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import time
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# --- Load environment variables ---
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

# --- FastAPI app ---
app = FastAPI(title="PDF Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Globals ---
chat_histories = {}
COLLECTION_NAME = "pdf_docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Models ---
class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

class DocumentUploadResponse(BaseModel):
    message: str
    chunks_count: int
    files_count: int

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- Helpers ---
def ensure_upload_dir() -> str:
    upload_dir = Path("./uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    return str(upload_dir)

def load_docs_from_path(path: str) -> List[Document]:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(path).load()
    if suffix == ".docx":
        return Docx2txtLoader(path).load()
    return []

def intelligent_chunk_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )
    return splitter.split_documents(documents)

def process_files(file_paths: List[str]):
    all_docs = []
    for path in file_paths:
        docs = load_docs_from_path(path)
        for doc in docs:
            doc.metadata = {
                **(doc.metadata or {}),
                "source": doc.metadata.get("source", str(path)),
                "file_name": Path(path).name,
            }
        all_docs.extend(docs)

    if not all_docs:
        return 0

    embeddings_model = MistralAIEmbeddings(model="mistral-embed")
    chunked = intelligent_chunk_documents(all_docs)

    persist_dir = f"./chroma_db/{COLLECTION_NAME}"
    os.makedirs(persist_dir, exist_ok=True)

    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings_model,
        persist_directory=persist_dir,
    )
    ids = [str(uuid4()) for _ in range(len(chunked))]
    vectordb.add_documents(documents=chunked, ids=ids)
    vectordb.persist()
    return len(chunked)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory()
    return chat_histories[session_id]

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "PDF Q&A API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/upload-documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        upload_dir = ensure_upload_dir()
        saved_paths = []

        for file in files:
            filename = f"{uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f_out:
                f_out.write(await file.read())
            saved_paths.append(file_path)

        chunks_added = process_files(saved_paths)

        return DocumentUploadResponse(
            message="Files processed and stored.",
            chunks_count=chunks_added,
            files_count=len(files),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process documents: {str(e)}")

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        model = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0.4,
            max_retries=2,
        )
        embeddings_model = MistralAIEmbeddings(model="mistral-embed")

        chroma_dir = f"./chroma_db/{COLLECTION_NAME}"
        if not os.path.isdir(chroma_dir):
            raise HTTPException(status_code=404, detail="No documents found. Please upload documents first.")

        # FIX: Specify the collection name when creating the vector store
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,  # This was missing!
            embedding_function=embeddings_model,
            persist_directory=chroma_dir,
        )
        
        # Verify the collection has documents
        try:
            collection = vector_store._collection
            doc_count = collection.count()
            if doc_count == 0:
                raise HTTPException(status_code=404, detail="No documents found in the collection. Please upload documents first.")
        except Exception as e:
            print(f"Warning: Could not verify document count: {e}")
        
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})

        # Contextualize question
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and the latest user question, formulate a standalone question that can be understood without the chat history. Do NOT answer the question, just reformulate it if needed."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(
            model, retriever, contextualize_q_prompt
        )

        # QA chain
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Keep the answer concise.\n\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        response = conversational_rag_chain.invoke(
            {"input": request.question},
            config={"configurable": {"session_id": request.session_id}},
        )

        # Extract source information from context documents
        sources = []
        if "context" in response:
            for doc in response["context"]:
                if hasattr(doc, 'metadata') and 'file_name' in doc.metadata:
                    sources.append(doc.metadata['file_name'])
        
        # Remove duplicates while preserving order
        sources = list(dict.fromkeys(sources))

        return QuestionResponse(answer=response["answer"], sources=sources)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/collections")
async def list_collections():
    chroma_dir = f"./chroma_db/{COLLECTION_NAME}"
    if os.path.isdir(chroma_dir):
        try:
            embeddings_model = MistralAIEmbeddings(model="mistral-embed")
            vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings_model,
                persist_directory=chroma_dir,
            )
            doc_count = vector_store._collection.count()
            return {"collections": [{"name": COLLECTION_NAME, "document_count": doc_count}]}
        except Exception as e:
            return {"collections": [{"name": COLLECTION_NAME, "document_count": "unknown", "error": str(e)}]}
    else:
        return {"collections": []}

@app.delete("/clear-documents")
async def clear_documents():
    """Clear all documents from the vector store"""
    try:
        chroma_dir = f"./chroma_db/{COLLECTION_NAME}"
        if os.path.isdir(chroma_dir):
            import shutil
            shutil.rmtree(chroma_dir)
            return {"message": "All documents cleared successfully"}
        else:
            return {"message": "No documents to clear"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
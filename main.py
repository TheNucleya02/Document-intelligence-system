import streamlit as st
import os
import time
from dotenv import load_dotenv
from uuid import uuid4
from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import MistralAIEmbeddings
from langchain_community.chat_models import ChatMistralAI
from langchain_community.vectorstores import AstraDB
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import Document
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests

load_dotenv()

# --- Configurations ---
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# --- Retry Configuration ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: st.warning(f"Database connection failed. Retrying in {retry_state.next_action.sleep} seconds... (Attempt {retry_state.attempt_number}/3)")
)
def create_astra_db_connection(collection_name: str, embeddings_model: MistralAIEmbeddings):
    """Create AstraDB connection with retry logic for hibernation handling"""
    try:
        vector_store = AstraDB(
            collection_name=collection_name,
            embedding=embeddings_model,
            api_endpoint=ASTRA_DB_API_ENDPOINT,
            token=ASTRA_DB_APPLICATION_TOKEN,
        )
        # Test the connection by trying to access the collection
        vector_store._collection.find_one()
        return vector_store
    except Exception as e:
        if "hibernate" in str(e).lower() or "connection" in str(e).lower():
            st.info("Database is hibernating. Waking it up...")
            raise  # This will trigger the retry
        else:
            st.error(f"Database error: {str(e)}")
            raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: st.warning(f"Database operation failed. Retrying in {retry_state.next_action.sleep} seconds... (Attempt {retry_state.attempt_number}/3)")
)
def add_documents_with_retry(vector_store: AstraDB, documents: List[Document], ids: List[str]):
    """Add documents to AstraDB with retry logic"""
    try:
        vector_store.add_documents(documents=documents, ids=ids)
    except Exception as e:
        if "hibernate" in str(e).lower() or "connection" in str(e).lower():
            st.info("Database hibernated during operation. Retrying...")
            raise  # This will trigger the retry
        else:
            st.error(f"Failed to add documents: {str(e)}")
            raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: st.warning(f"Retrieval failed. Retrying in {retry_state.next_action.sleep} seconds... (Attempt {retry_state.attempt_number}/3)")
)
def retrieve_with_retry(retriever, query: str):
    """Retrieve documents with retry logic"""
    try:
        return retriever.get_relevant_documents(query)
    except Exception as e:
        if "hibernate" in str(e).lower() or "connection" in str(e).lower():
            st.info("Database hibernated during retrieval. Retrying...")
            raise  # This will trigger the retry
        else:
            st.error(f"Retrieval error: {str(e)}")
            raise

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Document QnA (PDF, DOCX, Images)", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stButton>button {transition: all 0.3s ease;}
    .stButton>button:hover {background-color: #6c757d; color: white;}
    </style>
""", unsafe_allow_html=True)

# --- Helpers ---
def ensure_upload_dir() -> str:
    upload_dir = Path("/tmp/uploads")  # Use /tmp for Render compatibility
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
        st.warning(f"Image OCR not available for {Path(path).name}. Please convert to PDF/DOCX for text extraction.")
        return []
    return []


def intelligent_chunk_documents(documents: List[Document], strategy: str, embeddings_model: MistralAIEmbeddings, chunk_size: int, chunk_overlap: int) -> List[Document]:
    if strategy == "Semantic":
        try:
            from langchain.text_splitter import SemanticChunker
            semantic_splitter = SemanticChunker(embeddings_model, breakpoint_threshold_type="percentile")
            return semantic_splitter.split_documents(documents)
        except Exception:
            st.warning("Semantic chunking unavailable. Falling back to recursive chunking.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    )
    return splitter.split_documents(documents)

if 'vector_ready' not in st.session_state:
    st.session_state.vector_ready = False
if 'collection_name' not in st.session_state:
    st.session_state.collection_name = "doc_store"

# --- Sidebar Ingestion ---
st.sidebar.title("📄 Upload documents")
uploaded_files = st.sidebar.file_uploader(
    "Choose files (PDF, DOCX, images)",
    type=["pdf", "docx", "png", "jpg", "jpeg", "tif", "tiff", "bmp"],
    accept_multiple_files=True,
)

st.sidebar.subheader("Index settings")
st.session_state.collection_name = st.sidebar.text_input("Collection name", value=st.session_state.collection_name)
chunk_strategy = st.sidebar.selectbox("Chunking strategy", ["Recursive", "Semantic"], index=0)
chunk_size = st.sidebar.slider("Chunk size", min_value=300, max_value=2000, value=1000, step=50)
chunk_overlap = st.sidebar.slider("Chunk overlap", min_value=0, max_value=400, value=200, step=10)

if st.sidebar.button("Upload & Process") and uploaded_files:
    with st.spinner("Processing documents..."):
        upload_dir = ensure_upload_dir()
        saved_paths: List[str] = []
        for uf in uploaded_files:
            filename = f"{uuid4()}_{uf.name}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(uf.read())
            saved_paths.append(file_path)
        
        # Clean up old files to prevent disk space issues
        try:
            for old_file in Path(upload_dir).glob("*"):
                if old_file.is_file() and old_file.stat().st_mtime < (time.time() - 3600):  # 1 hour old
                    old_file.unlink()
        except Exception:
            pass  # Ignore cleanup errors

        # Load all documents
        all_docs: List[Document] = []
        for p in saved_paths:
            docs = load_docs_from_path(p)
            for d in docs:
                # Keep helpful metadata
                d.metadata = {**(d.metadata or {}), "source": d.metadata.get("source", p), "file_name": Path(p).name}
            all_docs.extend(docs)

        if not all_docs:
            st.error("No text extracted from the uploaded files.")
        else:
            embeddings_model = MistralAIEmbeddings(model="mistral-embed")

            # Intelligent chunking
            chunked_docs = intelligent_chunk_documents(all_docs, chunk_strategy, embeddings_model, chunk_size, chunk_overlap)

            # Create AstraDB connection with retry logic
            try:
                vector_store = create_astra_db_connection(st.session_state.collection_name, embeddings_model)
                
                uuids = [str(uuid4()) for _ in range(len(chunked_docs))]
                add_documents_with_retry(vector_store, chunked_docs, uuids)
                
                st.session_state.vector_ready = True
                st.success(f"Indexed {len(chunked_docs)} chunks from {len(uploaded_files)} file(s) into '{st.session_state.collection_name}'.")
            except Exception as e:
                st.error(f"Failed to process documents: {str(e)}")
                st.session_state.vector_ready = False

# --- Chat Section ---
st.title("📚 Ask Questions About Your Documents")
if st.session_state.vector_ready:
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_question = st.text_input("Your Question:", key="input")
    if st.button("Ask") and user_question:
        with st.spinner("Generating answer..."):
            try:
                model = ChatMistralAI(
                    model="mistral-large-latest",
                    temperature=0.4,
                    max_retries=2,
                )
                embeddings_model = MistralAIEmbeddings(model="mistral-embed")
                
                # Create AstraDB connection with retry logic
                vector_store = create_astra_db_connection(st.session_state.collection_name, embeddings_model)
                retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4})

                contextualize_q_system_prompt = """Given a chat history and the latest user question \
                which might reference context in the chat history, formulate a standalone question \
                which can be understood without the chat history. Do NOT answer the question, \
                just reformulate it if needed and otherwise return it as is."""
                contextualize_q_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", contextualize_q_system_prompt),
                        MessagesPlaceholder("chat_history"),
                        ("human", "{input}"),
                    ]
                )
                history_aware_retriever = create_history_aware_retriever(
                    model, retriever, contextualize_q_prompt
                )

                qa_system_prompt = """You are an assistant for question-answering tasks. \
                Use the following pieces of retrieved context to answer the question. \
                If you don't know the answer, just say that you don't know. \
                Keep answers concise and cite key phrases if helpful.\

                {context}"""
                qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", qa_system_prompt),
                        MessagesPlaceholder("chat_history"),
                        ("human", "{input}"),
                    ]
                )
                question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

                rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

                if 'lc_store' not in st.session_state:
                    st.session_state.lc_store = {}
                store = st.session_state.lc_store

                def get_session_history(session_id: str) -> BaseChatMessageHistory:
                    if session_id not in store:
                        store[session_id] = ChatMessageHistory()
                    return store[session_id]

                conversational_rag_chain = RunnableWithMessageHistory(
                    rag_chain,
                    get_session_history,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                    output_messages_key="answer",
                )

                response = conversational_rag_chain.invoke({"input": user_question}, config={"configurable": {"session_id": "abc123"}})
                st.session_state.chat_history.append((user_question, response["answer"]))
                
            except Exception as e:
                st.error(f"Failed to generate answer: {str(e)}")
                if "hibernate" in str(e).lower():
                    st.info("The database may be hibernating. Please try again in a moment.")

    for q, a in st.session_state.chat_history:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Bot:** {a}")
else:
    st.info("Please upload and process a PDF to start chatting.")

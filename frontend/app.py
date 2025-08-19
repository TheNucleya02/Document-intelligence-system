import streamlit as st
import requests
import json
from typing import List
import time

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change this to your backend URL

# Page setup
st.set_page_config(page_title="Document Q&A System", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stButton>button {transition: all 0.3s ease;}
    .stButton>button:hover {background-color: #6c757d; color: white;}
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'collection_name' not in st.session_state:
    st.session_state.collection_name = "pdf_docs"
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_documents(files: List, collection_name: str, chunk_strategy: str, chunk_size: int, chunk_overlap: int):
    """Upload documents to backend"""
    try:
        files_data = []
        for file in files:
            files_data.append(('files', (file.name, file.getvalue(), file.type)))
        
        data = {
            'collection_name': collection_name,
            'chunk_strategy': chunk_strategy,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap
        }
        
        response = requests.post(
            f"{BACKEND_URL}/upload-documents",
            files=files_data,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def ask_question(question: str, collection_name: str, session_id: str):
    """Ask question to backend"""
    try:
        data = {
            "question": question,
            "collection_name": collection_name,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/ask-question",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Question failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Question error: {str(e)}")
        return None

# Main UI
st.title("📚 Document Q&A System")

# Check backend health
if not check_backend_health():
    st.error("⚠️ Backend is not running. Please start the FastAPI backend first.")
    st.stop()

# Sidebar for document upload
st.sidebar.title("📄 Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Choose files (PDF, DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

st.sidebar.subheader("Index Settings")
st.session_state.collection_name = st.sidebar.text_input(
    "Collection name", 
    value=st.session_state.collection_name
)
chunk_strategy = st.sidebar.selectbox("Chunking strategy", ["Recursive", "Semantic"], index=0)
chunk_size = st.sidebar.slider("Chunk size", min_value=300, max_value=2000, value=1000, step=50)
chunk_overlap = st.sidebar.slider("Chunk overlap", min_value=0, max_value=400, value=200, step=10)

if st.sidebar.button("Upload & Process") and uploaded_files:
    with st.spinner("Processing documents..."):
        result = upload_documents(
            uploaded_files, 
            st.session_state.collection_name,
            chunk_strategy,
            chunk_size,
            chunk_overlap
        )
        
        if result:
            st.success(f"✅ {result['message']}")
            st.info(f"Collection: {result['collection_name']}")
            st.info(f"Chunks: {result['chunks_count']}, Files: {result['files_count']}")

# Main chat interface
st.subheader("💬 Ask Questions")

user_question = st.text_input("Your Question:", key="input")
if st.button("Ask") and user_question:
    with st.spinner("Generating answer..."):
        result = ask_question(
            user_question,
            st.session_state.collection_name,
            st.session_state.session_id
        )
        
        if result:
            st.session_state.chat_history.append((user_question, result["answer"]))
            st.success("Answer generated!")

# Display chat history
if st.session_state.chat_history:
    st.subheader(" Chat History")
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.expander(f"Q: {question[:50]}..." if len(question) > 50 else f"Q: {question}"):
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Answer:** {answer}")
            if st.button(f"Delete", key=f"delete_{i}"):
                st.session_state.chat_history.pop(i)
                st.rerun()

# Clear chat history
if st.session_state.chat_history and st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Document Q&A System | FastAPI Backend + Streamlit Frontend</p>
</div>
""", unsafe_allow_html=True)

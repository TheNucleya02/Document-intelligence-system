import streamlit as st
import requests
import json
from typing import List, Dict
import time
from datetime import datetime
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000"
ENDPOINTS = {
    "health": f"{API_BASE_URL}/health",
    "upload": f"{API_BASE_URL}/upload-documents",
    "ask": f"{API_BASE_URL}/ask-question",
    "collections": f"{API_BASE_URL}/collections",
    "clear": f"{API_BASE_URL}/clear-documents"
}

# Page configuration
st.set_page_config(
    page_title="PDF Q&A Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "api_status" not in st.session_state:
    st.session_state.api_status = None
if "document_count" not in st.session_state:
    st.session_state.document_count = 0

# Utility functions
def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(ENDPOINTS["health"], timeout=5)
        if response.status_code == 200:
            return True, "API is running"
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000"
    except Exception as e:
        return False, f"Error checking API: {str(e)}"

def get_collections_info():
    """Get information about collections"""
    try:
        response = requests.get(ENDPOINTS["collections"], timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"collections": []}
    except Exception as e:
        st.error(f"Error getting collections info: {str(e)}")
        return {"collections": []}

def upload_documents(files):
    """Upload documents to the API"""
    try:
        files_data = []
        for uploaded_file in files:
            files_data.append(("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)))
        
        response = requests.post(ENDPOINTS["upload"], files=files_data, timeout=60)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Upload failed with status code: {response.status_code}"
    except Exception as e:
        return False, f"Error uploading documents: {str(e)}"

def ask_question(question: str, session_id: str):
    """Ask a question to the API"""
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        
        response = requests.post(
            ENDPOINTS["ask"],
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.content else "Unknown error"
            return False, f"Question failed: {error_detail}"
    except Exception as e:
        return False, f"Error asking question: {str(e)}"

def clear_documents():
    """Clear all documents"""
    try:
        response = requests.delete(ENDPOINTS["clear"], timeout=10)
        if response.status_code == 200:
            return True, response.json()["message"]
        else:
            return False, "Failed to clear documents"
    except Exception as e:
        return False, f"Error clearing documents: {str(e)}"

# Main UI
def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>📚 PDF Q&A Assistant</h1>
            <p>Upload your documents and ask questions about their content</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        # API Status Check
        if st.button("🔄 Check API Status", key="check_status"):
            with st.spinner("Checking API status..."):
                status, message = check_api_status()
                st.session_state.api_status = (status, message)
        
        if st.session_state.api_status:
            status, message = st.session_state.api_status
            if status:
                st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Document Upload Section
        st.header("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF or DOCX files",
            accept_multiple_files=True,
            type=['pdf', 'docx'],
            help="Upload one or more PDF or DOCX files to ask questions about"
        )
        
        if uploaded_files and st.button("🚀 Process Documents", type="primary"):
            with st.spinner("Uploading and processing documents..."):
                success, result = upload_documents(uploaded_files)
                
                if success:
                    st.markdown(f"""
                        <div class="success-box">
                            ✅ Successfully processed {result['files_count']} files!<br>
                            📊 Created {result['chunks_count']} text chunks 
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.document_count = result['chunks_count'] # type: ignore
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">❌ {result}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Collections Info
        st.header("📊 Document Status")
        if st.button("📋 Refresh Status"):
            collections_info = get_collections_info()
            if collections_info.get("collections"):
                for collection in collections_info["collections"]:
                    if isinstance(collection, dict):
                        doc_count = collection.get("document_count", "unknown")
                        st.markdown(f"""
                            <div class="info-box">
                                📚 Collection: {collection.get("name", "Unknown")}<br>
                                📄 Documents: {doc_count}
                            </div>
                        """, unsafe_allow_html=True)
                        st.session_state.document_count = doc_count if isinstance(doc_count, int) else 0
                    else:
                        st.markdown(f"""
                            <div class="info-box">
                                📚 Collection: {collection}<br>
                                📄 Status: Active
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">📭 No documents uploaded yet</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Session Management
        st.header("🔄 Session")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 New Session"):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        
        # Danger Zone
        with st.expander("⚠️ Danger Zone", expanded=False):
            st.write("**Clear all uploaded documents**")
            if st.button("🗑️ Clear All Documents", type="secondary"):
                with st.spinner("Clearing documents..."):
                    success, message = clear_documents()
                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.document_count = 0
                        st.session_state.messages = []
                    else:
                        st.error(f"❌ {message}")
    
    # Main Chat Interface
    st.header("💬 Chat with your Documents")
    
    # Display document status
    if st.session_state.document_count > 0:
        st.markdown(f"""
            <div class="success-box">
                ✅ Ready to answer questions! {st.session_state.document_count} document chunks loaded.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="info-box">
                📤 Please upload some documents first to start asking questions.
            </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources if available
                if message["role"] == "assistant" and "sources" in message and message["sources"]:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.write(f"• {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents...", disabled=(st.session_state.document_count == 0)):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                success, result = ask_question(prompt, st.session_state.session_id)
                
                if success and isinstance(result, dict):
                    response = result.get("answer", "No answer received")
                    sources = result.get("sources", [])
                    
                    st.markdown(response)
                    
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.write(f"• {source}")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "sources": sources
                    })
                else:
                    error_message = f"❌ {result}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_message,
                        "sources": []
                    })

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            Built with ❤️ using Streamlit and FastAPI<br>
            Make sure your FastAPI server is running on <code>http://localhost:8000</code>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
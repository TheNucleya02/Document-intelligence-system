# 📚 PDF Q&A Assistant

A powerful document question-answering system that allows users to upload PDF and DOCX files and ask questions about their content using advanced AI technology. Built with FastAPI backend and Streamlit frontend.

## ✨ Features

### 🚀 **Core Functionality**
- **Multi-format Document Support**: Upload PDF and DOCX files
- **Intelligent Text Chunking**: Smart document segmentation for optimal retrieval
- **Conversational AI**: Ask follow-up questions with context awareness
- **Source Attribution**: Get references to specific documents that informed the answer
- **Session Management**: Maintain conversation history across interactions

### 🎯 **Advanced Capabilities**
- **Vector Database Storage**: Efficient document embedding using Chroma DB
- **Semantic Search**: Find relevant information using Mistral AI embeddings
- **RESTful API**: Well-documented FastAPI backend
- **Modern UI**: Intuitive Streamlit web interface
- **Real-time Processing**: Live document upload and processing feedback

### 🔧 **Technical Features**
- **Async Processing**: Non-blocking file uploads and queries
- **Error Handling**: Comprehensive error management and user feedback
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Monitoring**: API status checking and diagnostics
- **Scalable Architecture**: Modular design for easy extension

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐
│   Streamlit     │ ◄──────────────► │    FastAPI       │
│   Frontend      │                 │    Backend       │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Chroma DB      │
                                    │ Vector Storage   │
                                    └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Mistral AI     │
                                    │ Embeddings/LLM   │
                                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Mistral AI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TheNucleya02/Document-intelligence-system.git
   cd pdf-qa-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Edit .env file and add your MISTRAL_API_KEY
   ```

5. **Run the FastAPI backend**
   ```bash
   uvicorn main:app --reload
   ```

6. **Run the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```

7. **Open your browser**
   - FastAPI Docs: http://localhost:8000/docs
   - Streamlit App: http://localhost:8501

## 📋 Requirements

Create a `requirements.txt` file with:

```
fastapi
uvicorn
pydantic
python-multipart
python-dotenv
pypdf
langchain
langchain-community
langchain-text-splitters
langchain-mistralai
langchain-chroma
chromadb
tenacity
requests
streamlit
requests
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### API Configuration

The FastAPI backend runs on `http://localhost:8000` by default. Key endpoints:

- `GET /` - API status
- `GET /health` - Health check
- `POST /upload-documents` - Upload documents
- `POST /ask-question` - Ask questions
- `GET /collections` - View collections
- `DELETE /clear-documents` - Clear all documents

## 📖 Usage

### 1. Upload Documents
- Use the Streamlit interface to upload PDF or DOCX files
- Files are automatically processed and chunked
- Vector embeddings are created and stored

### 2. Ask Questions
- Type your question in the chat interface
- The system will search through your documents
- Get AI-generated answers with source references

### 3. Manage Sessions
- Each conversation has a unique session ID
- Start new sessions or clear chat history as needed
- Conversation context is maintained within sessions

## 🛠️ API Usage

### Upload Documents
```python
import requests

files = [('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf'))]
response = requests.post('http://localhost:8000/upload-documents', files=files)
print(response.json())
```

### Ask Question
```python
import requests

payload = {
    "question": "What is the main topic of the document?",
    "session_id": "unique-session-id"
}
response = requests.post('http://localhost:8000/ask-question', json=payload)
print(response.json())
```

## 📁 Project Structure
'''
Document-intelligence-system/
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── docker-compose.yml
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── README.md
'''

## 🔍 How It Works

1. **Document Upload**: Files are uploaded via the Streamlit interface
2. **Text Extraction**: PyPDF and docx2txt extract text from documents
3. **Chunking**: RecursiveCharacterTextSplitter creates manageable text chunks
4. **Embedding**: Mistral AI creates vector embeddings for each chunk
5. **Storage**: Chroma DB stores embeddings with metadata
6. **Query Processing**: User questions are embedded and matched against stored chunks
7. **Answer Generation**: Mistral AI generates answers using retrieved context
8. **Response**: Answer is returned with source attribution

## 🎨 Features Showcase

### Smart Document Processing
- Automatic file type detection
- Intelligent text chunking with overlap
- Metadata preservation for source tracking

### Advanced Search
- Semantic similarity search using vector embeddings
- Context-aware question reformulation
- Multi-document information synthesis

### User Experience
- Real-time upload progress
- Interactive chat interface
- Source document references
- Session management

## 🐛 Troubleshooting

### Common Issues

**API Connection Error**
- Ensure FastAPI server is running on port 8000
- Check if MISTRAL_API_KEY is properly set

**Upload Failures**
- Verify file formats (PDF, DOCX only)
- Check file size limitations
- Ensure sufficient disk space

**Empty Responses**
- Confirm documents were successfully uploaded
- Try rephrasing your question
- Check if the question relates to uploaded content

### Logs and Debugging

Enable debug mode in FastAPI:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
```

## 🚀 Docker

### Run the Application

1. **Clone the repository**
   ```bash
   git clone https://github.com/TheNucleya02/Document-intelligence-system.git
   cd Document-intelligence-system
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend (Streamlit): http://localhost:8501
   - Backend (FastAPI): http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Commands

```bash
# Run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Shell into container
docker-compose exec backend bash
docker-compose exec frontend bash

### Production Considerations

- Use a production WSGI server (Gunicorn + Uvicorn)
- Set up proper logging
- Configure environment-specific settings
- Implement authentication if needed
- Set up monitoring and health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** for providing powerful language models and embeddings
- **LangChain** for the excellent RAG framework
- **Chroma DB** for efficient vector storage
- **FastAPI** for the robust API framework
- **Streamlit** for the intuitive frontend framework

## 📞 Support

If you encounter any issues or have questions:

1. connect at kr.amanjha@gmail.com
2. Open an issue on GitHub
3. Review the API documentation at `/docs`

---

**Built with ❤️ using FastAPI, Streamlit, and Mistral AI**

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.api import router
from app.db.database import engine, Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Intelligence System",
    description="RAG-based Document Intelligence System",
    version="1.0.0"
)

# Include API Router
app.include_router(router, prefix="/api")

# Serve Frontend
# Create frontend directory if it doesn't exist
os.makedirs("frontend", exist_ok=True)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please create frontend/index.html"}

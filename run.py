#!/usr/bin/env python3
"""
Simple startup script for the PDF Q&A application
"""
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Starting PDF Q&A Application...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found. Please create one with your API keys:")
        print("   ASTRA_DB_API_ENDPOINT=your_endpoint")
        print("   ASTRA_DB_APPLICATION_TOKEN=your_token")
        print("   MISTRAL_API_KEY=your_key")
        print()
    
    # Start backend
    print("📡 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "backend.main:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        if check_backend():
            print("✅ Backend is running!")
            break
        time.sleep(1)
    else:
        print("❌ Backend failed to start")
        backend_process.terminate()
        return
    
    # Start frontend
    print("�� Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501", "--server.address", "localhost"
    ])
    
    print("\n🎉 Application is running!")
    print("📡 Backend: http://localhost:8000")
    print("🎨 Frontend: http://localhost:8501")
    print("\nPress Ctrl+C to stop both servers...")
    
    try:
        # Keep both processes running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()

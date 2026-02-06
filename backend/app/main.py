from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from uuid import uuid4
from app.api.routes import router
from app.api.auth import router as auth_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.logging import configure_logging, set_request_id, reset_request_id

configure_logging()

app = FastAPI(title="Document Intelligence API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(router)

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = set_request_id(request_id)
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)
    response.headers["X-Request-ID"] = request_id
    return response

# --------------------
# Minimal UI (static)
# --------------------
ui_dir = Path(__file__).resolve().parent / "static"
if ui_dir.exists():
    app.mount("/static", StaticFiles(directory=str(ui_dir)), name="static")

    @app.get("/login")
    async def login_page():
        return FileResponse(ui_dir / "login.html")

    @app.get("/")
    async def root_page():
        return FileResponse(ui_dir / "login.html")

    @app.get("/register")
    async def register_page():
        return FileResponse(ui_dir / "register.html")

    @app.get("/upload")
    async def upload_page():
        return FileResponse(ui_dir / "upload.html")

    @app.get("/chat")
    async def chat_page():
        return FileResponse(ui_dir / "chat.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

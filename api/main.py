from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.pipeline import run_pipeline
import uuid
import os

app = FastAPI(title="WAPEXP Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")

# frontend/ folder abhi is project mein maujood nahi — agar bina check ke
# mount karte to app startup pe hi crash ho jata (StaticFiles missing-dir error)
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def get_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    async def get_index():
        return {"status": "ok", "message": "WAPEXP Chatbot API is running. POST to /api/chat"}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        user_id = request.session_id or str(uuid.uuid4())
        reply = run_pipeline(user_id, request.message)
        return ChatResponse(reply=reply, session_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
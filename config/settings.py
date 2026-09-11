import os
from dotenv import load_dotenv

# .env file ka exact path do (config/.env) — taake yeh hamesha mil jaye,
# chahe tum kisi bhi folder se 'python app.py' chalao
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=_env_path)

class Config:
    # ========== MODELS ==========
    # llm_client.py Groq ke OpenAI-compatible endpoint ko hit karta hai.
    # NOTE: llama-3.3-70b-versatile ab Groq ke free/developer tier par
    # available nahi (Enterprise-only ho chuka hai) - isliye 404 aata tha.
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    # 🔥 CHANGE: BGE-M3 ki jagah E5-Large use karo (Rust ki zaroorat nahi)
    # (pehle yahan galti se "gemini-2.0-flash" tha jo embedding model hai hi nahi)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    # ========== PATHS ==========
    # Yeh automatically project root (wapexp-chatbot) dhoondh lega
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    CHROMA_PATH = os.path.join(BASE_DIR, "db", "vector_store")
    CHUNKS_JSONL_PATH = os.path.join(BASE_DIR, "data", "chunks", "chunks.jsonl")
    
    # ========== RETRIEVAL ==========
    TOP_K = 6                     # Kitne chunks retrieve karne hain
    SIMILARITY_THRESHOLD = 0.65   # Agar score is se kam to "I don't know"
    RRF_K = 60                    # Reciprocal Rank Fusion ka constant
    
    # ========== MEMORY ==========
    MAX_HISTORY = 4               # Last 4 exchanges yaad rakho
import os
import json
from src.retrieval.vector_store import get_collection, add_to_collection
from src.embeddings.embed_model import get_embedding_model
from config.settings import Config

def build_index():
    print("🚀 Building Vector Index...")
    
    # 1. Load chunks
    chunks_path = Config.CHUNKS_JSONL_PATH
    if not os.path.exists(chunks_path):
        print("❌ chunks.jsonl nahi mili! Pehle chunker.py chalao.")
        return
    
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    
    print(f"📂 Loaded {len(chunks)} chunks.")
    
    # 2. Prepare data
    ids = [str(i) for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    # 3. Generate embeddings
    print("⏳ Generating embeddings (bge-m3)...")
    model = get_embedding_model()
    embeddings = model.encode(documents, show_progress_bar=True)
    
    # 4. Store in ChromaDB
    collection = get_collection()
    add_to_collection(collection, ids, documents, metadatas, embeddings.tolist())
    
    print(f"🎉 Vector index ready! Total chunks: {len(chunks)}")
    print(f"📁 Saved at: {Config.CHROMA_PATH}")

if __name__ == "__main__":
    build_index()
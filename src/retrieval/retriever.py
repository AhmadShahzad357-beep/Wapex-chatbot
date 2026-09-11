"""
Pure vector-based retriever (ChromaDB + sentence-transformers embeddings).
hybrid_search.py isko keyword (BM25) search ke sath RRF mein combine karta hai.
"""

from src.retrieval.vector_store import get_query_collection
from src.embeddings.embed_model import get_embedding_model
from config.settings import Config

_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = get_embedding_model()
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        _collection = get_query_collection()
    return _collection


def vector_search(query: str, top_k: int = None):
    """
    Query ko embed karta hai aur ChromaDB se top_k similar chunks laata hai.
    Returns: [{"text": ..., "metadata": ..., "score": ...}, ...]
    """
    top_k = top_k or Config.TOP_K

    try:
        model = _get_model()
        collection = _get_collection()
    except Exception as e:
        print(f"⚠️ Vector search unavailable: {e}")
        return []

    if collection.count() == 0:
        return []

    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        similarity = 1 - dist  # chroma cosine distance -> similarity
        chunks.append({"text": doc, "metadata": meta, "score": similarity})

    return chunks
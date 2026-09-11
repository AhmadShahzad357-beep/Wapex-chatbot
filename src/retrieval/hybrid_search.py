"""
Hybrid search: Vector (semantic) search + BM25 (keyword) search ko
Reciprocal Rank Fusion (RRF) se combine karta hai — sirf semantic search se
behtar retrieval deta hai, khaas kar exact numbers/fees/names ke liye
(jahan keyword match zyada reliable hota hai).
"""

import json
import re

from rank_bm25 import BM25Okapi

from src.retrieval.retriever import vector_search
from config.settings import Config

_bm25 = None
_bm25_chunks = None


def _tokenize(text: str):
    return re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", text.lower())


def _load_bm25():
    """chunks.jsonl se BM25 index ek hi dafa banata hai aur cache karta hai."""
    global _bm25, _bm25_chunks
    if _bm25_chunks is not None:
        return

    chunks = []
    try:
        with open(Config.CHUNKS_JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
    except FileNotFoundError:
        print("⚠️ chunks.jsonl nahi mili, BM25 keyword search disable rahega.")
        _bm25_chunks = []
        return

    tokenized_corpus = [_tokenize(c["text"]) for c in chunks]
    _bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None
    _bm25_chunks = chunks


def _keyword_search(query: str, top_k: int):
    _load_bm25()
    if not _bm25_chunks or _bm25 is None:
        return []

    scores = _bm25.get_scores(_tokenize(query))
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    return [
        {
            "text": _bm25_chunks[i]["text"],
            "metadata": _bm25_chunks[i].get("metadata", {}),
            "score": float(scores[i]),
        }
        for i in ranked_indices
    ]


def hybrid_search(query: str, top_k: int = None):
    """
    Vector + keyword results ko RRF se merge karta hai.
    Returns: [{"text": ..., "metadata": ...}, ...] (top_k)
    """
    top_k = top_k or Config.TOP_K
    rrf_k = Config.RRF_K

    vector_results = vector_search(query, top_k=top_k * 2)
    keyword_results = _keyword_search(query, top_k=top_k * 2)

    rrf_scores = {}
    text_lookup = {}

    for rank, chunk in enumerate(vector_results):
        key = chunk["text"]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rrf_k + rank + 1)
        text_lookup[key] = chunk

    for rank, chunk in enumerate(keyword_results):
        key = chunk["text"]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rrf_k + rank + 1)
        text_lookup[key] = chunk

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return [text_lookup[key] for key, _ in ranked]
import chromadb
from config.settings import Config

def get_collection():
    client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
    # Agar collection pehle se hai toh delete karo (taake naye chunks add ho saken)
    try:
        client.delete_collection("wapex_docs")
    except:
        pass
    collection = client.create_collection("wapex_docs")
    return collection

def get_query_collection():
    """
    Query/retrieval ke waqt use karo — yeh get_collection() ki tarah collection
    ko delete nahi karta, sirf existing collection open karta hai.
    (get_collection() sirf build_index.py ke re-indexing step ke liye hai.)
    """
    client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
    return client.get_or_create_collection("wapex_docs")


def add_to_collection(collection, ids, documents, metadatas, embeddings):
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"✅ Added {len(ids)} chunks to ChromaDB")
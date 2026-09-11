from sentence_transformers import SentenceTransformer
from config.settings import Config

def get_embedding_model():
    return SentenceTransformer(Config.EMBEDDING_MODEL)
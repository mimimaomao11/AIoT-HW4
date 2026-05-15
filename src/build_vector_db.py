import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from preprocess import load_articles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "embeddings", "chroma_db")

MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading and chunking articles...")
chunks_with_metadata = load_articles()

print("Initializing ChromaDB...")
os.makedirs(CHROMA_DIR, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    client.delete_collection(name="insurance_kb")
    print("Deleted existing collection.")
except Exception:
    pass

sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)

collection = client.get_or_create_collection(
    name="insurance_kb",
    embedding_function=sentence_transformer_ef
)

print("Inserting documents into ChromaDB (embeddings generated automatically)...")
ids = [f"doc_{idx}" for idx, _ in enumerate(chunks_with_metadata)]
documents = [chunk for chunk, _ in chunks_with_metadata]
metadatas = [{"source": source} for _, source in chunks_with_metadata]

collection.add(ids=ids, documents=documents, metadatas=metadatas)

print(f"Successfully created ChromaDB collection 'insurance_kb' with {len(chunks_with_metadata)} documents.")
print(f"Database stored at: {CHROMA_DIR}")

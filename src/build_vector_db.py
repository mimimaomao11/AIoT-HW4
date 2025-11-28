# build_vector_db.py (關鍵修改)
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# 引入我們修改過的 preprocess 模組
from preprocess import load_articles

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")

MODEL_NAME = "all-MiniLM-L6-v2"

# 使用 preprocess.py 的函式來讀取並切分文章段落
print("Loading and chunking articles...")
chunks_with_metadata = load_articles()
documents = [item[0] for item in chunks_with_metadata] # 只取出段落內容來做 embedding
metadata = [item[1] for item in chunks_with_metadata] # 取出檔名等元數據

# 生成 embeddings
embed_model = SentenceTransformer(MODEL_NAME)
embeddings = embed_model.encode(documents, show_progress_bar=True, convert_to_numpy=True)

# 建立 FAISS
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# 存檔
os.makedirs(EMBEDDING_DIR, exist_ok=True)
faiss.write_index(index, os.path.join(EMBEDDING_DIR, "faiss_index.bin"))
# 將文字段落和元數據分開儲存
np.save(os.path.join(EMBEDDING_DIR, "texts.npy"), np.array(documents, dtype=object))
np.save(os.path.join(EMBEDDING_DIR, "metadata.npy"), np.array(metadata, dtype=object))
print("FAISS index, texts, and metadata saved.")

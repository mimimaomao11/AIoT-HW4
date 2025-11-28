# rag_engine.py
import os
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI

# -----------------------------
# 資料夾路徑
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")


# -----------------------------
# OpenAI client 初始化
# -----------------------------
@st.cache_resource
def get_openai_client():
    """初始化 OpenAI client，從 Streamlit secrets 讀取金鑰"""
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("請在 Streamlit Secrets 中設定 OPENAI_API_KEY")
        st.stop()
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# -----------------------------
# RAG Engine
# -----------------------------
class RAGEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.embedder = SentenceTransformer(model_name)
        self.index, self.documents, self.metadata = self._load_vector_db()

    def _load_vector_db(self):
        """從磁碟載入 FAISS 索引和相關資料"""
        faiss_index_path = os.path.join(EMBEDDING_DIR, "faiss_index.bin")
        texts_path = os.path.join(EMBEDDING_DIR, "texts.npy")
        metadata_path = os.path.join(EMBEDDING_DIR, "metadata.npy")

        if not all(os.path.exists(p) for p in [faiss_index_path, texts_path, metadata_path]):
            st.error("向量資料庫檔案不存在，請先執行 build_vector_db.py 來建立索引。")
            st.stop()

        index = faiss.read_index(faiss_index_path)
        documents = np.load(texts_path, allow_pickle=True)
        metadata = np.load(metadata_path, allow_pickle=True)
        return index, documents, metadata

    def retrieve_docs(self, query, top_k=3):
        """根據查詢檢索相關文件"""
        query_vec = self.embedder.encode([query])
        _, I = self.index.search(np.array(query_vec).astype("float32"), top_k)

        retrieved_docs = [str(self.documents[i]) for i in I[0]]
        retrieved_metadata = [str(self.metadata[i]) for i in I[0]]
        return retrieved_docs, retrieved_metadata


@st.cache_resource
def get_rag_engine():
    """快取 RAG 引擎，避免重複載入模型"""
    return RAGEngine()


# -----------------------------
# RAG 查詢函數
# -----------------------------
def generate_answer(query):
    rag_engine = get_rag_engine()
    client = get_openai_client()

    context_docs, context_metadata = rag_engine.retrieve_docs(query)
    context_text = "\n\n".join(context_docs)

    system_prompt = """你是一個名為「機車保險智多星」的AI助理。你的任務是根據提供的「參考資料」，用專業、親切且深入淺出的方式回答使用者的「問題」。請盡量詳細說明，並在適當的時候舉例。如果參考資料不足以回答問題，請誠實地回答「根據我所擁有的資料，目前無法回答這個問題，建議您洽詢專業的保險業務員喔。」"""

    user_prompt = f"""以下是我的問題以及相關的參考資料，請根據這些資料回答我的問題。

---[參考資料]---
{context_text}
---[參考資料]---

問題：「{query}」"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"呼叫 API 時發生錯誤: {e}"

    return answer

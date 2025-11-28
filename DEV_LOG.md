好的，這是為你準備的最終版本開發日誌，格式已經過優化，可以直接複製貼上到 GitHub 的 Markdown 文件（如 DEVELOPMENT_LOG.md 或直接作為你的 README.md 的一部分），確保排版不會跑掉。

🚀 機車保險知識型助手 (RAG + 本地 LLM) - 完整開發日誌
本文記錄了「機車保險知識型助手」專案從概念到最終部署就緒的完整開發與迭代過程。

1. 最終專案結構與技術棧

專案主題：機車保險知識型助手 。



目標：根據已建立的知識庫，提供正確、清晰、易理解的回答 。


介面：Streamlit.app 。


RAG 框架：純 Python 實現，避免 LangChain 版本衝突 。


知識來源：30 篇手動準備的機車保險文章（.txt 檔），用於確保知識庫穩定性 。




Embedding 模型：sentence-transformers/all-MiniLM-L6-v2 。



向量資料庫：FAISS 。



LLM 模型：公開、輕量化、非 Gated 的 3B GPTQ 模型（例如：TheBloke/guanaco-3B-GPTQ），適用於 Streamlit 線上部署 。




2. 開發階段與核心問題排查
2.1 階段 I：環境與爬蟲問題

初始程式碼結構：依照建議建立了 src/ 下的 crawler.py、preprocess.py、build_vector_db.py、rag_engine.py、app.py 結構 。


爬蟲失敗處理：


問題：src/crawler.py 無法成功爬取國泰產險網頁 。



原因：目標網頁使用 JavaScript 動態載入內容，單純的 requests + BeautifulSoup 無法擷取文章列表 。


解決方案：停止爬蟲，改為手動在 data/raw_html/ 中建立 30 篇示範文章（.txt 格式），確保知識來源穩定 。


Git 版本控制修正：

解決 git push 時的 rejected 錯誤，使用 git pull origin main 合併遠端變更後再推送 。

解決 fatal: refusing to merge unrelated histories 錯誤，使用 git pull origin main --allow-unrelated-histories 。

解決 Git 大檔案錯誤（GH001: Large files detected），透過更新 .gitignore 排除 /rag_env/ 並執行 git rm -r --cached rag_env 。

2.2 階段 II：LangChain 與 LLM 兼容性
移除 LangChain：


問題：遇到 ModuleNotFoundError: No module named 'langchain.text_splitter' 。



原因：LangChain 1.x 版本模組結構大改，導致舊版導入路徑失效 。



解決方案：放棄所有 LangChain 依賴，改用 純 Python + HuggingFace SentenceTransformer + FAISS 實現 RAG 流程 。

本地 LLM 選型與錯誤修正：


模型亂碼/重複輸出：小型中文 GPT2 模型無法理解長 RAG Prompt，導致生成亂碼或重複文本 。



解決方案：改用 ChatGLM-6B（後續替換為更穩定的公開 3B 模型）並強化 Prompt 。


AttributeError: ChatGLMTokenizer has no attribute vocab_size：


原因：ChatGLM 的自訂 Tokenizer 與 transformers 的標準 AutoTokenizer 或 pipeline 載入方式不兼容 。



解決方案：改用 公開、輕量化、標準載入 的 HuggingFace 模型（例如 3B GPTQ 系列），完全避開 ChatGLM 專屬的 tokenizer 錯誤 。



模型授權問題：嘗試載入 meta-llama/Llama-2-7b-chat-hf 等模型時，遭遇 401 Client Error: Unauthorized 。


解決方案：鎖定使用 **完全公開（Non-Gated）**的 3B GPTQ 模型，無需 Hugging Face 登入授權 。

FAISS 檢索錯誤：


問題：RAG Context 檢索到 requirements.txt 中的套件名稱，而非文章內容 。


解決方案：修正 src/build_vector_db.py，確保 只將文章內容 進行 Embedding 並儲存到 texts.npy 。


模型生成參數調整：將 pipeline 中的 max_length 替換為 max_new_tokens=300，避免長 RAG Prompt 導致的生成衝突 。


2.3 階段 III：部署與配置

API 金鑰配置：src/rag_engine.py 已從 Streamlit 的 st.secrets 改回依賴本地 .env 檔案 讀取 OPENAI_API_KEY，以利於本地開發流程 。


模型優化與額度問題：為解決 OpenAI API 呼叫失敗（Quota Exceeded），將模型呼叫從 gpt-3.5-turbo 升級為 gpt-4o-mini 。



最終文件：新增完整的 README.md 專案說明文件，詳細介紹功能、技術棧與執行步驟。

3. 專案文件與執行指南
3.1 檔案結構
Bash

HW4/
├── data/
│   └── raw_html/
├── embeddings/
│   ├── faiss_index.bin
│   └── texts.npy
├── src/
│   ├── preprocess.py
│   ├── build_vector_db.py
│   ├── rag_engine.py
│   └── app.py
├── .gitignore
└── requirements.txt
3.2 依賴套件 (requirements.txt)
Plaintext

# LLM (公開、輕量化模型，避免 401 錯誤)
torch>=2.1
transformers>=4.40
# RAG 核心
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4
numpy>=1.25.0
# Web 介面
streamlit>=1.26.0
# 其他 (視需要)
requests
beautifulsoup4
tiktoken
3.3 執行指令
安裝依賴：pip install -r requirements.txt

建立向量庫：python src/build_vector_db.py

啟動介面：streamlit run src/app.py

推送到 GitHub：

Bash

git pull origin main --allow-unrelated-histories
git push origin main

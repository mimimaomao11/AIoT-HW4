🚀 機車保險知識型助手 (RAG + 本地 LLM) - 開發日誌
1. 專案目標與最終技術棧

專案主題：機車保險知識型助手 。


目標：根據已建立的知識庫，結合 LLM 提供正確、清晰、易理解的回答 。


最終 LLM 模型：輕量化公開 3B GPTQ 模型（例如：TheBloke/guanaco-3B-GPTQ），以確保線上部署的可行性 。


Embedding 模型：sentence-transformers/all-MiniLM-L6-v2 。



向量資料庫：FAISS 。



RAG 框架：純 Python 實現，不依賴 LangChain 。


介面：Streamlit.app 。

2. 開發階段與核心問題解決
階段 I：環境與爬蟲問題

專案結構建立：初始化專案結構 HW4/，包含 data/、embeddings/ 和 src/ 資料夾 。



爬蟲失敗：嘗試使用 requests + BeautifulSoup 爬取國泰產險知識文章失敗（抓到 0 篇文章），因網站內容為 JavaScript 動態載入 。


知識來源替換：決定不再進行網頁爬蟲，改為使用 **30 篇手動準備的機車保險文章（.txt 檔）**作為知識來源 。



src/preprocess.py 和 src/build_vector_db.py 的讀取邏輯已修改為直接讀取 data/raw_html/ 下的 .txt 檔案 。



Git 大檔案追蹤：解決 git push 時發生的 GH001: Large files detected 錯誤 。


修正：更新 .gitignore 忽略 /rag_env/ 和 /venv/，並執行 git rm -r --cached rag_env 移除追蹤 。


Git 歷史衝突：解決 fatal: refusing to merge unrelated histories 錯誤，使用 git pull origin main --allow-unrelated-histories 成功強制合併 。

階段 II：LLM 與套件兼容性

LangChain 移除：為解決 ModuleNotFoundError: No module named 'langchain.text_splitter' 問題 ，決定移除 LangChain 。




原因：LangChain 1.x 版本模組結構大改，舊版 CharacterTextSplitter 路徑不再存在 。



FAISS 檢索修正：修正 build_vector_db.py，確保 embeddings/texts.npy 儲存的是正確的文章內容，而非專案依賴套件清單 。


問題：檢索結果曾出現套件名稱（如 streamlit, faiss-cpu），導致 RAG 回答錯誤 。

本地 LLM 選型與錯誤處理：


ChatGLM 問題：嘗試使用 ChatGLM-6B/int4，但持續遇到 AttributeError: ChatGLMTokenizer has no attribute vocab_size 錯誤 。



原因：ChatGLM 的自訂 Tokenizer 與 transformers 庫的 AutoTokenizer 不完全兼容 。


解決方案：放棄 ChatGLM 專用載入方法，改用 公開、標準 HuggingFace Pipeline 。


模型長度限制：為解決長 Prompt 導致的 ValueError: Input length of input_ids is... 警告 ，將 rag_engine.py 中的模型生成參數從 max_length=300 改為 max_new_tokens=150 。



階段 III：部署與最終配置

模型授權問題：嘗試使用 meta-llama/Llama-2-7b-chat-hf 等流行模型時，遭遇 401 Client Error: Unauthorized 錯誤 。


原因：該模型為 Gated Repository，需要 Hugging Face 登入授權 。


最終決定：模型鎖定為 公開、無 Gated 限制的輕量化 3B GPTQ 模型，確保 Streamlit 線上部署不會因授權失敗 。


API 金鑰配置：


src/rag_engine.py 已從 Streamlit 的 st.secrets 改回依賴本地 .env 檔案 讀取 OPENAI_API_KEY，以簡化本地開發流程 。

同時，為了解決 OpenAI 額度問題，模型呼叫已從 gpt-3.5-turbo 升級為 gpt-4o-mini 。


專案文件：新增完整的 README.md，詳細說明專案功能、技術棧與執行步驟 。

3. 專案結構與執行流程
3.1 檔案結構
Bash

HW4/
├── data/
│   └── raw_html/     # 30篇機車保險文章 .txt 檔案
├── embeddings/
│   ├── faiss_index.bin # FAISS 向量索引
│   └── texts.npy     # 檢索文本陣列
├── src/
│   ├── preprocess.py   # 文章分塊與清理 (純 Python)
│   ├── build_vector_db.py # 建立 FAISS 向量庫
│   ├── rag_engine.py   # RAG 核心邏輯 (檢索+LLM生成)
│   └── app.py        # Streamlit 互動介面
├── .gitignore          # 忽略虛擬環境、快取、模型等
└── requirements.txt    # 專案依賴套件清單
3.2 執行指令

安裝依賴：pip install -r requirements.txt 。


建立向量庫：python src/build_vector_db.py 。


啟動介面：streamlit run src/app.py 。

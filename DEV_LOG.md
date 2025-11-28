# 開發日誌

---

## 2025.11.28

### 新增
- 新增 `src/generate_new_article.py` 腳本，用於從國泰產險網站抓取指定的文章內容。
- 此腳本會自動將文章內容依 `<h3>` 標題切分成多個檔案，並儲存至 `data/raw_html/`。

### 變更
- 專案的知識來源已更新為關於「強制險與第三人責任險」的文章。

### 修正
- 由於從目標網站直接爬取內容不穩定，`src/generate_new_article.py` 腳本被重構。
- 新版本不再進行網路爬蟲，而是直接包含手動切分好的文章段落。
- 執行此腳本會將預先處理好的 `.txt` 檔案寫入 `data/raw_html/`，確保了知識庫來源的穩定性。

### 部署準備
- **程式碼審查**:
  - 為了準備線上部署，新增 `requirements.txt` 檔案，鎖定專案所有依賴套件，並使用 `faiss-cpu` 以符合 Streamlit Cloud 環境。
  - 為了安全性，修改 `src/rag_engine.py`，使其從 Streamlit 的 `st.secrets` 讀取 `OPENAI_API_KEY`，而不是將金鑰寫死在程式碼中。
- **版本控制與部署**:
  - 提供了將專案上傳到 GitHub 的完整指令教學。
  - 提供了將應用程式部署到 Streamlit Community Cloud 的詳細步驟，包含如何設定 Secrets。
- **專案文件與配置調整**:
  - 根據使用者要求，將 `src/rag_engine.py` 的金鑰讀取方式改回依賴本地的 `.env` 檔案，以簡化本地開發流程。
  - 新增了完整的 `README.md` 專案說明文件，詳細介紹了專案功能、技術棧、如何在本地端執行以及專案結構，方便後續維護與分享。
- **專案上傳**:
  - 提供了將專案上傳至指定 GitHub 儲存庫 (`https://github.com/mimimaomao11/AIoT-HW4`) 的完整 `git` 指令教學。
- **版本控制修正**:
  - 解決 `git push` 時發生的 `rejected` 錯誤。
  - 錯誤原因為遠端儲存庫含有本地不存在的提交。
  - 解決方案為先執行 `git pull origin main` 將遠端變更拉至本地合併，再執行 `git push origin main` 完成推送。
- **合併遠端歷史**:
  - 解決 `git pull` 時發生的 `fatal: refusing to merge unrelated histories` 錯誤。
  - 錯誤原因為本地與遠端的 Git 儲存庫有各自獨立的初始提交歷史。
  - 使用 `git pull origin main --allow-unrelated-histories` 指令強制合併兩個不相關的歷史，成功解決問題。

- **解決合併衝突 (Merge Conflict)**:
  - 在合併不相關歷史後，`README.md` 檔案發生內容衝突。
  - 手動編輯 `README.md`，移除 Git 自動產生的衝突標記 (`<<<<<<<`, `=======`, `>>>>>>>`)，並保留期望的專案說明內容。
  - 依序執行 `git add README.md` 將檔案標記為已解決，`git commit` 完成合併，最後 `git push` 成功將專案上傳。


- **解決合併衝突 (Merge Conflict)**:
  - 在合併不相關歷史後，`README.md` 檔案發生內容衝突。
  - 手動編輯 `README.md`，移除 Git 自動產生的衝突標記 (`<<<<<<<`, `=======`, `>>>>>>>`)，並保留期望的專案說明內容。
  - 依序執行 `git add README.md` 將檔案標記為已解決，`git commit` 完成合併，最後 `git push` 成功將專案上傳。


- **解決 Git 大檔案上傳失敗問題**:
  - `git push` 時發生 `GH001: Large files detected` 錯誤，原因是虛擬環境資料夾 (`rag_env`) 被加入版本控制。
  - 虛擬環境因體積龐大且與平台相關，不應納入版控。
  - **修正步驟**:
    1. 更新 `.gitignore` 檔案，加入 `/rag_env/` 和 `/venv/` 來忽略虛擬環境。
    2. 執行 `git rm -r --cached rag_env` 將已追蹤的虛擬環境從 Git 索引中移除。
    3. 提交變更後，成功將專案推送到 GitHub。



## 2025-11-28

**開發者:** Gemini Code Assist
**主題:** 解決 OpenAI API 超過額度 (Quota Exceeded) 的問題

### 問題描述

使用者回報在執行 RAG 專案 (`c:\Users\wawa8\Desktop\HW4\src\rag_engine.py`) 時，對 `gpt-3.5-turbo` 模型的 API 呼叫失敗，並顯示「超過額度」的錯誤。然而，使用者在另一個專案中使用相同的 API Key 卻可以正常運作。

### 分析與診斷

這個問題「同一個 Key 在 A 專案正常，在 B 專案卻報額度錯誤」通常有以下幾種可能原因：

1.  **模型存取權限不同**：您的 API Key 可能對於某些模型（例如較新的 `gpt-4o` 或 `gpt-4o-mini`）有存取權，但對於 `gpt-3.5-turbo` 的免費額度或組織存取權限剛好用完或有所限制。不同專案可能預設呼叫了不同的模型。
2.  **請求用量過大**：RAG 應用會將檢索到的文件 (`context_text`) 一併發送給 API。如果檢索出的上下文很長，會導致單次請求的 token 數量暴增，可能在短時間內就達到了您帳戶的每分鐘 token 限制 (TPM, Tokens-Per-Minute)，而被暫時阻擋。另一個專案的請求可能比較簡短，所以沒有觸發這個限制。
3.  **帳戶狀態**：您的 OpenAI 帳戶可能最近剛好用完了免費試用額度，或是綁定的付費方案出了問題。而另一個專案可能因為快取或其他原因，暫時還沒觸發到新的 API 呼叫。

綜合來看，最常見且最容易解決的是**更換一個成本效益更高、更新的模型**來嘗試。`gpt-4o-mini` 是 OpenAI 新推出的高性價比模型，速度快且能力優異，很適合用於這類問答場景。

### 解決方案與程式碼修改

我們將 `rag_engine.py` 中呼叫的 `gpt-3.5-turbo` 模型更換為 `gpt-4o-mini`。這通常能解決因為特定模型額度問題導致的錯誤。

**檔案:** `c:\Users\wawa8\Desktop\HW4\src\rag_engine.py`

```diff
--- a/c:/Users/wawa8/Desktop/HW4/src/rag_engine.py
+++ b/c:/Users/wawa8/Desktop/HW4/src/rag_engine.py
@@ -62,7 +62,7 @@
 
     try:
         response = client.chat.completions.create(
-            model="gpt-3.5-turbo",
+            model="gpt-4o-mini",
             messages=[
                 {"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}
```

### 後續步驟建議

1.  **套用修改**：將上述變更應用到您的 `rag_engine.py` 檔案中。
2.  **重新執行**：再次執行您的 Streamlit App (`app.py`) 並測試問答功能。
3.  **檢查 OpenAI 後台**：如果問題仍然存在，強烈建議您登入 OpenAI Platform，檢查您的帳戶用量 (Usage) 和帳單 (Billing) 狀態，確認是否有額度限制或付款問題。
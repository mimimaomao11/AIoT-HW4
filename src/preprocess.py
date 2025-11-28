import os
import re

# 自動定位到專案根目錄的 data/raw_html
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw_html")

def load_articles():
    chunks_with_metadata = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".txt"):
            path = os.path.join(DATA_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                text = clean_text(text)
                chunks = chunk_text(text) # 將文章切成段落
                for chunk in chunks:
                    chunks_with_metadata.append((chunk, fname)) # 儲存 (段落, 來源檔名)
    return chunks_with_metadata

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text, chunk_size=250, chunk_overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks

if __name__ == "__main__":
    chunks = load_articles()
    print(f"總共分成 {len(chunks)} 個段落。")
    if chunks:
        print("\n第一個段落範例：")
        print(f"內容: '{chunks[0][0]}'")
        print(f"來源: '{chunks[0][1]}'")

import os
import ollama
# 修正 DeprecationWarning：改用獨立的 langchain_ollama 套件來載入 Embeddings
from langchain_ollama import OllamaEmbeddings
# FAISS 和 TextLoader 目前仍由 langchain_community 提供，已修正原本的拼寫錯誤
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_file_paths():
    """
    讓使用者選擇 Markdown 檔案位置（支援多個檔案）
    優先嘗試使用 tkinter 開啟圖形化選擇視窗，若環境不支援則改用命令列輸入。
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw() # 隱藏主視窗
        file_paths = filedialog.askopenfilenames(
            title="請選擇 Markdown 檔案 (可多選)",
            filetypes=[("Markdown 檔案", "*.md"), ("所有檔案", "*.*")]
        )
        return list(file_paths)
    except Exception:
        # 如果在沒有 GUI 的環境（例如 Linux 伺服器），則退回使用命令列輸入
        print("無法開啟圖形化選擇視窗，請手動輸入。")
        # 修正為使用逗號分隔
        paths_input = input("請輸入 Markdown 檔案路徑（多個檔案請用逗號分隔）: ")
        return [p.strip() for p in paths_input.split(",") if p.strip()]

def main():
    try:
        # 1. 讓使用者選擇 md 檔案位置（可多個）
        file_paths = get_file_paths()
        if not file_paths:
            print("未選擇任何檔案，程式結束。")
            return

        documents = []    
        for path in file_paths: 
            if not os.path.exists(path): 
                print(f"警告：找不到檔案 {path}，將略過此檔案。") 
                continue 
            try: 
                # 加入 encoding="utf-8" 避免讀取中文時發生亂碼錯誤 
                loader = TextLoader(path, encoding="utf-8") 
                documents.extend(loader.load()) 
                print(f"成功載入：{path}") 
            except Exception as e: 
                print(f"讀取檔案 {path} 時發生錯誤：{e}")   
        
        if not documents: 
            print("沒有成功載入任何文件內容，程式結束。") 
            return

        # chunk_size=500 代表每塊大約500個字元
        # chunk_overlap=50 代表每塊之間保留50個字元的重疊，避免切斷上下文語意
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(documents)

        print("正在建立向量資料庫，請稍候...")  
        # 使用更新後的 OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")  
        db = FAISS.from_documents(split_docs, embeddings)

        query = input("\n請輸入您的問題(例如:如何學 Inkscape?): ")  
        if not query.strip():  
            query = "如何學 Inkscape?"

        try: 
            k_input = input("請輸入要檢索/產生的資料筆數（預設為 2): ") 
            k_num = int(k_input) if k_input.strip() else 2
        except ValueError: 
            print("輸入的筆數無效，將使用預設值 2。") 
            k_num = 2

        # 進行相似度搜尋（檢索）
        docs = db.similarity_search(query, k=k_num)

        # 7. 整理搜尋結果作為參考背景(Context)
        # 滿足需求：有資料才要換行，且最後一行不換行
        if docs: 
            context = "\n".join([d.page_content for d in docs]) 
        else: 
            context = "無相關參考資料。"

        # 8. 組合提示詞 (Prompt)
        prompt = f"根據以下文件回答問題：\n{context}\n\n問題：{query}"

        # 9. 呼叫 LLM 生成回答
        print("\n正在呼叫LLM生成回答，請稍候...")

        # 【重要修改】加入 stream=True，讓文字逐字輸出，解決「不知道是否還在執行」的疑慮
        response = ollama.chat(
            model="llama2",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        # 10. 輸出結果
        print("\n===產生結果===")  
        for chunk in response:  
            # 確保最後一行不換行（使用 end=""），並即時刷新輸出  
            print(chunk["message"]["content"], end="", flush=True)  
        print() # 程式結束前補一個換行，讓終端機畫面保持整潔

    except Exception as e:
        # 捕捉所有未預期的錯誤
        print(f"\n程式執行過程中發生錯誤：{e}")
        print("請檢查 Ollama 服務是否已啟動，以及模型（nomic-embed-text，llama2）是否已下載。")

if __name__ == "__main__": 
    main()

import os
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def compile_xelatex(tex_file, output_dir=".", log_file="compile.log"):
    try:
        # 確保輸出目錄存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # XeLaTeX 編譯命令
        command = [
            r"C:\texlive\2024\bin\windows\xelatex.exe",  # win11 不設 path
            "-synctex=1",
            "-interaction=nonstopmode",
            "-output-directory", output_dir,
            tex_file
        ]
        
        # 執行編譯命令
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        
        # 將輸出寫入日誌檔案
        with open(log_file, "w", encoding="utf-8") as log:
            log.write("標準輸出：\n")
            log.write(result.stdout)
            log.write("\n錯誤輸出：\n")
            log.write(result.stderr)
        
        # 打印編譯結果
        print("標準輸出：")
        print(result.stdout)
        print("錯誤輸出：")
        print(result.stderr)
        
        # 檢查是否成功
        if result.returncode == 0:
            print("編譯成功！日誌已保存到", log_file)
        else:
            print("編譯失敗，請檢查錯誤訊息。日誌已保存到", log_file)
    
    except FileNotFoundError:
        print("無法找到 xelatex，請確認已安裝並配置 PATH。")
    except Exception as e:
        print(f"發生錯誤：{e}")

def askfile_and_compile():
    # 使用 tkinter 開啟檔案選擇對話框
    Tk().withdraw()  # 隱藏主視窗
    tex_file = askopenfilename(
        title="選擇 .tex 檔案",
        filetypes=[("TeX files", "*.tex")]
    )
    
    if tex_file:
        print(f"已選擇檔案：{tex_file}")
        compile_xelatex(tex_file, output_dir=".", log_file=r".\compile.log")
    else:
        print("未選擇任何檔案。")

# 執行檔案選擇與編譯
askfile_and_compile()

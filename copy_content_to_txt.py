import tkinter as tk
from tkinter import filedialog
import os
import winreg
from markdown import markdown
from weasyprint import HTML
import tempfile
import PyPDF2
import locale  # 新增locale模組處理系統編碼

def get_desktop_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        path, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        return os.path.expandvars(path)
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Desktop")

def read_file_with_fallback(path):
    encodings = ['utf-8', 'big5', 'cp950', 'latin-1']
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def md_to_pdf(md_content, output_path):
    """Convert Markdown content to PDF"""
    html_content = markdown(md_content)
    HTML(string=html_content).write_pdf(output_path)

def process_pdf(pdf_path):
    """Process PDF file and return extracted text"""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# 主程序
if __name__ == "__main__":
    # === 新增編碼處理區塊 ===
    # 強制設定臨時目錄為ASCII路徑
    ascii_temp_dir = "C:\\PY_TEMP"
    os.makedirs(ascii_temp_dir, exist_ok=True)
    tempfile.tempdir = ascii_temp_dir
    
    # 設定系統環境編碼
    os.environ["FONTCONFIG_PATH"] = "C:\\Windows\\Fonts"  # 明確指定字型路徑
    if os.name == 'nt':
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # 強制使用UTF-8環境
    # ======================
    
    root = tk.Tk()
    root.withdraw()

    # 1. 读取 progaming.md
    progaming_path = r"rour_prompt_md_file_path"
    try:
        md_content = read_file_with_fallback(progaming_path)
        
        # 2. 转换为 PDF (临时文件)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name
            md_to_pdf(md_content, pdf_path)
        
        # 3. 处理 PDF
        pdf_content = process_pdf(pdf_path)
        os.unlink(pdf_path)  # 删除临时PDF
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        pdf_content = ""

    # 4. 选择用户文件
    source_file = filedialog.askopenfilename(title="選擇檔案")
    if not source_file:
        exit()
    
    # 5. 读取用户文件内容
    try:
        source_content = read_file_with_fallback(source_file)
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        source_content = ""

    # 6. 组合内容并写入桌面
    desktop_path = get_desktop_path()
    fyi_path = os.path.join(desktop_path, "fyi.txt")
    
    try:
        with open(fyi_path, 'w', encoding='utf-8') as f:
            f.write(pdf_content)  # 写入PDF处理后的文本
            f.write("\n\n" + "-"*50 + "\n\n")  # 分隔线
            f.write(source_content)  # 写入原始文件内容
        
        print(f"檔案已建立於桌面：{fyi_path}")
        print(f"內容結構: PDF處理文本 + 原始檔案內容")
    except Exception as e:
        print(f"檔案寫入失敗：{str(e)}")

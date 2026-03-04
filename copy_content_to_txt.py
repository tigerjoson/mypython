import tkinter as tk
from tkinter import filedialog
import os
import shutil
import winreg

def get_desktop_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        path, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        return os.path.expandvars(path)
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Desktop")

root = tk.Tk()
root.withdraw()

source_file = filedialog.askopenfilename(title="選擇檔案")
if not source_file:
    exit()

# 新增顯示完整路徑功能
print(f"您選擇的檔案完整路徑：{os.path.abspath(source_file)}")

desktop_path = get_desktop_path()
destination_file = os.path.join(desktop_path, "fyi.txt")

try:
    shutil.copy2(source_file, destination_file)
    print(f"檔案已複製至桌面：{destination_file}")
except Exception as e:
    print(f"複製失敗：{str(e)}")

import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog

# 1. 读取繁简体中文对照表
def load_conversion_table(csv_file):
    # 使用Pandas读取CSV文件
    df = pd.read_csv(csv_file)
    # 假设CSV文件有两列，分别为 'simplified' 和 'traditional'
    conversion_dict = pd.Series(df['繁體'].values, index=df['殘體']).to_dict()
    #print( pd.Series(df['殘體'].values))
    return conversion_dict

# 2. 读取文本文件
def load_text_file(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read()

# 3. 保存替换后的文本
def save_text_file(output_file, text):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)
# 主程序

def main():
    root = tk.Tk()
    root.geometry("300x200")
    root.title("請選擇支語檔")
    thefile = tk.filedialog.askopenfilename();
    newfile = re.sub(".txt","tran_chi.txt",thefile)
    csv_file = 'C:/..../繁體簡體.txt'  # 繁简体对照表的CSV文件路径
    txt_file = thefile            # 需要替换内容的文本文件路径
    output_file = newfile  # 输出文件路径

    # 加载对照表
    conversion_dict = load_conversion_table(csv_file)
    
    # 加载文本文件
    text = load_text_file(txt_file)
    
    # 替换文本中的词汇
    for  simplified,traditional in conversion_dict.items():
         text = text.replace(simplified,traditional)
         #print(simplified)
         print(traditional)
         #print(text)
         save_text_file(output_file, text)
       
    
    # 保存替换后的文本

    print("替换完成，输出文件为:", output_file)

main()

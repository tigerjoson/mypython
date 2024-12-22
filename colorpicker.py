import tkinter as tk
from tkinter import colorchooser
import pyperclip

#win11 copilot
def pick_color():
    color_code = colorchooser.askcolor(title="Choose a color")
    label.config(text=f"Selected Color: {color_code[1]}", bg=color_code[1])
    pyperclip.copy(color_code[1])

root = tk.Tk()
root.title("Color Picker")

label = tk.Label(root, text="Select a color", padx=20, pady=20)
label.pack(pady=20)

button = tk.Button(root, text="Pick a Color", command=pick_color)
button.pack(pady=20)

root.mainloop()
import tkinter as tk
from tkinter import filedialog
import os

def select_folder(title="Select Folder"):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_path

def select_file(title="Select File", filetypes=[("All Files", "*.*")]):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path

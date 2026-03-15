from tkinterdnd2 import TkinterDnD
import tkinter as tk
import os
import sys
from ui.main_window import MainWindow

def resource_path(relative):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.abspath(".")

    return os.path.join(base, relative)

def main():

    root = TkinterDnD.Tk()
    
    icon_path = resource_path("assets/icon.ico")
    root.iconbitmap(icon_path)
    
    root.title("Phần mềm nhập điểm")

    root.geometry("1100x650")

    app = MainWindow(root)

    root.mainloop()

if __name__ == "__main__":
    main()
from tkinterdnd2 import TkinterDnD
import tkinter as tk
from ui.main_window import MainWindow

def main():

    root = TkinterDnD.Tk()
    
    icon = tk.PhotoImage(file="assets/icon.png")
    root.iconphoto(True, icon)

    root.title("Phần mềm nhập điểm")

    root.geometry("1100x650")

    app = MainWindow(root)

    root.mainloop()

if __name__ == "__main__":
    main()
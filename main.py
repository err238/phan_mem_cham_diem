from tkinterdnd2 import TkinterDnD
from ui.main_window import MainWindow

def main():

    root = TkinterDnD.Tk()

    root.title("Student Grade Manager")

    root.geometry("1100x650")

    app = MainWindow(root)

    root.mainloop()

if __name__ == "__main__":
    main()
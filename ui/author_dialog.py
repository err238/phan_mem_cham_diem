import tkinter as tk

class AuthorDialog:

    def __init__(self, parent):

        win = tk.Toplevel(parent)

        win.title("Tác giả")

        win.geometry("350x200")

        tk.Label(
            win,
            text="Student Grade Manager",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            win,
            text="Tác giả: Phạm Hoàng Minh"
        ).pack()

        tk.Label(
            win,
            text="Email: your_email@example.com"
        ).pack()

        tk.Label(
            win,
            text="Version: 3.0"
        ).pack()

        tk.Label(
            win,
            text="© 2026"
        ).pack(pady=10)

        tk.Button(win, text="Đóng", command=win.destroy).pack()
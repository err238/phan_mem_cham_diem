import tkinter as tk

class AuthorDialog:

    def __init__(self, parent):

        win = tk.Toplevel(parent)

        win.title("Tác giả")

        win.geometry("350x360")

        tk.Label(
            win,
            text="Phần mềm nhập điểm",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Label(
            win,
            text="Version: alpha test"
        ).pack()
        
        tk.Label(
            win,
            text="◈>><<◈"
        ).pack()
        
        tk.Label(
            win,
            text="Tác giả: Phạm Hoàng Minh"
        ).pack()

        tk.Label(
            win,
            text="◈──────Keep in touch──────>>"
        ).pack()
        
        tk.Label(
            win,
            text="📧 phminh@hcmus.edu.vn"
        ).pack()
        
        tk.Label(
            win,
            text="🌐 https://ralathe.com"
        ).pack()
        
        tk.Label(
            win,
            text="▶️ https://www.youtube.com/@err238"
        ).pack()
        
        tk.Label(
            win,
            text="🐙 https://github.com/err238"
        ).pack()
        
        tk.Label(
            win,
            text="<<──────────────────◈"
        ).pack()

        tk.Label(
            win,
            text="© 2026 - 1 ngày tuyết rơi tháng 3"
        ).pack(pady=10)

        tk.Button(win, text="Đóng", command=win.destroy).pack()
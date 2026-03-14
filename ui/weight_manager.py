import tkinter as tk
from tkinter import ttk, messagebox
from core.validator import validate_weight
from core.config_service import save_weight


class WeightManager:

    def __init__(self, parent, weights, refresh_callback=None):

        self.weights = weights
        self.refresh_callback = refresh_callback

        self.win = tk.Toplevel(parent)
        self.win.title("Quản lý trọng số")
        self.win.geometry("350x320")

        self.create_ui()
        self.load_weights()

    def create_ui(self):

        self.tree = ttk.Treeview(
            self.win,
            columns=("Column", "Weight"),
            show="headings"
        )

        self.tree.heading("Column", text="Cột điểm")
        self.tree.heading("Weight", text="Trọng số")

        self.tree.column("Column", width=160)
        self.tree.column("Weight", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<Double-1>", self.edit_weight)

        self.sum_label = tk.Label(self.win, font=("Arial", 10, "bold"))
        self.sum_label.pack()

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Lưu",
            width=10,
            command=self.save
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Đóng",
            width=10,
            command=self.win.destroy
        ).pack(side="left")

    def load_weights(self):

        self.tree.delete(*self.tree.get_children())

        for col, w in self.weights.items():
            self.tree.insert("", tk.END, iid=col, values=(col, w))

        self.update_sum()

    def update_sum(self):

        total = sum(self.weights.values())

        text = f"Tổng trọng số: {total:.2f} / 1.0"

        color = "red" if total > 1 else "black"

        self.sum_label.config(text=text, fg=color)

    def edit_weight(self, event):

        row = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if column != "#2":
            return

        x, y, w, h = self.tree.bbox(row, column)

        value = self.tree.set(row, column)

        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)

        entry.insert(0, value)
        entry.focus()

        def save_edit(e=None):

            new = entry.get()

            if not validate_weight(new):

                messagebox.showerror("Error", "Trọng số phải từ 0 đến 1")
                entry.destroy()
                return

            weight = float(new)

            self.weights[row] = weight

            self.tree.set(row, column, new)

            entry.destroy()

            self.update_sum()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def save(self):

        total = sum(self.weights.values())

        if total != 1:

            messagebox.showwarning(
                "Warning",
                f"Tổng trọng số = {total:.2f} (không bằng 1)"
            )

        for col, w in self.weights.items():
            save_weight(col, w)

        if self.refresh_callback:
            self.refresh_callback()

        self.win.destroy()

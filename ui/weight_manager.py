import tkinter as tk
from tkinter import ttk, messagebox

from core.validator import validate_weight
from core.config_service import load_weights, save_weight, save_weights
from core.excel_io import save_excel

from ui.tooltip import create_tooltip


class WeightManager:

    def __init__(self, parent, excel_path, refresh_callback=None, df=None):

        self.excel_path = excel_path
        self.refresh_callback = refresh_callback
        self.df = df

        self.weights = load_weights(self.excel_path)

        self.win = tk.Toplevel(parent)
        self.win.title("Quản lý trọng số")
        self.win.geometry("350x380")

        self.create_ui()
        self.load_table()

    def create_ui(self):

        frame = tk.Frame(self.win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            frame,
            columns=("Column", "Weight"),
            show="headings"
        )

        self.tree.heading("Column", text="Cột điểm")
        self.tree.heading("Weight", text="Trọng số")

        self.tree.column("Column", width=200)
        self.tree.column("Weight", width=80)

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.edit_cell)

        self.sum_label = tk.Label(self.win, font=("Arial", 10, "bold"))
        self.sum_label.pack(pady=5)

        # ---- INPUT ADD COLUMN ----
        input_frame = tk.Frame(self.win)
        input_frame.pack(pady=5)

       # nhập cột điểm
        tk.Label(input_frame, text="Tên cột").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.col_entry = tk.Entry(input_frame, width=20)
        self.col_entry.grid(row=0, column=1, padx=5, pady=5)

        # Enter → nhảy sang trọng số
        self.col_entry.bind("<Return>", lambda e: self.weight_entry.focus())

        # nhập trọng số
        tk.Label(input_frame, text="Trọng số").grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.weight_entry = tk.Entry(input_frame, width=10)
        self.weight_entry.grid(row=0, column=3, padx=5, pady=5)

        self.weight_entry.bind("<Return>", self.add_column)

        # ---- BUTTONS ----
        btn = tk.Frame(self.win)
        btn.pack(pady=10)

        btn_add = tk.Button(
            btn,
            text="Thêm cột",
            width=10,
            command=self.add_column
        )
        btn_add.pack(side="left", padx=5)
        
        create_tooltip(btn_add, 'Thêm cột điểm và trọng số')

        btn_close = tk.Button(
            btn,
            text="Đóng",
            width=10,
            command=self.win.destroy
        )
        btn_close.pack(side="left")
        
        create_tooltip(btn_close, 'Đóng bảng trọng số')

        # tự nhảy đến cột weight luôn
        self.col_entry.focus()
        
        # xóa cột bằng delete
        self.tree.bind("<Delete>", self.delete_column)

        # Đổi tên cột
        self.tree.bind("<F2>", self.rename_column)


    def load_table(self):

        self.tree.delete(*self.tree.get_children())

        self.weights = load_weights(self.excel_path)

        for col, w in self.weights.items():

            self.tree.insert(
                "",
                tk.END,
                iid=col,
                values=(col, w)
            )

        self.update_sum()

    def update_sum(self):

        total = sum(self.weights.values())

        text = f"Tổng trọng số: {total:.2f} / 1.0"

        color = "red" if total > 1 else "black"

        self.sum_label.config(text=text, fg=color)

    def edit_cell(self, event):

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

                messagebox.showerror(
                    "Error",
                    "Trọng số phải từ 0 đến 1"
                )

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

        for col, w in self.weights.items():
            save_weight(self.excel_path, col, w)

        if self.refresh_callback:
            self.refresh_callback()

        self.win.destroy()


    def add_column(self, event=None):

        col = self.col_entry.get().strip()
        weight = self.weight_entry.get().strip()

        if col == "":
            return

        if not validate_weight(weight):

            messagebox.showerror(
                "Error",
                "Trọng số phải từ 0 đến 1"
            )
            return

        w = float(weight)

        self.weights[col] = w

        save_weight(self.excel_path, col, w)

        self.tree.insert(
            "",
            tk.END,
            iid=col,
            values=(col, w)
        )

        self.update_sum()

        self.col_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)

        self.col_entry.focus()
        
        # báo cho InputScoreDialog cập nhật
        if self.refresh_callback:
            self.refresh_callback()
        
        
    # xóa cột
    def delete_column(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        col = selected[0]

        if not messagebox.askyesno("Xóa", f"Xóa cột {col}?"):
            return

        if col in self.weights:
            del self.weights[col]

        self.tree.delete(col)

        if self.df is not None and col in self.df.columns:

            self.df.drop(columns=[col], inplace=True)

            save_excel(self.df, self.excel_path)

        save_weights(self.excel_path, self.weights)

        self.update_sum()

        if self.refresh_callback:
            self.refresh_callback()

    # đổi tên
    def rename_column(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        col = selected[0]

        x, y, w, h = self.tree.bbox(col, "#1")

        value = self.tree.set(col, "#1")

        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)

        entry.insert(0, value)
        entry.focus()

        def save_edit(e=None):

            new = entry.get().strip()

            if new == "":
                entry.destroy()
                return

            weight = self.weights[col]

            del self.weights[col]

            self.weights[new] = weight

            self.tree.delete(col)

            self.tree.insert(
                "",
                tk.END,
                iid=new,
                values=(new, weight)
            )

            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

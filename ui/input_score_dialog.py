import tkinter as tk
from tkinter import ttk, messagebox

from core.config_service import load_weights, save_weight
from core.validator import validate_score, validate_weight
from core.excel_io import save_excel

from ui.weight_manager import WeightManager
from ui.input_manager import InputManager
from ui.tooltip import create_tooltip


class InputScoreDialog:

    def __init__(self, parent, df, excel_path, refresh_callback=None):

        self.df = df
        self.excel_path = excel_path
        self.refresh_callback = refresh_callback

        self.weights = load_weights(self.excel_path)

        self.entered_students = set()

        self.win = tk.Toplevel(parent)
        self.win.title("Nhập điểm")

        w, h = 420, 320
        x = parent.winfo_rootx()
        y = parent.winfo_rooty()

        self.win.geometry(f"{w}x{h}+{x+80}+{y+80}")

        self.win.transient(parent)
        self.win.grab_set()

        self.create_ui()

        self.update_progress()
        self.update_weight_sum()

    def create_ui(self):

        frame = tk.Frame(self.win)
        frame.pack(pady=10)

        # ----- COLUMN -----
        tk.Label(frame, text="Cột điểm", width=12).grid(row=0, column=0)

        self.col_box = ttk.Combobox(frame, width=22)
        self.col_box.grid(row=0, column=1)

        self.column_manager = InputManager(
            self.col_box,
            list(self.weights.keys())
        )

        self.col_box.bind("<Return>", self.select_column)
        self.col_box.bind("<<ComboboxSelected>>", self.autofill_weight)

        # ----- WEIGHT -----
        tk.Label(frame, text="Trọng số", width=12).grid(row=1, column=0)

        self.weight_entry = tk.Entry(frame, width=24)
        self.weight_entry.grid(row=1, column=1)

        self.weight_entry.bind(
            "<Return>",
            lambda e: self.mssv_box.focus()
        )

        # ----- MSSV -----
        tk.Label(frame, text="MSSV", width=12).grid(row=2, column=0)

        self.mssv_box = ttk.Combobox(frame, width=22)
        self.mssv_box.grid(row=2, column=1)

        self.mssv_list = self.df["MSSV"].astype(str).tolist()

        self.mssv_manager = InputManager(
            self.mssv_box,
            self.mssv_list
        )

        self.mssv_box.bind("<Return>", self.check_student)
        self.mssv_box.bind("<<ComboboxSelected>>", self.check_student)

        # ----- NAME -----
        tk.Label(frame, text="Họ tên", width=12).grid(row=3, column=0)

        self.name_label = tk.Label(
            frame,
            text="",
            width=24,
            anchor="w"
        )

        self.name_label.grid(row=3, column=1)

        # ----- SCORE -----
        tk.Label(frame, text="Điểm", width=12).grid(row=4, column=0)

        self.score_entry = tk.Entry(frame, width=24)
        self.score_entry.grid(row=4, column=1)

        self.score_entry.bind("<Return>", self.save)

        # ----- PROGRESS -----
        self.progress_label = tk.Label(self.win)
        self.progress_label.pack()

        self.weight_sum_label = tk.Label(
            self.win,
            font=("Arial", 10, "bold")
        )

        self.weight_sum_label.pack()

        # ----- BUTTONS -----
        btn = tk.Frame(self.win)
        btn.pack(pady=10)

        btn_save = tk.Button(
            btn,
            text="Lưu",
            width=10,
            command=self.save
        )
        btn_save.pack(side="left", padx=5)
        
        create_tooltip(btn_save, 'Lưu điểm vào file excel')

        btn_weight = tk.Button(
            btn,
            text="Trọng số",
            width=10,
            command=self.open_weight_manager
        )
        btn_weight.pack(side="left", padx=5)
        
        create_tooltip(btn_weight, 'Mở bảng trọng số')

        btn_close = tk.Button(
            btn,
            text="Đóng",
            width=10,
            command=self.win.destroy
        )
        btn_close.pack(side="left")
        
        create_tooltip(btn_close, 'Đóng cửa sổ')

    def autofill_weight(self, event=None):

        column = self.col_box.get().strip()

        if column in self.weights:

            self.weight_entry.delete(0, tk.END)

            self.weight_entry.insert(
                0,
                str(self.weights[column])
            )

    def select_column(self, event=None):

        column = self.col_box.get().strip()

        if column in self.weights:

            self.autofill_weight()

            self.mssv_box.focus()

        else:

            self.weight_entry.delete(0, tk.END)

            self.weight_entry.focus()

    def check_student(self, event=None):

        mssv = self.mssv_box.get().strip()

        match = self.df[
            self.df["MSSV"].astype(str) == mssv
        ]

        if match.empty:

            messagebox.showerror(
                "Error",
                "MSSV không tồn tại"
            )

            return

        name = match.iloc[0]["HoTen"]

        self.name_label.config(text=name)

        self.score_entry.focus()

    def save(self, event=None):

        column = self.col_box.get().strip()
        mssv = self.mssv_box.get().strip()
        score_text = self.score_entry.get()

        if not validate_score(score_text):

            messagebox.showerror(
                "Error",
                "Điểm phải từ 0 đến 10"
            )

            return

        score = float(score_text)

        if column not in self.weights:

            weight_text = self.weight_entry.get()

            if not validate_weight(weight_text):

                messagebox.showerror(
                    "Error",
                    "Trọng số phải từ 0 đến 1"
                )

                return

            weight = float(weight_text)

            save_weight(
                self.excel_path,
                column,
                weight
            )

            self.weights = load_weights(self.excel_path)

            self.column_manager.set_values(
                list(self.weights.keys())
            )

            self.update_weight_sum()

        if column not in self.df.columns:

            self.df[column] = 0.0

        match = self.df[
            self.df["MSSV"].astype(str) == mssv
        ]

        if match.empty:

            messagebox.showerror(
                "Error",
                "MSSV không tồn tại"
            )

            return

        row_index = match.index[0]

        self.df.loc[row_index, column] = score

        self.entered_students.add(mssv)

        save_excel(self.df, self.excel_path)

        if self.refresh_callback:
            self.refresh_callback()

        self.mssv_box.set("")
        self.score_entry.delete(0, tk.END)

        self.name_label.config(text="")

        self.update_progress()

        self.mssv_box.focus()

    def update_progress(self):

        total = len(self.df)

        entered = len(self.entered_students)

        self.progress_label.config(
            text=f"Đã nhập: {entered} / {total}"
        )

    def update_weight_sum(self):

        total = sum(self.weights.values())

        text = f"Tổng trọng số: {total:.2f} / 1.0"

        color = "red" if total > 1 else "black"

        self.weight_sum_label.config(
            text=text,
            fg=color
        )

    def open_weight_manager(self):

        WeightManager(
            self.win,
            self.excel_path,
            self.after_weight_update,
            self.df
        )

    def after_weight_update(self):

        self.weights = load_weights(self.excel_path)

        self.column_manager.set_values(
            list(self.weights.keys())
        )

        self.update_weight_sum()

        if self.refresh_callback:
            self.refresh_callback()

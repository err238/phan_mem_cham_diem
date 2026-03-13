import tkinter as tk
from tkinter import ttk, messagebox

from core.config_service import load_weights, save_weight
from core.validator import validate_score
from core.excel_io import save_excel


class InputScoreDialog:

    def __init__(self, parent, df, excel_path):

        self.df = df
        self.excel_path = excel_path

        self.weights = load_weights()

        self.entered_students = set()

        self.win = tk.Toplevel(parent)
        self.win.title("Nhập điểm")
        self.win.geometry("420x300")

        self.create_ui()

    def create_ui(self):

        frame = tk.Frame(self.win)
        frame.pack(pady=10)

        # CỘT ĐIỂM (dropdown)
        tk.Label(frame, text="Cột điểm", width=12).grid(row=0, column=0)

        columns = list(self.weights.keys())

        self.col_box = ttk.Combobox(frame, values=columns, width=18)
        self.col_box.grid(row=0, column=1)

        self.col_box.bind("<<ComboboxSelected>>", self.autofill_weight)

        # TRỌNG SỐ
        tk.Label(frame, text="Trọng số", width=12).grid(row=1, column=0)

        self.weight_entry = tk.Entry(frame, width=20)
        self.weight_entry.grid(row=1, column=1)

        # MSSV
        tk.Label(frame, text="MSSV", width=12).grid(row=3, column=0)

        self.mssv_entry = tk.Entry(frame, width=20)
        self.mssv_entry.grid(row=3, column=1)

        self.mssv_entry.bind("<Return>", self.check_student)

        # HỌ TÊN
        tk.Label(frame, text="Họ tên", width=12).grid(row=4, column=0)

        self.name_label = tk.Label(frame, text="", width=20, anchor="w")
        self.name_label.grid(row=4, column=1)

        # ĐIỂM
        tk.Label(frame, text="Điểm", width=12).grid(row=5, column=0)

        self.score_entry = tk.Entry(frame, width=20)
        self.score_entry.grid(row=5, column=1)

        self.score_entry.bind("<Return>", self.save)

        # PROGRESS
        self.progress_label = tk.Label(self.win, text="")
        self.progress_label.pack()

        self.update_progress()

        # BUTTONS
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Lưu", width=10,
                  command=self.save).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Đóng", width=10,
                  command=self.win.destroy).pack(side="left")

    def autofill_weight(self, event=None):

        column = self.col_box.get().strip()

        if column in self.weights:

            weight = self.weights[column]

            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(weight))

    def check_student(self, event=None):

        mssv = self.mssv_entry.get().strip()

        match = self.df[self.df["MSSV"].astype(str) == mssv]

        if match.empty:

            messagebox.showerror("Error", "MSSV không tồn tại")
            return

        name = match.iloc[0]["HoTen"]

        self.name_label.config(text=name)

        self.score_entry.focus()

    def save(self, event=None):

        column = self.col_box.get().strip()
        mssv = self.mssv_entry.get().strip()
        score = self.score_entry.get()

        if column == "":
            messagebox.showerror("Error", "Chưa chọn cột điểm")
            return

        if not validate_score(score):
            messagebox.showerror("Error", "Điểm phải từ 0-10")
            return

        score = float(score)

        # kiểm tra trọng số
        if column not in self.weights:

            weight = self.weight_entry.get()

            try:
                weight = float(weight)
            except:
                messagebox.showerror("Error", "Trọng số không hợp lệ")
                return

            save_weight(column, weight)

            self.weights[column] = weight

            self.col_box["values"] = list(self.weights.keys())

        # tạo cột nếu chưa có
        if column not in self.df.columns:

            self.df[column] = 0.0

        self.df[column] = self.df[column].astype(float)

        match = self.df[self.df["MSSV"].astype(str) == mssv]

        if match.empty:
            messagebox.showerror("Error", "MSSV không tồn tại")
            return

        row_index = match.index[0]

        self.df.loc[row_index, column] = score

        self.entered_students.add(mssv)

        save_excel(self.df, self.excel_path)

        # reset input
        self.mssv_entry.delete(0, tk.END)
        self.score_entry.delete(0, tk.END)

        self.name_label.config(text="")

        self.update_progress()

        self.mssv_entry.focus()

    def update_progress(self):

        total = len(self.df)

        entered = len(self.entered_students)

        self.progress_label.config(
            text=f"Đã nhập: {entered} / {total}"
        )
import tkinter as tk
from tkinter import ttk, messagebox

from core.config_service import load_weights, save_weight
from core.validator import validate_score
from core.excel_io import save_excel


class InputScoreDialog:

    def __init__(self, parent, df, excel_path):

        self.df = df
        self.excel_path = excel_path
        self.input_dialog = None # lưu dialog để chỉ tạo 1 bảng duy nhất

        self.weights = load_weights()

        self.entered_students = set()

        self.win = tk.Toplevel(parent)
        self.win.title("Nhập điểm")

        width = 420
        height = 300

        # lấy vị trí cửa sổ chính
        x = parent.winfo_rootx()
        y = parent.winfo_rooty()

        # đặt dialog gần cửa sổ chính
        self.win.geometry(f"{width}x{height}+{x+80}+{y+80}")
                
        # người dùng không thể mở dialog khác
        self.win.transient(parent)
        self.win.grab_set()
        
        self.win.title("Nhập điểm")
        self.win.geometry("420x300")

        self.create_ui()

    def create_ui(self):

        frame = tk.Frame(self.win)
        frame.pack(pady=10)

        # CỘT ĐIỂM (dropdown)
        tk.Label(frame, text="Cột điểm", width=12).grid(row=0, column=0)

        columns = list(self.weights.keys())

        self.col_box = ttk.Combobox(
            frame,
            values=columns,
            width=18,
            state="normal"
        )
        # gõ phím thì tự động gắn chữ vào
        self.col_box.bind("<KeyRelease>", self.filter_columns)
        
        self.col_box.grid(row=0, column=1)

        self.col_box.bind("<<ComboboxSelected>>", self.autofill_weight)
        self.col_box.bind("<Return>", self.select_column) # dùng phím enter thay vì chọn

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
                  command=self.close).pack(side="left")
    
    # lọc danh sách
    def filter_columns(self, event=None):

        text = self.col_box.get().lower()

        if text == "":
            self.col_box["values"] = list(self.weights.keys())
            return

        filtered = [
            col for col in self.weights.keys()
            if text in col.lower()
        ]

        self.col_box["values"] = filtered

        # mở dropdown
        if filtered:
            self.col_box.event_generate("<Down>")
        
    def close(self):
        self.win.destroy()

    def autofill_weight(self, event=None):

        column = self.col_box.get().strip()

        if column in self.weights:

            weight = self.weights[column]

            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(weight))
            
    def select_first_column(self, event=None):

        values = self.col_box["values"]

        if not values:
            return

        # chọn giá trị đầu tiên
        column = values[0]

        self.col_box.set(column)

        # đóng dropdown
        self.win.focus()

        # autofill trọng số
        self.autofill_weight()

        # chuyển sang MSSV
        self.mssv_entry.focus()
            
    def select_column(self, event=None):

        column = self.col_box.get().strip()

        if column == "":
            return

        # autofill trọng số nếu có
        if column in self.weights:

            weight = self.weights[column]

            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(weight))

        # chuyển sang nhập MSSV
        self.mssv_entry.focus()

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
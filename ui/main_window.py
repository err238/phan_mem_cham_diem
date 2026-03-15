import tkinter as tk
import webbrowser # thêm link youtube hướng dẫn sử dụng phần mềm
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES

from ui.table_view import StudentTable
from ui.author_dialog import AuthorDialog
from ui.input_score_dialog import InputScoreDialog
from ui.tooltip import create_tooltip

from core.excel_io import load_excel, save_excel
from core.grade_calculator import calculate_total
from core.backup_service import backup_excel, set_backup_path
from core.config_service import load_weights
from core.last_file_service import load_recent_files, save_recent_file


class MainWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Phần mềm nhập điểm")
        
        self.create_menu()
        self.create_toolbar()
        self.create_search()

        self.table = StudentTable(root)
        self.table.pack(fill="both", expand=True)

        self.current_file = None
        self.input_dialog = None

        self.create_status()
        

        self.enable_drag_drop()

        files = load_recent_files()

        if files:
            try:
                self.load_file(files[0])
            except:
                pass

    def create_menu(self):

        menubar = tk.Menu(self.root)

        # -------- File menu --------
        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(
            label="Mở file excel",
            command=self.open_excel
        )

        self.recent_menu = tk.Menu(file_menu, tearoff=0)

        file_menu.add_cascade(
            label="File gần đây",
            menu=self.recent_menu
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Thoát",
            command=self.root.quit
        )

        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

        # -------- Tools menu --------
        tools_menu = tk.Menu(menubar, tearoff=0)

        tools_menu.add_command(
            label="Lưu",
            command=self.save_excel
        )
        
        tools_menu.add_command(
            label="Nhập điểm",
            command=self.open_input_score
        )

        tools_menu.add_command(
            label="Tính điểm TB",
            command=self.calculate_total
        )

        tools_menu.add_command(
            label="Thư mục Backup",
            command=self.choose_backup
        )

        menubar.add_cascade(
            label="Công cụ",
            menu=tools_menu
        )

        # -------- Help menu --------
        help_menu = tk.Menu(menubar, tearoff=0)

        help_menu.add_command(
            label="Hướng dẫn sử dụng (YouTube)",
            command=self.open_help_video
        )

        help_menu.add_separator()

        help_menu.add_command(
            label="Tác giả",
            command=self.show_author
        )

        menubar.add_cascade(label="Hỗ trợ", menu=help_menu)

        self.root.config(menu=menubar)
  
    def update_recent_menu(self):

        self.recent_menu.delete(0, tk.END)

        files = load_recent_files()

        if not files:

            self.recent_menu.add_command(
                label="(Empty)",
                state="disabled"
            )
            return

        for path in files:

            self.recent_menu.add_command(
                label=path,
                command=lambda p=path: self.load_file(p)
            )

    def create_toolbar(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        btn_open = tk.Button(
            frame,
            text="📂 Mở",
            command=self.open_excel
        )
        btn_open.pack(side="left", padx=2)
        
        create_tooltip(btn_open,'Mở file excel bạn muốn nhập điểm')

        btn_save = tk.Button(
            frame,
            text="💾 Lưu",
            command=self.save_excel
        )
        btn_save.pack(side="left", padx=2)
        
        create_tooltip(btn_save, 'Lưu file excel đang làm việc')

        btn_score = tk.Button(
            frame,
            text="✏ Nhập điểm",
            command=self.open_input_score
        )
        btn_score.pack(side="left", padx=2)
        
        create_tooltip(btn_score, 'Mở bảng nhập điểm')
        
        btn_meanscore = tk.Button(
            frame,
            text="🧮 Tính điểm TB",
            command=self.calculate_total
        )
        btn_meanscore.pack(side="left", padx=2)
        
        create_tooltip(btn_meanscore, 'Tính điểm trung bình khi trọng số đã bằng 1')

        btn_bk = tk.Button(
            frame,
            text="📦 Backup",
            command=self.choose_backup
        )
        btn_bk.pack(side="left", padx=2)
        
        create_tooltip(btn_bk, 'Nhập đường dẫn file backup')

        btn_author = tk.Button(
            frame,
            text="ℹ Tác giả",
            command=self.show_author
        )
        btn_author.pack(side="right", padx=2)
        
        create_tooltip(btn_author, 'Thông tin phần mềm')

    def create_search(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        tk.Label(frame, text="Tìm kiếm (MSSV hoặc Họ tên)").pack(side="left")

        self.search_var = tk.StringVar()

        entry = tk.Entry(
            frame,
            textvariable=self.search_var
        )

        entry.pack(side="left", padx=5)

        entry.bind("<KeyRelease>", self.do_search)

    def create_status(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        self.status_file = tk.Label(frame, text="Chưa có dữ liệu")
        self.status_file.pack(side="left", padx=5)

        self.status_students = tk.Label(frame, text="")
        self.status_students.pack(side="right", padx=5)

    # thanh trạng thái bên dưới
    def update_status(self):

        if self.current_file is None:
            return

        total = len(self.table.df)

        entered = 0

        # kiểm tra điểm >= 5
        if "TongKet" in self.table.df.columns:
            passed = (self.table.df["TongKet"] >= 5).sum()
        else:
            passed = 0

        percent = (entered / total * 100) if total else 0

        self.status_file.config(
            text=f"Loaded: {self.current_file}"
        )
        
        self.status_students.config(
            text=f"Số SV: {total} | SV trên TB: {passed}/{total} ({percent:.0f}%)"
        )

    def enable_drag_drop(self):

        self.root.drop_target_register(DND_FILES)

        self.root.dnd_bind("<<Drop>>", self.drop_file)

    def drop_file(self, event):

        path = event.data.strip("{}")

        if not path.endswith(".xlsx"):

            messagebox.showerror(
                "Error",
                "Kéo thả file excel (.xlsx)"
            )

            return

        self.load_file(path)

    def open_excel(self):

        path = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx")]
        )

        if path:
            self.load_file(path)

    def load_file(self, path):

        try:

            backup_excel(path)

            df = load_excel(path)

            self.table.load_dataframe(df, path)

            self.current_file = path

            save_recent_file(path)

            self.update_recent_menu()

            self.update_status()

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def save_excel(self):

        if self.table.df is None:
            return

        save_excel(self.table.df, self.current_file)

        self.status_file.config(text="Saved")

    def calculate_total(self):

        try:

            weights = load_weights(self.current_file)

            self.table.df = calculate_total(
                self.table.df,
                weights
            )

            self.table.refresh()

            self.update_status()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    def show_author(self):

        AuthorDialog(self.root)

    def do_search(self, event):

        keyword = self.search_var.get()

        self.table.search(keyword)

    def open_input_score(self):

        if self.table.df is None:
            return

        if self.input_dialog and self.input_dialog.win.winfo_exists():

            self.input_dialog.win.lift()
            self.input_dialog.win.focus_force()

            return

        self.input_dialog = InputScoreDialog(
            self.root,
            self.table.df,
            self.current_file,
            self.table.refresh
        )

    def choose_backup(self):

        folder = filedialog.askdirectory()

        if folder:
            set_backup_path(folder)
            
    # Tạo nút hướng dẫn
    def open_help_video(self):

        url = "https://www.youtube.com/@err238"

        webbrowser.open(url)


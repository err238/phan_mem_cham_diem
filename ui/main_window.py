import tkinter as tk
import webbrowser # thêm link youtube hướng dẫn sử dụng phần mềm
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES

from ui.table_view import StudentTable
from ui.author_dialog import AuthorDialog
from ui.input_score_dialog import InputScoreDialog

from core.excel_io import load_excel, save_excel
from core.grade_calculator import calculate_total
from core.backup_service import backup_excel, set_backup_path
from core.config_service import load_weights

from core.last_file_service import load_recent_files, save_recent_file


class MainWindow:

    def __init__(self, root):

        self.root = root
        self.root.title("Student Grade Manager")
        
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
            label="Open Excel",
            command=self.open_excel
        )

        self.recent_menu = tk.Menu(file_menu, tearoff=0)

        file_menu.add_cascade(
            label="Recent Files",
            menu=self.recent_menu
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.root.quit
        )

        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

        # -------- Tools menu --------
        tools_menu = tk.Menu(menubar, tearoff=0)

        tools_menu.add_command(
            label="Save",
            command=self.save_excel
        )

        tools_menu.add_command(
            label="Calculate Total",
            command=self.calculate_total
        )

        tools_menu.add_command(
            label="Nhập điểm",
            command=self.open_input_score
        )

        tools_menu.add_command(
            label="Backup Folder",
            command=self.choose_backup
        )

        menubar.add_cascade(
            label="Tools",
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

        menubar.add_cascade(label="Help", menu=help_menu)

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

        tk.Button(
            frame,
            text="📂 Open",
            command=self.open_excel
        ).pack(side="left", padx=2)

        tk.Button(
            frame,
            text="💾 Save",
            command=self.save_excel
        ).pack(side="left", padx=2)

        tk.Button(
            frame,
            text="🧮 Calculate",
            command=self.calculate_total
        ).pack(side="left", padx=2)

        tk.Button(
            frame,
            text="✏ Nhập điểm",
            command=self.open_input_score
        ).pack(side="left", padx=2)

        tk.Button(
            frame,
            text="📦 Backup",
            command=self.choose_backup
        ).pack(side="left", padx=2)

        tk.Button(
            frame,
            text="ℹ Tác giả",
            command=self.show_author
        ).pack(side="right", padx=2)

    def create_search(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        tk.Label(frame, text="Search").pack(side="left")

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

        self.status_file = tk.Label(frame, text="No file loaded")
        self.status_file.pack(side="left", padx=5)

        self.status_students = tk.Label(frame, text="")
        self.status_students.pack(side="right", padx=5)

    def update_status(self):

        if self.current_file is None:
            return

        total = len(self.table.df)

        entered = 0

        if "Total" in self.table.df.columns:
            entered = self.table.df["Total"].count()

        percent = (entered / total * 100) if total else 0

        self.status_file.config(
            text=f"Loaded: {self.current_file}"
        )

        self.status_students.config(
            text=f"Students: {total} | Progress: {entered}/{total} ({percent:.0f}%)"
        )

    def enable_drag_drop(self):

        self.root.drop_target_register(DND_FILES)

        self.root.dnd_bind("<<Drop>>", self.drop_file)

    def drop_file(self, event):

        path = event.data.strip("{}")

        if not path.endswith(".xlsx"):

            messagebox.showerror(
                "Error",
                "Drop file Excel (.xlsx)"
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


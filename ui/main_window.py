import tkinter as tk
from tkinter import filedialog,messagebox
from tkinterdnd2 import DND_FILES

from ui.table_view import StudentTable
from ui.author_dialog import AuthorDialog

from core.excel_io import load_excel,save_excel
from core.grade_calculator import calculate_total
from core.backup_service import backup_excel
from core.config_service import load_weights

from ui.input_score_dialog import InputScoreDialog
from core.backup_service import backup_excel,set_backup_path


class MainWindow:

    def __init__(self,root):

        self.root=root

        self.table=StudentTable(root)

        self.table.pack(fill="both",expand=True)

        self.current_file=None

        self.create_toolbar()

        self.create_status()

        self.enable_drag_drop()
        self.create_search()

    def create_toolbar(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        tk.Button(frame,text="Open Excel",
                command=self.open_excel).pack(side="left")

        tk.Button(frame,text="Save",
                command=self.save_excel).pack(side="left")

        tk.Button(frame,text="Calculate Total",
                command=self.calculate_total).pack(side="left")

        tk.Button(frame,text="Nhập điểm",
                command=self.open_input_score).pack(side="left")

        tk.Button(frame,text="Backup Folder",
                command=self.choose_backup).pack(side="left")

        tk.Button(frame,text="Tác giả",
                command=self.show_author).pack(side="right")

    def create_status(self):

        self.status=tk.Label(self.root,text="No file loaded")

        self.status.pack(fill="x")

    def enable_drag_drop(self):

        self.root.drop_target_register(DND_FILES)

        self.root.dnd_bind("<<Drop>>",self.drop_file)

    def drop_file(self,event):

        path=event.data.strip("{}")

        if not path.endswith(".xlsx"):

            messagebox.showerror("Error","Drop file Excel (.xlsx)")

            return

        self.load_file(path)

    def open_excel(self):

        path=filedialog.askopenfilename(
            filetypes=[("Excel","*.xlsx")]
        )

        if path:

            self.load_file(path)

    def load_file(self,path):

        try:

            backup_excel(path)

            df = load_excel(path)

            self.table.load_dataframe(df)

            self.current_file = path

            self.status.config(text=f"Loaded: {path}")

        except Exception as e:

            messagebox.showerror("Error", str(e))
        
    def save_excel(self):

        if self.table.df is None:
            return

        save_excel(self.table.df, self.current_file)

        self.status.config(text="Saved")

    def calculate_total(self):

        try:

            weights=load_weights()

            self.table.df=calculate_total(self.table.df,weights)

            self.table.refresh()

        except Exception as e:

            messagebox.showerror("Error",str(e))

    def show_author(self):

        AuthorDialog(self.root)
        
    def create_search(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x")

        tk.Label(frame,text="Search").pack(side="left")

        self.search_var = tk.StringVar()

        entry = tk.Entry(frame,textvariable=self.search_var)

        entry.pack(side="left",padx=5)

        entry.bind("<KeyRelease>",self.do_search)
        
    def do_search(self,event):

        keyword = self.search_var.get()

        self.table.search(keyword)
        
    def open_input_score(self):

        if self.table.df is None:
            return

        InputScoreDialog(
            self.root,
            self.table.df,
            self.current_file
        )
        
    def apply_scores(self,scores):

        selected = self.table.tree.selection()

        if not selected:
            return

        row = selected[0]

        row_index = self.table.tree.index(row)

        for col,val in scores.items():

            if val:

                self.table.df.loc[row_index,col] = float(val)

        self.table.refresh()
        
    def choose_backup(self):

        folder = filedialog.askdirectory()

        if folder:

            set_backup_path(folder)
            
    def after_input_score(self):

        # refresh table
        self.table.refresh()

        # save trực tiếp excel
        save_excel(self.table.df, self.current_file)

        self.status.config(text="Score updated")
        
    
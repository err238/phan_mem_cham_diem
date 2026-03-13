import tkinter as tk
from tkinter import filedialog,messagebox
from tkinterdnd2 import DND_FILES

from ui.table_view import StudentTable
from ui.author_dialog import AuthorDialog

from core.excel_io import load_excel,save_excel
from core.grade_calculator import calculate_total
from core.backup_service import backup_excel
from core.config_service import load_weights


class MainWindow:

    def __init__(self,root):

        self.root=root

        self.table=StudentTable(root)

        self.table.pack(fill="both",expand=True)

        self.current_file=None

        self.create_toolbar()

        self.create_status()

        self.enable_drag_drop()

    def create_toolbar(self):

        frame=tk.Frame(self.root)

        frame.pack(fill="x")

        tk.Button(frame,text="Open Excel",
                  command=self.open_excel).pack(side="left")

        tk.Button(frame,text="Save",
                  command=self.save_excel).pack(side="left")

        tk.Button(frame,text="Calculate Total",
                  command=self.calculate_total).pack(side="left")

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

        df=load_excel(path)

        self.table.load_dataframe(df)

        self.current_file=path

        self.status.config(text=f"Loaded: {path}")

    def save_excel(self):

        if self.table.df is None:
            return

        backup_excel(self.current_file)

        path=filedialog.asksaveasfilename(
            defaultextension=".xlsx"
        )

        save_excel(self.table.df,path)

    def calculate_total(self):

        try:

            weights=load_weights()

            self.table.df=calculate_total(self.table.df,weights)

            self.table.refresh()

        except Exception as e:

            messagebox.showerror("Error",str(e))

    def show_author(self):

        AuthorDialog(self.root)
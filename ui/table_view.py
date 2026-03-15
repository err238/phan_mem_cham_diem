import tkinter as tk
from tkinter import ttk, messagebox
from core.validator import validate_score
from core.excel_io import save_excel


class StudentTable(tk.Frame):

    def __init__(self,parent):

        super().__init__(parent)

        self.df=None
        self.file_path=None # lấy đường dẫn để lưu ra file excel khi sửa điểm

        # frame chứa bảng + scrollbar
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)

        # treeview
        self.tree = ttk.Treeview(frame)

        # scrollbar dọc
        scroll_y = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        # scrollbar ngang
        scroll_x = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        # layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>",self.edit_cell)

    def load_dataframe(self,df,path):

        self.df=df
        self.file_path=path

        self.refresh()

    def refresh(self):

        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        
        # gắn màu cho sv có điểm < 5
        self.tree.tag_configure(
            "fail",
            background="#ffe5d6"
        )

        for col in self.df.columns:

            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_column(c)
            )

            self.tree.column(col, width=140, stretch=False)

        # gắn tags màu cho sv có điểm < 5
        for idx, row in self.df.iterrows():
            values = [
                "" if str(v) == "nan" else v
                for v in row
            ]
            tags = ()
            
            if "TongKet" in self.df.columns:
                total = row["TongKet"]
                if total == total and total < 5:   # kiểm tra NaN
                    tags = ("fail",)

            self.tree.insert(
                "",
                tk.END,
                iid=idx,
                values=values,
                tags=tags
            )

            
        # FIX SCROLLBAR
        self.tree.xview_moveto(0)
        self.tree.update_idletasks()

    def sort_column(self,col):

        self.df=self.df.sort_values(by=col)

        self.refresh()

    def edit_cell(self,event):

        region=self.tree.identify_region(event.x,event.y)

        if region!="cell":
            return

        row=self.tree.identify_row(event.y)

        column=self.tree.identify_column(event.x)

        col_index=int(column.replace("#",""))-1

        row_index=int(row)

        x,y,w,h=self.tree.bbox(row,column)

        value=self.tree.set(row,column)

        entry=tk.Entry(self.tree)

        entry.place(x=x,y=y,width=w,height=h)

        entry.insert(0,value)

        entry.focus()

        def save(e):

            new = entry.get()
            col_name = self.df.columns[col_index]

            if not validate_score(new):

                messagebox.showerror("Error","Điểm phải từ 0-10")
                entry.destroy()
                return

            value = float(new)

            # lưu dataframe
            self.df.loc[row_index, col_name] = value

            # update treeview
            self.tree.set(row, column, new)
            
            # save vào file excel
            save_excel(self.df, self.file_path)

            entry.destroy()
            
        entry.bind("<FocusOut>", save) # click ra ngoài để lưu

        entry.bind("<Return>",save) # enter để lưu
        
    def search(self, keyword):

        keyword = keyword.lower()

        for item in self.tree.get_children():

            values = self.tree.item(item)["values"]

            text = " ".join(str(v).lower() for v in values)

            if keyword in text:

                self.tree.selection_set(item)

                self.tree.see(item)

                break
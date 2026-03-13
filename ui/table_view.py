import tkinter as tk
from tkinter import ttk, messagebox
from core.validator import validate_score


class StudentTable(tk.Frame):

    def __init__(self,parent):

        super().__init__(parent)

        self.df=None

        self.tree=ttk.Treeview(self)

        self.tree.pack(fill="both",expand=True)

        self.tree.bind("<Double-1>",self.edit_cell)

    def load_dataframe(self,df):

        self.df=df

        self.refresh()

    def refresh(self):

        self.tree.delete(*self.tree.get_children())

        self.tree["columns"]=list(self.df.columns)

        self.tree["show"]="headings"

        for col in self.df.columns:

            self.tree.heading(
                col,
                text=col,
                command=lambda c=col:self.sort_column(c)
            )

            self.tree.column(col,width=120)

        for _,row in self.df.iterrows():

            self.tree.insert("",tk.END,values=list(row))

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

        row_index=self.tree.index(row)

        x,y,w,h=self.tree.bbox(row,column)

        value=self.tree.set(row,column)

        entry=tk.Entry(self.tree)

        entry.place(x=x,y=y,width=w,height=h)

        entry.insert(0,value)

        entry.focus()

        def save(e):

            new=entry.get()

            if not validate_score(new):

                messagebox.showerror("Error","Điểm phải từ 0-10")

                entry.destroy()

                return

            self.tree.set(row,column,new)

            col_name=self.df.columns[col_index]

            self.df.iloc[row_index,col_name]=float(new)

            entry.destroy()

        entry.bind("<Return>",save)
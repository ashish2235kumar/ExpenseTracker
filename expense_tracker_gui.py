"""Personal Expense Tracker (GUI) - Mini Project
Libraries: tkinter, numpy, pandas, matplotlib
Features: set monthly budget, add expenses to a table (CSV),
          see remaining amount, view expense pie chart.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

EXPENSE_FILE = "expenses.csv"
BUDGET_FILE = "budget.txt"
COLUMNS = ["Date", "Category", "Description", "Amount"]
CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Other"]


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        root.title("Personal Expense Tracker")
        self.df = self.load_expenses()
        self.budget = self.load_budget()
        self.build_ui()
        self.refresh()

    # ---------- data ----------
    def load_expenses(self):
        if os.path.exists(EXPENSE_FILE):
            return pd.read_csv(EXPENSE_FILE, parse_dates=["Date"])
        return pd.DataFrame(columns=COLUMNS)

    def load_budget(self):
        if os.path.exists(BUDGET_FILE):
            with open(BUDGET_FILE) as f:
                return float(f.read())
        return 0.0

    # ---------- UI ----------
    def build_ui(self):
        # Budget section
        top = ttk.LabelFrame(self.root, text="Monthly Budget")
        top.pack(fill="x", padx=10, pady=5)
        self.budget_entry = ttk.Entry(top, width=15)
        self.budget_entry.pack(side="left", padx=5, pady=5)
        ttk.Button(top, text="Set Budget", command=self.set_budget).pack(side="left")

        # Add expense section
        form = ttk.LabelFrame(self.root, text="Add Expense")
        form.pack(fill="x", padx=10, pady=5)
        ttk.Label(form, text="Date").grid(row=0, column=0, padx=5)
        ttk.Label(form, text="Category").grid(row=0, column=1, padx=5)
        ttk.Label(form, text="Description").grid(row=0, column=2, padx=5)
        ttk.Label(form, text="Amount").grid(row=0, column=3, padx=5)

        self.date_e = ttk.Entry(form, width=12)
        self.date_e.insert(0, str(date.today()))
        self.cat_e = ttk.Combobox(form, values=CATEGORIES, width=10, state="readonly")
        self.cat_e.current(0)
        self.desc_e = ttk.Entry(form, width=20)
        self.amt_e = ttk.Entry(form, width=10)
        for i, w in enumerate([self.date_e, self.cat_e, self.desc_e, self.amt_e]):
            w.grid(row=1, column=i, padx=5, pady=5)
        ttk.Button(form, text="Add", command=self.add_expense).grid(row=1, column=4, padx=5)

        # Expense table
        self.tree = ttk.Treeview(self.root, columns=COLUMNS, show="headings", height=10)
        for c in COLUMNS:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Summary + chart button
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=5)
        self.summary = ttk.Label(bottom, text="", font=("Arial", 11, "bold"))
        self.summary.pack(side="left")
        ttk.Button(bottom, text="Show Pie Chart", command=self.show_pie).pack(side="right")
        ttk.Button(bottom, text="Reset All", command=self.reset_all).pack(side="right", padx=5)
        ttk.Button(bottom, text="Delete Selected", command=self.delete_selected).pack(side="right")

    # ---------- actions ----------
    def set_budget(self):
        try:
            self.budget = float(self.budget_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid budget amount.")
            return
        with open(BUDGET_FILE, "w") as f:
            f.write(str(self.budget))
        self.refresh()

    def add_expense(self):
        try:
            d = pd.to_datetime(self.date_e.get())
            amount = float(self.amt_e.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid date (YYYY-MM-DD) and amount.")
            return
        row = pd.DataFrame([[d, self.cat_e.get(), self.desc_e.get(), amount]], columns=COLUMNS)
        self.df = pd.concat([self.df, row], ignore_index=True)
        self.df.to_csv(EXPENSE_FILE, index=False)
        self.desc_e.delete(0, tk.END)
        self.amt_e.delete(0, tk.END)
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select an expense in the table first.")
            return
        self.df = self.df.drop(index=[int(i) for i in selected]).reset_index(drop=True)
        self.df.to_csv(EXPENSE_FILE, index=False)
        self.refresh()

    def reset_all(self):
        if messagebox.askyesno("Reset", "Delete ALL expenses? This cannot be undone."):
            self.df = pd.DataFrame(columns=COLUMNS)
            self.df.to_csv(EXPENSE_FILE, index=False)
            self.refresh()

    def refresh(self):
        """Update the table and the remaining-amount label."""
        self.tree.delete(*self.tree.get_children())
        for idx, r in self.df.sort_values("Date").iterrows():
            self.tree.insert("", tk.END, iid=str(idx), values=(r["Date"].date(), r["Category"],
                                                 r["Description"], f"{r['Amount']:.2f}"))
        today = pd.Timestamp.today()
        dates = pd.to_datetime(self.df["Date"])  # also works when the table is empty
        month = self.df[(dates.dt.month == today.month) & (dates.dt.year == today.year)]
        spent = np.sum(month["Amount"].to_numpy())
        remaining = self.budget - spent
        self.summary.config(
            text=f"Budget: {self.budget:.2f}   Spent: {spent:.2f}   Remaining: {remaining:.2f}",
            foreground="red" if remaining < 0 else "green")

    def show_pie(self):
        if self.df.empty:
            messagebox.showinfo("Info", "No expenses to plot yet.")
            return
        by_cat = self.df.groupby("Category")["Amount"].sum()
        win = tk.Toplevel(self.root)
        win.title("Expenses by Category")
        fig = Figure(figsize=(5, 5))
        ax = fig.add_subplot(111)
        ax.pie(by_cat, labels=by_cat.index, autopct="%1.1f%%")
        ax.set_title("Expenses by Category")
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack()
        canvas.draw()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    ExpenseTracker(root)
    root.mainloop()

# Personal Expense Tracker

A simple desktop app to track personal expenses, built as a Python mini project.

## Features
- Set a monthly budget
- Add expenses (date, category, description, amount) and view them in a table
- See the remaining amount for the current month (turns red when over budget)
- Pie chart of spending by category
- Delete a selected expense or reset all expenses

## Tech Stack
- Python 3
- tkinter (GUI)
- pandas (data handling and CSV storage)
- numpy (calculations)
- matplotlib (pie chart)

## How to Run
```
pip install numpy pandas matplotlib
python expense_tracker_gui.py
```

Your data is saved locally in `expenses.csv` and `budget.txt`.

import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from helpers import get_currency_input, print_table
from colorama import Fore, Style, init
import os

class BudgetTracker:
    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "finance_tracker.db")

    def __init__(self):
        init()
        print(f"Using database at: {self.DB_FILE}")  # Add this line
        self.conn = sqlite3.connect(self.DB_FILE)
        self.create_tables()

    def create_tables(self):
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        amount REAL,
                        category TEXT,
                        note TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS budgets (
                        user_id INTEGER,
                        category TEXT,
                        amount REAL NOT NULL,
                        PRIMARY KEY(user_id, category),
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                """)
        except Exception as e:
            print(f"{Fore.RED}Error creating tables: {e}{Style.RESET_ALL}")

    def add_user(self):
        username = input("Enter new username: ").strip()
        if not username:
            print(f"{Fore.RED}Username cannot be empty.{Style.RESET_ALL}")
            return
        try:
            with self.conn:
                self.conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
            print(f"{Fore.GREEN}✔ User '{username}' added!{Style.RESET_ALL}")
        except sqlite3.IntegrityError:
            print(f"{Fore.RED}Username '{username}' already exists.{Style.RESET_ALL}")

    def select_user(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, username FROM users")
        users = cur.fetchall()
        if not users:
            print(f"{Fore.RED}No users found. Please add a user first.{Style.RESET_ALL}")
            self.add_user()
            return self.select_user()
        print("\nUsers:")
        for uid, uname in users:
            print(f"{uid}: {uname}")
        while True:
            try:
                user_id = int(input("Select user by ID: ").strip())
                if any(uid == user_id for uid, _ in users):
                    self.current_user_id = user_id
                    self.current_username = next(uname for uid, uname in users if uid == user_id)
                    print(f"{Fore.GREEN}✔ Logged in as {self.current_username}{Style.RESET_ALL}")
                    return
                else:
                    print(f"{Fore.RED}Invalid user ID.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")

    # Update add_transaction to use user_id
    def add_transaction(self):
        if not hasattr(self, "current_user_id"):
            print(f"{Fore.RED}No user selected. Please select a user first.{Style.RESET_ALL}")
            self.select_user()
        print(f"\n{Fore.BLUE}➕ New Transaction for {self.current_username}{Style.RESET_ALL}")
        amount = get_currency_input("Amount (+income, -expense): $")
        while True:
            category = input("Category: ").strip().title()
            if category:
                break
            print(f"{Fore.RED}Category can't be empty{Style.RESET_ALL}")
        note = input("Note (optional): ").strip()
        date_str = datetime.now().strftime("%Y-%m-%d")
        with self.conn:
            self.conn.execute(
                "INSERT INTO transactions (user_id, date, amount, category, note) VALUES (?, ?, ?, ?, ?)",
                (self.current_user_id, date_str, amount, category, note)
            )
        print(f"{Fore.GREEN}✔ Added {category} transaction: ${abs(amount):.2f}{Style.RESET_ALL}")

    # Update view_transactions to filter by user
    def view_transactions(self):
        if not hasattr(self, "current_user_id"):
            print(f"{Fore.RED}No user selected. Please select a user first.{Style.RESET_ALL}")
            self.select_user()
        cur = self.conn.cursor()
        cur.execute(
            "SELECT date, category, amount, note FROM transactions WHERE user_id=? ORDER BY date DESC",
            (self.current_user_id,)
        )
        rows = cur.fetchall()
        if not rows:
            print(f"\n{Fore.RED}No transactions yet{Style.RESET_ALL}")
            return
        print(f"\n{Fore.BLUE}📋 All Transactions for {self.current_username}{Style.RESET_ALL}")
        headers = ["Date", "Category", "Amount", "Note"]
        table_rows = []
        for date, category, amount, note in rows:
            amt_str = f"${amount:.2f}" if amount >= 0 else f"-${abs(amount):.2f}"
            table_rows.append([date, category, amt_str, note])
        print_table(headers, table_rows)

    # Update budgets to filter by user
    def view_budgets(self):
        if not hasattr(self, "current_user_id"):
            print(f"{Fore.RED}No user selected. Please select a user first.{Style.RESET_ALL}")
            self.select_user()
        cur = self.conn.cursor()
        cur.execute("SELECT category, amount FROM budgets WHERE user_id=?", (self.current_user_id,))
        budgets = cur.fetchall()
        headers = ["Category", "Budget", "Spent", "Remaining"]
        rows = []
        for category, budget in budgets:
            cur.execute(
                "SELECT SUM(amount) FROM transactions WHERE user_id=? AND category=? AND amount<0",
                (self.current_user_id, category)
            )
            spent = cur.fetchone()[0] or 0
            remaining = budget + spent
            status_color = Fore.RED if remaining < 0 else Fore.GREEN
            status = "❌ OVER" if remaining < 0 else "✅ OK"
            rows.append([
                category,
                f"${budget:.2f}",
                f"${abs(spent):.2f}",
                f"{status_color}${abs(remaining):.2f} {status}{Style.RESET_ALL}"
            ])
        print_table(headers, rows)

    def edit_budget(self):
        if not hasattr(self, "current_user_id"):
            print(f"{Fore.RED}No user selected. Please select a user first.{Style.RESET_ALL}")
            self.select_user()
        category = input("Category name: ").strip().title()
        if not category:
            print(f"{Fore.RED}Category can't be empty{Style.RESET_ALL}")
            return
        amount = get_currency_input("Monthly budget amount: $")
        if amount <= 0:
            print(f"{Fore.RED}Invalid amount{Style.RESET_ALL}")
            return
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO budgets (user_id, category, amount) VALUES (?, ?, ?)",
                (self.current_user_id, category, amount)
            )
        print(f"{Fore.GREEN}✔ Budget for {category} set to ${amount:.2f}{Style.RESET_ALL}")

    def show_menu(self):
        print("\nWhat would you like to do?")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Manage Budgets")
        print("4. Monthly Report")
        print("5. Exit")
        return input("Enter your choice: ")

    # In your run() method, add user management options:
    def run(self):
        try:
            while True:
                print(f"\n{Fore.YELLOW}U.{Style.RESET_ALL} 👤 Add User")
                print(f"{Fore.YELLOW}L.{Style.RESET_ALL} 🔑 Login as User")
                choice = self.show_menu()
                if choice.lower() == "u":
                    self.add_user()
                elif choice.lower() == "l":
                    self.select_user()
                elif choice == "1":
                    self.add_transaction()
                elif choice == "2":
                    self.view_transactions()
                elif choice == "3":
                    self.manage_budgets()
                elif choice == "4":
                    self.monthly_report()
                elif choice == "5":
                    print(f"{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
            sys.exit(0)

if __name__ == "__main__":
    app = BudgetTracker()
    app.run()
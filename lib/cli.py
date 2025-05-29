import json
import sys
from datetime import datetime
from pathlib import Path
from helpers import get_currency_input, print_table
from colorama import Fore, Style, init

class BudgetTracker:
    DATA_FILE = "budget_data.json"
    
    def __init__(self):
        init()
        self.transactions = []
        self.budgets = {}
        self.load_data()
        
    def load_data(self):
        try:
            if Path(self.DATA_FILE).exists():
                with open(self.DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    self.budgets = data.get('budgets', {})
        except Exception as e:
            print(f"{Fore.RED}Error loading data: {e}{Style.RESET_ALL}")

    def save_data(self):
        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump({
                    'transactions': self.transactions,
                    'budgets': self.budgets
                }, f, indent=2)
        except Exception as e:
            print(f"{Fore.RED}Error saving data: {e}{Style.RESET_ALL}")

    def show_menu(self):
        print(f"\n{Fore.CYAN}💰 Budget Tracker v1.0{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} ➕ Add Transaction")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} 📊 View Transactions")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} 📝 Manage Budgets")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} 📈 Monthly Report")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} 🚪 Exit")
        return input(f"{Fore.GREEN}▶ Your choice:{Style.RESET_ALL} ").strip()

    def add_transaction(self):
        print(f"\n{Fore.BLUE}➕ New Transaction{Style.RESET_ALL}")
        
        amount = get_currency_input("Amount (+income, -expense): $")
        while True:
            category = input("Category: ").strip().title()
            if category:
                break
            print(f"{Fore.RED}Category can't be empty{Style.RESET_ALL}")
            
        note = input("Note (optional): ").strip()
        
        new_trans = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'amount': amount,
            'category': category,
            'note': note
        }
        
        self.transactions.append(new_trans)
        self.save_data()
        print(f"{Fore.GREEN}✔ Added {category} transaction: ${abs(amount):.2f}{Style.RESET_ALL}")

    def view_transactions(self):
        if not self.transactions:
            print(f"\n{Fore.RED}No transactions yet{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.BLUE}📋 All Transactions{Style.RESET_ALL}")
        headers = ["Date", "Category", "Amount", "Note"]
        rows = []
        
        for t in sorted(self.transactions, key=lambda x: x['date'], reverse=True):
            amount = f"${t['amount']:.2f}" if t['amount'] >=0 else f"-${abs(t['amount']):.2f}"
            rows.append([t['date'], t['category'], amount, t['note']])
        
        print_table(headers, rows)

    def manage_budgets(self):
        print(f"\n{Fore.BLUE}📝 Budget Management{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} View Current Budgets")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Add/Edit Budget")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Remove Budget")
        choice = input(f"{Fore.GREEN}▶ Your choice:{Style.RESET_ALL} ").strip()
        
        if choice == "1":
            self.view_budgets()
        elif choice == "2":
            self.edit_budget()
        elif choice == "3":
            self.remove_budget()
        else:
            print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")

    def view_budgets(self):
        if not self.budgets:
            print(f"\n{Fore.RED}No budgets set{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.BLUE}📊 Current Budgets{Style.RESET_ALL}")
        headers = ["Category", "Budget", "Spent", "Remaining"]
        rows = []
        
        for category, budget in self.budgets.items():
            spent = sum(t['amount'] for t in self.transactions 
                      if t['category'] == category and t['amount'] < 0)
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
        category = input("Category name: ").strip().title()
        if not category:
            print(f"{Fore.RED}Category can't be empty{Style.RESET_ALL}")
            return

        amount = get_currency_input("Monthly budget amount: $")
        if amount <= 0:
            print(f"{Fore.RED}Invalid amount{Style.RESET_ALL}")
            return

        self.budgets[category] = amount
        self.save_data()
        print(f"{Fore.GREEN}✔ Budget for {category} set to ${amount:.2f}{Style.RESET_ALL}")

    def remove_budget(self):
        print("Remove budget not implemented yet.")

    def monthly_report(self):
        # Implement monthly analysis
        pass

    def run(self):
        try:
            while True:
                choice = self.show_menu()
                
                if choice == "1":
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
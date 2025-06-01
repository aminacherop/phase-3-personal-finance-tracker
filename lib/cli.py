#!/usr/bin/env python3

import os
import sys
from datetime import datetime, date
from colorama import Fore, Style, Back
import colorama

from database import setup_database, get_db_connection
from transaction import (
    save_transaction_with_budget_alert,
    get_all_transactions,
    calculate_balance,
    get_recent_transactions,
    delete_transaction
)
from budget import (
    set_budget_limit,
    update_budget_limit,
    get_budget_summary,
    check_budget
)
from helper import get_spending_by_category, get_transaction_categories

colorama.init()

class FinanceTrackerCLI:
    def __init__(self):
        self.user_id = 1
        self.user_name = "Default User"
        self.setup_environment()
        self.select_or_create_user()

    def setup_environment(self):
        try:
            setup_database()
            print(f"{Fore.GREEN}✓ Database initialized successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Error initializing database: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        print(f"\n{Back.BLUE}{Fore.WHITE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}{'💰 PERSONAL FINANCE TRACKER':^60}{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}👤 Current User: {self.user_name} (ID: {self.user_id}){Style.RESET_ALL}\n")

    def print_menu(self):
        print(f"{Fore.CYAN}📋 MAIN MENU{Style.RESET_ALL}")
        print("─" * 30)
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} 👥 User Management")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} 💸 Add Transaction")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} 📊 View Transactions")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} 💰 View Balance")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} 🎯 Manage Budgets")
        print(f"{Fore.YELLOW}6.{Style.RESET_ALL} 📈 Budget Summary")
        print(f"{Fore.YELLOW}7.{Style.RESET_ALL} 🕒 Recent Activity")
        print(f"{Fore.YELLOW}8.{Style.RESET_ALL} 🗑️  Delete Transaction")
        print(f"{Fore.YELLOW}9.{Style.RESET_ALL} 🔄 Refresh Screen")
        print(f"{Fore.RED}10.{Style.RESET_ALL} 🚪 Exit")
        print()

    def get_user_input(self, prompt, input_type=str, validation_func=None):
        while True:
            try:
                user_input = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    return None

                if input_type == int:
                    value = int(user_input)
                elif input_type == float:
                    value = float(user_input)
                else:
                    value = user_input

                if validation_func and not validation_func(value):
                    print(f"{Fore.RED}✗ Invalid input. Please try again.{Style.RESET_ALL}")
                    continue

                return value
            except ValueError:
                print(f"{Fore.RED}✗ Please enter a valid {input_type.__name__}.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return None

    def confirm_action(self, message):
        response = self.get_user_input(f"{message} (y/N): ")
        return response and response.lower() in ['y', 'yes']

    def add_transaction(self):
        print(f"\n{Fore.GREEN}💸 ADD NEW TRANSACTION{Style.RESET_ALL}")
        print("─" * 25)

        amount = self.get_user_input(
            "Enter amount (positive for income, negative for expense): $",
            float,
            lambda x: x != 0
        )
        if amount is None:
            return

        category = self.get_user_input("Category: ")
        if not category:
            return

        date_input = self.get_user_input(
            f"Date (YYYY-MM-DD) or press Enter for today [{date.today()}]: "
        )
        if date_input:
            validated_date = self.validate_date(date_input)
            if not validated_date:
                print(f"{Fore.RED}Invalid date format. Use YYYY-MM-DD{Style.RESET_ALL}")
                return
            date_input = validated_date.isoformat()
        else:
            date_input = date.today().isoformat()

        description = self.get_user_input("Description (optional): ")
        if description is None:
            return

        transaction_type = "💰 Income" if amount > 0 else "💸 Expense"
        print(f"\n{Fore.YELLOW}📋 Transaction Summary:{Style.RESET_ALL}")
        print(f"Type: {transaction_type}")
        print(f"Amount: ${abs(amount):.2f}")
        print(f"Category: {category}")
        print(f"Date: {date_input}")
        print(f"Description: {description or 'None'}")

        if self.confirm_action("Save this transaction?"):
            success = save_transaction_with_budget_alert(
                self.user_id, amount, category, date_input, description
            )
            if success:
                print(f"\n{Fore.GREEN}✓ Transaction saved successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to save transaction.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Transaction cancelled.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def select_or_create_user(self):
        users = self.get_all_users()

        if len(users) == 1:
            self.user_id = users[0]['user_id']
            self.user_name = users[0]['name']
            return

        print(f"\n{Fore.CYAN}👥 USER SELECTION{Style.RESET_ALL}")
        print("─" * 20)
        print("Available users:")

        for i, user in enumerate(users, 1):
            print(f"{i}. {user['name']} (ID: {user['user_id']})")

        print(f"{len(users) + 1}. Create new user")

        choice = self.get_user_input(
            f"Select user (1-{len(users) + 1}): ",
            int,
            lambda x: 1 <= x <= len(users) + 1
        )

        if choice is None:
            self.user_id = users[0]['user_id']
            self.user_name = users[0]['name']
            return

        if choice <= len(users):
            selected_user = users[choice - 1]
            self.user_id = selected_user['user_id']
            self.user_name = selected_user['name']
            print(f"{Fore.GREEN}✓ Logged in as: {self.user_name}{Style.RESET_ALL}")
        else:
            self.create_new_user()

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def get_all_users(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name FROM users ORDER BY user_id")
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return users
        except Exception as e:
            print(f"{Fore.RED}Error fetching users: {e}{Style.RESET_ALL}")
            return [{'user_id': 1, 'name': 'Default User'}]

    def create_new_user(self):
        name = self.get_user_input("Enter your name: ")
        if not name or not name.strip():
            print(f"{Fore.RED}✗ Invalid name. Using Default User.{Style.RESET_ALL}")
            self.user_id = 1
            self.user_name = "Default User"
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name.strip(),))
            self.user_id = cursor.lastrowid
            self.user_name = name.strip()
            conn.commit()
            conn.close()
            print(f"{Fore.GREEN}✓ User '{self.user_name}' created successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}✗ Error creating user: {e}{Style.RESET_ALL}")
            self.user_id = 1
            self.user_name = "Default User"

    def user_management(self):
        print(f"\n{Fore.GREEN}👥 USER MANAGEMENT{Style.RESET_ALL}")
        print("─" * 20)

        print("1. Switch user")
        print("2. Create new user")
        print("3. View all users")
        print("4. Back to main menu")

        choice = self.get_user_input("Choose option (1-4): ", int, lambda x: 1 <= x <= 4)
        if choice is None or choice == 4:
            return

        if choice == 1:
            self.switch_user()
        elif choice == 2:
            self.create_new_user()
        elif choice == 3:
            self.view_all_users()

    def switch_user(self):
        users = self.get_all_users()

        print(f"\n{Fore.CYAN}Available users:{Style.RESET_ALL}")
        for i, user in enumerate(users, 1):
            current = " (Current)" if user['user_id'] == self.user_id else ""
            print(f"{i}. {user['name']} (ID: {user['user_id']}){current}")

        choice = self.get_user_input(
            f"Select user (1-{len(users)}): ",
            int,
            lambda x: 1 <= x <= len(users)
        )

        if choice is None:
            return

        selected_user = users[choice - 1]
        if selected_user['user_id'] != self.user_id:
            self.user_id = selected_user['user_id']
            self.user_name = selected_user['name']
            print(f"{Fore.GREEN}✓ Switched to: {self.user_name}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Already logged in as {self.user_name}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def view_all_users(self):
        users = self.get_all_users()

        print(f"\n{Fore.CYAN}👥 ALL USERS{Style.RESET_ALL}")
        print("─" * 30)
        print(f"{'ID':<4} {'Name':<20} {'Status':<10}")
        print("─" * 30)

        for user in users:
            status = "Current" if user['user_id'] == self.user_id else ""
            status_color = Fore.GREEN if status else ""
            print(f"{user['user_id']:<4} {user['name']:<20} {status_color}{status}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def view_transactions(self):
        print(f"\n{Fore.GREEN}📊 VIEW TRANSACTIONS{Style.RESET_ALL}")
        print("─" * 20)

        print("Filter options:")
        print("1. All transactions")
        print("2. This month")
        print("3. This year")
        print("4. Specific month/year")

        choice = self.get_user_input("Choose filter (1-4): ", int, lambda x: 1 <= x <= 4)
        if choice is None:
            return

        transactions = []
        if choice == 1:
            transactions = get_all_transactions(self.user_id)
        elif choice == 2:
            now = datetime.now()
            transactions = get_all_transactions(self.user_id, now.month, now.year)
        elif choice == 3:
            now = datetime.now()
            transactions = get_all_transactions(self.user_id, year=now.year)
        elif choice == 4:
            month = self.get_user_input("Month (1-12): ", int, lambda x: 1 <= x <= 12)
            if month is None:
                return
            year = self.get_user_input("Year: ", int, lambda x: x > 1900)
            if year is None:
                return
            transactions = get_all_transactions(self.user_id, month, year)

        self.display_transactions(transactions)
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def display_transactions(self, transactions):
        if not transactions:
            print(f"\n{Fore.YELLOW}📭 No transactions found.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}📋 TRANSACTION HISTORY{Style.RESET_ALL}")
        print("─" * 80)
        print(f"{'ID':<4} {'Date':<12} {'Category':<15} {'Amount':<12} {'Description':<25}")
        print("─" * 80)

        total_income = 0
        total_expenses = 0

        for trans in transactions:
            amount = float(trans['amount'])
            if amount > 0:
                total_income += amount
                amount_color = Fore.GREEN
                amount_str = f"+${amount:.2f}"
            else:
                total_expenses += abs(amount)
                amount_color = Fore.RED
                amount_str = f"-${abs(amount):.2f}"

            print(f"{trans['transaction_id']:<4} "
                  f"{trans['date']:<12} "
                  f"{trans['category']:<15} "
                  f"{amount_color}{amount_str:<12}{Style.RESET_ALL} "
                  f"{trans['description'][:25]:<25}")

        print("─" * 80)
        print(f"Total Income: {Fore.GREEN}+${total_income:.2f}{Style.RESET_ALL}")
        print(f"Total Expenses: {Fore.RED}-${total_expenses:.2f}{Style.RESET_ALL}")
        print(f"Net: {Fore.CYAN}${total_income - total_expenses:.2f}{Style.RESET_ALL}")

    def view_balance(self):
        balance = calculate_balance(self.user_id)

        print(f"\n{Fore.GREEN}💰 ACCOUNT BALANCE{Style.RESET_ALL}")
        print("─" * 20)

        if balance >= 0:
            print(f"Current Balance: {Fore.GREEN}${balance:.2f}{Style.RESET_ALL}")
        else:
            print(f"Current Balance: {Fore.RED}${balance:.2f}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def manage_budgets(self):
        print(f"\n{Fore.GREEN}🎯 MANAGE BUDGETS{Style.RESET_ALL}")
        print("─" * 18)

        print("1. Set new budget")
        print("2. Update existing budget")
        print("3. View all budgets")

        choice = self.get_user_input("Choose option (1-3): ", int, lambda x: 1 <= x <= 3)
        if choice is None:
            return

        if choice == 1:
            self.set_budget()
        elif choice == 2:
            self.update_budget()
        elif choice == 3:
            self.view_budget_summary()

    def set_budget(self):
        category = self.get_user_input("Category: ")
        if not category:
            return

        amount = self.get_user_input("Budget limit: $", float, lambda x: x > 0)
        if amount is None:
            return

        if self.confirm_action(f"Set budget of ${amount:.2f} for {category}?"):
            success = set_budget_limit(self.user_id, category, amount)
            if success:
                print(f"\n{Fore.GREEN}✓ Budget set successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to set budget.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def update_budget(self):
        try:
            summary = get_budget_summary(self.user_id)
            if summary is None:
                print(f"{Fore.YELLOW}Failed to retrieve budget data.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            if not summary:
                print(f"{Fore.YELLOW}No budgets found.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            print("\nCurrent budgets with limits:")
            has_budgets = False
            for item in summary:
                if item.get('limit', 0) > 0:
                    print(f"- {item.get('category', 'Unknown')}: ${item['limit']:.2f}")
                    has_budgets = True

            if not has_budgets:
                print(f"{Fore.YELLOW}No budgets with limits set.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            category = self.get_user_input("\nCategory to update: ")
            if not category:
                return

            if not any(item.get('category') == category and item.get('limit', 0) > 0 for item in summary):
                print(f"{Fore.RED}Category not found or has no budget set.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            new_amount = self.get_user_input("New budget limit: $", float, lambda x: x > 0)
            if new_amount is None:
                return

            if self.confirm_action(f"Update {category} budget to ${new_amount:.2f}?"):
                success = update_budget_limit(self.user_id, category, new_amount)
                if success:
                    print(f"\n{Fore.GREEN}✓ Budget updated successfully!{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}✗ Failed to update budget.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error updating budget: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def view_budget_summary(self):
        try:
            summary = get_budget_summary(self.user_id)
            if summary is None:
                print(f"{Fore.YELLOW}Failed to retrieve budget data.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            print(f"\n{Fore.GREEN}📈 BUDGET SUMMARY{Style.RESET_ALL}")
            print("─" * 70)
            
            if not summary:
                print(f"{Fore.YELLOW}No budget data available.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                return

            print(f"{'Category':<15} {'Limit':<12} {'Spent':<12} {'Remaining':<12} {'Status':<10}")
            print("─" * 70)

            for item in summary:
                category = item.get('category', 'Unknown')
                limit = item.get('limit', 0)
                spent = abs(item.get('spent', 0))
                status = item.get('status', 'OK')

                if limit and limit > 0:
                    remaining = limit - spent
                    remaining_percent = (remaining / limit) * 100
                    
                    if status == 'OK':
                        if remaining_percent < 0:
                            status = "OVER"
                        elif remaining_percent < 20:
                            status = "WARNING"
                        else:
                            status = "OK"
                    
                    limit_str = f"${limit:.2f}"
                    spent_str = f"${spent:.2f}"
                    remaining_str = f"${remaining:.2f}"

                    if status == "OVER":
                        status_color = Fore.RED
                        remaining_color = Fore.RED
                    elif status == "WARNING":
                        status_color = Fore.YELLOW
                        remaining_color = Fore.YELLOW
                    else:
                        status_color = Fore.GREEN
                        remaining_color = Fore.GREEN

                    print(f"{category:<15} "
                          f"{limit_str:<12} "
                          f"{spent_str:<12} "
                          f"{remaining_color}{remaining_str:<12}{Style.RESET_ALL} "
                          f"{status_color}{status:<10}{Style.RESET_ALL}")
                else:
                    print(f"{category:<15} "
                          f"{'No limit':<12} "
                          f"${spent:.2f:<11} "
                          f"{'N/A':<12} "
                          f"{Fore.GRAY}No Budget{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error displaying budget summary: {e}{Style.RESET_ALL}")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def view_recent_activity(self):
        print(f"\n{Fore.GREEN}🕒 RECENT ACTIVITY{Style.RESET_ALL}")
        print("─" * 20)

        limit = self.get_user_input("Number of transactions to show (default 10): ")
        if limit is None:
            return

        try:
            limit = int(limit) if limit else 10
        except ValueError:
            limit = 10

        transactions = get_recent_transactions(self.user_id, limit)
        self.display_transactions(transactions)

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def delete_transaction(self):
        print(f"\n{Fore.RED}🗑️  DELETE TRANSACTION{Style.RESET_ALL}")
        print("─" * 25)

        recent = get_recent_transactions(self.user_id, 10)
        if not recent:
            print(f"{Fore.YELLOW}No transactions found.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print("Recent transactions:")
        self.display_transactions(recent)

        transaction_id = self.get_user_input("\nTransaction ID to delete: ", int, lambda x: x > 0)
        if transaction_id is None:
            return

        transaction = None
        for trans in recent:
            if trans['transaction_id'] == transaction_id:
                transaction = trans
                break

        if not transaction:
            print(f"{Fore.RED}✗ Transaction not found in recent transactions.{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return

        print(f"\n{Fore.YELLOW}Transaction to delete:{Style.RESET_ALL}")
        print(f"ID: {transaction['transaction_id']}")
        print(f"Date: {transaction['date']}")
        print(f"Category: {transaction['category']}")
        print(f"Amount: ${transaction['amount']:.2f}")
        print(f"Description: {transaction['description']}")

        if self.confirm_action(f"{Fore.RED}Are you sure you want to delete this transaction?{Style.RESET_ALL}"):
            success = delete_transaction(transaction_id, self.user_id)
            if success:
                print(f"\n{Fore.GREEN}✓ Transaction deleted successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to delete transaction.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Deletion cancelled.{Style.RESET_ALL}")

        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    def run(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()

            choice = self.get_user_input("Select an option (1-10): ", int, lambda x: 1 <= x <= 10)

            if choice is None or choice == 10:
                print(f"\n{Fore.GREEN}Thank you for using Personal Finance Tracker! 👋{Style.RESET_ALL}")
                break

            try:
                if choice == 1:
                    self.user_management()
                elif choice == 2:
                    self.add_transaction()
                elif choice == 3:
                    self.view_transactions()
                elif choice == 4:
                    self.view_balance()
                elif choice == 5:
                    self.manage_budgets()
                elif choice == 6:
                    self.view_budget_summary()
                elif choice == 7:
                    self.view_recent_activity()
                elif choice == 8:
                    self.delete_transaction()
                elif choice == 9:
                    continue

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Operation interrupted. Returning to main menu...{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def main():
    try:
        app = FinanceTrackerCLI()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application terminated by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
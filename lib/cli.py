import argparse
from .transaction import (
    save_transaction_with_budget_alert,
    get_all_transactions,
    calculate_balance,
    delete_transaction,
    update_transaction
)
from lib.budget import (
    set_budget,
    get_budget_summary
)


def main():
    parser = argparse.ArgumentParser(
        description=" 💸 Budget CLI Tool - Track your expenses, budgets & balance with ease! 💰",
        epilog="Example: python cli.py add --user 1 --amount -100 --category Food --date 2025-05-01 --desc 'Lunch'"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add transaction
    add_parser = subparsers.add_parser("add", help="Add a new transaction")
    add_parser.add_argument("--user", type=int, required=True)
    add_parser.add_argument("--amount", type=float, required=True)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--date", required=True)
    add_parser.add_argument("--desc", default="")

    # View all transactions
    view_parser = subparsers.add_parser("view", help="View all transactions")
    view_parser.add_argument("--user", type=int, required=True)

    # Balance
    balance_parser = subparsers.add_parser("balance", help="View account balance")
    balance_parser.add_argument("--user", type=int, required=True)

    # Set budget
    budget_parser = subparsers.add_parser("set-budget", help="Set a category budget")
    budget_parser.add_argument("--user", type=int, required=True)
    budget_parser.add_argument("--category", required=True)
    budget_parser.add_argument("--limit", type=float, required=True)

    # View budget summary
    budget_summary = subparsers.add_parser("budget", help="View budget summary")
    budget_summary.add_argument("--user", type=int, required=True)

    # Delete a transaction
    delete_parser = subparsers.add_parser("delete", help="Delete a transaction by ID")
    delete_parser.add_argument("--user", type=int, required=True)
    delete_parser.add_argument("--id", type=int, required=True)

    # Update transaction
    update_parser = subparsers.add_parser("update", help="Update an existing transaction")
    update_parser.add_argument("--user", type=int, required=True)
    update_parser.add_argument("--id", type=int, required=True)
    update_parser.add_argument("--amount", type=float)
    update_parser.add_argument("--category")
    update_parser.add_argument("--date")
    update_parser.add_argument("--desc")

    args = parser.parse_args()

    if args.command == "add":
        save_transaction_with_budget_alert(args.user, args.amount, args.category, args.date, args.desc)

    elif args.command == "view":
        txns = get_all_transactions(args.user)
        for txn in txns:
            print(txn)

    elif args.command == "balance":
        print(f"Current balance: {calculate_balance(args.user):.2f}")

    elif args.command == "set-budget":
        success = set_budget(args.user, args.category, args.limit)
        print("Budget set!" if success else "Failed to set budget.")

    elif args.command == "budget":
        summary = get_budget_summary(args.user)
        for item in summary:
            print(item)

    elif args.command == "delete":
        delete_transaction(args.user, args.id)

    elif args.command == "update":
        success = update_transaction(
            args.user, args.id, args.amount, args.category, args.date, args.desc
        )
        print("Updated successfully." if success else "Update failed.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

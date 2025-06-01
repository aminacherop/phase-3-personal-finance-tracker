from datetime import datetime, date
from database import get_db_connection
from helper import check_transaction_budget_impact, check_current_budget_status, get_budget_limit, get_spending_by_category


def save_transaction(user_id, amount, category, date_input, description=''):
    try:
        if user_id <= 0:
            print("Error:Invalid user id")
            return False
        if amount == 0:
            print("Error: Amount cannot be zero")
            return False
        if not category.strip():
            print("Error: Category cannot be empty")
            return False

        if isinstance(date_input, str):
            try:
                transaction_date = datetime.strptime(
                    date_input, '%Y-%m-%d').date()
            except ValueError as e:
                print(
                    f"Error: Invalid date format. Use YYYY-MM-DD. Details: {e}")
                return False
        elif isinstance(date_input, date):
            transaction_date = date_input
        else:
            print("Error: Date must be a string (YYYY-MM-DD) or date object")
            return False

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, category.strip(), transaction_date, description.strip()))
        conn.commit()
        conn.close()
        print("Transaction saved successfully")
        return True
    except Exception as e:
        print(f"Error saving transaction:{e}")
        return False

# result = save_transaction(1, 2000, "Fare", "2025-04-18", "Transport")
# print(result)


def save_transaction_with_budget_alert(user_id, amount, category, date_input, description=''):
    if amount < 0:
        print("Checking budget impact...")
        impact = check_transaction_budget_impact(user_id, category, amount)
        print(f"Impact: {impact}")
        if impact == "OVER":
            print(
                f"WARNING: This transaction will exceed your {category} budget!")
        elif impact == "WARNING":
            print(
                f"CAUTION: This transaction will put you near your {category} budget limit!")
    result = save_transaction(
        user_id, amount, category, date_input, description)
    if result and amount < 0:
        print("Checking current budget status...")
        current_status = check_current_budget_status(user_id, category)
        print(f" {category} budget status: {current_status}")

    return result


# print(f"Food budget limit: {get_budget_limit(1, 'Food')}")
# print(f"Current Food spending: {get_spending_by_category(1, 'Food')}")

# print(check_transaction_budget_impact(1, 'Food', -280))
# print(check_transaction_budget_impact(1, 'Food', -350))

# result = save_transaction_with_budget_alert(
#     1, -280, "Food", date.today().isoformat(), "Groceries")
# print(result)


# result = save_transaction_with_budget_alert(1, 2000, "food", date.today().isoformat() ,"Groceries")
# print(result)


def get_all_transactions(user_id, month=None, year=None):
    try:
        if user_id <= 0:
            print("Error: User ID must be positive")
            return []

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT transaction_id, amount, category, date, description
            FROM transactions WHERE user_id = ?
        """
        params = [user_id]

        if month is not None and year is not None:
            if not (1 <= month <= 12):
                print("Error: Month must be between 1 and 12")
                return []
            query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
            params.extend([f"{month:02d}", str(year)])
        elif year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))

        query += " ORDER BY date DESC, created_at DESC"
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    except Exception as e:
        print(f"Database error: {e}")
        return []
# transactions = get_all_transactions(-1)
# transactions = get_all_transactions(1, 0,0)
# print(transactions)


def calculate_balance(user_id):
    try:
        if user_id <= 0:
            print("Error: User ID must be positive")
            return 0.0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as balance
            FROM transactions WHERE user_id = ?
        """, (user_id,))
        balance = float(cursor.fetchone()['balance'])
        conn.close()
        return balance
    except:
        return 0.0


def get_recent_transactions(user_id, limit=5):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT transaction_id, amount, category, date, description
            FROM transactions WHERE user_id = ?
            ORDER BY date DESC, created_at DESC LIMIT ?
        """, (user_id, limit))
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    except:
        return []


def delete_transaction(transaction_id, user_id):
    try:
        if transaction_id <= 0 or user_id <= 0:
            print("Error: Invalid transaction ID or user ID")
            return False

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if transaction exists and belongs to the user
        cursor.execute("""
            SELECT * FROM transactions WHERE transaction_id = ? AND user_id = ?
        """, (transaction_id, user_id))
        transaction = cursor.fetchone()
        if not transaction:
            print("Error: Transaction not found or does not belong to user.")
            conn.close()
            return False

        # Proceed to delete
        cursor.execute("""
            DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?
        """, (transaction_id, user_id))
        conn.commit()
        conn.close()

        print("Transaction deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False


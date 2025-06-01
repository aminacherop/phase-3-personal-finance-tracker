from database import get_db_connection
from transaction import get_spending_by_category
from datetime import datetime
from helper import get_spending_by_category, get_transaction_categories


def validate_amount(amount):
    return isinstance(amount, (int, float)) and amount > 0


def set_budget_limit(user_id, category, amount):
    if not validate_amount(amount):
        print("Error: Amount must be a positive number.")
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if budget already exists
        cursor.execute("""
            SELECT * FROM budgets WHERE user_id = ? AND category = ?
        """, (user_id, category))
        if cursor.fetchone():
            print(
                "Budget for this category already exists. Use update_budget_limit instead.")
            conn.close()
            return False

        cursor.execute("""
            INSERT INTO budgets (user_id, category, limit_amount)
            VALUES (?, ?, ?)
        """, (user_id, category.strip(), amount))
        conn.commit()
        conn.close()
        print(f"Budget set: {category} - ${amount}")
        return True
    except Exception as e:
        print(f"Error setting budget: {e}")
        return False


# budget = set_budget_limit(1, "food", 200)
# print(budget)


def update_budget_limit(user_id, category, new_amount):
    if not validate_amount(new_amount):
        print("Error: New amount must be a positive number.")
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE budgets SET limit_amount = ? WHERE user_id = ? AND category = ?
        """, (new_amount, user_id, category))
        if cursor.rowcount == 0:
            print("⚠️ Budget not found. Use set_budget_limit to create one.")
        else:
            print(f" Budget updated: {category} - ${new_amount}")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating budget: {e}")
        return False
# update = update_budget_limit(1,"Fare",2000)
# print(update)


def check_budget(user_id, category, spent):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT limit_amount FROM budgets 
            WHERE user_id = ? AND category = ?
        """, (user_id, category))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return "No Budget"

        limit = float(row["limit_amount"])

        if spent >= limit:
            return "OVER"
        elif spent >= 0.9 * limit:
            return "WARNING"
        else:
            return "OK"
    except:
        return "Unknown"

# checkbuget = check_budget(1, "Fare", 2800)  # → OK, WARNING, or OVER
# print(checkbuget)


def get_budget_summary(user_id):
    try:
        categories = get_transaction_categories(user_id)
        summary = []

        conn = get_db_connection()
        cursor = conn.cursor()

        for category in categories:
            # Get budget limit
            cursor.execute("""
                SELECT limit_amount FROM budgets WHERE user_id = ? AND category = ?
            """, (user_id, category))
            row = cursor.fetchone()
            limit = float(row["limit_amount"]) if row else None

            # Get total spent from transactions
            spent = get_spending_by_category(user_id, category)

            summary.append({
                "category": category,
                "limit": limit,
                "spent": spent,
                "status": check_budget(user_id, category, spent) if limit else "No Budget"
            })

        conn.close()
        return summary

    except Exception as e:
        print(f"Error generating budget summary: {e}")
        return []


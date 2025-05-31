from lib.database import get_db_connection
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)

def get_budget_limit(user_id, category):
    #Fetches the budget limit for a specific user and category.
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT limit_amount FROM budgets 
            WHERE user_id = ? AND category = ?
        """, (user_id, category))
        row = cursor.fetchone()
        conn.close()
        return float(row["limit_amount"]) if row else None
    except Exception as e:
        logging.error(f"Error fetching budget limit: {e}")
        return None


def get_spending_by_category(user_id, category, month=None, year=None):
    #Returns the total spending (as a positive float) for a given category
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0) as total_spent
            FROM transactions 
            WHERE user_id = ? AND category = ? AND amount < 0
        """
        params = [user_id, category]

        if month is not None and year is not None:
            query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
            params.extend([f"{month:02d}", str(year)])
        elif year is not None:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))

        cursor.execute(query, params)
        total = float(cursor.fetchone()["total_spent"])
        conn.close()
        return total
    except Exception as e:
        logging.error(f"Error calculating spending by category: {e}")
        return 0.0


def get_transaction_categories(user_id):
    #Returns a list of unique categories the user has transactions in.
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category FROM transactions 
            WHERE user_id = ? ORDER BY category
        """, (user_id,))
        categories = [row["category"] for row in cursor.fetchall()]
        conn.close()
        return categories
    except Exception as e:
        logging.error(f"Error fetching transaction categories: {e}")
        return []


def check_transaction_budget_impact(user_id, category, amount):
    #Checks the impact of a new transaction on the user's budget.Returns one of: "OVER", "WARNING", "OK", "NO BUDGET"
    
    try:
        limit = get_budget_limit(user_id, category)
        if limit is None:
            return "NO BUDGET"

        spent = get_spending_by_category(user_id, category)
        predicted_total = spent + abs(amount)

        if predicted_total > limit:
            return "OVER"
        elif predicted_total >= 0.9 * limit:
            return "WARNING"
        else:
            return "OK"
    except Exception as e:
        logging.error(f"Error checking budget impact: {e}")
        return "ERROR"


def check_current_budget_status(user_id, category):
    #Returns a user-friendly message about their current budget statusfor a given category.
    
    try:
        limit = get_budget_limit(user_id, category)
        if limit is None:
            return "No Budget Set"

        spent = get_spending_by_category(user_id, category)

        if spent > limit:
            return f"OVER BUDGET: Spent {spent:.2f} of {limit:.2f}"
        elif spent >= 0.9 * limit:
            return f"NEAR LIMIT: Spent {spent:.2f} of {limit:.2f}"
        else:
            return f" OK: Spent {spent:.2f} of {limit:.2f}"
    except Exception as e:
        logging.error(f"Error checking current budget status: {e}")
        return "Error Checking Budget"

from datetime import datetime, date
from .database import get_db_connection

def save_transaction(user_id, amount, category, date_input, description=''):
    try:
        if user_id <= 0:
            return False
        if amount == 0:
            return False
        if not category.strip():
            return False

        if isinstance(date_input, str):
            transaction_date = datetime.strptime(date_input, '%Y-%m-%d').date()
        elif isinstance(date_input, date):
            transaction_date = date_input
        else:
            return False

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, category.strip(), transaction_date, description.strip()))
        conn.commit()
        conn.close()
        return True
    except:
        return False
    
result = save_transaction(1, -20.0, "Food", "2023-01-03", "Lunch")
print(result)

def get_all_transactions(user_id, month=None, year=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT transaction_id, amount, category, date, description
            FROM transactions WHERE user_id = ?
        """
        params = [user_id]

        if month and year:
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
    except:
        return []

def calculate_balance(user_id):
    try:
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

def get_spending_by_category(user_id, category, month=None, year=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT COALESCE(SUM(ABS(amount)), 0) as total_spent
            FROM transactions WHERE user_id = ? AND category = ? AND amount < 0
        """
        params = [user_id, category]

        if month and year:
            query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
            params.extend([f"{month:02d}", str(year)])
        elif year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))

        cursor.execute(query, params)
        total = float(cursor.fetchone()['total_spent'])
        conn.close()
        return total
    except:
        return 0.0

def get_transaction_categories(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category FROM transactions 
            WHERE user_id = ? ORDER BY category
        """, (user_id,))
        categories = [row['category'] for row in cursor.fetchall()]
        conn.close()
        return categories
    except:
        return []
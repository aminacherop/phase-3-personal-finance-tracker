import sqlite3
import os

def setup_database():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/finance_tracker.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            CHECK (amount != 0),
            CHECK (user_id > 0),
            CHECK (category != '')
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_date ON transactions(user_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_category ON transactions(user_id, category)")

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database/finance_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn
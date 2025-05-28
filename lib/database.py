import sqlite3
import os

DATABASE_PATH = "data/finance_tracker.db"
def get_database_connection():
     os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
     connection = sqlite3.connect(DATABASE_PATH)
     connection.execute("PRAGMA foreign_keys = ON")
     connection.row_factory = sqlite3.Row
     return connection

def initialize_transactions_table():
     connection = get_database_connection()
     cursor = connection.cursor()

     cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
     

     cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
        ON transactions(user_id)
    ''')
    
     cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_date 
        ON transactions(date)
    ''')
    
     connection.commit()
     connection.close()
    
     print("Transactions table initialized successfully!")

if __name__ == "__main__":
    initialize_transactions_table()







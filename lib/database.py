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
            
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            CHECK (amount != 0),
            CHECK (user_id > 0),
            CHECK (category != '')
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            CHECK (name != ''),
            CHECK (user_id > 0)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category VARCHAR(50) NOT NULL,
            limit_amount DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            CHECK (limit_amount > 0),
            CHECK (user_id > 0),
            CHECK (category != ''),
            UNIQUE(user_id, category)
        )
    """)



    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_date ON transactions(user_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_category ON transactions(user_id, category)")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_date ON transactions(user_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_category ON transactions(user_id, category)")
    
    # Create indexes for budgets table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_user ON budgets(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_category ON budgets(user_id, category)")

    # Insert default user (user_id=1) if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, name) 
        VALUES (1, 'Default User')
    """)

    default_budgets = [
        (1, 'Food', 300.00),
        (1, 'Transport', 150.00),
        (1, 'Entertainment', 100.00),
        (1, 'Healthcare', 200.00),
        (1, 'Shopping', 250.00),
        (1, 'Utilities', 150.00)
    ]

    
    
    for user_id, category, limit_amount in default_budgets:
        cursor.execute("""
            INSERT OR IGNORE INTO budgets (user_id, category, limit_amount) 
            VALUES (?, ?, ?)
        """, (user_id, category, limit_amount))
    

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database/finance_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn


def reset_database():
    if os.path.exists('database/finance_tracker.db'):
        os.remove('database/finance_tracker.db')
        print("Existing database deleted")
    setup_database()

if __name__ == "__main__":
    setup_database()

# print("Database setup complete with users, transactions, and budgets tables!")
import sqlite3

class BudgetDB:
    DEFAULT_CATEGORIES = {"Food": 300, "Transport": 150}

    def __init__(self, db_name="budget.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()
        self._init_defaults()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    user_id INTEGER,
                    category TEXT,
                    limit_amount REAL NOT NULL,
                    PRIMARY KEY (user_id, category),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    CHECK (limit_amount > 0)
                )
            """)

    def _init_defaults(self):
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (1)")
            for category, amount in self.DEFAULT_CATEGORIES.items():
                self.conn.execute("""
                    INSERT OR IGNORE INTO budgets (user_id, category, limit_amount)
                    VALUES (1, ?, ?)
                """, (category, amount))

    def set_budget_limit(self, user_id, category, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO budgets (user_id, category, limit_amount)
                VALUES (?, ?, ?)
            """, (user_id, category, amount))

    def update_budget_limit(self, user_id, category, new_amount):
        self.set_budget_limit(user_id, category, new_amount)

    def get_budget(self, user_id, category):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT limit_amount FROM budgets 
            WHERE user_id = ? AND category = ?
        """, (user_id, category))
        result = cursor.fetchone()
        return result[0] if result else None

    def check_budget(self, user_id, category, spent_amount):
        budget = self.get_budget(user_id, category)
        if budget is None:
            return "NO_BUDGET"
        if spent_amount > budget:
            return "OVER"
        if spent_amount >= 0.9 * budget:
            return "WARNING"
        return "OK"

    def get_budget_summary(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT category, limit_amount FROM budgets 
            WHERE user_id = ?
        """, (user_id,))
        return {row[0]: {"limit": row[1], "spent": 0} for row in cursor.fetchall()}

    def close(self):
        self.conn.close()
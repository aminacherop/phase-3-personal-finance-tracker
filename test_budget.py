import unittest
import sqlite3
from budget import validate_amount, set_budget_limit, update_budget_limit, check_budget, get_budget_summary

class TestBudget(unittest.TestCase):
    def setUp(self):
        # Setup test database connection
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        self.cursor = self.conn.cursor()
        
        # Create necessary tables
        self.cursor.execute('''
            CREATE TABLE budgets (
                user_id INTEGER,
                category TEXT,
                limit_amount REAL,
                PRIMARY KEY (user_id, category)
            )
        ''')
        
        # Create transactions table for get_budget_summary tests
        self.cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                category TEXT,
                amount REAL,
                date TEXT
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        # Clean up after each test
        self.conn.close()

    def test_validate_amount(self):
        # Test valid amounts
        self.assertTrue(validate_amount(100))
        self.assertTrue(validate_amount(1.5))
        
        # Test invalid amounts
        self.assertFalse(validate_amount(0))
        self.assertFalse(validate_amount(-100))
        self.assertFalse(validate_amount("100"))
        self.assertFalse(validate_amount(None))

    def test_set_budget_limit(self):
        # Test successful budget creation
        result = set_budget_limit(1, "Food", 1000, self.conn)
        self.assertTrue(result)
        
        # Verify the budget was created
        self.cursor.execute("SELECT * FROM budgets WHERE user_id=1 AND category='Food'")
        budget = self.cursor.fetchone()
        self.assertIsNotNone(budget)
        self.assertEqual(float(budget['limit_amount']), 1000.0)
        
        # Test duplicate budget creation
        result = set_budget_limit(1, "Food", 1000, self.conn)
        self.assertFalse(result)
        
        # Test invalid amount
        result = set_budget_limit(1, "Transport", -100, self.conn)
        self.assertFalse(result)

    def test_update_budget_limit(self):
        # Setup initial budget
        set_budget_limit(1, "Food", 1000, self.conn)
        
        # Test successful update
        result = update_budget_limit(1, "Food", 1500, self.conn)
        self.assertTrue(result)
        
        # Verify the update
        self.cursor.execute("SELECT limit_amount FROM budgets WHERE user_id=1 AND category='Food'")
        budget = self.cursor.fetchone()
        self.assertEqual(float(budget['limit_amount']), 1500.0)
        
        # Test update with invalid amount
        self.assertFalse(update_budget_limit(1, "Food", -100, self.conn))
        
        # Test update of non-existent budget
        self.assertFalse(update_budget_limit(1, "NonExistent", 1000, self.conn))

    def test_check_budget(self):
        # Setup test budget
        set_budget_limit(1, "Food", 1000, self.conn)
        
        # Add some test transactions
        self.cursor.execute("""
            INSERT INTO transactions (user_id, category, amount, date)
            VALUES (1, 'Food', 500, '2025-05-31')
        """)
        self.conn.commit()
        
        # Test different spending scenarios
        self.assertEqual(check_budget(1, "Food", 500, self.conn), "OK")
        self.assertEqual(check_budget(1, "Food", 900, self.conn), "WARNING")
        self.assertEqual(check_budget(1, "Food", 1100, self.conn), "OVER")
        
        # Test non-existent budget
        self.assertEqual(check_budget(1, "NonExistent", 100, self.conn), "No Budget")

    def test_get_budget_summary(self):
        # Setup test data
        set_budget_limit(1, "Food", 1000)
        set_budget_limit(1, "Transport", 500)
        
        # Test budget summary
        summary = get_budget_summary(1)
        self.assertIsInstance(summary, list)
        
        if len(summary) > 0:
            self.assertIn("category", summary[0])
            self.assertIn("limit", summary[0])
            self.assertIn("spent", summary[0])
            self.assertIn("status", summary[0])

if __name__ == '__main__':
    unittest.main()
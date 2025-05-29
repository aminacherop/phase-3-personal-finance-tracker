import unittest
import os
from datetime import date
from lib.transaction import *
from lib.database import setup_database, get_db_connection


class TestTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_database()

    def setUp(self):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM transactions")
            conn.execute("""
                INSERT INTO transactions 
                (user_id, amount, category, date, description)
                VALUES 
                (1, -50.0, 'Food', '2023-01-01', 'Groceries'),
                (1, -30.0, 'Transport', '2023-01-02', 'Bus fare'),
                (1, 1000.0, 'Income', '2023-01-01', 'Salary')
            """)
            conn.commit()

    def test_save_transaction(self):

        result = save_transaction(1, -20.0, "Food", "2023-01-03", "Lunch")
        self.assertTrue(result)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM transactions WHERE description = 'Lunch'")
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_get_all_transactions(self):
        transactions = get_all_transactions(1)

        self.assertEqual(len(transactions), 3)

        self.assertEqual(transactions[0]['category'], "Transport")

    def test_calculate_balance(self):
        balance = calculate_balance(1)

        self.assertEqual(balance, 920.0)

    def test_get_spending_by_category(self):

        spending = get_spending_by_category(1, "Food")
        self.assertEqual(spending, 50.0)

    def test_get_transaction_categories(self):
        categories = get_transaction_categories(1)
        self.assertEqual(len(categories), 3)
        self.assertIn("Food", categories)
        self.assertIn("Transport", categories)


if __name__ == '_main_':
    unittest.main()

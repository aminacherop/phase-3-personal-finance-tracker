import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import json
from unittest.mock import patch, MagicMock
from io import StringIO
from cli import BudgetTracker

class TestBudgetCLI(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_data.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_transaction(self):
        """Test adding a new transaction"""
        tracker = BudgetTracker()
        tracker.DATA_FILE = self.test_file
        tracker.transactions = []  # Ensure empty before test

        with patch('builtins.input', side_effect=['100', 'Salary', '']):
            tracker.add_transaction()
            self.assertEqual(len(tracker.transactions), 1)
            self.assertEqual(tracker.transactions[0]['amount'], 100.0)
            self.assertTrue(os.path.exists(self.test_file))

    def test_view_transactions_empty(self):
        """Test viewing empty transactions"""
        tracker = BudgetTracker()
        tracker.transactions = []  # Ensure empty
        with patch('sys.stdout', new=StringIO()) as fake_out:
            tracker.view_transactions()
            self.assertIn("No transactions", fake_out.getvalue())

    def test_budget_overspending(self):
        """Test budget overspending alert"""
        tracker = BudgetTracker()
        tracker.budgets = {"Food": 200}
        tracker.transactions = [{"amount": -250, "category": "Food", "date": "2023-01-01", "note": ""}]
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            tracker.view_budgets()
            output = fake_out.getvalue()
            self.assertIn("OVER", output)
            self.assertIn("❌", output)

    def test_data_persistence(self):
        """Test data saving and loading"""
        tracker = BudgetTracker()
        tracker.DATA_FILE = self.test_file
        tracker.transactions = [{"amount": 50.0, "category": "Test", "date": "2023-01-01", "note": ""}]
        tracker.budgets = {"Test": 100}
        tracker.save_data()
        
        new_tracker = BudgetTracker()
        new_tracker.DATA_FILE = self.test_file
        new_tracker.load_data()
        self.assertEqual(len(new_tracker.transactions), 1)
        self.assertEqual(new_tracker.budgets["Test"], 100)

    @patch('builtins.input', side_effect=['3', '1'])  # Manage budgets -> View
    def test_manage_budgets_view(self, mock_input):
        """Test budget management menu"""
        tracker = BudgetTracker()
        tracker.budgets = {"Test": 100}
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            tracker.manage_budgets()
            self.assertIn("Current Budgets", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main()
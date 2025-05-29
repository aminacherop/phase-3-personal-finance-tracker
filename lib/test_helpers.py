import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
from io import StringIO
from unittest.mock import patch
from helpers import get_currency_input, print_table

class TestHelpers(unittest.TestCase):
    # Currency Input Tests
    @patch('builtins.input', side_effect=['50.25'])
    def test_valid_currency_input(self, mock_input):
        """Test valid numeric input"""
        self.assertEqual(get_currency_input("Amount: "), 50.25)

    @patch('builtins.input', side_effect=['abc', '20'])
    def test_invalid_then_valid_input(self, mock_input):
        """Test recovery from invalid input"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = get_currency_input("Amount: ")
            self.assertIn("Invalid amount", fake_out.getvalue())
            self.assertEqual(result, 20.0)

    @patch('builtins.input', side_effect=['-15.99'])
    def test_negative_input(self, mock_input):
        """Test negative values (expenses)"""
        self.assertEqual(get_currency_input("Amount: "), -15.99)

    @patch('builtins.input', side_effect=['0', '10'])
    def test_zero_input_rejection(self, mock_input):
        """Test rejection of zero amounts"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = get_currency_input("Amount: ")
            self.assertIn("can't be zero", fake_out.getvalue())
            self.assertEqual(result, 10.0)

    # Table Formatting Tests
    def test_print_table_basic(self):
        """Test basic table formatting"""
        headers = ["Name", "Age"]
        rows = [["Alice", 30], ["Bob", 25]]
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_table(headers, rows)
            output = fake_out.getvalue()
            self.assertIn("Alice", output)
            self.assertIn("Bob", output)
            self.assertIn("Name", output)
            self.assertIn("Age", output)

    def test_print_table_empty_data(self):
        """Test table with empty data"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_table([], [])
            self.assertIn("No data", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3
"""
Debug script to check database operations
"""

from database import get_db_connection, setup_database
from transaction import save_transaction_with_budget_alert
from budget import set_budget_limit, update_budget_limit
from datetime import date

def check_database_tables():
    """Check if tables exist and show their contents"""
    print("=== DATABASE TABLES CHECK ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table
        print("\n1. USERS TABLE:")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        if users:
            for user in users:
                print(f"   User ID: {user['user_id']}, Name: {user['name']}")
        else:
            print("   No users found!")
        
        # Check transactions table
        print("\n2. TRANSACTIONS TABLE:")
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        tx_count = cursor.fetchone()['count']
        print(f"   Total transactions: {tx_count}")
        
        if tx_count > 0:
            cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5")
            transactions = cursor.fetchall()
            print("   Recent transactions:")
            for tx in transactions:
                print(f"   - ID: {tx['transaction_id']}, Amount: {tx['amount']}, Category: {tx['category']}, Date: {tx['date']}")
        
        # Check budgets table
        print("\n3. BUDGETS TABLE:")
        cursor.execute("SELECT * FROM budgets")
        budgets = cursor.fetchall()
        if budgets:
            print("   Budgets:")
            for budget in budgets:
                print(f"   - Category: {budget['category']}, Limit: {budget['limit_amount']}")
        else:
            print("   No budgets found!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

def test_transaction_save():
    """Test saving a transaction"""
    print("\n=== TESTING TRANSACTION SAVE ===")
    
    try:
        # Test basic transaction save
        result = save_transaction_with_budget_alert(
            user_id=1, 
            amount=-50, 
            category="Food", 
            date_input=date.today(), 
            description="Test transaction"
        )
        print(f"Transaction save result: {result}")
        
        # Check if it was actually saved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE description = 'Test transaction'")
        count = cursor.fetchone()['count']
        print(f"Test transactions in database: {count}")
        conn.close()
        
    except Exception as e:
        print(f"Error testing transaction: {e}")

def test_budget_operations():
    """Test budget operations"""
    print("\n=== TESTING BUDGET OPERATIONS ===")
    
    try:
        # Test setting a new budget
        print("Testing set_budget_limit...")
        result1 = set_budget_limit(1, "TestCategory", 500.0)
        print(f"Set budget result: {result1}")
        
        # Test updating budget
        print("Testing update_budget_limit...")
        result2 = update_budget_limit(1, "Food", 400.0)
        print(f"Update budget result: {result2}")
        
        # Check if budgets were saved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM budgets WHERE user_id = 1")
        budgets = cursor.fetchall()
        print("Current budgets in database:")
        for budget in budgets:
            print(f"   - {budget['category']}: ${budget['limit_amount']}")
        conn.close()
        
    except Exception as e:
        print(f"Error testing budgets: {e}")

def check_database_file():
    """Check if database file exists and its location"""
    print("\n=== DATABASE FILE CHECK ===")
    
    import os
    db_path = "database/finance_tracker.db"
    
    if os.path.exists(db_path):
        print(f"✅ Database file exists at: {os.path.abspath(db_path)}")
        file_size = os.path.getsize(db_path)
        print(f"   File size: {file_size} bytes")
    else:
        print(f"❌ Database file not found at: {os.path.abspath(db_path)}")
        print("   Attempting to create database...")
        setup_database()
        if os.path.exists(db_path):
            print("✅ Database created successfully!")
        else:
            print("❌ Failed to create database!")

def main():
    """Run all debug checks"""
    print("🔍 FINANCE TRACKER DEBUG SCRIPT")
    print("=" * 40)
    
    check_database_file()
    check_database_tables()
    test_transaction_save()
    test_budget_operations()
    
    print("\n" + "=" * 40)
    print("Debug complete! Check the output above for any issues.")

if __name__ == "__main__":
    main()
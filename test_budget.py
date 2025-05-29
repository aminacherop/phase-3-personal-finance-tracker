import pytest
from budget import BudgetDB

@pytest.fixture
def db():
    # Use in-memory SQLite DB for isolation
    bdb = BudgetDB(":memory:")
    yield bdb
    bdb.close()

def test_no_budget_returns_no_budget(db):
    # user 2 does not exist, nor does category "Misc"
    assert db.check_budget(2, "Misc", 10) == "NO_BUDGET"

def test_over_budget(db):
    db.set_budget_limit(1, "TestCat", 100)
    assert db.check_budget(1, "TestCat", 150) == "OVER"

def test_warning_budget(db):
    db.set_budget_limit(1, "TestCat", 100)
    # 90 is exactly 90% of 100
    assert db.check_budget(1, "TestCat", 90) == "WARNING"
    # 99 is also >= 90% of 100
    assert db.check_budget(1, "TestCat", 99) == "WARNING"

def test_ok_budget(db):
    db.set_budget_limit(1, "TestCat", 100)
    # 89 is less than 90% of 100
    assert db.check_budget(1, "TestCat", 89) == "OK"

def test_get_budget_summary(db):
    db.set_budget_limit(1, "Groceries", 200)
    summary = db.get_budget_summary(1)
    assert "Groceries" in summary
    assert summary["Groceries"]["limit"] == 200
    assert summary["Groceries"]["spent"] == 0
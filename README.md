# 💰 Personal Finance Tracker

A simple CLI-based personal finance tracker built with Python and SQLite. Easily add users, log transactions, and track expenses with automatic budget alerts.

---

## 📌 Project Statement

The Personal Finance Tracker is designed to help users manage and track their income and expenses using a command-line interface. It supports adding users and transactions, categorizing expenses, and notifying users when a transaction exceeds a set budget threshold.

---

## 🛠️ Technologies Used

- **Python 3.x**
- **SQLite** (via Python’s `sqlite3` module)
- Standard Python Libraries (`datetime`, `argparse`, `os`, etc.)

---

## 🧪 MVP Features & Demo

### ✅ MVP Features
- Add users to the database.
- Add transactions (with user ID, amount, category, date, description).
- Store all data in an SQLite database.
- Simple budget alert if spending exceeds a threshold.

### 🎥 Demo

```
# Add a user
python -m lib.cli add-user Alice

# Add a transaction for the user
python -m lib.cli add-transaction 1 500 Groceries 2025-06-01 "Weekly shopping"

# If a transaction exceeds 1000, an alert will show
python -m lib.cli add-transaction 1 1200 Rent 2025-06-01 "Monthly rent"
```
## 🚀 Getting Started
1. Clone the Repository
```
git clone https://github.com/aminacherop/phase-3-personal-finance-tracker
cd personal-finance-tracker
```
2. Create Virtual Environment (optional but recommended)
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies
```
# No external dependencies needed. All standard libraries.
```
4. Set Up the Database
```
python -m lib.database
```
5. Run the CLI Tool
```
# Add a user
python -m lib.cli add-user Alice

# Add a transaction
python -m lib.cli add-transaction 1 1200 Rent 2025-06-01 "Monthly rent"
```
## 🧭 Command Reference
```
# Add a new user
python -m lib.cli add-user <name>

# Add a transaction
python -m lib.cli add-transaction <user_id> <amount> <category> <date> <description>
```
Example:

```
python -m lib.cli add-user Bob
python -m lib.cli add-transaction 1 450 Food 2025-06-01 "Lunch at cafe"
```
## 📁 Project Structure
```
personal-finance-tracker/
├── db/
│   └── finance.db             # SQLite database file
├── lib/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface logic
│   ├── database.py            # Setup script for database/tables
│   └── models.py              # Models and helpers
├── README.md
└── .gitignore
```
## 🔮 Future Plans
- Budget limits per user or category

- View transaction history with filters (by date, category, user)

- Summarized reports (daily, monthly, yearly)

- Export to CSV/Excel

- Web dashboard with charts and graphs

- User login and session management

- Mobile app using Flutter or React Native

## 🤝 Contributing
We welcome contributions!

```
# Fork the repository
# Create a feature branch
git checkout -b feature/my-feature

# Commit your changes
git commit -m "Add my feature"

# Push to GitHub
git push origin feature/my-feature

# Open a Pull Request
```
## 📃 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.

# 💸 Budget Tracker CLI App

A command-line budget tracking application built in Python, designed for personal finance management. Users can record transactions, view summaries, and monitor spending against set budgets — all from the terminal.

---

## 🧑‍💻 Team Roles

### 🖥️ Shuaib – CLI Interface
- Builds the entire command-line interface
- Manages user input, menu display, and confirmation prompts
- Formats output with color coding for clarity (e.g., green for success, red for warnings)
- Displays recent activity, balance, and summaries in a user-friendly format

### 🌟 Kevin – Budget & User Management
- Maintains the user and budget tables (always uses `user_id=1`)
- Implements:
  - `set_budget_limit(user_id, category, amount)`
  - `update_budget_limit(user_id, category, new_amount)`
  - `check_budget(user_id, category, spent_amount)`
  - `get_budget_summary(user_id)`
- Provides default budget categories and amount validation

### 💰 Amina – Transaction System
- Handles storage and retrieval of transactions
- Implements:
  - `save_transaction(user_id, amount, category, date)`
  - `get_all_transactions(user_id)`
  - `calculate_balance(user_id)`
  - `get_recent_transactions(user_id, limit=5)`
  - `get_all_transactions(user_id, month, year)`
- Ensures transaction data is valid and complete

---

## 📦 Features

- ✅ Record income and expense transactions
- 📊 View spending summaries by category
- 🎯 Track budgets with live status feedback (OK or OVER)
- 💬 User-friendly CLI with prompts and color-coded output
- 🧠 Recent activity log and monthly filters
- 🧪 Input validation to prevent errors

---

## 🛠️ Technologies Used

- **Python 3.10+**
- `colorama` for terminal colors
- Custom helper functions for currency input and table printing

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/budget-cli-app.git
   cd budget-cli-app
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the app

bash
Copy
Edit
python main.py
📁 Project Structure
graphql
Copy
Edit
budget-cli-app/
├── main.py                # Launches the CLI (Shuaib's domain)
├── helpers.py             # Shared utilities (input formatting, table display)
├── budget.py              # Budget logic (Kevin's domain)
├── transactions.py        # Transaction logic (Amina's domain)
└── README.md              # Project documentation
🤝 Contribution Workflow
Each team member works on their dedicated feature branch:

shuaib/cli-enhancements

kevin/budget-summary

amina/monthly-filter

Code reviews done via Pull Requests

All changes merged into main after review and testing

📌 Notes
Always use user_id = 1 for simplicity

No user authentication (by design)

All backend logic is separated from CLI interface


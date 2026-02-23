**Penny Track - Expense & Income Tracker**

Penny Track is a simple, interactive expense and income tracker built in Python. It allows you to manage your finances efficiently by recording your expenses and income, categorizing them, and providing insightful reports and analysis. You can set budgets, track recurring expenses, compare different time periods, and even generate backups of your financial data.

Key Features

Add Expenses & Income: Record both expenses and income, specifying amounts, categories, and notes. You can also add recurring expenses with customizable frequencies (daily, weekly, monthly).

Budget Management: Set and manage monthly budgets for different categories. The app will notify you when you're close to or exceeding your budget.

Recurring Expenses: Easily manage recurring expenses like subscriptions, rent, etc. The app will automatically add them based on the specified frequency.

Search & Filter: Filter your expenses based on category, date range, amount, keywords in notes, and more.

Reports & Analysis:

Monthly summary report of your income, expenses, and net balance.

Statistics dashboard with overall spending trends, highest expenses, and most frequent categories.

Comparison reports to compare spending across different months or time periods.

Backup & Export: Create backups of your data and export reports in CSV, JSON, or text format.

Settings: Customize settings such as currency symbols, color usage, and more.

Installation

Clone or download the repository:

git clone https://github.com/yourusername/penny-track.git
cd penny-track


Install required dependencies (if needed):

pip install -r requirements.txt


Run the application:

python PennyTrack.py

Usage

Once the application starts, you will be greeted with the main menu. The following are the options you can choose from:

Expenses & Income

Add Expense: Add a new expense entry.

Add Income: Add a new income entry.

View All Entries: View all expenses and income entries.

Edit Entry: Edit an existing expense or income entry.

Delete Entry: Delete an expense or income entry.

Reports & Analysis

Monthly Summary: View a summary of your expenses and income for the current month.

Statistics Dashboard: View overall statistics such as total expenses, income, and category breakdown.

Search & Filter: Search and filter your expenses based on various criteria.

Comparison Report: Compare different periods (e.g., month vs previous month or same month last year).

Budget & Planning

Manage Budgets: Set, update, or delete category budgets.

Manage Recurring Expenses: Manage recurring expenses and set their frequency.

Tools

Export Data: Export your expenses data to CSV, JSON, or a text report.

Backup Data: Backup all your financial data to a separate directory.

Settings

Settings: Adjust application settings like currency symbol and color usage.

Exit

Exit: Exit the application.

Settings

You can configure some basic settings:

Toggle Colors: Enable or disable colored output in the terminal.

Currency Symbol: Customize the currency symbol to match your local currency.

Data Files

The app stores your data in local files:

expenses.csv: Stores all your expenses and income entries.

budgets.json: Stores your category-specific budgets.

recurring.json: Stores your recurring expenses configuration.

config.json: Stores configuration settings (e.g., currency symbol, color usage).

Backup & Export

Backup: Create backups of your data files in a timestamped folder.

Export Data: Export your expenses in CSV, JSON, or as a text report.

Requirements

Python 3.x

Dependencies (if any) listed in the requirements.txt file.

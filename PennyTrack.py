import csv
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import shutil


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        Colors.RED = Colors.GREEN = Colors.YELLOW = ''
        Colors.BLUE = Colors.MAGENTA = Colors.CYAN = ''
        Colors.WHITE = Colors.BOLD = Colors.RESET = ''


class ExpenseTracker:
    def __init__(self, filename="expenses.csv", budgets_file="budgets.json", 
                 recurring_file="recurring.json", config_file="config.json"):
        self.filename = filename
        self.budgets_file = budgets_file
        self.recurring_file = recurring_file
        self.config_file = config_file
        
        self.expenses = []
        self.budgets = {}
        self.recurring_expenses = []
        self.config = self._load_config()
        
        self._initialize_files()
        self._load_expenses()
        self._load_budgets()
        self._load_recurring()
        self._process_recurring_expenses()
    
    def _load_config(self):
        default_config = {
            "use_colors": True,
            "currency_symbol": "$",
            "date_format": "%Y-%m-%d",
            "backup_enabled": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except:
                return default_config
        return default_config
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _initialize_files(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Date', 'Amount', 'Category', 'Note', 'Type'])
            print(f"Created new expense file: {self.filename}")
        
        if not os.path.exists(self.budgets_file):
            with open(self.budgets_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.recurring_file):
            with open(self.recurring_file, 'w') as f:
                json.dump([], f)
    
    def _load_expenses(self):
        self.expenses = []
        with open(self.filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.expenses.append(row)
    
    def _load_budgets(self):
        try:
            with open(self.budgets_file, 'r') as f:
                self.budgets = json.load(f)
        except:
            self.budgets = {}
    
    def _save_budgets(self):
        with open(self.budgets_file, 'w') as f:
            json.dump(self.budgets, f, indent=2)
    
    def _load_recurring(self):
        try:
            with open(self.recurring_file, 'r') as f:
                self.recurring_expenses = json.load(f)
        except:
            self.recurring_expenses = []
    
    def _save_recurring(self):
        with open(self.recurring_file, 'w') as f:
            json.dump(self.recurring_expenses, f, indent=2)
    
    def _get_next_id(self):
        if not self.expenses:
            return "1"
        max_id = max([int(e.get('ID', 0)) for e in self.expenses])
        return str(max_id + 1)
    
    def _process_recurring_expenses(self):
        today = datetime.now().date()
        added = 0
        
        for recurring in self.recurring_expenses:
            last_added = datetime.strptime(recurring['last_added'], '%Y-%m-%d').date()
            frequency = recurring['frequency']
            should_add = False
            if frequency == 'daily':
                should_add = (today - last_added).days >= 1
            elif frequency == 'weekly':
                should_add = (today - last_added).days >= 7
            elif frequency == 'monthly':
                should_add = (today - last_added).days >= 28

            if should_add:
                expense_id = self._get_next_id()
                with open(self.filename, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        expense_id,
                        today.strftime('%Y-%m-%d'),
                        recurring['amount'],
                        recurring['category'],
                        recurring['note'],
                        'expense'
                    ])

                recurring['last_added'] = today.strftime('%Y-%m-%d')
                added += 1
        
        if added > 0:
            self._save_recurring()
            self._load_expenses()
            print(f"{Colors.GREEN}✓ Added {added} recurring expense(s){Colors.RESET}")
    
    def add_expense(self, is_income=False):
        """Add a new expense or income entry"""
        entry_type = "Income" if is_income else "Expense"
        print(f"\n--- Add New {entry_type} ---")
        
        while True:
            try:
                amount = float(input("Amount: $"))
                if amount <= 0:
                    print("Amount must be positive. Try again.")
                    continue
                break
            except ValueError:
                print("Invalid amount. Please enter a number.")
        
        if not is_income:
            recent_categories = list(set([e['Category'] for e in self.expenses[-10:] if e.get('Type', 'expense') == 'expense']))
            if recent_categories:
                print(f"Recent categories: {', '.join(recent_categories[:5])}")
        
        category = input("Category: ").strip()
        if not category:
            category = "Uncategorized"
        
        date_input = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if not date_input:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                date = date_input
            except ValueError:
                print("Invalid date format. Using today's date.")
                date = datetime.now().strftime("%Y-%m-%d")
        
        note = input("Note (optional): ").strip()
        
        if not is_income:
            recurring = input("Is this a recurring expense? (y/n): ").strip().lower() == 'y'
            if recurring:
                print("Frequency: 1) Daily  2) Weekly  3) Monthly")
                freq_choice = input("Select frequency (1-3): ").strip()
                frequency_map = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
                frequency = frequency_map.get(freq_choice, 'monthly')
                
                self.recurring_expenses.append({
                    'amount': f"{amount:.2f}",
                    'category': category,
                    'note': note,
                    'frequency': frequency,
                    'last_added': date
                })
                self._save_recurring()
                print(f"{Colors.GREEN}✓ Set up as recurring {frequency} expense{Colors.RESET}")
        
        expense_id = self._get_next_id()
        entry_type_code = 'income' if is_income else 'expense'
        
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([expense_id, date, f"{amount:.2f}", category, note, entry_type_code])
        
        color = Colors.GREEN if is_income else Colors.YELLOW
        print(f"\n{color}✓ {entry_type} added: ${amount:.2f} for {category} on {date}{Colors.RESET}")
        self._load_expenses()
        
        if not is_income:
            self._check_budget_alert(category, date)
    
    def _check_budget_alert(self, category, date):

        month_key = date[:7]
        budget_key = f"{month_key}:{category}"
        
        if budget_key in self.budgets:
            budget_amount = self.budgets[budget_key]
            month_expenses = [e for e in self.expenses 
                            if e['Date'].startswith(month_key) 
                            and e['Category'] == category
                            and e.get('Type', 'expense') == 'expense']
            total_spent = sum(float(e['Amount']) for e in month_expenses)
            
            percentage = (total_spent / budget_amount) * 100
            
            if percentage >= 100:
                print(f"{Colors.RED}WARNING: Over budget for {category}! (${total_spent:.2f}/${budget_amount:.2f}){Colors.RESET}")
            elif percentage >= 80:
                print(f"{Colors.YELLOW}Alert: {category} at {percentage:.0f}% of budget (${total_spent:.2f}/${budget_amount:.2f}){Colors.RESET}")
    
    def edit_expense(self):
        """Edit an existing expense"""
        if not self.expenses:
            print("No expenses to edit.")
            return
        
        print("\n--- Recent Expenses ---")
        recent = sorted(self.expenses, key=lambda x: x['Date'], reverse=True)[:20]
        for exp in recent:
            exp_type = "📈" if exp.get('Type') == 'income' else "💰"
            print(f"{exp_type} ID: {exp['ID']:<4} | {exp['Date']} | ${float(exp['Amount']):>8.2f} | {exp['Category']:<15} | {exp['Note'][:30]}")
        
        expense_id = input("\nEnter ID to edit (or 'cancel'): ").strip()
        if expense_id.lower() == 'cancel':
            return
        

        expense = next((e for e in self.expenses if e['ID'] == expense_id), None)
        if not expense:
            print(f"{Colors.RED}Expense ID not found.{Colors.RESET}")
            return
        
        print(f"\nEditing expense: {expense['Date']} | ${expense['Amount']} | {expense['Category']}")
        print("Press Enter to keep current value")
        
        new_amount = input(f"Amount (${expense['Amount']}): ").strip()
        new_category = input(f"Category ({expense['Category']}): ").strip()
        new_date = input(f"Date ({expense['Date']}): ").strip()
        new_note = input(f"Note ({expense['Note']}): ").strip()
        
        if new_amount:
            expense['Amount'] = f"{float(new_amount):.2f}"
        if new_category:
            expense['Category'] = new_category
        if new_date:
            expense['Date'] = new_date
        if new_note:
            expense['Note'] = new_note

        self._rewrite_expenses_file()
        print(f"{Colors.GREEN}✓ Expense updated{Colors.RESET}")

    def delete_expense(self):
        if not self.expenses:
            print("No expenses to delete.")
            return

        print("\n--- Recent Expenses ---")
        recent = sorted(self.expenses, key=lambda x: x['Date'], reverse=True)[:20]
        for exp in recent:
            exp_type = "" if exp.get('Type') == 'income' else ""
            print(f"{exp_type} ID: {exp['ID']:<4} | {exp['Date']} | ${float(exp['Amount']):>8.2f} | {exp['Category']:<15} | {exp['Note'][:30]}")
        
        expense_id = input("\nEnter ID to delete (or 'cancel'): ").strip()
        if expense_id.lower() == 'cancel':
            return
        
        expense = next((e for e in self.expenses if e['ID'] == expense_id), None)
        if not expense:
            print(f"{Colors.RED}Expense ID not found.{Colors.RESET}")
            return
        
        print(f"\nDelete: {expense['Date']} | ${expense['Amount']} | {expense['Category']} | {expense['Note']}")
        confirm = input(f"{Colors.YELLOW}Are you sure? (yes/no): {Colors.RESET}").strip().lower()
        
        if confirm == 'yes':
            self.expenses.remove(expense)
            self._rewrite_expenses_file()
            print(f"{Colors.GREEN}✓ Expense deleted{Colors.RESET}")
        else:
            print("Deletion cancelled.")
    
    def _rewrite_expenses_file(self):
        """Rewrite the entire expenses file"""
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Date', 'Amount', 'Category', 'Note', 'Type'])
            for expense in self.expenses:
                writer.writerow([
                    expense['ID'],
                    expense['Date'],
                    expense['Amount'],
                    expense['Category'],
                    expense['Note'],
                    expense.get('Type', 'expense')
                ])
        self._load_expenses()
    
    def search_expenses(self):
        """Search and filter expenses"""
        print("\n--- Search & Filter ---")
        print("1. By category")
        print("2. By date range")
        print("3. By amount range")
        print("4. By keyword in notes")
        print("5. By type (expense/income)")
        
        choice = input("\nSelect search type (1-5): ").strip()
        
        filtered = self.expenses[:]
        
        if choice == '1':
            category = input("Enter category: ").strip()
            filtered = [e for e in filtered if e['Category'].lower() == category.lower()]
        
        elif choice == '2':
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            filtered = [e for e in filtered if start_date <= e['Date'] <= end_date]
        
        elif choice == '3':
            min_amount = float(input("Minimum amount: $").strip())
            max_amount = float(input("Maximum amount: $").strip())
            filtered = [e for e in filtered if min_amount <= float(e['Amount']) <= max_amount]
        
        elif choice == '4':
            keyword = input("Enter keyword: ").strip().lower()
            filtered = [e for e in filtered if keyword in e['Note'].lower()]
        
        elif choice == '5':
            print("1. Expenses only")
            print("2. Income only")
            type_choice = input("Select (1-2): ").strip()
            search_type = 'expense' if type_choice == '1' else 'income'
            filtered = [e for e in filtered if e.get('Type', 'expense') == search_type]
        
        else:
            print("Invalid choice.")
            return
        
        if not filtered:
            print(f"\n{Colors.YELLOW}No results found.{Colors.RESET}")
            return
        
        print(f"\n--- Search Results ({len(filtered)} found) ---")
        sorted_filtered = sorted(filtered, key=lambda x: x['Date'])
        
        print(f"\n{'ID':<5} {'Date':<12} {'Amount':>10} {'Category':<20} {'Note':<30}")
        print("-" * 80)
        
        total = 0
        for expense in sorted_filtered:
            amount = float(expense['Amount'])
            total += amount if expense.get('Type', 'expense') == 'expense' else -amount
            note = expense['Note'][:27] + "..." if len(expense['Note']) > 30 else expense['Note']
            exp_type = "+" if expense.get('Type') == 'income' else "-"
            print(f"{expense['ID']:<5} {expense['Date']:<12} {exp_type}${amount:>8.2f} {expense['Category']:<20} {note:<30}")
        
        print("-" * 80)
        print(f"{'TOTAL':<5} {'':12} ${total:>9.2f}")
    
    def view_all_expenses(self):
        print("\n--- All Expenses ---")
        
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        sorted_expenses = sorted(self.expenses, key=lambda x: x['Date'])
        
        print(f"\n{'ID':<5} {'Date':<12} {'Amount':>10} {'Category':<20} {'Note':<30}")
        print("-" * 80)
        
        total_expenses = 0
        total_income = 0
        
        for expense in sorted_expenses:
            amount = float(expense['Amount'])
            is_income = expense.get('Type', 'expense') == 'income'
            
            if is_income:
                total_income += amount
            else:
                total_expenses += amount
            
            note = expense['Note'][:27] + "..." if len(expense['Note']) > 30 else expense['Note']
            sign = "+" if is_income else "-"
            color = Colors.GREEN if is_income else Colors.WHITE
            print(f"{color}{expense['ID']:<5} {expense['Date']:<12} {sign}${amount:>8.2f} {expense['Category']:<20} {note:<30}{Colors.RESET}")
        
        print("-" * 80)
        print(f"{Colors.RED}Expenses: ${total_expenses:>9.2f}{Colors.RESET}")
        print(f"{Colors.GREEN}Income:   ${total_income:>9.2f}{Colors.RESET}")
        print(f"{Colors.CYAN}Net:      ${(total_income - total_expenses):>9.2f}{Colors.RESET}")
        print(f"\nTotal entries: {len(sorted_expenses)}")
    
    def monthly_summary(self):
        print("\n--- Monthly Summary ---")
        
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        month_input = input("Enter month (YYYY-MM, or press Enter for current month): ").strip()
        
        if not month_input:
            month_input = datetime.now().strftime("%Y-%m")
        
        try:
            datetime.strptime(month_input + "-01", "%Y-%m-%d")
        except ValueError:
            print("Invalid format. Please use YYYY-MM (e.g., 2026-04)")
            return
        
        month_expenses = [e for e in self.expenses if e['Date'].startswith(month_input) and e.get('Type', 'expense') == 'expense']
        month_income = [e for e in self.expenses if e['Date'].startswith(month_input) and e.get('Type') == 'income']
        
        if not month_expenses and not month_income:
            print(f"\nNo entries found for {month_input}")
            return
        
        total_expenses = sum(float(e['Amount']) for e in month_expenses)
        total_income = sum(float(e['Amount']) for e in month_income)
        category_totals = defaultdict(float)
        
        for expense in month_expenses:
            category_totals[expense['Category']] += float(expense['Amount'])
        
        month_name = datetime.strptime(month_input + "-01", "%Y-%m-%d").strftime("%B %Y")
        print(f"\n{'='*50}")
        print(f"  {month_name}")
        print(f"{'='*50}")
        print(f"{Colors.GREEN}Income:   ${total_income:>10.2f}{Colors.RESET}")
        print(f"{Colors.RED}Expenses: ${total_expenses:>10.2f}{Colors.RESET}")
        print(f"{Colors.CYAN}Net:      ${(total_income - total_expenses):>10.2f}{Colors.RESET}")
        
        if month_expenses:
            print(f"\n{Colors.BOLD}Spending by Category:{Colors.RESET}")
            print("-" * 50)
            
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_categories:
                percentage = (amount / total_expenses) * 100
                
                budget_key = f"{month_input}:{category}"
                budget_status = ""
                bar_color = Colors.WHITE
                
                if budget_key in self.budgets:
                    budget = self.budgets[budget_key]
                    budget_pct = (amount / budget) * 100
                    if budget_pct > 100:
                        bar_color = Colors.RED
                        budget_status = f" {Colors.RED}Over budget!{Colors.RESET}"
                    elif budget_pct > 80:
                        bar_color = Colors.YELLOW
                    else:
                        bar_color = Colors.GREEN
                    budget_status = f" (${amount:.2f}/${budget:.2f})" + budget_status
                
                bar_length = int(percentage / 5)
                bar = bar_color + "█" * bar_length + "░" * (20 - bar_length) + Colors.RESET
                
                print(f"{category:<20} {bar} ${amount:>8.2f} ({percentage:>5.1f}%){budget_status}")
            
            print("=" * 50)
            
            days_in_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            avg_daily = total_expenses / days_in_month.day
            print(f"Daily average: ${avg_daily:.2f}")
    
    def statistics_dashboard(self):
        print("\n" + "="*60)
        print(f"{Colors.BOLD}{'STATISTICS DASHBOARD':^60}{Colors.RESET}")
        print("="*60)
        
        if not self.expenses:
            print("No data available yet.")
            return
        
        expenses_only = [e for e in self.expenses if e.get('Type', 'expense') == 'expense']
        income_only = [e for e in self.expenses if e.get('Type') == 'income']
        
        if not expenses_only:
            print("No expense data available yet.")
            return
        
        total_expense = sum(float(e['Amount']) for e in expenses_only)
        total_income = sum(float(e['Amount']) for e in income_only)
        avg_expense = total_expense / len(expenses_only)
        
        highest = max(expenses_only, key=lambda x: float(x['Amount']))
        
        category_counts = defaultdict(int)
        category_totals = defaultdict(float)
        for exp in expenses_only:
            category_counts[exp['Category']] += 1
            category_totals[exp['Category']] += float(exp['Amount'])
        
        most_frequent_cat = max(category_counts.items(), key=lambda x: x[1])
        most_expensive_cat = max(category_totals.items(), key=lambda x: x[1])
        
        dates = sorted([datetime.strptime(e['Date'], '%Y-%m-%d') for e in expenses_only])
        first_date = dates[0]
        last_date = dates[-1]
        days_tracked = (last_date - first_date).days + 1
        

        print(f"\n{Colors.CYAN}Overall Statistics:{Colors.RESET}")
        print(f"  Total Expenses:        ${total_expense:,.2f}")
        print(f"  Total Income:          ${total_income:,.2f}")
        print(f"  Net:                   ${(total_income - total_expense):,.2f}")
        print(f"  Number of Expenses:    {len(expenses_only)}")
        print(f"  Average Expense:       ${avg_expense:.2f}")
        print(f"  Days Tracked:          {days_tracked}")
        print(f"  Average Daily Spend:   ${total_expense/days_tracked:.2f}")
        
        print(f"\n{Colors.YELLOW}Highest Expense:{Colors.RESET}")
        print(f"  ${highest['Amount']} - {highest['Category']} on {highest['Date']}")
        print(f"  Note: {highest['Note']}")
        
        print(f"\n{Colors.MAGENTA}Category Analysis:{Colors.RESET}")
        print(f"  Most Frequent:         {most_frequent_cat[0]} ({most_frequent_cat[1]} times)")
        print(f"  Most Expensive:        {most_expensive_cat[0]} (${most_expensive_cat[1]:.2f})")
        print(f"  Total Categories:      {len(category_counts)}")

        if len(expenses_only) >= 10:
            recent_10 = expenses_only[-10:]
            older_10 = expenses_only[-20:-10] if len(expenses_only) >= 20 else expenses_only[:-10]
            
            recent_avg = sum(float(e['Amount']) for e in recent_10) / len(recent_10)
            older_avg = sum(float(e['Amount']) for e in older_10) / len(older_10)
            
            trend = "↑ Increasing" if recent_avg > older_avg else "↓ Decreasing"
            trend_color = Colors.RED if recent_avg > older_avg else Colors.GREEN
            
            print(f"\n{Colors.CYAN}Spending Trend:{Colors.RESET}")
            print(f"  {trend_color}{trend}{Colors.RESET} (Recent avg: ${recent_avg:.2f} vs ${older_avg:.2f})")
        
        print(f"\n{Colors.BOLD}Top 5 Expenses:{Colors.RESET}")
        top_5 = sorted(expenses_only, key=lambda x: float(x['Amount']), reverse=True)[:5]
        for i, exp in enumerate(top_5, 1):
            print(f"  {i}. ${exp['Amount']:<8} - {exp['Category']:<15} ({exp['Date']})")
        
        print("="*60)
    
    def manage_budgets(self):
        """Manage category budgets"""
        print("\n--- Budget Management ---")
        print("1. Set/Update budget")
        print("2. View all budgets")
        print("3. Delete budget")
        print("4. Budget status (current month)")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            month = input("Month (YYYY-MM, or Enter for current): ").strip()
            if not month:
                month = datetime.now().strftime("%Y-%m")
            
            category = input("Category: ").strip()
            amount = float(input("Budget amount: $").strip())
            
            budget_key = f"{month}:{category}"
            self.budgets[budget_key] = amount
            self._save_budgets()
            print(f"{Colors.GREEN}✓ Budget set: {category} = ${amount:.2f} for {month}{Colors.RESET}")
        
        elif choice == '2':
            if not self.budgets:
                print("No budgets set.")
                return
            
            print(f"\n{'Month':<10} {'Category':<20} {'Budget':>10}")
            print("-" * 45)
            for key, amount in sorted(self.budgets.items()):
                month, category = key.split(':')
                print(f"{month:<10} {category:<20} ${amount:>9.2f}")
        
        elif choice == '3':
            if not self.budgets:
                print("No budgets to delete.")
                return
            
            print("\nExisting budgets:")
            for i, key in enumerate(sorted(self.budgets.keys()), 1):
                month, category = key.split(':')
                print(f"{i}. {month} - {category}: ${self.budgets[key]:.2f}")
            
            idx = int(input("\nEnter number to delete: ").strip()) - 1
            keys = sorted(self.budgets.keys())
            if 0 <= idx < len(keys):
                del self.budgets[keys[idx]]
                self._save_budgets()
                print(f"{Colors.GREEN}✓ Budget deleted{Colors.RESET}")
        
        elif choice == '4':
            current_month = datetime.now().strftime("%Y-%m")
            month_budgets = {k: v for k, v in self.budgets.items() if k.startswith(current_month)}
            
            if not month_budgets:
                print("No budgets set for current month.")
                return
            
            print(f"\n{Colors.BOLD}Budget Status - {datetime.now().strftime('%B %Y')}{Colors.RESET}")
            print("-" * 60)
            
            for key, budget in sorted(month_budgets.items()):
                _, category = key.split(':')
                
                month_expenses = [e for e in self.expenses 
                                if e['Date'].startswith(current_month) 
                                and e['Category'] == category
                                and e.get('Type', 'expense') == 'expense']
                spent = sum(float(e['Amount']) for e in month_expenses)
                
                remaining = budget - spent
                percentage = (spent / budget) * 100 if budget > 0 else 0
                
                if percentage > 100:
                    color = Colors.RED
                    status = "OVER"
                elif percentage > 80:
                    color = Colors.YELLOW
                    status = "WARNING"
                else:
                    color = Colors.GREEN
                    status = "OK"
                

                bar_length = min(int(percentage / 5), 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                print(f"{category:<20} {color}{bar}{Colors.RESET}")
                print(f"  ${spent:.2f} / ${budget:.2f} ({percentage:.1f}%) - {color}{status}{Colors.RESET}")
                print(f"  Remaining: ${remaining:.2f}\n")
    
    def manage_recurring(self):
        print("\n--- Recurring Expenses ---")
        
        if not self.recurring_expenses:
            print("No recurring expenses set up.")
            print("You can mark expenses as recurring when adding them.")
            return
        
        print(f"\n{'#':<3} {'Amount':>10} {'Category':<20} {'Frequency':<10} {'Last Added':<12}")
        print("-" * 60)
        
        for i, rec in enumerate(self.recurring_expenses, 1):
            print(f"{i:<3} ${float(rec['amount']):>9.2f} {rec['category']:<20} {rec['frequency']:<10} {rec['last_added']:<12}")
        
        print("\n1. Delete recurring expense")
        print("2. Back to main menu")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            idx = int(input("Enter number to delete: ").strip()) - 1
            if 0 <= idx < len(self.recurring_expenses):
                deleted = self.recurring_expenses.pop(idx)
                self._save_recurring()
                print(f"{Colors.GREEN}✓ Deleted recurring expense: {deleted['category']}{Colors.RESET}")
    
    def comparison_report(self):
        print("\n--- Comparison Report ---")
        print("1. Month vs Previous Month")
        print("2. Month vs Same Month Last Year")
        print("3. Custom Date Range Comparison")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            current_month = datetime.now().strftime("%Y-%m")
            prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
            
            self._compare_periods(current_month, prev_month, 
                                 datetime.strptime(current_month + "-01", "%Y-%m-%d").strftime("%B %Y"),
                                 datetime.strptime(prev_month + "-01", "%Y-%m-%d").strftime("%B %Y"))
        
        elif choice == '2':
            current_month = datetime.now().strftime("%Y-%m")
            last_year = (datetime.now().replace(year=datetime.now().year - 1)).strftime("%Y-%m")
            
            self._compare_periods(current_month, last_year,
                                 datetime.strptime(current_month + "-01", "%Y-%m-%d").strftime("%B %Y"),
                                 datetime.strptime(last_year + "-01", "%Y-%m-%d").strftime("%B %Y"))
        
        elif choice == '3':
            period1_start = input("Period 1 start (YYYY-MM-DD): ").strip()
            period1_end = input("Period 1 end (YYYY-MM-DD): ").strip()
            period2_start = input("Period 2 start (YYYY-MM-DD): ").strip()
            period2_end = input("Period 2 end (YYYY-MM-DD): ").strip()
            
            self._compare_date_ranges(period1_start, period1_end, period2_start, period2_end)
    
    def _compare_periods(self, period1, period2, label1, label2):
        """Compare two monthly periods"""
        expenses1 = [e for e in self.expenses if e['Date'].startswith(period1) and e.get('Type', 'expense') == 'expense']
        expenses2 = [e for e in self.expenses if e['Date'].startswith(period2) and e.get('Type', 'expense') == 'expense']
        
        total1 = sum(float(e['Amount']) for e in expenses1)
        total2 = sum(float(e['Amount']) for e in expenses2)
        
        cat1 = defaultdict(float)
        cat2 = defaultdict(float)
        
        for e in expenses1:
            cat1[e['Category']] += float(e['Amount'])
        for e in expenses2:
            cat2[e['Category']] += float(e['Amount'])
        
        all_categories = set(cat1.keys()) | set(cat2.keys())
        
        print(f"\n{'='*70}")
        print(f"{label1} vs {label2}")
        print(f"{'='*70}")
        print(f"{'Category':<20} {label1[:10]:>12} {label2[:10]:>12} {'Change':>12} {'%':>8}")
        print("-" * 70)
        
        for category in sorted(all_categories):
            amt1 = cat1.get(category, 0)
            amt2 = cat2.get(category, 0)
            change = amt1 - amt2
            pct_change = ((amt1 - amt2) / amt2 * 100) if amt2 > 0 else 0
            
            change_color = Colors.RED if change > 0 else Colors.GREEN if change < 0 else Colors.WHITE
            sign = "+" if change > 0 else ""
            
            print(f"{category:<20} ${amt1:>11.2f} ${amt2:>11.2f} {change_color}{sign}${change:>10.2f} {sign}{pct_change:>6.1f}%{Colors.RESET}")
        
        print("-" * 70)
        total_change = total1 - total2
        total_pct = ((total1 - total2) / total2 * 100) if total2 > 0 else 0
        change_color = Colors.RED if total_change > 0 else Colors.GREEN if total_change < 0 else Colors.WHITE
        sign = "+" if total_change > 0 else ""
        
        print(f"{'TOTAL':<20} ${total1:>11.2f} ${total2:>11.2f} {change_color}{sign}${total_change:>10.2f} {sign}{total_pct:>6.1f}%{Colors.RESET}")
        print("="*70)
    
    def _compare_date_ranges(self, start1, end1, start2, end2):
        """Compare two custom date ranges"""
        expenses1 = [e for e in self.expenses if start1 <= e['Date'] <= end1 and e.get('Type', 'expense') == 'expense']
        expenses2 = [e for e in self.expenses if start2 <= e['Date'] <= end2 and e.get('Type', 'expense') == 'expense']
        
        total1 = sum(float(e['Amount']) for e in expenses1)
        total2 = sum(float(e['Amount']) for e in expenses2)
        print(f"\nPeriod 1 ({start1} to {end1}): ${total1:.2f} ({len(expenses1)} expenses)")
        print(f"Period 2 ({start2} to {end2}): ${total2:.2f} ({len(expenses2)} expenses)")
        
        print(f"Difference: ${total1 - total2:.2f}")
    def backup_data(self):
        """Create a backup of all data files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            shutil.copy(self.filename, os.path.join(backup_dir, self.filename))
            if os.path.exists(self.budgets_file):
                shutil.copy(self.budgets_file, os.path.join(backup_dir, self.budgets_file))
            if os.path.exists(self.recurring_file):
                shutil.copy(self.recurring_file, os.path.join(backup_dir, self.recurring_file))
            
            print(f"{Colors.GREEN}✓ Backup created: {backup_dir}/{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Backup failed: {e}{Colors.RESET}")
    
    def export_data(self):
        print("\n--- Export Data ---")
        print("1. Export to CSV (custom range)")
        print("2. Export to JSON")
        print("3. Export text report (current month)")
        
        choice = input("\nSelect format (1-3): ").strip()
        
        if choice == '1':
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            
            filtered = [e for e in self.expenses if start_date <= e['Date'] <= end_date]
            
            filename = f"export_{start_date}_to_{end_date}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['ID', 'Date', 'Amount', 'Category', 'Note', 'Type'])
                writer.writeheader()
                writer.writerows(filtered)
            
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")
        
        elif choice == '2':
            filename = f"expenses_export_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(self.expenses, f, indent=2)
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")
        
        elif choice == '3':
            current_month = datetime.now().strftime("%Y-%m")
            month_expenses = [e for e in self.expenses if e['Date'].startswith(current_month)]
            
            filename = f"report_{current_month}.txt"
            with open(filename, 'w') as f:
                f.write(f"Expense Report - {datetime.now().strftime('%B %Y')}\n")
                f.write("="*60 + "\n\n")
                
                for exp in sorted(month_expenses, key=lambda x: x['Date']):
                    f.write(f"{exp['Date']} | ${exp['Amount']:>8} | {exp['Category']:<20} | {exp['Note']}\n")
                
                total = sum(float(e['Amount']) for e in month_expenses if e.get('Type', 'expense') == 'expense')
                f.write("\n" + "-"*60 + "\n")
                f.write(f"Total: ${total:.2f}\n")
            
            print(f"{Colors.GREEN}✓ Report saved to {filename}{Colors.RESET}")
    
    def display_menu(self):
        print("\n" + "="*50)
        print(f"{Colors.BOLD}{'Penny Track':^50}{Colors.RESET}")
        print("="*50)
        print(f"{Colors.CYAN}Expenses & Income{Colors.RESET}")
        print("  1. Add expense")
        print("  2. Add income")
        print("  3. View all entries")
        print("  4. Edit entry")
        print("  5. Delete entry")
        print(f"\n{Colors.YELLOW}Reports & Analysis{Colors.RESET}")
        print("  6. Monthly summary")
        print("  7. Statistics dashboard")
        print("  8. Search & filter")
        print("  9. Comparison report")
        print(f"\n{Colors.MAGENTA}Budget & Planning{Colors.RESET}")
        print(" 10. Manage budgets")
        print(" 11. Manage recurring expenses")
        print(f"\n{Colors.GREEN}Tools{Colors.RESET}")
        print(" 12. Export data")
        print(" 13. Backup data")
        print(" 14. Settings")
        print(f"\n{Colors.RED}15. Exit{Colors.RESET}")
        print("="*50)
    
    def settings_menu(self):
        """Manage application settings"""
        print("\n--- Settings ---")
        print(f"1. Toggle colors (currently: {'ON' if self.config['use_colors'] else 'OFF'})")
        print(f"2. Currency symbol (currently: {self.config['currency_symbol']})")
        print("3. Back to main menu")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            self.config['use_colors'] = not self.config['use_colors']
            if not self.config['use_colors']:
                Colors.disable()
            self._save_config()
            print(f"{Colors.GREEN}✓ Colors {'enabled' if self.config['use_colors'] else 'disabled'}{Colors.RESET}")
        
        elif choice == '2':
            symbol = input("Enter new currency symbol: ").strip()
            self.config['currency_symbol'] = symbol
            self._save_config()
            print(f"{Colors.GREEN}✓ Currency symbol updated to {symbol}{Colors.RESET}")
    
    def run(self):
        """Main application loop"""
        if not self.config['use_colors']:
            Colors.disable()
        
        print(f"\n{Colors.BOLD} Welcome to Penny Track{Colors.RESET}")
        print(f"Data file: {self.filename}")
        print(f"Total entries: {len(self.expenses)}")
        
        while True:
            self.display_menu()
            choice = input(f"\n{Colors.CYAN}Select an option (1-15): {Colors.RESET}").strip()
            
            try:
                if choice == '1':
                    self.add_expense(is_income=False)
                elif choice == '2':
                    self.add_expense(is_income=True)
                elif choice == '3':
                    self.view_all_expenses()
                elif choice == '4':
                    self.edit_expense()
                elif choice == '5':
                    self.delete_expense()
                elif choice == '6':
                    self.monthly_summary()
                elif choice == '7':
                    self.statistics_dashboard()
                elif choice == '8':
                    self.search_expenses()
                elif choice == '9':
                    self.comparison_report()
                elif choice == '10':
                    self.manage_budgets()
                elif choice == '11':
                    self.manage_recurring()
                elif choice == '12':
                    self.export_data()
                elif choice == '13':
                    self.backup_data()
                elif choice == '14':
                    self.settings_menu()
                elif choice == '15':
                    print(f"\n{Colors.BOLD} Thank you for using Penny Track!{Colors.RESET}")
                    print("Your data has been saved.")
                    break
                else:
                    print(f"\n{Colors.RED}Invalid option. Please choose 1-15.{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
                print("Please try again.")

            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")


def main():
    tracker = ExpenseTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BOLD}Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.RESET}")


if __name__ == "__main__":
    main()
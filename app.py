
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date
from pathlib import Path
import requests
import time

app = Flask(__name__)
app.secret_key = "expense-tracker-local-secret"

DATABASE = Path(app.root_path) / "expenses.db"

# ---------------- CURRENCY CONVERSION ----------------

CURRENCY_CODES = {
    "₹": "INR",
    "$": "USD",
    "€": "EUR",
    "£": "GBP"
}

# Store exchange rates for one hour
exchange_rate_cache = {}


def get_exchange_rate(target_code):
    if target_code == "INR":
        return 1.0

    current_time = time.time()

    # Reuse cached rate if it is less than one hour old
    cached = exchange_rate_cache.get(target_code)

    if cached and current_time - cached["time"] < 3600:
        return cached["rate"]

    try:
        response = requests.get(
            "https://open.er-api.com/v6/latest/INR",
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return None

        rate = data["rates"].get(target_code)

        if rate is None:
            return None

        exchange_rate_cache[target_code] = {
            "rate": rate,
            "time": current_time
        }

        return rate

    except (requests.RequestException, ValueError, KeyError):
        return None


def convert_currency(amount, target_currency):
    target_code = CURRENCY_CODES.get(target_currency, "INR")

    if target_code == "INR":
        return amount

    rate = get_exchange_rate(target_code)

    if rate is None:
        return amount

    return round(amount * rate, 2)




# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- DATABASE TABLES ----------------

def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            expense_date TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            display_name TEXT NOT NULL DEFAULT 'Mohsin',
            currency TEXT NOT NULL DEFAULT '₹',
            theme TEXT NOT NULL DEFAULT 'light',
            monthly_budget REAL NOT NULL DEFAULT 10000
        )
    """)

    conn.execute("""
        INSERT OR IGNORE INTO settings
        (id, display_name, currency, theme, monthly_budget)
        VALUES (1, 'Mohsin', '₹', 'light', 10000)
    """)

    conn.commit()
    conn.close()


# ---------------- GET USER SETTINGS ----------------

def get_user_settings():
    conn = get_db_connection()

    settings = conn.execute(
        "SELECT * FROM settings WHERE id = 1"
    ).fetchone()

    conn.close()
    return settings




# ---------------- DASHBOARD ----------------

@app.route("/")
def home():
    conn = get_db_connection()

    total_inr = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    count = conn.execute(
        "SELECT COUNT(*) FROM expenses"
    ).fetchone()[0]
    current_settings = get_user_settings()

    
    # Convert monthly budget from INR
    monthly_budget = convert_currency(
        current_settings["monthly_budget"],
        current_settings["currency"]
    )

    # Calculate spending for the current month in INR
    monthly_spent_inr = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE strftime('%Y-%m', expense_date) = ?
        """,
        (date.today().strftime("%Y-%m"),)
    ).fetchone()[0]

    # Convert monthly spending
    monthly_spent = convert_currency(
        monthly_spent_inr,
        current_settings["currency"]
    )


    total = convert_currency(
        total_inr,
        current_settings["currency"]
    )

    # Get ALL expenses for charts
    all_expenses = conn.execute(
        """
        SELECT * FROM expenses
        ORDER BY expense_date DESC, id DESC
        """
    ).fetchall()

    # Keep only latest 5 for Recent Transactions
    recent_expenses = all_expenses[:5]

    # Convert all expenses for dashboard charts
    chart_expenses = [
        {
            "category": expense["category"],
            "amount": convert_currency(
                expense["amount"],
                current_settings["currency"]
            ),
            "expense_date": expense["expense_date"]
        }
        for expense in all_expenses
    ]

    conn.close()

    return render_template(
        "index.html",
        total=total,
        count=count,
        expenses=recent_expenses,
        chart_expenses=chart_expenses,
        today=date.today().isoformat(),
        settings=current_settings,
                monthly_budget=monthly_budget,
        monthly_spent=monthly_spent,
    )




# ---------------- ADD EXPENSE ----------------

@app.route("/add-expense", methods=["POST"])
def add_expense():
    amount_text = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    expense_date = request.form.get("expense_date", "").strip()

    try:
        amount = float(amount_text)

        if amount <= 0:
            raise ValueError

    except ValueError:
        flash(
            "Please enter a valid amount greater than zero.",
            "error"
        )
        return redirect(url_for("home"))

    if not category or not description or not expense_date:
        flash("Please fill in all the fields.", "error")
        return redirect(url_for("home"))

    try:
        date.fromisoformat(expense_date)
    except ValueError:
        flash("Please select a valid date.", "error")
        return redirect(url_for("home"))

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO expenses
        (amount, category, description, expense_date)
        VALUES (?, ?, ?, ?)
        """,
        (amount, category, description, expense_date)
    )

    conn.commit()
    conn.close()

    flash("Expense added successfully!", "success")
    return redirect(url_for("home"))



# ---------------- ALL TRANSACTIONS ----------------

@app.route("/expenses")
def expenses():
    conn = get_db_connection()

    all_expenses = conn.execute(
        """
        SELECT * FROM expenses
        ORDER BY expense_date DESC, id DESC
        """
    ).fetchall()

    total_inr = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]

    count = len(all_expenses)

    conn.close()

    current_settings = get_user_settings()
    currency_symbol = current_settings["currency"]

    # Convert transaction amounts for display
    converted_expenses = []

    for expense in all_expenses:
        converted_expenses.append({
            "id": expense["id"],
            "amount": convert_currency(
                expense["amount"],
                currency_symbol
            ),
            "category": expense["category"],
            "description": expense["description"],
            "expense_date": expense["expense_date"]
        })

    # Convert total spending for display
    total = convert_currency(
        total_inr,
        currency_symbol
    )

    return render_template(
        "expenses.html",
        expenses=converted_expenses,
        total=total,
        count=count,
        settings=current_settings
    )


# ---------------- DELETE EXPENSE ----------------

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    flash("Expense deleted successfully.", "success")
    return redirect(url_for("expenses"))


# ---------------- ABOUT PAGE ----------------

@app.route("/about")
def about():
    return render_template(
        "about.html",
        settings=get_user_settings()
    )


# ---------------- SETTINGS PAGE ----------------

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":

        display_name = request.form.get(
            "display_name", ""
        ).strip()

        currency = request.form.get(
            "currency", "₹"
        )

        theme = request.form.get(
            "theme", "light"
        )

        budget_text = request.form.get(
            "monthly_budget", ""
        ).strip()

        if not display_name:
            flash("Please enter your name.", "error")
            return redirect(url_for("settings"))

        if currency not in ["₹", "$", "€", "£"]:
            flash("Please select a valid currency.", "error")
            return redirect(url_for("settings"))

        if theme not in ["light", "dark"]:
            flash("Please select a valid theme.", "error")
            return redirect(url_for("settings"))

        try:
            monthly_budget = float(budget_text)

            if monthly_budget <= 0:
                raise ValueError

        except ValueError:
            flash(
                "Please enter a valid monthly budget greater than zero.",
                "error"
            )
            return redirect(url_for("settings"))

        conn = get_db_connection()

        conn.execute(
            """
            UPDATE settings
            SET display_name = ?,
                currency = ?,
                theme = ?,
                monthly_budget = ?
            WHERE id = 1
            """,
            (display_name, currency, theme, monthly_budget)
        )

        conn.commit()
        conn.close()

        flash("Settings saved successfully!", "success")
        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        settings=get_user_settings()
    )


# ---------------- CALENDAR PAGE ----------------

@app.route("/calendar")
def calendar():
    selected_date = request.args.get(
        "date", date.today().isoformat()
    )

    try:
        date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today().isoformat()

    conn = get_db_connection()

    selected_expenses = conn.execute(
        """
        SELECT * FROM expenses
        WHERE expense_date = ?
        ORDER BY id DESC
        """,
        (selected_date,)
    ).fetchall()

    daily_total = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE expense_date = ?
        """,
        (selected_date,)
    ).fetchone()[0]

    current_settings = get_user_settings()
    currency_symbol = current_settings["currency"]

    daily_total = convert_currency(
        daily_total,
        currency_symbol
    )

    converted_expenses = []

    for expense in selected_expenses:
        converted_expenses.append({
            "id": expense["id"],
            "description": expense["description"],
            "category": expense["category"],
            "amount": convert_currency(
                expense["amount"],
                currency_symbol
            ),
            "expense_date": expense["expense_date"]
        })

    conn.close()

    return render_template(
        "calendar.html",
        expenses=converted_expenses,
        selected_date=selected_date,
        daily_total=daily_total,
        settings=current_settings
    )


# ---------------- NOTIFICATIONS PAGE ----------------

@app.route("/notifications")
def notifications():
    conn = get_db_connection()

    recent_activity = conn.execute(
        """
        SELECT * FROM expenses
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    conn.close()

    return render_template(
        "notifications.html",
        expenses=recent_activity,
        settings=get_user_settings()
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_table()
    app.run(debug=True)

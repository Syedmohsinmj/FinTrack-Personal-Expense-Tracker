# 💰 FinTrack – Personal Expense Tracker

**A smart and user-friendly personal finance management web application built with Python Flask.**

FinTrack helps users record, organize, monitor, and analyze their daily expenses through an interactive dashboard. It provides expense tracking, category-wise analytics, budget management, and multi-currency display support.

---

## 🚀 Features

- **Dashboard:** View total spending, transaction count, average expense, and largest expense.
- **Expense Management:** Add, view, and delete transactions.
- **Category-wise Analysis:** Visualize spending patterns using interactive charts.
- **Monthly Budget:** Set a monthly budget and monitor spending.
- **Multi-Currency Support:** Display expense values in INR, USD, EUR, and GBP using exchange rates.
- **Currency Rate Caching:** Reuse exchange rates for one hour to improve performance.
- **Calendar:** View expense-related information by date.
- **Notifications:** Access expense-related notifications.
- **Personal Settings:** Customize display name, currency, and appearance.
- **Dark and Light Modes:** Choose your preferred interface appearance.
- **SQLite Database:** Store expenses and settings locally.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive interface |
| JavaScript | Interactive functionality |
| Chart.js | Data visualization |
| Requests | Exchange rate API integration |

---

## 📂 Project Structure

```text
Expense_Tracker_Flask/
│
├── app.py
├── expenses.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── expenses.html
│   ├── settings.html
│   ├── about.html
│   ├── calendar.html
│   └── notifications.html
│
└── static/
    └── style.css
```

---

## ⚙️ Installation and Setup

### 1. Install Python

Download and install Python from:

https://www.python.org/downloads/

### 2. Clone or Download the Project

Download the project and open its folder in VS Code.

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open FinTrack

Visit the following address in your browser:

http://127.0.0.1:5000/

---

## 💱 Currency Conversion

FinTrack stores all expense amounts and monthly budgets in Indian Rupees (INR) as the base currency.

Users can select a display currency:

- INR – Indian Rupee
- USD – US Dollar
- EUR – Euro
- GBP – British Pound

Exchange rates are retrieved through an external exchange-rate service and cached for one hour to reduce repeated API requests and improve application performance.

An internet connection is required to retrieve updated exchange rates.

---

## 🗄️ Database

FinTrack uses SQLite for local data storage.

The application creates its database automatically when it starts.

The database stores:
- Expense records
- Transaction descriptions
- Categories
- Expense dates
- User preferences
- Monthly budget settings

---

## 🔒 Data and Privacy

FinTrack is designed as a locally running personal expense tracker. Its SQLite database is stored in the project folder.

The application does not require a cloud database for its core expense-tracking functionality.

---

## 🎯 Project Objective

The objective of FinTrack is to provide a simple and accessible way to manage personal finances, track daily expenses, understand spending habits, and maintain better budget control.

---

## 👨‍💻 Developed By

**Syed Mohsin Shah**

Project: FinTrack – Personal Expense Tracker

Technologies: Python, Flask, SQLite, HTML, CSS, JavaScript

---

⭐ **FinTrack – Track Smart. Spend Better.**

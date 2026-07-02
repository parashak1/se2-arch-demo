# =============================================================
#  app.py — BudgetFlow v1
#  SE-II Session 3 — App 3 Challenge
#
#  A simple personal budget tracker.
#  Add income and expenses, see your balance, filter by category.
#
#  This app works perfectly.
#  Your job is not to fix it — yet.
#  Your job is to find what is wrong with how it is structured.
# =============================================================

from flask import Flask, request, redirect, url_for, render_template_string
from datetime import datetime

app = Flask(__name__)

# ── "Database" ── a list in memory ───────────────────────────
transactions = []
next_id = 1

# ── valid categories ──────────────────────────────────────────
CATEGORIES = ["food", "transport", "housing", "health", "entertainment", "income", "other"]

# ── HTML template ─────────────────────────────────────────────
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BudgetFlow</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f4f6f9; padding: 32px 16px; color: #222; }
    .wrap { max-width: 680px; margin: 0 auto; }
    h1 { font-size: 26px; color: #1a3a5c; margin-bottom: 4px; }
    .sub { font-size: 13px; color: #888; margin-bottom: 20px; }
    .balance-card { border-radius: 10px; padding: 20px 24px; margin-bottom: 20px; color: #fff; }
    .balance-card.positive { background: #2e7d32; }
    .balance-card.negative { background: #c62828; }
    .balance-card.zero     { background: #555; }
    .balance-label { font-size: 13px; opacity: 0.85; margin-bottom: 4px; }
    .balance-amount { font-size: 36px; font-weight: 700; }
    .balance-meta { font-size: 12px; opacity: 0.75; margin-top: 6px; }
    .summary { display: flex; gap: 12px; margin-bottom: 20px; }
    .summary-card { flex: 1; background: #fff; border-radius: 8px; padding: 14px 16px;
                    border: 1px solid #dde3ed; }
    .summary-num { font-size: 20px; font-weight: 700; }
    .summary-num.income  { color: #2e7d32; }
    .summary-num.expense { color: #c62828; }
    .summary-lbl { font-size: 11px; color: #888; margin-top: 2px; }
    .add-form { background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 20px;
                border: 1px solid #dde3ed; }
    .add-form h3 { font-size: 15px; color: #1a3a5c; margin-bottom: 14px; }
    .form-row { display: flex; gap: 10px; flex-wrap: wrap; }
    .form-row input, .form-row select { padding: 9px 11px; border: 1px solid #ccc;
                                         border-radius: 6px; font-size: 14px; }
    .form-row input[type=text]   { flex: 2; min-width: 140px; }
    .form-row input[type=number] { flex: 1; min-width: 100px; }
    .form-row select { flex: 1; min-width: 110px; }
    .btn { padding: 9px 20px; border: none; border-radius: 6px;
           font-size: 14px; cursor: pointer; color: #fff; }
    .btn-income  { background: #2e7d32; }
    .btn-expense { background: #c62828; }
    .filters { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
    .filters a { padding: 5px 13px; border-radius: 99px; font-size: 12px; text-decoration: none;
                 background: #e8edf5; color: #444; border: 1px solid #d0d7e3; }
    .filters a.active { background: #2E75B6; color: #fff; border-color: #2E75B6; }
    .tx-list { list-style: none; }
    .tx { background: #fff; border-radius: 8px; padding: 13px 16px; margin-bottom: 8px;
          border: 1px solid #dde3ed; display: flex; align-items: center; gap: 12px; }
    .tx-type { width: 28px; height: 28px; border-radius: 50%; display: flex;
               align-items: center; justify-content: center; font-size: 14px;
               font-weight: 700; flex-shrink: 0; }
    .tx-type.income  { background: #e8f5e9; color: #2e7d32; }
    .tx-type.expense { background: #fde8e8; color: #c62828; }
    .tx-desc { flex: 1; }
    .tx-title { font-size: 14px; font-weight: 500; }
    .tx-meta  { font-size: 11px; color: #aaa; margin-top: 2px; }
    .tx-amount { font-size: 15px; font-weight: 600; }
    .tx-amount.income  { color: #2e7d32; }
    .tx-amount.expense { color: #c62828; }
    .cat-badge { font-size: 10px; padding: 2px 7px; border-radius: 4px;
                 background: #e8edf5; color: #555; margin-left: 6px; }
    .btn-del { background: #fde8e8; color: #c62828; border: 1px solid #f5c6c6;
               padding: 3px 10px; border-radius: 5px; font-size: 11px;
               text-decoration: none; }
    .empty { text-align: center; padding: 32px; color: #aaa; font-size: 14px; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>BudgetFlow</h1>
  <p class="sub">Personal budget tracker &nbsp; v1</p>

  <!-- Balance -->
  <div class="balance-card {{ balance_class }}">
    <div class="balance-label">Current balance</div>
    <div class="balance-amount">${{ "%.2f"|format(balance|abs) }}
      {% if balance < 0 %} (negative){% endif %}
    </div>
    <div class="balance-meta">{{ income_count }} income  /  {{ expense_count }} expenses</div>
  </div>

  <!-- Summary -->
  <div class="summary">
    <div class="summary-card">
      <div class="summary-num income">+${{ "%.2f"|format(total_income) }}</div>
      <div class="summary-lbl">Total income</div>
    </div>
    <div class="summary-card">
      <div class="summary-num expense">-${{ "%.2f"|format(total_expenses) }}</div>
      <div class="summary-lbl">Total expenses</div>
    </div>
    <div class="summary-card">
      <div class="summary-num" style="color:#2E75B6">{{ tx_count }}</div>
      <div class="summary-lbl">Transactions</div>
    </div>
  </div>

  <!-- Add transaction -->
  <div class="add-form">
    <h3>Add transaction</h3>
    <form method="POST" action="/add">
      <div class="form-row" style="margin-bottom:10px">
        <input type="text"   name="description" placeholder="Description" required>
        <input type="number" name="amount" placeholder="Amount" min="0.01" step="0.01" required>
        <select name="category">
          {% for cat in categories %}
          <option value="{{ cat }}">{{ cat|capitalize }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="form-row">
        <button type="submit" name="type" value="income"  class="btn btn-income">+ Income</button>
        <button type="submit" name="type" value="expense" class="btn btn-expense">- Expense</button>
      </div>
    </form>
  </div>

  <!-- Filters -->
  <div class="filters">
    <a href="/" class="{{ 'active' if current_filter == 'all' }}">All ({{ tx_count }})</a>
    <a href="/?filter=income"  class="{{ 'active' if current_filter == 'income' }}">Income</a>
    <a href="/?filter=expense" class="{{ 'active' if current_filter == 'expense' }}">Expenses</a>
    {% for cat in categories %}
    <a href="/?filter={{ cat }}" class="{{ 'active' if current_filter == cat }}">{{ cat|capitalize }}</a>
    {% endfor %}
  </div>

  <!-- Transaction list -->
  <ul class="tx-list">
    {% for tx in visible_transactions %}
    <li class="tx">
      <div class="tx-type {{ tx.type }}">{{ '+' if tx.type == 'income' else '-' }}</div>
      <div class="tx-desc">
        <div class="tx-title">
          {{ tx.description }}
          <span class="cat-badge">{{ tx.category }}</span>
        </div>
        <div class="tx-meta">{{ tx.date }}</div>
      </div>
      <div class="tx-amount {{ tx.type }}">
        {{ '+' if tx.type == 'income' else '-' }}${{ "%.2f"|format(tx.amount) }}
      </div>
      <a href="/delete/{{ tx.id }}" class="btn-del">Delete</a>
    </li>
    {% else %}
    <li class="empty">No transactions here.</li>
    {% endfor %}
  </ul>
</div>
</body>
</html>
"""


# ── Routes ────────────────────────────────────────────────────


@app.route("/")
def index():
    global transactions

    current_filter = request.args.get("filter", "all")

    # ⚠️  FILTER LOGIC INSIDE ROUTE
    if current_filter == "all":
        visible_transactions = transactions
    elif current_filter == "income":
        visible_transactions = [t for t in transactions if t["type"] == "income"]
    elif current_filter == "expense":
        visible_transactions = [t for t in transactions if t["type"] == "expense"]
    elif current_filter == "food":
        visible_transactions = [t for t in transactions if t["category"] == "food"]
    elif current_filter == "transport":
        visible_transactions = [t for t in transactions if t["category"] == "transport"]
    elif current_filter == "housing":
        visible_transactions = [t for t in transactions if t["category"] == "housing"]
    elif current_filter == "health":
        visible_transactions = [t for t in transactions if t["category"] == "health"]
    elif current_filter == "entertainment":
        visible_transactions = [t for t in transactions if t["category"] == "entertainment"]
    else:
        visible_transactions = [t for t in transactions if t["category"] == current_filter]

    # ⚠️  BALANCE CALCULATION INSIDE ROUTE
    balance = 0
    for t in transactions:
        if t["type"] == "income":
            balance += t["amount"]
        else:
            balance -= t["amount"]

    # ⚠️  SUMMARY STATS INSIDE ROUTE
    total_income   = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    income_count   = len([t for t in transactions if t["type"] == "income"])
    expense_count  = len([t for t in transactions if t["type"] == "expense"])
    tx_count       = len(transactions)

    # ⚠️  DISPLAY LOGIC INSIDE ROUTE
    if balance > 0:
        balance_class = "positive"
    elif balance < 0:
        balance_class = "negative"
    else:
        balance_class = "zero"

    return render_template_string(
        TEMPLATE,
        visible_transactions=visible_transactions,
        balance=balance,
        balance_class=balance_class,
        total_income=total_income,
        total_expenses=total_expenses,
        income_count=income_count,
        expense_count=expense_count,
        tx_count=tx_count,
        current_filter=current_filter,
        categories=CATEGORIES,
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    global transactions, next_id

    description = request.form.get("description", "").strip()
    category    = request.form.get("category", "other")
    tx_type     = request.form.get("type", "expense")

    # ⚠️  VALIDATION INSIDE ROUTE
    if not description:
        return redirect(url_for("index"))

    if len(description) > 100:
        description = description[:100]

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        return redirect(url_for("index"))

    if amount <= 0:
        return redirect(url_for("index"))

    if tx_type not in ("income", "expense"):
        tx_type = "expense"

    if category not in CATEGORIES:
        category = "other"

    # ⚠️  TRANSACTION CREATION INSIDE ROUTE
    transaction = {
        "id":          next_id,
        "description": description,
        "amount":      amount,
        "type":        tx_type,
        "category":    category,
        "date":        datetime.now().strftime("%b %d, %H:%M"),
    }
    transactions.append(transaction)
    next_id += 1

    # ⚠️  SIDE EFFECT (logging) JAMMED INTO ROUTE
    print(f"  [NEW TX]  {tx_type.upper()} ${amount:.2f} — {description} ({category})")

    return redirect(url_for("index"))


@app.route("/delete/<int:tx_id>")
def delete_transaction(tx_id):
    global transactions

    # ⚠️  DATA MUTATION DIRECTLY IN ROUTE
    tx_to_delete = None
    for tx in transactions:
        if tx["id"] == tx_id:
            tx_to_delete = tx
            break

    if tx_to_delete:
        transactions.remove(tx_to_delete)

        # ⚠️  BALANCE RECALCULATED AGAIN HERE (duplicated from index)
        balance = 0
        for t in transactions:
            if t["type"] == "income":
                balance += t["amount"]
            else:
                balance -= t["amount"]

        # ⚠️  LOGGING DUPLICATED FROM add_transaction
        print(f"  [DEL TX]  #{tx_id} deleted — new balance: ${balance:.2f}")

    return redirect(url_for("index"))


# ── Seed data ─────────────────────────────────────────────────

def seed():
    global transactions, next_id
    samples = [
        ("Monthly salary",      2500.00, "income",  "income"),
        ("Apartment rent",       850.00, "expense", "housing"),
        ("Weekly groceries",      95.40, "expense", "food"),
        ("Bus pass",              45.00, "expense", "transport"),
        ("Doctor visit",          30.00, "expense", "health"),
        ("Netflix subscription",  15.99, "expense", "entertainment"),
        ("Freelance project",    400.00, "income",  "income"),
        ("Restaurant dinner",     62.50, "expense", "food"),
    ]
    for desc, amount, tx_type, category in samples:
        transactions.append({
            "id":          next_id,
            "description": desc,
            "amount":      amount,
            "type":        tx_type,
            "category":    category,
            "date":        datetime.now().strftime("%b %d, %H:%M"),
        })
        next_id += 1


if __name__ == "__main__":
    seed()
    print("\n  BudgetFlow running  →  http://localhost:5000\n")
    app.run(debug=True)

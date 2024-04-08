import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT symbol, SUM(number) FROM (SELECT symbol, SUM(number) as number FROM purchases WHERE userid = ? GROUP BY symbol UNION SELECT symbol, 0 - SUM(number) as number FROM sales WHERE userid = ? GROUP BY symbol) GROUP BY symbol", session.get("user_id"), session.get("user_id"))
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]
    total = cash
    stocks = {}
    for row in rows:
        number = row["SUM(number)"]
        price = lookup(row["symbol"])["price"]
        stocks[row["symbol"]] = [number, usd(price), usd(number * price)]
        total += number * price
    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        if not lookup(request.form.get("symbol")):
            return apology("symbol not found")
        elif not request.form.get("shares"):
            return apology("must provide shares")
        elif not request.form.get("shares").isnumeric():
            return apology("shares must be numeric")
        elif int(request.form.get("shares")) <= 0:
            return apology("shares must be positive")
        funds = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]
        price = lookup(request.form.get("symbol"))["price"]
        amount = int(request.form.get("shares")) * price
        if amount > funds:
            return apology("insufficient funds")
        db.execute("UPDATE users SET cash = ? WHERE id = ?", funds - amount, session.get("user_id"))
        db.execute("INSERT INTO purchases (userid, time, symbol, number, price) VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)",
                   session.get("user_id"), request.form.get("symbol"), request.form.get("shares"), price)
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    data = db.execute("SELECT 'Buy', * FROM purchases WHERE userid = ? UNION SELECT 'Sell', * FROM sales WHERE userid = ? ORDER BY time",
                      session.get("user_id"), session.get("user_id"))
    for row in data:
        row["price"] = usd(row["price"])
    return render_template("history.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = lookup(request.form.get("symbol"))
        if symbol:
            return render_template("quoted.html", symbol=usd(symbol["price"]))
        else:
            return apology("symbol not found")
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if rows:
            return apology("user is already registered")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))
        return redirect("/")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        if not lookup(request.form.get("symbol")):
            return apology("symbol not found")
        elif not request.form.get("shares"):
            return apology("must provide shares")
        elif not request.form.get("shares").isnumeric():
            return apology("shares must be numeric")
        elif int(request.form.get("shares")) <= 0:
            return apology("shares must be positive")
        funds = db.execute("SELECT cash FROM users WHERE id = ?", session.get("user_id"))[0]["cash"]
        have = db.execute("SELECT SUM(number) FROM (SELECT symbol, SUM(number) as number FROM purchases WHERE userid = ? GROUP BY symbol UNION SELECT symbol, 0 - SUM(number) as number FROM sales WHERE userid = ? GROUP BY symbol) GROUP BY symbol",
                          session.get("user_id"), session.get("user_id"))[0]["SUM(number)"]
        price = lookup(request.form.get("symbol"))["price"]
        shares = int(request.form.get("shares"))
        if shares > have:
            return apology("insufficient shares")
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   funds + shares * price, session.get("user_id"))
        db.execute("INSERT INTO sales (userid, time, symbol, number, price) VALUES (?, DATE('now'), ?, ?, ?)",
                   session.get("user_id"), request.form.get("symbol"), request.form.get("shares"), price)
        return redirect("/")
    else:
        stocks = db.execute("SELECT symbol FROM purchases GROUP BY symbol")
        return render_template("sell.html", stocks=stocks)

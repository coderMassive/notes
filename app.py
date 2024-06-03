from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///notes.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def fetch_notes(query):
    return db.execute(
        """
        SELECT notes.id as id, name, content
        FROM notes
        JOIN note_access
            ON notes.id = note_access.noteid
        WHERE userid = ?
            AND (name LIKE ? OR content LIKE ?)
        ORDER BY timestamp DESC
        """,
        session["user_id"],
        "%" + query + "%",
        "%" + query + "%"
    )

@app.route("/", methods=["GET"])
@login_required
def index():
    query = request.args.get('query') or ""
    notes = fetch_notes(query)
    return render_template("index.html", notes=notes, query=query)

@app.route("/notes", methods=["POST"])
@login_required
def post_note():
    db.execute("INSERT INTO notes (name, timestamp, content, owner) VALUES (?, CURRENT_TIMESTAMP, '', ?)", request.form.get("name"), session["user_id"])
    db.execute("INSERT INTO note_access (userid, noteid) VALUES (?, (SELECT MAX(id) FROM notes))", session["user_id"])
    return redirect("/note/" + str(db.execute("SELECT MAX(id) AS x FROM notes")[0]["x"]))


@app.route("/note/<id>", methods=["GET"])
@login_required
def get_note(id):
    query = request.args.get('query') or ""
    notes = fetch_notes(query)
    try:
        ind = notes.index(next(filter(lambda n: n.get("id") == int(id), notes)))
    except:
        return redirect("/?query=" + query)
    shared = db.execute("SELECT username FROM users JOIN note_access ON users.id = userid JOIN notes ON noteid = notes.id WHERE noteid = ? AND userid != ?", id, session["user_id"])
    return render_template("index.html", notes=notes, id=int(id), ind=ind, shared=shared, query=query)


@app.route("/note/<id>", methods=["POST"])
@login_required
def note_action(id):
    method = request.form.get("method")
    if method == "PUT":
        update_note(id)
    elif method == "DELETE":
        delete_note(id)
    return redirect("/note/" + id)

def update_note(id):
    db.execute("UPDATE notes SET name = ?, timestamp = CURRENT_TIMESTAMP, content = ? WHERE id = ?", request.form.get("name"), request.form.get("content"), id)

def delete_note(id):
    owner = db.execute("SELECT owner FROM notes WHERE id = ?", id)[0]["owner"]
    if owner == session["user_id"]:
        db.execute("DELETE FROM note_access WHERE noteid = ?", id)
        db.execute("DELETE FROM notes WHERE id = ?", id)
    else:
        db.execute("DELETE FROM note_access WHERE noteid = ? AND userid = ?", id, session["user_id"])
    return redirect("/")

@app.route("/note/<id>/shares", methods=["POST"])
@login_required
def share_note(id):
    owner = db.execute("SELECT owner FROM notes WHERE id = ?", id)[0]["owner"]
    if owner == session["user_id"]:
        try:
            db.execute("INSERT INTO note_access (userid, noteid) VALUES ((SELECT id FROM users WHERE username = ?), ?)", request.form.get("username"), id)
        except ValueError as ex:
            if str(ex).split()[0] == "UNIQUE":
                return apology("User is already shared")
            else:
                return apology("This user does not exist")
        return redirect("/note/" + id)
    else:
        return apology("You are not the owner")


@app.route("/login", methods=["GET"])
def get_login():
    session.clear()
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def post_login():
    session.clear()
    if not request.form.get("username"):
        return apology("must provide username", 403)
    elif not request.form.get("password"):
        return apology("must provide password", 403)
    rows = db.execute(
        "SELECT * FROM users WHERE username = ?", request.form.get("username")
    )
    if len(rows) != 1 or not check_password_hash(
        rows[0]["hash"], request.form.get("password")
    ):
        return apology("invalid username and/or password", 403)
    session["user_id"] = rows[0]["id"]
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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

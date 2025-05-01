import os
import sqlite3 as sql

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/uploads"
Session(app)

def get_db_connection():
    connection = sql.connect('data.db')
    connection.row_factory = sql.Row
    return connection

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def dashboard():
    username = session.get("username")
    now = datetime.now()
    hour = now.hour

    if hour < 12:
        greeting = "Good Morning"
        subtext = "Let's Make Today A Productive Day"
    elif hour < 18:
        greeting = "Good Afternoon"
        subtext = "Remember To Take A Break From Time To Time"
    else:
        greeting = "Good Evening"
        subtext = "You Should Hit The Hay Soon And Get A Good Night's Rest"

    todos = [...]
    notes = [...]

    return render_template("dashboard.html", dashboard=True, username=username, greeting=greeting, subtext=subtext, todos=todos, notes=notes)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    return render_template("buy.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required", "danger")
            return render_template("login.html")
        if not password:
            flash("Please Provide the Password", "danger")
            return render_template("login.html")

        conn = get_db_connection()
        row = conn.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchone()

        if row is None or not check_password_hash(row["password"], password):
            flash("Invalid Username or Password", "danger")
            return render_template("login.html")

        session["user_id"] = row["id"]
        session["username"] = row["username"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        profile_pic = request.files.get("profile_pic")

        if not username or not password or not confirmation:
            flash("All fields are required except profile picture", "danger")
            return redirect("/register")
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user:
            flash("Username already exists", "danger")
            return redirect("/register")

        hash_pass = generate_password_hash(password)
        
        filename = "placeholder.png"
        if profile_pic and profile_pic.filename != "":
            filename = f"{username}_{profile_pic.filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_pic.save(filepath)

        cursor.execute("INSERT INTO users (username, password, profile_picture) VALUES (?, ?, ?)", (username, hash_pass, filename))

        connection.commit()
        connection.close()

        flash("User Created Successfully", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    return render_template("sell.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    return render_template("change-password.html")

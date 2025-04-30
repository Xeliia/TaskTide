import os
import sqlite3 as sql

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

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
def index():
    """Homepage"""
    
    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    return render_template("buy.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Username is required", "danger")
            return redirect("/login")
        if not request.form.get("password"):
            flash("Please Provide the Password", "danger")
            return redirect("/login")

        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM users where username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash (
            rows[0]["password"], request.form.get("password")
        ):
            flash("Invalid Username or Password", "danger")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
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
        
        user = cursor.execute("SELECT * FROM users WHERE username = ?", username)
        if user:
            flash("Username already exists", "danger")
            return redirect("/register")
        
        hash_pass = generate_password_hash(password)
        
        filename = "placeholder.png"
        if profile_pic and profile_pic.filename != "":
            filename = f"{username}_{profile_pic.filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_pic.save(filepath)

        cursor.execute("INSER INTO users (username, hash, profile_pic) VALUES (?, ?, ?)", username, hash_pass, filename)
        
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

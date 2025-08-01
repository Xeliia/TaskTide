# Some code in this project was developed with the assistance of GitHub Copilot and ChatGPT.
# Specifically in suggesting logic for the database interaction, and other functionalities

import os
import random

from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import get_db_connection, login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "static/uploads"
Session(app)

notes_data = {}

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def dashboard():
    user_id = session.get("user_id")
    username = session.get("username")

    from datetime import datetime
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

    conn = get_db_connection()
    user = conn.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,)).fetchone()
    profile_picture = user["profile_picture"] if user else "placeholder.png"

    notes = conn.execute("SELECT * FROM notes WHERE user_id = ?", (user_id,)).fetchall()
    random_note = random.choice(notes) if notes else None
    notes_count = len(notes)

    todos = conn.execute("SELECT * FROM todos WHERE user_id = ?", (user_id,)).fetchall()
    todos_count = len(todos)

    conn.close()

    return render_template(
        "dashboard.html",
        username=username,
        greeting=greeting,
        subtext=subtext,
        profile_picture=profile_picture,
        notes_count=notes_count,
        todos_count=todos_count,
        todos=todos,
        random_note=random_note
    )


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

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    user_id = session.get('user_id')
    conn = get_db_connection()

    if request.method == 'POST':
        task = request.form.get('task')
        if task:
            conn.execute('INSERT INTO todos (user_id, task) VALUES (?, ?)', (user_id, task))
            conn.commit()
            conn.close()
            return redirect('/todo')

    todos = conn.execute('SELECT * FROM todos WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    conn.close()
    return render_template('todo.html', todos=todos, current_page="todo")
    
@app.route('/todo/delete/<int:todo_id>')
def delete_todo(todo_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))
    conn.commit()
    conn.close()
    return redirect('/todo')

@app.route('/todo/toggle/<int:todo_id>')
def toggle_complete(todo_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute('UPDATE todos SET completed = NOT completed WHERE id = ? AND user_id = ?', (todo_id, user_id))
    conn.commit()
    conn.close()
    return redirect('/todo')

@app.route("/pomodoro", methods=["GET", "POST"])
@login_required
def pomodoro():
    return render_template("pomodoro.html", current_page="pomodoro")

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        today = datetime.today()
        title = "New Note"
        cur.execute("INSERT INTO notes (user_id, note_date, title, content) VALUES (?, ?, ?, ?)", 
                    (user_id, today, title, ""))
        conn.commit()
        note_id = cur.lastrowid
        conn.close()
        return jsonify({'id': note_id}), 201

    selected_id = request.args.get('selected')
    cur.execute("SELECT id, note_date, title, content FROM notes WHERE user_id = ?", (user_id,))
    notes = cur.fetchall()

    selected_note = None
    if selected_id:
        cur.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (selected_id, user_id))
        selected_note = cur.fetchone()

    conn.close()

    notes_dict = {
        str(note['id']): {
            'id': note['id'],
            'title': note['title'] or f"Note {note['id']}",
            'content': note['content']
        } for note in notes
    }

    return render_template("notes.html", current_page="notes", notes=notes_dict, selected_id=selected_id, selected_note=selected_note)

@app.route('/notes/rename', methods=['POST'])
def rename_note():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    data = request.get_json()
    note_id = data.get('note_id')
    new_title = data.get('title')

    if not note_id or not new_title:
        return jsonify({'success': False, 'message': 'Note ID and title are required.'})

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET title = ? WHERE id = ? AND user_id = ?", (new_title, note_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/notes/save-content', methods=['POST'])
def save_content():
    user_id = session.get('user_id')
    data = request.get_json()
    note_id = data.get('note_id')
    content = data.get('content')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET content = ? WHERE id = ? AND user_id = ?", (content, note_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    user_id = session.get('user_id')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    conn.commit()
    conn.close()
    return '', 204

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        profile_pic = request.files.get("profile_pic")

        if username and username != session["username"]:
            existing = cur.execute("SELECT id FROM users WHERE username = ? AND id != ?", (username, user_id)).fetchone()
            if existing:
                flash("Username already taken.", "danger")
                conn.close()
                return redirect("/settings")
            cur.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
            session["username"] = username

        if password:
            if password != confirmation:
                flash("Passwords do not match.", "danger")
                conn.close()
                return redirect("/settings")
            hash_pass = generate_password_hash(password)
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (hash_pass, user_id))

        if profile_pic and profile_pic.filename != "":
            filename = f"{username}_{profile_pic.filename}"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            profile_pic.save(filepath)
            cur.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (filename, user_id))

        conn.commit()
        conn.close()
        flash("Settings updated!", "success")
        return redirect("/settings")

    user = conn.execute("SELECT profile_picture FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template("settings.html", profile_picture=user["profile_picture"] if user else "placeholder.png", current_page="settings")

@app.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    user_id = session.get("user_id")
    password = request.form.get("delete_password")
    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or not check_password_hash(user["password"], password):
        flash("Incorrect password. Account not deleted.", "danger")
        conn.close()
        return redirect("/settings")
    cur.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM todos WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    session.clear()
    flash("Account deleted.", "info")
    return redirect("/login")
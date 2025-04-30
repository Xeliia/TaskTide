import sqlite3 as sql

def create_db():
    connection = sql.connect('data.db')
    cursor = connection.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       password TEXT NOT NULL,
                       profile_picture TEXT
                       )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS notes (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       note_date DATA NOT NULL,
                       content TEXT,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                       )
                   """)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        task TEXT NOT NULL,i
                        completed BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                       )
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       start_time DATETIME NOT NULL,
                       end_time DATETIME,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                       )
                   """)

    connection.commit()
    connection.close()

create_db()

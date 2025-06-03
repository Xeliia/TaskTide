import sqlite3

conn = sqlite3.connect('data.db')  # Replace with your actual DB file name if different
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(notes);")
columns = cursor.fetchall()
print("Notes table schema:")
for col in columns:
    print(col)
conn.close()
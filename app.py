from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amka TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_patient", methods=["POST"])
def add_patient():
    data = request.form

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients (amka, name, age, gender)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("amka"),
        data.get("name"),
        data.get("age"),
        data.get("gender")
    ))

    conn.commit()
    conn.close()

    return "OK"

@app.route("/patients")
def patients():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)

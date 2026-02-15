from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            amka VARCHAR(20),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, amka, first_name, last_name FROM patients ORDER BY created_at DESC")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    amka = request.form["amka"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (amka, first_name, last_name) VALUES (%s, %s, %s)",
        (amka, first_name, last_name)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/")

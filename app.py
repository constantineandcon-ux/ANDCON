from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        amka TEXT UNIQUE,
        phone TEXT,
        address TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS medical_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        diagnosis TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        medication TEXT,
        dosage TEXT,
        instructions TEXT,
        date TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS xrays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        filename TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM patients")
    patients = c.fetchall()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    name = request.form["name"]
    age = request.form["age"]
    amka = request.form["amka"]
    phone = request.form["phone"]
    address = request.form["address"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""

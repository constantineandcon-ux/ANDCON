from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================================
# ΑΡΧΙΚΟΠΟΙΗΣΗ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ
# ================================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ΠΙΝΑΚΑΣ ΑΣΘΕΝΩΝ
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amka TEXT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        created_at TEXT
    )
    """)

    # ΠΙΝΑΚΑΣ ΑΚΤΙΝΟΓΡΑΦΙΩΝ
    c.execute("""
    CREATE TABLE IF NOT EXISTS xrays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        filename TEXT,
        exam_type TEXT,
        exam_date TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    # ΠΙΝΑΚΑΣ ΣΥΝΤΑΓΩΝ
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

    conn.commit()
    conn.close()

init_db()

# ================================
# ΑΡΧΙΚΗ ΣΕΛΙΔΑ
# ================================
@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM patients")
    patients = c.fetchall()
    conn.close()
    return render_template("index.html", patients=patients)

# ================================
# ΠΡΟΣΘΗΚΗ ΑΣΘΕΝΗ
# ================================
@app.route("/add_patient", methods=["POST"])
def add_patient():
    amka = request.form["amka"]
    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO patients (amka, name, age, gender, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (amka, name, age, gender, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    return redirect("/")

# ================================
# ΑΝΕΒΑΣΜΑ ΑΚΤΙΝΟΓΡΑΦΙΑΣ
# ================================
@app.route("/upload_xray/<int:patient_id>", methods=["POST"])
def upload_xray(patient_id):
    file = request.files["file"]
    exam_type = request.form["exam_type"]

    if file and file.filename != "":
        filename = f"{patient_id}_{datetime.now().timestamp()}_{file.filename}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO xrays (patient_id, filename, exam_type, exam_date)
            VALUES (?, ?, ?, ?)
        """, (patient_id, filename, exam_type,
              datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()

    return redirect("/")

# ================================
# ΠΡΟΣΘΗΚΗ ΣΥΝΤΑΓΗΣ
# ================================
@app.route("/add_prescription/<int:patient_id>", methods=["POST"])
def add_prescription(patient_id):
    medication = request.form["medication"]
    dosage = request.form["dosage"]
    instructions = request.form["instructions"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO prescriptions (patient_id, medication, dosage, instructions, date)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, medication, dosage, instructions,
          datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    return redirect("/")

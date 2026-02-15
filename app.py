from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# Φάκελος αποθήκευσης ακτινογραφιών
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Δημιουργία βάσης
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS xrays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            filename TEXT
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

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/upload_xray/<int:patient_id>", methods=["POST"])
def upload_xray(patient_id):
    file = request.files["file"]

    if file.filename != "":
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO xrays (patient_id, filename) VALUES (?, ?)",
                  (patient_id, file.filename))
        conn.commit()
        conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run()

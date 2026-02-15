import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_cors import CORS
import psycopg2
from io import BytesIO

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (amka, first_name, last_name, birth_date, phone, email)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        request.form["amka"],
        request.form["first_name"],
        request.form["last_name"],
        request.form["birth_date"],
        request.form["phone"],
        request.form["email"]
    ))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/upload/<int:patient_id>", methods=["POST"])
def upload_file(patient_id):
    file = request.files["file"]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medical_files (patient_id, file_name, file_type, file_data)
        VALUES (%s,%s,%s,%s)
    """, (
        patient_id,
        file.filename,
        file.content_type,
        psycopg2.Binary(file.read())
    ))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/file/<int:file_id>")
def get_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_type, file_data FROM medical_files WHERE id=%s", (file_id,))
    file = cur.fetchone()
    cur.close()
    conn.close()
    return send_file(BytesIO(file[2]), download_name=file[0], mimetype=file[1])

@app.route("/search", methods=["POST"])
def search():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amka, first_name, last_name
        FROM patients
        WHERE amka=%s OR last_name ILIKE %s
    """, (
        request.form["search"],
        f"%{request.form['search']}%"
    ))
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", patients=patients)

if __name__ == "__main__":
    app.run()

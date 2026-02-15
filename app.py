from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, amka, first_name, last_name FROM patients ORDER BY created_at DESC")
    patients = cur.fetchall()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    amka = request.form["amka"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    birth_date = request.form["birth_date"]
    phone = request.form["phone"]
    email = request.form["email"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (amka, first_name, last_name, birth_date, phone, email)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(amka,first_name,last_name,birth_date,phone,email))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/upload_file/<int:patient_id>", methods=["POST"])
def upload_file(patient_id):
    file = request.files["file"]
    file_data = file.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medical_files (patient_id, file_name, file_type, file_data)
        VALUES (%s,%s,%s,%s)
    """,(patient_id,file.filename,file.content_type,file_data))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/view_file/<int:file_id>")
def view_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_type, file_data FROM medical_files WHERE id=%s",(file_id,))
    file = cur.fetchone()
    conn.close()
    return (file[2], 200, {"Content-Type": file[1]})

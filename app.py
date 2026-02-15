from flask import Flask, render_template, request, redirect, send_file
import psycopg2
import os
import io

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, amka, first_name, last_name, birth_date, phone, email FROM patients ORDER BY id DESC")
    patients_raw = cur.fetchall()
    patients = []
    for p in patients_raw:
        cur.execute("SELECT id, file_name FROM medical_files WHERE patient_id = %s", (p[0],))
        files = cur.fetchall()
        patients.append({'info': p, 'files': files})
    cur.close()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO patients (amka, first_name, last_name, birth_date, phone, email) VALUES (%s, %s, %s, %s, %s, %s)",
                (request.form["amka"], request.form["first_name"], request.form["last_name"], request.form["birth_date"] or None, request.form["phone"], request.form["email"]))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/edit_patient/<int:id>", methods=["POST"])
def edit_patient(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE patients SET amka=%s, first_name=%s, last_name=%s, phone=%s, email=%s WHERE id=%s",
                (request.form["amka"], request.form["first_name"], request.form["last_name"], request.form["phone"], request.form["email"], id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/upload_file/<int:patient_id>", methods=["POST"])
def upload_file(patient_id):
    f = request.files["file"]
    if f:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO medical_files (patient_id, file_name, file_type, file_data) VALUES (%s, %s, %s, %s)",
                    (patient_id, f.filename, f.content_type, f.read()))
        conn.commit()
        cur.close()
        conn.close()
    return redirect("/")

@app.route("/view_file/<int:file_id>")
def view_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_type, file_data FROM medical_files WHERE id = %s", (file_id,))
    file = cur.fetchone()
    cur.close()
    conn.close()
    return send_file(io.BytesIO(file[2]), mimetype=file[1])

@app.route("/delete_file/<int:file_id>")
def delete_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medical_files WHERE id = %s", (file_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

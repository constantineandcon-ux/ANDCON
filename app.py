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
    cur.execute("SELECT id, amka, first_name, last_name FROM ασθενείς ORDER BY created_at DESC")
    patients = cur.fetchall()
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
        "INSERT INTO ασθενείς (amka, first_name, last_name) VALUES (%s,%s,%s)",
        (amka, first_name, last_name),
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ασθενείς WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/upload/<int:patient_id>", methods=["POST"])
def upload_file(patient_id):
    file = request.files["file"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO medical_files (patient_id, file_name, file_type, file_data) VALUES (%s,%s,%s,%s)",
        (patient_id, file.filename, file.content_type, file.read()),
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/files/<int:patient_id>")
def view_files(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, file_name FROM medical_files WHERE patient_id=%s",
        (patient_id,),
    )
    files = cur.fetchall()
    conn.close()
    return render_template("files.html", files=files, patient_id=patient_id)

@app.route("/download/<int:file_id>")
def download_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT file_name, file_type, file_data FROM medical_files WHERE id=%s",
        (file_id,),
    )
    file = cur.fetchone()
    conn.close()

    return send_file(
        io.BytesIO(file[2]),
        download_name=file[0],
        mimetype=file[1],
        as_attachment=False,
    )

@app.route("/delete_file/<int:file_id>")
def delete_file(file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM medical_files WHERE id=%s", (file_id,))
    conn.commit()
    conn.close()
    return redirect("/")

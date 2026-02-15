from flask import Flask, render_template, request, redirect, Response
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    cur = conn.cursor()
    cur.execute("SELECT * FROM ασθενείς ORDER BY created_at DESC")
    patients = cur.fetchall()

    patient_list = []
    for p in patients:
        cur.execute("SELECT id, file_name FROM medical_files WHERE patient_id=%s", (p[0],))
        files = cur.fetchall()
        patient_list.append(p + (files,))
    return render_template("index.html", patients=patient_list)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ασθενείς (amka, first_name, last_name, birth_date, phone, email)
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
    return redirect("/")

@app.route("/update_patient/<int:id>", methods=["POST"])
def update_patient(id):
    cur = conn.cursor()
    cur.execute("""
        UPDATE ασθενείς
        SET first_name=%s, last_name=%s, phone=%s, email=%s
        WHERE id=%s
    """, (
        request.form["first_name"],
        request.form["last_name"],
        request.form["phone"],
        request.form["email"],
        id
    ))
    conn.commit()
    return redirect("/")

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    cur = conn.cursor()
    cur.execute("DELETE FROM ασθενείς WHERE id=%s", (id,))
    conn.commit()
    return redirect("/")

@app.route("/upload_file/<int:id>", methods=["POST"])
def upload_file(id):
    file = request.files["file"]
    data = file.read()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medical_files (patient_id, file_name, file_type, file_data)
        VALUES (%s,%s,%s,%s)
    """, (id, file.filename, file.content_type, psycopg2.Binary(data)))
    conn.commit()
    return redirect("/")

@app.route("/view_file/<int:id>")
def view_file(id):
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_type, file_data FROM medical_files WHERE id=%s", (id,))
    f = cur.fetchone()
    return Response(f[2], mimetype=f[1], headers={"Content-Disposition": f"inline; filename={f[0]}"})

@app.route("/delete_file/<int:id>")
def delete_file(id):
    cur = conn.cursor()
    cur.execute("DELETE FROM medical_files WHERE id=%s", (id,))
    conn.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run()

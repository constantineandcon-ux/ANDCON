from flask import Flask, render_template, request, redirect, url_for, send_file
import psycopg2
import io

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "YOUR_PASSWORD",
    "host": "YOUR_HOST",
    "port": "5432"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, amka, first_name, last_name FROM patients ORDER BY created_at DESC;")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    amka = request.form["amka"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    photo = request.files["photo"].read()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (amka, first_name, last_name, photo)
        VALUES (%s, %s, %s, %s)
    """, (amka, first_name, last_name, photo))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/patient_photo/<int:patient_id>")
def patient_photo(patient_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT photo FROM patients WHERE id = %s;", (patient_id,))
    photo = cur.fetchone()[0]
    cur.close()
    conn.close()
    return send_file(io.BytesIO(photo), mimetype="image/jpeg")

@app.route("/add_file/<int:patient_id>", methods=["POST"])
def add_file(patient_id):
    file = request.files["file"]
    file_data = file.read()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO medical_files (patient_id, file_type, file_name, file_data)
        VALUES (%s, %s, %s, %s)
    """, (patient_id, file.content_type, file.filename, file_data))
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

@app.route("/download_file/<int:file_id>")
def download_file(file_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_data FROM medical_files WHERE id = %s;", (file_id,))
    file_name, file_data = cur.fetchone()
    cur.close()
    conn.close()
    return send_file(io.BytesIO(file_data), download_name=file_name, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

import os
import base64
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
from io import BytesIO

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return "PROFESSIONAL MEDICAL SYSTEM ONLINE"

@app.route("/patients", methods=["POST"])
def create_patient():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO patients (amka, first_name, last_name, birth_date, phone, email)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        data["amka"],
        data["first_name"],
        data["last_name"],
        data.get("birth_date"),
        data.get("phone"),
        data.get("email")
    ))

    patient_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"patient_id": patient_id})

@app.route("/upload/<int:patient_id>", methods=["POST"])
def upload_file(patient_id):
    file = request.files["file"]
    file_data = file.read()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO medical_files (patient_id, file_name, file_type, file_data)
        VALUES (%s,%s,%s,%s)
    """, (
        patient_id,
        file.filename,
        file.content_type,
        psycopg2.Binary(file_data)
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "file saved"})

@app.route("/files/<int:file_id>")
def get_file(file_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT file_name, file_type, file_data FROM medical_files WHERE id=%s", (file_id,))
    file = cur.fetchone()

    cur.close()
    conn.close()

    return send_file(
        BytesIO(file[2]),
        download_name=file[0],
        mimetype=file[1]
    )

@app.route("/search")
def search():
    amka = request.args.get("amka")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM patients
        WHERE amka=%s
    """, (amka,))

    result = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(result)

if __name__ == "__main__":
    app.run()

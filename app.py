from flask import Flask, render_template, request, redirect, send_file
import psycopg2
import io

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    database="medical",
    user="postgres",
    password="1234"
)

@app.route("/")
def index():
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients = cur.fetchall()
    cur.close()
    return render_template("index.html", patients=patients)

@app.route("/add_patient", methods=["POST"])
def add_patient():
    photo = request.files["photo"].read()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (amka, first_name, last_name, birth_date, phone, email, photo)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["amka"],
        request.form["first_name"],
        request.form["last_name"],
        request.form["birth_date"],
        request.form["phone"],
        request.form["email"],
        photo
    ))
    conn.commit()
    cur.close()
    return redirect("/")

@app.route("/patient_photo/<int:id>")
def patient_photo(id):
    cur = conn.cursor()
    cur.execute("SELECT photo FROM patients WHERE id=%s", (id,))
    photo = cur.fetchone()[0]
    cur.close()
    return send_file(io.BytesIO(photo), mimetype="image/jpeg")

@app.route("/add_file/<int:id>", methods=["POST"])
def add_file(id):
    file = request.files["file"]
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO files (patient_id, file_name, file_type, file_data)
        VALUES (%s,%s,%s,%s)
    """, (
        id,
        file.filename,
        file.content_type,
        file.read()
    ))
    conn.commit()
    cur.close()
    return redirect("/")

@app.route("/file/<int:id>")
def get_file(id):
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_type, file_data FROM files WHERE id=%s", (id,))
    file = cur.fetchone()
    cur.close()
    return send_file(io.BytesIO(file[2]), download_name=file[0], mimetype=file[1])

@app.route("/add_prescription/<int:id>", methods=["POST"])
def add_prescription(id):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prescriptions (patient_id, prescription_date, doctor_name, therapy_text)
        VALUES (%s,%s,%s,%s)
    """, (
        id,
        request.form["date"],
        request.form["doctor"],
        request.form["therapy"]
    ))
    conn.commit()
    cur.close()
    return redirect("/")

if __name__ == "__main__":
    app.run()

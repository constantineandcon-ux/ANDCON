from flask import Flask, render_template_string, request, redirect, Response
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Professional Medical System</title>
<style>
body{font-family:Arial;background:#f0f0f0;padding:20px}
.card{background:white;padding:15px;margin-bottom:15px;border-radius:8px}
input,button{padding:8px;margin:5px}
button{background:#007BFF;color:white;border:none;border-radius:5px}
</style>
</head>
<body>

<h1>Professional Medical System Online</h1>

<div class="card">
<h2>Νέος Ασθενής</h2>
<form method="POST" action="/add_patient">
<input name="amka" placeholder="AMKA" required>
<input name="first_name" placeholder="Όνομα" required>
<input name="last_name" placeholder="Επώνυμο" required>
<input type="date" name="birth_date">
<input name="phone" placeholder="Τηλέφωνο">
<input name="email" placeholder="Email">
<button type="submit">Αποθήκευση</button>
</form>
</div>

{% for p in patients %}
<div class="card">
<h3>{{p[2]}} {{p[3]}} (AMKA: {{p[1]}})</h3>

<form method="POST" action="/update_patient/{{p[0]}}">
<input name="first_name" value="{{p[2]}}" required>
<input name="last_name" value="{{p[3]}}" required>
<input name="phone" value="{{p[5]}}">
<input name="email" value="{{p[6]}}">
<button type="submit">Ενημέρωση</button>
</form>

<a href="/delete_patient/{{p[0]}}">
<button style="background:red">Διαγραφή Ασθενή</button>
</a>

<h4>Αρχεία</h4>
<form method="POST" action="/upload_file/{{p[0]}}" enctype="multipart/form-data">
<input type="file" name="file" required>
<button type="submit">Ανέβασμα Αρχείου</button>
</form>

{% for f in p[7] %}
<div>
<a href="/view_file/{{f[0]}}" target="_blank">{{f[1]}}</a>
<a href="/delete_file/{{f[0]}}">
<button style="background:red">Διαγραφή</button>
</a>
</div>
{% endfor %}

</div>
{% endfor %}

</body>
</html>
"""

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
    return render_template_string(HTML, patients=patient_list)

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

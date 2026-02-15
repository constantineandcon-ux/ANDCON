from flask import Flask, request, render_template_string, redirect
from supabase import create_client
import uuid
import datetime

SUPABASE_URL = "ΒΑΛΕ_ΕΔΩ_URL"
SUPABASE_KEY = "ΒΑΛΕ_ΕΔΩ_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Ιατρικό Σύστημα Υπουργείου</title>
<style>
body { font-family: Arial; background:#111; color:white; padding:30px;}
input, textarea { width:100%; padding:8px; margin:5px 0;}
button { padding:10px; background:#00ff88; border:none;}
table { width:100%; margin-top:30px; border-collapse: collapse;}
td, th { border:1px solid #444; padding:6px;}
a { color:#00ff88;}
</style>
</head>
<body>

<h2>Νέος Ασθενής</h2>
<form method="post" enctype="multipart/form-data">
<input name="amka" placeholder="ΑΜΚΑ" required>
<input name="first_name" placeholder="Όνομα" required>
<input name="last_name" placeholder="Επώνυμο" required>
<input name="birth_date" placeholder="Ημερομηνία Γέννησης">
<input name="prescription_code" placeholder="Κωδικός Συνταγής">
<input name="prescription_date" placeholder="Ημερομηνία Συνταγής">
<textarea name="therapy_text" placeholder="Θεραπεία"></textarea>

<label>Φωτογραφία</label>
<input type="file" name="photo">

<label>Ακτινογραφία</label>
<input type="file" name="xray">

<button type="submit">Αποθήκευση</button>
</form>

<h2>Αναζήτηση με ΑΜΚΑ</h2>
<form method="get">
<input name="search" placeholder="ΑΜΚΑ">
<button type="submit">Αναζήτηση</button>
</form>

<table>
<tr>
<th>ΑΜΚΑ</th>
<th>Όνομα</th>
<th>Συνταγή</th>
<th>Θεραπεία</th>
<th>Φωτο</th>
<th>Ακτινογραφία</th>
</tr>
{% for p in patients %}
<tr>
<td>{{p['amka']}}</td>
<td>{{p['first_name']}} {{p['last_name']}}</td>
<td>{{p['prescription_code']}} - {{p['prescription_date']}}</td>
<td>{{p['therapy_text']}}</td>
<td>{% if p['photo_url'] %}<a href="{{p['photo_url']}}" target="_blank">Άνοιγμα</a>{% endif %}</td>
<td>{% if p['xray_url'] %}<a href="{{p['xray_url']}}" target="_blank">Άνοιγμα</a>{% endif %}</td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":

        amka = request.form["amka"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        birth_date = request.form["birth_date"]
        prescription_code = request.form["prescription_code"]
        prescription_date = request.form["prescription_date"]
        therapy_text = request.form["therapy_text"]

        photo = request.files["photo"]
        xray = request.files["xray"]

        photo_url = None
        xray_url = None

        if photo.filename != "":
            filename = "photo_" + str(uuid.uuid4())
            supabase.storage.from_("medical_files").upload(filename, photo.read())
            photo_url = supabase.storage.from_("medical_files").get_public_url(filename)

        if xray.filename != "":
            filename = "xray_" + str(uuid.uuid4())
            supabase.storage.from_("medical_files").upload(filename, xray.read())
            xray_url = supabase.storage.from_("medical_files").get_public_url(filename)

        supabase.table("patients").insert({
            "amka": amka,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "prescription_code": prescription_code,
            "prescription_date": prescription_date,
            "therapy_text": therapy_text,
            "photo_url": photo_url,
            "xray_url": xray_url,
            "created_at": str(datetime.datetime.now())
        }).execute()

        return redirect("/")

    search = request.args.get("search")

    if search:
        patients = supabase.table("patients").select("*").eq("amka", search).execute().data
    else:
        patients = supabase.table("patients").select("*").order("created_at", desc=True).execute().data

    return render_template_string(HTML, patients=patients)

if __name__ == "__main__":
    app.run()

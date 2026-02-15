from flask import Flask, request, render_template_string, redirect
from supabase import create_client
import uuid

# ================= ΡΥΘΜΙΣΕΙΣ =================

SUPABASE_URL = "ΒΑΛΕ_ΕΔΩ_ΤΟ_URL_ΣΟΥ"
SUPABASE_KEY = "ΒΑΛΕ_ΕΔΩ_ΤΟ_ΚΛΕΙΔΙ_ΣΟΥ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# ================= HTML ΠΕΡΙΒΑΛΛΟΝ =================

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Ιατρικό Σύστημα</title>
<style>
body { font-family: Arial; margin:40px; background:#111; color:white;}
input, textarea { width:100%; padding:10px; margin:5px 0;}
button { padding:10px 20px; background:#00ff88; border:none; cursor:pointer;}
table { width:100%; margin-top:20px; border-collapse: collapse;}
td, th { border:1px solid #444; padding:8px;}
a { color:#00ff88;}
</style>
</head>
<body>

<h2>Νέος Ασθενής</h2>

<form method="post" enctype="multipart/form-data">
<input name="amkA" placeholder="ΑΜΚΑ" required>
<input name="first_name" placeholder="Όνομα" required>
<input name="last_name" placeholder="Επώνυμο" required>
<textarea name="diagnosis" placeholder="Διάγνωση"></textarea>
<input type="file" name="xray">
<button type="submit">Αποθήκευση</button>
</form>

<h2>Αναζήτηση</h2>
<form method="get">
<input name="search" placeholder="ΑΜΚΑ">
<button type="submit">Αναζήτηση</button>
</form>

<table>
<tr>
<th>ΑΜΚΑ</th>
<th>Όνομα</th>
<th>Διάγνωση</th>
<th>Ακτινογραφία</th>
</tr>
{% for p in patients %}
<tr>
<td>{{p['amka']}}</td>
<td>{{p['first_name']}} {{p['last_name']}}</td>
<td>{{p['diagnosis']}}</td>
<td>
{% if p['xray_url'] %}
<a href="{{p['xray_url']}}" target="_blank">Άνοιγμα</a>
{% endif %}
</td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

# ================= ΛΕΙΤΟΥΡΓΙΑ =================

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        amka = request.form["amkA"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        diagnosis = request.form["diagnosis"]

        xray_file = request.files["xray"]
        xray_url = None

        if xray_file.filename != "":
            filename = str(uuid.uuid4()) + "_" + xray_file.filename
            supabase.storage.from_("xrays").upload(filename, xray_file.read())
            xray_url = supabase.storage.from_("xrays").get_public_url(filename)

        supabase.table("patients").insert({
            "amka": amka,
            "first_name": first_name,
            "last_name": last_name,
            "diagnosis": diagnosis,
            "xray_url": xray_url
        }).execute()

        return redirect("/")

    search = request.args.get("search")

    if search:
        patients = supabase.table("patients").select("*").eq("amka", search).execute().data
    else:
        patients = supabase.table("patients").select("*").execute().data

    return render_template_string(HTML, patients=patients)


if __name__ == "__main__":
    app.run()

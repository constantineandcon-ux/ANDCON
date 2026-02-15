from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(name)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
file = request.files["file"]
if file.filename != "":
filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
file.save(filepath)
return redirect(url_for("index"))

if name == "main":
app.run()

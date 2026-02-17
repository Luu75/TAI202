from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

API_URL = "http://localhost:5000/v1/usuarios/"

@app.route("/")
def index():
    try:
        response = requests.get(API_URL)
        data = response.json()
        usuarios = data.get("usuarios", [])
    except:
        usuarios = []
    return render_template("index.html", usuarios=usuarios)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        nuevo_usuario = {
            "id": int(request.form["id"]),
            "nombre": request.form["nombre"],
            "edad": int(request.form["edad"])
        }

        requests.post(API_URL, json=nuevo_usuario)
        return redirect("/")

    return render_template("create.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        usuario_actualizado = {
            "id": id,
            "nombre": request.form["nombre"],
            "edad": int(request.form["edad"])
        }

        requests.put(f"{API_URL}{id}", json=usuario_actualizado)
        return redirect("/")

    # Obtener usuario actual
    response = requests.get(API_URL)
    usuarios = response.json().get("usuarios", [])
    usuario = next((u for u in usuarios if u["id"] == id), None)

    return render_template("edit.html", usuario=usuario)

@app.route("/delete/<int:id>")
def delete(id):
    requests.delete(f"{API_URL}{id}")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5010)

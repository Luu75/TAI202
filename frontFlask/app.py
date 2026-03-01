from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

API_URL = "http://localhost:5000/v1/usuarios/"

@app.route("/")
def index():
    response = requests.get(API_URL)
    data = response.json()
    usuarios = data.get("usuarios", [])
    return render_template("index.html", usuarios=usuarios)

@app.route("/crear", methods=["POST"])
def crear_usuario():
        nuevo_usuario = {
            "id": int(request.form["id"]),
            "nombre": request.form["nombre"],
            "edad": int(request.form["edad"])
        }

        requests.post(API_URL, json=nuevo_usuario)
        return redirect("/")

@app.route("/eliminar/<int:id>")
def eliminar_usuario(id):
    requests.delete(API_URL + str(id))
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5010)

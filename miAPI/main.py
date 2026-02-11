from fastapi import FastAPI
import asyncio

#Instancia del servidor
app = FastAPI()

#Endpoints
@app.get("/")
async def read_root():
    return {"mensaje": "¡Hola, mundo! Esta es mi API con FastAPI."}

@app.get("/bienvenido")
async def bienvenido():
    return {
        "mensaje": "Bienvenido a mi FastAPI",
        "estatus": "activo"
    }

# Endpoint con parámetro obligatorio
@app.get("/usuarios/{id}")
async def obtener_usuario(id: int):
    return {
        "mensaje": "Usuario encontrado",
        "id_usuario": id
    }

# Endpoint con parámetro opcional
@app.get("/saludo")
async def saludo(nombre: str = "Invitado"):
    return {
        "mensaje": f"Hola {nombre}"
    }




from fastapi import FastAPI
import asyncio

#Instancia del servidor
app = FastAPI()

#Endpoints
@app.get("/")
async def read_root():
    return {"message": "¡Hola, mundo! Esta es mi API con FastAPI."}

@app.get("/bienvenido")
async def bienvenido():
    return {
        "message": "Bienvenido a mi FastAPI",
        "estatus": "activo"
    }


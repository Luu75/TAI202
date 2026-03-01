from fastapi import FastAPI, status, HTTPException
from typing import Optional 
import asyncio
from pydantic import BaseModel, Field   #<----- Agregar BaseModel pydantic

app = FastAPI()

#Instancia del servidor
app= FastAPI(
    title="Mi primer API",
    description="Luis Enrique Gachuzo E",
    version="1.0",
)

usuarios = [
    {"id": 1, "nombre": "Eros", "edad": 21},
    {"id": 2, "nombre": "Axel", "edad": 20},
    {"id": 3, "nombre": "Carmen", "edad": 21},
]

#**********
# Modelo de Validacion pydantic <---- Creamos el modelo
#**********

class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description= "Identificador de Usuario")
    nombre: str= Field(..., min_length=3, max_length=50, description="Juanita")
    edad: int= Field(..., ge=1, le=123, description="Edad valida entre 1 y 123")


@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['CRUD HTTP'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:crear_usuario): #<---- usuamos el modelo
    for usr in usuarios:
        if usr["id"] == usuario.id: #<----cambiamos por que ya no usamos dict
            raise HTTPException(
                status_code=400, 
                detail="El ID ya existe"
            )
    
    usuarios.append(usuario)
    return {
        "mensaje": "Usuario Creado", 
        "Usuario": usuario
    }


#NUEVAS RUTAS: PUT, PATCH Y DELETE 

@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: dict):
    # Buscamos el índice del usuario
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            # Reemplazamos el diccionario viejo por el nuevo
            usuarios[indice] = usuario_actualizado
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}
    
    # Si termina el ciclo y no lo encuentra
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.patch("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: dict):
    """PATCH: Modifica solo los campos enviados."""
    for usr in usuarios:
        if usr["id"] == usuario_id:
            # Actualizamos solo las llaves que vienen en el diccionario
            usr.update(datos_parciales)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}
    
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.delete("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def eliminar_usuario(usuario_id: int):
    """DELETE: Elimina al usuario de la lista."""
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": "Usuario eliminado", "usuario": usuario_eliminado}
    
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

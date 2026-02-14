from fastapi import FastAPI
import asyncio
from typing import Optional

app= FastAPI (
    tittle= "Mi primer API",
    description= "Luis Enrique Gachuzo E",
    version= "1.0"
)

#TB ficticia
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Aly","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

#Endpoints
@app.get("/")
async def holamundo():
    return {"mensaje":"Hola Mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {
        "mensaje": "Bienvenido a FastAPI",
        "estatus":"200",
    }

@app.get("/v1/parametroOb/{id}", tags=['Parametro Obligario'])
async def consultauno(id:int):
    return {"mensaje":"usuario encontrado",
            "usuario":id,
            "status":"200"  }

@app.get("/v1/parametro0p/", tags=['Paremtro Opcional'])
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return{"mensaje":"usuario encontrado","usuario":usuarioK}
        return{"mensaje":"usuario no encontrado","status":"200"}
    else:
        return {"mensaje":"No se proporciono id","status":"200"}
    


            
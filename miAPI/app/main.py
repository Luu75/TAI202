from fastapi import FastAPI
from app.router import usuario, misc

#Instancia del servidor
app= FastAPI(
    title="Mi primer API",
    description="Luis Enrique Gachuzo E",
    version="1.0",
)

app.include_router(usuario.router)
app.include_router(misc.router)
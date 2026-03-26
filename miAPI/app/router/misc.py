import asyncio
from typing import Optional
from fastapi import APIRouter

router = APIRouter(tags=["Miscelaneo"])

@router.get("/")
async def holamundo():
    return {"mensaje": "Hola mundo FastAPI"}

@router.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {"mensaje": "Bienvenido a FastAPI"}




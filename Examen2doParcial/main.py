from fastapi import FastAPI
import uvicorn  
import asyncio
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
app = FastAPI()


class crearReserva(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=6, description="Nombre del Cliente")

class Listarserva(BaseModel):
    FechaReserva: str = Field(..., description="Fecha de la reserva futura entre 8:00 AM y 10:00 PM")

    
class ConsultarporID(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a consultar")

class confirmarReserva(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a confirmar")

class cancelarReserva(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a cancelar")
    

@app.post("/crear_reserva")
async def crear_reserva(reserva: crearReserva):
    return {"message": f"Reserva creada para {reserva.nombre_cliente}"}

@app.post("/listar_reserva")
async def listar_reserva(reserva: Listarserva):
    return {"message": f"Reservas listadas para la fecha {reserva.FechaReserva}"}

@app.post("/consultar_reserva")
async def consultar_reserva(reserva: ConsultarporID):
    return {"message": f"Reserva consultada con ID {reserva.id_reserva}"}

@app.post("/confirmar_reserva")
async def confirmar_reserva(reserva: confirmarReserva):
    return {"message": f"Reserva confirmada con ID {reserva.id_reserva}"}

@app.post("/cancelar_reserva")
async def cancelar_reserva(reserva: cancelarReserva):
    return {"message": f"Reserva cancelada con ID {reserva.id_reserva}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5020)










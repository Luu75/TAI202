from fastapi import FastAPI
import uvicorn  
import asyncio
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
app = FastAPI()


security= HTTPBasic()

def verificar_peticion(credentiales:HTTPBasicCredentials=Depends(security)):
    usuario_correcto= secrets.compare_digest(credentiales.username, "admin")
    contrasena_correcta= secrets.compare_digest(credentiales.password, "rest123")

    if not (usuario_correcto and contrasena_correcta):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no validas",
        )
    return credentiales.username


class crearReserva(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva")
    nombre_cliente: str = Field(..., min_length=2, max_length=6, description="Nombre del Cliente")
      #Fecha reserva futura entre 8:00 AM y 10:00 PM
    FechaReserva: datetime = Field(..., description="Fecha y hora de la reserva")
    CupodePersonas: str = Field(..., min_length=1, max_length=10, description="Cupo de personas para la reserva")

#no permitir reservas en domingos
    @validator('FechaReserva')
    def validar_fecha_reserva(cls, value):
        if value.weekday() == 6:  
            raise ValueError("No se permiten reservas los domingos")
        return value

    
class ConsultarporID(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a consultar")

class confirmarReserva(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a confirmar")

class cancelarReserva(BaseModel):
    id_reserva: int = Field(..., description="ID de la reserva a cancelar")
    

#Aplicar HTTPBasic a Listar reservas y Cancelar Reservas
@app.get("/v1/listar_reservas", tags=["Reservas"])
async def listar_reservas(username: str = Depends(verificar_peticion)):
    return {"message": "Listado de reservas"}

@app.delete("/v1/cancelar_reserva", tags=["Reservas"])
async def cancelar_reserva(reserva: cancelarReserva, username: str = Depends(verificar_peticion)):
    return {"message": f"Reserva cancelada con ID {reserva.id_reserva}"}

@app.post("/v1/crear_reserva", tags=["Reservas"])
async def crear_reserva(reserva: crearReserva):
    return {"message": f"Reserva creada con ID {reserva.id_reserva}"}

@app.get("/v1/consultar_reserva", tags=["Reservas"] )
async def consultar_reserva(reserva: ConsultarporID):
    return {"message": f"Consulta de reserva con ID {reserva.id_reserva}"}

@app.post("/v1/confirmar_reserva", tags=["Reservas"])
async def confirmar_reserva(reserva: confirmarReserva):
    return {"message": f"Reserva confirmada con ID {reserva.id_reserva}"}

if __name__ == "__main__":
    uvicorn.run(app, host="5020", port=5020)




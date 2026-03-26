from pydantic import BaseModel, Field
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50, example="Luis")
    edad: int = Field(..., ge=1, le=123, description="Edad del usuario entre 1 y 123 años")

class crear_usuario(UsuarioBase):
    pass

class UsuarioResponse(UsuarioBase):
    id: int
    
    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    edad: Optional[int] = Field(None, ge=1, le=123)
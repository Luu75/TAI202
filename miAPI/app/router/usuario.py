from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.models.usuario import crear_usuario, UsuarioResponse, UsuarioUpdate
from app.data.database import usuarios
from app.security.auth import verificar_peticion
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data import usuario as dbUsuario

router = APIRouter(
    prefix="/v1/usuarios",
    tags=["HTTP CRUD"]
)

@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):

    queryUsuarios = db.query(dbUsuario.usuario).all()

    return {
        "status": "200",
        "total": len(queryUsuarios),
        "usuarios": queryUsuarios
    }

@router.get("/{id}")
async def leer_usuario_por_id(id: int, db: Session = Depends(get_db)):
    usuario = db.query(dbUsuario.usuario).filter(dbUsuario.usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuarioP: crear_usuario, db: Session = Depends(get_db)):
    nuevoU = dbUsuario.usuario(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)
    return {
        "mensaje": "Usuario Agregado",
        "usuario": nuevoU
    }

@router.put("/{id}")
async def actualizar_usuario(id: int, usuario_actualizado: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(dbUsuario.usuario).filter(dbUsuario.usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario_actualizado.nombre is not None:
        usuario.nombre = usuario_actualizado.nombre
    if usuario_actualizado.edad is not None:
        usuario.edad = usuario_actualizado.edad
    
    db.commit()
    db.refresh(usuario)
    return usuario

@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def actualizar_parcial_usuario(id: int, usuario_actualizado: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.query(dbUsuario.usuario).filter(dbUsuario.usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario_actualizado.nombre is not None:
        usuario.nombre = usuario_actualizado.nombre
    if usuario_actualizado.edad is not None:
        usuario.edad = usuario_actualizado.edad
    
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(dbUsuario.usuario).filter(dbUsuario.usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado correctamente"}


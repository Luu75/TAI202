from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt

# --- CONFIGURACIONES (a) ---
SECRET_KEY = "mi_llave_secreta_super_segura" # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="Mi primer API con JWT",
    description="Luis Enrique Gachuzo E",
    version="2.0",
)

# Base de datos ficticia- 
usuarios = [
    {"id": 1, "nombre": "Eros", "edad": 21},
    {"id": 2, "nombre": "Axel", "edad": 20},
    {"id": 3, "nombre": "Carmen", "edad": 21},
]

# Configuración del esquema de seguridad
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de Usuario")
    nombre: str = Field(..., min_length=3, max_length=50)
    edad: int = Field(..., ge=1, le=123)

# --- GENERACIÓN DE TOKENS (b) ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- VALIDACIÓN DE TOKENS (c) ---
async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token o ha expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# Ruta para observar el token
@app.post("/token", tags=['Seguridad'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validación simple de usuario (como en tu ejemplo original)
    if form_data.username == "luisenrique" and form_data.password == "123456":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

# --- ENDPOINTS ---

@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['CRUD HTTP'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: CrearUsuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
    usuarios.append(usuario.dict())
    return {"mensaje": "Usuario Creado", "Usuario": usuario}

# --- PROTECCIÓN DE ENDPOINTS (d) ---

@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_completo(
    usuario_id: int, 
    usuario_actualizado: dict, 
    token: str = Depends(obtener_usuario_actual) # Protegido
):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios[indice] = usuario_actualizado
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def eliminar_usuario(
    usuario_id: int, 
    user: str = Depends(obtener_usuario_actual) # Protegido
):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": f"Usuario eliminado por {user}", "usuario": usuario_eliminado}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
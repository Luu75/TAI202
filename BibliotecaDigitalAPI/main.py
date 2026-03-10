"""
GUÍA COMPLETA DE FASTAPI PARA EXAMEN
=====================================
Este archivo contiene todo lo necesario para tu examen de FastAPI:
- Configuración básica de FastAPI
- Verbos HTTP (GET, POST, PUT, DELETE, PATCH)
- Validación con Pydantic
- Protección con HTTP Basic Auth
- Protección con OAuth2 + JWT
"""

from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import jwt
import secrets
from passlib.context import CryptContext
import uvicorn

# CONFIGURACIÓN BÁSICA
app = FastAPI(
    title="API Guía para Examen",
    description="API completa con FastAPI para estudio",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIGURACIÓN DE SEGURIDAD
SECRET_KEY = "tu_clave_secreta_aqui_cambia_en_produccion"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquemas de seguridad
security_basic = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MODELOS PYDANTIC PARA VALIDACIÓN
class UsuarioBase(BaseModel):
    """Modelo base para usuarios con validación Pydantic"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Email válido")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('El username debe ser alfanumérico')
        return v

class UsuarioCreate(UsuarioBase):
    """Modelo para crear usuarios (incluye contraseña)"""
    password: str = Field(..., min_length=6, description="Contraseña mínima 6 caracteres")
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

class UsuarioResponse(UsuarioBase):
    """Modelo para respuesta de usuarios (sin contraseña)"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    """Modelo base para productos"""
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: float = Field(..., gt=0, description="Precio debe ser mayor a 0")
    descripcion: Optional[str] = Field(None, max_length=500)
    stock: int = Field(default=0, ge=0, description="Stock no puede ser negativo")

class ProductoCreate(ProductoBase):
    """Modelo para crear productos"""
    pass

class ProductoUpdate(BaseModel):
    """Modelo para actualizar productos (todos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    precio: Optional[float] = Field(None, gt=0)
    descripcion: Optional[str] = Field(None, max_length=500)
    stock: Optional[int] = Field(None, ge=0)

class ProductoResponse(ProductoBase):
    """Modelo para respuesta de productos"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Modelo para token JWT"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Modelo para datos del token"""
    username: Optional[str] = None

# BASE DE DATOS SIMULADA (en memoria)
# En examen, puedes usar esta simulación o diccionarios simples
usuarios_db = {}
productos_db = {}
next_user_id = 1
next_product_id = 1

# USUARIO ADMIN POR DEFECTO
admin_password = pwd_context.hash("admin123")
usuarios_db[1] = {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "password": admin_password,
    "created_at": datetime.now()
}

# FUNCIONES DE UTILIDAD
def verify_password(plain_password, hashed_password):
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashear contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(username: str):
    """Obtener usuario por username"""
    for user in usuarios_db.values():
        if user["username"] == username:
            return user
    return None

# DEPENDENCIAS DE AUTENTICACIÓN
async def get_current_user_basic(credentials: HTTPBasicCredentials = Depends(security_basic)):
    """Autenticación con HTTP Basic"""
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

async def get_current_user_jwt(token: str = Depends(oauth2_scheme)):
    """Autenticación con OAuth2 JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# ENDPOINTS - VERBOS HTTP

# ====== ENDPOINTS DE AUTENTICACIÓN ======
@app.post("/token", response_model=Token, tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 Password Flow - Obtener token JWT"""
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ====== ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN) ======
@app.get("/", tags=["Públicos"])
async def root():
    """Endpoint raíz - GET"""
    return {"message": "API de FastAPI para examen", "version": "1.0.0"}

@app.get("/public/info", tags=["Públicos"])
async def public_info():
    """Endpoint público con información básica - GET"""
    return {
        "api": "FastAPI Guía Examen",
        "features": ["HTTP Basic Auth", "OAuth2 JWT", "Pydantic Validation"],
        "endpoints": {
            "public": ["/", "/public/info", "/productos"],
            "basic_auth": ["/basic/profile"],
            "jwt_auth": ["/jwt/profile", "/productos/crear"],
            "admin": ["/admin/stats"]
        }
    }

# ====== ENDPOINTS CON HTTP BASIC AUTH ======
@app.get("/basic/profile", tags=["HTTP Basic Auth"])
async def get_profile_basic(current_user: dict = Depends(get_current_user_basic)):
    """Obtener perfil del usuario - GET con HTTP Basic"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "auth_method": "HTTP Basic",
        "user_id": current_user["id"]
    }

# ====== ENDPOINTS CON OAuth2 JWT ======
@app.get("/jwt/profile", tags=["OAuth2 JWT"])
async def get_profile_jwt(current_user: dict = Depends(get_current_user_jwt)):
    """Obtener perfil del usuario - GET con JWT"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "auth_method": "OAuth2 JWT",
        "user_id": current_user["id"]
    }

# ====== ENDPOINTS DE PRODUCTOS (CRUD COMPLETO) ======

# GET - Obtener todos los productos
@app.get("/productos", response_model=List[ProductoResponse], tags=["Productos"])
async def get_productos():
    """GET - Obtener todos los productos"""
    return list(productos_db.values())

# GET - Obtener producto por ID
@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def get_producto(producto_id: int):
    """GET - Obtener producto específico por ID"""
    if producto_id not in productos_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return productos_db[producto_id]

# POST - Crear producto (requiere JWT)
@app.post("/productos", response_model=ProductoResponse, tags=["Productos"])
async def create_producto(
    producto: ProductoCreate, 
    current_user: dict = Depends(get_current_user_jwt)
):
    """POST - Crear nuevo producto (requiere autenticación JWT)"""
    global next_product_id
    
    nuevo_producto = {
        "id": next_product_id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "descripcion": producto.descripcion,
        "stock": producto.stock,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    productos_db[next_product_id] = nuevo_producto
    next_product_id += 1
    
    return nuevo_producto

# PUT - Actualizar producto completo
@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def update_producto(
    producto_id: int,
    producto: ProductoCreate,
    current_user: dict = Depends(get_current_user_jwt)
):
    """PUT - Actualizar producto completo"""
    if producto_id not in productos_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_actualizado = {
        "id": producto_id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "descripcion": producto.descripcion,
        "stock": producto.stock,
        "created_at": productos_db[producto_id]["created_at"],
        "updated_at": datetime.now()
    }
    
    productos_db[producto_id] = producto_actualizado
    return producto_actualizado

# PATCH - Actualizar producto parcialmente
@app.patch("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
async def patch_producto(
    producto_id: int,
    producto: ProductoUpdate,
    current_user: dict = Depends(get_current_user_jwt)
):
    """PATCH - Actualizar producto parcialmente"""
    if producto_id not in productos_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto_actual = productos_db[producto_id]
    
    # Actualizar solo los campos proporcionados
    update_data = producto.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            producto_actual[field] = value
    
    producto_actual["updated_at"] = datetime.now()
    return producto_actual

# DELETE - Eliminar producto
@app.delete("/productos/{producto_id}", tags=["Productos"])
async def delete_producto(
    producto_id: int,
    current_user: dict = Depends(get_current_user_jwt)
):
    """DELETE - Eliminar producto"""
    if producto_id not in productos_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    del productos_db[producto_id]
    return {"message": f"Producto {producto_id} eliminado correctamente"}

# ====== ENDPOINTS DE USUARIOS ======

# POST - Crear usuario
@app.post("/usuarios", response_model=UsuarioResponse, tags=["Usuarios"])
async def create_usuario(usuario: UsuarioCreate):
    """POST - Crear nuevo usuario"""
    global next_user_id
    
    # Verificar si el username ya existe
    if get_user_by_username(usuario.username):
        raise HTTPException(status_code=400, detail="El username ya existe")
    
    nuevo_usuario = {
        "id": next_user_id,
        "username": usuario.username,
        "email": usuario.email,
        "password": get_password_hash(usuario.password),
        "created_at": datetime.now()
    }
    
    usuarios_db[next_user_id] = nuevo_usuario
    next_user_id += 1
    
    # Devolver usuario sin contraseña
    respuesta = nuevo_usuario.copy()
    del respuesta["password"]
    return respuesta

# GET - Obtener todos los usuarios (solo admin)
@app.get("/admin/usuarios", response_model=List[UsuarioResponse], tags=["Admin"])
async def get_all_users(current_user: dict = Depends(get_current_user_jwt)):
    """GET - Obtener todos los usuarios (solo admin)"""
    if current_user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede ver todos los usuarios")
    
    usuarios_respuesta = []
    for user in usuarios_db.values():
        user_copy = user.copy()
        del user_copy["password"]
        usuarios_respuesta.append(user_copy)
    
    return usuarios_respuesta

# ====== ENDPOINT DE EJEMPLOS AVANZADOS ======
@app.post("/admin/productos/bulk", tags=["Admin"])
async def create_bulk_productos(
    productos: List[ProductoCreate],
    current_user: dict = Depends(get_current_user_jwt)
):
    """POST - Crear múltiples productos a la vez"""
    if current_user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el admin puede crear productos masivamente")
    
    global next_product_id
    productos_creados = []
    
    for producto in productos:
        nuevo_producto = {
            "id": next_product_id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "descripcion": producto.descripcion,
            "stock": producto.stock,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        productos_db[next_product_id] = nuevo_producto
        productos_creados.append(nuevo_producto)
        next_product_id += 1
    
    return {"message": f"Se crearon {len(productos_creados)} productos", "productos": productos_creados}

# INSTRUCCIONES PARA EJECUTAR
if __name__ == "__main__":
    print("=" * 50)
    print("GUÍA FASTAPI PARA EXAMEN")
    print("=" * 50)
    print("Ejecuta: uvicorn main:app --reload")
    print("Documentación: http://localhost:8000/docs")
    print("Usuario admin: username=admin, password=admin123")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)

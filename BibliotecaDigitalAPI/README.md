# 📚 GUÍA COMPLETA DE FASTAPI PARA EXAMEN

Esta guía contiene todo lo que necesitas saber para tu examen de FastAPI. ¡Estudia estos conceptos y estarás listo!

## 🚀 INSTALACIÓN Y EJECUCIÓN

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la API
```bash
uvicorn main:app --reload
```

### 3. Acceder a la documentación
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 USUARIOS DE PRUEBA

### Usuario Admin
- **Username**: `admin`
- **Password**: `admin123`

## 📋 CONCEPTOS CLAVE PARA EXAMEN

### 1. **VERBOS HTTP**
```python
# GET - Obtener datos
@app.get("/productos")
async def get_productos():
    return productos_db

# POST - Crear datos
@app.post("/productos")
async def create_producto(producto: ProductoCreate):
    return nuevo_producto

# PUT - Actualizar datos completos
@app.put("/productos/{id}")
async def update_producto(id: int, producto: ProductoCreate):
    return producto_actualizado

# PATCH - Actualizar datos parciales
@app.patch("/productos/{id}")
async def patch_producto(id: int, producto: ProductoUpdate):
    return producto_parcial

# DELETE - Eliminar datos
@app.delete("/productos/{id}")
async def delete_producto(id: int):
    return {"message": "Eliminado"}
```

### 2. **VALIDACIÓN CON PYDANTIC**
```python
from pydantic import BaseModel, Field, EmailStr, validator

class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Debe ser alfanumérico')
        return v
```

**Tipos de validación:**
- `Field(..., min_length=3)` - Longitud mínima
- `Field(..., gt=0)` - Mayor que 0
- `Field(..., ge=0)` - Mayor o igual que 0
- `EmailStr` - Email válido
- `Optional[str]` - Campo opcional

### 3. **HTTP BASIC AUTH**
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security_basic = HTTPBasic()

async def get_current_user_basic(credentials: HTTPBasicCredentials = Depends(security_basic)):
    user = get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return user

@app.get("/basic/profile")
async def profile_basic(current_user: dict = Depends(get_current_user_basic)):
    return current_user
```

### 4. **OAUTH2 CON JWT**
```python
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## 🧪 EJEMPLOS DE USO

### Probar HTTP Basic Auth
```bash
curl -X GET "http://localhost:8000/basic/profile" \
  -u "admin:admin123"
```

### Probar OAuth2 JWT
```bash
# 1. Obtener token
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 2. Usar token
curl -X GET "http://localhost:8000/jwt/profile" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### Crear producto
```bash
curl -X POST "http://localhost:8000/productos" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop",
    "precio": 999.99,
    "descripcion": "Laptop potente",
    "stock": 10
  }'
```

## 📝 ESTRUCTURA DEL PROYECTO

```
fastapi_guia_completa/
├── main.py              # Código principal de la API
├── requirements.txt     # Dependencias
└── README.md           # Esta guía
```

## 🔍 ENDPOINTS DISPONIBLES

### Públicos
- `GET /` - Mensaje de bienvenida
- `GET /public/info` - Información de la API

### Autenticación
- `POST /token` - Obtener token JWT
- `GET /basic/profile` - Perfil con HTTP Basic
- `GET /jwt/profile` - Perfil con JWT

### Productos (CRUD)
- `GET /productos` - Listar todos
- `GET /productos/{id}` - Obtener por ID
- `POST /productos` - Crear (requiere JWT)
- `PUT /productos/{id}` - Actualizar completo (requiere JWT)
- `PATCH /productos/{id}` - Actualizar parcial (requiere JWT)
- `DELETE /productos/{id}` - Eliminar (requiere JWT)

### Usuarios
- `POST /usuarios` - Crear usuario
- `GET /admin/usuarios` - Listar todos (solo admin)

### Admin
- `POST /admin/productos/bulk` - Crear múltiples productos

## ⚠️ ERRORES COMUNES EN EXAMEN

1. **Olvidar importar dependencias**
   ```python
   from fastapi import FastAPI, Depends, HTTPException
   from pydantic import BaseModel
   ```

2. **No validar datos correctamente**
   ```python
   # ❌ Mal
   nombre: str
   
   # ✅ Bien
   nombre: str = Field(..., min_length=1, max_length=100)
   ```

3. **No manejar errores HTTP**
   ```python
   if not user:
       raise HTTPException(status_code=404, detail="No encontrado")
   ```

4. **Olvidar proteger endpoints**
   ```python
   # ❌ Olvidar la dependencia
   @app.get("/perfil")
   async def get_profile():
   
   # ✅ Con protección
   @app.get("/perfil")
   async def get_profile(current_user = Depends(get_current_user_jwt)):
   ```

## 🎯 CONSEJOS PARA EL EXAMEN

1. **Memoriza los imports principales**
2. **Practica la validación con Pydantic**
3. **Entiende la diferencia entre PUT y PATCH**
4. **Sabe cómo implementar ambos métodos de autenticación**
5. **Recuerda los códigos de estado HTTP comunes**:
   - 200: OK
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found

## 🚀 PARA PROBAR EN EXAMEN

1. **Crea un entorno virtual**: `python -m venv venv`
2. **Actívalo**: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
3. **Instala las dependencias**: `pip install -r requirements.txt`
4. **Ejecuta**: `uvicorn main:app --reload`
5. **Prueba en**: `http://localhost:8000/docs`

¡Mucha suerte en tu examen! 🍀

---

**Recuerda**: La clave es entender los conceptos, no memorizar código. Practica modificando los ejemplos y creando tus propios endpoints.

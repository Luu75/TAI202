from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field


class Usuario(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico válido")


class LibroBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Título del libro")
    autor: str = Field(..., min_length=2, max_length=100, description="Autor del libro")
    anio: int = Field(
        ...,
        gt=1450,
        le=datetime.now().year,
        description="Año de publicación mayor a 1450 y menor o igual al año actual",
    )
    paginas: int = Field(..., gt=1, description="Número de páginas mayor a 1")
    estado: str = Field(
        default="disponible",
        pattern="^(disponible|prestado)$",
        description='Estado del libro: "disponible" o "prestado"',
    )


class Libro(LibroBase):
    id: int


class LibroCreate(LibroBase):
    pass


class PrestamoCreate(BaseModel):
    libro_id: int = Field(..., gt=0, description="Identificador del libro a prestar")
    usuario: Usuario


class Prestamo(BaseModel):
    id: int
    libro_id: int
    usuario: Usuario
    fecha_prestamo: datetime
    devuelto: bool = False


app = FastAPI(
    title="Biblioteca Digital API",
    description="API para control de una biblioteca digital",
    version="1.0.0",
)


libros: Dict[int, Libro] = {}
prestamos: Dict[int, Prestamo] = {}
next_libro_id: int = 1
next_prestamo_id: int = 1


@app.post(
    "/v1/libros",
    response_model=Libro,
    status_code=status.HTTP_201_CREATED,
    tags=["Libros"],
)
async def registrar_libro(libro_in: LibroCreate) -> Libro:
    """
    Registra un libro nuevo en la biblioteca.

    Debe devolver:
    - 201 Created al registrar libro.
    - 400 Request si faltan datos o el nombre del libro no es válido (manejado por validación).
    """
    global next_libro_id

    if not libro_in.nombre.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del libro no es válido.",
        )

    nuevo_libro = Libro(id=next_libro_id, **libro_in.model_dump())
    libros[next_libro_id] = nuevo_libro
    next_libro_id += 1
    return nuevo_libro


@app.get("/v1/libros", response_model=List[Libro], tags=["Libros"])
async def listar_libros() -> List[Libro]:
    """Lista todos los libros disponibles (en cualquier estado)."""
    return list(libros.values())


@app.get("/v1/libros/buscar", response_model=List[Libro], tags=["Libros"])
async def buscar_libro_por_nombre(
    nombre: str = Query(..., min_length=2, description="Nombre (completo o parcial) del libro a buscar"),
) -> List[Libro]:
    """Busca libros por nombre usando coincidencia parcial (case-insensitive)."""
    termino = nombre.lower()
    resultados = [libro for libro in libros.values() if termino in libro.nombre.lower()]
    return resultados


def _obtener_libro_or_404(libro_id: int) -> Libro:
    libro = libros.get(libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro especificado no existe.",
        )
    return libro


@app.post(
    "/v1/prestamos",
    response_model=Prestamo,
    status_code=status.HTTP_201_CREATED,
    tags=["Préstamos"],
)
async def registrar_prestamo(prestamo_in: PrestamoCreate) -> Prestamo:
    """
    Registra el préstamo de un libro a un usuario.

    - 409 Conflict si el libro ya está prestado.
    """
    global next_prestamo_id

    libro = _obtener_libro_or_404(prestamo_in.libro_id)

    if libro.estado == "prestado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El libro ya está prestado.",
        )

    nuevo_prestamo = Prestamo(
        id=next_prestamo_id,
        libro_id=prestamo_in.libro_id,
        usuario=prestamo_in.usuario,
        fecha_prestamo=datetime.now(),
        devuelto=False,
    )
    prestamos[next_prestamo_id] = nuevo_prestamo
    next_prestamo_id += 1

    libro.estado = "prestado"
    libros[libro.id] = libro

    return nuevo_prestamo


@app.post(
    "/v1/prestamos/{prestamo_id}/devolver",
    response_model=Prestamo,
    status_code=status.HTTP_200_OK,
    tags=["Préstamos"],
)
async def marcar_libro_como_devuelto(prestamo_id: int) -> Prestamo:
    """
    Marca un libro como devuelto.

    - 200 OK al devolver un libro.
    - 409 Conflict si el registro de préstamo ya no existe.
    """
    prestamo = prestamos.get(prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El registro de préstamo ya no existe.",
        )

    if prestamo.devuelto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El libro ya fue devuelto anteriormente.",
        )

    prestamo.devuelto = True

   
    libro = libros.get(prestamo.libro_id)
    if libro:
        libro.estado = "disponible"
        libros[libro.id] = libro

    return prestamo


@app.delete(
    "/v1/prestamos/{prestamo_id}",
    status_code=status.HTTP_200_OK,
    tags=["Préstamos"],
)
async def eliminar_prestamo(prestamo_id: int) -> Dict[str, str]:
    """
    Elimina el registro de un préstamo.

    - 409 Conflict si el registro de préstamo ya no existe.
    """
    prestamo = prestamos.get(prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El registro de préstamo ya no existe.",
        )

   
    libro = libros.get(prestamo.libro_id)
    if libro and not prestamo.devuelto:
        libro.estado = "disponible"
        libros[libro.id] = libro

    del prestamos[prestamo_id]
    return {"mensaje": "Registro de préstamo eliminado correctamente."}

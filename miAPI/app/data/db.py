from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#1. definimos la url de conexion 
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:123456@localhost:5432/DB_miapi"
)

#2. Creamos el motor de conexion
engine = create_engine(DATABASE_URL)

#3. Preparamos el gestionador de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)

#4. Base declarativa para los modelos 
Base= declarative_base()

#5. Obtener sesiones de cada petición
def get_db():
    db= SessionLocal()
    try: 
        yield db 
    finally: 
        db.close()
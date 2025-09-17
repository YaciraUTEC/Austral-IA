from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Simulación de base de datos con contraseña
USUARIOS = {
    "nicol@demo.com": {"nombre": "Nicol", "password": "clavenicol"},
    "erick@demo.com": {"nombre": "Erick", "password": "clavejuan"},
    "mario@demo.com": {"nombre": "Mario", "password": "clavemario"},
    "felipe@demo.com": {"nombre": "Felipe", "password": "clavefelipe"},
    "Hector@demo.com": {"nombre": "Hector", "password": "clavehector"},
}

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    usuario = USUARIOS.get(data.email.lower())
    if usuario and usuario["password"] == data.password:
        return {"nombre": usuario["nombre"]}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@router.get("/usuario")
def get_usuario(email: str = Query(...)):
    usuario = USUARIOS.get(email.lower())
    if usuario:
        return {"nombre": usuario["nombre"]}
    return {"detail": "Usuario no encontrado"}



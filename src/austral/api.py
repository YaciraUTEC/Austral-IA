from fastapi import APIRouter
from pydantic import BaseModel
from austral.services.asistente import responder_asistente
    
router = APIRouter()

class PreguntaRequest(BaseModel):
    pregunta: str
    categoria: str = None  # Ahora aceptamos la categoría como parámetro opcional

@router.post("/asistente")
def preguntar_al_asistente(req: PreguntaRequest):
    respuesta = responder_asistente(req.pregunta, categoria=req.categoria)
    return {"respuesta": respuesta}

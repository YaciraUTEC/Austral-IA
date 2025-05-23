from fastapi import APIRouter
from pydantic import BaseModel
from austral.services.asistente import responder_asistente

router = APIRouter()

class PreguntaRequest(BaseModel):
    pregunta: str

@router.post("/asistente")
def preguntar_al_asistente(req: PreguntaRequest):
    respuesta = responder_asistente(req.pregunta)
    return {"respuesta": respuesta}

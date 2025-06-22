from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from austral.services.asistente import responder_asistente

router = APIRouter()

# Clase para la solicitud de la pregunta
class PreguntaRequest(BaseModel):
    user_id: str  # Incluye el user_id para manejar el contexto
    pregunta: str

@router.post("/asistente")
def preguntar_al_asistente(req: PreguntaRequest):
    try:
        # Llamamos al asistente pasándole la pregunta y el user_id
        respuesta = responder_asistente(req.pregunta, req.user_id)
        return {"respuesta": respuesta}
    except Exception as e:
        # En caso de error, se retorna un mensaje adecuado
        raise HTTPException(status_code=500, detail=f"Error al procesar la pregunta: {str(e)}")

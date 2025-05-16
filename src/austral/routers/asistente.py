from fastapi import APIRouter, Body
from austral.services.asistente import responder_asistente

router = APIRouter()

@router.post("/asistente")
def chat(pregunta: str = Body(..., embed=True)):
    try:
        respuesta = responder_asistente(pregunta)
        return {"respuesta": respuesta}
    except Exception as e:
        print("❌ Error en /asistente:", str(e))
        return {"error": str(e)}

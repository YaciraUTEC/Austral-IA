
# src/austral/tests/test_asistente.py
import sys
import os
sys.path.append(os.path.abspath("src"))

from austral.services.asistente import responder_asistente

pregunta = "Hay una parte "
respuesta = responder_asistente(pregunta)
print("🤖 Respuesta:", respuesta)

import sys
import os

OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output"))

from austral.services.asistente import responder_asistente

def test_prompt():
    preguntas_prueba = [
        "Hola, ¿cómo estás?",
        "¿Cuáles son las especificaciones de las calderas?",
        "Dame los antecedentes del proyecto",
        "¿Qué información hay en las tablas de capacidad?"
    ]

    print("\n🔍 Iniciando pruebas del prompt...\n")
    
    for pregunta in preguntas_prueba:
        print(f"\n📝 Pregunta: {pregunta}")
        print("-" * 80)
        try:
            respuesta = responder_asistente(pregunta)
            print(f"🤖 Respuesta:\n{respuesta}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        print("-" * 80)

if __name__ == "__main__":
    test_prompt()
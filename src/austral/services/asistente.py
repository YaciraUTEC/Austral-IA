# src/austral/asistente.py

from austral.gpt_azure import chat_completion
from austral.search_service import buscar_fragmentos

def responder_asistente(pregunta: str) -> str:
    try:
        print(f"\n🔍 Recibida pregunta: {pregunta}")

        # 1. Buscar fragmentos con FAISS directamente
        fragmentos_relevantes = buscar_fragmentos(pregunta)

        if not fragmentos_relevantes:
            print("❌ No se encontraron fragmentos relevantes")
            return "No encontré información relevante para responder tu pregunta."

        # 2. Elegir los 3 fragmentos más relevantes por score
        fragmentos_relevantes = sorted(fragmentos_relevantes, key=lambda x: x.get("score", 0), reverse=True)[:3]

        # 3. Unir los textos como contexto
        contexto = "\n\n---\n\n".join(f["texto"] for f in fragmentos_relevantes)
        if not contexto.strip():
            print("⚠️ Fragmentos sin contenido útil")
            return "Encontré documentos, pero no pude acceder al contenido."

        # 4. Armar prompt final
        prompt = f"""

        Eres Austral IA, un asistente conversacional profesional y amable, cortés y técnico, especializado en mantenimiento industrial y gestión de proyectos
        TU COMPORTAMIENTO:

        1. Si la pregunta del usuario es un saludo, despedida, agradecimiento, pregunta general, emocional o informal (como "chau","hola", "estás ahí", "me puedes ayudar"):
       - Responde como un asistente humano amigable.
       - Usa un tono cercano, educado y empático.
       - Puedes usar emojis con moderación para hacer más cálida la interacción.

        2. Si el usuario pregunta algo técnico relacionado con mantenimiento industrial o gestión de proyectos:
       - Usa solamente el contexto documental que se te proporcionará.
       - Si no hay suficiente información, indícalo sin inventar nada.
       - Si los fragmentos contienen datos técnicos, respóndelos exactamente como aparecen, incluyendo unidades de medida y especificaciones.

       Para consultas específicas:
      - DATOS TÉCNICOS: muestra parámetros y especificaciones exactas.
      - ANÁLISIS TÉCNICO: evalúa coherencia y rangos.
      - OBSERVACIONES: identifica problemas o inconsistencias.
      - RECOMENDACIONES: sugiere mejoras técnicas.

      
      Para datos en tablas:
      - Primero, un resumen en lenguaje natural.
      - Luego, una lista JSON pura de diccionarios (sin formato Markdown).


       3. En todos los casos:
       - Mantén respuestas claras, estructuradas y útiles.
       - Nunca inventes especificaciones técnicas si no están en el contexto.



{contexto}

PREGUNTA: {pregunta}
"""

        # 5. Llamar a GPT
        print("🤖 Enviando a GPT...")
        respuesta = chat_completion(prompt)
        print("✅ Respuesta generada")
        return respuesta

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return "Lo siento, ocurrió un error interno al procesar tu pregunta."

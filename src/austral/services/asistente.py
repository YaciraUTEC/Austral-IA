from austral.gpt_azure import chat_completion
from austral.search_service import buscar_fragmentos

def responder_asistente(pregunta: str) -> str:
    try:
        print(f"\n🔍 Recibida pregunta: {pregunta}")
        fragmentos_relevantes = buscar_fragmentos(pregunta)

        if not fragmentos_relevantes:
            print("No se encontraron fragmentos relevantes")
            return "No encontré información relevante para responder tu pregunta."

        fragmentos_relevantes = sorted(fragmentos_relevantes, key=lambda x: x.get("score", 0), reverse=True)[:3]
        contexto = "\n\n---\n\n".join(f["texto"] for f in fragmentos_relevantes)

        if not contexto.strip():
            print("⚠️ Fragmentos sin contenido útil")
            return "Encontré documentos, pero no pude acceder al contenido."

        prompt = f"""
Eres Austral IA, un asistente técnico especializado en mantenimiento industrial y gestión de proyectos. Tu objetivo es brindar respuestas claras, útiles y profesionales usando exclusivamente el contexto proporcionado. 

Si la información exacta no está presente, pero puedes inferirla razonablemente a partir del contenido, hazlo con cuidado y menciona que se trata de una deducción.

Reglas de comportamiento:

1. Si la respuesta está explícita en los fragmentos, respóndela tal como está (con unidades, valores, tablas, etc.).
2. Si la respuesta no está textual pero se puede deducir, hazlo de forma lógica, sin inventar.
3. Si no hay forma razonable de responder, indícalo claramente sin agregar información externa.
4. Para preguntas emocionales, saludos o agradecimientos, responde de forma cálida, profesional y empática.
5. Para tablas, proporciona primero un resumen breve en texto natural y luego una tabla estructurada y dividida con lineas. 

---


CONTEXTO EXTRAÍDO:

{contexto}

---

PREGUNTA DEL USUARIO: {pregunta}
"""

        print("🤖 Enviando a GPT...")
        respuesta = chat_completion(prompt)
        print("✅ Respuesta generada")
        return respuesta

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return "Lo siento, ocurrió un error interno al procesar tu pregunta."

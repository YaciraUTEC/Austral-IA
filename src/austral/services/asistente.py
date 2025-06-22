
from austral.gpt_azure import chat_completion, extraer_objeto_gpt
from austral.search_service import buscar_fragmentos
import difflib

# Memoria para guardar el contexto de la conversación por usuario
HISTORIAL_CONVERSACION = {}
MAX_MENSAJES_HISTORIAL = 5

SYSTEM_PROMPT= f"""
   "Eres Austral IA, un asistente técnico confiable y profesional, especializado en mantenimiento industrial y gestión de proyectos. Eres capaz de mantener un hilo conversacional. Tu tarea es proporcionar respuestas claras, bien redactadas y útiles, usando únicamente el contexto proporcionado.

        La información proviene de documentos PDF (como informes técnicos y reportes de avance) y hojas Excel (como cronogramas, presupuestos y seguimientos). Estos pueden incluir texto libre, tablas numéricas y descripciones detalladas de actividades.

        Tu estilo debe ser técnico pero accesible: escribe en lenguaje formal, redacta oraciones completas, resume si es necesario y evita repetir frases textuales del contexto sin adaptarlas. Siempre responde de forma elegante, clara y precisa.

        Comportamiento esperado:
        1. Si el usuario hace un saludo, agradecimiento u opinión, responde cordialmente y con empatía.
        2. Si la pregunta actual es una continuación de una pregunta anterior, asegúrate de mantener el mismo contexto y responde de manera coherente.
        3. Si la respuesta no está textual pero se puede deducir, hazlo de forma lógica, sin inventar.
        4. Si no encuentras suficiente información para responder la pregunta, indícalo de forma profesional.
        5. Si el usuario solicita una tabla, primero describe brevemente su contenido y luego muestra la tabla en markdown.


)   
  """
def construir_contexto(fragmentos):
    contexto = ""
    for f in fragmentos:
        texto_fragmento = f.get("texto", "").strip()
        if texto_fragmento:
            document_id = f.get("document_id", "Documento desconocido")
            fragment_id = f.get("fragment_id", "Fragmento sin nombre")
            sheet_name = f.get("sheet_name", "")
            encabezado = f"[document_id: {document_id}] [fragment_id: {fragment_id}]"
            if sheet_name:
                encabezado += f" [sheet_name: {sheet_name}]"
            contexto += encabezado + "\n" + texto_fragmento + "\n\n---\n\n"
    return contexto

def obtener_respuesta(pregunta, historial, contexto):
    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
    mensajes.append({"role": "user", "content": f"Contexto documental:\n{contexto}"})
    mensajes += historial[-MAX_MENSAJES_HISTORIAL:]
    mensajes.append({"role": "user", "content": pregunta})
    return chat_completion(mensajes)



def respuesta_contiene_info(respuesta, pregunta, contexto):
    prompt = (
        f"Pregunta: {pregunta}\n"
        f"Contexto: {contexto}\n"
        f"Respuesta: {respuesta}\n"
        "¿La respuesta contiene información relevante del contexto? (sí/no):"
    )
    mensajes = [
        {"role": "system", "content": "Eres un verificador de relevancia. Responde solo sí o no."},
        {"role": "user", "content": prompt}
    ]
    veredicto = chat_completion(mensajes).strip().lower()
    return veredicto.startswith("s")


'''
def respuesta_contiene_info(respuesta, contexto, pregunta):
    tokens_respuesta = set(respuesta.lower().split())
    tokens_contexto = set(contexto.lower().split())
    tokens_pregunta = set(pregunta.lower().split()) 

    interseccion = tokens_respuesta & tokens_contexto
    score = len(interseccion) / (len(tokens_respuesta) + 1)

    frases_genericas = {
        "no se encontró", "no hay información", "no incluye", "no contiene",
        "no se dispone", "no existe", "no está disponible"
    }
    contiene_negacion = any(frase in respuesta.lower() for frase in frases_genericas)

    repite_pregunta = len(tokens_respuesta & tokens_pregunta) / (len(tokens_pregunta) + 1) > 0.5

    # Si la respuesta es corta y contiene palabra clave de contexto o pregunta, acéptala
    if not contiene_negacion and len(respuesta.split()) < 12 and (len(interseccion) > 0 or len(tokens_respuesta & tokens_pregunta) > 0):
        return True

    return score > 0.05 and not contiene_negacion and not repite_pregunta

'''

def reformular_pregunta_explicita_gpt(pregunta, objeto, historial):
    prompt = (
        "Historial de la conversación:\n"
    )
    for mensaje in historial[-3:]:
        prompt += f"{mensaje['role']}: {mensaje['content']}\n"
    prompt += (
        f"Pregunta: {pregunta}\n"
        f"Objeto: {objeto}\n"
        "Reformula la pregunta para que sea explícita y clara, usando el objeto si es necesario. "
        "Asegúrate de que la pregunta resultante sea específica y permita obtener una respuesta detallada y técnica, incluyendo datos numéricos, modelos, fechas o cualquier información relevante del contexto. "
        "Si la pregunta ya es explícita, repítela tal cual."
    )
    mensajes = [
        {"role": "system", "content": "Eres un asistente experto en mantenimiento industrial. Reformula preguntas implícitas de manera explícita, clara y técnica, usando el contexto conversacional y asegurando que la nueva pregunta permita obtener respuestas detalladas y precisas."},
        {"role": "user", "content": prompt}
    ]
    return chat_completion(mensajes).strip()
def buscar_y_responder(pregunta, historial):
    fragmentos = buscar_fragmentos(pregunta)
    fragmentos = sorted(fragmentos, key=lambda x: x.get("score", 0), reverse=True)[:6] if fragmentos else []
    contexto = construir_contexto(fragmentos)
    if not contexto:
        return "", contexto
    respuesta = obtener_respuesta(pregunta, historial, contexto)
    return respuesta, contexto



''''
def es_cambio_de_tema(historial, pregunta_actual):
    if not historial:
        return False
    pregunta_anterior = ""
    # Busca la última pregunta del usuario en el historial
    for mensaje in reversed(historial):
        if mensaje["role"] == "user":
            pregunta_anterior = mensaje["content"]
            break
    if not pregunta_anterior:
        return False
    prompt = (
        "Dadas dos preguntas de un usuario, responde solo 'sí' si la segunda pregunta trata sobre un tema diferente a la primera, "
        "o 'no' si ambas preguntas tratan sobre el mismo tema o son seguimiento. "
        f"Primera pregunta: {pregunta_anterior}\n"
        f"Segunda pregunta: {pregunta_actual}\n"
        "¿La segunda pregunta es de un tema diferente? (sí/no):"
    )
    mensajes = [
        {"role": "system", "content": "Eres un detector de cambio de tema. Responde solo sí o no."},
        {"role": "user", "content": prompt}
    ]
    veredicto = chat_completion(mensajes).strip().lower()
    return veredicto.startswith("s")
'''



PRONOMBRES_SEGUIMIENTO = {"son", "es", "fue", "fueron", "tiene", "tienen", "hay", "cuánto", "cuántos", "cuántas", "qué", "cuál", "cuáles", "dónde", "cómo", "por qué", "quién", "quiénes", "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "su", "sus", "lo", "le", "les", "se"}

def es_cambio_de_tema(historial, pregunta_actual):
    if not historial:
        return False
    pregunta_anterior = ""
    for mensaje in reversed(historial):
        if mensaje["role"] == "user":
            pregunta_anterior = mensaje["content"]
            break
    if not pregunta_anterior:
        return False

    # --- NUEVA HEURÍSTICA: Si la pregunta es muy corta o solo contiene palabras genéricas, NO es cambio de tema ---
    palabras_actual = set(pregunta_actual.lower().split())
    if len(palabras_actual) < 5 or palabras_actual.issubset(PRONOMBRES_SEGUIMIENTO):
        return False

    # --- HEURÍSTICA RÁPIDA ---
    set_anterior = set(pregunta_anterior.lower().split())
    interseccion = palabras_actual & set_anterior
    if len(interseccion) / max(1, len(palabras_actual | set_anterior)) < 0.4:
        return True

    ratio = difflib.SequenceMatcher(None, pregunta_anterior, pregunta_actual).ratio()
    if ratio < 0.4:
        return True

    # Si la heurística no decide, llama a GPT (casos ambiguos)
    prompt = (
       # "Dadas dos preguntas de un usuario, responde solo 'sí' si la segunda pregunta trata sobre un tema diferente a la primera, "
      #  "o 'no' si ambas preguntas tratan sobre el mismo tema o son seguimiento. "
        f"Primera pregunta: {pregunta_anterior}\n"
        f"Segunda pregunta: {pregunta_actual}\n"
        "¿La segunda pregunta es de un tema diferente? (sí/no):"
    )
    mensajes = [
        {"role": "system", "content": "Eres un detector de cambio de tema. Responde solo sí o no."},
        {"role": "user", "content": prompt}
    ]
    veredicto = chat_completion(mensajes).strip().lower()
    return veredicto.startswith("s")

def responder_asistente(pregunta: str, user_id: str) -> str:
    try:
        print(f"\n🔍 Pregunta recibida de {user_id}: {pregunta}")
        
        # Inicializar historial si es la primera vez del usuario
        if user_id not in HISTORIAL_CONVERSACION:
            HISTORIAL_CONVERSACION[user_id] = []

        historial = HISTORIAL_CONVERSACION[user_id]

        # Buscar nuevos fragmentos relacionados con la pregunta
        print("🔎 Buscando nuevos fragmentos...")
        fragmentos_relevantes = buscar_fragmentos(pregunta)

        if not fragmentos_relevantes:
            print("⚠️ No se encontraron fragmentos relevantes.")
            respuesta = "No se encontró información relevante en los documentos para responder tu pregunta."
            historial.append({"role": "user", "content": pregunta})
            historial.append({"role": "assistant", "content": respuesta})
            HISTORIAL_CONVERSACION[user_id] = historial[-MAX_MENSAJES_HISTORIAL:]
            return respuesta

        # Tomar los 6 mejores fragmentos
        fragmentos_relevantes = sorted(fragmentos_relevantes, key=lambda x: x.get("score", 0), reverse=True)[:6]

        # Construir el contexto de los fragmentos encontrados
        contexto = ""
        for f in fragmentos_relevantes:
            texto_fragmento = f.get("texto", "").strip()
            if texto_fragmento:
                document_id = f.get("document_id", "Documento desconocido")
                fragment_id = f.get("fragment_id", "Fragmento sin nombre")
                sheet_name = f.get("sheet_name", "")

                encabezado = f"[document_id: {document_id}] [fragment_id: {fragment_id}]"
                if sheet_name:
                    encabezado += f" [sheet_name: {sheet_name}]"

                contexto += encabezado + "\n" + texto_fragmento + "\n\n---\n\n"

        if not contexto.strip():
            print("⚠️ Fragmentos sin contenido útil.")
            respuesta = "Encontré documentos, pero no pude acceder al contenido."
            historial.append({"role": "user", "content": pregunta})
            historial.append({"role": "assistant", "content": respuesta})
            HISTORIAL_CONVERSACION[user_id] = historial[-MAX_MENSAJES_HISTORIAL:]
            return respuesta

        # Construir la lista de mensajes para GPT
        mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
        mensajes.append({"role": "user", "content": f"Contexto documental:\n{contexto}"})
        mensajes += historial[-MAX_MENSAJES_HISTORIAL:]
        mensajes.append({"role": "user", "content": pregunta})

        print("🤖 Enviando a GPT...")
        respuesta = chat_completion(mensajes)
        print("✅ Respuesta generada")

        # Guardar la pregunta y la respuesta en el historial
        historial.append({"role": "user", "content": pregunta})
        historial.append({"role": "assistant", "content": respuesta})
        HISTORIAL_CONVERSACION[user_id] = historial[-MAX_MENSAJES_HISTORIAL:]

        return respuesta

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return "Lo siento, ocurrió un error interno al procesar tu pregunta."

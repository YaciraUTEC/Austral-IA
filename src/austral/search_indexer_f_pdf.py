import os
import json
import faiss
import numpy as np
import re
from pathlib import Path
from austral.gpt_azure import embed_text
from austral.utils.index_config import get_faiss_index_type
import tiktoken
import sys


# Configuración base
BASE_DIR = Path(__file__).resolve().parents[2]

# Ahora usamos una función para obtener las rutas según la categoría
def get_paths_for_category(categoria):
    """Devuelve las rutas de archivos para una categoría específica"""
    return {
        "fragmentos": BASE_DIR / "output" / "extractos_json" / "pdf" / categoria,
        "enriquecido": BASE_DIR / "output" / f"fragmentos_enriquecido_{categoria}_pdf.json",
        "index": BASE_DIR / "output" / f"faiss_index_{categoria}_pdf.bin"
    }

MAX_TOKENS_PER_REQUEST = 8192  # Límite real del modelo
SAFE_TOKENS = 7000             # Margen seguro para fragmentación

def cargar_fragmentos(categoria):
    """Carga los fragmentos JSON de la categoría especificada"""
    fragmentos = []
    fragmentos_path = get_paths_for_category(categoria)["fragmentos"]
    
    if not os.path.exists(fragmentos_path):
        print(f"⚠️ No se encontró la carpeta {fragmentos_path}")
        return []
    
    for archivo in os.listdir(fragmentos_path):
        if archivo.endswith(".json"):
            with open(os.path.join(fragmentos_path, archivo), "r", encoding="utf-8") as f:
                try:
                    frag = json.load(f)
                    fragmentos.append(frag)
                except json.JSONDecodeError:
                    print(f"⚠️ Error al cargar {archivo}: formato JSON incorrecto")
    
    print(f"✅ Cargados {len(fragmentos)} fragmentos de la categoría '{categoria}'")
    return fragmentos

def calcular_tokens(texto):
    encoding = tiktoken.encoding_for_model("text-embedding-3-small") #ontiene el esquema de codificación
    return len(encoding.encode(texto)) #convierte el texto en ese esquema y luego cuenta tokens

def split_text_safe(texto, max_tokens=SAFE_TOKENS):
    palabras = texto.split()
    subfrags = []
    fragmento_actual = []

    for palabra in palabras:
        fragmento_actual.append(palabra)
        texto_actual = " ".join(fragmento_actual)
        if calcular_tokens(texto_actual) > max_tokens:
            subfrags.append(" ".join(fragmento_actual[:-1]))
            fragmento_actual = [palabra]

    # Agregar el último fragmento
    if fragmento_actual:
        subfrags.append(" ".join(fragmento_actual))

    return subfrags

def ordenar_fragmentos_enriquecidos(fragmentos):
    """
    Ordena los fragmentos enriquecidos por document_id, número de página y parte.
    """
    def obtener_orden_fragmento(frag):
        document_id = frag["document_id"]
        fragment_id = frag["fragment_id"]

        # Extraer número de página y parte del fragment_id
        match_pagina = re.search(r"_p(\d+)", fragment_id)
        match_parte = re.search(r"_part(\d+)$", fragment_id)

        pagina = int(match_pagina.group(1)) if match_pagina else 0
        parte = int(match_parte.group(1)) if match_parte else 0

        return (document_id, pagina, parte)

    fragmentos.sort(key=obtener_orden_fragmento)
    return fragmentos

def procesar_y_indexar(fragmentos, categoria):
    enriquecidos = []

    for frag in fragmentos:
        nombre_archivo = frag.get("archivo", "")
        document_id = nombre_archivo.split("_p")[0].strip()
        fragment_id = nombre_archivo.replace(".pdf", "")
        paginas = frag.get("paginas", [])

        textos_paginas = []
        for p in paginas:
            if "texto" in p:
                texto = p.get("texto", "").strip()
                texto = texto.replace("/\n", " ").replace("\r\n", " ").replace("\n", " ").replace("\\n", " ")
                texto = re.sub(r' {2,}', ' ', texto)
                texto = texto.replace('\u0000', '')
                textos_paginas.append(texto)

        texto_completo = " ".join(textos_paginas)

        # Dividir el texto en fragmentos seguros
        subfragmentos = split_text_safe(texto_completo, max_tokens=SAFE_TOKENS)
        for idx, subfrag in enumerate(subfragmentos):
            enriquecidos.append({
                "fragment_id": f"{fragment_id}_part{idx+1}" if len(subfragmentos) > 1 else fragment_id,
                "document_id": document_id,
                "texto": subfrag
            })

    # Validar tamaño de los fragmentos antes de generar embeddings
    for i, frag in enumerate(enriquecidos):
        estimated_tokens = calcular_tokens(frag["texto"])
        if estimated_tokens > MAX_TOKENS_PER_REQUEST:
            print(f"⚠️ Fragmento {i+1} supera el límite de tokens ({estimated_tokens} tokens).")
            raise ValueError(f"Fragmento demasiado largo: {estimated_tokens} tokens.")

    # Ordenar los fragmentos enriquecidos antes de generar embeddings
    enriquecidos = ordenar_fragmentos_enriquecidos(enriquecidos)    # Generar embeddings para cada subfragmento
    print(f"Generando embeddings para {len(enriquecidos)} subfragmentos...")
    embeddings = [embed_text(f["texto"]) for f in enriquecidos]

    # Añadir la categoría a todos los fragmentos enriquecidos
    for frag in enriquecidos:
        frag["categoria"] = categoria

    # Crear índice solo si hay embeddings
    if len(embeddings) > 0:
        embeddings_np = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_np)

        index = get_faiss_index_type(embeddings_np)
        index.add(embeddings_np)
        
        # Guardar índice y fragmentos enriquecidos
        paths = get_paths_for_category(categoria)
        faiss.write_index(index, str(paths["index"]))
        
        with open(paths["enriquecido"], "w", encoding="utf-8") as f:
            json.dump(enriquecidos, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Indexación completada para {len(enriquecidos)} subfragmentos PDF en categoría '{categoria}'.")
    else:
        print(f"⚠️ No hay fragmentos para indexar en la categoría '{categoria}'.")
    
    return len(enriquecidos)

def procesar_todas_categorias(categorias):
    """Procesa todas las categorías especificadas"""
    total_fragmentos = 0
    
    for categoria in categorias:
        print(f"\n🔍 Procesando categoría PDF: {categoria.upper()}")
        fragmentos = cargar_fragmentos(categoria)
        if fragmentos:
            total = procesar_y_indexar(fragmentos, categoria)
            total_fragmentos += total
    
    print(f"\n✅ Indexación global completada para {total_fragmentos} fragmentos PDF en {len(categorias)} categorías")

if __name__ == "__main__":
    # Permitir especificar categoría desde la línea de comandos
    categorias = ["mantenimiento", "proyectos"]  # Categorías por defecto
    
    if len(sys.argv) > 1:
        categoria_arg = sys.argv[1].lower()
        if categoria_arg in categorias:
            print(f"Procesando solo la categoría: {categoria_arg}")
            fragmentos = cargar_fragmentos(categoria_arg)
            procesar_y_indexar(fragmentos, categoria_arg)
        else:
            print(f"Categoría no reconocida: {categoria_arg}")
            print(f"Categorías disponibles: {', '.join(categorias)}")
    else:
        # Procesar todas las categorías
        procesar_todas_categorias(categorias)
import os
import json
import time
import re
from austral.sharepoint_conector import obtener_archivos_sharepoint
from austral.extractor.fragmenter_dispatcher import fragmentar_documento_memoria
from austral.extractor.parser import extraer_texto_a_json
from austral.extractor.parser_excel import guardar_fragmentos_excel

OUTPUT_FOLDER = "output"
FRAGMENTS_FOLDER = os.path.join(OUTPUT_FOLDER, "fragmentos")

# Ahora estas serán rutas base y se completarán con la categoría
EXTRACTED_JSON_BASE_PDF = os.path.join(OUTPUT_FOLDER, "extractos_json", "pdf")
EXTRACTED_JSON_BASE_EXCEL = os.path.join(OUTPUT_FOLDER, "extractos_json", "excel")

# La metadata y registros también se separan por categoría
METADATA_BASE_PATH = os.path.join(FRAGMENTS_FOLDER, "fragmentos_metadata_{}.json")
REGISTRO_BASE_PATH = os.path.join(OUTPUT_FOLDER, "procesados_{}.json")

# Categorías disponibles
CATEGORIAS = ["mantenimiento", "proyectos"]

# Crear directorios base
os.makedirs(FRAGMENTS_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_JSON_BASE_PDF, exist_ok=True)
os.makedirs(EXTRACTED_JSON_BASE_EXCEL, exist_ok=True)

# Crear directorios para cada categoría
for categoria in CATEGORIAS:
    os.makedirs(os.path.join(EXTRACTED_JSON_BASE_PDF, categoria), exist_ok=True)
    os.makedirs(os.path.join(EXTRACTED_JSON_BASE_EXCEL, categoria), exist_ok=True)

def cargar_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def filtrar_contenido_metadato(frag: dict) -> dict:
    campos_permitidos = ["document_id", "fragment_id", "fragment_path", "page_range", "sheet_name", "status"]
    return {k: v for k, v in frag.items() if k in campos_permitidos}

def eliminar_fragmentos_y_jsons(nombre_base):
    for carpeta in [FRAGMENTS_FOLDER, EXTRACTED_JSON_BASE_PDF, EXTRACTED_JSON_BASE_EXCEL]:
        for archivo in os.listdir(carpeta):
            if archivo.startswith(nombre_base):
                os.remove(os.path.join(carpeta, archivo))



def obtener_rutas_categoria(categoria):
    """
    Devuelve las rutas específicas para una categoría
    """
    return {
        "pdf": os.path.join(EXTRACTED_JSON_BASE_PDF, categoria),
        "excel": os.path.join(EXTRACTED_JSON_BASE_EXCEL, categoria),
        "metadata": METADATA_BASE_PATH.format(categoria),
        "registro": REGISTRO_BASE_PATH.format(categoria)
    }

def procesar_categoria(categoria):
    """
    Procesa todos los documentos de una categoría específica
    """
    inicio_categoria = time.perf_counter()
    print(f"\n🔍 Procesando categoría: {categoria.upper()}")
    
    # Obtener rutas específicas para esta categoría
    rutas = obtener_rutas_categoria(categoria)
    
    # Cargar registros y metadatos de esta categoría
    registro_procesados = cargar_json(rutas["registro"])
    metadatos = cargar_json(rutas["metadata"])
    metadatos_actualizados = []
    
    # Obtener archivos solo de esta categoría
    archivos = obtener_archivos_sharepoint(categoria)
    
    ids_actuales = set()
    
    for archivo in archivos:
        nombre = archivo["filename"]
        contenido = archivo["content"]
        item_id = archivo["id"]
        ultima_fecha = archivo["lastModifiedDateTime"]
        ids_actuales.add(item_id)

        if item_id in registro_procesados and registro_procesados[item_id]["lastModified"] == ultima_fecha:
            print(f"⏩ Saltando {nombre} (sin cambios)")
            continue

        print(f"📂 Procesando {nombre}")
        try:
            fragmentos = fragmentar_documento_memoria(nombre, contenido, output_dir=FRAGMENTS_FOLDER)

            if nombre.lower().endswith(".pdf"):
                for frag in fragmentos:
                    fragment_path = frag["fragment_path"]
                    with open(fragment_path, "rb") as f:
                        fragment_bytes = f.read()

                    output_path = os.path.join(rutas["pdf"], f"{frag['fragment_id']}.json")
                    extraer_texto_a_json(frag["fragment_id"], fragment_bytes, output_path=output_path)

                    # Añadir la categoría a los metadatos
                    frag_data = filtrar_contenido_metadato(frag)
                    frag_data["categoria"] = categoria
                    metadatos_actualizados.append(frag_data)

            elif nombre.lower().endswith((".xlsx", ".xls")):
                guardar_fragmentos_excel(fragmentos, rutas["excel"])
                for frag in fragmentos:
                    frag_data = filtrar_contenido_metadato(frag)
                    frag_data["categoria"] = categoria
                    metadatos_actualizados.append(frag_data)

            registro_procesados[item_id] = {
                "filename": nombre,
                "lastModified": ultima_fecha,
                "procesado": True,
                "categoria": categoria
            }

        except Exception as e:
            print(f"❌ Error al procesar {nombre}: {e}")

    # Eliminar archivos de documentos eliminados en SharePoint
    ids_guardados = set(registro_procesados.keys())
    ids_eliminados = ids_guardados - ids_actuales
    for id_eliminado in ids_eliminados:
        print(f"🗑️ Eliminando archivos de {registro_procesados[id_eliminado]['filename']}")
        nombre_base = os.path.splitext(registro_procesados[id_eliminado]["filename"])[0]
        eliminar_fragmentos_y_jsons(nombre_base)
        del registro_procesados[id_eliminado]

    # Guardar registros y metadatos actualizados
    guardar_json(registro_procesados, rutas["registro"])
    guardar_json(metadatos_actualizados, rutas["metadata"])
    
    fin_categoria = time.perf_counter()
    print(f"✅ Tiempo procesando {categoria}: {fin_categoria - inicio_categoria:.2f} segundos")

def run():
    inicio = time.perf_counter()
    
    # Procesar cada categoría por separado
    for categoria in CATEGORIAS:
        procesar_categoria(categoria.lower())
    
    ids_actuales = set()    # Este bloque ahora está incluido en procesar_categoria()
    # y hemos eliminado el código redundante

    fin = time.perf_counter()
    print(f"✅ Tiempo total para todas las categorías: {fin - inicio:.2f} segundos")

    fin = time.perf_counter()
    print(f"✅ Tiempo total: {fin - inicio:.2f} segundos")

if __name__ == "__main__":
    run()
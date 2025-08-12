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
EXTRACTED_JSON_FOLDER_PDF = os.path.join(OUTPUT_FOLDER, "extractos_json", "pdf")
EXTRACTED_JSON_FOLDER_EXCEL = os.path.join(OUTPUT_FOLDER, "extractos_json", "excel")
METADATA_PATH = os.path.join(FRAGMENTS_FOLDER, "fragmentos_metadata.json")
REGISTRO_PROCESADOS_PATH = os.path.join(OUTPUT_FOLDER, "procesados.json")

os.makedirs(FRAGMENTS_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_JSON_FOLDER_PDF, exist_ok=True)
os.makedirs(EXTRACTED_JSON_FOLDER_EXCEL, exist_ok=True)

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
    for carpeta in [FRAGMENTS_FOLDER, EXTRACTED_JSON_FOLDER_PDF, EXTRACTED_JSON_FOLDER_EXCEL]:
        for archivo in os.listdir(carpeta):
            if archivo.startswith(nombre_base):
                os.remove(os.path.join(carpeta, archivo))



def run():
    inicio = time.perf_counter()
    archivos = obtener_archivos_sharepoint()

    registro_procesados = cargar_json(REGISTRO_PROCESADOS_PATH)
    metadatos = cargar_json(METADATA_PATH)
    metadatos_actualizados = []

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

                    output_path = os.path.join(EXTRACTED_JSON_FOLDER_PDF, f"{frag['fragment_id']}.json")
                    extraer_texto_a_json(frag["fragment_id"], fragment_bytes, output_path=output_path)

                    metadatos_actualizados.append(filtrar_contenido_metadato(frag))

            elif nombre.lower().endswith((".xlsx", ".xls")):
                guardar_fragmentos_excel(fragmentos, EXTRACTED_JSON_FOLDER_EXCEL)
                for frag in fragmentos:
                    metadatos_actualizados.append(filtrar_contenido_metadato(frag))

            registro_procesados[item_id] = {
                "filename": nombre,
                "lastModified": ultima_fecha,
                "procesado": True
            }

        except Exception as e:
            print(f"❌ Error al procesar {nombre}: {e}")

    # 🔁 Eliminar archivos locales de documentos eliminados de SharePoint
    ids_guardados = set(registro_procesados.keys())
    ids_eliminados = ids_guardados - ids_actuales
    for id_eliminado in ids_eliminados:
        print(f"🗑️ Eliminando archivos de {registro_procesados[id_eliminado]['filename']}")
        nombre_base = os.path.splitext(registro_procesados[id_eliminado]["filename"])[0]
        eliminar_fragmentos_y_jsons(nombre_base)
        del registro_procesados[id_eliminado]

    guardar_json(registro_procesados, REGISTRO_PROCESADOS_PATH)
    
    guardar_json(metadatos_actualizados, METADATA_PATH)

    fin = time.perf_counter()
    print(f"✅ Tiempo total: {fin - inicio:.2f} segundos")

if __name__ == "__main__":
    run()
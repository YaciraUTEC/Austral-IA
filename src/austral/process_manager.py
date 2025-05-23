import os
import json
from itertools import islice
from austral.extractor.fragmenter import fragmentar_pdf
from austral.extractor.parser import extraer_texto_a_json
from austral.utils.file_ops import json_ya_existe

PDF_FOLDER = "Doc"
OUTPUT_FOLDER = "output"
FRAGMENTS_FOLDER = os.path.join(OUTPUT_FOLDER, "fragmentos")
EXTRACTED_JSON_FOLDER = os.path.join(OUTPUT_FOLDER, "extractos_json")
METADATA_PATH = os.path.join(FRAGMENTS_FOLDER, "fragmentos_metadata.json")

os.makedirs(FRAGMENTS_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_JSON_FOLDER, exist_ok=True)

def procesar_lotes(iterable, tamano_lote=10):
    it = iter(iterable)
    while True:
        lote = list(islice(it, tamano_lote))
        if not lote:
            break
        yield lote

def guardar_metadatos(metadatos: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadatos, f, indent=2, ensure_ascii=False)

def cargar_metadatos(path: str) -> list:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def run():
    pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("No se encontraron archivos PDF en la carpeta 'Doc'.")
        return

    # Carga metadatos previos
    todos_los_metadatos = cargar_metadatos(METADATA_PATH)
    fragment_ids_existentes = set(frag["fragment_id"] for frag in todos_los_metadatos)

    for lote_pdfs in procesar_lotes(pdfs, tamano_lote=10):
        print(f"Procesando lote de {len(lote_pdfs)} PDFs")
        for pdf in lote_pdfs:
            input_path = os.path.join(PDF_FOLDER, pdf)
            print(f"Procesando: {pdf}")
            fragmentos = fragmentar_pdf(input_path, FRAGMENTS_FOLDER)

            for frag in fragmentos:
                fragment_id = frag["fragment_id"]
                output_path = os.path.join(EXTRACTED_JSON_FOLDER, f"{fragment_id}.json")
                if json_ya_existe(output_path):
                    print(f"Saltando {fragment_id} (JSON ya existe)")
                    continue
                extraer_texto_a_json(frag["fragment_path"], output_path)
                if fragment_id not in fragment_ids_existentes:
                    todos_los_metadatos.append(frag)
                    fragment_ids_existentes.add(fragment_id)

    # Guardar todos los metadatos (previos + nuevos)
    guardar_metadatos(todos_los_metadatos, METADATA_PATH)

    print("Todos los PDFs fueron fragmentados y procesados correctamente.")

import os
import json
import time
from itertools import islice
from austral.extractor.fragmenter import fragmentar_pdf
from austral.extractor.parser import extraer_texto_a_json
from austral.utils.file_ops import json_ya_existe
from austral.utils.convert_w import convertir_docx_a_pdf_libreoffice

PDF_FOLDER = "Doc"             # PDFs originales
WORD_FOLDER = "Word"           # Word fuera de Doc
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
    inicio_total = time.perf_counter()

    pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    docx = [f for f in os.listdir(WORD_FOLDER) if f.lower().endswith(".docx")]

    print(f"Archivos DOCX encontrados: {docx}")
    print(f"Archivos PDF encontrados: {pdfs}")

    inicio_conversion = time.perf_counter()
    # Convertir DOCX a PDF
    for docx_file in docx:
        ruta_docx = os.path.join(WORD_FOLDER, docx_file)
        nombre_pdf = os.path.splitext(docx_file)[0] + ".pdf"
        ruta_pdf_convertido = os.path.join(PDF_FOLDER, nombre_pdf)
        if not os.path.exists(ruta_pdf_convertido):
            print(f"Convirtiendo {docx_file} a PDF {nombre_pdf} en {PDF_FOLDER}...")
            convertir_docx_a_pdf_libreoffice(ruta_docx, PDF_FOLDER)
    fin_conversion = time.perf_counter()
    print(f"Duración conversión DOCX a PDF: {fin_conversion - inicio_conversion:.2f} segundos")

    pdfs_a_procesar = pdfs + [
        f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")
    ]

    todos_los_metadatos = cargar_metadatos(METADATA_PATH)
    fragment_ids_existentes = set(frag["fragment_id"] for frag in todos_los_metadatos)

    inicio_procesamiento = time.perf_counter()
    for lote_pdfs in procesar_lotes(pdfs_a_procesar, tamano_lote=10):
        print(f"Procesando lote de {len(lote_pdfs)} PDFs")
        for pdf in lote_pdfs:
            input_path = os.path.join(PDF_FOLDER, pdf)
            print(f"Procesando: {pdf}")
            inicio_fragmentacion = time.perf_counter()
            fragmentos = fragmentar_pdf(input_path, FRAGMENTS_FOLDER)
            fin_fragmentacion = time.perf_counter()
            print(f"Fragmentación de {pdf} duró {fin_fragmentacion - inicio_fragmentacion:.2f} segundos")

            for frag in fragmentos:
                fragment_id = frag["fragment_id"]
                output_path = os.path.join(EXTRACTED_JSON_FOLDER, f"{fragment_id}.json")
                if json_ya_existe(output_path):
                    print(f"Saltando {fragment_id} (JSON ya existe)")
                    continue

                inicio_extraccion = time.perf_counter()
                extraer_texto_a_json(frag["fragment_path"], output_path)
                fin_extraccion = time.perf_counter()
                print(f"Extracción de {fragment_id} duró {fin_extraccion - inicio_extraccion:.2f} segundos")

                if fragment_id not in fragment_ids_existentes:
                    todos_los_metadatos.append(frag)
                    fragment_ids_existentes.add(fragment_id)

    fin_procesamiento = time.perf_counter()
    print(f"Duración total procesamiento PDFs: {fin_procesamiento - inicio_procesamiento:.2f} segundos")

    guardar_metadatos(todos_los_metadatos, METADATA_PATH)

    fin_total = time.perf_counter()
    print(f"Tiempo total ejecución completa: {fin_total - inicio_total:.2f} segundos")
    print("Todos los documentos fueron fragmentados y procesados correctamente.")

if __name__ == "__main__":
    run()
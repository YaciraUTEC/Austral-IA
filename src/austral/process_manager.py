import os
import json
import time
from itertools import islice
from austral.extractor.fragmenter_dispatcher import fragmentar_documento
from austral.extractor.parser import extraer_texto_a_json
from austral.extractor.parser_excel import guardar_fragmentos_excel
from austral.utils.file_ops import json_ya_existe
from austral.utils.convert_w import convertir_docx_a_pdf_libreoffice

PDF_FOLDER = "Doc"
WORD_FOLDER = "Word"
EXCEL_FOLDER = "Excel"
OUTPUT_FOLDER = "output"

FRAGMENTS_FOLDER = os.path.join(OUTPUT_FOLDER, "fragmentos")
EXTRACTED_JSON_FOLDER_PDF = os.path.join(OUTPUT_FOLDER, "extractos_json", "pdf")
EXTRACTED_JSON_FOLDER_EXCEL = os.path.join(OUTPUT_FOLDER, "extractos_json", "excel")
METADATA_PATH = os.path.join(FRAGMENTS_FOLDER, "fragmentos_metadata.json")

# Crear carpetas necesarias
os.makedirs(FRAGMENTS_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_JSON_FOLDER_PDF, exist_ok=True)
os.makedirs(EXTRACTED_JSON_FOLDER_EXCEL, exist_ok=True)

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

def filtrar_contenido_metadato(frag: dict) -> dict:
    """Devuelve solo los campos necesarios para metadatos, sin 'contenido'."""
    campos_permitidos = ["document_id", "fragment_id", "fragment_path", "page_range", "sheet_name", "status"]
    return {k: v for k, v in frag.items() if k in campos_permitidos}

def run():
    inicio_total = time.perf_counter()

    pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    docx = [f for f in os.listdir(WORD_FOLDER) if f.lower().endswith(".docx")]
    excels = [f for f in os.listdir(EXCEL_FOLDER) if f.lower().endswith((".xlsx", ".xls"))]

    print(f"Archivos DOCX encontrados: {docx}")
    print(f"Archivos PDF encontrados: {pdfs}")
    print(f"Archivos Excel encontrados: {excels}")

    # Convertir DOCX a PDF
    for docx_file in docx:
        ruta_docx = os.path.join(WORD_FOLDER, docx_file)
        nombre_pdf = os.path.splitext(docx_file)[0] + ".pdf"
        ruta_pdf_convertido = os.path.join(PDF_FOLDER, nombre_pdf)
        if not os.path.exists(ruta_pdf_convertido):
            print(f"Convirtiendo {docx_file} a PDF {nombre_pdf}...")
            convertir_docx_a_pdf_libreoffice(ruta_docx, PDF_FOLDER)

    todos_los_metadatos = cargar_metadatos(METADATA_PATH)
    fragment_ids_existentes = set(frag["fragment_id"] for frag in todos_los_metadatos)

    # Procesar PDF
    for lote_pdfs in procesar_lotes(os.listdir(PDF_FOLDER), tamano_lote=10):
        for pdf_file in lote_pdfs:
            if not pdf_file.lower().endswith(".pdf"):
                continue
            input_path = os.path.join(PDF_FOLDER, pdf_file)
            print(f"📄 Procesando PDF: {pdf_file}")
            fragmentos = fragmentar_documento(input_path, FRAGMENTS_FOLDER)
            for frag in fragmentos:
                output_path = os.path.join(EXTRACTED_JSON_FOLDER_PDF, f"{frag['fragment_id']}.json")
                if json_ya_existe(output_path):
                    print(f"⏩ Saltando {frag['fragment_id']} (ya existe)")
                    continue
                extraer_texto_a_json(frag["fragment_path"], output_path)
                if frag["fragment_id"] not in fragment_ids_existentes:
                    metadato = filtrar_contenido_metadato(frag)
                    todos_los_metadatos.append(metadato)
                    fragment_ids_existentes.add(frag["fragment_id"])

    # Procesar Excel
    for excel_file in excels:
        input_path = os.path.join(EXCEL_FOLDER, excel_file)
        print(f"📊 Procesando Excel: {excel_file}")

    # ← este es el dict completo
        fragmentos = fragmentar_documento(input_path, FRAGMENTS_FOLDER)
        guardar_fragmentos_excel(fragmentos, EXTRACTED_JSON_FOLDER_EXCEL)


        for frag in fragmentos:
            if frag["fragment_id"] not in fragment_ids_existentes:
                metadato = filtrar_contenido_metadato(frag)
                todos_los_metadatos.append(metadato)
                fragment_ids_existentes.add(frag["fragment_id"])

    guardar_metadatos(todos_los_metadatos, METADATA_PATH)
    fin_total = time.perf_counter()
    print(f"✅ Tiempo total ejecución completa: {fin_total - inicio_total:.2f} segundos")

if __name__ == "__main__":
    run()

import os
from austral.extractor.parser import extraer_texto_a_json
from austral.utils.file_ops import json_ya_existe

PDF_FOLDER = "Doc"
OUTPUT_FOLDER = "output"

if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    if not pdfs:
        print("No se encontraron archivos PDF en la carpeta 'Doc'.")
        exit()

    for pdf in pdfs:
        input_path = os.path.join(PDF_FOLDER, pdf)
        output_path = os.path.join(OUTPUT_FOLDER, pdf.replace(".pdf", ".json"))

        if json_ya_existe(output_path):
            print(f"Saltando {pdf} (JSON ya existe)")
            continue

        print(f"Procesando: {pdf}")
        extraer_texto_a_json(input_path, output_path)

    print("Todos los PDFs fueron procesados correctamente.")

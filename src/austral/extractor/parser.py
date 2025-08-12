import os
import json
from io import BytesIO
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_FORMRECOGNIZER_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_FORMRECOGNIZER_KEY")

client = DocumentAnalysisClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

def extraer_texto_a_json(nombre_archivo: str, contenido_bytes: bytes, output_path: str = None) -> dict:
    """
    Extrae texto y tablas desde un fragmento PDF en memoria y lo convierte a estructura JSON.
    Si se indica 'output_path', guarda el resultado como archivo .json.
    """
    archivo_stream = BytesIO(contenido_bytes)
    poller = client.begin_analyze_document("prebuilt-document", document=archivo_stream)
    result = poller.result()

    data = {
        "archivo": nombre_archivo,
        "paginas": []
    }

    for page in result.pages:
        texto = "\n".join([line.content for line in page.lines])
        pagina = {
            "numero_pagina": page.page_number,
            "texto": texto,
            "tablas": []
        }
        for table in result.tables:
            if table.bounding_regions and any(region.page_number == page.page_number for region in table.bounding_regions):
                filas = []
                max_row = max(cell.row_index for cell in table.cells)
                for row_idx in range(max_row + 1):
                    fila = [cell.content for cell in table.cells if cell.row_index == row_idx]
                    filas.append(fila)
                pagina["tablas"].append(filas)
        data["paginas"].append(pagina)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Guardado JSON: {output_path}")

    return data

import os
import json
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

def extraer_texto_a_json(pdf_path: str, output_path: str):
    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result()

    data = {
        "archivo": os.path.basename(pdf_path),
        "paginas": []
    }

    for page in result.pages:
        texto = "\n".join([line.content for line in page.lines])
        pagina = {
            "numero_pagina": page.page_number,
            "texto": texto,
            "tablas": []
        }
        # Extraer tablas si existen
        for table in result.tables:
            # Solo tablas que pertenezcan a esta página
            if table.bounding_regions and any(region.page_number == page.page_number for region in table.bounding_regions):
                filas = []
                # table.cells está en orden secuencial, hay que reconstruir filas por row_index
                max_row = max(cell.row_index for cell in table.cells)
                for row_idx in range(max_row + 1):
                    fila = [cell.content for cell in table.cells if cell.row_index == row_idx]
                    filas.append(fila)
                pagina["tablas"].append(filas)

        data["paginas"].append(pagina)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

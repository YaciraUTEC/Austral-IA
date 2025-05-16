import os, json
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

        for table in result.tables:
            if table.bounding_regions and table.bounding_regions[0].page_number == page.page_number:
                filas = []
                for i in range(table.row_count):
                    fila = []
                    for j in range(table.column_count):
                        celda = next((c for c in table.cells if c.row_index == i and c.column_index == j), None)
                        fila.append(celda.content if celda else "")
                    filas.append(fila)
                pagina["tablas"].append(filas)

        data["paginas"].append(pagina)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"JSON generado: {output_path}")

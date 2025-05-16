
import os
import json
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import comtypes.client  # Asegúrate de que Word esté instalado

# Cargar variables de entorno
load_dotenv()
AZURE_ENDPOINT = os.getenv("AZURE_FORMRECOGNIZER_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_FORMRECOGNIZER_KEY")

# Crear cliente
client = DocumentAnalysisClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

# Función: convertir Word a PDF
def convertir_docx_a_pdf(input_path: str, output_path: str):
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(input_path)
    doc.SaveAs(output_path, FileFormat=17)  # 17 = wdFormatPDF
    doc.Close()
    word.Quit()

# Función: analizar PDF con Form Recognizer
def extraer_texto_a_json(pdf_path: str, output_dir: str):
    nombre_pdf = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"{nombre_pdf}.json")

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result()

    print(f"✅ Total de páginas detectadas en '{nombre_pdf}': {len(result.pages)}")

    data = {
        "archivo": os.path.basename(pdf_path),
        "paginas": []
    }

    for page in result.pages:
        print(f"   → Procesando página {page.page_number}...")
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

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON generado: {output_path}\n")

# Función principal: detecta PDF y DOCX
def procesar_todos_los_documentos():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    doc_dir = os.path.join(base_dir, "Doc")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    temp_pdf_dir = os.path.join(os.path.dirname(__file__), "temp_pdf")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_pdf_dir, exist_ok=True)

    archivos = [archivo for archivo in os.listdir(doc_dir) if archivo.lower().endswith((".pdf", ".docx"))]

    if not archivos:
        print("⚠️ No se encontraron archivos PDF o Word en la carpeta 'Doc'.")
        return

    print(f"🔍 Encontrados {len(archivos)} archivos. Iniciando procesamiento...\n")

    for archivo in archivos:
        ruta_doc = os.path.join(doc_dir, archivo)

        if archivo.lower().endswith(".docx"):
            nombre_base = os.path.splitext(archivo)[0]
            ruta_pdf_convertido = os.path.join(temp_pdf_dir, f"{nombre_base}.pdf")
            print(f"📄 Convirtiendo Word a PDF: {archivo}")
            convertir_docx_a_pdf(ruta_doc, ruta_pdf_convertido)
            ruta_a_procesar = ruta_pdf_convertido
        else:
            ruta_a_procesar = ruta_doc

        extraer_texto_a_json(ruta_a_procesar, output_dir)

    print("🚀 Procesamiento de todos los documentos completado.")

if __name__ == "__main__":
    procesar_todos_los_documentos()

# src/austral/api.py

#from fastapi import FastAPI
#from austral.routers import asistente

#app = FastAPI()

#app.include_router(asistente.router, prefix="/api")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from austral.routers.asistente import router

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
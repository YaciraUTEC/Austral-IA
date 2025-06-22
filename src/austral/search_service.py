import faiss
import json
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from austral.gpt_azure import embed_text

# Configuración de FAISS
faiss.omp_set_num_threads(4)  # Ajusta según tu CPU

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
INDEX_PDF_PATH = BASE_DIR / "output" / "faiss_index_pdf.bin"
INDEX_EXCEL_PATH = BASE_DIR / "output" / "faiss_index_excel.bin"
FRAGMENTOS_PDF_PATH = BASE_DIR / "output" / "fragmentos_enriquecido_pdf.json"
FRAGMENTOS_EXCEL_PATH = BASE_DIR / "output" / "fragmentos_enriquecido_excel.json"

# Cargar índices
index_pdf = faiss.read_index(str(INDEX_PDF_PATH))
index_excel = faiss.read_index(str(INDEX_EXCEL_PATH))

# Cargar fragmentos
with open(FRAGMENTOS_PDF_PATH, "r", encoding="utf-8") as f:
    fragmentos_pdf = json.load(f)

with open(FRAGMENTOS_EXCEL_PATH, "r", encoding="utf-8") as f:
    fragmentos_excel = json.load(f)

# Configurar búsqueda para índice IVF si aplica
if isinstance(index_pdf, faiss.IndexIVFFlat):
    if not index_pdf.is_trained:
        raise RuntimeError("❌ El índice IVF de PDF no ha sido entrenado.")
    index_pdf.nprobe = 30

if isinstance(index_excel, faiss.IndexIVFFlat):
    if not index_excel.is_trained:
        raise RuntimeError("❌ El índice IVF de Excel no ha sido entrenado.")
    index_excel.nprobe = 30

def detectar_hoja_en_pregunta(pregunta: str, hojas_disponibles: list) -> str | None:
    pregunta_lower = pregunta.lower()
    for hoja in hojas_disponibles:
        if hoja.lower() in pregunta_lower:
            return hoja
    return None

# Funciones separadas para búsqueda
def buscar_en_pdf(embedding_np, top_k):
    D_pdf, I_pdf = index_pdf.search(embedding_np, top_k)
    resultados_pdf = []
    for rank, idx in enumerate(I_pdf[0]):
        if 0 <= idx < len(fragmentos_pdf):
            frag = fragmentos_pdf[idx].copy()
            frag["score"] = float(D_pdf[0][rank])
            frag["tipo"] = "PDF"
            resultados_pdf.append(frag)
    return resultados_pdf

def buscar_en_excel(embedding_np, top_k, hoja_mencionada):
    D_excel, I_excel = index_excel.search(embedding_np, top_k)
    resultados_excel = []
    for rank, idx in enumerate(I_excel[0]):
        if 0 <= idx < len(fragmentos_excel):
            frag = fragmentos_excel[idx].copy()
            frag["score"] = float(D_excel[0][rank])
            frag["tipo"] = "EXCEL"
            if hoja_mencionada:
                if frag.get("sheet_name", "").lower() != hoja_mencionada.lower():
                    continue
            resultados_excel.append(frag)
    return resultados_excel

# Búsqueda principal
def buscar_fragmentos(query: str, top_k: int = 12) -> list:
    embedding = embed_text(query)
    embedding_np = np.array([embedding], dtype=np.float32)
    faiss.normalize_L2(embedding_np)

    hojas_disponibles = list({frag.get("sheet_name", "") for frag in fragmentos_excel if "sheet_name" in frag})
    hoja_mencionada = detectar_hoja_en_pregunta(query, hojas_disponibles)

    with ThreadPoolExecutor() as executor:
        futuro_pdf = executor.submit(buscar_en_pdf, embedding_np, top_k)
        futuro_excel = executor.submit(buscar_en_excel, embedding_np, top_k, hoja_mencionada)

        resultados_pdf = futuro_pdf.result()
        resultados_excel = futuro_excel.result()

    return resultados_pdf + resultados_excel

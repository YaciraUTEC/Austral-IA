# src/austral/search_service.py
import faiss
import json
import numpy as np
from pathlib import Path
from austral.gpt_azure import embed_text

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
INDEX_PATH = BASE_DIR / "output" / "faiss_index.bin"
FRAGMENTOS_PATH = BASE_DIR / "output" / "fragmentos_enriquecido.json"


index = faiss.read_index(str(INDEX_PATH))
with open(FRAGMENTOS_PATH, "r", encoding="utf-8") as f:
    fragmentos = json.load(f)

# Detectar si el índice es IVF (IndexIVFFlat)
usa_ivf = isinstance(index, faiss.IndexIVFFlat)
if usa_ivf and not index.is_trained:
    raise RuntimeError("❌ El índice IVF no ha sido entrenado.")

# Para IVF, activamos modo búsqueda
if usa_ivf:
    index.nprobe = 15  # nprobe controla cuántos clusters se exploran (puedes ajustar)

def buscar_fragmentos(query: str, top_k: int = 5) -> list:
    embedding = embed_text(query)
    embedding_np = np.array([embedding], dtype=np.float32)

    # Normalizar si usamos producto interno (similitud coseno)
    faiss.normalize_L2(embedding_np)

    # Buscar en el índice
    D, I = index.search(embedding_np, top_k)

    resultados = []
    for rank, idx in enumerate(I[0]):
        if 0 <= idx < len(fragmentos):
            frag = fragmentos[idx].copy()
            frag["score"] = float(D[0][rank])  # Producto interno ya refleja similitud
            resultados.append(frag)

    return resultados

import faiss
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
INDEX_PATH = BASE_DIR / "output" / "faiss_index.bin"
FRAGMENTOS_PATH = BASE_DIR / "output" / "fragmentos_enriquecido.json"

# Modelo y FAISS
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(str(INDEX_PATH))

# Fragmentos cargados una sola vez en memoria
with open(FRAGMENTOS_PATH, "r", encoding="utf-8") as f:
    fragmentos = json.load(f)

def buscar_fragmentos(query: str, top_k: int = 5):
    vector = model.encode([query], normalize_embeddings=True)
    D, I = index.search(np.array(vector, dtype=np.float32), top_k)

    resultados = []
    for rank, idx in enumerate(I[0]):
        if 0 <= idx < len(fragmentos):
            frag = fragmentos[idx].copy()
            frag["score"] = float(D[0][rank])  # ya está normalizado, por lo tanto esto es el coseno
            resultados.append(frag)

    return resultados

import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "output/faiss_index.bin"
FRAGMENTOS_PATH = "output/fragmentos_enriquecido.json"

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(INDEX_PATH)

with open(FRAGMENTOS_PATH, "r", encoding="utf-8") as f:
    fragmentos = json.load(f)

def buscar_fragmentos(query: str, top_k: int = 5):
    vector = model.encode([query])
    distancias, indices = index.search(np.array(vector), top_k)

    resultados = []
    for rank, i in enumerate(indices[0]):
        fragmento = fragmentos[i].copy()  # evita modificar el original
        fragmento["score"] = float(1 - distancias[0][rank])  # más alto = más similar
        resultados.append(fragmento)

    return resultados


import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parents[2]
EXTRACTOS_PATH = BASE_DIR / "output" / "extractos_json"
OUTPUT_INDEX = BASE_DIR / "output" / "faiss_index.bin"
OUTPUT_FRAGMENTOS = BASE_DIR / "output" / "fragmentos_enriquecido.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# Cargar el modelo
model = SentenceTransformer(MODEL_NAME)

def construir_fragmentos_enriquecidos():
    fragmentos = []
    for filename in os.listdir(EXTRACTOS_PATH):
        if not filename.endswith(".json"):
            continue

        filepath = EXTRACTOS_PATH / filename
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        texto_completo = " ".join(p.get("texto", "") for p in data.get("paginas", []))
        fragmentos.append({
            "fragment_id": filename.replace(".json", ""),
            "document_id": data.get("archivo", "desconocido").replace(".pdf", ""),
            "texto": texto_completo.strip()
        })

    return fragmentos

def construir_faiss_coseno(fragmentos):
    textos = [f["texto"] for f in fragmentos]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    index = faiss.IndexFlatIP(vectores.shape[1])  # Coseno: usar producto punto con vectores normalizados
    index.add(np.array(vectores, dtype=np.float32))
    return index

def guardar(fragmentos, index):
    with open(OUTPUT_FRAGMENTOS, "w", encoding="utf-8") as f:
        json.dump(fragmentos, f, ensure_ascii=False, indent=2)
    faiss.write_index(index, str(OUTPUT_INDEX))
    print("✅ Índice FAISS y fragmentos enriquecidos guardados.")

if __name__ == "__main__":
    fragmentos = construir_fragmentos_enriquecidos()
    index = construir_faiss_coseno(fragmentos)
    guardar(fragmentos, index)

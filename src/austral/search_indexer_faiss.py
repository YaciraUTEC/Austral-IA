import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EXTRACTOS_PATH = "output/extractos_json"
OUTPUT_INDEX = "output/faiss_index.bin"
OUTPUT_FRAGMENTOS = "output/fragmentos_enriquecido.json"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def construir_fragmentos_enriquecidos():
    fragmentos = []

    for filename in os.listdir(EXTRACTOS_PATH):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(EXTRACTOS_PATH, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        texto_completo = " ".join(p.get("texto", "") for p in data.get("paginas", []))
        fragmentos.append({
            "fragment_id": filename.replace(".json", ""),
            "document_id": data.get("archivo", "desconocido").replace(".pdf", ""),
            "texto": texto_completo.strip()
        })

    return fragmentos

def construir_faiss(fragmentos):
    textos = [f["texto"] for f in fragmentos]
    vectores = model.encode(textos, show_progress_bar=True)
    index = faiss.IndexFlatL2(len(vectores[0]))
    index.add(np.array(vectores))
    return index

def guardar(fragmentos, index):
    with open(OUTPUT_FRAGMENTOS, "w", encoding="utf-8") as f:
        json.dump(fragmentos, f, ensure_ascii=False, indent=2)
    faiss.write_index(index, OUTPUT_INDEX)
    print("✅ Índice FAISS y fragmentos enriquecidos guardados.")

if __name__ == "__main__":
    fragmentos = construir_fragmentos_enriquecidos()
    index = construir_faiss(fragmentos)
    guardar(fragmentos, index)

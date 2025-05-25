import os
import json
import faiss
import numpy as np
from pathlib import Path
from austral.gpt_azure import embed_text

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
EXTRACTOS_PATH = BASE_DIR / "output" / "extractos_json"
OUTPUT_INDEX = BASE_DIR / "output" / "faiss_index.bin"
OUTPUT_FRAGMENTOS = BASE_DIR / "output" / "fragmentos_enriquecido.json"

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

'''
def construir_faiss_ivf_dot(fragmentos, nlist=32):
    textos = [f["texto"] for f in fragmentos]
    
    # Generar embeddings y normalizarlos
    vectores = [embed_text(t) for t in textos]
    vectores_np = np.array(vectores, dtype=np.float32)
    faiss.normalize_L2(vectores_np)  # Necesario para usar dot product como coseno

    dim = vectores_np.shape[1]
    quantizer = faiss.IndexFlatIP(dim)  # Cuantizador para producto interno
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)

    index.train(vectores_np)
    index.add(vectores_np)
    return index
'''


def construir_faiss_adaptativo(fragmentos):
    textos = [f["texto"] for f in fragmentos]
    vectores = [embed_text(t) for t in textos]
    vectores_np = np.array(vectores, dtype=np.float32)

    dim = vectores_np.shape[1]

    if len(fragmentos) < 500:
        print(f"🔹 Usando IndexFlatIP para {len(fragmentos)} fragmentos.")
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectores_np)  # Normalizamos para usar coseno con producto interno
        index.add(vectores_np)
    else:
        nlist = max(10, len(fragmentos) // 20)
        print(f"⚡️ Usando IndexIVFFlat (nlist={nlist}) para {len(fragmentos)} fragmentos.")
        quantizer = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        faiss.normalize_L2(vectores_np)
        index.train(vectores_np)
        index.add(vectores_np)

    return index


def guardar(fragmentos, index):
    with open(OUTPUT_FRAGMENTOS, "w", encoding="utf-8") as f:
        json.dump(fragmentos, f, ensure_ascii=False, indent=2)
    faiss.write_index(index, str(OUTPUT_INDEX))
    print("✅ Índice FAISS y fragmentos enriquecidos guardados.")

if __name__ == "__main__":
    fragmentos = construir_fragmentos_enriquecidos()
    index = construir_faiss_adaptativo(fragmentos)
    guardar(fragmentos, index)

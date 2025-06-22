# src/austral/indexing/search_indexer_faiss_pdf.py

import os
import json
import faiss
import numpy as np
from pathlib import Path
from austral.gpt_azure import embed_text
from austral.utils.index_config import get_faiss_index_type

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
FRAGMENTOS_PATH = BASE_DIR / "output" / "extractos_json" / "pdf"
ENRIQUECIDO_PATH = BASE_DIR / "output" / "fragmentos_enriquecido_pdf.json"
INDEX_PATH = BASE_DIR / "output" / "faiss_index_pdf.bin"

def cargar_fragmentos():
    fragmentos = []
    for archivo in os.listdir(FRAGMENTOS_PATH):
        if archivo.endswith(".json"):
            with open(os.path.join(FRAGMENTOS_PATH, archivo), "r", encoding="utf-8") as f:
                frag = json.load(f)
                fragmentos.append(frag)
    return fragmentos

def procesar_y_indexar(fragmentos):
    enriquecidos = []
    textos = []

    for frag in fragmentos:
        nombre_archivo = frag.get("archivo", "")
        document_id = nombre_archivo.split("_p")[0].strip()
        fragment_id = nombre_archivo.replace(".pdf", "")

        paginas = frag.get("paginas", [])
        texto_completo = "\n".join(p.get("texto", "").strip() for p in paginas if "texto" in p)

        enriquecidos.append({
            "fragment_id": fragment_id,
            "document_id": document_id,
            "texto": texto_completo
        })
        textos.append(texto_completo)

    embeddings = [embed_text(t) for t in textos]
    embeddings_np = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(embeddings_np)

    index = get_faiss_index_type(embeddings_np)
    index.add(embeddings_np)
    faiss.write_index(index, str(INDEX_PATH))

    with open(ENRIQUECIDO_PATH, "w", encoding="utf-8") as f:
        json.dump(enriquecidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Indexación completada para {len(enriquecidos)} fragmentos PDF.")

if __name__ == "__main__":
    fragmentos = cargar_fragmentos()
    procesar_y_indexar(fragmentos)

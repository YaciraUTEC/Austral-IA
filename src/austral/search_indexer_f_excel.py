import os
import json
import faiss
import numpy as np
from pathlib import Path
from austral.gpt_azure import embed_text
from austral.utils.index_config import get_faiss_index_type

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
FRAGMENTOS_PATH = BASE_DIR / "output" / "extractos_json" / "excel"
ENRIQUECIDO_PATH = BASE_DIR / "output" / "fragmentos_enriquecido_excel.json"
INDEX_PATH = BASE_DIR / "output" / "faiss_index_excel.bin"

def cargar_fragmentos():
    fragmentos = []
    for archivo in os.listdir(FRAGMENTOS_PATH):
        if archivo.endswith(".json"):
            with open(FRAGMENTOS_PATH / archivo, "r", encoding="utf-8") as f:
                frag = json.load(f)
                fragmentos.append(frag)
    return fragmentos

def tabla_a_texto_lineal(tabla: list[list[str]]) -> str:
    if not tabla:
        return ""
    encabezados = tabla[0]
    filas = tabla[1:]
    resultado = []
    for fila in filas:
        columnas = []
        for col, val in zip(encabezados, fila):
            val = val.strip() if val else "(vacío)"
            columnas.append(f"{col}: {val}")
        resultado.append(" - ".join(columnas))
    return "\n".join(resultado)

def procesar_y_indexar(fragmentos):
    enriquecidos = []
    textos = []

    for frag in fragmentos:
        document_id = frag.get("document_id", "desconocido")
        for hoja in frag.get("fragmentos", []):
            sheet_name = hoja.get("sheet_name", "unknown")
            fragment_id = f"{document_id}_{sheet_name}"

            bloques = hoja.get("contenido", [])
            texto_unificado = ""
            for b in bloques:
                if not isinstance(b, dict):
                    continue
                if b.get("tipo") == "texto":
                    texto_unificado += b.get("contenido", "") + "\n"
                elif b.get("tipo") == "tabla":
                    texto_unificado += tabla_a_texto_lineal(b.get("contenido", [])) + "\n"

            enriquecidos.append({
                "fragment_id": fragment_id,
                "document_id": document_id,
                "sheet_name": sheet_name,
                "texto": texto_unificado.strip()
            })
            textos.append(texto_unificado.strip())

    embeddings = [embed_text(texto) for texto in textos]
    embeddings_np = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(embeddings_np)

    index = get_faiss_index_type(embeddings_np)
    index.add(embeddings_np)
    faiss.write_index(index, str(INDEX_PATH))

    with open(ENRIQUECIDO_PATH, "w", encoding="utf-8") as f:
        json.dump(enriquecidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Indexación completada para {len(enriquecidos)} fragmentos Excel.")

if __name__ == "__main__":
    fragmentos = cargar_fragmentos()
    procesar_y_indexar(fragmentos)

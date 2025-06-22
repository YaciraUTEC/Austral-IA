import os
import json
import faiss
import numpy as np
import re
from pathlib import Path
from austral.gpt_azure import embed_text

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
EXTRACTOS_PDF_PATH = BASE_DIR / "output" / "extractos_json" / "pdf"
EXTRACTOS_EXCEL_PATH = BASE_DIR / "output" / "extractos_json" / "excel"
OUTPUT_INDEX = BASE_DIR / "output" / "faiss_index.bin"
OUTPUT_FRAGMENTOS = BASE_DIR / "output" / "fragmentos_enriquecido.json"

def construir_fragmentos_enriquecidos():
    fragmentos = []

    # Procesar PDFs
    for filename in os.listdir(EXTRACTOS_PDF_PATH):
        if not filename.endswith(".json"):
            continue
        filepath = EXTRACTOS_PDF_PATH / filename
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        texto_completo = " ".join(p.get("texto", "") for p in data.get("paginas", []))
        fragment_id = filename.replace(".json", "")
        archivo_nombre = data.get("archivo", "desconocido").replace(".pdf", "")
        document_id = re.sub(r"_p\d+(_\d+)?$", "", archivo_nombre)

        if texto_completo.strip():  # Omitir fragmentos vacíos
            fragmentos.append({
                "fragment_id": fragment_id,
                "document_id": document_id,
                "texto": texto_completo.strip(),
                "tipo": "pdf"
            })

    # Procesar Excels agrupados por archivo
    for filename in os.listdir(EXTRACTOS_EXCEL_PATH):
        if not filename.endswith(".json"):
            continue
        filepath = EXTRACTOS_EXCEL_PATH / filename
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        document_id = data.get("document_id", filename.replace(".json", ""))
        fragmentos_excel = data.get("fragmentos", [])

        for frag in fragmentos_excel:
            fragment_id = frag.get("fragment_id", "")
            sheet_name = frag.get("sheet_name", "unknown")
            contenido_raw = frag.get("contenido", [])

            texto_completo = []
            for bloque in contenido_raw:
                if not isinstance(bloque, dict):
                    continue
                tipo = bloque.get("tipo")
                contenido_bloque = bloque.get("contenido", "")
                if tipo == "texto" and isinstance(contenido_bloque, str):
                    texto_completo.append(contenido_bloque)
                elif tipo == "tabla" and isinstance(contenido_bloque, list):
                    filas = []
                    for fila in contenido_bloque:
                        if isinstance(fila, list):
                            fila_limpia = [str(cell).strip() for cell in fila if str(cell).strip()]
                            if fila_limpia:
                                filas.append(" | ".join(fila_limpia))
                    texto_completo.extend(filas)

            texto_final = "\n".join(texto_completo).strip()
            if texto_final:  # Omitir fragmentos vacíos
                fragmentos.append({
                    "fragment_id": fragment_id,
                    "document_id": document_id,
                    "sheet_name": sheet_name,
                    "texto": texto_final,
                    "tipo": "excel"
                })

    # Ordenar por tipo: pdf (por página) y excel (por hoja y fila)
    def orden_fragmento(frag):
        document_id = frag.get("document_id", "")
        fragment_id = frag.get("fragment_id", "")
        sheet_name = frag.get("sheet_name", "")
        if frag["tipo"] == "pdf":
            match = re.search(r"_p(\d+)", fragment_id)
            pagina = int(match.group(1)) if match else 0
            return (document_id, pagina)
        elif frag["tipo"] == "excel":
            match = re.search(r"_r(\d+)", fragment_id)
            fila = int(match.group(1)) if match else 0
            return (document_id, sheet_name.lower(), fila)
        return (document_id, 0)

    fragmentos.sort(key=orden_fragmento)
    return fragmentos

def construir_faiss_adaptativo(fragmentos):
    textos = [f["texto"] for f in fragmentos]
    vectores = [embed_text(t) for t in textos]
    vectores_np = np.array(vectores, dtype=np.float32)

    dim = vectores_np.shape[1]

    if len(fragmentos) < 300:
        print(f"🔹 Usando IndexFlatIP para {len(fragmentos)} fragmentos.")
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectores_np)
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

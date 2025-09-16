
import os
import json

def guardar_fragmentos_excel(fragmentos: list, output_dir: str):
    """Guarda todos los fragmentos de un archivo Excel en un único archivo JSON."""
    if not fragmentos:
        print("⚠️ No se encontraron fragmentos para guardar.")
        return

    os.makedirs(output_dir, exist_ok=True)

    document_id = fragmentos[0].get("document_id", "desconocido")
    output_path = os.path.join(output_dir, f"{document_id}.json")

    data = {
        "document_id": document_id,
        "tipo": "excel",
        "fragmentos": fragmentos
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Guardado archivo completo: {document_id}.json")

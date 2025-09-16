import os
import re
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_API_KEY)
)

def normalizar_clave(key: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", key)


def indexar_fragmento(metadato: dict):
    json_path = metadato["fragment_path"].replace(".pdf", ".json").replace("fragmentos", "extractos_json")
    if not os.path.exists(json_path):
        print(f"JSON no encontrado para fragmento {metadato['fragment_id']}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    contenido_texto = " ".join(p.get("texto", "") for p in data.get("paginas", []))
    fragment_id = normalizar_clave(metadato["fragment_id"])
    document_id = normalizar_clave(metadato["document_id"])

    doc = {
        "fragment_id": fragment_id,
        "document_id": document_id,
        "page_range": metadato.get("page_range", ""),
        "contenido_texto": contenido_texto,
        "status": metadato.get("status", "unknown")
    }

    result = search_client.upload_documents(documents=[doc])
    print(f"Indexado: {metadato['fragment_id']} -> {result}")

def indexar_todos_fragmentos(metadatos_path: str):
    with open(metadatos_path, "r", encoding="utf-8") as f:
        metadatos = json.load(f)

    for meta in metadatos:
        indexar_fragmento(meta)

if __name__ == "__main__":
    indexar_todos_fragmentos("output/fragmentos/fragmentos_metadata.json")

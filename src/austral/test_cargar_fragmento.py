import os
import json

# Ajusta esta ruta si tu carpeta de extractos es diferente
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../output/extractos_json"))

def cargar_texto_fragmento(fragment_id: str) -> str:
    json_path = os.path.join(OUTPUT_FOLDER, f"{fragment_id}.json")
    if not os.path.exists(json_path):
        print(f"No existe JSON para fragmento {fragment_id}")
        return ""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        texto = ""
        for pagina in data.get("paginas", []):
            texto += pagina.get("texto", "") + "\n"
        return texto
    except Exception as e:
        print(f"Error leyendo JSON {json_path}: {e}")
        return ""

if __name__ == "__main__":
    # Cambia este fragment_id por uno que tengas en tu carpeta extractos_json
    fragment_id = "Manual Secador FRT 8000 SC 30208_p1_50"

    contenido = cargar_texto_fragmento(fragment_id)
    if contenido:
        print(f"Contenido cargado del fragmento {fragment_id} (primeros 500 caracteres):\n")
        print(contenido[:500])
    else:
        print("No se pudo cargar contenido para ese fragmento.")

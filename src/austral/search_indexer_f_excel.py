import os
import json
import faiss
import numpy as np
from pathlib import Path
import sys
from austral.gpt_azure import embed_text
from austral.utils.index_config import get_faiss_index_type

# Configuración base
BASE_DIR = Path(__file__).resolve().parents[2]

# Función para obtener rutas según la categoría
def get_paths_for_category(categoria):
    """Devuelve las rutas de archivos para una categoría específica"""
    return {
        "fragmentos": BASE_DIR / "output" / "extractos_json" / "excel" / categoria,
        "enriquecido": BASE_DIR / "output" / f"fragmentos_enriquecido_{categoria}_excel.json",
        "index": BASE_DIR / "output" / f"faiss_index_{categoria}_excel.bin"
    }

def cargar_fragmentos(categoria):
    """Carga los fragmentos JSON de Excel de la categoría especificada"""
    fragmentos = []
    fragmentos_path = get_paths_for_category(categoria)["fragmentos"]
    
    if not os.path.exists(fragmentos_path):
        print(f"⚠️ No se encontró la carpeta {fragmentos_path}")
        return []
    
    for archivo in os.listdir(fragmentos_path):
        if archivo.endswith(".json"):
            try:
                with open(fragmentos_path / archivo, "r", encoding="utf-8") as f:
                    frag = json.load(f)
                    fragmentos.append(frag)
            except json.JSONDecodeError:
                print(f"⚠️ Error al cargar {archivo}: formato JSON incorrecto")
            except Exception as e:
                print(f"⚠️ Error al procesar {archivo}: {str(e)}")
    
    print(f"✅ Cargados {len(fragmentos)} fragmentos Excel de la categoría '{categoria}'")
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

def procesar_y_indexar(fragmentos, categoria):
    """Procesa e indexa los fragmentos Excel de una categoría específica"""
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
                "texto": texto_unificado.strip(),
                "categoria": categoria
            })
            textos.append(texto_unificado.strip())

    # Solo proceder si hay textos para indexar
    if not textos:
        print(f"⚠️ No hay contenido para indexar en la categoría '{categoria}'")
        return 0
        
    # Generar embeddings para cada texto
    print(f"Generando embeddings para {len(textos)} hojas de Excel...")
    embeddings = [embed_text(texto) for texto in textos]
    
    # Crear y guardar el índice
    embeddings_np = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(embeddings_np)

    index = get_faiss_index_type(embeddings_np)
    index.add(embeddings_np)
    
    # Obtener rutas para esta categoría
    paths = get_paths_for_category(categoria)
    faiss.write_index(index, str(paths["index"]))

    with open(paths["enriquecido"], "w", encoding="utf-8") as f:
        json.dump(enriquecidos, f, indent=2, ensure_ascii=False)

    print(f"✅ Indexación completada para {len(enriquecidos)} fragmentos Excel en categoría '{categoria}'.")
    return len(enriquecidos)

def procesar_todas_categorias(categorias):
    """Procesa todas las categorías especificadas"""
    total_fragmentos = 0
    
    for categoria in categorias:
        print(f"\n🔍 Procesando categoría Excel: {categoria.upper()}")
        fragmentos = cargar_fragmentos(categoria)
        if fragmentos:
            total = procesar_y_indexar(fragmentos, categoria)
            total_fragmentos += total
    
    print(f"\n✅ Indexación global completada para {total_fragmentos} fragmentos Excel en {len(categorias)} categorías")

if __name__ == "__main__":
    # Permitir especificar categoría desde la línea de comandos
    categorias = ["mantenimiento", "proyectos"]  # Categorías por defecto
    
    if len(sys.argv) > 1:
        categoria_arg = sys.argv[1].lower()
        if categoria_arg in categorias:
            print(f"Procesando solo la categoría: {categoria_arg}")
            fragmentos = cargar_fragmentos(categoria_arg)
            procesar_y_indexar(fragmentos, categoria_arg)
        else:
            print(f"Categoría no reconocida: {categoria_arg}")
            print(f"Categorías disponibles: {', '.join(categorias)}")
    else:
        # Procesar todas las categorías
        procesar_todas_categorias(categorias)

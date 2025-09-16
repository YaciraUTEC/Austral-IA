import os
import json
import faiss
import numpy as np
from pathlib import Path
import sys
from austral.gpt_azure import embed_text
from austral.utils.index_config import get_faiss_index_type
import concurrent.futures

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
    
    print(f"📂 Buscando en: {fragmentos_path}")
    archivos_json = [f for f in os.listdir(fragmentos_path) if f.endswith('.json')]
    print(f"🔍 Encontrados {len(archivos_json)} archivos JSON")

    for archivo in archivos_json:
        try:
            print(f"📄 Leyendo archivo: {archivo}")
            with open(os.path.join(fragmentos_path, archivo), "r", encoding="utf-8") as f:
                contenido = json.load(f)
                
                # Verificar estructura del contenido
                if isinstance(contenido, list):
                    print(f"  ↳ El archivo contiene una lista de {len(contenido)} elementos")
                    fragmentos.extend(contenido)  # Si es lista, extender
                elif isinstance(contenido, dict):
                    print(f"  ↳ El archivo contiene un diccionario")
                    if "content" in contenido:
                        print(f"  ↳ Encontrado campo 'content' con {len(contenido['content'])} elementos")
                    fragmentos.append(contenido)  # Si es diccionario, agregar
                else:
                    print(f"⚠️ Formato no reconocido en {archivo}")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON en {archivo}: {str(e)}")
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {str(e)}")

    print(f"\n✅ Total fragmentos cargados: {len(fragmentos)}")
    
    # Mostrar ejemplo del primer fragmento si existe
    if fragmentos:
        print("\n📝 Ejemplo del primer fragmento:")
        primer_frag = fragmentos[0]
        print(f"Keys disponibles: {list(primer_frag.keys())}")
        if "content" in primer_frag:
            print(f"Tipo de content: {type(primer_frag['content'])}")
            if isinstance(primer_frag["content"], list):
                print(f"Elementos en content: {len(primer_frag['content'])}")

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

def procesar_contenido_excel(content):
    """Procesa el contenido del Excel y lo convierte a texto limpio"""
    if not content:
        return ""

    texto_unificado = []
    headers = None

    for idx, item in enumerate(content):
        if isinstance(item, dict):
            # Primera fila es headers
            if idx == 0:
                headers = list(item.values())
                continue

            # Procesar valores
            valores = list(item.values())
            fila_texto = []
            for header, valor in zip(headers, valores):
                if valor and str(valor).strip():
                    fila_texto.append(f"{header}: {valor}")
            if fila_texto:
                texto_unificado.append(" ".join(fila_texto))  # Reemplazar '|' con espacio

    return "\n".join(texto_unificado)

def dividir_texto(texto, max_tokens=8000):
    """
    Divide un texto en fragmentos más pequeños que no excedan el límite de tokens.
    """
    palabras = texto.split()
    fragmentos = []
    fragmento_actual = []

    for palabra in palabras:
        if len(" ".join(fragmento_actual + [palabra])) > max_tokens:
            fragmentos.append(" ".join(fragmento_actual))
            fragmento_actual = [palabra]
        else:
            fragmento_actual.append(palabra)

    if fragmento_actual:
        fragmentos.append(" ".join(fragmento_actual))

    return fragmentos

def procesar_y_indexar(fragmentos, categoria):
    """Procesa e indexa los fragmentos Excel"""
    enriquecidos = []
    textos = []

    print(f"\n🔄 Procesando {len(fragmentos)} fragmentos Excel...")

    for doc in fragmentos:
        try:
            document_id = doc.get("document_id", "")
            print(f"\n📄 Procesando documento: {document_id}")

            for frag in doc.get("fragmentos", []):
                fragment_id = frag.get("fragment_id", "")
                sheet_name = frag.get("sheet_name", "")
                content = frag.get("content", [])

                print(f"  📑 Procesando hoja: {sheet_name} (Fragmento ID: {fragment_id})")

                texto = procesar_contenido_excel(content)

                if texto.strip():
                    print(f"✅ Texto extraído: {len(texto.split())} palabras")
                    fragmentos_texto = dividir_texto(texto)
                    for idx, frag_texto in enumerate(fragmentos_texto):
                        fragmento_enriquecido = {
                            "fragment_id": f"{fragment_id}_{idx}",
                            "document_id": document_id,
                            "sheet_name": sheet_name,
                            "texto": frag_texto,
                            "categoria": categoria
                        }
                        enriquecidos.append(fragmento_enriquecido)
                        textos.append(frag_texto)
                else:
                    print(f"⚠️ No se encontró texto en fragmento: {fragment_id}")

        except Exception as e:
            print(f"❌ Error procesando documento {document_id}: {str(e)}")
            continue

    if not textos:
        print(f"⚠️ No hay contenido para indexar en la categoría '{categoria}'")
        return 0

    print(f"\n✅ Procesados {len(textos)} fragmentos con texto")

    # Generar embeddings para cada fragmento
    embeddings = []
    for idx, texto in enumerate(textos, start=1):
        try:
            print(f"🔄 Generando embedding para fragmento {idx}/{len(textos)}...")
            embeddings.append(embed_text(texto))
        except Exception as e:
            print(f"❌ Error generando embedding para un fragmento: {str(e)}")
            continue

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
        procesar_todas_categorias(categorias)



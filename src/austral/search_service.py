import faiss
import json
import numpy as np
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor
from austral.gpt_azure import embed_text

# Configuración de FAISS
faiss.omp_set_num_threads(4)  # Ajusta según tu CPU

# Rutas base
BASE_DIR = Path(__file__).resolve().parents[2]

# Categorías disponibles
CATEGORIAS = ["mantenimiento", "proyectos"]

# Diccionarios para almacenar índices y fragmentos por categoría
indices_pdf = {}
indices_excel = {}
fragmentos_pdf = {}
fragmentos_excel = {}

def get_paths_for_category(categoria):
    """Devuelve las rutas de archivos para una categoría específica"""
    return {
        "index_pdf": BASE_DIR / "output" / f"faiss_index_{categoria}_pdf.bin",
        "index_excel": BASE_DIR / "output" / f"faiss_index_{categoria}_excel.bin",
        "fragmentos_pdf": BASE_DIR / "output" / f"fragmentos_enriquecido_{categoria}_pdf.json",
        "fragmentos_excel": BASE_DIR / "output" / f"fragmentos_enriquecido_{categoria}_excel.json"
    }

# Cargar índices y fragmentos para todas las categorías
def cargar_indices_y_fragmentos():
    for categoria in CATEGORIAS:
        rutas = get_paths_for_category(categoria)
        
        # Cargar índices PDF si existen
        if os.path.exists(rutas["index_pdf"]):
            indices_pdf[categoria] = faiss.read_index(str(rutas["index_pdf"]))
            
            # Configurar búsqueda para índice IVF si aplica
            if isinstance(indices_pdf[categoria], faiss.IndexIVFFlat):
                if not indices_pdf[categoria].is_trained:
                    print(f"⚠️ El índice IVF de PDF para '{categoria}' no ha sido entrenado.")
                else:
                    indices_pdf[categoria].nprobe = 30
            
            # Cargar fragmentos PDF
            if os.path.exists(rutas["fragmentos_pdf"]):
                with open(rutas["fragmentos_pdf"], "r", encoding="utf-8") as f:
                    fragmentos_pdf[categoria] = json.load(f)
                    print(f"✅ Cargados {len(fragmentos_pdf[categoria])} fragmentos PDF para '{categoria}'")
            else:
                fragmentos_pdf[categoria] = []
        else:
            print(f"⚠️ No existe índice PDF para la categoría '{categoria}'")
            indices_pdf[categoria] = None
            fragmentos_pdf[categoria] = []
        
        # Cargar índices Excel si existen
        if os.path.exists(rutas["index_excel"]):
            indices_excel[categoria] = faiss.read_index(str(rutas["index_excel"]))
            
            # Configurar búsqueda para índice IVF si aplica
            if isinstance(indices_excel[categoria], faiss.IndexIVFFlat):
                if not indices_excel[categoria].is_trained:
                    print(f"⚠️ El índice IVF de Excel para '{categoria}' no ha sido entrenado.")
                else:
                    indices_excel[categoria].nprobe = 30
            
            # Cargar fragmentos Excel
            if os.path.exists(rutas["fragmentos_excel"]):
                with open(rutas["fragmentos_excel"], "r", encoding="utf-8") as f:
                    fragmentos_excel[categoria] = json.load(f)
                    print(f"✅ Cargados {len(fragmentos_excel[categoria])} fragmentos Excel para '{categoria}'")
            else:
                fragmentos_excel[categoria] = []
        else:
            print(f"⚠️ No existe índice Excel para la categoría '{categoria}'")
            indices_excel[categoria] = None
            fragmentos_excel[categoria] = []

# Cargar todos los índices y fragmentos al iniciar
cargar_indices_y_fragmentos()

# Ya no necesitamos este bloque aquí, lo hemos movido a la función cargar_indices_y_fragmentos

def detectar_hoja_en_pregunta(pregunta: str, categoria: str) -> str | None:
    """Detecta si se menciona una hoja específica en la pregunta"""
    if categoria not in fragmentos_excel:
        return None
        
    # Obtener todas las hojas disponibles para la categoría
    hojas_disponibles = list({frag.get("sheet_name", "") for frag in fragmentos_excel[categoria] if "sheet_name" in frag})
    
    pregunta_lower = pregunta.lower()
    for hoja in hojas_disponibles:
        if hoja and hoja.lower() in pregunta_lower:
            return hoja
    return None

# Funciones separadas para búsqueda
def buscar_en_pdf(embedding_np, top_k, categoria):
    """Busca en el índice PDF de una categoría específica"""
    if indices_pdf.get(categoria) is None or not fragmentos_pdf.get(categoria):
        return []
    
    D_pdf, I_pdf = indices_pdf[categoria].search(embedding_np, top_k)
    resultados_pdf = []
    
    for rank, idx in enumerate(I_pdf[0]):
        if 0 <= idx < len(fragmentos_pdf[categoria]):
            frag = fragmentos_pdf[categoria][idx].copy()
            frag["score"] = float(D_pdf[0][rank])
            frag["tipo"] = "PDF"
            frag["categoria"] = categoria
            resultados_pdf.append(frag)
    
    return resultados_pdf

def buscar_en_excel(embedding_np, top_k, categoria, hoja_mencionada):
    """Busca en el índice Excel de una categoría específica"""
    if indices_excel.get(categoria) is None or not fragmentos_excel.get(categoria):
        return []
    
    D_excel, I_excel = indices_excel[categoria].search(embedding_np, top_k)
    resultados_excel = []
    
    for rank, idx in enumerate(I_excel[0]):
        if 0 <= idx < len(fragmentos_excel[categoria]):
            frag = fragmentos_excel[categoria][idx].copy()
            frag["score"] = float(D_excel[0][rank])
            frag["tipo"] = "EXCEL"
            frag["categoria"] = categoria
            
            if hoja_mencionada:
                if frag.get("sheet_name", "").lower() != hoja_mencionada.lower():
                    continue
                    
            resultados_excel.append(frag)
    
    return resultados_excel

# Búsqueda principal
def buscar_fragmentos(query: str, categoria: str = None, top_k: int = 12) -> list:
    """
    Busca fragmentos relevantes para una consulta.
    
    Args:
        query (str): La consulta del usuario
        categoria (str, optional): Categoría específica donde buscar ('mantenimiento', 'proyectos', etc.)
                                  Si es None, buscará en todas las categorías disponibles.
        top_k (int, optional): Número máximo de resultados por tipo de documento. Por defecto 12.
        
    Returns:
        list: Lista combinada de fragmentos relevantes ordenados por puntuación
    """
    # Generar embedding para la consulta
    embedding = embed_text(query)
    embedding_np = np.array([embedding], dtype=np.float32)
    faiss.normalize_L2(embedding_np)
    
    # Si no se especifica categoría, buscar en todas las disponibles
    categorias_a_buscar = [categoria] if categoria else CATEGORIAS
    
    todos_resultados = []
    
    for cat in categorias_a_buscar:
        if cat not in fragmentos_excel and cat not in fragmentos_pdf:
            print(f"⚠️ Categoría no encontrada: {cat}")
            continue
        
        # Detectar si la consulta menciona alguna hoja específica para esta categoría
        hoja_mencionada = detectar_hoja_en_pregunta(query, cat)
        
        # Realizar búsquedas en paralelo para esta categoría
        with ThreadPoolExecutor() as executor:
            futuro_pdf = executor.submit(buscar_en_pdf, embedding_np, top_k, cat)
            futuro_excel = executor.submit(buscar_en_excel, embedding_np, top_k, cat, hoja_mencionada)
            
            resultados_pdf = futuro_pdf.result()
            resultados_excel = futuro_excel.result()
            
            todos_resultados.extend(resultados_pdf)
            todos_resultados.extend(resultados_excel)
    
    # Ordenar por relevancia (mayor score)
    todos_resultados.sort(key=lambda x: x["score"], reverse=True)
    
    # Limitar a los top_k mejores resultados en total
    return todos_resultados[:top_k]

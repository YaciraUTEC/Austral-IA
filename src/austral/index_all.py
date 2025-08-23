#!/usr/bin/env python3
"""
Script unificado para indexar todas las categorías y tipos de documentos.
Ejecuta los indexadores para PDF y Excel en todas las categorías configuradas.
"""

import os
import sys
import time
import multiprocessing
import subprocess
from pathlib import Path
from austral.search_indexer_f_pdf import procesar_todas_categorias as procesar_todas_pdf
from austral.search_indexer_f_excel import procesar_todas_categorias as procesar_todas_excel
from austral.process_manager import run as procesar_archivos

# Categorías soportadas por el sistema
CATEGORIAS = ["mantenimiento", "proyectos"]

def correr_indexador_pdf(categoria=None):
    if categoria:
        subprocess.run(["python", "src/austral/search_indexer_f_pdf.py", categoria], check=True)
    else:
        subprocess.run(["python", "src/austral/search_indexer_f_pdf.py"], check=True)

def correr_indexador_excel(categoria=None):
    if categoria:
        subprocess.run(["python", "src/austral/search_indexer_f_excel.py", categoria], check=True)
    else:
        subprocess.run(["python", "src/austral/search_indexer_f_excel.py"], check=True)

def ejecutar_indexacion_completa():
    """Ejecuta todo el proceso de indexación"""
    tiempo_inicio = time.perf_counter()
    
    print("\n" + "=" * 80)
    print(" 📂 PASO 1: DESCARGA Y PROCESAMIENTO DE ARCHIVOS")
    print("=" * 80)
    procesar_archivos()
    
    print("\n" + "=" * 80)
    print(" 📄 PASO 2: INDEXACIÓN DE DOCUMENTOS")
    print("=" * 80)
    
    # Podemos procesar en paralelo las categorías
    procesos = []
    
    for categoria in CATEGORIAS:
        print(f"\n🔍 Procesando categoría: {categoria.upper()}")
        
        proceso_pdf = multiprocessing.Process(target=correr_indexador_pdf, args=(categoria,))
        proceso_excel = multiprocessing.Process(target=correr_indexador_excel, args=(categoria,))
        
        procesos.append(proceso_pdf)
        procesos.append(proceso_excel)
        
        proceso_pdf.start()
        proceso_excel.start()
    
    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()
    
    tiempo_fin = time.perf_counter()
    duracion = tiempo_fin - tiempo_inicio
    
    print("\n" + "=" * 80)
    print(f" ✅ INDEXACIÓN COMPLETADA EN {duracion:.2f} SEGUNDOS")
    print(f" 🔍 Categorías indexadas: {', '.join(CATEGORIAS)}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    # Verificar si hay que añadir una nueva categoría
    if len(sys.argv) > 1 and sys.argv[1] == "--add-category" and len(sys.argv) > 2:
        nueva_categoria = sys.argv[2].lower()
        if nueva_categoria in CATEGORIAS:
            print(f"La categoría '{nueva_categoria}' ya existe.")
        else:
            CATEGORIAS.append(nueva_categoria)
            print(f"Nueva categoría añadida: '{nueva_categoria}'")
    
    ejecutar_indexacion_completa()

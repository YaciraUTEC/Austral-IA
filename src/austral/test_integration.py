"""
Script de prueba para validar la integración completa del sistema de indexación y búsqueda por categorías.
Este script ejecuta todo el flujo desde la descarga de archivos de SharePoint hasta la búsqueda en índices.
"""
import os
import time
import json
from pathlib import Path
import requests

# Importar los módulos del sistema
from austral.sharepoint_conector import obtener_archivos_sharepoint
from austral.process_manager import procesar_categoria
from austral.search_indexer_f_pdf import create_index as create_index_pdf
from austral.search_indexer_f_excel import create_index as create_index_excel
from austral.search_service import cargar_indices_y_fragmentos, buscar_fragmentos

# Definir las categorías a probar
CATEGORIAS = ["mantenimiento", "proyectos"]

def test_sharepoint_connection():
    """Prueba la conexión con SharePoint y la descarga de archivos por categoría"""
    print("\n===== PROBANDO CONEXIÓN CON SHAREPOINT =====")
    for categoria in CATEGORIAS:
        print(f"\nProbando descarga de archivos para la categoría '{categoria}':")
        try:
            archivos = obtener_archivos_sharepoint(categoria)
            print(f"✅ Conexión exitosa. Se encontraron {len(archivos)} archivos en la categoría '{categoria}'")
            # Mostrar los primeros 3 archivos para verificar
            for i, archivo in enumerate(archivos[:3]):
                print(f"  - {archivo['filename']} (Última modificación: {archivo['lastModifiedDateTime']})")
            if len(archivos) > 3:
                print(f"  ... y {len(archivos) - 3} archivos más")
        except Exception as e:
            print(f"❌ Error al conectar con SharePoint para la categoría '{categoria}': {str(e)}")
            return False
    
    return True

def test_document_processing():
    """Prueba el procesamiento de documentos por categoría"""
    print("\n===== PROBANDO PROCESAMIENTO DE DOCUMENTOS =====")
    for categoria in CATEGORIAS:
        print(f"\nProcesando documentos para la categoría '{categoria}':")
        try:
            # Verificar que hay archivos en SharePoint
            archivos = obtener_archivos_sharepoint(categoria)
            if not archivos:
                print(f"⚠️ No se encontraron archivos para la categoría '{categoria}'")
                continue
            
            print(f"📂 Encontrados {len(archivos)} archivos para procesar en la categoría '{categoria}'")    
                
            # Procesar los documentos utilizando procesar_categoria directamente
            procesar_categoria(categoria)
            
            # Verificar que se hayan generado archivos en las rutas esperadas
            import os
            import json
            from pathlib import Path
            from austral.process_manager import obtener_rutas_categoria
            
            rutas = obtener_rutas_categoria(categoria)
            
            # Verificar registro de archivos procesados
            if os.path.exists(rutas['registro']):
                with open(rutas['registro'], 'r', encoding='utf-8') as f:
                    registro = json.load(f)
                print(f"✅ Procesamiento exitoso. Registro contiene {len(registro)} archivos")
                
                # Contar PDFs y Excels procesados
                pdf_count = sum(1 for item in registro.values() if item.get('filename', '').lower().endswith('.pdf'))
                excel_count = sum(1 for item in registro.values() if item.get('filename', '').lower().endswith('.xlsx'))
                
                print(f"  - PDFs procesados: {pdf_count}")
                print(f"  - Excels procesados: {excel_count}")
            else:
                print(f"⚠️ No se encontró archivo de registro para la categoría '{categoria}'")
        except Exception as e:
            print(f"❌ Error al procesar documentos para la categoría '{categoria}': {str(e)}")
            return False
    
    return True

def test_indexing():
    """Prueba la creación de índices por categoría y tipo de archivo"""
    print("\n===== PROBANDO CREACIÓN DE ÍNDICES =====")
    
    # Base dir para verificar archivos
    base_dir = Path(__file__).resolve().parents[2]
    
    for categoria in CATEGORIAS:
        print(f"\nCreando índices para la categoría '{categoria}':")
        
        # Rutas de archivos para verificar
        index_pdf_path = base_dir / "output" / f"faiss_index_{categoria}_pdf.bin"
        fragments_pdf_path = base_dir / "output" / f"fragmentos_enriquecido_{categoria}_pdf.json"
        index_excel_path = base_dir / "output" / f"faiss_index_{categoria}_excel.bin"
        fragments_excel_path = base_dir / "output" / f"fragmentos_enriquecido_{categoria}_excel.json"
        
        try:
            # Indexar PDFs
            start_time = time.time()
            create_index_pdf(categoria)
            pdf_time = time.time() - start_time
            
            # Verificar que se crearon los archivos de índice PDF
            pdf_exists = index_pdf_path.exists() and fragments_pdf_path.exists()
            
            if pdf_exists:
                # Contar fragmentos PDF
                with open(fragments_pdf_path, 'r', encoding='utf-8') as f:
                    pdf_fragments = json.load(f)
                print(f"✅ Índice PDF creado con {len(pdf_fragments)} fragmentos en {pdf_time:.2f} segundos")
            else:
                print(f"⚠️ No se creó el índice PDF para '{categoria}', posiblemente no hay archivos PDF procesados")
                
            # Indexar Excels
            start_time = time.time()
            create_index_excel(categoria)
            excel_time = time.time() - start_time
            
            # Verificar que se crearon los archivos de índice Excel
            excel_exists = index_excel_path.exists() and fragments_excel_path.exists()
            
            if excel_exists:
                # Contar fragmentos Excel
                with open(fragments_excel_path, 'r', encoding='utf-8') as f:
                    excel_fragments = json.load(f)
                print(f"✅ Índice Excel creado con {len(excel_fragments)} fragmentos en {excel_time:.2f} segundos")
            else:
                print(f"⚠️ No se creó el índice Excel para '{categoria}', posiblemente no hay archivos Excel procesados")
                
        except Exception as e:
            print(f"❌ Error al crear índices para la categoría '{categoria}': {str(e)}")
            return False
    
    return True

def test_search():
    """Prueba la búsqueda en los índices por categoría"""
    print("\n===== PROBANDO BÚSQUEDA EN ÍNDICES =====")
    
    # Cargar índices y fragmentos
    cargar_indices_y_fragmentos()
    
    # Consultas de prueba para cada categoría
    consultas = {
        "mantenimiento": [
            "procedimiento de mantenimiento preventivo", 
            "reemplazo de piezas",
            "frecuencia de mantenimiento"
        ],
        "proyectos": [
            "presupuesto del proyecto",
            "cronograma de implementación", 
            "requisitos técnicos"
        ]
    }
    
    for categoria in CATEGORIAS:
        print(f"\nRealizando búsquedas para la categoría '{categoria}':")
        
        for consulta in consultas.get(categoria, ["información"]):
            try:
                print(f"\nConsulta: '{consulta}'")
                
                # Realizar búsqueda específica en esta categoría
                resultados = buscar_fragmentos(consulta, categoria=categoria)
                
                if resultados:
                    print(f"✅ Búsqueda exitosa: {len(resultados)} resultados encontrados")
                    
                    # Mostrar los primeros 3 resultados
                    for i, res in enumerate(resultados[:3]):
                        print(f"  {i+1}. Tipo: {res['tipo']}, Score: {res['score']:.2f}")
                        print(f"     Fragmento: {res['text'][:100]}...")
                        if 'filename' in res:
                            print(f"     Archivo: {res['filename']}")
                else:
                    print(f"⚠️ La búsqueda no devolvió resultados")
                    
                # También probar búsqueda global (sin especificar categoría)
                resultados_globales = buscar_fragmentos(consulta)
                print(f"\nBúsqueda global para '{consulta}': {len(resultados_globales)} resultados")
                
            except Exception as e:
                print(f"❌ Error al realizar la búsqueda '{consulta}' en '{categoria}': {str(e)}")
                return False
    
    return True

def test_api():
    """Prueba la API de búsqueda con parámetro de categoría"""
    print("\n===== PROBANDO API CON PARÁMETRO DE CATEGORÍA =====")
    
    # Consultas de prueba para cada categoría
    consultas = {
        "mantenimiento": "plan de mantenimiento",
        "proyectos": "presupuesto del proyecto"
    }
    
    try:
        # Suponiendo que la API está corriendo localmente en el puerto 8000
        base_url = "http://localhost:8000/asistente"
        
        for categoria, consulta in consultas.items():
            print(f"\nConsulta a la API para categoría '{categoria}': '{consulta}'")
            
            # Realizar consulta a la API con categoría
            response = requests.post(
                base_url,
                json={"pregunta": consulta, "categoria": categoria}
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("respuesta", "")
                print(f"✅ API respondió correctamente")
                print(f"Respuesta (primeros 150 caracteres): {respuesta[:150]}...")
            else:
                print(f"❌ Error en la API: Código {response.status_code}")
                print(f"Detalle: {response.text}")
                return False
            
            # Probar también sin especificar categoría
            print(f"\nConsulta a la API sin especificar categoría: '{consulta}'")
            response = requests.post(
                base_url,
                json={"pregunta": consulta}
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("respuesta", "")
                print(f"✅ API respondió correctamente")
                print(f"Respuesta (primeros 150 caracteres): {respuesta[:150]}...")
            else:
                print(f"❌ Error en la API: Código {response.status_code}")
                print(f"Detalle: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error al probar la API: {str(e)}")
        print("⚠️ Asegúrate de que la API esté en ejecución antes de ejecutar esta prueba.")
        return False
        
    return True

def run_all_tests():
    """Ejecuta todas las pruebas secuencialmente"""
    print("🔍 INICIANDO PRUEBAS DE INTEGRACIÓN COMPLETA DEL SISTEMA")
    
    # Paso 1: Probar conexión con SharePoint y descarga de archivos
    if not test_sharepoint_connection():
        print("\n❌ PRUEBA FALLIDA: Error en la conexión con SharePoint")
        return False
        
    # Paso 2: Probar procesamiento de documentos
    if not test_document_processing():
        print("\n❌ PRUEBA FALLIDA: Error en el procesamiento de documentos")
        return False
        
    # Paso 3: Probar creación de índices
    if not test_indexing():
        print("\n❌ PRUEBA FALLIDA: Error en la creación de índices")
        return False
        
    # Paso 4: Probar búsqueda en índices
    if not test_search():
        print("\n❌ PRUEBA FALLIDA: Error en la búsqueda en índices")
        return False
        
    # Paso 5: Probar API (opcional, ya que requiere que la API esté en ejecución)
    print("\n⚠️ La prueba de la API requiere que la API esté en ejecución.")
    print("¿Deseas probar la API? (s/n): ", end="")
    if input().lower().startswith("s"):
        if not test_api():
            print("\n❌ PRUEBA FALLIDA: Error en la API")
            return False
    else:
        print("Prueba de API omitida.")
        
    print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    return True

if __name__ == "__main__":
    run_all_tests()

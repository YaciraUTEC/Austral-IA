"""
Script para probar el filtrado por categorías en el sistema de búsqueda.
Este script envía consultas directamente al backend con diferentes combinaciones
de preguntas y categorías para verificar que el filtrado funciona correctamente.
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8000/api/asistente"
USER_ID = "test_user"

# Categorías disponibles
CATEGORIAS = ["mantenimiento", "proyectos"]

# Consultas de prueba para cada categoría
CONSULTAS = {
    "mantenimiento": [
        "¿Cuáles son las partes de una electrobomba?",
        "¿Cuál es el procedimiento de mantenimiento preventivo?",
        "¿Cada cuánto se debe hacer el mantenimiento de los equipos?"
    ],
    "proyectos": [
        "¿Cuál es el presupuesto del proyecto?",
        "¿Cuál es el avance actual del proyecto de caldera?",
        "¿Cuándo finaliza el proyecto?"
    ]
}

def enviar_consulta(pregunta, categoria=None):
    """Envía una consulta al backend con o sin categoría"""
    payload = {
        "user_id": USER_ID,
        "pregunta": pregunta
    }
    
    if categoria:
        payload["categoria"] = categoria
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return None
            
        data = response.json()
        return data.get("respuesta")
    except Exception as e:
        print(f"Error al enviar consulta: {str(e)}")
        return None

def probar_filtrado():
    """
    Prueba diferentes combinaciones de consultas y categorías para
    verificar que el filtrado funciona correctamente.
    """
    print("🔍 PROBANDO FILTRADO POR CATEGORÍAS\n")
    
    # 1. Probar cada consulta en su categoría correspondiente (debería funcionar)
    print("===== PRUEBA 1: CONSULTAS EN SU CATEGORÍA CORRESPONDIENTE =====")
    for categoria, consultas in CONSULTAS.items():
        print(f"\n📂 CATEGORÍA: {categoria.upper()}")
        
        for i, consulta in enumerate(consultas):
            print(f"\nConsulta {i+1}: {consulta}")
            respuesta = enviar_consulta(consulta, categoria)
            
            if respuesta:
                # Verificar si la respuesta indica falta de información
                if "No se encontró información relevante" in respuesta:
                    print("❌ ERROR: La consulta debería encontrar información en su propia categoría")
                else:
                    print("✅ Respuesta obtenida correctamente")
                    print(f"Fragmento de la respuesta: {respuesta[:100]}...")
            else:
                print("❌ ERROR: No se recibió respuesta del servidor")
    
    # 2. Probar cada consulta en la categoría opuesta (debería indicar que no hay información)
    print("\n\n===== PRUEBA 2: CONSULTAS EN LA CATEGORÍA OPUESTA =====")
    for categoria, consultas in CONSULTAS.items():
        categoria_opuesta = [c for c in CATEGORIAS if c != categoria][0]
        print(f"\n📂 CATEGORÍA DE LA CONSULTA: {categoria.upper()}")
        print(f"📂 CATEGORÍA USADA: {categoria_opuesta.upper()}")
        
        for i, consulta in enumerate(consultas):
            print(f"\nConsulta {i+1}: {consulta}")
            respuesta = enviar_consulta(consulta, categoria_opuesta)
            
            if respuesta:
                # Verificar si la respuesta indica falta de información
                if "No se encontró información relevante" in respuesta:
                    print("✅ Correcto: Indica que no hay información en esta categoría")
                else:
                    print("❌ ERROR: La consulta está respondiendo con información de otra categoría")
                    print(f"Fragmento de la respuesta: {respuesta[:100]}...")
            else:
                print("❌ ERROR: No se recibió respuesta del servidor")
    
    # 3. Probar cada consulta sin especificar categoría (debería funcionar)
    print("\n\n===== PRUEBA 3: CONSULTAS SIN ESPECIFICAR CATEGORÍA =====")
    for categoria, consultas in CONSULTAS.items():
        print(f"\n📂 CONSULTAS DE: {categoria.upper()}")
        
        for i, consulta in enumerate(consultas):
            print(f"\nConsulta {i+1}: {consulta}")
            respuesta = enviar_consulta(consulta)
            
            if respuesta:
                # Verificar si la respuesta indica falta de información
                if "No se encontró información relevante" in respuesta:
                    print("❌ ERROR: La consulta debería encontrar información en alguna categoría")
                else:
                    print("✅ Respuesta obtenida correctamente (búsqueda global)")
                    print(f"Fragmento de la respuesta: {respuesta[:100]}...")
            else:
                print("❌ ERROR: No se recibió respuesta del servidor")

if __name__ == "__main__":
    # Verificar conexión con el backend
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ Conexión con el backend establecida\n")
            probar_filtrado()
        else:
            print(f"❌ Error al conectar con el backend: {response.status_code}")
    except Exception as e:
        print(f"❌ No se pudo conectar con el backend: {str(e)}")
        print("Asegúrate de que el servidor esté en ejecución en http://localhost:8000")

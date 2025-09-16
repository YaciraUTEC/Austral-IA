import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID")
CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET")
SHAREPOINT_SITE = os.getenv("SHAREPOINT_SITE")
SHAREPOINT_DRIVE = os.getenv("SHAREPOINT_DRIVE")  # Ej: "Documentos"
SHAREPOINT_FOLDER = os.getenv("SHAREPOINT_FOLDER")  # "" o carpeta específica

def obtener_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def obtener_site_id(token):
    parsed = urlparse(SHAREPOINT_SITE)
    hostname = parsed.hostname
    path = parsed.path.lstrip("/")
    url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["id"]

def obtener_drive_id(token, site_id):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    drives = r.json()["value"]
    for d in drives:
        if d["name"].lower() == SHAREPOINT_DRIVE.lower():
            return d["id"]
    raise Exception("No se encontró el drive")

def listar_archivos_recursivo(token, drive_id, folder_path="", categoria_principal=None):
    """
    Lista archivos en el drive de SharePoint de forma recursiva, explorando subcarpetas.
    """
    print(f"🔍 Explorando carpeta: {folder_path}")
    
    # Construir URL para listar elementos
    if folder_path:
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}:/children"
    else:
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    items = r.json()["value"]

    archivos = []
    for item in items:
        current_path = folder_path + "/" + item["name"] if folder_path else item["name"]
        
        if "file" in item:
            print(f"📄 Archivo encontrado: {item['name']} en {folder_path}")
            archivos.append({
                "name": item["name"],
                "id": item["id"],
                "lastModifiedDateTime": item["lastModifiedDateTime"],
                "path": folder_path,
                "file": True
            })
        elif "folder" in item:
            print(f"📂 Explorando subcarpeta: {current_path}")
            # Llamada recursiva para la subcarpeta
            subcarpeta_archivos = listar_archivos_recursivo(token, drive_id, current_path, categoria_principal)
            archivos.extend(subcarpeta_archivos)
    
    return archivos

def listar_archivos(token, drive_id, categoria=None):
    """
    Lista archivos en el drive de SharePoint, filtrando por categoría e incluyendo subcarpetas.
    """
    base_folder = SHAREPOINT_FOLDER or ""
    folder_path = f"{base_folder}/{categoria}".strip("/") if categoria else base_folder
    print(f"🔍 Iniciando búsqueda en categoría: {categoria} (ruta: {folder_path})")
    return listar_archivos_recursivo(token, drive_id, folder_path, categoria)

def descargar_archivo_bytes(token, drive_id, item_id):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.content  # Devuelve los bytes del archivo

# Agregar constante de extensiones soportadas
EXTENSIONES_SOPORTADAS = [".pdf", ".docx", ".doc", ".xlsx", ".xls"]

# Función principal para obtener archivos como diccionario de {nombre: bytes}
def obtener_archivos_sharepoint(categoria=None):
    """
    Obtiene archivos desde SharePoint, incluyendo los de subcarpetas.
    Solo descarga archivos con extensiones soportadas.
    """
    print(f"🔄 Iniciando obtención de archivos para categoría: {categoria}")
    token = obtener_token()
    site_id = obtener_site_id(token)
    drive_id = obtener_drive_id(token, site_id)
    
    archivos = listar_archivos(token, drive_id, categoria)
    print(f"📁 Total de archivos encontrados: {len(archivos)}")

    archivos_bytes = []
    for item in archivos:
        if item.get("file"):
            nombre = item["name"]
            extension = os.path.splitext(nombre)[1].lower()
            
            # Verificar si la extensión está soportada antes de descargar
            if extension not in EXTENSIONES_SOPORTADAS:
                print(f"⏩ Omitiendo descarga de {nombre} (formato no soportado)")
                continue

            print(f"📥 Descargando: {nombre} de {item['path']}")
            try:
                contenido = descargar_archivo_bytes(token, drive_id, item["id"])
                archivos_bytes.append({
                    "filename": nombre,
                    "content": contenido,
                    "id": item["id"],
                    "drive_id": drive_id,
                    "lastModifiedDateTime": item["lastModifiedDateTime"],
                    "categoria": categoria,
                    "path": item["path"]
                })
                print(f"✅ Descargado: {nombre}")
            except Exception as e:
                print(f"❌ Error descargando {nombre}: {str(e)}")
    
    print(f"✅ Total de archivos procesados: {len(archivos_bytes)}")
    return archivos_bytes

def convertir_word_a_pdf(token, drive_id, item_id):
 
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content?format=pdf"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content
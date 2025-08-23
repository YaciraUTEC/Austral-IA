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

def listar_archivos(token, drive_id, categoria=None):
    """
    Lista archivos en el drive de SharePoint, opcionalmente filtrando por categoría
    Si se especifica una categoría, buscará en esa subcarpeta.
    """
    base_folder = SHAREPOINT_FOLDER or ""
    
    if categoria:
        # Si hay una categoría, la concatenamos a la carpeta base
        folder_path = f"{base_folder}/{categoria}".strip('/')
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}:/children"
    elif base_folder:
        # Si hay carpeta base pero no categoría
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{base_folder}:/children"
    else:
        # Si no hay ni carpeta base ni categoría
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["value"]

def descargar_archivo_bytes(token, drive_id, item_id):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.content  # Devuelve los bytes del archivo

# Función principal para obtener archivos como diccionario de {nombre: bytes}
def obtener_archivos_sharepoint(categoria=None):
    """
    Obtiene archivos desde SharePoint, opcionalmente filtrando por categoría.
    
    Args:
        categoria (str, optional): Categoría de documentos (ej. 'Mantenimiento', 'Proyectos')
        
    Returns:
        list: Lista de diccionarios con información de cada archivo
    """
    token = obtener_token()
    site_id = obtener_site_id(token)
    drive_id = obtener_drive_id(token, site_id)
    archivos = listar_archivos(token, drive_id, categoria)

    archivos_bytes = []
    for item in archivos:
        if "file" in item:
            nombre = item["name"]
            contenido = descargar_archivo_bytes(token, drive_id, item["id"])
            archivos_bytes.append({
                "filename": nombre,
                "content": contenido,
                "id": item["id"],
                "lastModifiedDateTime": item["lastModifiedDateTime"],
                "categoria": categoria or "general"  # Guardar la categoría con el archivo
            })
    return archivos_bytes

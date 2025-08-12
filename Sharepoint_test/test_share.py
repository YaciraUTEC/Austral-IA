import os
import requests
from dotenv import load_dotenv

# Carga las variables de entorno del .env
load_dotenv()

TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID")
CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET")
SHAREPOINT_SITE = os.getenv("SHAREPOINT_SITE")  # Ej: https://milton02.sharepoint.com/sites/Mantenimiento
DRIVE_NAME = os.getenv("SHAREPOINT_DRIVE")      # Ej: Documentos compartidos
FOLDER_PATH = os.getenv("SHAREPOINT_FOLDER")    # Ej: "" para raíz o "Austral"

# 1. Obtener token de acceso (OAuth 2.0 client_credentials)
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# 2. Obtener site_id
def get_site_id(token):
    from urllib.parse import urlparse

    parsed = urlparse(SHAREPOINT_SITE)
    hostname = parsed.hostname  # milton02.sharepoint.com
    site_path = parsed.path.lstrip("/")  # sites/Mantenimiento
    url = f"https://graph.microsoft.com/v1.0/sites/{hostname}:/{site_path}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

# 3. Obtener drive_id
def get_drive_id(token, site_id):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    drives = response.json()["value"]

    print("\n📦 Drives disponibles en el sitio:")
    for d in drives:
        print(f"- {d['name']} (ID: {d['id']})")

    # Intenta encontrar el drive que coincida
    for drive in drives:
        if drive["name"].lower() == DRIVE_NAME.lower():
            return drive["id"]
    
    raise ValueError(f"No se encontró el drive con nombre: {DRIVE_NAME}")


# 4. Listar archivos en la carpeta
def list_files(token, drive_id):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{FOLDER_PATH}:/children" if FOLDER_PATH else f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json().get("value", [])
    if not items:
        print("📂 La carpeta está vacía.")
    for item in items:
        print(f"- {item['name']} ({'📁' if 'folder' in item else '📄'})")

# 5. Ejecutar prueba
if __name__ == "__main__":
    try:
        print("🔐 Autenticando...")
        token = get_access_token()
        print("✅ Token obtenido")

        print("🌐 Obteniendo site ID...")
        site_id = get_site_id(token)
        print(f"✅ site_id: {site_id}")

        print("📁 Obteniendo drive ID...")
        drive_id = get_drive_id(token, site_id)
        print(f"✅ drive_id: {drive_id}")

        print("📄 Listando archivos:")
        list_files(token, drive_id)

    except Exception as e:
        print("❌ Error:", str(e))

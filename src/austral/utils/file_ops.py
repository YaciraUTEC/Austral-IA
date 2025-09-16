import os

def json_ya_existe(ruta_json: str) -> bool:
    return os.path.isfile(ruta_json)

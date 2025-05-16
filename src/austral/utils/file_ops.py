import os

def json_ya_existe(output_path: str) -> bool:
    return os.path.exists(output_path)

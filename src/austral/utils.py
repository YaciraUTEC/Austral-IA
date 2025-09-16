import os
import hashlib

def generar_nombre_corto(nombre_largo: str, ruta_base: str = "", max_length: int = 240) -> str:
    """
    Genera un nombre corto solo si la ruta completa excede el límite.
    Args:
        nombre_largo: Nombre del archivo
        ruta_base: Ruta donde se guardará el archivo
        max_length: Longitud máxima permitida (240 para Windows)
    """
    ruta_completa = os.path.join(ruta_base, nombre_largo) if ruta_base else nombre_largo
    if len(ruta_completa) <= max_length:
        return nombre_largo

    nombre_base, ext = os.path.splitext(nombre_largo)
    hash_parte = hashlib.md5(nombre_base.encode()).hexdigest()[:8]
    
    # Calcular espacio disponible considerando la ruta base
    espacio_disponible = max_length - len(ruta_base) - len(ext) - len(hash_parte) - 2
    mitad = max(1, espacio_disponible // 2)
    nombre_corto = f"{nombre_base[:mitad]}_{hash_parte}{ext}"

    return nombre_corto

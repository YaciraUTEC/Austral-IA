import os
from io import BytesIO
from austral.extractor.fragmenter_pdf import fragmentar_pdf_memoria
from austral.extractor.fragmenter_excel import fragmentar_excel_memoria

def fragmentar_documento_memoria(nombre_archivo: str, contenido_bytes: bytes, output_dir: str=None) -> list:
    ext = os.path.splitext(nombre_archivo)[1].lower()
    archivo_en_memoria = BytesIO(contenido_bytes)

    if ext == ".pdf":
        if not output_dir:
            raise ValueError("Se requiere 'output_dir' para fragmentar PDF.")
        return fragmentar_pdf_memoria(archivo_en_memoria, nombre_archivo, output_dir)

    elif ext in [".xlsx", ".xls"]:
        return fragmentar_excel_memoria(archivo_en_memoria, nombre_archivo)

    else:
        raise ValueError(f"Extensión no soportada: {ext}")

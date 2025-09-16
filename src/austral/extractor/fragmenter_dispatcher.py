import os
from io import BytesIO
from austral.extractor.fragmenter_pdf import fragmentar_pdf_memoria
from austral.extractor.fragmenter_excel import fragmentar_excel_memoria
from austral.sharepoint_conector import convertir_word_a_pdf, obtener_token

def fragmentar_documento_memoria(nombre_archivo: str, contenido_bytes: bytes, output_dir: str=None, drive_id:  str =None, item_id: str = None) -> list:
    ext = os.path.splitext(nombre_archivo)[1].lower()
    archivo_en_memoria = BytesIO(contenido_bytes)

    if ext == ".pdf":
        if not output_dir:
            raise ValueError("Se requiere 'output_dir' para fragmentar PDF.")
        return fragmentar_pdf_memoria(archivo_en_memoria, nombre_archivo, output_dir)

    elif ext in [".xlsx", ".xls"]:
        return fragmentar_excel_memoria(archivo_en_memoria, nombre_archivo)

    elif ext in [".docx", ".doc"]:
        if not drive_id or not item_id:
            raise ValueError("Se requieren 'drive_id' e 'item_id' para convertir Word a PDF.")
        
        # Convertir Word a PDF
        print(f"🔄 Convirtiendo {nombre_archivo} a PDF...")
        token = obtener_token()  # Obtener el token de autenticación
        contenido_pdf = convertir_word_a_pdf(token, drive_id, item_id)
        
        # Actualizar el nombre del archivo a .pdf
        nombre_pdf = nombre_archivo.rsplit(".", 1)[0] + ".pdf"
        
        # Fragmentar el PDF resultante
        archivo_pdf_en_memoria = BytesIO(contenido_pdf)
        if not output_dir:
            raise ValueError("Se requiere 'output_dir' para fragmentar el PDF convertido.")
        return fragmentar_pdf_memoria(archivo_pdf_en_memoria, nombre_pdf, output_dir)

    else:
        raise ValueError(f"Extensión no soportada: {ext}")
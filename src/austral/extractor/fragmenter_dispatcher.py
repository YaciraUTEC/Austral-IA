import os

from austral.extractor.fragmenter_pdf import fragmentar_pdf
from austral.extractor.fragmenter_excel import fragmentar_excel
def fragmentar_documento(path_archivo: str, output_dir: str = None) -> list:
    ext = os.path.splitext(path_archivo)[1].lower()

    if ext == ".pdf":
        if not output_dir:
            raise ValueError("Se requiere 'output_dir' para fragmentar PDF.")
        return fragmentar_pdf(path_archivo, output_dir)

    elif ext in [".xlsx", ".xls"]:
        return fragmentar_excel(path_archivo)

    else:
        raise ValueError(f"Extensión no soportada: {ext}")

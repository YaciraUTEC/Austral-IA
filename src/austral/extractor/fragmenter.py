import os
from PyPDF2 import PdfReader, PdfWriter

def fragmentar_pdf(path_pdf: str, output_dir: str, max_paginas: int = 50) -> list:
    """
    Divide un PDF en fragmentos de hasta `max_paginas` páginas.
    Devuelve una lista de metadatos de fragmento.

    Parámetros:
    - path_pdf: ruta del archivo PDF original.
    - output_dir: carpeta donde guardar los fragmentos.
    - max_paginas: máximo de páginas por fragmento (por defecto 50).

    Retorna:
    - lista de diccionarios con metadatos de cada fragmento.
    """
    reader = PdfReader(path_pdf)
    total_paginas = len(reader.pages)
    fragmentos = []

    document_id = os.path.basename(path_pdf).replace(".pdf", "")

    if total_paginas <= max_paginas:
        # Documento pequeño: único fragmento sin crear nuevo archivo
        fragment_id = document_id
        fragment_path = path_pdf
        fragmentos.append({
            "document_id": document_id,
            "fragment_id": fragment_id,
            "fragment_path": fragment_path,
            "page_range": f"1-{total_paginas}",
            "status": "complete"
        })
        return fragmentos

    for i in range(0, total_paginas, max_paginas):
        writer = PdfWriter()
        for j in range(i, min(i + max_paginas, total_paginas)):
            writer.add_page(reader.pages[j])

        fragment_id = f"{document_id}_p{i+1}_{min(i+max_paginas, total_paginas)}"
        fragment_path = os.path.join(output_dir, f"{fragment_id}.pdf")

        os.makedirs(output_dir, exist_ok=True)
        with open(fragment_path, "wb") as f:
            writer.write(f)

        fragmentos.append({
            "document_id": document_id,
            "fragment_id": fragment_id,
            "fragment_path": fragment_path,
            "page_range": f"{i+1}-{min(i+max_paginas, total_paginas)}",
            "status": "fragmented"
        })

    return fragmentos

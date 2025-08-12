from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
import os

def fragmentar_pdf_memoria(pdf_bytes: BytesIO, nombre_archivo: str, output_dir: str, max_paginas: int = 10) -> list:
    """
    Fragmenta un archivo PDF recibido como bytes en fragmentos de hasta max_paginas.
    Guarda los fragmentos como archivos temporales en output_dir.
    """
    reader = PdfReader(pdf_bytes)
    total_paginas = len(reader.pages)
    fragmentos = []

    document_id = os.path.splitext(nombre_archivo)[0]  # Ej: reporte_mensual.pdf -> reporte_mensual

    if total_paginas <= max_paginas:
        # No se fragmenta, se guarda como un solo archivo temporal
        fragment_path = os.path.join(output_dir, f"{document_id}.pdf")
        with open(fragment_path, "wb") as f:
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.write(f)

        fragmentos.append({
            "document_id": document_id,
            "fragment_id": document_id,
            "fragment_path": fragment_path,
            "page_range": f"1-{total_paginas}",
            "status": "complete"
        })
        return fragmentos

    # Fragmentación en trozos de max_paginas
    os.makedirs(output_dir, exist_ok=True)
    for i in range(0, total_paginas, max_paginas):
        writer = PdfWriter()
        for j in range(i, min(i + max_paginas, total_paginas)):
            writer.add_page(reader.pages[j])

        fragment_id = f"{document_id}_p{i+1}_{min(i+max_paginas, total_paginas)}"
        fragment_path = os.path.join(output_dir, f"{fragment_id}.pdf")
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

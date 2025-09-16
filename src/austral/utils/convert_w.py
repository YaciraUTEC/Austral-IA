import subprocess
import os

def convertir_docx_a_pdf_libreoffice(input_path: str, output_dir: str):

    soffice_path = r"C:\Program Files\LibreOffice\program\soffice.com"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cmd = [
        soffice_path,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ]

    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        print("Error al convertir:", resultado.stderr)
        raise RuntimeError("Fallo en conversión LibreOffice")
    else:
        print(f"Archivo convertido exitosamente: {input_path} → {output_dir}")

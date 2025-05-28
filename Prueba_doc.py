import subprocess
import os

def convertir_docx_a_pdf_libreoffice(input_path: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cmd = [
        "C:\Program Files\LibreOffice\program\soffice.com",  # Asegúrate que LibreOffice esté en PATH; si no, pon ruta completa aquí
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
        print(f"Archivo convertido: {input_path} → {output_dir}")

if __name__ == "__main__":
    input_docx = "C:/Users/Nicol/Documentos/Austral/Doc/Word/INFORME DE TRABAJO DE MONTAJE LINEA RSW.docx" # Cambia esta ruta a tu archivo
    output_folder = "temp_pdf"              # Carpeta donde guardarás el PDF convertido
    convertir_docx_a_pdf_libreoffice(input_docx, output_folder)

import subprocess
import os

def convertir_docx_a_pdf_libreoffice(input_path: str, output_dir: str):
    soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
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

# Uso de ejemplo
if __name__ == "__main__":
    input_docx = r"C:/Users/Nicol/Documentos/Austral/Doc/Word/INFORME DE TRABAJO DE MONTAJE LINEA RSW.docx"  # Cambia a la ruta real
    output_folder = "temp_pdf"
    convertir_docx_a_pdf_libreoffice(input_docx, output_folder)

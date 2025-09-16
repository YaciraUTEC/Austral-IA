import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet._reader")

from io import BytesIO
import pandas as pd
import numpy as np
import openpyxl
import xlrd
from typing import List, Dict
import os
import json
import hashlib
from austral.utils import generar_nombre_corto

def obtener_hojas_visibles_bytesio(excel_bytes: BytesIO) -> List[str]:
    """Devuelve solo las hojas visibles del archivo Excel en memoria."""
    wb = openpyxl.load_workbook(excel_bytes, read_only=True, data_only=True)
    return [ws.title for ws in wb.worksheets if ws.sheet_state == "visible"]

def fila_a_frase_semantica(fila: List[str], encabezados: List[str]) -> str:
    """Convierte una fila en una oración clave:valor, ignorando vacíos."""
    partes = []
    for i, valor in enumerate(fila):
        valor = valor.strip()
        if valor and i < len(encabezados):
            clave = encabezados[i].strip().capitalize() or f"Columna {i+1}"
            partes.append(f"{clave}: {valor}")
    return ". ".join(partes)

def analizar_rango_filas(df_rango: pd.DataFrame, fila_inicio: int, fila_fin: int) -> List[Dict]:
    """Convierte un rango de filas en frases semánticas por fila."""
    contenido = []
    encabezados = None

    for _, fila in df_rango.iterrows():
        fila_limpia = [str(cell).strip() for cell in fila]
        if any(fila_limpia):
            encabezados = fila_limpia
            break

    if encabezados is None:
        encabezados = [f"Columna {i+1}" for i in range(df_rango.shape[1])]

    for i, (_, fila) in zip(range(fila_inicio, fila_fin), df_rango.iterrows()):
        fila_limpia = [str(cell).strip() for cell in fila]
        if not any(fila_limpia):
            continue
        frase = fila_a_frase_semantica(fila_limpia, encabezados)
        if frase:
            contenido.append({
                "tipo": "texto",
                "contenido": frase,
                "posicion": f"Fila {i+1}"
            })

    return contenido

def limpiar_nan(valor):
    """Convierte NaN y otros valores problemáticos a string vacío para JSON."""
    if pd.isna(valor) or (isinstance(valor, float) and np.isnan(valor)):
        return ""
    return str(valor) if not isinstance(valor, bool) else valor

def limpiar_nombre_columna(nombre, extension):
    """Limpia y simplifica nombres de columnas según la extensión."""
    if pd.isna(nombre) or isinstance(nombre, float):
        return ""
    nombre = str(nombre).strip()
    
    # Para archivos .xls usar números directos
    if extension == ".xls":
        if nombre.startswith("Unnamed:"):
            return nombre.split(":")[1].strip()
        try:
            # Intentar convertir a índice numérico
            return str(int(nombre)) if nombre.isdigit() else nombre
        except:
            return nombre
    
    # Para archivos .xlsx usar prefijo columna_
    else:
        if nombre.startswith("Unnamed:"):
            return f"columna_{nombre.split(':')[1].strip()}"
        return nombre

def fragmentar_excel_memoria(excel_bytes: BytesIO, nombre_archivo: str, filas_por_fragmento: int = 100) -> list:
    """
    Fragmenta un archivo Excel (.xls o .xlsx) en memoria.
    """
    document_id = os.path.splitext(nombre_archivo)[0]
    fragmentos = []
    extension = os.path.splitext(nombre_archivo)[1].lower()

    try:
        excel_bytes.seek(0)
        if extension == ".xls":
            workbook = xlrd.open_workbook(file_contents=excel_bytes.getvalue())
            for sheet_name in workbook.sheet_names():
                sheet = workbook.sheet_by_name(sheet_name)
                data = [[sheet.cell_value(row, col) for col in range(sheet.ncols)] for row in range(sheet.nrows)]
                df = pd.DataFrame(data)
                # Usar índices numéricos para .xls
                df.columns = [str(i) for i in range(len(df.columns))]
        else:  # .xlsx
            excel_file = pd.ExcelFile(excel_bytes, engine="openpyxl")
            df = pd.read_excel(excel_file, sheet_name=None)

        for sheet_name, df_sheet in (df.items() if isinstance(df, dict) else [(sheet_name, df)]):
            # Limpiar nombres de columnas según extensión
            df_sheet.columns = [limpiar_nombre_columna(col, extension) for col in df_sheet.columns]
            
            # Convertir DataFrame a diccionario y limpiar NaN
            records = df_sheet.to_dict(orient='records')
            cleaned_records = []
            for record in records:
                cleaned_record = {k: limpiar_nan(v) for k, v in record.items() if k}
                cleaned_records.append(cleaned_record)

            fragment_id = f"{document_id}_{sheet_name}"
            fragmentos.append({
                "document_id": document_id,
                "fragment_id": fragment_id,
                "sheet_name": sheet_name,
                "content": cleaned_records,
                "status": "complete"
            })
    except Exception as e:
        print(f"❌ Error procesando Excel: {str(e)}")
        return []

    return fragmentos

def guardar_fragmentos_excel(fragmentos: list, output_dir: str):
    """Guarda los fragmentos de Excel en archivos JSON."""
    for fragmento in fragmentos:
        fragment_id = fragmento["fragment_id"]
        nombre_archivo = generar_nombre_corto(
            f"{fragment_id}.json",
            ruta_base=output_dir
        )
        output_path = os.path.join(output_dir, nombre_archivo)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fragmento["content"], f, ensure_ascii=False, indent=2)
    mitad = chars_disponibles // 2
    nombre_corto = f"{nombre_base[:mitad]}_{hash_parte}{ext}"
    
    return nombre_corto

def guardar_fragmentos_excel(fragmentos: list, output_dir: str):
    """Guarda los fragmentos de Excel en archivos JSON."""
    for fragmento in fragmentos:
        fragment_id = fragmento["fragment_id"]
        # Acortar nombre si es necesario
        nombre_archivo = generar_nombre_corto(f"{fragment_id}.json")
        output_path = os.path.join(output_dir, nombre_archivo)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fragmento["content"], f, ensure_ascii=False, indent=2)

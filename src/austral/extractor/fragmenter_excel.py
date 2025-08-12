from io import BytesIO
import pandas as pd
import openpyxl
from typing import List, Dict
import os

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

def fragmentar_excel_memoria(excel_bytes: BytesIO, nombre_archivo: str, filas_por_fragmento: int = 100) -> List[Dict]:
    """Fragmenta un archivo Excel en memoria, retornando su contenido como lista de fragmentos."""
    document_id = os.path.splitext(nombre_archivo)[0]
    fragmentos = []

    try:
        # Reset de puntero por si otro lector consumió parte del stream
        excel_bytes.seek(0)
        xls = pd.ExcelFile(excel_bytes, engine="openpyxl")
        excel_bytes.seek(0)
        hojas_visibles = obtener_hojas_visibles_bytesio(excel_bytes)
    except Exception as e:
        print(f"❌ Error al leer el Excel: {e}")
        return []

    for sheet_name in hojas_visibles:
        try:
            df = xls.parse(sheet_name, header=None, dtype=str).fillna("")
        except Exception as e:
            print(f"⚠️ Error al procesar hoja '{sheet_name}': {e}")
            continue

        total_filas = df.shape[0]

        if total_filas <= 200:
            contenido = analizar_rango_filas(df, 0, total_filas)
            fragmentos.append({
                "document_id": document_id,
                "fragment_id": f"{document_id}_{sheet_name}",
                "sheet_name": sheet_name,
                "contenido": contenido,
                "estructura": "frases",
                "status": "complete"
            })
        else:
            for i in range(0, total_filas, filas_por_fragmento):
                fin = min(i + filas_por_fragmento, total_filas)
                df_fragmento = df.iloc[i:fin]
                contenido = analizar_rango_filas(df_fragmento, i, fin)
                fragmentos.append({
                    "document_id": document_id,
                    "fragment_id": f"{document_id}_{sheet_name}_r{i+1}_{fin}",
                    "sheet_name": sheet_name,
                    "contenido": contenido,
                    "estructura": "frases",
                    "status": "fragmented"
                })

    return fragmentos

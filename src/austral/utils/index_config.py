# src/austral/utils/index_config.py
import faiss
import numpy as np

def get_faiss_index_type(vectors: np.ndarray):
    """
    Devuelve un índice FAISS adecuado dependiendo del número de vectores.
    - Si son pocos, usa IndexFlatIP (búsqueda exacta).
    - Si son muchos, usa IndexIVFFlat (más rápido, pero necesita entrenamiento).
    """
    d = vectors.shape[1]
    n = vectors.shape[0]

    if n < 300:
        return faiss.IndexFlatIP(d)
    else:
        nlist = 100  # número de clusters
        quantizer = faiss.IndexFlatIP(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
        index.train(vectors)
        return index

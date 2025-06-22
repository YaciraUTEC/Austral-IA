import multiprocessing
import subprocess

def correr_indexador_pdf():
    subprocess.run(["python", "src/austral/search_indexer_f_pdf.py"], check=True)

def correr_indexador_excel():
    subprocess.run(["python", "src/austral/search_indexer_f_excel.py"], check=True)

if __name__ == "__main__":
    print("🔁 Iniciando indexación paralela de PDF y Excel...")
    
    proceso_pdf = multiprocessing.Process(target=correr_indexador_pdf)
    proceso_excel = multiprocessing.Process(target=correr_indexador_excel)

    proceso_pdf.start()
    proceso_excel.start()

    proceso_pdf.join()
    proceso_excel.join()

    print("✅ Ambos índices FAISS generados correctamente.")

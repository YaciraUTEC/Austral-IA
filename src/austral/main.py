from austral.process_manager import run as run_process_manager
from austral.search_indexer import indexar_todos_fragmentos

def main():
    print("Iniciando procesamiento de PDFs...")
    run_process_manager()
    print("Procesamiento finalizado.")

    print("Iniciando indexación en Azure Cognitive Search...")
    indexar_todos_fragmentos("output/fragmentos/fragmentos_metadata.json")
    print("Indexación finalizada.")

if __name__ == "__main__":
    main()

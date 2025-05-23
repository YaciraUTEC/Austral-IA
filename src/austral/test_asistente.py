
# src/austral/tests/test_asistente.py
import sys
import os

OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../output/extractos_json"))
from austral.services.asistente import buscar_fragmentos

def main():
    pregunta = "cuantos tubos tiene un rotatubos"
    fragmentos = buscar_fragmentos(pregunta)
    print("Fragmentos encontrados:")
    for f in fragmentos:
        print(f)

if __name__ == "__main__":
    main()
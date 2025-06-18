import json
import math
import random
import os   # <-- AÑADIR IMPORT

# Cargar el archivo JSON
def Convertidor():
    BASE_DIR = os.path.dirname(__file__)
    with open(BASE_DIR + "/grafo_sin_cruce.json", "r") as f:
        data = json.load(f)

    grafo = data["grafo"]
    coords = data["coordenadas"]
    inicio = data["inicio"]
    meta = data["meta"]

    # Si inicio o meta son null, seleccionar aleatoriamente
    if inicio is None or meta is None:
        nodos = list(grafo.keys())
        inicio, meta = random.sample(nodos, 2)
        data["inicio"] = inicio
        data["meta"] = meta

    # Archivo principal
    with open("logica/datos_completos.txt", "w") as out:
        out.write("# Grafo\n")
        for nodo, vecinos in grafo.items():
            linea = f"{nodo}: "
            conexiones = []
            for vecino in vecinos:
                x1, y1 = coords[nodo]
                x2, y2 = coords[vecino]
                dist = round(math.dist([x1, y1], [x2, y2]))
                conexiones.append(f"{vecino}:{dist}")
            linea += ", ".join(conexiones) + "\n"
            out.write(linea)

        out.write("\n# Coordenadas\n")
        for nodo, (x, y) in coords.items():
            out.write(f"{nodo} = ({x}, {y})\n")

        out.write("\n# Inicio y Meta\n")
        out.write(f"Inicio = {inicio}\n")
        out.write(f"Meta = {meta}\n")

    # Segundo archivo: solo conexiones tipo diccionario
    with open("logica/grafo.txt", "w") as out2:
        for nodo, vecinos in grafo.items():
            conexiones = ", ".join(vecinos)
            out2.write(f"\"{nodo}\": [{conexiones}]\n")

        out2.write(f"\ninicio={inicio}\n")
        out2.write(f"meta={meta}\n")

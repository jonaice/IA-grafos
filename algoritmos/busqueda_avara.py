import math
import os

def leer_todo_del_archivo_Avara(ruta):
    grafo = {}
    coordenadas = {}
    nodo_inicio = None
    nodo_meta = None

    leyendo = None

    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                if "grafo" in linea.lower():
                    leyendo = "grafo"
                elif "coordenadas" in linea.lower():
                    leyendo = "coordenadas"
                elif "inicio" in linea.lower() or "meta" in linea.lower():
                    leyendo = "otros"
                continue

            if leyendo == "grafo":
                nodo, hijos = linea.split(':', 1)
                nodo = nodo.strip()
                hijos = hijos.strip().strip('[]').replace(' ', '')
                lista_hijos = []
                if hijos:
                    for hijo_peso in hijos.split(','):
                        hijo, peso = hijo_peso.split(':')
                        hijo = hijo.strip()
                        peso = int(peso.strip())
                        lista_hijos.append((hijo, peso))
                        # Agregar arco inverso automáticamente
                        if hijo not in grafo:
                            grafo[hijo] = []
                        grafo[hijo].append((nodo, peso))
                if nodo not in grafo:
                    grafo[nodo] = []
                grafo[nodo].extend(lista_hijos)

            elif leyendo == "coordenadas":
                nodo, coord = linea.split('=')
                x, y = coord.strip('() ').split(',')
                coordenadas[nodo.strip()] = (float(x), float(y))

            elif leyendo == "otros":
                if "inicio" in linea.lower():
                    _, nodo_inicio = linea.split('=')
                    nodo_inicio = nodo_inicio.strip()
                elif "meta" in linea.lower():
                    _, nodo_meta = linea.split('=')
                    nodo_meta = nodo_meta.strip()

    return grafo, coordenadas, nodo_inicio, nodo_meta


def calcular_heuristica(coordenadas, objetivo):
    heuristica = {}
    x_goal, y_goal = coordenadas[objetivo]
    for nodo, (x, y) in coordenadas.items():
        heuristica[nodo] = math.sqrt((x - x_goal) ** 2 + (y - y_goal) ** 2)
    return heuristica


def busqueda_avara_con_costos(grafo, heuristica, nodo_inicio, nodo_meta):
    nodos = [nodo_inicio]
    padres = {nodo_inicio: None}
    visitados = set()
    costo_total = {nodo_inicio: 0}

    while nodos:
        nodo = nodos.pop(0)

        if nodo == nodo_meta:
            camino = []
            actual = nodo_meta
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino, costo_total[nodo_meta]

        visitados.add(nodo)

        hijos = []
        for hijo, peso in grafo.get(nodo, []):
            if hijo not in visitados and hijo not in nodos:
                padres[hijo] = nodo
                costo_total[hijo] = costo_total[nodo] + peso
                hijos.append(hijo)

        hijos.sort(key=lambda x: heuristica[x])

        for hijo in hijos:
            i = 0
            while i < len(nodos) and heuristica[hijo] >= heuristica[nodos[i]]:
                i += 1
            nodos.insert(i, hijo)

    return None, None


def ejecutar_busqueda_avara_desde_archivo(ruta_archivo):
    grafo, coordenadas, nodo_inicio, nodo_meta = leer_todo_del_archivo_Avara(ruta_archivo)
    heuristica = calcular_heuristica(coordenadas, nodo_meta)
    camino, costo = busqueda_avara_con_costos(grafo, heuristica, nodo_inicio, nodo_meta)
    return camino, costo


# MAIN de prueba
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    ruta_archivo = os.path.abspath(os.path.join(BASE_DIR, "..", "logica", "datos_completos.txt"))
    camino, costo = ejecutar_busqueda_avara_desde_archivo(ruta_archivo)

    if camino:
        print("Camino encontrado:", camino)
        print("Costo total:", costo)
    else:
        print("No se encontró un camino.")

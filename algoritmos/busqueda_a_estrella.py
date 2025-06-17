import math
import os

def leer_todo_del_archivo_A_estrella(ruta):
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
        heuristica[nodo] = math.sqrt((x - x_goal)**2 + (y - y_goal)**2)
    return heuristica


def busqueda_a_estrella(grafo, heuristica, nodo_inicio, nodo_meta):
    nodos = [(nodo_inicio, 0)]
    padres = {nodo_inicio: None}
    costos = {nodo_inicio: 0}
    visitados = set()

    while nodos:
        nodos.sort(key=lambda x: costos[x[0]] + heuristica[x[0]])
        nodo, _ = nodos.pop(0)

        if nodo in visitados:
            continue

        visitados.add(nodo)

        if nodo == nodo_meta:
            camino = []
            actual = nodo
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino, costos[nodo]

        for hijo, peso in grafo.get(nodo, []):
            nuevo_costo = costos[nodo] + peso
            if (hijo not in costos or nuevo_costo < costos[hijo]) and hijo not in visitados:
                costos[hijo] = nuevo_costo
                padres[hijo] = nodo
                nodos.append((hijo, nuevo_costo))

    return None, None


def ejecutar_a_estrella_desde_archivo(ruta_archivo):
    grafo, coordenadas, nodo_inicio, nodo_meta = leer_todo_del_archivo_A_estrella(ruta_archivo)
    heuristica = calcular_heuristica(coordenadas, nodo_meta)
    camino, costo = busqueda_a_estrella(grafo, heuristica, nodo_inicio, nodo_meta)
    return camino, costo


# MAIN de prueba
if __name__ == "__main__":

    BASE_DIR = os.path.dirname(__file__)
    ruta_archivo = os.path.abspath(os.path.join(BASE_DIR, "..", "logica", "datos_completos.txt"))
    camino, costo = ejecutar_a_estrella_desde_archivo(ruta_archivo)

    if camino:
        print("Camino encontrado:", camino)
        print(f"Costo total: {costo}")
    else:
        print("No se encontró un camino.")

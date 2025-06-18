import os

def leer_grafo_desde_archivo(ruta):
    grafo = {}
    nodo_inicio = None
    nodo_meta = None
    with open(ruta, 'r') as archivo:
        for linea in archivo:
            if linea.strip():
                if linea.lower().startswith("inicio"):
                    nodo_inicio = linea.split('=')[1].strip()
                    continue
                elif linea.lower().startswith("meta"):
                    nodo_meta = linea.split('=')[1].strip()
                    continue
                nodo, hijos = linea.strip().split(':')
                nodo = nodo.strip().replace('"', '')
                hijos = hijos.strip().strip('[]').replace(' ', '')
                lista_hijos = hijos.split(',') if hijos else []
                grafo[nodo] = lista_hijos
                for hijo in lista_hijos:
                    hijo = hijo.strip()
                    if hijo not in grafo:
                        grafo[hijo] = []
                    if nodo not in grafo[hijo]:
                        grafo[hijo].append(nodo)
    return grafo, nodo_inicio, nodo_meta

def leer_grafo_desde_archivo_ORIGINAL(ruta):
    grafo = {}
    with open(ruta, 'r') as archivo:
        for linea in archivo:
            if linea.strip():  # Evita líneas vacías
                nodo, hijos = linea.strip().split(':')
                nodo = nodo.strip().replace('"', '')
                hijos = hijos.strip().strip('[]').replace(' ', '')
                lista_hijos = hijos.split(',') if hijos else []
                grafo[nodo] = lista_hijos
    return grafo

def busquedaProfundidadLimitada(grafo, nodo_inicio, nodo_meta, profundidad_maxima):
    nodos = [(nodo_inicio, 0)]  # pila: (nodo, profundidad)
    padres = {nodo_inicio: None}

    while nodos:
        print("Nodos: ", nodos)
        nodo, profundidad = nodos.pop()
        print(f"Nodo: {nodo}, Profundidad: {profundidad}")

        if nodo == nodo_meta:
            # Construir camino
            camino = []
            actual = nodo_meta
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino

        if profundidad < profundidad_maxima:
            for hijo in reversed(grafo.get(nodo, [])):
                print("hijo:", hijo)
                if padres[nodo] is not None and hijo == padres[nodo]:
                    continue  # Saltar al padre
                if hijo not in padres:
                    padres[hijo] = nodo
                    nodos.append((hijo, profundidad + 1))

    return None  # No se encontró el nodo meta

def busquedaProfundizacionIterativa(grafo, nodo_inicio, nodo_meta, profundidad_maxima_max):
    for limite in range(profundidad_maxima_max + 1):
        print(f"\n👉 Buscando con límite de profundidad: {limite}")
        camino = busquedaProfundidadLimitada(grafo, nodo_inicio, nodo_meta, limite)
        if camino is not None:
            return camino
    return None  # No se encontró el nodo meta en ninguna profundidad

# MAIN
def ProfundidadI():
    BASE_DIR = os.path.dirname(__file__)
    ruta_archivo = os.path.abspath(os.path.join(BASE_DIR, "..", "logica", "grafo.txt"))
    grafo, nodo_inicio, nodo_meta = leer_grafo_desde_archivo(ruta_archivo)
    print("Grafo:", grafo)

    camino = busquedaProfundizacionIterativa(grafo, nodo_inicio, nodo_meta, 10)
    if camino:
        print("Camino encontrado:", camino)
    else:
        print("No se encontró un camino.")
    return camino
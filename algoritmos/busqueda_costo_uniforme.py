import os

def leer_todo_del_archivo_Costo_uniforme(ruta):
    grafo = {}
    nodo_inicio = None
    nodo_meta = None
    leyendo = None

    with open(ruta, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                if "grafo" in linea.lower():
                    leyendo = "grafo"
                elif "inicio" in linea.lower() or "meta" in linea.lower():
                    leyendo = "otros"
                continue

            if leyendo == "grafo":
                if ':' not in linea:
                    continue  # evita errores por líneas mal formateadas
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

            elif leyendo == "otros":
                if "inicio" in linea.lower():
                    _, nodo_inicio = linea.split('=')
                    nodo_inicio = nodo_inicio.strip()
                elif "meta" in linea.lower():
                    _, nodo_meta = linea.split('=')
                    nodo_meta = nodo_meta.strip()

    return grafo, nodo_inicio, nodo_meta


def busqueda_costo_uniforme(grafo, nodo_inicio, nodo_meta):
    nodos = [(nodo_inicio, 0)]  # (nodo, costo acumulado)
    padres = {nodo_inicio: None}
    costos = {nodo_inicio: 0}
    visitados = set()

    while nodos:
        nodos.sort(key=lambda x: x[1])
        nodo, costo_actual = nodos.pop(0)

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
            nuevo_costo = costo_actual + peso
            if hijo not in costos or nuevo_costo < costos[hijo]:
                costos[hijo] = nuevo_costo
                padres[hijo] = nodo
                if hijo not in visitados:
                    nodos.append((hijo, nuevo_costo))

    return None, None


def ejecutar_busqueda_costo_uniforme_desde_archivo(ruta_archivo):
    grafo, nodo_inicio, nodo_meta = leer_todo_del_archivo_Costo_uniforme(ruta_archivo)
    return busqueda_costo_uniforme(grafo, nodo_inicio, nodo_meta)


# MAIN de prueba
def Uniforme():
    BASE_DIR = os.path.dirname(__file__)
    ruta_archivo = os.path.abspath(os.path.join(BASE_DIR, "..", "logica", "datos_completos.txt"))
    camino, costo = ejecutar_busqueda_costo_uniforme_desde_archivo(ruta_archivo)
    if camino:
        print("Camino encontrado:", camino)
        print("Costo total del camino:", costo)
    else:
        print("No se encontró un camino.")
    return camino


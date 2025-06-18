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
                # Elimina comillas y espacios
                nodo, hijos = linea.strip().split(':')
                nodo = nodo.strip().replace('"', '')
                hijos = hijos.strip().strip('[]').replace(' ', '')
                lista_hijos = hijos.split(',') if hijos else []
                grafo[nodo] = lista_hijos
    return grafo


def busquedaProfundidad(grafo, nodo_inicio, nodo_meta):
    nodos = [nodo_inicio] #Lo vamos a trabajar como una cola
    padres = {nodo_inicio: None}  # Guarda de dónde viene cada nodo

    while nodos:
        print("Nodos: ", nodos);
        nodo = nodos.pop(0)
        print("Nodo: ", nodo)
        if nodo == nodo_meta:
            # Construir camino
            camino = []
            actual = nodo_meta
            while actual is not None:
                camino.insert(0, actual)
                actual = padres[actual]
            return camino
        
        #Expandir
        for hijo in reversed(grafo.get(nodo, [])):
            print("hijo:", hijo)
            if padres[nodo] is not None and hijo == padres[nodo]:
                continue  # Saltar al padre
            else:
                if hijo not in padres:  # Si no fue visitado ni en cola (porque solo entra a padres si ya fue agregado)
                    padres[hijo] = nodo
                    nodos.insert(0,hijo)
       
                
    return None  # No se encontró el nodo meta

#Main
def Profundidad():
    BASE_DIR = os.path.dirname(__file__)
    ruta_archivo = os.path.abspath(os.path.join(BASE_DIR, "..", "logica", "grafo.txt"))
    grafo, nodo_inicio, nodo_meta = leer_grafo_desde_archivo(ruta_archivo)
    print("grafo", grafo)
    print("grafo A", grafo.get("A",[]))
    camino = busquedaProfundidad(grafo, nodo_inicio, nodo_meta)
    if camino:
        print("Camino encontrado:", camino)
    else:
        print("No se encontró un camino.")
    return camino

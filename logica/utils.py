#author: AlfredoHJDLO

def cargar_coordenadas(ruta_archivo="logica/datos_completos.txt"):
    """
    Lee el archivo de datos completos y extrae únicamente la sección de coordenadas

    Args: 
        ruta_archivo (str): La ruta al archivo datos_completos.txt

    Return: 
        dict: Un diccionario, donde las llaves son los nombres de los nodos (str)
                y los valores son tuplas con sus coordenadas (int, int)
                Ej: {'Robot': (255,359), 'X0_0': (577,216), ...}
    """
    coordenadas = {}
    try:
        with open(ruta_archivo, 'r') as f:
            leyendo_seccion_coords = False

            for linea in f:
                linea = linea.strip()
                if "# Coordenadas" in linea:
                    leyendo_seccion_coords = True
                    continue
                if leyendo_seccion_coords and linea.startswith('#'):
                    break
                if leyendo_seccion_coords and '=' in linea:
                    nombre_nodo, coords_str = linea.split('=', 1)
                    nombre_nodo = nombre_nodo.strip()
                    corods_sin_parentesis = coords_str.strip().strip('()')
                    partes = corods_sin_parentesis.split(',')
                    if len(partes) == 2:
                        x_val = int(partes[0].strip())
                        y_val = int(partes[1].strip())
                        coordenadas[nombre_nodo] = (x_val, y_val)
    except FileNotFoundError:
        print(f"Error, no se pudo encontra el archivo en la ruta: {ruta_archivo}")
        return None
    return coordenadas

def traducir_camino_a_coordenadas(camino_ids, todas_las_cords, offset):
    """
    Convierte una lista de IDs de nodos de un camino a una lista de coordenadas
    de pantalla, aplicando un desfase.

    Args:
        camino_ids (list): Una lista de strings con los IDs de los nodos.
                           Ej: ['Robot', 'X1_0', 'X0_0', 'Bandera']
        todas_las_coords (dict): El diccionario generado por cargar_coordenadas.
        offset (tuple): Una tupla (x, y) con el desfase a aplicar. Ej: (60, 120)

    Returns:
        list: Una lista de tuplas con las coordenadas listas para dibujar en pantalla.
    """
    coordenatas_camino = []
    if not camino_ids or not todas_las_cords:
        return []
    offset_x, offset_y = offset
    for nodo_id in camino_ids:
        if nodo_id in todas_las_cords:
            local_x, local_y = todas_las_cords[nodo_id]
            screen_x = local_x + offset_x
            screen_y = local_y + offset_y

            coordenatas_camino.append((screen_x, screen_y))
        else:
            print(f"Advertencia: El nodo '{nodo_id}' del camino no tiene coordenadas.")
    return coordenatas_camino
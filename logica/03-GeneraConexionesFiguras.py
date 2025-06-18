# logica/03-GeneraConexionesFiguras.py

import json
import networkx as nx
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union # <--- AÑADIR ESTA IMPORTACIÓN
from math import atan2

# === CONFIGURACIÓN ===
ARCHIVO_ENTRADA = "logica/grafo_figuras.json"
ARCHIVO_SALIDA = "logica/grafo_sin_cruce.json"

# --- NUEVA CONSTANTE ---
# Define qué tan cerca deben estar los obstáculos para fusionarse (en píxeles).
# Un valor más grande fusionará obstáculos más lejanos.
DISTANCIA_FUSION = 15 

# === CARGAR GRAFO ORIGINAL ===
with open(ARCHIVO_ENTRADA) as f:
    data = json.load(f)

grafo_original = data["grafo"]
coordenadas = data["coordenadas"]

# === DETECTAR FIGURAS COMO COMPONENTES CONECTADOS ===
G_figuras = nx.Graph()
for nodo, vecinos in grafo_original.items():
    # Ignorar Robot y Bandera para la construcción de polígonos de obstáculos
    if nodo not in ["Robot", "Bandera"]:
        for vecino in vecinos:
            if vecino not in ["Robot", "Bandera"]:
                G_figuras.add_edge(nodo, vecino)

componentes = list(nx.connected_components(G_figuras))

# === CONSTRUIR POLÍGONOS DE CADA FIGURA ===
poligonos_originales = []
figura_por_nodo = {}

for i, comp in enumerate(componentes):
    nodos = list(comp)
    coords = [tuple(coordenadas[n]) for n in nodos]

    if len(coords) >= 3:
        # Ordenar coordenadas para asegurar un polígono válido
        cx = sum(x for x, y in coords) / len(coords)
        cy = sum(y for x, y in coords) / len(coords)
        coords_ordenadas = sorted(coords, key=lambda p: atan2(p[1] - cy, p[0] - cx))
        poligono = Polygon(coords_ordenadas)
        poligonos_originales.append(poligono)

        for n in comp:
            figura_por_nodo[n] = i

# --- INICIO DE LA NUEVA LÓGICA DE FUSIÓN DE OBSTÁCULOS ---

# 1. Inflamos cada polígono. El resultado es una lista de polígonos más grandes.
poligonos_inflados = [p.buffer(DISTANCIA_FUSION) for p in poligonos_originales]

# 2. Unimos todos los polígonos inflados que se superponen.
#    El resultado puede ser un solo MultiPolygon o varios polígonos separados.
geometria_unificada = unary_union(poligonos_inflados)

# 3. Encogemos la geometría unificada para devolverla a su tamaño original.
geometria_final = geometria_unificada.buffer(-DISTANCIA_FUSION)

# 4. Creamos la lista final de polígonos de obstáculos.
#    Si la geometría es una colección de polígonos (MultiPolygon), los separamos.
poligonos_fusionados = []
if isinstance(geometria_final, MultiPolygon):
    poligonos_fusionados.extend(geometria_final.geoms)
elif isinstance(geometria_final, Polygon):
    poligonos_fusionados.append(geometria_final)

print(f"Se fusionaron {len(poligonos_originales)} obstáculos en {len(poligonos_fusionados)} grupos.")

# --- FIN DE LA LÓGICA DE FUSIÓN ---


# === GENERAR CONEXIONES ENTRE FIGURAS (VISIBILIDAD) ===
# Se mantiene la misma lógica, pero ahora se usa la lista de polígonos fusionados.
nuevo_grafo = {n: list(v) for n, v in grafo_original.items()}
conexiones_visibles = []

nodos = list(coordenadas.keys())
for i in range(len(nodos)):
    for j in range(i + 1, len(nodos)):
        a, b = nodos[i], nodos[j]

        # Evitar conectar nodos de la misma figura original
        fig_a = figura_por_nodo.get(a)
        fig_b = figura_por_nodo.get(b)
        if (fig_a is not None and fig_b is not None and fig_a == fig_b):
            continue

        linea = LineString([tuple(coordenadas[a]), tuple(coordenadas[b])])

        cruza_figura = False
        # --- MODIFICACIÓN IMPORTANTE ---
        # Ahora comprobamos la intersección contra los polígonos fusionados.
        for poly in poligonos_fusionados:
            # Una línea "toca" si solo comparte un punto o un borde.
            # Una línea "intersecta" si pasa por el interior. Queremos evitar esto.
            if linea.intersects(poly) and not linea.touches(poly):
                cruza_figura = True
                break

        if not cruza_figura:
            if b not in nuevo_grafo[a]:
                nuevo_grafo[a].append(b)
            if a not in nuevo_grafo[b]:
                nuevo_grafo[b].append(a)
            conexiones_visibles.append((a, b))

# === GUARDAR GRAFO ACTUALIZADO ===
nuevo_json = {
    "grafo": nuevo_grafo,
    "coordenadas": coordenadas,
    "inicio": data.get("inicio"),
    "meta": data.get("meta")
}
with open(ARCHIVO_SALIDA, "w") as f:
    json.dump(nuevo_json, f, indent=4)

print(f"Grafo con obstáculos fusionados guardado en {ARCHIVO_SALIDA}")
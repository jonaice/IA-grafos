import json
import networkx as nx
from shapely.geometry import Polygon, LineString
from math import atan2

# === CONFIGURACIÓN ===
ARCHIVO_ENTRADA = "lografo_figuras.json"
ARCHIVO_SALIDA = "grafo_sin_cruce.json"

# === CARGAR GRAFO ORIGINAL ===
with open(ARCHIVO_ENTRADA) as f:
    data = json.load(f)

grafo_original = data["grafo"]
coordenadas = data["coordenadas"]

# === DETECTAR FIGURAS COMO COMPONENTES CONECTADOS ===
G_figuras = nx.Graph()
for nodo, vecinos in grafo_original.items():
    for vecino in vecinos:
        G_figuras.add_edge(nodo, vecino)

componentes = list(nx.connected_components(G_figuras))

# === CONSTRUIR POLÍGONOS DE CADA FIGURA ===
poligonos = []
figura_por_nodo = {}

for i, comp in enumerate(componentes):
    nodos = list(comp)
    coords = [tuple(coordenadas[n]) for n in nodos]

    if len(coords) >= 3:
        cx = sum(x for x, y in coords) / len(coords)
        cy = sum(y for x, y in coords) / len(coords)
        coords_ordenadas = sorted(coords, key=lambda p: atan2(p[1] - cy, p[0] - cx))
        poligono = Polygon(coords_ordenadas)
        poligonos.append(poligono)

        for n in comp:
            figura_por_nodo[n] = i

# === GENERAR CONEXIONES ENTRE FIGURAS ===
# === PASO 4: Conexiones visibles entre figuras ===
nuevo_grafo = {n: list(v) for n, v in grafo_original.items()}
conexiones_visibles = []

nodos = list(coordenadas.keys())
for i in range(len(nodos)):
    for j in range(i + 1, len(nodos)):
        a, b = nodos[i], nodos[j]

        fig_a = figura_por_nodo.get(a)
        fig_b = figura_por_nodo.get(b)

        # Si al menos uno de ellos no pertenece a una figura (es Robot o Bandera), permitimos comparar
        if (fig_a is not None and fig_b is not None and fig_a == fig_b):
            continue

        linea = LineString([tuple(coordenadas[a]), tuple(coordenadas[b])])

        cruza_figura = False
        for poly in poligonos:
            if linea.intersects(poly) and not linea.touches(poly):
                cruza_figura = True
                break

        if not cruza_figura:
            if b not in nuevo_grafo[a]:
                nuevo_grafo[a].append(b)
            if a not in nuevo_grafo[b]:
                nuevo_grafo[b].append(a)
            conexiones_visibles.append((a, b))

# === PASO 5: Guardar grafo actualizado ===
nuevo_json = {
    "grafo": nuevo_grafo,
    "coordenadas": coordenadas,
    "inicio": data.get("inicio"),
    "meta": data.get("meta")
}
with open(ARCHIVO_SALIDA, "w") as f:
    json.dump(nuevo_json, f, indent=4)

print(f"✅ Grafo sin cruce y con visibilidad desde Robot y Bandera guardado en {ARCHIVO_SALIDA}")

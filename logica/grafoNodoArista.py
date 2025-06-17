import json
import networkx as nx
import matplotlib.pyplot as plt
import os

# Cargar el grafo generado con conexiones visibles


with open("logica/grafo_sin_cruce.json", "r") as f:
    data = json.load(f)

G = nx.Graph()

# Agregar nodos con sus posiciones
pos = data["coordenadas"]
for nodo, coord in pos.items():
    G.add_node(nodo, pos=tuple(coord))

# Agregar aristas
for nodo, vecinos in data["grafo"].items():
    for vecino in vecinos:
        if not G.has_edge(nodo, vecino):
            G.add_edge(nodo, vecino)

# Identificar componentes conectados (figuras)
componentes = list(nx.connected_components(G))
colores = plt.get_cmap("tab20")

# Visualizar cada componente con color distinto
plt.figure(figsize=(12, 10))
for i, comp in enumerate(componentes):
    subgraph = G.subgraph(comp)
    sub_pos = {n: pos[n] for n in subgraph.nodes()}
    color = colores(i % colores.N)
    nx.draw(subgraph, pos=sub_pos,
            node_color=[color] * len(subgraph),
            edge_color='gray',
            with_labels=True, node_size=700, font_size=10)

plt.title("Grafo separado por componentes (una figura por grupo)")
plt.axis("off")
plt.gca().invert_yaxis()
plt.show()

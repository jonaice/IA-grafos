import numpy as np
import os


# Canvas blanco
canvas = np.ones((800, 1200, 3), dtype=np.uint8) * 255

# Parámetros globales
robot_radio = 50
max_width = 200

# Variables globales
imagenes_config = [
    {"nombre": "img/casa.png"},
    #{"nombre": "img/edificio.png"},
    #{"nombre": "img/arbol.png"},
    #{"nombre": "img/roca.png"},
    #{"nombre": "img/coche.png"},
]

imagenes_cargadas = []
nodos = []
aristas = []
obstaculos_shapely = []
start_node = None
end_node = None
node_labels = {}

import cv2
import numpy as np
import json
import os
from shapely.geometry import Polygon

# === CONFIGURACIÓN ===
BASE_DIR = os.path.dirname(__file__)
ARCHIVO_ESCENARIO = os.path.abspath(os.path.join(BASE_DIR, "..", "interfaz", "escenario.json"))
ARCHIVO_SALIDA = "logica/grafo_figuras.json"
UMBRAL_SIMPLIFICACION = 0.01  # Tolerancia para simplificar contornos
LETRA_POR_TIPO = {
    "robot": "R",
    "bandera": "F",
    "obstaculo": "O"
}

# === CARGAR ESCENARIO ===
with open(ARCHIVO_ESCENARIO) as f:
    escenario = json.load(f)

grafo = {}
coordenadas = {}
contador_por_tipo = {}

# === FUNCIONES ===

def extraer_vertices(img,angle):

    #Rotar la imagen
    if(angle!=0):
        h, w = img.shape[:2] # Obtiene alto y ancho de la imagen
        centro = (w // 2, h // 2)
        matriz_rotacion = cv2.getRotationMatrix2D(centro, angle, 1.0)
        # Aplicar rotación
        img = cv2.warpAffine(img, matriz_rotacion, (w, h))

    if img.shape[2] == 4:
        gray = img[:, :, 3]  # Canal alfa
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    

    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return []

    contorno = max(contornos, key=cv2.contourArea)
    epsilon = UMBRAL_SIMPLIFICACION * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)

    vertices = [tuple(p[0]) for p in approx]
    return vertices

def obtener_prefijo(path):
    nombre = path.split(".")[0]
    for tipo in LETRA_POR_TIPO:
        if nombre.startswith(tipo):
            return LETRA_POR_TIPO[tipo]
    return "X"  # Default

# === PROCESAR CADA IMAGEN ===
for objeto in escenario:
    archivo = objeto["path"]
    cx, cy = objeto["pos"]
    angle = objeto["angle"]

    if not os.path.exists(archivo):
        print(f"❌ No encontrado: {archivo}")
        continue

    imagen = cv2.imread(archivo, cv2.IMREAD_UNCHANGED)
    if imagen is None:
        print(f"❌ No se pudo cargar: {archivo}")
        continue

    tipo = archivo.split(".")[0]  # sin extensión
    if tipo == "robot":
        nodo_id = "Robot"
        coordenadas[nodo_id] = [cx, cy]
        grafo[nodo_id] = []
        inicio = nodo_id
        continue
    elif tipo == "bandera":
        nodo_id = "Bandera"
        coordenadas[nodo_id] = [cx, cy]
        grafo[nodo_id] = []
        meta = nodo_id
        continue

    # Procesar como obstáculo normal
    h, w = imagen.shape[:2]
    x0 = cx - w // 2
    y0 = cy - h // 2

    vertices_locales = extraer_vertices(imagen,angle)
    if len(vertices_locales) < 3:
        print(f"⚠️ Pocos vértices en {archivo}")
        continue

    tipo = obtener_prefijo(archivo)
    contador = contador_por_tipo.get(tipo, 0)
    prefijo = f"{tipo}{contador}"
    contador_por_tipo[tipo] = contador + 1

    nodos_figura = []

    for i, (vx, vy) in enumerate(vertices_locales):
        global_x = x0 + vx
        global_y = y0 + vy
        nodo_id = f"{prefijo}_{i}"
        coordenadas[nodo_id] = [int(global_x), int(global_y)]
        nodos_figura.append(nodo_id)

    # Conectar nodos en ciclo
    for i in range(len(nodos_figura)):
        a = nodos_figura[i]
        b = nodos_figura[(i + 1) % len(nodos_figura)]
        grafo.setdefault(a, []).append(b)
        grafo.setdefault(b, []).append(a)


# === DETECTAR INICIO Y META
inicio = next((n for n in coordenadas if n.startswith("R")), None)
meta = next((n for n in coordenadas if n.startswith("F")), None)

# === GUARDAR JSON ===
salida = {
    "grafo": grafo,
    "coordenadas": coordenadas,
    "inicio": inicio,
    "meta": meta
}
with open(ARCHIVO_SALIDA, "w") as f:
    json.dump(salida, f, indent=4)

print(f"✅ Grafo guardado en {ARCHIVO_SALIDA}")

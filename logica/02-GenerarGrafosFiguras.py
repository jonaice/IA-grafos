import cv2
import numpy as np
import json
import os
from shapely.geometry import Polygon

# === CONFIGURACIÓN ===
BASE_DIR = os.path.dirname(__file__)
ARCHIVO_ESCENARIO = os.path.abspath(os.path.join(BASE_DIR, "..", "interfaz", "escenario.json"))
ARCHIVO_SALIDA = "logica/grafo_figuras.json"
UMBRAL_SIMPLIFICACION = 0.02  # Tolerancia para simplificar contornos
LETRA_POR_TIPO = {
    "robot": "R",
    "bandera": "F",
    "obstaculo": "O"
}
MARGEN_INFLADO = 50

# === CARGAR ESCENARIO ===
with open(ARCHIVO_ESCENARIO) as f:
    escenario = json.load(f)

grafo = {}
coordenadas = {}
contador_por_tipo = {}
inicio = None
meta = None

# === FUNCIONES ===

def extraer_vertices(img, angle):
    # Rotar la imagen si se requiere
    if angle != 0:
        h, w = img.shape[:2]
        centro = (w // 2, h // 2)
        matriz_rotacion = cv2.getRotationMatrix2D(centro, angle, 1.0)
        img = cv2.warpAffine(img, matriz_rotacion, (w, h))

    # Obtener máscara binaria a partir de canal alfa o intensidad
    if img.shape[2] == 4:
        gray = img[:, :, 3]
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Contornos
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return []

    contorno = max(contornos, key=cv2.contourArea)
    epsilon = UMBRAL_SIMPLIFICACION * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)

    return [tuple(p[0]) for p in approx]

def obtener_prefijo(path):
    nombre = path.split(".")[0]
    for tipo in LETRA_POR_TIPO:
        if nombre.startswith(tipo):
            return LETRA_POR_TIPO[tipo]
    return "X"  # Default

# === PROCESAR CADA IMAGEN DEL ESCENARIO ===
for objeto in escenario:
    archivo = objeto["path"]
    cx, cy = objeto["pos"]
    angle = objeto.get("angle", 0)

    if not os.path.exists(archivo):
        print(f"❌ No encontrado: {archivo}")
        continue

    imagen = cv2.imread(archivo, cv2.IMREAD_UNCHANGED)
    if imagen is None:
        print(f"❌ No se pudo cargar: {archivo}")
        continue

    # Nombre base sin ruta ni extensión
    nombre_base = os.path.splitext(os.path.basename(archivo))[0].lower()

    # === Nodo único para robot ===
    if nombre_base == "robot":
        nodo_id = "Robot"
        coordenadas[nodo_id] = [cx, cy]
        grafo[nodo_id] = []
        inicio = nodo_id
        continue

    # === Nodo único para bandera ===
    elif nombre_base == "bandera":
        nodo_id = "Bandera"
        coordenadas[nodo_id] = [cx, cy]
        grafo[nodo_id] = []
        meta = nodo_id
        continue

    # === Procesar como figura normal ===
    h, w = imagen.shape[:2]
    x0 = cx - w // 2
    y0 = cy - h // 2

    vertices_locales = extraer_vertices(imagen, angle)
    if len(vertices_locales) < 3:
        print(f"⚠️ Pocos vértices en {archivo}")
        continue

    # --- INICIO DE LA NUEVA LÓGICA DE INFLADO Y SIMPLIFICACIÓN ---
    # 1. Creamos un polígono con los vértices originales.
    poligono_original = Polygon(vertices_locales)

    # 2. Creamos una versión "inflada" del polígono usando buffer().
    poligono_inflado = poligono_original.buffer(MARGEN_INFLADO)

    # 3. Extraemos las coordenadas del nuevo polígono inflado y las convertimos
    #    a un formato que OpenCV pueda usar (NumPy array).
    coords_infladas_np = np.array(poligono_inflado.exterior.coords, dtype=np.int32)

    # 4. --- NUEVO PASO DE SIMPLIFICACIÓN ---
    #    Aplicamos el mismo algoritmo de simplificación al polígono inflado para
    #    reducir su número de vértices de vuelta a una cantidad manejable.
    #    La variable UMBRAL_SIMPLIFICACION controla qué tan agresiva es la simplificación.
    epsilon = UMBRAL_SIMPLIFICACION * cv2.arcLength(coords_infladas_np, True)
    approx_inflado = cv2.approxPolyDP(coords_infladas_np, epsilon, True)

    # 5. Reemplazamos los vértices locales por los nuevos: inflados Y simplificados.
    vertices_locales = [tuple(p[0]) for p in approx_inflado]
    # --- FIN DE LA NUEVA LÓGICA ---

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

    # Conexiones entre nodos de la figura (en ciclo)
    for i in range(len(nodos_figura)):
        a = nodos_figura[i]
        b = nodos_figura[(i + 1) % len(nodos_figura)]
        grafo.setdefault(a, []).append(b)
        grafo.setdefault(b, []).append(a)

# === GUARDAR JSON ===
salida = {
    "grafo": grafo,
    "coordenadas": coordenadas,
    "inicio": inicio,
    "meta": meta
}
with open(ARCHIVO_SALIDA, "w") as f:
    json.dump(salida, f, indent=4)

print(f"Grafo guardado en {ARCHIVO_SALIDA}")

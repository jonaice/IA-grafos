import cv2
import numpy as np
import json
import os

# === CONFIGURACIÓN ===
BASE_DIR = os.path.dirname(__file__)
ARCHIVO_ESCENARIO = os.path.abspath(os.path.join(BASE_DIR, "..", "interfaz", "escenario.json"))

ANCHO_LIENZO = 1000
ALTO_LIENZO = 720

# === CARGAR ESCENARIO ===
with open(ARCHIVO_ESCENARIO) as f:
    escenario = json.load(f)

# === CREAR LIENZO BLANCO CON CANAL ALFA ===
canvas = np.ones((ALTO_LIENZO, ANCHO_LIENZO, 4), dtype=np.uint8) * 255  # RGBA

# === PROCESAR CADA IMAGEN ===
for objeto in escenario:
    archivo = objeto["path"]
    cx, cy = objeto["pos"]

    if not os.path.exists(archivo):
        print(f"❌ No encontrado: {archivo}")
        continue

    imagen = cv2.imread(archivo, cv2.IMREAD_UNCHANGED)
    if imagen is None:
        print(f"❌ No se pudo cargar: {archivo}")
        continue

    h, w = imagen.shape[:2]

    # Calculamos posición superior izquierda a partir del centro
    x1 = cx - w // 2
    y1 = cy - h // 2
    x2 = x1 + w
    y2 = y1 + h

    # Verificar que no se salga del lienzo
    if x1 < 0 or y1 < 0 or x2 > ANCHO_LIENZO or y2 > ALTO_LIENZO:
        print(f"⚠️ {archivo} se sale del lienzo. Posición: ({cx}, {cy}) Tamaño: ({w}, {h})")
        continue

    # Superponer imagen (con o sin transparencia)
    if imagen.shape[2] == 4:  # Con canal alfa
        alpha_s = imagen[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(3):  # BGR
            canvas[y1:y2, x1:x2, c] = (
                alpha_s * imagen[:, :, c] + alpha_l * canvas[y1:y2, x1:x2, c]
            )
        canvas[y1:y2, x1:x2, 3] = 255  # Forzar fondo opaco
    else:
        canvas[y1:y2, x1:x2, :3] = imagen
        canvas[y1:y2, x1:x2, 3] = 255

# === MOSTRAR RESULTADO ===
cv2.imshow("Escenario", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

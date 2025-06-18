import pygame
import sys
import subprocess
import json # <-- AÑADIR IMPORT
import os   # <-- AÑADIR IMPORT
import math # <-- AÑADIR IMPORT
from logica.utils import cargar_coordenadas, traducir_camino_a_coordenadas

#import locales
from algoritmos import BusqAmplitud
from algoritmos import BusqProfundidad
from algoritmos import BusqProfIterativa
from algoritmos import busqueda_costo_uniforme
from algoritmos import busqueda_avara
from algoritmos import busqueda_a_estrella

# Inicializar pygame
pygame.init()

# <-- PASO 1: AÑADIR LA CLASE Y LA FUNCIÓN DE CARGA -->
# (Este es el código que preparamos en la respuesta anterior)

class ObjetoJuego(pygame.sprite.Sprite):
    """
    Representa un objeto cargado desde el escenario.json (un obstáculo, el jugador, etc.).
    """
    def __init__(self, pos, image, angle, path):
        super().__init__()
        self.original_image = image
        self.path = path
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=pos)

def calcular_angulo(p1, p2):
    """Calcula el ángulo en grados desde el punto p1 al punto p2."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    # Usamos atan2 para obtener el ángulo en radianes y lo convertimos a grados
    rads = math.atan2(-dy, dx)
    rads %= 2 * math.pi
    degs = math.degrees(rads)
    degs_corregido = degs + 90
    return degs_corregido

# main.py

def cargar_escenario_juego(offset):
    """
    Carga los objetos desde 'escenario.json', separa el robot del resto
    y devuelve ambos.
    """
    objetos_estaticos = pygame.sprite.Group()
    robot_para_animar = None
    imagenes_cargadas = {}
    offset_x, offset_y = offset

    if not os.path.exists('interfaz/escenario.json'):
        print("⚠ No se encontró el archivo 'escenario.json'.")
        return objetos_estaticos, robot_para_animar

    with open('interfaz/escenario.json', 'r') as f:
        data_escenario = json.load(f)

    for item_data in data_escenario:
        path = item_data['path']
        if path not in imagenes_cargadas:
            try:
                imagenes_cargadas[path] = pygame.image.load(path).convert_alpha()
            except pygame.error:
                print(f"⚠ No se pudo cargar la imagen: {path}. Se omitirá este objeto.")
                continue
        
        imagen = imagenes_cargadas[path]
        pos_guardada = item_data['pos']
        angulo_guardado = item_data['angle']
        
        nuevo_x = pos_guardada[0] + offset_x
        nuevo_y = pos_guardada[1] + offset_y
        
        objeto = ObjetoJuego((nuevo_x, nuevo_y), imagen, angulo_guardado, path)

        # --- LÓGICA DE SEPARACIÓN INTERNA ---
        # Si el objeto es el robot, lo guardamos en su propia variable.
        if "robot.png" in path:
            robot_para_animar = objeto
        # Si es cualquier otro objeto, lo añadimos al grupo de sprites estáticos.
        else:
            objetos_estaticos.add(objeto)
    
    # La cantidad de objetos cargados es la de los estáticos + 1 (si se encontró el robot)
    num_objetos = len(objetos_estaticos) + (1 if robot_para_animar else 0)
    print(f"✔ Escenario cargado con {num_objetos} objetos.")
    
    # Devolvemos los dos valores que esperamos
    return objetos_estaticos, robot_para_animar
# --- FIN DEL PASO 1 ---


# Dimensiones más amplias
WIDTH, HEIGHT = 1200, 860
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menú Principal - Pygame")

# Colores
BG_COLOR = (29, 29, 47)
WHITE = (255, 255, 255)
GRAY = (58, 58, 90)
GREEN = (60, 176, 67)
RED = (198, 64, 64)
LIGHT_GRAY = (100, 100, 140)
DISABLED_GRAY = (80, 80, 110)
HOVER_GRAY = (75, 75, 110)
HOVER_GREEN = (80, 200, 90)
HOVER_RED = (210, 80, 80)
BASE_PATH = os.path.dirname(__file__)
IMG_PATH = os.path.join(BASE_PATH,"interfaz" ,"img", "fondo_menu.png")
camino = []

# Fuente
font = pygame.font.SysFont("arial", 16)

# Layout 
btn_width = 170
btn_height = 40
GAP_X = 40
TOP_MARGIN = 45

# Calcular posición inicial para centrar grupo de botones
group_width = btn_width * 4 + GAP_X * 3 + 120  # 120 extra por combo ancho
start_x = (WIDTH - group_width) // 2

# Rects centrados
btn_back = pygame.Rect(start_x, TOP_MARGIN, btn_width, btn_height)
combo_box = pygame.Rect(btn_back.right + GAP_X, TOP_MARGIN, btn_width + 120, btn_height)
btn_start = pygame.Rect(combo_box.right + GAP_X, TOP_MARGIN, btn_width, btn_height)
btn_exit = pygame.Rect(btn_start.right + GAP_X, TOP_MARGIN, btn_width, btn_height)

# Opciones
algoritmos = ["Búsqueda en Amplitud", "Búsqueda en Profundidad", "Búsqueda por Profundización Iterativa", "Búsqueda de Costo Uniforme", "Búsqueda A*", "Búsqueda Avara"]
selected_index = -1
combo_open = False

def get_combo_items_rects():
    return [pygame.Rect(combo_box.x, combo_box.bottom + 5 + i * 30, combo_box.width, 30)
            for i in range(len(algoritmos))]

# <-- PASO 2: DEFINIR ÁREA Y CARGAR RECURSOS UNA SOLA VEZ (FUERA DEL BUCLE) -->
# Definir el área de juego
juego_area = pygame.Rect(60, 120, 1000, 720)

# Cargar y ajustar el fondo del área de juego
try:
    fondo_imagen = pygame.image.load(IMG_PATH).convert()
    fondo_ajustado = pygame.transform.scale(fondo_imagen, (juego_area.width, juego_area.height))
except Exception as e:
    print("⚠ No se pudo cargar fondo.PNG:", e)
    fondo_ajustado = None

# Cargar los objetos del escenario JSON
escenario_sprites, robot_animado = cargar_escenario_juego(juego_area.topleft)
if robot_animado:
    robot_animado_group = pygame.sprite.Group(robot_animado)
else:
    robot_animado_group = pygame.sprite.Group()

# --- CÓDIGO DE CARGA SIMPLIFICADO ---

# La llamada a la función ahora funciona porque devuelve dos valores.
escenario_sprites, robot_animado = cargar_escenario_juego(juego_area.topleft)

# Creamos un grupo de sprites solo para el robot animado (si se encontró).
if robot_animado:
    robot_animado_group = pygame.sprite.Group(robot_animado)
else:
    print("⚠️ Advertencia: No se encontró el robot en el escenario para animar.")
    robot_animado_group = pygame.sprite.Group()


# --- BUCLE PRINCIPAL ---
running = True
camino_a_dibujar = None
camino_a_dibujar = None
estado_animacion = "IDLE"  # Nuestros estados: IDLE, PLAYING, ARRIVED, RETURNING
segmento_actual_idx = 0
progreso_segmento = 0.0
velocidad_animacion = 0.001 # O el valor que hayas elegido

tiempo_llegada = 0 # Para el temporizador de 2 segundos
posicion_inicio = None # Para recordar dónde empezar y a dónde volver

while running:
    screen.fill(BG_COLOR)

    # --- PRIMERO: dibujar el fondo y los objetos del escenario ---
    
    # 1. Dibujar el fondo del área de juego
    if fondo_ajustado:
        screen.blit(fondo_ajustado, juego_area.topleft)
    else:
        # Si no hay fondo, dibujar un rectángulo de color
        pygame.draw.rect(screen, (20, 20, 30), juego_area)

    # <-- PASO 3: DIBUJAR LOS SPRITES DEL ESCENARIO -->
    # Esta línea dibuja todos los objetos cargados del JSON
    escenario_sprites.draw(screen)


    # --- MÁQUINA DE ESTADOS DE ANIMACIÓN ---
    if camino_a_dibujar:
        # Dibujamos siempre la línea completa del camino en amarillo
        if len(camino_a_dibujar) > 1:
            pygame.draw.lines(screen, (255, 255, 0), False, camino_a_dibujar, 5)

        # --- ESTADO 1: Yendo hacia la bandera ---
        if estado_animacion == "PLAYING" and robot_animado:
            p0 = camino_a_dibujar[segmento_actual_idx]
            p1 = camino_a_dibujar[segmento_actual_idx + 1]
            progreso_segmento += velocidad_animacion

            if progreso_segmento >= 1.0:
                progreso_segmento = 0.0
                segmento_actual_idx += 1

                if segmento_actual_idx >= len(camino_a_dibujar) - 1:
                    # --- TRANSICIÓN: HEMOS LLEGADO ---
                    estado_animacion = "ARRIVED"
                    tiempo_llegada = pygame.time.get_ticks() # Iniciamos el temporizador
                    robot_animado.rect.center = p1
                    # Reseteamos la rotación a la original (mirando hacia abajo, que es 0 en nuestro sistema corregido)
                    robot_animado.image = pygame.transform.rotate(robot_animado.original_image, 0)
                else:
                    nuevo_angulo = calcular_angulo(camino_a_dibujar[segmento_actual_idx], camino_a_dibujar[segmento_actual_idx + 1])
                    robot_animado.image = pygame.transform.rotate(robot_animado.original_image, nuevo_angulo)
            
            if estado_animacion == "PLAYING":
                current_x = p0[0] + (p1[0] - p0[0]) * progreso_segmento
                current_y = p0[1] + (p1[1] - p0[1]) * progreso_segmento
                robot_animado.rect.center = (int(current_x), int(current_y))

        # --- ESTADO 2: En pausa en la bandera ---
        elif estado_animacion == "ARRIVED":
            # Verificamos si han pasado 2 segundos (2000 milisegundos)
            if pygame.time.get_ticks() - tiempo_llegada > 2000:
                # --- TRANSICIÓN: Iniciar el regreso ---
                estado_animacion = "RETURNING"
                progreso_segmento = 0.0 # Reiniciamos el progreso para el viaje de vuelta
                # Orientamos el robot para el viaje de regreso
                angulo_regreso = calcular_angulo(robot_animado.rect.center, posicion_inicio)
                robot_animado.image = pygame.transform.rotate(robot_animado.original_image, angulo_regreso)

        # --- ESTADO 3: Regresando al origen ---
        elif estado_animacion == "RETURNING":
            p0 = camino_a_dibujar[-1] # El punto de partida ahora es el final del camino
            p1 = posicion_inicio     # El destino es el inicio original
            progreso_segmento += velocidad_animacion

            if progreso_segmento >= 1.0:
                # --- TRANSICIÓN: Hemos vuelto ---
                estado_animacion = "IDLE"
                robot_animado.rect.center = posicion_inicio
                camino_a_dibujar = None # Limpiamos el camino para la próxima vez
            else:
                current_x = p0[0] + (p1[0] - p0[0]) * progreso_segmento
                current_y = p0[1] + (p1[1] - p0[1]) * progreso_segmento
                robot_animado.rect.center = (int(current_x), int(current_y))

    # --- DIBUJAR EL ROBOT ANIMADO ---
    # Esto no cambia: siempre dibujamos el robot en su posición actual
    if robot_animado_group:
        robot_animado_group.draw(screen)
    
    # --- DIBUJAR EL ROBOT ANIMADO ---
    # Dibujamos el grupo que contiene al robot animado.
    # Esto se hace aquí para que se dibuje por encima de la línea del camino.
    if robot_animado_group:
        robot_animado_group.draw(screen)
    # --- LUEGO: interfaz de usuario ---
    mouse_pos = pygame.mouse.get_pos()
    combo_items_rects = get_combo_items_rects()

    # Botón Editar entorno
    back_hover = btn_back.collidepoint(mouse_pos)
    pygame.draw.rect(screen, HOVER_GRAY if back_hover else GRAY, btn_back)
    text_back = font.render("← editar entorno", True, WHITE)
    screen.blit(text_back, text_back.get_rect(center=btn_back.center))

    # ComboBox
    pygame.draw.rect(screen, GRAY, combo_box)
    texto = "selecciona el algoritmo de búsqueda" if selected_index == -1 else algoritmos[selected_index]
    text_combo = font.render(texto, True, WHITE)
    screen.blit(text_combo, text_combo.get_rect(center=combo_box.center))

    # Botón Iniciar
    start_hover = btn_start.collidepoint(mouse_pos)
    if selected_index != -1:
        color_start = HOVER_GREEN if start_hover else GREEN
    else:
        color_start = DISABLED_GRAY
    pygame.draw.rect(screen, color_start, btn_start)
    text_start = font.render("iniciar", True, WHITE)
    screen.blit(text_start, text_start.get_rect(center=btn_start.center))

    # Botón Salir
    exit_hover = btn_exit.collidepoint(mouse_pos)
    pygame.draw.rect(screen, HOVER_RED if exit_hover else RED, btn_exit)
    text_exit = font.render("salir", True, WHITE)
    screen.blit(text_exit, text_exit.get_rect(center=btn_exit.center))

    # Lista desplegable
    if combo_open:
        for i, rect in enumerate(combo_items_rects):
            item_hover = rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, HOVER_GRAY if item_hover else LIGHT_GRAY, rect)
            text_item = font.render(algoritmos[i], True, WHITE)
            screen.blit(text_item, (rect.x + 10, rect.y + 6))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if btn_exit.collidepoint(mx, my):
                running = False

            elif btn_back.collidepoint(mx, my):
                try:
                    subprocess.Popen(["python", "interfaz/editorEscenarios.py"])
                    pygame.quit()
                    sys.exit()
                except Exception as e:
                    print("Error al abrir editorEscenarios.py:", e)

            elif btn_start.collidepoint(mx, my) and selected_index != -1:
                print(f"Iniciando algoritmo: {algoritmos[selected_index]}")
                if (selected_index == 0):
                    camino = BusqAmplitud.Amplitud()
                elif (selected_index == 1):
                    camino = BusqProfundidad.Profundidad()
                elif (selected_index == 2):
                    camino = BusqProfIterativa.ProfundidadI()
                elif (selected_index == 3):
                    camino = busqueda_costo_uniforme.Uniforme()
                elif (selected_index == 4):
                    camino = busqueda_avara.Avara()

                if camino:
                    print(f"Camino encontrado (IDs): {camino}")
                    # 1. Cargar todas las coordenadas del archivo
                    todas_las_coords = cargar_coordenadas("logica/datos_completos.txt")
                    # 2. Obtener el offset del área de juego
                    offset = juego_area.topleft
                    # 3. Traducir y guardar el resultado para dibujarlo
                    camino_a_dibujar = traducir_camino_a_coordenadas(camino, todas_las_coords, offset)
                    # --- INICIAR Y REINICIAR ESTADO DE ANIMACIÓN ---
                    if camino_a_dibujar and len(camino_a_dibujar) > 1:
                        estado_animacion = "PLAYING" # Iniciamos la animación
                        segmento_actual_idx = 0
                        progreso_segmento = 0.0

                        posicion_inicio = camino_a_dibujar[0] # Guardamos la posición de inicio
                        robot_animado.rect.center = posicion_inicio

                        # Orientamos al robot para el primer tramo
                        angulo_inicial = calcular_angulo(camino_a_dibujar[0], camino_a_dibujar[1])
                        robot_animado.image = pygame.transform.rotate(robot_animado.original_image, angulo_inicial)
                    print(f"Camino traducido a coordenadas de pantalla: {camino_a_dibujar}")
                else:
                    print("No se encontró un camino.")
                    camino_a_dibujar = None

            elif combo_box.collidepoint(mx, my):
                combo_open = not combo_open

            elif combo_open:
                for i, rect in enumerate(combo_items_rects):
                    if rect.collidepoint(mx, my):
                        selected_index = i
                        combo_open = False
                        break
                else: # Si el clic no fue en un item, pero la lista está abierta, ciérrala
                    combo_open = False

    pygame.display.flip()







pygame.quit()
sys.exit()
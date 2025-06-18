import pygame
import sys
import subprocess
import json  # <-- AÑADIR IMPORT
import os   # <-- AÑADIR IMPORT
import math  # <-- AÑADIR IMPORT
from logica.utils import cargar_coordenadas, traducir_camino_a_coordenadas
# Import locales
from algoritmos import BusqAmplitud
from algoritmos import BusqProfundidad
from algoritmos import BusqProfIterativa
from algoritmos import busqueda_costo_uniforme
from algoritmos import busqueda_avara
from algoritmos import busqueda_a_estrella
import editorEscenarios

# Inicializar pygame

def menu():
    pygame.init()
    camino_a_dibujar = None

    # <-- PASO 1: AÑADIR LA CLASE Y LA FUNCIÓN DE CARGA -->
    class ObjetoJuego(pygame.sprite.Sprite):
        """
        Representa un objeto cargado desde el escenario.json (un obstáculo, el jugador, etc.).
        """
        def __init__(self, pos, image, angle):
            super().__init__()
            self.original_image = image
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=pos)

    def cargar_escenario_juego(offset):
        """
        Carga los objetos desde 'escenario.json', ajusta sus posiciones con el offset
        y los devuelve en un grupo de sprites.
        """
        objetos_del_juego = pygame.sprite.Group()
        imagenes_cargadas = {}
        
        offset_x, offset_y = offset

        if not os.path.exists('interfaz/escenario.json'):
            print("⚠ No se encontró el archivo 'escenario.json'. El escenario estará vacío.")
            return objetos_del_juego

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
            
            objeto = ObjetoJuego((nuevo_x, nuevo_y), imagen, angulo_guardado)
            objetos_del_juego.add(objeto)
            
        print(f"✔ Escenario cargado con {len(objetos_del_juego)} objetos.")
        return objetos_del_juego

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
    IMG_PATH = os.path.join(BASE_PATH, "interfaz", "img", "fondo_menu.png")
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

    # Variables de animación
    segmento_actual = 0
    progreso_segmento = 0.0
    velocidad_animacion = 0.0002  # Controla la velocidad de la animación
    frame_counter = 0  # Contador de frames para alternar entre las imágenes
    image_toggle = True  # Alternador para elegir entre las dos imágenes
    # Cargar imagen del robot
    # Cargar las dos imágenes del robot
    robot_image_1 = pygame.image.load("interfaz/img/robot1.png").convert_alpha()  # Imagen con un pie adelante
    robot_image_2 = pygame.image.load("interfaz/img/robot2.png").convert_alpha()  # Imagen con el otro pie adelante


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
    escenario_sprites = cargar_escenario_juego(juego_area.topleft)

    # --- BUCLE PRINCIPAL ---
    running = True
    while running:
        screen.fill(BG_COLOR)

        # --- PRIMERO: dibujar el fondo y los objetos del escenario ---
        
        # 1. Dibujar el fondo del área de juego
        if fondo_ajustado:
            screen.blit(fondo_ajustado, juego_area.topleft)
        else:
            # Si no hay fondo, dibujar un rectángulo de color
            pygame.draw.rect(screen, (20, 20, 30), juego_area)

        # --- PASO 2: DIBUJAR LOS SPRITES DEL ESCENARIO -->
        # Esta línea dibuja todos los objetos cargados del JSON
        escenario_sprites.draw(screen)

        # --- TAREA 2.2: Dibujar el Camino Estático ---
        if camino_a_dibujar and len(camino_a_dibujar) > 1:
            # Dibuja líneas que conectan todos los puntos del camino
            pygame.draw.lines(screen, (255, 255, 0), False, camino_a_dibujar, 5)  # Color amarillo, 5px de grosor

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

        # --- TAREA 2.3: Animar el Movimiento del Robot ---

        if camino_a_dibujar and len(camino_a_dibujar) > 1:
        # Interpolación entre el punto A y B del camino
            A = camino_a_dibujar[segmento_actual]
            B = camino_a_dibujar[segmento_actual + 1] if segmento_actual + 1 < len(camino_a_dibujar) else A

        # Calcular la posición actual usando interpolación lineal (Lerp)
            P_x = A[0] + (B[0] - A[0]) * progreso_segmento
            P_y = A[1] + (B[1] - A[1]) * progreso_segmento

        # Alternar la imagen cada ciertos ciclos
            if frame_counter % 100 == 0:  # Cambiar imagen cada 100 cuadros (ajusta según la velocidad)
                image_toggle = not image_toggle

        # Selecciona la imagen que se mostrará
            robot_image = robot_image_1 if image_toggle else robot_image_2

        # Dibujar la imagen del robot
            robot_rect = robot_image.get_rect(center=(int(P_x), int(P_y)))  # Obtiene el rectángulo de la imagen y lo centra en la posición calculada
            screen.blit(robot_image, robot_rect)  # Dibuja la imagen del robot en la pantalla

        # Actualizar progreso
            progreso_segmento += velocidad_animacion
            if progreso_segmento >= 1.0:
                progreso_segmento = 0.0
                segmento_actual += 1

            # Si se ha llegado al final del camino, reiniciar la animación
                if segmento_actual >= len(camino_a_dibujar) - 1:
                    segmento_actual = 0  # Para repetir la animación desde el inicio del camino

        # Incrementar el contador de frames
            frame_counter += 1


        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if btn_exit.collidepoint(mx, my):
                    try:
                        if os.path.exists('interfaz/escenario.json'):
                            os.remove('interfaz/escenario.json')
                            print("Archivo 'escenario.json' eliminado.")
                    except OSError as e:
                        print(f"Error al eliminar el archivo: {e}")
                    running = False

                elif btn_back.collidepoint(mx, my):
                    try:
                        editorEscenarios.Editor()
                        pygame.quit()
                        sys.exit()
                    except Exception as e:
                        print("Error al abrir editorEscenarios.py:", e)

                elif btn_start.collidepoint(mx, my) and selected_index != -1:
                    print(f"Iniciando algoritmo: {algoritmos[selected_index]}")
                    if selected_index == 0:
                        camino = BusqAmplitud.Amplitud()
                    elif selected_index == 1:
                        camino = BusqProfundidad.Profundidad()
                    elif selected_index == 2:
                        camino = BusqProfIterativa.ProfundidadI()
                    elif selected_index == 3:
                        camino = busqueda_costo_uniforme.Uniforme()
                    elif selected_index == 5:
                        camino = busqueda_a_estrella.estrella()
                    elif selected_index == 5:
                        camino = busqueda_avara.Avara()

                    print(camino)

                    # Aquí se procesa el camino al que se debe dibujar
                    if camino:
                        # Obtener todas las coordenadas del archivo
                        todas_las_coords = cargar_coordenadas("logica/datos_completos.txt")  # Usamos la función cargada de utils.py
                        # Obtener el offset del área de juego
                        offset = juego_area.topleft  # Asume que tienes un área de juego definida
                        # Traducir el camino y guardarlo para dibujarlo
                        camino_a_dibujar = traducir_camino_a_coordenadas(camino, todas_las_coords, offset)  # Usamos la función traducir

                elif combo_box.collidepoint(mx, my):
                    combo_open = not combo_open

                elif combo_open:
                    for i, rect in enumerate(combo_items_rects):
                        if rect.collidepoint(mx, my):
                            selected_index = i
                            combo_open = False
                            break
                    else:  # Si el clic no fue en un item, pero la lista está abierta, ciérrala
                        combo_open = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

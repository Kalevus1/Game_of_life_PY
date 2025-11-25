#pip install pygame numpy
import pygame
import numpy as np
import time
import sys

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)

# Dimensiones iniciales
CELL_SIZE = 12
GRID_WIDTH = 60
GRID_HEIGHT = 40
UI_HEIGHT = 80  # Altura para los botones

# Configuración de la ventana
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + UI_HEIGHT

class GameOfLife:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Juego de la Vida de Conway")
        
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH))
        self.running_simulation = False
        self.speed = 5  # Velocidad inicial (1-10)
        self.zoom_level = 1.0
        
        # Fuente para texto
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Estados
        self.show_explanation = False
        
        # Inicializar con algunos patrones
        self.initialize_patterns()
    
    def initialize_patterns(self):
        """Inicializa algunos patrones interesantes"""
        # Planeador
        self.add_glider(5, 5)
        
        # Blinker
        self.add_blinker(15, 15)
        
        # Nave ligera
        self.add_lightweight_spaceship(10, 25)
    
    def add_glider(self, x, y):
        """Añade un planeador en la posición (x, y)"""
        pattern = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ])
        self.add_pattern(x, y, pattern)
    
    def add_blinker(self, x, y):
        """Añade un blinker en la posición (x, y)"""
        pattern = np.array([
            [1, 1, 1]
        ])
        self.add_pattern(x, y, pattern)
    
    def add_lightweight_spaceship(self, x, y):
        """Añade una nave ligera en la posición (x, y)"""
        pattern = np.array([
            [0, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0]
        ])
        self.add_pattern(x, y, pattern)
    
    def add_pattern(self, x, y, pattern):
        """Añade un patrón en la posición (x, y)"""
        h, w = pattern.shape
        for i in range(h):
            for j in range(w):
                if 0 <= x + i < GRID_HEIGHT and 0 <= y + j < GRID_WIDTH:
                    self.grid[x + i, y + j] = pattern[i, j]
    
    def count_neighbors(self, grid, x, y):
        """Cuenta los vecinos vivos de una celda"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = x + i, y + j
                if 0 <= nx < GRID_HEIGHT and 0 <= ny < GRID_WIDTH:
                    count += grid[nx, ny]
        return count
    
    def update_grid(self):
        """Actualiza la grilla según las reglas del Juego de la Vida"""
        new_grid = self.grid.copy()
        
        for x in range(GRID_HEIGHT):
            for y in range(GRID_WIDTH):
                neighbors = self.count_neighbors(self.grid, x, y)
                
                # Celula viva
                if self.grid[x, y] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[x, y] = 0  # Muere por soledad o sobrepoblación
                    else:
                        new_grid[x, y] = 1  # Sobrevive
                # Celula muerta
                else:
                    if neighbors == 3:
                        new_grid[x, y] = 1  # Nace
        
        self.grid = new_grid
    
    def reset_grid(self):
        """Reinicia la grilla a un estado vacío"""
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH))
        self.running_simulation = False
    
    def draw_grid(self):
        """Dibuja la grilla en la pantalla"""
        # Fondo negro para el área de la grilla
        pygame.draw.rect(self.screen, BLACK, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT - UI_HEIGHT))
        
        # Dibujar celdas vivas
        for x in range(GRID_HEIGHT):
            for y in range(GRID_WIDTH):
                if self.grid[x, y] == 1:
                    rect = pygame.Rect(
                        y * CELL_SIZE * self.zoom_level,
                        x * CELL_SIZE * self.zoom_level,
                        CELL_SIZE * self.zoom_level,
                        CELL_SIZE * self.zoom_level
                    )
                    pygame.draw.rect(self.screen, WHITE, rect)
        
        # Dibujar líneas de la grilla (solo si el zoom no es muy pequeño)
        if self.zoom_level >= 0.5:
            for x in range(0, int(WINDOW_WIDTH), int(CELL_SIZE * self.zoom_level)):
                pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT - UI_HEIGHT))
            for y in range(0, int(WINDOW_HEIGHT - UI_HEIGHT), int(CELL_SIZE * self.zoom_level)):
                pygame.draw.line(self.screen, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario con botones"""
        # Fondo del panel de UI
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, WINDOW_HEIGHT - UI_HEIGHT, WINDOW_WIDTH, UI_HEIGHT))
        
        # Definir botones
        button_width = 100
        button_height = 30
        margin = 10
        start_y = WINDOW_HEIGHT - UI_HEIGHT + margin
        
        # Botón Play/Pause
        play_text = "PAUSE" if self.running_simulation else "PLAY"
        play_color = RED if self.running_simulation else GREEN
        self.play_button = pygame.Rect(margin, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, play_color, self.play_button)
        play_surface = self.font.render(play_text, True, WHITE)
        self.screen.blit(play_surface, (margin + 20, start_y + 5))
        
        # Botón Next
        self.next_button = pygame.Rect(margin * 2 + button_width, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.next_button)
        next_surface = self.font.render("NEXT", True, WHITE)
        self.screen.blit(next_surface, (margin * 2 + button_width + 25, start_y + 5))
        
        # Botón Reset
        self.reset_button = pygame.Rect(margin * 3 + button_width * 2, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.reset_button)
        reset_surface = self.font.render("RESET", True, WHITE)
        self.screen.blit(reset_surface, (margin * 3 + button_width * 2 + 20, start_y + 5))
        
        # Botón Speed Up
        self.speed_up_button = pygame.Rect(margin * 4 + button_width * 3, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.speed_up_button)
        speed_up_surface = self.font.render("SPEED +", True, WHITE)
        self.screen.blit(speed_up_surface, (margin * 4 + button_width * 3 + 15, start_y + 5))
        
        # Botón Speed Down
        self.speed_down_button = pygame.Rect(margin * 5 + button_width * 4, start_y, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.speed_down_button)
        speed_down_surface = self.font.render("SPEED -", True, WHITE)
        self.screen.blit(speed_down_surface, (margin * 5 + button_width * 4 + 15, start_y + 5))
        
        # Botón Explanation
        self.explanation_button = pygame.Rect(margin, start_y + button_height + margin, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.explanation_button)
        exp_surface = self.font.render("HELP", True, WHITE)
        self.screen.blit(exp_surface, (margin + 25, start_y + button_height + margin + 5))
        
        # Botón Zoom In
        self.zoom_in_button = pygame.Rect(margin * 2 + button_width, start_y + button_height + margin, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.zoom_in_button)
        zoom_in_surface = self.font.render("ZOOM +", True, WHITE)
        self.screen.blit(zoom_in_surface, (margin * 2 + button_width + 15, start_y + button_height + margin + 5))
        
        # Botón Zoom Out
        self.zoom_out_button = pygame.Rect(margin * 3 + button_width * 2, start_y + button_height + margin, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, self.zoom_out_button)
        zoom_out_surface = self.font.render("ZOOM -", True, WHITE)
        self.screen.blit(zoom_out_surface, (margin * 3 + button_width * 2 + 15, start_y + button_height + margin + 5))
        
        # Mostrar velocidad actual
        speed_text = f"Speed: {self.speed}/10"
        speed_surface = self.small_font.render(speed_text, True, BLACK)
        self.screen.blit(speed_surface, (WINDOW_WIDTH - 100, start_y + 10))
        
        # Mostrar estado
        status_text = "RUNNING" if self.running_simulation else "PAUSED"
        status_surface = self.small_font.render(status_text, True, BLACK)
        self.screen.blit(status_surface, (WINDOW_WIDTH - 100, start_y + 30))
    
    def draw_explanation(self):
        """Dibuja la explicación del juego en una superposición"""
        # Fondo semitransparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Negro semitransparente
        self.screen.blit(overlay, (0, 0))
        
        # Título
        title = self.font.render("JUEGO DE LA VIDA DE CONWAY", True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Reglas
        rules = [
            "REGLAS:",
            "- Una célula viva con menos de 2 vecinos vivos muere (soledad)",
            "- Una célula viva con 2 o 3 vecinos vivos sobrevive",
            "- Una célula viva con más de 3 vecinos vivos muere (sobrepoblación)",
            "- Una célula muerta con exactamente 3 vecinos vivos nace",
            "",
            "CONTROLES:",
            "- Clic izquierdo: Añadir/eliminar células",
            "- PLAY/PAUSE: Iniciar/pausar simulación",
            "- NEXT: Avanzar un paso",
            "- RESET: Reiniciar la grilla",
            "- SPEED +-: Aumentar/disminuir velocidad",
            "- ZOOM +-: Acercar/alejar",
            "- HELP: Mostrar/ocultar esta ayuda"
        ]
        
        for i, line in enumerate(rules):
            text_surface = self.small_font.render(line, True, WHITE)
            self.screen.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2, 100 + i * 25))
        
        # Botón para cerrar
        close_button = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100, 100, 40)
        pygame.draw.rect(self.screen, RED, close_button)
        close_text = self.font.render("CERRAR", True, WHITE)
        self.screen.blit(close_text, (WINDOW_WIDTH // 2 - close_text.get_width() // 2, WINDOW_HEIGHT - 95))
        
        return close_button
    
    def handle_click(self, pos):
        """Maneja los clics del mouse"""
        x, y = pos
        
        # Si estamos en modo explicación, solo manejar el botón de cerrar
        if self.show_explanation:
            close_button = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100, 100, 40)
            if close_button.collidepoint(x, y):
                self.show_explanation = False
            return
        
        # Verificar si el clic fue en la grilla
        if y < WINDOW_HEIGHT - UI_HEIGHT:
            grid_x = int(y / (CELL_SIZE * self.zoom_level))
            grid_y = int(x / (CELL_SIZE * self.zoom_level))
            
            if 0 <= grid_x < GRID_HEIGHT and 0 <= grid_y < GRID_WIDTH:
                # Alternar el estado de la celda
                self.grid[grid_x, grid_y] = 1 - self.grid[grid_x, grid_y]
        
        # Verificar botones de la UI
        elif self.play_button.collidepoint(x, y):
            self.running_simulation = not self.running_simulation
        
        elif self.next_button.collidepoint(x, y):
            self.update_grid()
        
        elif self.reset_button.collidepoint(x, y):
            self.reset_grid()
        
        elif self.speed_up_button.collidepoint(x, y) and self.speed < 10:
            self.speed += 1
        
        elif self.speed_down_button.collidepoint(x, y) and self.speed > 1:
            self.speed -= 1
        
        elif self.explanation_button.collidepoint(x, y):
            self.show_explanation = True
        
        elif self.zoom_in_button.collidepoint(x, y) and self.zoom_level < 2.0:
            self.zoom_level += 0.1
        
        elif self.zoom_out_button.collidepoint(x, y) and self.zoom_level > 0.3:
            self.zoom_level -= 0.1
    
    def run(self):
        """Bucle principal del juego"""
        clock = pygame.time.Clock()
        last_update_time = 0
        
        while True:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic izquierdo
                        self.handle_click(event.pos)
            
            # Actualizar la simulación si está corriendo y ha pasado el tiempo suficiente
            if self.running_simulation and current_time - last_update_time > (1.1 - self.speed * 0.1):
                self.update_grid()
                last_update_time = current_time
            
            # Dibujar todo
            self.draw_grid()
            self.draw_ui()
            
            if self.show_explanation:
                self.draw_explanation()
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    game = GameOfLife()
    game.run()
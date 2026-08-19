# -*- coding: utf-8 -*-
"""
Día 6 - Juego de la Vida de Conway  ·  (pygame + numpy)
-------------------------------------------------------
Versión mejorada de un proyecto propio:
  · Update vectorizado con NumPy (toroidal) → rápido con muchas celdas.
  · Velocidad en generaciones/segundo (por tiempo) + Turbo.
  · Color por 'edad' (nacen brillantes y se enfrían con el tiempo).
  · Dibuja con el mouse (clic y arrastrar) + biblioteca de patrones
    (Glider, Blinker, Nave, Pulsar, Cañón de Gosper) + soup aleatorio.
  · Zoom/paneo con encaje al mundo, pantalla completa (F), controles de mapa.

Controles: Espacio play/pausa · → una generación · R limpiar · A aleatorio
           T turbo · F pantalla completa · +/- velocidad · H ayuda
Ejecuta con "Vida.bat".
"""

import sys
import colorsys
import random

import numpy as np
import pygame

pygame.init()
pygame.font.init()

# ---------------- Config ----------------
GRID_W, GRID_H = 120, 80
ZOOM_FACTORS = [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 9.0, 13.0]
SPEEDS = [1, 2, 3, 5, 8, 12, 20, 30, 45, 60]      # generaciones por SEGUNDO
TURBO_GENS = 20                                    # generaciones por frame en turbo
FPS = 60
EDADES = 48                                        # niveles de color por edad

# ---------------- Colores UI ----------------
BG = (10, 13, 16)
PANEL_BG = (18, 24, 22)
PANEL_LINE = (36, 52, 44)
TXT = (228, 244, 236)
MUTED = (130, 160, 145)
ACCENT = (80, 220, 130)
BTN_BG = (26, 38, 32)
BTN_HOVER = (36, 54, 44)
BTN_BORDER = (52, 78, 64)
GRID_BG = (10, 13, 16)

TITLE_FONT = pygame.font.SysFont("Segoe UI", 24, bold=True)
MED_FONT = pygame.font.SysFont("Segoe UI", 15, bold=True)
SMALL_FONT = pygame.font.SysFont("Segoe UI", 14, bold=True)


def hacer_paleta():
    pal = np.zeros((EDADES, 3), dtype=np.uint8)
    pal[0] = GRID_BG
    pal[1] = (235, 255, 220)                        # recién nacida: destello claro
    for i in range(2, EDADES):
        t = (i - 2) / (EDADES - 3)                  # 0..1
        h = (150 + t * 80) / 360.0                  # verde -> cian -> azul
        v = 1.0 - t * 0.5
        r, g, b = colorsys.hsv_to_rgb(h, 0.75, v)
        pal[i] = (int(r * 255), int(g * 255), int(b * 255))
    return pal


PAL = hacer_paleta()

# ---------------- Patrones (listas de (x, y)) ----------------
PATRONES = {
    "Glider": [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
    "Blinker": [(0, 0), (1, 0), (2, 0)],
    "Nave (LWSS)": [(1, 0), (4, 0), (0, 1), (0, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3)],
    "Pulsar": [
        (2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0),
        (0, 2), (5, 2), (7, 2), (12, 2),
        (0, 3), (5, 3), (7, 3), (12, 3),
        (0, 4), (5, 4), (7, 4), (12, 4),
        (2, 5), (3, 5), (4, 5), (8, 5), (9, 5), (10, 5),
        (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
        (0, 8), (5, 8), (7, 8), (12, 8),
        (0, 9), (5, 9), (7, 9), (12, 9),
        (0, 10), (5, 10), (7, 10), (12, 10),
        (2, 12), (3, 12), (4, 12), (8, 12), (9, 12), (10, 12),
    ],
    "Cañón de Gosper": [
        (0, 4), (0, 5), (1, 4), (1, 5),
        (10, 4), (10, 5), (10, 6), (11, 3), (11, 7), (12, 2), (12, 8), (13, 2), (13, 8),
        (14, 5), (15, 3), (15, 7), (16, 4), (16, 5), (16, 6), (17, 5),
        (20, 2), (20, 3), (20, 4), (21, 2), (21, 3), (21, 4), (22, 1), (22, 5),
        (24, 0), (24, 1), (24, 5), (24, 6),
        (34, 2), (34, 3), (35, 2), (35, 3),
    ],
}
MARGIN = 0


def conway(g):
    N = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1)
         + np.roll(np.roll(g, 1, 0), 1, 1) + np.roll(np.roll(g, 1, 0), -1, 1)
         + np.roll(np.roll(g, -1, 0), 1, 1) + np.roll(np.roll(g, -1, 0), -1, 1))
    return ((N == 3) | ((g == 1) & (N == 2))).astype(np.uint8)


class JuegoVida:
    def __init__(self, size=(1300, 820)):
        self.window_w, self.window_h = size
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Juego de la Vida de Conway")
        self.fullscreen = False
        self._win_size = size

        self.grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
        self.age = np.zeros((GRID_H, GRID_W), dtype=np.int16)
        self.gen = 0
        self.is_running = False
        self.turbo = False
        self.speed_idx = 3          # 5 gen/s
        self._acc = 0.0

        self.zoom_idx = 0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._actualizar_cell()
        self._centrar()

        self.dragging = False       # botón derecho: mover
        self.painting = None        # botón izq: pintar (valor)
        self.last_drag = None
        self.buttons = {}
        self.hover = None

        # empieza VACÍO (para dibujar con clic) con un patrón de ejemplo en el centro
        self.limpiar()
        self.colocar(PATRONES["Cañón de Gosper"])

    # ---------------- simulación ----------------
    def paso(self):
        nueva = conway(self.grid)
        self.age = np.where(nueva == 1, np.minimum(self.age + 1, EDADES - 1), 0).astype(np.int16)
        self.grid = nueva
        self.gen += 1

    def limpiar(self):
        self.grid[:] = 0
        self.age[:] = 0
        self.gen = 0
        self.is_running = False

    def aleatorio(self):
        self.grid = (np.random.random((GRID_H, GRID_W)) < 0.22).astype(np.uint8)
        self.age = self.grid.astype(np.int16)
        self.gen = 0

    def colocar(self, patron):
        gx, gy = self._centro_vista_grid()
        xs = [p[0] for p in patron]; ys = [p[1] for p in patron]
        ox = gx - (max(xs) + min(xs)) // 2
        oy = gy - (max(ys) + min(ys)) // 2
        for px, py in patron:
            x = (ox + px) % GRID_W; y = (oy + py) % GRID_H
            self.grid[y, x] = 1
            self.age[y, x] = max(1, int(self.age[y, x]))

    def pintar(self, sx, sy):
        gx, gy = self.screen_to_grid(sx, sy)
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H and self.painting is not None:
            self.grid[gy, gx] = self.painting
            self.age[gy, gx] = 1 if self.painting else 0

    # ---------------- geometría (encaje al mundo) ----------------
    def panel_w(self):
        return max(300, min(400, int(self.window_w * 0.26)))

    def view_size(self):
        return self.window_w - self.panel_w(), self.window_h

    def _fit_cell(self):
        vw, vh = self.view_size()
        return max(1.0, min(vw / GRID_W, vh / GRID_H))

    def _actualizar_cell(self):
        self.cell = max(1, int(self._fit_cell() * ZOOM_FACTORS[self.zoom_idx]))

    def _centrar(self):
        vw, vh = self.view_size()
        self.pan_x = (vw - GRID_W * self.cell) / 2
        self.pan_y = (vh - GRID_H * self.cell) / 2
        self.limitar_pan()

    def limitar_pan(self):
        vw, vh = self.view_size()
        cw, ch = GRID_W * self.cell, GRID_H * self.cell
        self.pan_x = (vw - cw) / 2 if cw <= vw else max(min(self.pan_x, 0.0), float(vw - cw))
        self.pan_y = (vh - ch) / 2 if ch <= vh else max(min(self.pan_y, 0.0), float(vh - ch))

    def zoom_en(self, pos, acercar):
        old = self.cell
        if acercar and self.zoom_idx < len(ZOOM_FACTORS) - 1:
            self.zoom_idx += 1
        elif not acercar and self.zoom_idx > 0:
            self.zoom_idx -= 1
        self._actualizar_cell()
        if self.cell == old:
            return
        sx, sy = pos
        ox = MARGIN + self.pan_x; oy = MARGIN + self.pan_y
        cellx = (sx - ox) / old; celly = (sy - oy) / old
        self.pan_x += (sx - ox) - cellx * self.cell
        self.pan_y += (sy - oy) - celly * self.cell
        self.limitar_pan()

    def screen_to_grid(self, sx, sy):
        ox = MARGIN + self.pan_x; oy = MARGIN + self.pan_y
        return int((sx - ox) // self.cell), int((sy - oy) // self.cell)

    def _centro_vista_grid(self):
        vw, vh = self.view_size()
        gx, gy = self.screen_to_grid(vw / 2, vh / 2)
        return max(0, min(GRID_W - 1, gx)), max(0, min(GRID_H - 1, gy))

    def _aplicar_pantalla(self, screen):
        ovw, ovh = self.view_size()
        ox = MARGIN + self.pan_x; oy = MARGIN + self.pan_y
        cgx = (ovw / 2 - ox) / self.cell; cgy = (ovh / 2 - oy) / self.cell
        self.screen = screen
        self.window_w, self.window_h = screen.get_size()
        self._actualizar_cell()
        nvw, nvh = self.view_size()
        self.pan_x = nvw / 2 - cgx * self.cell - MARGIN
        self.pan_y = nvh / 2 - cgy * self.cell - MARGIN
        self.limitar_pan()

    def alternar_fullscreen(self):
        if self.fullscreen:
            self.fullscreen = False
            self._aplicar_pantalla(pygame.display.set_mode(self._win_size, pygame.RESIZABLE))
        else:
            self._win_size = (self.window_w, self.window_h)
            self.fullscreen = True
            self._aplicar_pantalla(pygame.display.set_mode((0, 0), pygame.FULLSCREEN))

    # ---------------- iconos ----------------
    def _icono(self, cx, cy, tipo):
        s = self.screen; c = ACCENT
        if tipo == "play":
            pygame.draw.polygon(s, c, [(cx - 6, cy - 8), (cx - 6, cy + 8), (cx + 8, cy)])
        elif tipo == "pause":
            pygame.draw.rect(s, c, (cx - 7, cy - 8, 5, 16)); pygame.draw.rect(s, c, (cx + 2, cy - 8, 5, 16))
        elif tipo == "step":
            pygame.draw.polygon(s, c, [(cx - 8, cy - 8), (cx - 8, cy + 8), (cx + 3, cy)])
            pygame.draw.rect(s, c, (cx + 5, cy - 9, 3, 18))
        elif tipo == "clear":
            pygame.draw.line(s, c, (cx - 7, cy - 7), (cx + 7, cy + 7), 3)
            pygame.draw.line(s, c, (cx + 7, cy - 7), (cx - 7, cy + 7), 3)
        elif tipo == "rand":
            pygame.draw.rect(s, c, (cx - 8, cy - 8, 16, 16), 2, border_radius=3)
            for dx, dy in ((-4, -4), (4, 4), (4, -4), (-4, 4), (0, 0)):
                pygame.draw.circle(s, c, (cx + dx, cy + dy), 2)
        elif tipo == "slow":
            pygame.draw.polygon(s, c, [(cx + 3, cy - 7), (cx + 3, cy + 7), (cx - 5, cy)])
            pygame.draw.rect(s, c, (cx + 4, cy - 7, 3, 14))
        elif tipo in ("fast", "turbo"):
            pygame.draw.polygon(s, c, [(cx - 8, cy - 7), (cx - 8, cy + 7), (cx - 1, cy)])
            pygame.draw.polygon(s, c, [(cx - 1, cy - 7), (cx - 1, cy + 7), (cx + 6, cy)])
        elif tipo == "plus":
            pygame.draw.line(s, c, (cx - 8, cy), (cx + 8, cy), 3); pygame.draw.line(s, c, (cx, cy - 8), (cx, cy + 8), 3)
        elif tipo == "minus":
            pygame.draw.line(s, c, (cx - 8, cy), (cx + 8, cy), 3)
        elif tipo == "target":
            pygame.draw.circle(s, c, (cx, cy), 7, 2); pygame.draw.circle(s, c, (cx, cy), 2, 0)
            pygame.draw.line(s, c, (cx - 11, cy), (cx - 5, cy), 2); pygame.draw.line(s, c, (cx + 5, cy), (cx + 11, cy), 2)
            pygame.draw.line(s, c, (cx, cy - 11), (cx, cy - 5), 2); pygame.draw.line(s, c, (cx, cy + 5), (cx, cy + 11), 2)
        elif tipo == "expand":
            pygame.draw.rect(s, c, (cx - 8, cy - 6, 16, 12), 2)
        elif tipo == "help":
            t = MED_FONT.render("?", True, c); s.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    # ---------------- dibujo ----------------
    def dibujar(self):
        self.screen.fill(BG)
        vw, vh = self.view_size()
        area = pygame.Rect(0, 0, vw, vh)
        pygame.draw.rect(self.screen, GRID_BG, area)

        rgb = PAL[self.age]
        base = pygame.image.frombuffer(rgb.tobytes(), (GRID_W, GRID_H), "RGB")
        cs = self.cell
        ox = MARGIN + self.pan_x; oy = MARGIN + self.pan_y
        gx0 = max(0, int((0 - ox) // cs)); gx1 = min(GRID_W, int((vw - ox) // cs) + 1)
        gy0 = max(0, int((0 - oy) // cs)); gy1 = min(GRID_H, int((vh - oy) // cs) + 1)
        self.screen.set_clip(area)
        if gx1 > gx0 and gy1 > gy0:
            sub = base.subsurface(pygame.Rect(gx0, gy0, gx1 - gx0, gy1 - gy0))
            esc = pygame.transform.scale(sub, ((gx1 - gx0) * cs, (gy1 - gy0) * cs))
            self.screen.blit(esc, (int(ox + gx0 * cs), int(oy + gy0 * cs)))
        self.screen.set_clip(None)

        self._dibujar_panel(int(self.grid.sum()))
        self._controles_mapa()
        pygame.display.flip()

    def _boton(self, rect, label, name, icon=None, on=False):
        col = BTN_HOVER if self.hover == name else BTN_BG
        pygame.draw.rect(self.screen, col, rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT if on else BTN_BORDER, rect, 2 if on else 1, border_radius=8)
        cy = rect.y + rect.h // 2
        if icon:
            self._icono(rect.x + 17, cy, icon)
            t = SMALL_FONT.render(label, True, TXT)
            self.screen.blit(t, (rect.x + 32, cy - t.get_height() // 2))
        else:
            t = SMALL_FONT.render(label, True, TXT)
            self.screen.blit(t, (rect.x + (rect.w - t.get_width()) // 2, cy - t.get_height() // 2))
        self.buttons[name] = rect

    def _boton_mapa(self, rect, name, tipo):
        col = BTN_HOVER if self.hover == name else (22, 32, 28)
        pygame.draw.rect(self.screen, col, rect, border_radius=10)
        pygame.draw.rect(self.screen, BTN_BORDER, rect, 1, border_radius=10)
        self._icono(rect.centerx, rect.centery, tipo)
        self.buttons[name] = rect

    def _controles_mapa(self):
        vw, vh = self.view_size()
        sz, gap, m = 44, 8, 18
        x = vw - sz - m; yb = vh - sz - m
        self._boton_mapa(pygame.Rect(x, yb, sz, sz), "center", "target")
        self._boton_mapa(pygame.Rect(x, yb - (sz + gap), sz, sz), "zoom_out", "minus")
        self._boton_mapa(pygame.Rect(x, yb - 2 * (sz + gap), sz, sz), "zoom_in", "plus")

    def _dibujar_panel(self, vivas):
        pw = self.panel_w(); px = self.window_w - pw
        pygame.draw.rect(self.screen, PANEL_BG, pygame.Rect(px, 0, pw, self.window_h))
        pygame.draw.line(self.screen, PANEL_LINE, (px, 0), (px, self.window_h), 1)
        self.buttons = {}
        mx = px + 18; bw = pw - 36; y = 18
        self.screen.blit(TITLE_FONT.render("Juego de la Vida", True, TXT), (mx, y)); y += 30
        self.screen.blit(SMALL_FONT.render("de Conway · dibuja con el mouse", True, MUTED), (mx, y)); y += 28

        bh = 38; gap = 9; hw = bw // 2 - 5
        self._boton(pygame.Rect(mx, y, hw, bh), "Pausa" if self.is_running else "Play",
                    "play", "pause" if self.is_running else "play")
        self._boton(pygame.Rect(mx + hw + 10, y, hw, bh), "Paso", "step", "step")
        y += bh + gap
        self._boton(pygame.Rect(mx, y, hw, bh), "Limpiar", "clear", "clear")
        self._boton(pygame.Rect(mx + hw + 10, y, hw, bh), "Aleatorio", "rand", "rand")
        y += bh + gap + 4

        self.screen.blit(SMALL_FONT.render("Patrones (aparecen en el centro)", True, MUTED), (mx, y)); y += 20
        pats = list(PATRONES.keys())
        for i, nombre in enumerate(pats):
            r = pygame.Rect(mx + (i % 2) * (hw + 10), y + (i // 2) * (bh + gap), hw, bh)
            self._boton(r, nombre if len(nombre) < 14 else nombre[:12] + "…", "pat_" + str(i))
        y += ((len(pats) + 1) // 2) * (bh + gap) + 4

        v = "TURBO" if self.turbo else f"{SPEEDS[self.speed_idx]} gen/s"
        self.screen.blit(SMALL_FONT.render("Velocidad: " + v, True, MUTED), (mx, y)); y += 20
        self._boton(pygame.Rect(mx, y, hw, bh), "Lento", "slower", "slow")
        self._boton(pygame.Rect(mx + hw + 10, y, hw, bh), "Rápido", "faster", "fast")
        y += bh + gap
        self._boton(pygame.Rect(mx, y, bw, bh),
                    "Turbo: ACTIVADO" if self.turbo else "Turbo (máx. velocidad)",
                    "turbo", "turbo", on=self.turbo)
        y += bh + gap + 4

        self._stat_box(pygame.Rect(mx, y, hw, 56), f"{self.gen:,}", "Generación")
        self._stat_box(pygame.Rect(mx + hw + 10, y, hw, 56), f"{vivas:,}", "Población")
        y += 56 + gap
        self.screen.blit(SMALL_FONT.render(
            "Estado: " + ("EJECUTANDO" if self.is_running else "PAUSADO"), True, ACCENT), (mx, y))

        self._boton(pygame.Rect(mx, self.window_h - 54 - 48, bw, 40),
                    "Salir de pantalla completa (Esc)" if self.fullscreen else "Pantalla completa (F)",
                    "fullscreen", "expand")
        self._boton(pygame.Rect(mx, self.window_h - 54, bw, 40), "Explicación y controles", "help", "help")

    def _stat_box(self, rect, valor, etq):
        pygame.draw.rect(self.screen, BTN_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, PANEL_LINE, rect, 1, border_radius=8)
        v = MED_FONT.render(valor, True, ACCENT)
        self.screen.blit(v, (rect.x + (rect.w - v.get_width()) // 2, rect.y + 8))
        e = SMALL_FONT.render(etq, True, MUTED)
        self.screen.blit(e, (rect.x + (rect.w - e.get_width()) // 2, rect.y + 32))

    # ---------------- acciones ----------------
    def accion(self, name):
        if name == "play":
            self.is_running = not self.is_running
        elif name == "step":
            self.is_running = False; self.paso()
        elif name == "clear":
            self.limpiar()
        elif name == "rand":
            self.aleatorio()
        elif name == "slower":
            self.speed_idx = max(0, self.speed_idx - 1)
        elif name == "faster":
            self.speed_idx = min(len(SPEEDS) - 1, self.speed_idx + 1)
        elif name == "turbo":
            self.turbo = not self.turbo
        elif name == "zoom_in":
            self.zoom_en((self.view_size()[0] // 2, self.window_h // 2), True)
        elif name == "zoom_out":
            self.zoom_en((self.view_size()[0] // 2, self.window_h // 2), False)
        elif name == "center":
            self._centrar()
        elif name == "fullscreen":
            self.alternar_fullscreen()
        elif name == "help":
            self.ayuda()
        elif name.startswith("pat_"):
            self.colocar(list(PATRONES.values())[int(name[4:])])

    # ---------------- eventos ----------------
    def evento(self, e):
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif e.type == pygame.VIDEORESIZE:
            if not self.fullscreen:
                self._aplicar_pantalla(pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE))
        elif e.type == pygame.MOUSEMOTION:
            self.hover = None
            for n, r in self.buttons.items():
                if r.collidepoint(e.pos):
                    self.hover = n; break
            if self.dragging:
                x, y = e.pos; lx, ly = self.last_drag
                self.pan_x += x - lx; self.pan_y += y - ly
                self.last_drag = e.pos; self.limitar_pan()
            elif self.painting is not None:
                self.pintar(*e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if e.button == 1:
                for n, r in self.buttons.items():
                    if r.collidepoint(mx, my):
                        self.accion(n); return
                if mx < self.view_size()[0]:
                    gx, gy = self.screen_to_grid(mx, my)
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        self.painting = 0 if self.grid[gy, gx] else 1
                        self.pintar(mx, my)
            elif e.button == 3:
                self.dragging = True; self.last_drag = e.pos
            elif e.button == 4:
                self.zoom_en(e.pos, True)
            elif e.button == 5:
                self.zoom_en(e.pos, False)
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 3:
                self.dragging = False
            elif e.button == 1:
                self.painting = None
        elif e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx < self.view_size()[0]:
                self.zoom_en((mx, my), e.y > 0)
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                self.is_running = not self.is_running
            elif e.key == pygame.K_f:
                self.alternar_fullscreen()
            elif e.key == pygame.K_ESCAPE and self.fullscreen:
                self.alternar_fullscreen()
            elif e.key == pygame.K_RIGHT:
                self.is_running = False; self.paso()
            elif e.key == pygame.K_r:
                self.limpiar()
            elif e.key == pygame.K_a:
                self.aleatorio()
            elif e.key == pygame.K_t:
                self.turbo = not self.turbo
            elif e.key == pygame.K_h:
                self.ayuda()
            elif e.key in (pygame.K_PLUS, pygame.K_EQUALS):
                self.speed_idx = min(len(SPEEDS) - 1, self.speed_idx + 1)
            elif e.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                self.speed_idx = max(0, self.speed_idx - 1)

    # ---------------- ayuda ----------------
    def ayuda(self):
        L = [
            ("JUEGO DE LA VIDA DE CONWAY", True),
            ("", False),
            ("Autómata celular (John Conway, 1970). Cada célula vive o", False),
            ("muere según sus 8 vecinas:", False),
            ("• Viva con 2 o 3 vecinas → sobrevive.", False),
            ("• Muerta con exactamente 3 vecinas → nace.", False),
            ("• En cualquier otro caso → muere.", False),
            ("De estas reglas surgen naves, osciladores y estructuras vivas.", False),
            ("", False),
            ("El color indica la EDAD de cada célula (nace brillante y se", False),
            ("va enfriando). El mundo es toroidal (los bordes conectan).", False),
            ("", False),
            ("CONTROLES:", False),
            ("• Clic izq (y arrastrar): dibujar / borrar células.", False),
            ("• Clic der + arrastrar: mover · Rueda: zoom.", False),
            ("• Espacio: play/pausa · →: una generación.", False),
            ("• R: limpiar · A: aleatorio · T: turbo · F: pantalla completa.", False),
            ("• Botones de patrones: Glider, Nave, Pulsar, Cañón de Gosper…", False),
            ("", False),
            ("(Clic o cualquier tecla para cerrar)", False),
        ]
        mw = min(self.window_w - 120, 780); mh = min(self.window_h - 120, 640)
        overlay = pygame.Surface((self.window_w, self.window_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        modal = pygame.Rect((self.window_w - mw) // 2, (self.window_h - mh) // 2, mw, mh)
        while True:
            self.screen.blit(overlay, (0, 0))
            pygame.draw.rect(self.screen, (22, 30, 26), modal, border_radius=14)
            pygame.draw.rect(self.screen, (60, 90, 74), modal, 2, border_radius=14)
            y = modal.y + 26
            for txt, es_tit in L:
                f = TITLE_FONT if es_tit else SMALL_FONT
                self.screen.blit(f.render(txt, True, ACCENT if es_tit else TXT), (modal.x + 26, y))
                y += (30 if es_tit else 23)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

    # ---------------- loop ----------------
    def run(self):
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                self.evento(e)
            if self.is_running:
                if self.turbo:
                    for _ in range(TURBO_GENS):
                        self.paso()
                else:
                    self._acc += SPEEDS[self.speed_idx] * dt
                    n = int(self._acc + 1e-9)
                    if n > 0:
                        self._acc -= n
                        for _ in range(min(n, 8)):
                            self.paso()
            self.dibujar()


if __name__ == "__main__":
    JuegoVida().run()

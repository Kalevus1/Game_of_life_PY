# 🟢 Juego de la Vida de Conway

Autor: **KALEVI LATVA AIJO ALEGRIA** · Windows · 100 % local

El **autómata celular** más famoso (John Conway, 1970): con reglas simplísimas sobre una
cuadrícula surgen **naves, osciladores y estructuras "vivas"**. Versión mejorada de un
proyecto propio: rápida, colorida y con biblioteca de patrones.

## ⬇️ Descargar (sin instalar Python)

En **[Releases](../../releases)**: `JuegoDeLaVida_carpeta.zip` → descomprime y ejecuta
**`JuegoDeLaVida.exe`**.
*(Es un `.exe` sin firmar: Windows SmartScreen puede pedir "Más info → Ejecutar de todos modos".)*

## ✨ Qué mejoré respecto a la versión original

- ⚡ **Update vectorizado con NumPy** (toroidal): miles de celdas fluidas, sin el bucle
  celda-por-celda del original.
- ⏱️ **Velocidad en generaciones/segundo** (por tiempo, no por frame) + modo **Turbo**.
- 🎨 **Color por edad:** cada célula nace brillante y se va **enfriando** (verde → cian →
  azul) → el tablero cobra vida.
- ✏️ **Dibuja con el mouse** (clic y arrastrar) y **biblioteca de patrones**: Glider,
  Blinker, Nave (LWSS), Pulsar y el **Cañón de Gosper** (¡dispara gliders sin parar!).
- 🔍 Zoom/paneo con **encaje al mundo**, **pantalla completa (F)** y controles tipo mapa.

## 🧠 Las reglas

Cada célula mira a sus **8 vecinas**:
- **Viva** con **2 o 3** vecinas → sobrevive.
- **Muerta** con exactamente **3** vecinas → **nace**.
- En cualquier otro caso → **muere** (soledad o sobrepoblación).

## ▶️ Controles

| Acción | Cómo |
|--------|------|
| Dibujar / borrar células | Clic izquierdo (y arrastrar) |
| Mover el lienzo | Clic derecho + arrastrar |
| Zoom | Rueda, o botones **＋ / −** del mapa · **◎** centra |
| Play / Pausa | **Espacio** o botón *(empieza en pausa)* |
| Una generación | **→** o botón |
| Limpiar / Aleatorio | **R** / **A** o botones |
| Velocidad (gen/seg) | **+** / **−** · **T** = Turbo |
| Patrones | Botones (aparecen en el centro) |
| Pantalla completa | **F** (Esc para salir) · Ayuda **H** |

## ⚙️ Tecnología

- **Python 3.12** + **pygame** 2.6 + **NumPy**.
- Simulación toroidal con `np.roll` (vectorizada); render con `pygame.image.frombuffer`
  desde una paleta de edad NumPy + recorte por viewport.
- Reutiliza el entorno `..\.venv_face`; si no, `instalar.bat` crea `.venv`.

## 🔨 Generar el `.exe`

`pip install pyinstaller` y doble clic en **`crear_exe.bat`** → queda en `dist\JuegoDeLaVida\`.

---

Desarrollado y documentado por **KALEVI LATVA AIJO ALEGRIA**.

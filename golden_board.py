# golden_board.py
import pygame
import sys
import os

# Handle PyInstaller temp path (works with GitHub Actions too)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load icon
icon_path = resource_path("icon.icns")  # macOS requires .icns
try:
    pygame.display.set_icon(pygame.image.load(icon_path))
except Exception as e:
    print("Icon load error:", e)

pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Golden Board")

BLACK = (0, 0, 0)
RED = (220, 20, 60)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
DARK = (17, 17, 17)
font = pygame.font.SysFont("Arial", 40, bold=True)

dots = set()
connections = []
selected = []
last_click_time = {}
DOUBLE_CLICK_DELAY = 400

def get_board_metrics():
    board_size = min(screen.get_width(), screen.get_height())
    square_size = board_size // COLS
    offset_x = (screen.get_width() - board_size) // 2
    offset_y = (screen.get_height() - board_size) // 2
    return board_size, square_size, offset_x, offset_y

def get_square_index(pos):
    x, y = pos
    board_size, square_size, offset_x, offset_y = get_board_metrics()
    if not (offset_x <= x < offset_x + board_size and offset_y <= y < offset_y + board_size):
        return None
    col = (x - offset_x) // square_size
    row = (y - offset_y) // square_size
    return row, col

def get_square_num(row, col):
    return (ROWS - 1 - row) * COLS + col + 1

def draw_grid():
    board_size, square_size, offset_x, offset_y = get_board_metrics()
    for row in range(ROWS):
        for col in range(COLS):
            x = offset_x + col * square_size
            y = offset_y + row * square_size
            rect = pygame.Rect(x, y, square_size, square_size)
            color = BLACK if (row + col) % 2 == 0 else RED
            pygame.draw.rect(screen, color, rect)
            square_num = get_square_num(row, col)
            num_color = GOLD if (row, col) in dots else WHITE
            num_text = font.render(str(square_num), True, num_color)
            text_rect = num_text.get_rect(center=(x + square_size // 2, y + square_size // 2))
            screen.blit(num_text, text_rect)

def draw_lines():
    board_size, square_size, offset_x, offset_y = get_board_metrics()
    for (r1, c1), (r2, c2) in connections:
        x1 = offset_x + c1 * square_size + square_size // 2
        y1 = offset_y + r1 * square_size + square_size // 2
        x2 = offset_x + c2 * square_size + square_size // 2
        y2 = offset_y + r2 * square_size + square_size // 2
        pygame.draw.line(screen, GOLD, (x1, y1), (x2, y2), 5)

def remove_connections_at(pos):
    global connections
    connections = [conn for conn in connections if pos not in conn]
    dots.discard(pos)

running = True
while running:
    screen.fill(DARK)
    draw_grid()
    draw_lines()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            square_pos = get_square_index(pos)
            if not square_pos:
                continue
            row, col = square_pos
            square = (row, col)
            current_time = pygame.time.get_ticks()
            if event.button == 1:
                last_time = last_click_time.get(square, 0)
                if current_time - last_time < DOUBLE_CLICK_DELAY:
                    remove_connections_at(square)
                    selected.clear()
                else:
                    if square not in selected:
                        dots.add(square)
                        selected.append(square)
                        if len(selected) == 2:
                            connections.append((selected[0], selected[1]))
                            selected.clear()
                last_click_time[square] = current_time

pygame.quit()
sys.exit()

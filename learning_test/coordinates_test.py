import pygame

pygame.init()

# ==========================================
# DISPLAY SETTINGS
# ==========================================

# Widened screen slightly to comfortably fit the input boxes
SCREEN_WIDTH = 1050 
SCREEN_HEIGHT = 650
SCALE = 2                 # 1 graph unit = 2 screen pixels
GRAPH_LEFT = 50
GRAPH_TOP = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Interactive Pygame Collision Visualizer (Type & Drag)")

font = pygame.font.Font(None, 25)
small_font = pygame.font.Font(None, 20)
clock = pygame.time.Clock()

# ==========================================
# RECTANGLES & INITIAL VALUES
# ==========================================

snake_rect = pygame.Rect(100, 100, 20, 20)
apple_rect = pygame.Rect(110, 110, 20, 20)

# ==========================================
# HELPERS & INPUT BOX CLASS
# ==========================================

def graph_to_screen(x, y):
    screen_x = GRAPH_LEFT + x * SCALE
    screen_y = GRAPH_TOP + y * SCALE
    return screen_x, screen_y

def screen_to_graph(screen_x, screen_y):
    x = (screen_x - GRAPH_LEFT) / SCALE
    y = (screen_y - GRAPH_TOP) / SCALE
    return x, y

def draw_text(text, x, y, color=(35, 35, 35), selected_font=small_font):
    image = selected_font.render(text, True, color)
    screen.blit(image, (x, y))

class InputBox:
    def __init__(self, x, y, w, h, label, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (200, 204, 210)
        self.color_active = (52, 152, 219)
        self.color = self.color_inactive
        self.label = label
        self.text = str(initial_val)
        self.active = False
        self.txt_surface = font.render(self.text, True, (35, 35, 35))

    def handle_event(self, event):
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on click position
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive
                
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    changed = True
                # Allow numbers and minus sign
                elif event.unicode.isnumeric() or (event.unicode == '-' and len(self.text) == 0):
                    self.text += event.unicode
                    changed = True
                    
        if changed:
            self.txt_surface = font.render(self.text, True, (35, 35, 35))
        return changed

    def update_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self.txt_surface = font.render(self.text, True, (35, 35, 35))

    def draw(self, surface):
        # Draw label
        label_surf = font.render(self.label, True, (100, 100, 100))
        surface.blit(label_surf, (self.rect.x - label_surf.get_width() - 5, self.rect.y + 6))
        # Draw input rectangle background & border
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)
        # Draw text inside
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 6))

    def get_value(self):
        try:
            return int(self.text)
        except ValueError:
            return 0  # Default to 0 if box is empty or just a minus sign

# Create Input Boxes
input_boxes = {
    'sx': InputBox(730, 70, 50, 30, 'X:', snake_rect.x),
    'sy': InputBox(840, 70, 50, 30, 'Y:', snake_rect.y),
    'sw': InputBox(730, 110, 50, 30, 'W:', snake_rect.width),
    'sh': InputBox(840, 110, 50, 30, 'H:', snake_rect.height),
    
    'ax': InputBox(730, 180, 50, 30, 'X:', apple_rect.x),
    'ay': InputBox(840, 180, 50, 30, 'Y:', apple_rect.y),
    'aw': InputBox(730, 220, 50, 30, 'W:', apple_rect.width),
    'ah': InputBox(840, 220, 50, 30, 'H:', apple_rect.height),
}

# ==========================================
# MAIN WINDOW LOOP
# ==========================================

running = True
dragging_snake = False
dragging_apple = False
offset_x = 0
offset_y = 0

while running:
    # 1. HANDLE EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Handle keyboard typing in boxes
        for key, box in input_boxes.items():
            if box.handle_event(event):
                # If text changed, instantly apply new values to rects
                snake_rect.x = input_boxes['sx'].get_value()
                snake_rect.y = input_boxes['sy'].get_value()
                snake_rect.width = input_boxes['sw'].get_value()
                snake_rect.height = input_boxes['sh'].get_value()
                
                apple_rect.x = input_boxes['ax'].get_value()
                apple_rect.y = input_boxes['ay'].get_value()
                apple_rect.width = input_boxes['aw'].get_value()
                apple_rect.height = input_boxes['ah'].get_value()
            
        # Handle Mouse Dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            s_sx, s_sy = graph_to_screen(snake_rect.x, snake_rect.y)
            s_rect = pygame.Rect(s_sx, s_sy, snake_rect.width * SCALE, snake_rect.height * SCALE)
            
            a_sx, a_sy = graph_to_screen(apple_rect.x, apple_rect.y)
            a_rect = pygame.Rect(a_sx, a_sy, apple_rect.width * SCALE, apple_rect.height * SCALE)
            
            gx, gy = screen_to_graph(mx, my)

            # Prioritize clicking inputs over dragging rectangles
            clicked_on_input = any(box.rect.collidepoint(mx, my) for box in input_boxes.values())
            
            if not clicked_on_input:
                if s_rect.collidepoint(mx, my):
                    dragging_snake = True
                    offset_x = snake_rect.x - gx
                    offset_y = snake_rect.y - gy
                elif a_rect.collidepoint(mx, my):
                    dragging_apple = True
                    offset_x = apple_rect.x - gx
                    offset_y = apple_rect.y - gy

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging_snake = False
            dragging_apple = False

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            gx, gy = screen_to_graph(mx, my)
            if dragging_snake:
                snake_rect.x = int(gx + offset_x)
                snake_rect.y = int(gy + offset_y)
                # Sync dragging back to text boxes
                input_boxes['sx'].update_text(str(snake_rect.x))
                input_boxes['sy'].update_text(str(snake_rect.y))
            elif dragging_apple:
                apple_rect.x = int(gx + offset_x)
                apple_rect.y = int(gy + offset_y)
                # Sync dragging back to text boxes
                input_boxes['ax'].update_text(str(apple_rect.x))
                input_boxes['ay'].update_text(str(apple_rect.y))

    # 2. UPDATE COLLISION CONDITIONS
    condition_1 = snake_rect.left < apple_rect.right
    condition_2 = snake_rect.right > apple_rect.left
    condition_3 = snake_rect.top < apple_rect.bottom
    condition_4 = snake_rect.bottom > apple_rect.top

    collision = condition_1 and condition_2 and condition_3 and condition_4

    checks = [
        ("snake.left < apple.right", f"{snake_rect.left} < {apple_rect.right}", condition_1),
        ("snake.right > apple.left", f"{snake_rect.right} > {apple_rect.left}", condition_2),
        ("snake.top < apple.bottom", f"{snake_rect.top} < {apple_rect.bottom}", condition_3),
        ("snake.bottom > apple.top", f"{snake_rect.bottom} > {apple_rect.top}", condition_4),
    ]

    # 3. DRAW EVERYTHING
    screen.fill((248, 249, 251))

    # Draw graph grid
    for x in range(0, 301, 10):
        screen_x = GRAPH_LEFT + x * SCALE
        pygame.draw.line(screen, (220, 224, 230), (screen_x, GRAPH_TOP), (screen_x, GRAPH_TOP + 500), 1)
        if x % 20 == 0:
            draw_text(str(x), screen_x - 8, GRAPH_TOP + 505)

    for y in range(0, 251, 10):
        screen_y = GRAPH_TOP + y * SCALE
        pygame.draw.line(screen, (220, 224, 230), (GRAPH_LEFT, screen_y), (GRAPH_LEFT + 600, screen_y), 1)
        if y % 20 == 0:
            draw_text(str(y), GRAPH_LEFT - 30, screen_y - 8)

    # Draw Snake Rectangle (Green)
    snake_sx, snake_sy = graph_to_screen(snake_rect.x, snake_rect.y)
    snake_w, snake_h = snake_rect.width * SCALE, snake_rect.height * SCALE
    if snake_w > 0 and snake_h > 0:
        pygame.draw.rect(screen, (165, 214, 167), (snake_sx, snake_sy, snake_w, snake_h))
        pygame.draw.rect(screen, (56, 142, 60), (snake_sx, snake_sy, snake_w, snake_h), 2)
        draw_text("Snake", snake_sx + 4, snake_sy - 15, (56, 142, 60))

    # Draw Apple Rectangle (Red)
    apple_sx, apple_sy = graph_to_screen(apple_rect.x, apple_rect.y)
    apple_w, apple_h = apple_rect.width * SCALE, apple_rect.height * SCALE
    if apple_w > 0 and apple_h > 0:
        apple_surf = pygame.Surface((apple_w, apple_h), pygame.SRCALPHA)
        apple_surf.fill((239, 154, 154, 180)) 
        pygame.draw.rect(apple_surf, (211, 47, 47, 255), (0, 0, apple_w, apple_h), 2)
        screen.blit(apple_surf, (apple_sx, apple_sy))
        draw_text("Apple", apple_sx + 4, apple_sy + apple_h + 4, (211, 47, 47))

    # Draw Right Panel
    panel_x = GRAPH_LEFT + 630
    
    # Draw Inputs
    draw_text("Snake Dimensions", panel_x, GRAPH_TOP, (56, 142, 60), font)
    draw_text("Apple Dimensions", panel_x, GRAPH_TOP + 110, (211, 47, 47), font)
    
    for box in input_boxes.values():
        box.draw(screen)

    # Draw Collision Results
    panel_y = GRAPH_TOP + 230
    status_color = (56, 142, 60) if collision else (211, 47, 47)
    draw_text(f"COLLISION DETECTED: {collision}", panel_x, panel_y, status_color, font)
    
    panel_y += 40

    for name, value, cond in checks:
        color = (56, 142, 60) if cond else (211, 47, 47)
        draw_text(name, panel_x, panel_y, (50, 50, 50), font)
        draw_text(f"{value}  =>  {cond}", panel_x, panel_y + 20, color, font)
        panel_y += 50

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
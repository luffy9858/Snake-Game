import pygame
import random
import os
import sys

# ==============================================================================
# SIZES & CONFIGURATION
# ==============================================================================
display_size_1 = 600
display_size_2 = 600

apple_size = 20
bomb_size = 20
snake_size = 20
current_size_x = 500
current_size_y = 500

grid_cols = display_size_1 // snake_size  # 30 columns
grid_rows = display_size_2 // snake_size  # 30 rows


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ==============================================================================
# BOMB & OBSTACLES
# ==============================================================================
class Bomb:
    def __init__(self, x, y, reason="Initial Guard"):
        self.x = x
        self.y = y
        self.grid_x = x // bomb_size
        self.grid_y = y // bomb_size
        self.rect = pygame.Rect(self.x, self.y, bomb_size, bomb_size)
        self.reason = reason
        # Pulse timer counts down frames to display the flashing warning rectangle
        self.pulse_timer = 25

    def update_position(self, grid_x, grid_y, reason="Relocated"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * bomb_size
        self.y = grid_y * bomb_size
        self.rect.topleft = (self.x, self.y)
        self.reason = reason
        self.pulse_timer = 25  # Trigger visual alert rectangle when moved


class Obstacles:
    def __init__(self, parent_screen, game):
        self.parent = parent_screen
        self.game = game
        self.bomb_image = pygame.image.load(resource_path("assets/bomb.png"))
        self.bomb_image = pygame.transform.scale(self.bomb_image, (bomb_size, bomb_size))
        self.bombs = []

    def max_bombs_for_score(self, score):
        # Starts with 1 bomb, reaches 4, and scales up to 6 bombs as score rises
        if score < 3:
            return 1
        elif score < 7:
            return 2
        elif score < 12:
            return 3
        elif score < 18:
            return 4
        elif score < 25:
            return 5
        else:
            return 6

    def get_bomb_cells(self):
        return {(b.grid_x, b.grid_y) for b in self.bombs}

    def bomb_draw(self):
        for bomb in self.bombs:
            self.parent.blit(self.bomb_image, (bomb.x, bomb.y))
            # Flashing warning rectangle around the bomb
            if bomb.pulse_timer > 0:
                flash_color = (255, 50, 50) if (bomb.pulse_timer // 3) % 2 == 0 else (255, 230, 60)
                pygame.draw.rect(self.parent, flash_color, bomb.rect, 2)
                bomb.pulse_timer -= 1

    def check_bomb_collision(self, head_rect):
        for bomb in self.bombs:
            if head_rect.colliderect(bomb.rect):
                return True, bomb
        return False, None

    def spawn_initial_bomb(self, snake_positions, food_pos):
        self.bombs = []
        forbidden = set(snake_positions) | {food_pos}
        for _ in range(50):
            gx = random.randint(8, grid_cols - 9)
            gy = random.randint(8, grid_rows - 9)
            if (gx, gy) not in forbidden:
                bomb = Bomb(gx * bomb_size, gy * bomb_size, "Initial Guard")
                self.bombs.append(bomb)
                return bomb

        bomb = Bomb(12 * bomb_size, 12 * bomb_size, "Initial Guard")
        self.bombs.append(bomb)
        return bomb

    def add_or_relocate_bomb(self, target_gx, target_gy, reason, snake_positions, food_pos, current_score):
        snake_grid = {(px // snake_size, py // snake_size) for px, py in snake_positions}
        occupied = snake_grid | {food_pos} | self.get_bomb_cells()

        if (target_gx, target_gy) in occupied:
            found = False
            for radius in range(1, 4):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        cand = ((target_gx + dx) % grid_cols, (target_gy + dy) % grid_rows)
                        if cand not in occupied:
                            target_gx, target_gy = cand
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

        max_allowed = self.max_bombs_for_score(current_score)

        if len(self.bombs) < max_allowed:
            new_bomb = Bomb(target_gx * bomb_size, target_gy * bomb_size, reason)
            self.bombs.append(new_bomb)
            return new_bomb, "spawned"
        else:
            if not self.bombs:
                new_bomb = Bomb(target_gx * bomb_size, target_gy * bomb_size, reason)
                self.bombs.append(new_bomb)
                return new_bomb, "spawned"

            head_x, head_y = snake_positions[0]
            head_gx = head_x // snake_size
            head_gy = head_y // snake_size

            farthest_bomb = max(
                self.bombs,
                key=lambda b: abs(b.grid_x - head_gx) + abs(b.grid_y - head_gy)
            )
            farthest_bomb.update_position(target_gx, target_gy, reason)
            return farthest_bomb, "relocated"


# ==============================================================================
# FOOD (CHESS GAMBIT SPAWNING)
# ==============================================================================
class Food:
    def __init__(self, parent_food_null):
        self.parent_food_null = parent_food_null
        self.food_image = pygame.image.load(resource_path("assets/apple.png"))
        self.food_image = pygame.transform.scale(self.food_image, (apple_size, apple_size))
        self.x = 300
        self.y = 200
        self.grid_x = self.x // apple_size
        self.grid_y = self.y // apple_size
        self.rect = pygame.Rect(self.x, self.y, apple_size, apple_size)

    def food_draw(self):
        self.parent_food_null.blit(self.food_image, (self.x, self.y))
        self.rect.topleft = (self.x, self.y)

    def spawn_apple(self):
        self.grid_x = random.randint(0, grid_cols - 1)
        self.grid_y = random.randint(0, grid_rows - 1)
        self.x = self.grid_x * apple_size
        self.y = self.grid_y * apple_size
        self.rect.topleft = (self.x, self.y)

    def spawn_strategic_apple(self, snake, obstacles, tracking, score):
        snake_grid = {(px // snake_size, py // snake_size) for px, py in snake.positions}
        bomb_cells = obstacles.get_bomb_cells()
        head_x, head_y = snake.positions[0]
        head_gx = head_x // snake_size
        head_gy = head_y // snake_size

        candidates = []
        for gx in range(grid_cols):
            for gy in range(grid_rows):
                pos = (gx, gy)
                if pos in snake_grid or pos in bomb_cells:
                    continue

                dx = min(abs(gx - head_gx), grid_cols - abs(gx - head_gx))
                dy = min(abs(gy - head_gy), grid_rows - abs(gy - head_gy))
                dist = dx + dy

                if dist < 4:
                    continue

                candidates.append((pos, dist))

        if not candidates:
            self.spawn_apple()
            return

        def evaluate_spot(candidate):
            pos, dist = candidate
            gx, gy = pos

            open_exits = 0
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx = (gx + ox) % grid_cols
                ny = (gy + oy) % grid_rows
                if (nx, ny) not in snake_grid and (nx, ny) not in bomb_cells:
                    open_exits += 1

            if open_exits < 2:
                return -9999

            dist_score = 30 - abs(dist - 12) * 2

            if bomb_cells:
                min_bomb_dist = min(
                    min(abs(gx - bx), grid_cols - abs(gx - bx)) + min(abs(gy - by), grid_rows - abs(gy - by))
                    for bx, by in bomb_cells
                )
            else:
                min_bomb_dist = 10

            if score < 5:
                danger_score = min_bomb_dist
            else:
                danger_score = 25 - abs(min_bomb_dist - 2) * 6

            visits = tracking.snake_area_visited.get(pos, 0)
            comfort_penalty = visits * 2

            return dist_score + danger_score - comfort_penalty

        best_pos, _ = max(candidates, key=evaluate_spot)
        self.grid_x, self.grid_y = best_pos
        self.x = self.grid_x * apple_size
        self.y = self.grid_y * apple_size
        self.rect.topleft = (self.x, self.y)


# ==============================================================================
# SNAKE PLAYER
# ==============================================================================
class Snake:
    def __init__(self, parent_null, game):
        self.game = game
        self.parent_null = parent_null

        self.snake_image = pygame.image.load(resource_path("assets/white eye circle.png"))
        self.snake_image = pygame.transform.scale(self.snake_image, (snake_size, snake_size))

        self.snake_body = pygame.image.load(resource_path("assets/snake_back.png"))
        self.snake_body = pygame.transform.scale(self.snake_body, (snake_size, snake_size))

        self.positions = [(100, 100), (80, 100), (60, 100)]
        self.direction = "right"
        self.direction_queue = []

        head_x, head_y = self.positions[0]
        self.head_rect = pygame.Rect(head_x, head_y, snake_size, snake_size)
        self.should_grow = False
        self.game_over = False

    def collision_own(self):
        head_pos = self.positions[0]
        if head_pos in self.positions[1:]:
            self.game_over = True
            return True
        return False

    def draw(self):
        for i, position in enumerate(self.positions):
            if i == 0:
                self.parent_null.blit(self.snake_image, position)
            else:
                self.parent_null.blit(self.snake_body, position)

    def queue_direction(self, new_dir):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        last_dir = self.direction_queue[-1] if self.direction_queue else self.direction

        if new_dir != last_dir and new_dir != opposites.get(last_dir):
            if len(self.direction_queue) < 2:
                self.direction_queue.append(new_dir)

    def move_down(self):
        self.queue_direction("down")

    def move_up(self):
        self.queue_direction("up")

    def move_right(self):
        self.queue_direction("right")

    def move_left(self):
        self.queue_direction("left")

    def movement(self):
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)

        head_x, head_y = self.positions[0]

        if self.direction == "up":
            head_y -= snake_size
        elif self.direction == "down":
            head_y += snake_size
        elif self.direction == "left":
            head_x -= snake_size
        elif self.direction == "right":
            head_x += snake_size

        if head_x < 0:
            head_x = display_size_1 - snake_size
        elif head_x >= display_size_1:
            head_x = 0
        if head_y < 0:
            head_y = display_size_2 - snake_size
        elif head_y >= display_size_2:
            head_y = 0

        new_head = (head_x, head_y)
        self.positions.insert(0, new_head)

        if not self.should_grow:
            self.positions.pop()
        else:
            self.should_grow = False

        self.head_rect.topleft = self.positions[0]

        self.game.tracking.record_position(self.positions[0])
        self.game.tracking.record_direction(self.direction)

        self.collision_own()


# ==============================================================================
# PATTERN DETECTION AI
# ==============================================================================
class Tracking:
    def __init__(self, game):
        self.game = game
        self.snake_area_visited = {}
        self.recent_positions = []
        self.recent_directions = []
        self.moves_since_eat = 0
        self.ambush_cooldown = 0

    def record_position(self, position):
        grid_pos = (position[0] // snake_size, position[1] // snake_size)
        self.snake_area_visited[grid_pos] = self.snake_area_visited.get(grid_pos, 0) + 1
        self.recent_positions.append(grid_pos)
        if len(self.recent_positions) > 35:
            self.recent_positions.pop(0)

    def record_direction(self, direction):
        self.recent_directions.append(direction)
        if len(self.recent_directions) > 40:
            self.recent_directions.pop(0)

    def detect_repetition(self):
        moves = self.recent_directions
        for pattern_len in (2, 3, 4, 5, 6):
            if len(moves) >= pattern_len * 2:
                last_slice = moves[-pattern_len:]
                prev_slice = moves[-pattern_len * 2 : -pattern_len]
                if last_slice == prev_slice and len(set(last_slice)) > 1:
                    pattern_type = "ZIG-ZAG" if pattern_len == 2 else "LOOP"
                    return True, pattern_type, last_slice
        return False, None, []

    def detect_wall_hugging(self):
        if len(self.recent_positions) >= 14:
            wall_moves = sum(
                1 for x, y in self.recent_positions[-14:]
                if x in (0, grid_cols - 1) or y in (0, grid_rows - 1)
            )
            return wall_moves >= 10
        return False

    def detect_straight_rush(self):
        if len(self.recent_directions) >= 9:
            return len(set(self.recent_directions[-9:])) == 1
        return False

    def get_direction_vector(self, direction):
        if direction == "up":
            return (0, -1)
        elif direction == "down":
            return (0, 1)
        elif direction == "left":
            return (-1, 0)
        elif direction == "right":
            return (1, 0)
        return (0, 0)

    def update_ai_strategy(self):
        self.moves_since_eat += 1

        if self.ambush_cooldown > 0:
            self.ambush_cooldown -= 1

        # Anti-Stall: If player cowers/circles for too long, relocate food & bomb
        stall_limit = max(45, 90 - self.game.score_int * 2)
        if self.moves_since_eat > stall_limit:
            self.moves_since_eat = 0
            self.game.food.spawn_strategic_apple(self.game.snake, self.game.obstacle, self, self.game.score_int)
            head_x, head_y = self.game.snake.positions[0]
            dx, dy = self.get_direction_vector(self.game.snake.direction)
            ambush_gx = (head_x // snake_size + dx * 4) % grid_cols
            ambush_gy = (head_y // snake_size + dy * 4) % grid_rows
            self.game.obstacle.add_or_relocate_bomb(
                ambush_gx, ambush_gy, "Anti-Stall", self.game.snake.positions,
                (self.game.food.grid_x, self.game.food.grid_y), self.game.score_int
            )
            return

        # Pattern Ambush: Drop a bomb 3 tiles ahead in their forward path
        if self.ambush_cooldown == 0:
            has_rep, ptype, _ = self.detect_repetition()
            if has_rep:
                self.ambush_cooldown = max(10, 22 - self.game.score_int // 3)
                head_x, head_y = self.game.snake.positions[0]
                dx, dy = self.get_direction_vector(self.game.snake.direction)
                ambush_gx = (head_x // snake_size + dx * 3) % grid_cols
                ambush_gy = (head_y // snake_size + dy * 3) % grid_rows
                self.game.obstacle.add_or_relocate_bomb(
                    ambush_gx, ambush_gy, f"Ambush_{ptype}", self.game.snake.positions,
                    (self.game.food.grid_x, self.game.food.grid_y), self.game.score_int
                )
                try:
                    self.game.lvl_up_sound.play()
                except Exception:
                    pass
                return

            if self.detect_wall_hugging():
                self.ambush_cooldown = 18
                head_x, head_y = self.game.snake.positions[0]
                dx, dy = self.get_direction_vector(self.game.snake.direction)
                ambush_gx = (head_x // snake_size + dx * 4) % grid_cols
                ambush_gy = (head_y // snake_size + dy * 4) % grid_rows
                self.game.obstacle.add_or_relocate_bomb(
                    ambush_gx, ambush_gy, "Border_Trap", self.game.snake.positions,
                    (self.game.food.grid_x, self.game.food.grid_y), self.game.score_int
                )
                return

            if self.detect_straight_rush():
                self.ambush_cooldown = 20
                head_x, head_y = self.game.snake.positions[0]
                dx, dy = self.get_direction_vector(self.game.snake.direction)
                ambush_gx = (head_x // snake_size + dx * 4) % grid_cols
                ambush_gy = (head_y // snake_size + dy * 4) % grid_rows
                self.game.obstacle.add_or_relocate_bomb(
                    ambush_gx, ambush_gy, "Intercept", self.game.snake.positions,
                    (self.game.food.grid_x, self.game.food.grid_y), self.game.score_int
                )
                return


# ==============================================================================
# MAIN GAME
# ==============================================================================
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.eat_sound = pygame.mixer.Sound(resource_path("assets/sfx/apple_bite.wav"))
        self.g_over_sound = pygame.mixer.Sound(resource_path("assets/sfx/game_over.wav"))
        self.lvl_up_sound = pygame.mixer.Sound(resource_path("assets/sfx/level_up.wav"))
        self.start_s_sound = pygame.mixer.Sound(resource_path("assets/sfx/start_screen.wav"))
        self.game_enter_sound = pygame.mixer.Sound(resource_path("assets/sfx/game_enter.wav"))
        self.collision_sound = pygame.mixer.Sound(resource_path("assets/sfx/collision.wav"))
        self.game_enter_sound.set_volume(0.5)

        self.screen = pygame.display.set_mode((display_size_1, display_size_2))
        self.font = resource_path('assets/fonts/MinecraftRegular-Bmg3.otf')

        self.grid = pygame.image.load(resource_path("assets/grid.png"))
        self.grid = pygame.transform.scale(self.grid, (display_size_1, display_size_2))

        self.clock = pygame.time.Clock()
        self.start = True

        self.reset_game()

    def render_bg(self):
        self.screen.blit(self.grid, (0, 0))

    def reset_game(self):
        self.tracking = Tracking(self)
        self.snake = Snake(self.screen, self)
        self.food = Food(self.screen)
        self.obstacle = Obstacles(self.screen, self)

        # Starts with 1 bomb
        self.obstacle.spawn_initial_bomb(self.snake.positions, (self.food.grid_x, self.food.grid_y))

        self.score_int = 0
        self.game_state = "playing"
        self.game_confirm = False
        self.base_difficulty = 6
        self.game_over_time = 0
        self.death_reason = ""
        self.tracking.record_position(self.snake.positions[0])

    def dynamic_scaling(self, x, y):
        self.x = x / current_size_x
        self.y = y / current_size_y
        true_x = self.x * display_size_1
        true_y = self.y * display_size_2
        main_tuple = (true_x, true_y)
        return main_tuple

    def display_score(self):
        font = pygame.font.Font(self.font, 20)
        self.score = font.render(f"Score: {self.score_int}", False, (255, 255, 255))
        self.screen.blit(self.score, self.dynamic_scaling(380, 20))

    def update_difficulty(self):
        # Speed scales smoothly from 6 FPS to 18 FPS at score 30
        target_fps = min(18, 6 + int((self.score_int / 30.0) * 12))
        self.base_difficulty = target_fps

        target_bombs = self.obstacle.max_bombs_for_score(self.score_int)
        if len(self.obstacle.bombs) < target_bombs:
            head_x, head_y = self.snake.positions[0]
            dx, dy = self.tracking.get_direction_vector(self.snake.direction)
            spawn_gx = (head_x // snake_size + dx * 4) % grid_cols
            spawn_gy = (head_y // snake_size + dy * 4) % grid_rows

            self.obstacle.add_or_relocate_bomb(
                spawn_gx, spawn_gy, "Score_Milestone", self.snake.positions,
                (self.food.grid_x, self.food.grid_y), self.score_int
            )
            self.lvl_up_sound.play()

    def draw_screen(self):
        self.render_bg()
        self.food.food_draw()
        self.obstacle.bomb_draw()
        self.snake.draw()
        self.display_score()
        pygame.display.flip()

    def game_over_screen(self):
        self.render_bg()

        # "Game over!" in Red
        font = pygame.font.Font(self.font, 30)
        self.over = font.render(f"Game over!", False, (255, 60, 60))
        game_over = self.over.get_rect(center=self.dynamic_scaling(250, 185))
        self.screen.blit(self.over, game_over)

        # "Score: X" in White
        self.score = font.render(f"Score: {self.score_int}", False, (255, 255, 255))
        score_more = self.score.get_rect(center=self.dynamic_scaling(250, 235))
        self.screen.blit(self.score, score_more)

        # "Press R to restart" in Green
        font_2 = pygame.font.Font(self.font, 20)
        self.restart = font_2.render(f"Press R to restart", False, (80, 240, 80))
        restart = self.restart.get_rect(center=self.dynamic_scaling(250, 285))
        self.screen.blit(self.restart, restart)

        # "Press Esc to quit" in White
        font_3 = pygame.font.Font(self.font, 16)
        self.quit_hint = font_3.render(f"Press Esc to quit", False, (255, 255, 255))
        quit_hint_rect = self.quit_hint.get_rect(center=self.dynamic_scaling(250, 325))
        self.screen.blit(self.quit_hint, quit_hint_rect)

        pygame.display.flip()

    def start_screen(self):
        self.render_bg()
        font = pygame.font.Font(self.font, 20)
        font_render = font.render(f"Press 'Enter' to start the Game!", False, (255, 255, 255))
        font_render_adjusted = font_render.get_rect(center=self.dynamic_scaling(250, 250))
        self.screen.blit(font_render, font_render_adjusted)
        pygame.display.flip()

    def quit_confirmation(self):
        self.render_bg()
        font = pygame.font.Font(self.font, 15)
        self.quit = font.render(f"Do you want to quit the game?", True, (255, 255, 255))
        quit_rect = self.quit.get_rect(center=self.dynamic_scaling(250, 200))
        self.screen.blit(self.quit, quit_rect)

        font_2 = pygame.font.Font(self.font, 15)
        self.confirm = font_2.render(f"Press Y to confirm or any other key to Cancel!", True, (255, 255, 255))
        confirm_rect = self.confirm.get_rect(center=self.dynamic_scaling(250, 240))
        self.screen.blit(self.confirm, confirm_rect)

        pygame.display.flip()

    def run(self):
        running = True
        self.start_s_sound.play()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    self.start_s_sound.stop()

                    if event.key == pygame.K_ESCAPE and not self.start:
                        if self.game_state == "playing":
                            self.game_confirm = True
                            continue
                        elif self.game_state == "game over" and not self.game_confirm:
                            self.game_confirm = True
                            continue

                    # Quit confirmation state
                    if self.game_confirm:
                        if event.key == pygame.K_y:
                            running = False
                            break
                        else:
                            self.game_confirm = False
                            continue

                    # Start screen state
                    if self.start:
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                            self.game_enter_sound.play()
                            self.start = False
                            self.tracking.record_position(self.snake.positions[0])
                            continue
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                            break

                    # Playing state controls
                    if self.game_state == "playing" and not self.start:
                        if event.key in (pygame.K_w, pygame.K_UP):
                            self.snake.move_up()
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            self.snake.move_down()
                        elif event.key in (pygame.K_a, pygame.K_LEFT):
                            self.snake.move_left()
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            self.snake.move_right()

                    # Game over state
                    if self.game_state == "game over" and not self.game_confirm:
                        if pygame.time.get_ticks() - self.game_over_time >= 400:
                            if event.key == pygame.K_r:
                                self.reset_game()
                                self.g_over_sound.stop()
                                self.game_enter_sound.play()
                            else:
                                self.game_confirm = True
                                continue

            # Gameplay logic
            if self.game_state == "playing" and not self.start and not self.game_confirm:
                self.snake.movement()

                if self.snake.game_over:
                    self.game_state = "game over"
                    self.game_over_time = pygame.time.get_ticks()
                    self.sound_channel = pygame.mixer.Channel(0)
                    self.sound_channel.play(self.collision_sound)
                    self.sound_channel.queue(self.g_over_sound)

                else:
                    hit_bomb, bomb = self.obstacle.check_bomb_collision(self.snake.head_rect)
                    if hit_bomb:
                        self.game_state = "game over"
                        self.game_over_time = pygame.time.get_ticks()
                        self.sound_channel = pygame.mixer.Channel(0)
                        self.sound_channel.play(self.collision_sound)
                        self.sound_channel.queue(self.g_over_sound)

                    else:
                        if self.snake.head_rect.colliderect(self.food.rect):
                            self.eat_sound.play()
                            self.score_int += 1
                            self.snake.should_grow = True
                            self.update_difficulty()
                            self.food.spawn_strategic_apple(self.snake, self.obstacle, self.tracking, self.score_int)
                            self.tracking.moves_since_eat = 0

                        self.tracking.update_ai_strategy()
                        self.draw_screen()

            elif self.game_confirm:
                self.quit_confirmation()

            elif self.start:
                self.start_screen()

            elif self.game_state == "game over":
                self.game_over_screen()

            self.clock.tick(self.base_difficulty)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

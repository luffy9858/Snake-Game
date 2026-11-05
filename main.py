import pygame
import random
import os
import sys
# from pygame import *

#organised the sizes so we can change it in one go
display_size_1 = 600
display_size_2 = 600

#don't change these values
apple_size = 20
bomb_size = 20
snake_size = 20
current_size_x = 500
current_size_y = 500

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# started classes here
class Obstacles:
    def __init__(self, parent_screen, game):
        self.parent = parent_screen
        self.game = game
        self.bomb_image = pygame.image.load(resource_path("assets/bomb.png"))
        self.bomb_image = pygame.transform.scale(self.bomb_image, (bomb_size, bomb_size))
        self.x = 500
        self.y = 600
        self.bomb_rect = pygame.Rect(self.x, self.y, bomb_size, bomb_size)

    def bomb_draw(self):
        if self.game.score_int >= 3 and self.game.score_int%3 == 0 and self.game.game_state == "playing":
            self.parent.blit(self.bomb_image, (self.x, self.y))
            self.bomb_rect.topleft = (self.x, self.y)

    def spawn_bomb(self):
        self.x = random.randint(0, (display_size_1 // bomb_size) - 1) * bomb_size
        self.y = random.randint(0, (display_size_2 // bomb_size) - 1) * bomb_size

class Food:
    def __init__(self, parent_food_null):
        self.parent_food_null = parent_food_null
        self.food_image = pygame.image.load(resource_path("assets/apple.png"))
        self.food_image = pygame.transform.scale(self.food_image, (apple_size,apple_size))
        self.x = 300
        self.y = 200
        self.rect = pygame.Rect(self.x, self.y, apple_size, apple_size)

    def food_draw(self):
        self.parent_food_null.blit(self.food_image, (self.x, self.y))
        # self.rect = pygame.Rect(self.x, self.y, apple_size, apple_size) we can use this but we will use different one
        self.rect.topleft = (self.x, self.y)

    def spawn_apple(self):
        self.x = random.randint(0, (display_size_1 // apple_size) - 1) * apple_size
        self.y = random.randint(0, (display_size_2 // apple_size) - 1) * apple_size

class Snake:
    def __init__(self, parent_null, game):
        self.game = game
        self.parent_null = parent_null #not used here, it is just so we don't get error for the draw fun

        self.snake_image = pygame.image.load(resource_path("assets/white eye circle.png"))
        self.snake_image = pygame.transform.scale(self.snake_image, (snake_size,snake_size))

        self.snake_body = pygame.image.load(resource_path("assets/snake_back.png"))
        self.snake_body = pygame.transform.scale(self.snake_body, (snake_size,snake_size))

        self.positions = [(100,100), (80,100), (60,100)]
        self.direction = "down"

        head_x_main, head_y_main = self.positions[0]
        self.head_rect = pygame.Rect(head_x_main, head_y_main, snake_size, snake_size)
        self.should_grow = False
        self.game_over = False

    def collision_own(self):
        self.game_over = False
        for position in self.positions[1:]:
            head_x, head_y = position
            self.tail_rect = pygame.Rect(head_x, head_y, snake_size, snake_size)
            if self.head_rect.colliderect(self.tail_rect):
                self.game_over = True
                self.sound_channel = pygame.mixer.Channel(0)
                self.sound_channel.play(self.game.collision_sound)
                self.sound_channel.queue(self.game.g_over_sound)
                break

    def draw(self):
        for i, position in enumerate(self.positions):
            if i == 0:
                self.parent_null.blit(self.snake_image, (position))
            else:
                self.parent_null.blit(self.snake_body, (position))
        
    def move_down(self):
        if self.direction != "up":
            self.direction = "down"
            self.game.user_pattern.append("down")
    def move_up(self):
        if self.direction != "down":
            self.direction = "up"
            self.game.user_pattern.append("up")
    def move_right(self):
        if self.direction != "left":
            self.direction = "right"
            self.game.user_pattern.append("right")
    def move_left(self):
        if self.direction != "right":
            self.direction = "left"
            self.game.user_pattern.append("left")
    
    def movement(self):

        if self.direction == "up":
            self.logic_sub_y(snake_size)

        if self.direction == "down":
            self.logic_add_y(snake_size)

        if self.direction == "left":
            self.logic_sub_x(snake_size)

        if self.direction == "right":
            self.logic_add_x(snake_size)


        head_x, head_y = self.positions[0]
        if head_x < 0:
            head_x = display_size_1 - 20
        if head_x >=display_size_1:
            head_x = 0
        if head_y < 0:
            head_y = display_size_2 - 20
        if head_y >=display_size_2:
            head_y = 0
        
        self.positions[0] = (head_x, head_y)
        head_x_main, head_y_main = self.positions[0]
        # self.head_rect = pygame.Rect(head_x_main, head_y_main, snake_size, snake_size) #we can use this but we will use another one here
        self.head_rect.topleft = (head_x_main, head_y_main)
        self.collision_own()

    def logic_add_x(self,n):
        head_x, head_y = self.positions[0]
        new_head = (head_x + n, head_y)
        self.positions.insert(0, new_head)
        if not self.should_grow:
            self.positions.pop()
        else:
            self.should_grow = False

    def logic_sub_x(self,n):
        head_x, head_y = self.positions[0]
        new_head = (head_x - n, head_y)
        self.positions.insert(0, new_head)
        if not self.should_grow:
            self.positions.pop()
        else:
            self.should_grow = False

    def logic_add_y(self,n):
        head_x, head_y = self.positions[0]
        new_head = (head_x, head_y + n)
        self.positions.insert(0, new_head)
        if not self.should_grow:
            self.positions.pop()
        else:
            self.should_grow = False

    def logic_sub_y(self,n):
        head_x, head_y = self.positions[0]
        new_head = (head_x, head_y - n)
        self.positions.insert(0, new_head)
        if not self.should_grow:
            self.positions.pop()
        else:
            self.should_grow = False

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
        # self.screen.fill((163, 37, 247))
        # self.render_bg()
        self.snake = Snake(self.screen, self)
        self.food = Food(self.screen)
        self.obstacle = Obstacles(self.screen, self)
        self.clock = pygame.time.Clock()
        self.score_int = 0
        self.font = resource_path('assets/fonts/MinecraftRegular-Bmg3.otf')
        self.game_state = "playing"
        self.game_confirm = False
        self.game_over_time = 0
        self.base_difficulty = 5
        self.start = True
        self.user_pattern = []

    def render_bg(self):
        self.grid = pygame.image.load(resource_path("assets/grid.png"))
        self.grid = pygame.transform.scale(self.grid, (display_size_1, display_size_2))
        self.screen.blit(self.grid,(0,0))

    def reset_game(self):
        self.snake = Snake(self.screen, self)
        self.food = Food(self.screen)
        self.obstacle = Obstacles(self.screen, self)
        self.score_int = 0
        self.game_state = "playing"
        self.game_confirm = False
        self.base_difficulty = 5
        self.game_over_time = 0
        self.user_pattern = []

    def dynamic_scaling(self, x, y):
        self.x = x / current_size_x
        self.y = y / current_size_y
        true_x = self.x * display_size_1
        true_y = self.y * display_size_2
        main_tuple = (true_x, true_y)
        # print(f"This is the scoring coordinates: {main_tuple}") #debug
        return main_tuple

    def display_score(self):
        font = pygame.font.Font(self.font, 20)
        self.score = font.render(f"Score: {self.score_int}", False, (255,255,255))
        self.screen.blit(self.score, self.dynamic_scaling(380,20))

    def draw_screen(self):
        self.render_bg()
        self.food.food_draw()
        self.snake.draw()
        self.obstacle.bomb_draw()
        self.display_score()
        pygame.display.flip()

    def game_over_screen(self):
            self.render_bg()
            font = pygame.font.Font(self.font, 30)
            self.over = font.render(f"Game over!", False, (255,255,255))
            game_over = self.over.get_rect(center= self.dynamic_scaling(250,200))
            self.screen.blit(self.over, game_over)
            
            self.score = font.render(f"Score: {self.score_int}", False, (255,255,255))
            score_more = self.score.get_rect(center=self.dynamic_scaling(250,250))
            self.screen.blit(self.score, score_more)
            
            font_2 = pygame.font.Font(self.font, 20)
            self.restart = font_2.render(f"Press R to restart", False, (255,255,255))
            restart = self.restart.get_rect(center=self.dynamic_scaling(250,300))
            self.screen.blit(self.restart, restart)

            pygame.display.flip()

    def quit_confirmation(self):
            self.render_bg()
            font = pygame.font.Font(self.font, 15)
            self.quit = font.render(f"Do you want to quit the game?", True, (255,255,255))
            quit = self.quit.get_rect(center=self.dynamic_scaling(250,200))
            self.screen.blit(self.quit, quit)
            
            font_2 = pygame.font.Font(self.font, 15)
            self.confirm = font_2.render(f"Press Y to confirm or any other key to Cancel!", True, (255,255,255))
            confirm = self.confirm.get_rect(center=self.dynamic_scaling(250,240))
            self.screen.blit(self.confirm, confirm)

            pygame.display.flip()

    def spawn_check(self):
        # check = True

        # while check:
        #     if (self.food.x, self.food.y) in self.snake.positions:
        #         self.food.spawn_apple()
        #     if (self.food.x, self.food.y) in self.snake.positions:
        #         continue
        #     else:
        #         check = False

        #or we can write it as this but in a shorter way:

        while (self.food.x, self.food.y) in self.snake.positions:
            self.food.spawn_apple()

    def spawn_check_obstacles(self):
        while (self.obstacle.x, self.obstacle.y) in self.snake.positions:
            self.obstacle.spawn_bomb()

    def set_game_difficulty(self):
        if self.score_int % 3 == 0:
            self.base_difficulty += 2
            self.lvl_up_sound.play()

    def start_screen(self):
        self.render_bg()
        font = pygame.font.Font(self.font, 20)
        font_render = font.render(f"Press 'Enter' to start the Game!", False, (255,255,255))
        font_render_adjusted = font_render.get_rect(center=self.dynamic_scaling(250, 250))
        self.screen.blit(font_render, font_render_adjusted)
        pygame.display.flip()

    def run(self):
        running = True
        self.start_s_sound.play()
        while running:
            # print(pygame.mouse.get_pos()) # this is to get coordinates
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    self.start_s_sound.stop()
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    if self.game_state == "playing" and self.start == False:
                        if event.key == pygame.K_s:
                            self.snake.move_down()
                        if event.key == pygame.K_w:
                            self.snake.move_up()
                        if event.key == pygame.K_d:
                            self.snake.move_right()
                        if event.key == pygame.K_a:
                            self.snake.move_left()
                    if self.game_state == "game over" and self.game_confirm == False:
                        if pygame.time.get_ticks() - self.game_over_time >= 500:
                            if event.key == pygame.K_r:
                                self.reset_game()
                                self.g_over_sound.stop()
                                self.game_enter_sound.play()
                            else:
                                self.game_confirm = True
                                continue
                    if self.game_state == "game over" and self.game_confirm:
                        if event.key == pygame.K_y:
                            running = False
                            break
                        else:
                            self.game_confirm = False
                            continue
                    if self.start:
                        if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                            self.game_enter_sound.play()
                            self.start = False
                            continue

            if self.game_state == "playing" and self.start == False:
                self.snake.movement()
                if self.snake.game_over and self.game_state == "playing":
                    self.game_state = "game over"
                    self.game_over_time = pygame.time.get_ticks()
                #this is for game over

                elif self.snake.head_rect.colliderect(self.obstacle.bomb_rect) and self.game_state == "playing":
                    self.game_state = "game over"
                    self.game_over_time = pygame.time.get_ticks()
                    self.game_over = True
                    self.sound_channel = pygame.mixer.Channel(0)
                    self.sound_channel.play(self.collision_sound)
                    self.sound_channel.queue(self.g_over_sound)

                else:
                    if self.snake.head_rect.colliderect(self.food.rect):
                        self.eat_sound.play()
                        self.food.spawn_apple()
                        self.spawn_check()
                        self.score_int += 1
                        # self.snake.grow()
                        self.snake.should_grow = True
                        self.set_game_difficulty()
                    self.draw_screen()

            elif self.game_state == "game over" and self.game_confirm == False:
                self.game_over_screen()
                # pygame.time.wait(10000)

            elif self.game_state == "game over" and self.game_confirm:
                self.quit_confirmation()

            elif self.start:
                self.start_screen()

            if self.score_int > 2 and self.game_state == "playing":
                self.obstacle.spawn_bomb()
                self.spawn_check_obstacles()

            self.clock.tick(self.base_difficulty)
            # print(self.user_pattern) #debug for user pattern
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

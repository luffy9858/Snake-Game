import pygame
import time

#try 1
# positions = [(100, 100), (70, 100), (40, 100)]
# head_x, head_y = positions[0]
# new_head = (head_x + 20, head_y)
# positions.insert(0, new_head)
# positions.pop()
# print(positions)

#try 2
# apple = pygame.Rect(100, 100, 20, 20)
# snake = pygame.Rect(200, 100, 20, 20)
# print(snake.colliderect(apple))

#try 3
# pygame.init()
# pygame.font.init()
# print(pygame.font.match_font("Minecraft"))

#try 4
class Check:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.font = '/Users/raghav/Library/Fonts/MinecraftRegular-Bmg3.otf'
        pygame.display.flip()

    def run(self):
        self.screen.fill((255,255,255))

        font = pygame.font.Font(self.font, 30)
        self.over = font.render(f"Game over!", False, (0,0,0))
        game_over = self.over.get_rect(center=(250,250))
        self.screen.blit(self.over, game_over)
        pygame.display.flip()
        pygame.time.wait(10000)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

game = Check()
game.run()
    
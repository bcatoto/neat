import pygame
import os
import time
import neat
pygame.font.init()

WIN_WIDTH = 1214
WIN_HEIGHT = 654

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("World's Hardest Game NEAT")

PLAYER_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "player.png")).convert_alpha())
ENEMY_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "enemy.png")).convert_alpha())
LEVEL_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "level1.png")).convert_alpha())

class Player:
    """
    Player class representing square player
    """
    SIZE = 10
    COLOR = 0
    STEP = 5
    IMG = PLAYER_IMG

    def __init__(self, x, y):
        """
        Initialize object
        """
        self.x = x
        self.y = y

    def up(self):
        """
        Make player move up
        """
        self.y -= STEP

    def down(self):
        """
        Make player move down
        """
        self.y += STEP

    def left(self):
        """
        Make player move left
        """
        self.x -= STEP

    def right(self):
        """
        Make player move right
        """
        self.x += STEP

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

def draw_window(win, player):
    # draw base
    win.blit(LEVEL_IMG, (0, 0))

    # draw player
    player.draw(win)

    pygame.display.update()

def main():
    player = Player(200, 200)

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        draw_window(WIN, player)



if __name__ == "__main__":
    main()

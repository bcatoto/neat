import pygame
import os
import time
import neat
import math
pygame.font.init()

WIN_WIDTH = 1200
WIN_HEIGHT = 600

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("World's Hardest Game NEAT")
STAT_FONT = pygame.font.SysFont("arial", 50)

PLAYER_IMG = pygame.image.load(os.path.join("imgs", "player.png")).convert_alpha()
ENEMY_IMG = pygame.image.load(os.path.join("imgs", "enemy.png")).convert_alpha()
STAGE_IMG = pygame.image.load(os.path.join("imgs", "stage.png")).convert_alpha()
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png")).convert_alpha()

GEN = 0

class Player:
    """
    Player class representing square player
    """
    VEL = 5
    WIDTH = PLAYER_IMG.get_width()
    IMG = PLAYER_IMG
    MASK = pygame.mask.from_surface(PLAYER_IMG)
    BG_MASK = pygame.mask.from_surface(BG_IMG)
    STAG_TIME = 10
    INITIAL_X = 255 - WIDTH // 2
    INITIAL_Y = 425 - WIDTH // 2

    def __init__(self):
        """
        Initialize object
        """
        self.x = self.INITIAL_X
        self.y = self.INITIAL_Y
        self.fitness = 0
        self.steps = 0

    def move(self, x, y):
        self.x += x * self.VEL
        self.y += y * self.VEL

        # collide with wall
        if self.BG_MASK.overlap(self.MASK, (self.x, self.y)):
            self.x -= x * self.VEL
            self.y -= y * self.VEL

        self.updateFitness()

    def inStart(self):
        return self.x < 300 - self.WIDTH

    def closestEnemy(self, enemies):
        dist = float("inf")
        closest = None
        for enemy in enemies:
            dist = min(dist, math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2))
            closest = enemy
        x = (enemy.x - self.x) / dist
        y = (enemy.y - self.y) / dist
        return (dist, x, y)

    def updateFitness(self):
        if self.x > 900 - self.WIDTH:
            fitness = 1000 + 10000 / (self.steps ** 2)
        elif self.x > 300 - self.WIDTH:
            fitness = 700 - math.sqrt((900 - self.x) ** 2 + (self.y - 175) ** 2)
        else:
            fitness =  600 - math.sqrt((900 - self.x) ** 2 + (self.y - 175) ** 2)
        self.fitness = max(self.fitness, fitness)

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

class Enemy:
    """
    Enemy class representing circle enemy
    """
    VEL = 10
    RADIUS = ENEMY_IMG.get_width()
    IMG = ENEMY_IMG
    MASK = pygame.mask.from_surface(ENEMY_IMG)

    def __init__(self, y, left):
        """
        Initialize object
        """
        self.y = y - self.RADIUS // 2

        if left:
            self.x = 375 - self.RADIUS // 2
            self.dir = 1
        else:
            self.x = 825 - self.RADIUS // 2
            self.dir = -1

    def move(self):
        """
        Make enemy move horizontally and change direction if it hits a wall
        """
        self.x += self.dir * self.VEL

        if (self.x < 352):
            self.x = 352
            self.dir = 1

        if (self.x > 848 - self.RADIUS):
            self.x = 848 - self.RADIUS
            self.dir = -1

    def collide(self, player):
        """
        Determines if enemy is colliding with player
        """
        offset = (player.x - self.x, player.y - self.y)
        if self.MASK.overlap(player.MASK, offset):
            return True
        return False

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

def draw_window(win, players, enemies, gen, moves, alive):
    # draw level
    win.blit(STAGE_IMG, (0, 0))
    win.blit(BG_IMG, (0, 0))

    # draw enemies
    for enemy in enemies:
        enemy.draw(win)

    # draw players
    for player in players:
        player.draw(win)

    # generations
    gen_label = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(gen_label, (10, 10))

    # moves
    moves_label = STAT_FONT.render("Moves: " + str(moves), 1, (255,255,255))
    win.blit(moves_label, (10, 50))

    # alive
    alive_label = STAT_FONT.render("Alive: " + str(alive), 1, (255,255,255))
    win.blit(alive_label, (10, 90))

    pygame.display.update()

def eval_genomes(genomes, config):
    global GEN
    MOVES = "Infinite"
    INCREMENT = True

    if INCREMENT:
        MOVES = 50 + (GEN // 2) * 10

    nets = []
    players = []
    ge = []
    enemies = [Enemy(225, True), Enemy(275, False), Enemy(325, True), Enemy(375, False)]
    move = 0

    for id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player())
        ge.append(genome)

    clock = pygame.time.Clock()


    run = True
    while run and len(players) > 0:
        clock.tick(30)

        if INCREMENT and move == MOVES:
            break
        if not INCREMENT and move == 100:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        for i, player in enumerate(players):
            # calculate fitness
            ge[i].fitness = player.fitness

            # send player and closest enemy location
            dist, x, y = player.closestEnemy(enemies)
            output = nets[i].activate((move, player.x, player.y))

            # moves player based on output
            mod = output[0] // 1 % 8
            if mod == 0:
                player.move(-1, -1)
            elif mod == 1:
                player.move(0, -1)
            elif mod == 2:
                player.move(1, -1)
            elif mod == 3:
                player.move(-1, 0)
            elif mod == 4:
                player.move(1, 0)
            elif mod == 5:
                player.move(-1, 1)
            elif mod == 6:
                player.move(0, 1)
            else:
                player.move(1, 1)

        for enemy in enemies:
            enemy.move()

            # check for collision
            for i, player in enumerate(players):
                if enemy.collide(player):
                    ge[i].fitness -= 1
                    nets.pop(i)
                    ge.pop(i)
                    players.pop(i)

        # remove players still in start zone after every 30 moves
        if move > 0 and move % 30 == 0:
            rem_player = []
            rem_net = []
            rem_ge = []
            for i, player in enumerate(players):
                if player.inStart():
                    rem_player.append(player)
                    rem_net.append(nets[i])
                    rem_ge.append(ge[i])
            for player in rem_player:
                players.remove(player)
            for net in rem_net:
                nets.remove(net)
            for genome in rem_ge:
                ge.remove(genome)

        draw_window(WIN, players, enemies, GEN, MOVES, len(players))
        move += 1
    GEN += 1

def run(config_file):
    """
    Runs the NEAT algorithm to train a neural network to play the World's
    Hardest Game
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    # Run indefinitely.
    winner = p.run(eval_genomes)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    """
    Determine path to configuration file. This path manipulation is here so that
    the script will run successfully regardless of the current working
    directory.
    """
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

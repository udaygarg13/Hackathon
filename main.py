import pygame
import sys
import random

class Character:
    def __init__(self, x, y, name, health):
        self.x = x
        self.y = y
        self.size = Stage.GRID_SIZE-2
        self.name = name
        self.health = health
        self.image = pygame.image.load(f"{name}.png")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def move(self, key):
        if key == 'w' and self.y > Stage.GRID_SIZE:
            self.y -= Stage.GRID_SIZE
        if key == 's' and self.y < Stage.GRID_SIZE*(Stage.ROWS-1):
            self.y += Stage.GRID_SIZE
        if key == 'a' and self.x > Stage.GRID_SIZE:
            self.x -= Stage.GRID_SIZE
        if key == 'd' and self.x < Stage.GRID_SIZE*(Stage.COLS-1):
            self.x += Stage.GRID_SIZE

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Player(Character):
    def __init__(self,name,health):
        x, y = 1, 1
        super().__init__(x, y, name, health)
    
    def sword(self, boss_health):
        return boss_health - 10

class Boss(Character):
    def __init__(self,name,health,speed,dps):
        x, y = 1, 1
        self.speed = speed
        self.dps = dps
        while x == 1 and y == 1:
            x, y = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1, random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
            print (x,y)
        super().__init__(x, y, name, health)

class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = Stage.GRID_SIZE - 2
        self.image = pygame.image.load("a.gif")
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Stage:
    WIDTH, HEIGHT = 1280, 720
    GRID_SIZE = 80
    ROWS, COLS = 9, 9
    FPS = 10

    def __init__(self,stage):
        pygame.init()
        self.stage = stage
        # Create the screen
        self.screen = pygame.display.set_mode((Stage.WIDTH, Stage.HEIGHT))
        pygame.display.set_caption("Grid Movement")

        # Create the player and boss
        self.player = Player("Player",100)
        self.boss = Boss("Boss1",100,1.5,5)
        self.chest_locations = []
        for i in range(self.stage):
            self.chest_locations.append([(random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1), (random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1)]) 
        self.chests = [Chest(x, y) for x, y in self.chest_locations]
        # Game loop
        self.clock = pygame.time.Clock()
        self.boss_move_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def process_input(self):
        keys = pygame.key.get_pressed()
        player_key = ""

        if keys:
            if keys[pygame.K_w]:
                player_key = 'w'
            if keys[pygame.K_s]:
                player_key = 's'
            if keys[pygame.K_a]:
                player_key = 'a'
            if keys[pygame.K_d]:
                player_key = 'd'
            if keys[pygame.K_SLASH] and 0 < (abs(self.player.x - self.boss.x) <= Stage.GRID_SIZE and 0 < abs(self.player.y - self.boss.y) <= Stage.GRID_SIZE):
                self.boss.health = self.player.sword(self.boss.health)

        self.player.move(player_key)

    def update_game(self):
        self.boss_move_timer += 1

        if self.player.x == self.boss.x and self.player.y == self.boss.y:
            self.player.health -= self.boss.dps
        else:
            if self.boss_move_timer % self.boss.speed == 0:
                boss_key = random.choice(['w', 's', 'a', 'd'])
                self.boss.move(boss_key)

    def draw_grid(self):
        for row in range(Stage.ROWS):
            for col in range(Stage.COLS):
                pygame.draw.rect(self.screen, (255, 255, 255), (col * Stage.GRID_SIZE, row * Stage.GRID_SIZE, Stage.GRID_SIZE, Stage.GRID_SIZE), 1)

    def draw_characters(self):
        self.player.draw(self.screen)
        self.boss.draw(self.screen)

    def draw_chests(self):
        for chest in self.chests:
            chest.draw(self.screen)


    def draw_hud(self):
        # Draw background
        self.screen.fill((0, 0, 0))

        # Draw the grid
        self.draw_grid()

        # Draw the characters
        self.draw_characters()

        # Draw player and boss sprites with spacing
        self.screen.blit(self.player.image, (750, 20))
        self.screen.blit(self.boss.image, (750, 120))
        pygame.draw.rect(self.screen, (255, 255, 255), (745, 15, 90, 90), 5)
        pygame.draw.rect(self.screen, (255, 255, 255), (745, 115, 90, 90), 5)

        # Draw player name
        player_name_display = pygame.font.SysFont('Calibri', 30, True).render(self.player.name, True, (0, 255, 0))
        self.screen.blit(player_name_display, (840, 35))

        # Draw health bars
        player_health_bar_width = (self.player.health / 100) * 40
        pygame.draw.rect(self.screen, (0, 255, 0), (835, 70, player_health_bar_width, 20))

        boss_name_display = pygame.font.SysFont('Calibri', 30, True).render(self.boss.name, True, (255, 0, 0))
        self.screen.blit(boss_name_display, (840, 135))
        boss_health_bar_width = (self.boss.health / 100) * 40
        pygame.draw.rect(self.screen, (255, 0, 0), (835, 170, boss_health_bar_width, 20))

    def display_results(self):
        if self.player.health == 0:
            text_surface_2 = pygame.font.SysFont('Calibri', 30, True).render("You lose", False, (255, 255, 255))
            self.screen.blit(text_surface_2, (1000, 360))
            pygame.display.flip()
        elif self.boss.health == 0:
            text_surface_3 = pygame.font.SysFont('Calibri', 30, True).render("You win", False, (255, 255, 255))
            self.screen.blit(text_surface_3, (1000, 360))
            pygame.display.flip()

    def run_game(self):
        while True:
            self.handle_events()
            self.process_input()
            self.update_game()
            self.draw_hud()
            self.draw_chests()
            pygame.display.flip()
            self.clock.tick(Stage.FPS)
            self.display_results()

if __name__ == "__main__":
    game = Stage(1)
    game.run_game()

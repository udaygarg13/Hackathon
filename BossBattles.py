import pygame
import sys
import random
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Character:
    def __init__(self, x, y, name, health):
        self.x = x
        self.y = y
        self.size = Stage.GRID_SIZE-2
        self.name = name
        self.health = health
        self.image = pygame.image.load(resource_path(f"{name}.png"))
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
    
    def move(self, key, rock_locations):
        current_x = self.x
        current_y = self.y
        
        if key == 'w' and self.y > Stage.GRID_SIZE:
            self.y -= Stage.GRID_SIZE
        if key == 's' and self.y < Stage.GRID_SIZE*(Stage.ROWS-1):
            self.y += Stage.GRID_SIZE
        if key == 'a' and self.x > Stage.GRID_SIZE:
            self.x -= Stage.GRID_SIZE
        if key == 'd' and self.x < Stage.GRID_SIZE*(Stage.COLS-1):
            self.x += Stage.GRID_SIZE
        for rock_x, rock_y in rock_locations:
            if self.x == rock_x and self.y == rock_y:
                self.x = current_x
                self.y = current_y
        

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Player(Character):
    def __init__(self, name, health):
        x, y = 1, 1
        self.damage = 0
        self.swordname = ''
        self.hp_pot = 0
        super().__init__(x, y, name, health)

    def sword(self, boss_health):
        return boss_health - self.damage

class Boss(Character):
    def __init__(self, name, health, speed, dps):
        x, y = 1, 1
        self.speed = speed
        self.dps = dps
        while x == 1 and y == 1:
            x, y = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1, random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
        super().__init__(x, y, name, health)

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = Stage.GRID_SIZE - 2
        self.image = pygame.image.load(resource_path("rock.png"))
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = Stage.GRID_SIZE - 2
        self.image = pygame.image.load(resource_path("chest.png"))
        self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def open(self,stage):
        healing = int(*random.choices([0,1],weights=[0.80,0.20],k=1))
        rarities=["Legendary","Epic","Rare","Uncommon","Common"]
        rarityroll = random.choices(rarities,weights=[5,10,20,25,40], k=1)
        rarity=''.join(rarityroll)
        level = stage
        bowdmg=0
        sworddmg=0
        if level==1:
            swordbase=12
            bowbase=10
        elif level==2:
            swordbase=16
            bowbase=15
        elif level==3:
            swordbase=20
            bowbase=18
        elif level==4:
            swordbase=30
            bowbase=35
        elif level==5:
            swordbase=50
            bowbase=45
        dmgbuff=[3,2,1.5,1.25,1]
        for i in range (0,len(rarities)):
            if rarity==rarities[i]:
                sworddmg=swordbase*dmgbuff[i]
                bowdmg=bowbase*dmgbuff[i]
        swordname = f"{rarity} Sword"
        return(healing,sworddmg,swordname)

class Stage:
    WIDTH, HEIGHT = 1280, 720
    GRID_SIZE = 80
    ROWS, COLS = 9, 9
    FPS = 10

    def __init__(self, stage, boss_name, boss_health, boss_attack):
        pygame.init()
        self.stage = stage
        # Create the screen
        self.screen = pygame.display.set_mode((Stage.WIDTH, Stage.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Boss Battles")

        # Create the player and boss
        self.player = Player("Player", 75*self.stage)
        self.boss = Boss(boss_name, boss_health, 1.5, boss_attack)
        self.chest_locations = []
        for i in range(self.stage):
            chest_x = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1
            chest_y = random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
            while (chest_x, chest_y) == (self.player.x, self.player.y) or (chest_x, chest_y) == (self.boss.x, self.boss.y):
                chest_x = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1
            chest_y = random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
            self.chest_locations.append((chest_x, chest_y))

        self.chests = [Chest(x, y) for x, y in self.chest_locations]

        # Add rocks to some random grid locations
        self.rock_locations = []
        rock_number = random.randint(0,Stage.ROWS)
        for i in range(rock_number):
            rock_x = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1
            rock_y = random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
            # Ensure rocks don't spawn on player, boss, or chest locations
            while (rock_x, rock_y) in self.chest_locations or (rock_x, rock_y) == (self.player.x, self.player.y) or (rock_x, rock_y) == (self.boss.x, self.boss.y):
                rock_x = random.randint(0, Stage.COLS-1) * Stage.GRID_SIZE + 1
                rock_y = random.randint(0, Stage.ROWS-1) * Stage.GRID_SIZE + 1
            self.rock_locations.append((rock_x, rock_y))

        self.rocks = [Rock(x, y) for x, y in self.rock_locations]

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
            if keys[pygame.K_SLASH] and (
    (abs(self.player.x - self.boss.x) == Stage.GRID_SIZE and abs(self.player.y - self.boss.y) == 0) or
    (abs(self.player.y - self.boss.y) == Stage.GRID_SIZE and abs(self.player.x - self.boss.x) == 0) or
    (abs(self.player.y - self.boss.y) == Stage.GRID_SIZE and abs(self.player.x - self.boss.x) == Stage.GRID_SIZE)
):
                self.boss.health = self.player.sword(self.boss.health)
            if keys[pygame.K_LCTRL]:
                if self.player.hp_pot>0:
                    self.player.health += 25
                    self.player.hp_pot -= 1
            if keys[pygame.K_0] and keys[pygame.K_1]:
                self.player.health = 10000
        self.player.move(player_key,self.rock_locations)
        for chest in self.chests:
            if self.player.x == chest.x and self.player.y == chest.y:
                
                tempheal,tempdamage,tempswordname=chest.open(self.stage)
                self.player.hp_pot += tempheal
                if tempdamage > self.player.damage:
                    self.player.damage = tempdamage
                    self.player.swordname = f" ({tempswordname})"
                self.chests.remove(chest)

    def update_game(self):
        self.boss_move_timer += 1

        # Check for collisions with rocks
        

        if self.player.x == self.boss.x and self.player.y == self.boss.y:
            self.player.health -= self.boss.dps
        else:
            if self.boss_move_timer % self.boss.speed == 0:
                boss_key = random.choice(['w', 's', 'a', 'd'])
                self.boss.move(boss_key,self.rock_locations)

    def draw_grid(self):
        for row in range(Stage.ROWS):
            for col in range(Stage.COLS):
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (col * Stage.GRID_SIZE, row * Stage.GRID_SIZE, Stage.GRID_SIZE, Stage.GRID_SIZE), 1)

    def draw_characters(self):
        self.player.draw(self.screen)
        self.boss.draw(self.screen)

    def draw_rocks(self):
        for rock in self.rocks:
            rock.draw(self.screen)

    def draw_chests(self):
        for chest in self.chests:
            chest.draw(self.screen)

    def draw_hud(self):
        
        # Draw background
        self.screen.fill((0, 0, 0))

        # Draw the grid
        self.draw_grid()

    

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
        stage_display = pygame.font.SysFont('Calibri', 45, True).render(f"LEVEL {int(self.stage)}", True, (0, 0, 255))
        self.screen.blit(stage_display, (745, 230))
        player_damage_display = pygame.font.SysFont('Calibri', 25, True).render(f"Current Damage{self.player.swordname}: {int(self.player.damage)}", True, (0, 0, 255))
        self.screen.blit(player_damage_display, (745, 275))
        player_hp_pot_display = pygame.font.SysFont('Calibri', 25, True).render(f"+25 HP Potions: {int(self.player.hp_pot)}", True, (0, 0, 255))
        self.screen.blit(player_hp_pot_display, (745, 310))
    def display_results(self):
        if self.player.health <= 0:
            text_surface_2 = pygame.font.SysFont('Calibri', 30, True).render("YOU LOST", True, (255, 255, 255))
            self.screen.blit(text_surface_2, (940, 640))
            pygame.display.flip()
            restart = self.ask_restart()
            if restart:
                bosses()
        if self.stage<5 and self.boss.health <= 0:
            return("Won")
        if self.stage==5 and self.boss.health <= 0:
            text_surface_3 = pygame.font.SysFont('Calibri', 30, True).render("YOU WIN", True, (255, 255, 255))
            self.screen.blit(text_surface_3, (940, 640))
            pygame.display.flip()
            restart = self.ask_restart()
            if restart:
                bosses()

    def display_controls(self):
            controls_text = [
                "CONTROLS",
                "W: Move Up",
                "S: Move Down",
                "A: Move Left",
                "D: Move Right",
                "/: Attack Boss",
                "LCTRL: Use Health Potion"
            ]

            # Calculate the size of the box based on the number of lines
            box_width = 225
            box_height = len(controls_text) * 25+2

            # Calculate the position on the right-hand side
            box_x = 745
            box_y = 360

            pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 0)  # Draw filled rectangle
            pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)  # Draw border

            font = pygame.font.SysFont('Calibri', 20, True)
            y_position = 365

            for line in controls_text:
                text_surface = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (box_x + 10, y_position))
                y_position += 25
    def run_game(self):
        result = ''
        while True:
            self.handle_events()
            self.process_input()
            self.update_game()
            self.draw_hud()
            self.draw_rocks()
            self.draw_chests()
            self.draw_characters()
            self.display_controls()
            pygame.display.flip()
            self.clock.tick(Stage.FPS)
            result=self.display_results()
            if result is not None:
                return(result)
            
    def display_message(self, message,x,y):
        font = pygame.font.SysFont('Calibri', 30, True)
        text_surface = font.render(message, True, (255, 255, 255))
        self.screen.blit(text_surface, (x,y))
        pygame.display.flip()
    
    def ask_restart(self):
        self.display_message("Do you want to restart the game? (Y/N)",760,670)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return True
                    elif event.key == pygame.K_n:
                        sys.exit()

def bosses():
    bosses = [["Blinky", 150, 10],
            ["Pinky", 300, 20],
            ["Inky", 450, 30],
            ["Clyde", 600, 40],
            ["Pacman", 1000, 100]]
    for i in range(len(bosses)):
        game = Stage(i+1,bosses[i][0],bosses[i][1],bosses[i][2])
        result=game.run_game()

if __name__ == '__main__':
    bosses()
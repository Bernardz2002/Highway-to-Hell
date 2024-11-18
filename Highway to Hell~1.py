import pygame
import random
import sys

pygame.init()

#Screen settings
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Cross the Road Clone")

#Displays
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0,100,0)
BROWN = (100,50,0)
font = pygame.font.SysFont(None, 36)

#Game variables
car_speed_base = 5
car_spawn_rate = 50
block_spawn_rate = 80
block_speed = 3
player_start_y = screen_height - 100
player_max_population = 100
roads_per_stage = 5
total_stages = 5
car_lane_y = 400
block_lane_y = car_lane_y - 45
special_block_types = ["+10","x2","+20"]

clock = pygame.time.Clock()

class Player:

    def __init__(self):
        self.x = screen_width // 2
        self.y = player_start_y
        self.population = 10
        self.crossing = False
        self.invulnerable = False
        self.invulnerable_timer = 0

    def draw(self):
        radius = 15 if self.population<=30 else 25 if self.population<=60 else 35 #3 population sizes
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), radius)
        population_text = font.render(str(self.population), True, BLACK)
        text_rect = population_text.get_rect(center=(self.x, self.y))
        screen.blit(population_text, text_rect)

    def reset(self):
        self.y = player_start_y
        self.population = 10
        self.crossing = False
        self.invulnerable = False
        self.invulnerable_timer = 0

    def move_up(self, step=10):
        self.y -= step
        if self.y < 0:
            self.y = player_start_y
            return True
        return False

    def update_invulnerability(self):
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

class Car:

    def __init__(self, existing_cars):
        self.width = random.randint(50, 100)
        self.height = 40
        self.color = random.choice([RED, BLUE, GREEN])
        self.y = car_lane_y
        self.x = screen_width
        self.direction = -1

        if existing_cars:
            min_existing_x = min(car.x for car in existing_cars if car.y == self.y)
            if self.x - min_existing_x < 150:  # Keep at least 150 pixels between cars
                self.x = min_existing_x - 150

    def move(self, speed):
        self.x += speed * self.direction

    def draw(self):
        pygame.draw.rect(screen, self.color,(self.x, self.y, self.width, self.height))

class SpecialBlock:

    def __init__(self, existing_blocks):
        self.effect = random.choice(special_block_types)
        self.width, self.height = 120, 40
        self.color = WHITE
        self.y = block_lane_y
        self.x = screen_width

        if existing_blocks:
            min_existing_x = min(block.x for block in existing_blocks if block.y == self.y)
            if self.x - min_existing_x < 150:
                self.x = min_existing_x - 150

    def move(self):
        self.x -= block_speed

    def draw(self):
        pygame.draw.rect(screen, self.color,(self.x, self.y, self.width, self.height))
        text = font.render(self.effect, True, BLACK)
        screen.blit(text, (self.x + 20, self.y + 5))


class Environment:

    def __init__(self):
        self.elements = []
        self.chickens = []
        self.generate_environment()

    def generate_environment(self):
        self.elements.clear()
        self.chickens.clear()

        for _ in range(10):
            kind = random.choice(["tree", "grass"])
            dark = random.choice([True,False])
            x = random.randint(0, screen_width - 50)
            y = random.randint(50, 150)
            self.elements.append((kind, x, y, dark))

        for _ in range(3):
            x = random.randint(0, screen_width - 50)
            y = random.randint(50, 150)
            direction = random.choice([-1, 1])  # Random left or right movement
            self.chickens.append({"x": x, "y": y, "direction": direction})

    def draw(self):
        for kind, x, y, dark in self.elements:
            if kind == "tree":
                pygame.draw.rect(screen,BROWN,(x, y, 20, 40))
                pygame.draw.circle(screen,GREEN if not dark else DARK_GREEN,(x + 10, y), 20)
            elif kind == "grass":
                pygame.draw.rect(screen,GREEN if not dark else DARK_GREEN,(x, y, 30, 10))

        for chicken in self.chickens:
            pygame.draw.circle(screen,WHITE,(chicken["x"], chicken["y"]), 10)
            pygame.draw.circle(screen,BLACK,(chicken["x"] - 3, chicken["y"] - 3), 2)
            chicken["x"] += chicken["direction"] * 2

            if random.randint(1, 100) < 5: chicken["direction"] *= -1
            if chicken["x"] < 0 or chicken["x"] > screen_width - 10: chicken["direction"] *= -1

    def draw_road_lines(self):
        for i in range(0, screen_width, 40):
            pygame.draw.line(screen,WHITE,(i, car_lane_y + 20),(i + 20, car_lane_y + 20), 5)

class Game:

    def __init__(self):
        self.player = Player()
        self.cars = []
        self.special_blocks = []
        self.environment = Environment()
        self.score = 0
        self.game_over = False
        self.stage = 1
        self.crossings = 0
        self.completion_message = None

    def reset(self):
        self.player.reset()
        self.cars.clear()
        self.special_blocks.clear()
        self.environment.generate_environment()
        self.crossings = 0
        self.stage = 1
        self.score = 0
        self.game_over = False
        self.completion_message = None

    def next_stage(self):
        self.score += self.player.population
        self.player.population = 10
        self.crossings = 0
        self.stage += 1
        if self.stage > total_stages: self.game_over = True
        else: self.environment.generate_environment()

    def spawn_car(self):
        if random.randint(1, car_spawn_rate) == 1: self.cars.append(Car(self.cars))

    def spawn_special_block(self):
        if random.randint(1, block_spawn_rate) == 1: self.special_blocks.append(SpecialBlock(self.special_blocks))

    def check_collisions(self):
        player_rect = pygame.Rect(self.player.x - 20, self.player.y - 20, 40,40)

        for car in self.cars:
            car_rect = pygame.Rect(car.x, car.y, car.width, car.height)
            if player_rect.colliderect(car_rect) and not self.player.invulnerable:

                if self.player.population <= 20:
                    self.player.population -= 10
                elif self.player.population <= 50:
                    self.player.population -= 20
                else:
                    self.player.population //= 2

                if self.player.population <= 0:
                    self.game_over = True

                self.player.invulnerable = True
                self.player.invulnerable_timer = 60
                break

        for block in self.special_blocks:
            block_rect = pygame.Rect(block.x, block.y, block.width, block.height)
            if player_rect.colliderect(block_rect):
                if block.effect == "+10":
                    self.player.population = min(self.player.population + 10, player_max_population)
                elif block.effect == "x2":
                    self.player.population = min(self.player.population * 2, player_max_population)
                elif block.effect == "+20":
                    self.player.population = min(self.player.population + 20, player_max_population)
                self.special_blocks.remove(block)
                break

    def generate_completion_message(self):
        messages = ["Awesome!", "Well done!", "Excellent!", "Good job!", "Amazing!","Ausgezeichnet!"]
        message = random.choice(messages)
        self.completion_message = message+" "+"⭐"*(1 if 10<=self.score<=100 else 2 if 101<=self.score<=200 else 3)

    def draw_road(self):
        road_height = 50
        pygame.draw.rect(screen,DARK_GRAY,(0, car_lane_y, screen_width, road_height))
        pygame.draw.rect(screen,DARK_GRAY,(0, block_lane_y, screen_width, road_height))

    def game_loop(self):
        while True:
            screen.fill(GRAY)
            self.draw_road()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset()
                    elif not self.player.crossing:
                        self.player.crossing = True

            if self.player.crossing and not self.game_over:
                if self.player.move_up(step=10):
                    self.crossings += 1
                    self.player.crossing = False
                    if self.crossings >= roads_per_stage:
                        self.next_stage()

            self.player.update_invulnerability()

            self.spawn_car()
            for car in self.cars: car.move(car_speed_base + self.stage * 0.5)
            self.cars = [car for car in self.cars if -car.width <= car.x <= screen_width + car.width]

            self.spawn_special_block()
            for block in self.special_blocks: block.move()
            self.special_blocks = [block for block in self.special_blocks]

            self.check_collisions()

            self.environment.draw()
            self.environment.draw_road_lines()
            self.player.draw()
            for car in self.cars: car.draw()
            for block in self.special_blocks: block.draw()

            stats_background = pygame.Surface((250, 150))
            stats_background.set_alpha(300)
            stats_background.fill((50, 50, 50))
            screen.blit(stats_background, (10, 10))
            score_text = font.render(f"Score: {self.score}",True,WHITE)
            stage_text = font.render(f"Stage: {min(self.stage,total_stages)}/{total_stages}",True,WHITE)
            road_text = font.render(f"Roads Crossed: {self.crossings}/{roads_per_stage}",True,WHITE)
            screen.blit(score_text, (20, 20))
            screen.blit(stage_text, (20, 60))
            screen.blit(road_text, (20, 100))

            if self.game_over:
                if self.stage > total_stages:
                    if not self.completion_message:
                        self.generate_completion_message()
                    completion_text = font.render(self.completion_message,True,BLACK)
                    text_rect = completion_text.get_rect(center=(screen_width//2,screen_height//2))
                    screen.blit(completion_text, text_rect)
                else:
                    game_over_text = font.render("Game Over! Press Space or Click to Restart",True,BLACK)
                    screen.blit(game_over_text,(screen_width // 2 - 200, screen_height // 2))

            pygame.display.flip()
            clock.tick(60)

# Start the game
if __name__ == "__main__":
    game = Game()
    game.game_loop()
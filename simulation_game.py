import pygame
import sys
import math
import random
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
GRAVITY = 0.1
THRUST_POWER = 0.15
ROTATION_SPEED = 3
INITIAL_ALTITUDE = 500
REQUIRED_HORIZONTAL_DISTANCE = 2000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = RED

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def check_collision(self, lander):
        lander_rect = pygame.Rect(lander.x, lander.y, lander.width, lander.height)
        return self.rect.colliderect(lander_rect)

class Lander:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.velocity_x = 0
        self.angle = 0
        self.main_thrust = False
        self.horizontal_thrust = False
        self.width = 60
        self.height = 80
        self.fuel = 100
        self.crashed = False
        self.landed = False
        self.distance_traveled = 0
        self.telemetry = {'altitude': [], 'velocity_y': [], 'velocity_x': [], 'time': []}
        self.time = 0

    def apply_main_thrust(self):
        if self.fuel > 0:
            angle_rad = math.radians(self.angle)
            self.velocity_x += math.sin(angle_rad) * THRUST_POWER
            self.velocity_y -= math.cos(angle_rad) * THRUST_POWER
            self.fuel -= 0.1
            return True
        return False

    def apply_horizontal_thrust(self, direction):
        if self.fuel > 0:
            self.velocity_x += direction * THRUST_POWER * 0.5
            self.fuel -= 0.05
            return True
        return False

    def update(self):
        if not (self.crashed or self.landed):
            self.velocity_y += GRAVITY
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.distance_traveled += abs(self.velocity_x)
            self.time += 1/FPS
            self.telemetry['altitude'].append(WINDOW_HEIGHT - self.y)
            self.telemetry['velocity_y'].append(self.velocity_y)
            self.telemetry['velocity_x'].append(self.velocity_x)
            self.telemetry['time'].append(self.time)

            if self.x < 0:
                self.x = 0
                self.velocity_x = 0
            elif self.x > WINDOW_WIDTH - self.width:
                self.x = WINDOW_WIDTH - self.width
                self.velocity_x = 0

    def rotate(self, direction):
        self.angle += direction * ROTATION_SPEED
        self.angle = self.angle % 360

    def draw(self, screen):
        lander_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(lander_surface, WHITE, [
            (self.width//2, 0),
            (self.width//4, self.height//3),
            (self.width//6, self.height*2//3),
            (0, self.height),
            (self.width, self.height),
            (5*self.width//6, self.height*2//3),
            (3*self.width//4, self.height//3),
        ])
        pygame.draw.line(lander_surface, WHITE, (self.width//6, self.height*2//3), (0, self.height), 2)
        pygame.draw.line(lander_surface, WHITE, (5*self.width//6, self.height*2//3), (self.width, self.height), 2)

        if self.main_thrust and self.fuel > 0:
            flame_height = random.randint(20, 30)
            pygame.draw.polygon(lander_surface, YELLOW, [
                (self.width//2, self.height),
                (self.width//3, self.height + flame_height),
                (2*self.width//3, self.height + flame_height)
            ])

        if self.horizontal_thrust and self.fuel > 0:
            flame_width = random.randint(10, 15)
            if self.velocity_x > 0:
                pygame.draw.polygon(lander_surface, YELLOW, [
                    (0, self.height*2//3),
                    (-flame_width, self.height//2),
                    (-flame_width, self.height*3//4)
                ])
            else:
                pygame.draw.polygon(lander_surface, YELLOW, [
                    (self.width, self.height*2//3),
                    (self.width + flame_width, self.height//2),
                    (self.width + flame_width, self.height*3//4)
                ])

        rotated_surface = pygame.transform.rotate(lander_surface, self.angle)
        rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(rotated_surface, rect.topleft)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chandrayaan-3 Moon Lander Simulation")
        self.clock = pygame.time.Clock()
        self.lander = Lander(50, INITIAL_ALTITUDE)
        self.phase = "horizontal"
        self.control_mode = "manual"
        self.reset_obstacles()
        self.load_background()
        self.landing_pad = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 20, 100, 10)

    def reset_obstacles(self):
        self.obstacles = [
            Obstacle(random.randint(300, 1000), random.randint(200, 500), 40, random.randint(150, 300))
            for _ in range(3)
        ]

    def load_background(self):
        moon_surface = cv2.imread("moon_surface.jpg") if os.path.exists("moon_surface.jpg") else None
        if moon_surface is None:
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.background.fill(BLACK)
            for _ in range(200):
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                radius = random.randint(1, 3)
                pygame.draw.circle(self.background, WHITE, (x, y), radius)
        else:
            moon_surface = cv2.resize(moon_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            moon_surface = cv2.cvtColor(moon_surface, cv2.COLOR_BGR2RGB)
            self.background = pygame.surfarray.make_surface(moon_surface)

    def create_telemetry_graph(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4, 6))
        ax1.plot(self.lander.telemetry['time'], self.lander.telemetry['altitude'], 'b-', label='Altitude')
        ax1.set_ylabel('Altitude (m)')
        ax1.set_xlabel('Time (s)')
        ax1.grid(True)
        ax1.legend()
        ax2.plot(self.lander.telemetry['time'], self.lander.telemetry['velocity_y'], 'r-', label='Vertical')
        ax2.plot(self.lander.telemetry['time'], self.lander.telemetry['velocity_x'], 'g-', label='Horizontal')
        ax2.set_ylabel('Velocity (m/s)')
        ax2.set_xlabel('Time (s)')
        ax2.grid(True)
        ax2.legend()
        plt.tight_layout()
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        graph_surface = pygame.image.frombuffer(raw_data, size, "RGB")
        plt.close(fig)
        return graph_surface

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_m:
                    self.control_mode = "manual"
                elif event.key == pygame.K_a:
                    self.control_mode = "automatic"

        keys = pygame.key.get_pressed()
        if self.control_mode == "manual":
            if keys[pygame.K_UP]:
                self.lander.main_thrust = self.lander.apply_main_thrust()
            else:
                self.lander.main_thrust = False
            if keys[pygame.K_LEFT]:
                if self.phase == "horizontal":
                    self.lander.horizontal_thrust = self.lander.apply_horizontal_thrust(-1)
                else:
                    self.lander.rotate(1)
            elif keys[pygame.K_RIGHT]:
                if self.phase == "horizontal":
                    self.lander.horizontal_thrust = self.lander.apply_horizontal_thrust(1)
                else:
                    self.lander.rotate(-1)
            else:
                self.lander.horizontal_thrust = False
        elif self.control_mode == "automatic":
            if self.phase == "horizontal":
                self.lander.horizontal_thrust = self.lander.apply_horizontal_thrust(1)
            else:
                if self.lander.y < WINDOW_HEIGHT - 100:
                    self.lander.main_thrust = self.lander.apply_main_thrust()
                else:
                    self.lander.main_thrust = False

        return True

    def check_landing(self):
        for obstacle in self.obstacles:
            if obstacle.check_collision(self.lander):
                self.lander.crashed = True
                return
        if self.lander.y + self.lander.height >= WINDOW_HEIGHT - 20:
            if (self.landing_pad.left < self.lander.x < self.landing_pad.right and
                abs(self.lander.velocity_y) < 2 and
                abs(self.lander.velocity_x) < 1 and
                abs(self.lander.angle % 360) < 15):
                self.lander.landed = True
            else:
                self.lander.crashed = True
            self.lander.velocity_y = 0
            self.lander.velocity_x = 0
            self.lander.y = WINDOW_HEIGHT - 20 - self.lander.height

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        pygame.draw.rect(self.screen, BLUE, self.landing_pad)
        self.lander.draw(self.screen)
        font = pygame.font.Font(None, 36)
        fuel_text = font.render(f"Fuel: {int(self.lander.fuel)}%", True, WHITE)
        velocity_text = font.render(f"Vertical Velocity: {abs(int(self.lander.velocity_y*10))}m/s", True, WHITE)
        horizontal_text = font.render(f"Horizontal Velocity: {abs(int(self.lander.velocity_x*10))}m/s", True, WHITE)
        phase_text = font.render(f"Phase: {self.phase.capitalize()} ({self.control_mode})", True, GREEN)
        self.screen.blit(fuel_text, (10, 10))
        self.screen.blit(velocity_text, (10, 50))
        self.screen.blit(horizontal_text, (10, 90))
        self.screen.blit(phase_text, (10, 130))
        if self.lander.crashed or self.lander.landed:
            graph = self.create_telemetry_graph()
            graph = pygame.transform.scale(graph, (400, 300))
            self.screen.blit(graph, (WINDOW_WIDTH - 420, WINDOW_HEIGHT - 320))
        if self.lander.crashed:
            crash_text = font.render("CRASHED!", True, RED)
            self.screen.blit(crash_text, (WINDOW_WIDTH//2 - 50, WINDOW_HEIGHT//2))
        elif self.lander.landed:
            landed_text = font.render("LANDED SUCCESSFULLY!", True, BLUE)
            self.screen.blit(landed_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            if self.phase == "horizontal" and self.lander.x >= WINDOW_WIDTH - 300:
                self.phase = "vertical"
                self.reset_obstacles()
                new_pad_x = random.randint(100, WINDOW_WIDTH - 200)
                self.landing_pad = pygame.Rect(new_pad_x, WINDOW_HEIGHT - 20, 100, 10)
            self.lander.update()
            self.check_landing()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

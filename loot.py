import pygame
import random
import math
from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT

class Loot:
    def __init__(self):
        self.radius = 12  # menší loot
        self.x = random.randint(self.radius, LOGICAL_WIDTH - self.radius)
        self.y = random.randint(self.radius, LOGICAL_HEIGHT - self.radius)
        # Barevný gradient pro loot
        self.color1 = (random.randint(80, 180), random.randint(200, 255), random.randint(80, 180))
        self.color2 = (random.randint(180, 255), random.randint(180, 255), random.randint(80, 180))
        self.angle = random.uniform(0, 2 * math.pi)

    def draw(self, surface):
        # Gradientový kruh
        for i in range(self.radius, 0, -1):
            ratio = i / self.radius
            r = int(self.color1[0] * ratio + self.color2[0] * (1 - ratio))
            g = int(self.color1[1] * ratio + self.color2[1] * (1 - ratio))
            b = int(self.color1[2] * ratio + self.color2[2] * (1 - ratio))
            pygame.draw.circle(surface, (r, g, b), (self.x, self.y), i)
        # Lesklý efekt
        highlight_rect = pygame.Rect(0, 0, self.radius, self.radius // 2)
        highlight_rect.center = (int(self.x - self.radius // 3), int(self.y - self.radius // 3))
        pygame.draw.ellipse(surface, (255, 255, 255, 120), highlight_rect)
        # Jemný světlý okraj
        pygame.draw.circle(surface, (200, 255, 200), (self.x, self.y), self.radius, 2)

class Particle:
    def __init__(self, x, y, color=None, vx=None, vy=None, life=None, radius=None):
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else random.randint(2, 5)
        if color is None:
            # Náhodná barva pro ohňostroj
            self.color = (
                random.randint(120, 255),
                random.randint(120, 255),
                random.randint(120, 255)
            )
        else:
            self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6) if vx is None else vx
        self.vx = math.cos(angle) * speed if vx is None else vx
        self.vy = math.sin(angle) * speed if vy is None else vy
        self.life = life if life is not None else random.randint(18, 32)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.radius = max(0, self.radius - 0.12)
        # Pomalejší ztráta rychlosti pro efekt ohňostroje
        self.vx *= 0.96
        self.vy *= 0.96

    def draw(self, surface):
        if self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

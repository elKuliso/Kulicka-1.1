import math
import pygame
from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT, GOLD, WHITE

class Player:
    def __init__(self, player_speed):
        self.base_radius = int(40 * 0.5)
        self.radius = self.base_radius
        self.x = LOGICAL_WIDTH // 2
        self.y = LOGICAL_HEIGHT // 2
        self.speed = player_speed
        self.color = GOLD
        self.shadow_color = (180, 140, 0)
        self.shoot_cooldown = 20
        self.shoot_timer = 0
        self.damage = 1.0

    def update_radius(self, level):
        growth = 1 + 0.05 * (level // 10)
        self.radius = int(self.base_radius * growth)

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(self.radius, min(LOGICAL_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(LOGICAL_HEIGHT - self.radius, self.y))

    def can_shoot(self):
        return self.shoot_timer <= 0

    def reset_shoot_timer(self):
        self.shoot_timer = self.shoot_cooldown

    def update_shoot_timer(self):
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def draw(self, surface, shop=None):
        # shop je potřeba pro stín, pokud není předán, stín se nevykreslí
        if shop is not None:
            sun_x = shop.icon_rect.centerx
            sun_y = shop.icon_rect.centery
            dx = self.x - sun_x
            dy = self.y - sun_y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dx, dy = 1, 1
            else:
                dx /= dist
                dy /= dist
            max_offset = int(12 * 0.75)
            min_offset = 0
            max_shadow_radius = int((self.radius + 2) * 0.75)
            min_shadow_radius = 0
            max_dist = 400
            shadow_offset = int(min_offset + (max_offset - min_offset) * min(dist, max_dist) / max_dist)
            shadow_radius = int(min_shadow_radius + (max_shadow_radius - min_shadow_radius) * min(dist, max_dist) / max_dist)
            if shadow_radius > 0:
                shadow_x = int(self.x + dx * shadow_offset)
                shadow_y = int(self.y + dy * shadow_offset)
                pygame.draw.circle(surface, (90, 70, 0), (shadow_x, shadow_y), shadow_radius)
        # Hlavní tělo s gradientem
        for i in range(self.radius, 0, -1):
            color_ratio = i / self.radius
            r = int(self.color[0] * color_ratio + 255 * (1 - color_ratio))
            g = int(self.color[1] * color_ratio + 220 * (1 - color_ratio))
            b = int(self.color[2] * color_ratio + 100 * (1 - color_ratio))
            pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), i)
        # Lesklý efekt
        highlight_rect = pygame.Rect(0, 0, self.radius, self.radius // 2)
        highlight_rect.center = (int(self.x - self.radius // 3), int(self.y - self.radius // 3))
        pygame.draw.ellipse(surface, (255, 255, 255, 120), highlight_rect)
        # Jemný okraj
        pygame.draw.circle(surface, (255, 230, 80), (int(self.x), int(self.y)), self.radius, 2)

class Joystick:
    def __init__(self):
        self.active = False
        self.start_pos = (0, 0)
        self.current_pos = (0, 0)
        self.max_radius = 150
        self.sensitivity = 1.6

    def start(self, pos):
        self.active = True
        self.start_pos = pos
        self.current_pos = pos

    def move(self, pos):
        if self.active:
            self.current_pos = pos

    def stop(self):
        self.active = False

    def get_vector(self):
        if not self.active:
            return 0, 0
        dx = self.current_pos[0] - self.start_pos[0]
        dy = self.current_pos[1] - self.start_pos[1]
        dist = math.hypot(dx, dy)
        if dist > self.max_radius:
            dx = dx / dist * self.max_radius
            dy = dy / dist * self.max_radius
            dist = self.max_radius
        if dist == 0:
            return 0, 0
        nx = dx / self.max_radius * self.sensitivity
        ny = dy / self.max_radius * self.sensitivity
        nx = max(-1, min(1, nx))
        ny = max(-1, min(1, ny))
        return nx, ny
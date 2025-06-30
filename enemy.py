import random
import math
import pygame

class Enemy:
    def __init__(self, level=1, split_on_death=False, LOGICAL_WIDTH=800, LOGICAL_HEIGHT=1220):
        self.radius = int(35 * 0.4)
        self.x = random.randint(self.radius, LOGICAL_WIDTH - self.radius)
        self.y = -self.radius  # Spawn z horní strany
        self.base_color = (220, 40, 40)
        self.color = self.base_color
        speed_bonus = 1 + 0.015 * (level // 10)
        if level < 10:
            self.health = max(1, int((5 + (level - 1)) * 0.4))
            self.speed = (1.5 + (level - 1) * 0.05) * 0.2 * speed_bonus
        else:
            self.health = max(2, int((10 + (level - 1) * 2) * 0.4))
            self.speed = (1.8 + (level - 10) * 0.07) * 0.2 * speed_bonus
        self.split_on_death = split_on_death

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, surface, shop, WHITE=(255,255,255)):
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
        max_offset = int(6 * 0.7)
        min_offset = 0
        max_shadow_radius = int((self.radius + 2) * 0.7)
        min_shadow_radius = 0
        max_dist = 400
        shadow_offset = int(min_offset + (max_offset - min_offset) * min(dist, max_dist) / max_dist)
        shadow_radius = int(min_shadow_radius + (max_shadow_radius - min_shadow_radius) * min(dist, max_dist) / max_dist)
        if shadow_radius > 0:
            shadow_x = int(self.x + dx * shadow_offset)
            shadow_y = int(self.y + dy * shadow_offset)
            pygame.draw.circle(surface, (40, 40, 40), (shadow_x, shadow_y), shadow_radius)
        for i in range(self.radius, 0, -1):
            color_ratio = i / self.radius
            r = int(self.base_color[0] * color_ratio + 255 * (1 - color_ratio))
            g = int(self.base_color[1] * color_ratio + 255 * (1 - color_ratio))
            b = int(self.base_color[2] * color_ratio + 255 * (1 - color_ratio))
            pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), i)
        highlight_rect = pygame.Rect(0, 0, self.radius, self.radius // 2)
        highlight_rect.center = (int(self.x - self.radius // 3), int(self.y - self.radius // 3))
        pygame.draw.ellipse(surface, (255, 255, 255, 120), highlight_rect)
        pygame.draw.circle(surface, (220, 220, 255), (int(self.x), int(self.y)), self.radius, 2)

    def is_dead(self):
        return self.health <= 0

class FastEnemy(Enemy):
    def __init__(self, level=1, LOGICAL_WIDTH=800, LOGICAL_HEIGHT=1220):
        super().__init__(level, LOGICAL_WIDTH=LOGICAL_WIDTH, LOGICAL_HEIGHT=LOGICAL_HEIGHT)
        self.base_color = (80, 180, 255)
        self.color = self.base_color
        self.speed *= 1.7
        self.health = max(1, int(self.health * 0.7))

class TankEnemy(Enemy):
    def __init__(self, level=1, LOGICAL_WIDTH=800, LOGICAL_HEIGHT=1220):
        super().__init__(level, LOGICAL_WIDTH=LOGICAL_WIDTH, LOGICAL_HEIGHT=LOGICAL_HEIGHT)
        self.base_color = (80, 255, 80)
        self.color = self.base_color
        self.radius = int(self.radius * 1.5)
        self.speed *= 0.6
        self.health = int(self.health * 2)

class ZigZagEnemy(Enemy):
    def __init__(self, level=1, LOGICAL_WIDTH=800, LOGICAL_HEIGHT=1220):
        super().__init__(level, LOGICAL_WIDTH=LOGICAL_WIDTH, LOGICAL_HEIGHT=LOGICAL_HEIGHT)
        self.base_color = (255, 255, 80)
        self.color = self.base_color
        self.phase = random.uniform(0, 2*math.pi)

    def move_towards_player(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist
        angle = math.atan2(dy, dx)
        angle += math.sin(pygame.time.get_ticks()/300 + self.phase) * 0.7
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

class BossEnemy(Enemy):
    def __init__(self, level=10, LOGICAL_WIDTH=800, LOGICAL_HEIGHT=1220):
        super().__init__(level, LOGICAL_WIDTH=LOGICAL_WIDTH, LOGICAL_HEIGHT=LOGICAL_HEIGHT)
        self.radius = int(70 * 0.4)
        self.base_color = (180, 80, 255)
        self.color = self.base_color
        self.health = int(30 + level * 2.5)
        self.speed = 0.12 + 0.01 * (level // 10)

    def draw(self, surface, shop, WHITE=(255,255,255)):
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
        max_offset = int(12 * 0.7)
        min_offset = 0
        max_shadow_radius = int((self.radius + 6) * 0.7)
        min_shadow_radius = 0
        max_dist = 400
        shadow_offset = int(min_offset + (max_offset - min_offset) * min(dist, max_dist) / max_dist)
        shadow_radius = int(min_shadow_radius + (max_shadow_radius - min_shadow_radius) * min(dist, max_dist) / max_dist)
        if shadow_radius > 0:
            shadow_x = int(self.x + dx * shadow_offset)
            shadow_y = int(self.y + dy * shadow_offset)
            pygame.draw.circle(surface, (60, 30, 60), (shadow_x, shadow_y), shadow_radius)
        for i in range(self.radius, 0, -1):
            color_ratio = i / self.radius
            r = int(self.base_color[0] * color_ratio + 255 * (1 - color_ratio))
            g = int(self.base_color[1] * color_ratio + 255 * (1 - color_ratio))
            b = int(self.base_color[2] * color_ratio + 255 * (1 - color_ratio))
            pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), i)
        highlight_rect = pygame.Rect(0, 0, self.radius, self.radius // 2)
        highlight_rect.center = (int(self.x - self.radius // 3), int(self.y - self.radius // 3))
        pygame.draw.ellipse(surface, (255, 255, 255, 120), highlight_rect)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 3)
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"HP: {self.health}", True, WHITE)
        surface.blit(text, (int(self.x) - 40, int(self.y) - self.radius - 30))
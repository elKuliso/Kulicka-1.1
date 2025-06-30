import math
import pygame
import random

class Arrow:
    def __init__(self, x, y, target_x, target_y, shop, player):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.radius = 8
        # Barva šipky závisí na úrovni explozivního upgradu
        explosive = shop.explosive_radius
        red = min(255, 200 + explosive * 2)
        green = max(0, 80 - explosive)
        blue = max(0, 80 - explosive // 2)
        self.color = (red, green, blue)
        self.speed = 15
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = dx / dist * self.speed
        self.vy = dy / dist * self.speed
        self.shop = shop
        self.player = player

    def update(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        # Pokud je explozivní upgrade, vykresli i záři
        if self.shop.explosive_radius > 0:
            s = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            intensity = min(180, 60 + self.shop.explosive_radius)
            pygame.draw.circle(s, (255, 40, 40, intensity), (self.radius*2, self.radius*2), self.radius*2)
            surface.blit(s, (int(self.x - self.radius*2), int(self.y - self.radius*2)))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def off_screen(self, logical_width, logical_height):
        return (self.x < -self.radius or self.x > logical_width + self.radius or
                self.y < -self.radius or self.y > logical_height + self.radius)

    def collides_with(self, enemy):
        # Line-circle intersection (lepší detekce rychlých šipek)
        ex, ey, er = enemy.x, enemy.y, enemy.radius
        ax, ay = self.prev_x, self.prev_y
        bx, by = self.x, self.y
        abx = bx - ax
        aby = by - ay
        acx = ex - ax
        acy = ey - ay
        ab_len2 = abx * abx + aby * aby
        if ab_len2 == 0:
            t = 0
        else:
            t = max(0, min(1, (acx * abx + acy * aby) / ab_len2))
        closest_x = ax + abx * t
        closest_y = ay + aby * t
        dist = math.hypot(closest_x - ex, closest_y - ey)
        return dist < self.radius + er
    
class Rocket:
     def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.radius = 9
        self.color = (255, 120, 40)
        self.speed = 8
        self.target = target
        # Start směrem od hráče (z boku)
        angle = math.atan2(target.y - y, target.x - x) + random.choice([-1, 1]) * math.pi / 2
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.trail = []  # pro kouřovou stopu
     def update(self):
        # Navádění na cíl
        if self.target and not self.target.is_dead():
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.atan2(dy, dx)
            self.vx += (math.cos(angle) * self.speed - self.vx) * 0.08
            self.vy += (math.sin(angle) * self.speed - self.vy) * 0.08
        self.x += self.vx
        self.y += self.vy
        # Přidej pozici do stopy
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)

     def draw(self, surface):
        # Kouřová stopa
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(60 * (i / len(self.trail)))
            color = (120, 120, 120, alpha)
            s = pygame.Surface((self.radius, self.radius), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (self.radius // 2, self.radius // 2), max(2, self.radius // 3 - i // 2))
            surface.blit(s, (int(tx - self.radius // 2), int(ty - self.radius // 2)))
        # Plamen
        flame_len = self.radius * 1.5
        angle = math.atan2(self.vy, self.vx)
        fx = self.x - math.cos(angle) * flame_len
        fy = self.y - math.sin(angle) * flame_len
        pygame.draw.line(surface, (255, 200, 40), (self.x, self.y), (fx, fy), 8)
        pygame.draw.line(surface, (255, 80, 10), (self.x, self.y), (fx, fy), 3)
        # Tělo rakety
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.rect(surface, (255, 200, 80), (int(self.x)-4, int(self.y)-self.radius-8, 8, 16), border_radius=4)

     def off_screen(self, logical_width, logical_height):
        return (self.x < -self.radius or self.x > logical_width + self.radius or
                self.y < -self.radius or self.y > logical_height + self.radius)

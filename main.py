import pygame
import sys
import random
import time
import math

try:
    from player import vibrator
except ImportError:
    vibrator = None

from settings import *
from player import Player, Joystick
from enemy import Enemy, FastEnemy, TankEnemy, ZigZagEnemy, BossEnemy
from loot import Loot, Particle
from shop import Shop
from arrow import Arrow, Rocket
from ui import (
    show_settings_window, settings_loop, show_menu_window, menu_loop,
    show_achievements_window, achievements_loop, show_game_over_menu, restart_game
)

def main():
    # Inicializace pygame a základních proměnných
    pygame.init()
    screen = pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    pygame.display.set_caption("2D hra pouze na výšku")
    clock = pygame.time.Clock()

    # Všechny objekty až po pygame.init()
    player_speed = 1.0
    player = Player(player_speed)
    joystick = Joystick()
    shop = Shop()
    loots = [Loot() for _ in range(5)]
    particles = []
    arrows = []
    enemies = [Enemy(level=1)]

    segment_length_base = int(15 * 0.5)
    tail_segments = []
    max_segments = 10  # základní "životy" hráče

    # --- Funkce pro délku segmentu ocasu ---
    def get_segment_length(level):
        growth = 1 + 0.05 * (level // 10)
        return int(segment_length_base * growth)

    def update_tail():
        if max_segments == 0:
            return
        segment_length = get_segment_length(level)
        if len(tail_segments) < max_segments:
            tail_segments.extend([[player.x, player.y]] * (max_segments - len(tail_segments)))
        elif len(tail_segments) > max_segments:
            del tail_segments[max_segments:]
        tail_segments[0][0] = player.x
        tail_segments[0][1] = player.y
        for i in range(1, max_segments):
            prev_x, prev_y = tail_segments[i - 1]
            cur_x, cur_y = tail_segments[i]
            dx = prev_x - cur_x
            dy = prev_y - cur_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                target_dist = segment_length
                if dist > target_dist:
                    angle = math.atan2(dy, dx)
                    tail_segments[i][0] = prev_x - math.cos(angle) * target_dist
                    tail_segments[i][1] = prev_y - math.sin(angle) * target_dist

    def draw_tail(surface):
        for i, (x, y) in enumerate(tail_segments):
            growth = 1 + 0.05 * (level // 10)
            radius = max(int((player.radius // 2 - i // 3) * growth), 3)
            pygame.draw.circle(surface, GOLD, (int(x), int(y)), radius)

    rocket_level = 0
    rockets = []
    rocket_damage = 5
    rocket_upgrade_cost = 100
    rocket_damage_upgrade_cost = 120

    def shoot_arrows():
        nonlocal arrows, player, enemies, shop
        player.update_shoot_timer()
        if not player.can_shoot():
            return
        target = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
            if dist <= shop.shoot_range and dist < min_dist:
                min_dist = dist
                target = enemy
        if target:
            arrows.append(Arrow(player.x, player.y, target.x, target.y, shop, player))
            player.reset_shoot_timer()

    # 1. Při startu nastav ocas podle skóre (nebo nastav základní délku jako životy)
    tail_segments = []
    max_segments = 10  # základní "životy" hráče

    # 2. Funkce pro zmenšení ocasu (životů)
    def reduce_tail(damage):
        nonlocal max_segments
        max_segments = max(0, max_segments - int(damage))
        while len(tail_segments) > max_segments:
            tail_segments.pop()

    running = True
    paused = False
    pause_width = 70   # původně 100
    pause_height = 56  # původně 80
    pause_rect = pygame.Rect(LOGICAL_WIDTH - pause_width - 20, 20, pause_width, pause_height)

    shop = Shop()
    shop.icon_size = 56  # původně 80
    shop.x = pause_rect.x - shop.icon_size - 16  # menší mezera, aby to sedělo k menším tlačítkům
    shop.y = pause_rect.y
    shop.icon_rect = pygame.Rect(shop.x, shop.y, shop.icon_size, shop.icon_size)

    # Nastavení pro vibrace a citlivost
    settings = {
        "vibration": True,
        "sensitivity": 1.6
    }

    next_loot_time = time.time() + random.uniform(1, 10)

    achievements = {
        "score_100": False,
        "level_10": False,
        "enemy_100": False
    }
    achievement_queue = []
    achievement_timer = 0

    # Nové proměnné pro rakety
    rocket_cooldown = 1200  # 10 sekund při FPS 120
    rocket_timer = 0

    level = 1
    score = 0
    enemy_kill_count = 1

    shop_message = ""
    shop_message_timer = 0

    # Hlavní smyčka hry
    running = True
    while running:
        # Zpracování událostí
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Scrollování obchodu kolečkem myši (PC)
            if event.type == pygame.MOUSEWHEEL:
                shop.handle_scroll(event)
            if event.type == pygame.FINGERDOWN:
                touch_start = (event.x * LOGICAL_WIDTH, event.y * LOGICAL_HEIGHT)
            if event.type == pygame.FINGERMOTION and touch_start:
                touch_end = (event.x * LOGICAL_WIDTH, event.y * LOGICAL_HEIGHT)
                shop.handle_touch_scroll(touch_start, touch_end)
                touch_start = touch_end
            if event.type == pygame.FINGERUP:
                touch_start = None
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                # Získání pozice pro dotyk i myš
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                else:  # FINGERDOWN
                    click_pos = (event.x * LOGICAL_WIDTH, event.y * LOGICAL_HEIGHT)
                # Nejprve: pokud kliknu na pauzu, otevři menu
                if pause_rect.collidepoint(click_pos):
                    menu_loop()
                    continue
                # Otevři obchod při kliknutí na ikonu obchodu
                if shop.icon_rect.collidepoint(click_pos):
                    shop.visible = True
                    continue
                # Pak obchod
                result = shop.handle_click(click_pos, player, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost)
                if result[0]:
                    _, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost = result
                    shop_message = "Zakoupeno!"
                    shop_message_timer = pygame.time.get_ticks()
                    continue
                # Pokud kliknutí bylo do shop_rect a nebyl nákup, ale obchod je otevřený, zobraz nedostatek skóre
                if shop.visible and shop.shop_rect.collidepoint(click_pos):
                    shop_message = "Nedostatek skóre!"
                    shop_message_timer = pygame.time.get_ticks()
                    continue
                # Pak joystick (pouze pro myš)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    joystick.start(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                joystick.stop()
            if event.type == pygame.MOUSEMOTION:
                joystick.move(event.pos)
            if event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                if w <= h:
                    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

        if paused:
            font = pygame.font.SysFont(None, 100)
            pause_text = font.render("PAUZA", True, WHITE)
            screen.blit(pause_text, (LOGICAL_WIDTH // 2 - 120, LOGICAL_HEIGHT // 2 - 50))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        joystick.sensitivity = settings["sensitivity"]
        dx, dy = joystick.get_vector()
        player.x += dx * player.speed
        player.y += dy * player.speed

        for enemy in enemies[:]:
            dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
            if dist < player.radius + enemy.radius:
                reduce_tail(enemy.health)  # nebo např. reduce_tail(1)
                # Můžeš přidat efekt, zvuk, atd.
                enemies.remove(enemy)

        for loot in loots[:]:
            dist = math.hypot(player.x - loot.x, player.y - loot.y)
            magnet_radius = 5 * (shop.loot_radius + player.radius)
            if dist < magnet_radius:
                loots.remove(loot)
                score += 1
                max_segments += 1  # přidej "život"
                while len(tail_segments) < max_segments:
                    tail_segments.append([player.x, player.y])
                # Krásná barevná animace ohňostroje
                for _ in range(32):
                    color = (
                        random.randint(120, 255),
                        random.randint(120, 255),
                        random.randint(120, 255)
                    )
                    particles.append(Particle(loot.x, loot.y, color=color, radius=random.randint(3, 7), life=random.randint(18, 32)))
        while len(loots) < 5:
            loots.append(Loot())

        update_tail()

        # Pohyb nepřátel
        for enemy in enemies:
            enemy.move_towards_player(player.x, player.y)

        # Aktualizace šipek (pohyb a kolize)
        for arrow in arrows[:]:
            arrow.update()
            if arrow.off_screen(LOGICAL_WIDTH, LOGICAL_HEIGHT):
                arrows.remove(arrow)
                continue
            hit = False
            for enemy in enemies[:]:
                if arrow.collides_with(enemy):
                    enemy.health -= player.damage
                    hit = True
                    if enemy.is_dead():
                        # ... split_on_death ...
                        enemies.remove(enemy)
                        enemy_kill_count += 1
                        score += 5 * 10
                        for _ in range(30):
                            particles.append(Particle(enemy.x, enemy.y))
                        # Vibrace při zabití enemy
                        if settings.get("vibration", False) and 'vibrator' in globals() and vibrator:
                            try:
                                vibrator.vibrate
                            except TypeError:
                                try:
                                    vibrator.vibrate(0.1)
                                except Exception:
                                    pass
                            except Exception:
                                pass
            if hit and arrow in arrows:
                arrows.remove(arrow)

        # Aktualizace částic
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0 or particle.radius <= 0:
                particles.remove(particle)

        shoot_arrows()

        # LEVEL UP a generování nepřátel
        if len(enemies) == 0:
            level += 1
            if level % 10 == 0:
                enemies.append(BossEnemy(level=level))
            else:
                # Vždy alespoň 1 náhodný enemy
                enemy_types = [Enemy, FastEnemy, TankEnemy, ZigZagEnemy]
                chosen_enemy = random.choice(enemy_types)
                enemies.append(chosen_enemy(level=level))
                # Dále můžeš přidat další podle původní logiky, pokud chceš více nepřátel na vyšších levelech

        # Po zabití enemy (v cyklu kde je: if enemy.is_dead(): ...)
        if not achievements["enemy_100"] and enemy_kill_count >= 100:
            achievements["enemy_100"] = True
            achievement_queue.append("Zabil jsi 100 nepřátel!")

        # Po zvýšení skóre (např. po sebrání lootu nebo zabití enemy)
        if not achievements["score_100"] and score >= 100:
            achievements["score_100"] = True
            achievement_queue.append("Skóre 100!")

        # Po level up
        if not achievements["level_10"] and level >= 10:
            achievements["level_10"] = True
            achievement_queue.append("Level 10 dosažen!")

        # Vykreslení
        screen.fill(BLACK)

        # Vykresli loot
        for loot in loots:
            loot.draw(screen)

        # Vykresli ocas hada
        draw_tail(screen)

        # Vykresli hráče
        player.draw(screen)

        # Vykresli nepřátele
        for enemy in enemies:
            enemy.draw(screen, shop)

        # Vykresli šipky
        for arrow in arrows:
            arrow.draw(screen)

        # Vykresli částice
        for particle in particles:
            particle.draw(screen)

        # Vykresli skóre a level
        font = pygame.font.SysFont(None, 50)
        score_text = font.render(f"Skóre: {score}", True, WHITE)
        level_text = font.render(f"Úroveň: {level}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(level_text, (20, 80))

        # Vykresli obchod
        shop.draw_icon(screen)
        if shop.visible:
            shop.draw_shop(screen, player, rocket_cooldown=rocket_cooldown, rocket_level=rocket_level, rocket_upgrade_cost=rocket_upgrade_cost, rocket_damage=rocket_damage, rocket_damage_upgrade_cost=rocket_damage_upgrade_cost, FPS=FPS)
            # Zobraz hlášku po nákupu nebo při nedostatku skóre
            if shop_message:
                font_msg = pygame.font.SysFont(None, 44)
                surf = font_msg.render(shop_message, True, (255, 255, 80) if shop_message == "Zakoupeno!" else (255, 80, 80))
                rect = surf.get_rect(center=(LOGICAL_WIDTH // 2, shop.shop_rect.y + shop.shop_rect.height - 40))
                pygame.draw.rect(screen, (40, 40, 80), rect.inflate(40, 20), border_radius=12)
                pygame.draw.rect(screen, GOLD, rect.inflate(40, 20), 2, border_radius=12)
                screen.blit(surf, rect)
                # Hláška zmizí po 1.2s
                if pygame.time.get_ticks() - shop_message_timer > 1200:
                    shop_message = ""

        # --- Vylepšené tlačítko pauzy ve stejném stylu jako obchod ---
        # Stín pod tlačítkem
        shadow = pygame.Surface((pause_rect.width, pause_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (30, 30, 40, 120), (8, 12, pause_rect.width-16, pause_rect.height-8))
        screen.blit(shadow, (pause_rect.x, pause_rect.y + 8))

        # Gradientové tlačítko
        pause_surf = pygame.Surface((pause_rect.width, pause_rect.height), pygame.SRCALPHA)
        for y in range(pause_rect.height):
            ratio = y / pause_rect.height
            r = int(80 + 100 * ratio)
            g = int(80 + 80 * (1 - ratio))
            b = int(160 + 60 * ratio)
            pygame.draw.line(pause_surf, (r, g, b, 255), (0, y), (pause_rect.width, y))
        pygame.draw.ellipse(pause_surf, (255,255,255,30), (0, 0, pause_rect.width, pause_rect.height//2))
        screen.blit(pause_surf, (pause_rect.x, pause_rect.y))

        # Bílý rámeček
        pygame.draw.rect(screen, WHITE, pause_rect, 3, border_radius=20)

        # Ikona pauzy (dva bílé obdélníky)
        bar_w = pause_rect.width // 6
        bar_h = pause_rect.height // 2
        bar_x1 = pause_rect.x + pause_rect.width // 3 - bar_w // 2
        bar_x2 = pause_rect.x + 2 * pause_rect.width // 3 - bar_w // 2
        bar_y = pause_rect.y + pause_rect.height // 4
        pygame.draw.rect(screen, WHITE, (bar_x1, bar_y, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, WHITE, (bar_x2, bar_y, bar_w, bar_h), border_radius=6)

        # Volitelně zobraz počet životů na obrazovce:
        font = pygame.font.SysFont(None, 50)
        lives_text = font.render(f"Životy: {max_segments}", True, GOLD)
        screen.blit(lives_text, (20, 140))

        # --- Přidání lootu po náhodném čase ---
        if time.time() >= next_loot_time:
            loots.append(Loot())
            next_loot_time = time.time() + random.uniform(1, 10)

        if achievement_queue:
            if achievement_timer == 0:
                achievement_timer = pygame.time.get_ticks()
            font_ach = pygame.font.SysFont(None, 48)
            msg = achievement_queue[0]
            surf = font_ach.render(f"Achievement: {msg}", True, (255, 255, 80))
            rect = surf.get_rect(center=(LOGICAL_WIDTH // 2, 180))
            pygame.draw.rect(screen, (40, 40, 80), rect.inflate(40, 30), border_radius=16)
            pygame.draw.rect(screen, GOLD, rect.inflate(40, 30), 3, border_radius=16)
            screen.blit(surf, rect)
            # Zobraz 2.5 sekundy
            if pygame.time.get_ticks() - achievement_timer > 2500:
                achievement_queue.pop(0)
                achievement_timer = 0

        # Rakety
        if rocket_level > 0:
            rocket_timer += 1
            if rocket_timer >= rocket_cooldown:
                if enemies:
                    target = min(enemies, key=lambda e: math.hypot(player.x - e.x, player.y - e.y))
                    angle = math.atan2(target.y - player.y, target.x - player.x)
                    side = random.choice([-1, 1])
                    rx = player.x + math.cos(angle + side * math.pi/2) * player.radius
                    ry = player.y + math.sin(angle + side * math.pi/2) * player.radius
                    rockets.append(Rocket(rx, ry, target))
                    rocket_timer = 0
        for rocket in rockets[:]:
            rocket.update()
            if rocket.off_screen(LOGICAL_WIDTH, LOGICAL_HEIGHT):
                rockets.remove(rocket)
                continue
            if rocket.target and not rocket.target.is_dead():
                if math.hypot(rocket.x - rocket.target.x, rocket.y - rocket.target.y) < rocket.radius + rocket.target.radius:
                    rocket.target.health -= player.damage * rocket_damage
                    particles.extend([Particle(rocket.x, rocket.y, color=(255, 120, 40)) for _ in range(40)])
                    rockets.remove(rocket)
        for rocket in rockets:
            rocket.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


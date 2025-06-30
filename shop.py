from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT, WHITE, GOLD, SHOP_BG_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, LOOT_COLOR
import pygame
import math

class Shop:
    def __init__(self):
        self.width = 600   # zmenšeno
        self.height = 500  # zmenšeno
        self.icon_size = 80
        self.x = (LOGICAL_WIDTH - self.icon_size) // 2
        self.y = 20
        self.visible = False
        self.font = pygame.font.SysFont(None, 36)
        self.speed_upgrade_cost = 10
        self.shoot_range_upgrade_cost = 15
        self.shoot_speed_upgrade_cost = 25
        self.damage_upgrade_cost = 5
        self.loot_radius_upgrade_cost = 30  # cena upgradu
        self.explosive_upgrade_cost = 80
        self.shoot_range = 200  # počáteční dosah střelby
        self.loot_radius = 0    # počáteční radius pro auto-sběr
        self.explosive_radius = 0
        self.visible_buttons = []

        # Vycentrování shop_rect na střed obrazovky
        self.shop_rect = pygame.Rect(
            (LOGICAL_WIDTH - self.width) // 2,
            (LOGICAL_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        self.icon_rect = pygame.Rect(self.x, self.y, self.icon_size, self.icon_size)
        self.button_speed_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 80, self.width - 32, 60)
        self.button_damage_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 150, self.width - 32, 60)
        self.button_shoot_speed_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 220, self.width - 32, 60)
        self.button_range_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 290, self.width - 32, 60)
        self.button_loot_radius_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 360, self.width - 32, 60)
        self.button_explosive_rect = pygame.Rect(self.shop_rect.x + 16, self.shop_rect.y + 430, self.width - 32, 60)

        # Raketové upgrady vedle sebe, větší mezera od předchozích
        self.button_rocket_rect = pygame.Rect(self.shop_rect.x + 40, self.shop_rect.y + 520, (self.width - 100)//2, 60)
        self.button_rocket_damage_rect = pygame.Rect(self.shop_rect.x + 60 + (self.width - 100)//2, self.shop_rect.y + 520, (self.width - 100)//2, 60)
        self.scroll_offset = 0  # pro budoucí scrollování

    def draw_icon(self, surface):
        # Jemný stín pod tlačítkem
        shadow = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (30, 30, 40, 120), (8, 12, self.icon_size-16, self.icon_size-8))
        surface.blit(shadow, (self.x, self.y + 8))

        # Gradientové tlačítko
        icon_surf = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        for y in range(self.icon_size):
            ratio = y / self.icon_size
            r = int(80 + 100 * ratio)
            g = int(80 + 80 * (1 - ratio))
            b = int(160 + 60 * ratio)
            pygame.draw.line(icon_surf, (r, g, b, 255), (0, y), (self.icon_size, y))
        pygame.draw.ellipse(icon_surf, (255,255,255,30), (0, 0, self.icon_size, self.icon_size//2))
        surface.blit(icon_surf, (self.x, self.y))

        # Bílý rámeček
        pygame.draw.rect(surface, WHITE, self.icon_rect, 3, border_radius=18)

        # Ikona "košíku" (obchod)
        cx, cy = self.icon_rect.center
        pygame.draw.rect(surface, (255, 215, 0), (cx-18, cy-8, 36, 18), border_radius=6)
        pygame.draw.arc(surface, (255, 215, 0), (cx-18, cy-18, 36, 20), math.pi, 2*math.pi, 4)
        pygame.draw.circle(surface, (255, 215, 0), (cx-12, cy+12), 5)
        pygame.draw.circle(surface, (255,215,0), (cx+12, cy+12), 5)

    def handle_scroll(self, event):
        # Oprava: MOUSEWHEEL nemá event.pos, použijeme aktuální pozici myši
        if self.visible:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.shop_rect.collidepoint(mouse_x, mouse_y):
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll_offset -= event.y * 40  # rychlost scrollu
                    min_offset = 0
                    max_offset = max(0, 80 * 8 - self.height + 100)
                    self.scroll_offset = max(min_offset, min(self.scroll_offset, max_offset))

    def handle_touch_scroll(self, start_pos, end_pos):
        # Posun podle rozdílu Y (jen pokud je obchod otevřený a dotyk ve shop_rect)
        if self.visible and self.shop_rect.collidepoint(start_pos):
            dy = end_pos[1] - start_pos[1]
            self.scroll_offset -= dy
            min_offset = 0
            max_offset = max(0, 80 * 8 - self.height + 100)
            self.scroll_offset = max(min_offset, min(self.scroll_offset, max_offset))

    def draw_shop(self, surface, player, rocket_cooldown=0, rocket_level=0, rocket_upgrade_cost=0, rocket_damage=0, rocket_damage_upgrade_cost=0, FPS=60):
        # Větší okno a dynamická výška
        self.height = 600
        self.shop_rect = pygame.Rect(
            (LOGICAL_WIDTH - self.width) // 2,
            (LOGICAL_HEIGHT - self.height) // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, SHOP_BG_COLOR, self.shop_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.shop_rect, 3, border_radius=10)
        title = self.font.render("Obchod - Vylepšení", True, WHITE)
        surface.blit(title, (self.shop_rect.x + 20, self.shop_rect.y + 20))

        mouse_pos = pygame.mouse.get_pos()

        # Menší fonty pro přehlednější vzhled upgradů
        font_label = pygame.font.SysFont(None, 22)
        font_desc = pygame.font.SysFont(None, 16)
        font_cost = pygame.font.SysFont(None, 16)
        font_button = pygame.font.SysFont(None, 18)

        upgrades = [
            {
                "rect": self.button_speed_rect,
                "label": "Rychlost pohybu",
                "desc": f"Aktuální: {int(player.speed)}",
                "cost": self.speed_upgrade_cost,
                "button": "Koupit rychlost"
            },
            {
                "rect": self.button_damage_rect,
                "label": "Poškození šipky",
                "desc": f"Aktuální: {round(player.damage, 2)}",
                "cost": self.damage_upgrade_cost,
                "button": "Zvýšit poškození"
            },
            {
                "rect": self.button_shoot_speed_rect,
                "label": "Rychlost střelby",
                "desc": f"Rychlost: {round(60 / player.shoot_cooldown, 1)} /s",
                "cost": self.shoot_speed_upgrade_cost,
                "button": "Rychlejší střelba"
            },
            {
                "rect": self.button_range_rect,
                "label": "Dosah střelby",
                "desc": f"Aktuální: {self.shoot_range}",
                "cost": self.shoot_range_upgrade_cost,
                "button": "Koupit dosah"
            },
            {
                "rect": self.button_loot_radius_rect,
                "label": "Magnet",
                "desc": f"Sbírá loot z {5 * (self.loot_radius + player.radius)} px",
                "cost": self.loot_radius_upgrade_cost,
                "button": "Zvýšit magnet"
            },
            {
                "rect": self.button_explosive_rect,
                "label": "Explozivní šipky",
                "desc": f"Poloměr: {self.explosive_radius} px",
                "cost": self.explosive_upgrade_cost,
                "button": "Zvětšit explozi"
            },
            # --- větší mezera ---
            {
                "rect": self.button_rocket_rect,
                "label": "Raketomet",
                "desc": f"Cooldown: {round(rocket_cooldown / FPS, 1)} s" if rocket_level > 0 else "Neaktivní",
                "cost": rocket_upgrade_cost,
                "button": "Zrychlit raketomet"
            },
            {
                "rect": self.button_rocket_damage_rect,
                "label": "Poškození raket",
                "desc": f"Aktuální: {rocket_damage}x",
                "cost": rocket_damage_upgrade_cost,
                "button": "Zvýšit poškození raket"
            }
        ]
        # --- Bloky pro vykreslení vedle sebe ---
        # Poškození šipky a rychlost střelby na jednom řádku
        # Dosah střelby a explozivní šipky na jednom řádku
        # Raketomet a poškození raket na jednom řádku
        paired_upgrades = [
            [upgrades[1], upgrades[2]],  # Poškození šipky, Rychlost střelby
            [upgrades[3], upgrades[5]],  # Dosah střelby, Explozivní šipky
            [upgrades[6], upgrades[7]],  # Raketomet, Poškození raket
        ]
        single_upgrades = [upgrades[0], upgrades[4]]  # Rychlost pohybu, Loot radius
        # Scrollovací plocha
        scroll_area = pygame.Surface((self.width, self.height-60), pygame.SRCALPHA)
        scroll_y = 20 - self.scroll_offset
        upg_width = 260  # zvětšeno pro širší tlačítka
        upg_gap = 40     # větší mezera mezi páry
        upg_x_left = (self.width // 2) - upg_width - (upg_gap // 2)
        upg_x_right = (self.width // 2) + (upg_gap // 2)
        self.visible_buttons = []
        idx = 0
        # První single upgrade
        upg = single_upgrades[0]
        upg_rect = upg["rect"].copy()
        upg_rect.x = (self.width - 420) // 2
        upg_rect.width = 420
        upg_rect.y = scroll_y + idx * 80
        grad_surf = pygame.Surface((upg_rect.width, upg_rect.height), pygame.SRCALPHA)
        for y in range(upg_rect.height):
            ratio = y / upg_rect.height
            r = int(60 + 80 * ratio)
            g = int(60 + 60 * (1 - ratio))
            b = int(120 + 80 * ratio)
            pygame.draw.line(grad_surf, (r, g, b, 220), (0, y), (upg_rect.width, y))
        shadow_rect = upg_rect.move(3, 5)
        pygame.draw.rect(scroll_area, (30, 30, 40, 90), shadow_rect, border_radius=14)
        scroll_area.blit(grad_surf, upg_rect.topleft)
        pygame.draw.rect(scroll_area, WHITE, upg_rect, 2, border_radius=14)
        icon_color = (255, 215, 0) if "rychlost" in upg["label"].lower() else (100, 255, 100)
        icon_center = (upg_rect.x + 35, upg_rect.centery)
        pygame.draw.circle(scroll_area, icon_color, icon_center, 22)
        label = font_label.render(upg["label"], True, GOLD)
        scroll_area.blit(label, (upg_rect.x + 60, upg_rect.y + 6))
        desc = font_desc.render(upg["desc"], True, WHITE)
        desc_rect = desc.get_rect()
        desc_rect.topleft = (upg_rect.x + 60, upg_rect.y + 30)
        scroll_area.blit(desc, desc_rect)
        cost = font_cost.render(f"Cena: {upg['cost']}", True, LOOT_COLOR)
        cost_rect = cost.get_rect()
        cost_rect.topright = (upg_rect.right - 18, upg_rect.y + 6)
        scroll_area.blit(cost, cost_rect)
        button = font_button.render(upg["button"], True, WHITE)
        button_rect = button.get_rect(center=(upg_rect.centerx, upg_rect.y + upg_rect.height - 14))
        scroll_area.blit(button, button_rect)
        abs_button_rect = pygame.Rect(
            self.shop_rect.x + upg_rect.x + button_rect.x,
            self.shop_rect.y + 60 + upg_rect.y + button_rect.y,
            button_rect.width,
            button_rect.height
        )
        # Přidat klikací oblast i na ikonu (kruh)
        abs_icon_rect = pygame.Rect(
            self.shop_rect.x + icon_center[0] - 22,
            self.shop_rect.y + 60 + icon_center[1] - 22,
            44, 44
        )
        self.visible_buttons.append({"rect": abs_button_rect, "type": "speed"})
        self.visible_buttons.append({"rect": abs_icon_rect, "type": "speed"})
        idx += 1
        # Párované upgrady vedle sebe
        for pair_idx, (left, right) in enumerate(paired_upgrades):
            left_rect = left["rect"].copy()
            left_rect.x = upg_x_left
            left_rect.width = upg_width
            left_rect.y = scroll_y + idx * 80
            right_rect = right["rect"].copy()
            right_rect.x = upg_x_right
            right_rect.width = upg_width
            right_rect.y = scroll_y + idx * 80
            # Vykresli levou
            grad_surf = pygame.Surface((left_rect.width, left_rect.height), pygame.SRCALPHA)
            for y in range(left_rect.height):
                ratio = y / left_rect.height
                r = int(60 + 80 * ratio)
                g = int(60 + 60 * (1 - ratio))
                b = int(120 + 80 * ratio)
                pygame.draw.line(grad_surf, (r, g, b, 220), (0, y), (left_rect.width, y))
            shadow_rect = left_rect.move(3, 5)
            pygame.draw.rect(scroll_area, (30, 30, 40, 90), shadow_rect, border_radius=14)
            scroll_area.blit(grad_surf, left_rect.topleft)
            pygame.draw.rect(scroll_area, WHITE, left_rect, 2, border_radius=14)
            icon_color = (255, 215, 0) if "rychlost" in left["label"].lower() else (100, 255, 100)
            icon_center = (left_rect.x + 35, left_rect.centery)
            pygame.draw.circle(scroll_area, icon_color, icon_center, 22)
            label = font_label.render(left["label"], True, GOLD)
            scroll_area.blit(label, (left_rect.x + 60, left_rect.y + 6))
            desc = font_desc.render(left["desc"], True, WHITE)
            desc_rect = desc.get_rect()
            desc_rect.topleft = (left_rect.x + 60, left_rect.y + 30)
            scroll_area.blit(desc, desc_rect)
            cost = font_cost.render(f"Cena: {left['cost']}", True, LOOT_COLOR)
            cost_rect = cost.get_rect()
            cost_rect.topright = (left_rect.right - 18, left_rect.y + 6)
            scroll_area.blit(cost, cost_rect)
            button = font_button.render(left["button"], True, WHITE)
            button_rect = button.get_rect(center=(left_rect.centerx, left_rect.y + left_rect.height - 14))
            scroll_area.blit(button, button_rect)
            abs_left_button_rect = pygame.Rect(
                self.shop_rect.x + left_rect.x + button_rect.x,
                self.shop_rect.y + 60 + left_rect.y + button_rect.y,
                button_rect.width,
                button_rect.height
            )
            abs_left_icon_rect = pygame.Rect(
                self.shop_rect.x + icon_center[0] - 22,
                self.shop_rect.y + 60 + icon_center[1] - 22,
                44, 44
            )
            # Vykresli pravou
            grad_surf = pygame.Surface((right_rect.width, right_rect.height), pygame.SRCALPHA)
            for y in range(right_rect.height):
                ratio = y / right_rect.height
                r = int(60 + 80 * ratio)
                g = int(60 + 60 * (1 - ratio))
                b = int(120 + 80 * ratio)
                pygame.draw.line(grad_surf, (r, g, b, 220), (0, y), (right_rect.width, y))
            shadow_rect = right_rect.move(3, 5)
            pygame.draw.rect(scroll_area, (30, 30, 40, 90), shadow_rect, border_radius=14)
            scroll_area.blit(grad_surf, right_rect.topleft)
            pygame.draw.rect(scroll_area, WHITE, right_rect, 2, border_radius=14)
            icon_color = (255, 215, 0) if "rychlost" in right["label"].lower() else (100, 255, 100)
            icon_center = (right_rect.x + 35, right_rect.centery)
            pygame.draw.circle(scroll_area, icon_color, icon_center, 22)
            label = font_label.render(right["label"], True, GOLD)
            scroll_area.blit(label, (right_rect.x + 60, right_rect.y + 6))
            desc = font_desc.render(right["desc"], True, WHITE)
            desc_rect = desc.get_rect()
            desc_rect.topleft = (right_rect.x + 60, right_rect.y + 30)
            scroll_area.blit(desc, desc_rect)
            cost = font_cost.render(f"Cena: {right['cost']}", True, LOOT_COLOR)
            cost_rect = cost.get_rect()
            cost_rect.topright = (right_rect.right - 18, right_rect.y + 6)
            scroll_area.blit(cost, cost_rect)
            button = font_button.render(right["button"], True, WHITE)
            button_rect = button.get_rect(center=(right_rect.centerx, right_rect.y + right_rect.height - 14))
            scroll_area.blit(button, button_rect)
            abs_right_button_rect = pygame.Rect(
                self.shop_rect.x + right_rect.x + button_rect.x,
                self.shop_rect.y + 60 + right_rect.y + button_rect.y,
                button_rect.width,
                button_rect.height
            )
            abs_right_icon_rect = pygame.Rect(
                self.shop_rect.x + icon_center[0] - 22,
                self.shop_rect.y + 60 + icon_center[1] - 22,
                44, 44
            )
            # Uložení rectů s typem - přesně button_rect i ikona
            if pair_idx == 0:
                self.visible_buttons.append({"rect": abs_left_button_rect, "type": "damage"})
                self.visible_buttons.append({"rect": abs_left_icon_rect, "type": "damage"})
                self.visible_buttons.append({"rect": abs_right_button_rect, "type": "shoot_speed"})
                self.visible_buttons.append({"rect": abs_right_icon_rect, "type": "shoot_speed"})
            elif pair_idx == 1:
                self.visible_buttons.append({"rect": abs_left_button_rect, "type": "range"})
                self.visible_buttons.append({"rect": abs_left_icon_rect, "type": "range"})
                self.visible_buttons.append({"rect": abs_right_button_rect, "type": "explosive"})
                self.visible_buttons.append({"rect": abs_right_icon_rect, "type": "explosive"})
            elif pair_idx == 2:
                self.visible_buttons.append({"rect": abs_left_button_rect, "type": "rocket"})
                self.visible_buttons.append({"rect": abs_left_icon_rect, "type": "rocket"})
                self.visible_buttons.append({"rect": abs_right_button_rect, "type": "rocket_damage"})
                self.visible_buttons.append({"rect": abs_right_icon_rect, "type": "rocket_damage"})
            idx += 1
        # Zbytek upgradů pod sebe
        for upg in single_upgrades[1:]:
            upg_rect = upg["rect"].copy()
            upg_rect.x = (self.width - 420) // 2
            upg_rect.width = 420
            upg_rect.y = scroll_y + idx * 80
            grad_surf = pygame.Surface((upg_rect.width, upg_rect.height), pygame.SRCALPHA)
            for y in range(upg_rect.height):
                ratio = y / upg_rect.height
                r = int(60 + 80 * ratio)
                g = int(60 + 60 * (1 - ratio))
                b = int(120 + 80 * ratio)
                pygame.draw.line(grad_surf, (r, g, b, 220), (0, y), (upg_rect.width, y))
            shadow_rect = upg_rect.move(3, 5)
            pygame.draw.rect(scroll_area, (30, 30, 40, 90), shadow_rect, border_radius=14)
            scroll_area.blit(grad_surf, upg_rect.topleft)
            pygame.draw.rect(scroll_area, WHITE, upg_rect, 2, border_radius=14)
            icon_color = (255, 215, 0) if "rychlost" in upg["label"].lower() else (100, 255, 100)
            icon_center = (upg_rect.x + 35, upg_rect.centery)
            pygame.draw.circle(scroll_area, icon_color, icon_center, 22)
            label = font_label.render(upg["label"], True, GOLD)
            scroll_area.blit(label, (upg_rect.x + 60, upg_rect.y + 6))
            desc = font_desc.render(upg["desc"], True, WHITE)
            desc_rect = desc.get_rect()
            desc_rect.topleft = (upg_rect.x + 60, upg_rect.y + 30)
            scroll_area.blit(desc, desc_rect)
            cost = font_cost.render(f"Cena: {upg['cost']}", True, LOOT_COLOR)
            cost_rect = cost.get_rect()
            cost_rect.topright = (upg_rect.right - 18, upg_rect.y + 6)
            scroll_area.blit(cost, cost_rect)
            button = font_button.render(upg["button"], True, WHITE)
            button_rect = button.get_rect(center=(upg_rect.centerx, upg_rect.y + upg_rect.height - 14))
            scroll_area.blit(button, button_rect)
            abs_button_rect = pygame.Rect(
                self.shop_rect.x + upg_rect.x + button_rect.x,
                self.shop_rect.y + 60 + upg_rect.y + button_rect.y,
                button_rect.width,
                button_rect.height
            )
            abs_icon_rect = pygame.Rect(
                self.shop_rect.x + icon_center[0] - 22,
                self.shop_rect.y + 60 + icon_center[1] - 22,
                44, 44
            )
            self.visible_buttons.append({"rect": abs_button_rect, "type": "loot_radius"})
            self.visible_buttons.append({"rect": abs_icon_rect, "type": "loot_radius"})
            idx += 1
        # Vykresli scrollovací plochu do hlavního surface
        surface.blit(scroll_area, (self.shop_rect.x, self.shop_rect.y + 60))
        # (NEPŘEPISUJ self.visible_buttons zde!)

    def handle_click(self, pos, player, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost):
        if self.visible:
            # Pokud nejsou připravené recty, vygeneruj je do neviditelného surface
            if not self.visible_buttons:
                dummy_surface = pygame.Surface((self.width, self.height))
                self.draw_shop(dummy_surface, player, rocket_cooldown, rocket_level, rocket_upgrade_cost, rocket_damage, rocket_damage_upgrade_cost)
            for button in self.visible_buttons:
                if button["rect"].collidepoint(pos):
                    t = button["type"]
                    if t == "speed":
                        if score >= self.speed_upgrade_cost:
                            score -= self.speed_upgrade_cost
                            player.speed += 1
                            self.speed_upgrade_cost = int(self.speed_upgrade_cost * 1.5)
                    elif t == "damage":
                        if score >= self.damage_upgrade_cost:
                            score -= self.damage_upgrade_cost
                            player.damage += 2
                            self.damage_upgrade_cost = int(self.damage_upgrade_cost * 1.7)
                    elif t == "shoot_speed":
                        if score >= self.shoot_speed_upgrade_cost and player.shoot_cooldown > 5:
                            score -= self.shoot_speed_upgrade_cost
                            player.shoot_cooldown = max(5, player.shoot_cooldown - 3)
                            self.shoot_speed_upgrade_cost = int(self.shoot_speed_upgrade_cost * 1.7)
                    elif t == "range":
                        if score >= self.shoot_range_upgrade_cost:
                            score -= self.shoot_range_upgrade_cost
                            self.shoot_range += 50
                            self.shoot_range_upgrade_cost = int(self.shoot_range_upgrade_cost * 2)
                    elif t == "loot_radius":
                        if score >= self.loot_radius_upgrade_cost:
                            score -= self.loot_radius_upgrade_cost
                            self.loot_radius += 30
                            self.loot_radius_upgrade_cost = int(self.loot_radius_upgrade_cost * 2)
                    elif t == "explosive":
                        if score >= self.explosive_upgrade_cost:
                            score -= self.explosive_upgrade_cost
                            self.explosive_radius += 30
                            self.explosive_upgrade_cost = int(self.explosive_upgrade_cost * 1.7)
                    elif t == "rocket":
                        if score >= rocket_upgrade_cost:
                            score -= rocket_upgrade_cost
                            rocket_level += 1
                            rocket_cooldown = max(240, rocket_cooldown - 180)
                            rocket_upgrade_cost = int(rocket_upgrade_cost * 1.7)
                    elif t == "rocket_damage":
                        if score >= rocket_damage_upgrade_cost:
                            score -= rocket_damage_upgrade_cost
                            rocket_damage += 2
                            rocket_damage_upgrade_cost = int(rocket_damage_upgrade_cost * 1.7)
                    return True, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost
            # Kliknutí mimo shop zavře okno
            if not self.shop_rect.collidepoint(pos) and not self.icon_rect.collidepoint(pos):
                self.visible = False
                return True, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost
        else:
            if self.icon_rect.collidepoint(pos):
                self.visible = True
                return True, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost
        return False, score, rocket_cooldown, rocket_upgrade_cost, rocket_level, rocket_damage, rocket_damage_upgrade_cost

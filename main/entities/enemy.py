import pygame
import math
import random
from .projectiles import Egg

class EnemyChicken:
    def __init__(self, boss=False, killer=False):
        self.boss = boss
        self.killer = killer
        self.kind = "boss" if boss else ("killer" if killer else "normal")

        if boss:
            self.w, self.h = 120, 110
            self.hp = 20
        elif killer:
            self.w, self.h = 82, 78
            self.hp = 6
        else:
            self.w, self.h = 70, 70
            self.hp = 3

        self.x = 0
        self.y = 0

        base_cd = 0.65 if boss else 0.9
        if killer:
            base_cd = 0.65
        self.cooldown = base_cd if boss else random.uniform(base_cd, base_cd + 0.6)

        self.timer = random.uniform(0.1, 0.6)
        self.telegraph = 0.0
        self.float_t = 0.0

    def spawn(self, x, ground_y):
        self.x = x
        self.y = ground_y - self.h

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, speed, eggs, biome, ground_y):
        speed_mult = 0.8 if self.boss else (1.25 if self.killer else 1.0)
        self.x -= speed * dt * speed_mult

        if self.boss:
            self.float_t += dt
            self.y = (ground_y - self.h) - 40 * (0.5 + 0.5 * math.sin(self.float_t * 2.2))
        else:
            self.y = ground_y - self.h

        self.timer += dt
        if self.telegraph > 0:
            self.telegraph = max(0.0, self.telegraph - dt)
            if self.telegraph == 0.0:
                if self.boss:
                    for i in range(3):
                        eggs.append(Egg(self.x + 10, self.y + self.h*0.55, lob=(i == 0)))
                elif self.killer:
                    eggs.append(Egg(self.x + 10, self.y + self.h*0.50, lob=True))
                    eggs.append(Egg(self.x + 12, self.y + self.h*0.62, lob=False))
                else:
                    eggs.append(Egg(self.x + 10, self.y + self.h*0.55, lob=(random.random() < biome["lob_chance"])))
                self.timer = 0.0
                base = 0.55 if self.boss else (0.62 if self.killer else random.uniform(0.85, 1.35))
                self.cooldown = base / biome["enemy_rate_mult"]

        if self.telegraph == 0 and self.timer >= self.cooldown and -120 < self.x < 960 + 80:
            self.telegraph = 0.18 if self.boss else (0.20 if self.killer else 0.16)

    def take_damage(self, dmg=1):
        self.hp -= dmg
        return self.hp <= 0

    def draw(self, surf, shake=(0,0), fonts=None):
        sx, sy = shake
        r = self.rect.move(sx, sy)
        flash = (self.telegraph > 0)

        if self.killer:
            base_body = (230, 235, 245)
            outline = (80, 20, 20)
            comb = (200, 40, 50)
            eye_col = (200, 40, 40)
        elif self.boss:
            base_body = (255, 170, 170)
            outline = (160, 40, 40)
            comb = (230, 80, 80)
            eye_col = (30, 30, 30)
        else:
            base_body = (255, 220, 200)
            outline = (140, 90, 60)
            comb = (220, 120, 120)
            eye_col = (20, 20, 20)

        body_col = outline if flash else base_body

        # body (rounded pill)
        pygame.draw.ellipse(surf, body_col, r.inflate(8, 6))
        pygame.draw.ellipse(surf, outline, r.inflate(8, 6), 3)

        # belly highlight
        belly = r.inflate(-10, -8).move(int(r.w*0.08), int(r.h*0.12))
        pygame.draw.ellipse(surf, (255, 245, 240), belly)

        # wing
        wing = pygame.Rect(r.left + int(r.w*0.25), r.top + int(r.h*0.35), int(r.w*0.5), int(r.h*0.35))
        pygame.draw.ellipse(surf, (240, 210, 190), wing)
        pygame.draw.ellipse(surf, outline, wing, 2)

        # head
        head = pygame.Rect(r.left + int(r.w*0.60), r.top + int(r.h*0.08), int(r.w*0.45), int(r.h*0.5))
        pygame.draw.ellipse(surf, body_col, head)
        pygame.draw.ellipse(surf, outline, head, 2)

        # comb
        comb_rect = pygame.Rect(head.left + int(head.w*0.18), head.top - int(head.h*0.18), int(head.w*0.5), int(head.h*0.35))
        pygame.draw.ellipse(surf, comb, comb_rect)

        # beak
        beak = pygame.Rect(head.left - 10, head.centery + 2, 18, 10)
        pygame.draw.rect(surf, (255, 190, 80), beak, border_radius=3)

        # eye
        eye = pygame.Rect(head.left + int(head.w*0.65), head.top + int(head.h*0.30), 8, 8)
        pygame.draw.ellipse(surf, eye_col, eye)

        # tail feathers
        tail = pygame.Rect(r.left - int(r.w*0.25), r.top + int(r.h*0.25), int(r.w*0.35), int(r.h*0.4))
        pygame.draw.ellipse(surf, (235, 205, 185), tail)

        # legs
        leg_y = r.bottom - 6
        for offset in (-10, 6):
            pygame.draw.line(surf, (210, 150, 60), (r.left + r.w//2 + offset, leg_y), (r.left + r.w//2 + offset, leg_y + 12), 4)
            pygame.draw.line(surf, (210, 150, 60), (r.left + r.w//2 + offset, leg_y + 12), (r.left + r.w//2 + offset + 6, leg_y + 12), 4)

        if self.boss and fonts:
            SMALL = fonts["SMALL"]
            bar_w = 140
            x = 960//2 - bar_w//2
            y = 70
            pygame.draw.rect(surf, (25, 25, 25), (x-3, y-3, bar_w+6, 16), border_radius=8)
            frac = max(0.0, min(1.0, self.hp / 20))
            pygame.draw.rect(surf, (200, 60, 60), (x, y, int(bar_w*frac), 10), border_radius=8)
            label = SMALL.render("BOSS", True, (20,20,20))
            surf.blit(label, (x - label.get_width() - 12, y - 2))

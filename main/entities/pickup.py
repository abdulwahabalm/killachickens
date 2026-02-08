import pygame
import random
import math

class Pickup:
    def __init__(self, kind):
        self.kind = kind
        self.r = 14 if kind == "corn" else 16
        self.x = 0.0
        self.y = 0.0

    def spawn(self, x, ground_y):
        self.x = float(x)
        self.y = float(random.choice([ground_y - 90, ground_y - 140, ground_y - 65]))

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r*2, self.r*2)

    def update(self, dt, speed, player):
        if player.magnet > 0:
            dx = (player.x + player.w/2) - self.x
            dy = (player.y + player.base_h/2) - self.y
            dist = max(1.0, math.hypot(dx, dy))
            pull = 900.0 * dt
            self.x += (dx / dist) * pull
            self.y += (dy / dist) * pull
        else:
            self.x -= speed * dt

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        x, y = int(self.x+sx), int(self.y+sy)

        if self.kind == "corn":
            pygame.draw.circle(surf, (255, 220, 60), (x, y), self.r)
            pygame.draw.circle(surf, (220, 180, 40), (x, y), self.r, 2)
        elif self.kind == "shield":
            pygame.draw.circle(surf, (60, 160, 255), (x, y), self.r)
            pygame.draw.circle(surf, (245, 245, 245), (x, y), self.r-6, 2)
        elif self.kind == "rapid":
            pygame.draw.circle(surf, (255, 80, 80), (x, y), self.r)
            pygame.draw.line(surf, (20,20,20), (x-6, y-6), (x+8, y+8), 3)
            pygame.draw.line(surf, (20,20,20), (x-6, y+6), (x+8, y-8), 3)
        elif self.kind == "magnet":
            pygame.draw.circle(surf, (160, 80, 255), (x, y), self.r)
            pygame.draw.rect(surf, (245,245,245), (x-8, y-10, 16, 22), 2, border_radius=4)

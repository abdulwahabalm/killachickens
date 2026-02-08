import pygame
import random

class Bullet:
    def __init__(self, x, y):
        self.w, self.h = 18, 6
        self.x = float(x)
        self.y = float(y)
        self.vx = 980.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt):
        self.x += self.vx * dt

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        pygame.draw.rect(surf, (20, 20, 20), self.rect.move(sx, sy), border_radius=3)

class Egg:
    def __init__(self, x, y, lob=False):
        self.r = 10
        self.x = float(x)
        self.y = float(y)
        self.vx = -740.0
        self.vy = random.uniform(-240, -120) if lob else random.uniform(-60, 40)
        self.counted = False  # for near-miss mission
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r*2, self.r*2)

    def update(self, dt, world_speed):
        g = 1200.0
        self.vy += g * dt
        self.x += (self.vx - 0.22 * world_speed) * dt
        self.y += self.vy * dt

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        pygame.draw.circle(surf, (250, 250, 250), (int(self.x+sx), int(self.y+sy)), self.r)
        pygame.draw.circle(surf, (200, 200, 200), (int(self.x+sx), int(self.y+sy)), self.r, 2)

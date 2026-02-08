import math
import random
import pygame

class Particles:
    def __init__(self):
        self.p = []

    def burst(self, x, y, n=12, speed=260, life=0.45, spread=math.pi):
        for _ in range(n):
            ang = random.uniform(-spread/2, spread/2)
            vx = math.cos(ang) * random.uniform(speed*0.4, speed)
            vy = math.sin(ang) * random.uniform(speed*0.4, speed) - random.uniform(0, speed*0.35)
            self.p.append([float(x), float(y), vx, vy, life, life])

    def update(self, dt):
        g = 1200.0
        alive = []
        for px, py, vx, vy, t, tmax in self.p:
            t -= dt
            if t <= 0:
                continue
            vy += g * dt
            px += vx * dt
            py += vy * dt
            alive.append([px, py, vx * 0.97, vy * 0.97, t, tmax])
        self.p = alive

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        for px, py, vx, vy, t, tmax in self.p:
            a = t / tmax
            r = int(3 + 5*(1-a))
            pygame.draw.circle(surf, (20, 20, 20), (int(px+sx), int(py+sy)), r)

class ScreenShake:
    def __init__(self):
        self.amount = 0.0

    def add(self, a, cap=0.35):
        self.amount = min(cap, self.amount + a)

    def update(self, dt):
        self.amount = max(0.0, self.amount - 1.8 * dt)

    def offset(self):
        s = self.amount
        if s <= 0:
            return (0, 0)
        return (random.randint(-int(12*s*40), int(12*s*40)),
                random.randint(-int(8*s*40), int(8*s*40)))

import pygame
import random

class Obstacle:
    def __init__(self, color):
        # Treat obstacles as rolling eggs
        self.w = random.randint(46, 82)
        self.h = int(self.w * 1.28)
        self.x = 0.0
        self.y = 0.0
        self.color = color
        self.cracked = False
        self.crack_timer = 0.0
        self.harmless = False

    def spawn(self, x, ground_y):
        self.x = x
        self.y = ground_y - self.h

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, speed):
        if self.cracked:
            self.crack_timer = max(0.0, self.crack_timer - dt)
            slow = 0.55
            self.x -= speed * dt * slow
        else:
            self.x -= speed * dt

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        r = self.rect.move(sx, sy)

        base_col = (252, 244, 228)
        shadow = (220, 200, 180)
        outline = (120, 90, 70)

        if self.cracked:
            # Splat of egg white + yolk on ground
            white = pygame.Rect(r.left - 6, r.bottom - int(r.h * 0.35), r.w + 12, int(r.h * 0.6))
            yolk = white.inflate(-int(white.w * 0.55), -int(white.h * 0.55))
            yolk.move_ip(int(white.w * 0.12), -int(white.h * 0.05))

            pygame.draw.ellipse(surf, (245, 245, 240), white)
            pygame.draw.ellipse(surf, (210, 210, 205), white, 2)
            pygame.draw.ellipse(surf, (255, 210, 70), yolk)
            pygame.draw.ellipse(surf, (220, 150, 40), yolk, 2)
        else:
            pygame.draw.ellipse(surf, base_col, r)
            pygame.draw.ellipse(surf, shadow, r.inflate(-12, -8))
            pygame.draw.ellipse(surf, outline, r, 2)

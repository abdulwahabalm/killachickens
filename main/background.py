import random
import pygame
from settings import W, H, GROUND_Y

class Parallax:
    def __init__(self):
        self.clouds = []
        for _ in range(7):
            self.clouds.append([random.uniform(0, W), random.uniform(40, 180), random.uniform(22, 50)])
        self.hill_offset = 0.0
        self.streaks = [random.uniform(0, W) for _ in range(22)]

    def update(self, dt, speed):
        for c in self.clouds:
            c[0] -= (0.10 * speed + 25) * dt
            if c[0] < -120:
                c[0] = W + random.uniform(50, 220)
                c[1] = random.uniform(40, 180)
                c[2] = random.uniform(22, 50)

        self.hill_offset -= 0.22 * speed * dt
        if self.hill_offset < -W:
            self.hill_offset += W

        for i in range(len(self.streaks)):
            self.streaks[i] -= 1.2 * speed * dt
            if self.streaks[i] < 0:
                self.streaks[i] = W + random.uniform(0, 60)

    def draw(self, surf, biome):
        surf.fill((245, 245, 245))
        pygame.draw.rect(surf, biome["sky"], (0, 0, W, int(H*0.55)))

        cloud_col = (255, 255, 255) if biome["name"] != "NIGHT" else (160, 165, 180)
        for x, y, s in self.clouds:
            pygame.draw.circle(surf, cloud_col, (int(x), int(y)), int(s))
            pygame.draw.circle(surf, cloud_col, (int(x + s*0.9), int(y + 4)), int(s*0.8))
            pygame.draw.circle(surf, cloud_col, (int(x - s*0.8), int(y + 8)), int(s*0.7))

        for k in range(2):
            base = int(H*0.60)
            off = self.hill_offset + k*W
            pygame.draw.ellipse(surf, biome["hill1"], (off-80, base-40, W+180, 240))
            pygame.draw.ellipse(surf, biome["hill2"], (off-160, base-10, W+240, 260))

        pygame.draw.rect(surf, biome["ground"], (0, GROUND_Y, W, H - GROUND_Y))
        pygame.draw.line(surf, biome["line"], (0, GROUND_Y), (W, GROUND_Y), 4)

        for x in self.streaks:
            pygame.draw.line(surf, biome["line"], (int(x), GROUND_Y + 20), (int(x+30), GROUND_Y + 20), 2)

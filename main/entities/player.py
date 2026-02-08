import pygame
from settings import GROUND_Y
from utils import clamp  # we'll add utils.py below
from .projectiles import Bullet

class Player:
    def __init__(self, sounds=None):
        self.w, self.h = 64, 64
        self.base_h = self.h
        self.x = 150
        self.y = GROUND_Y - self.h
        self.sounds = sounds

        self.vy = 0.0
        self.gravity = 2650.0
        self.jump_v = 940.0
        self.on_ground = True

        self.jump_buffer = 0.0
        self.coyote = 0.0
        self.JUMP_BUFFER_MAX = 0.12
        self.COYOTE_MAX = 0.10

        self.sliding = False
        self.slide_timer = 0.0
        self.SLIDE_MAX = 0.40

        self.overheat = 0.0
        self.OVERHEAT_MAX = 1.0
        self.heat_per_shot = 0.17
        self.cool_rate = 0.55
        self.rapid_timer = 0.0

        self.shield = 0.0
        self.magnet = 0.0
        self.iframes = 0.0

    @property
    def rect(self):
        if self.sliding:
            return pygame.Rect(int(self.x), int(self.y + self.base_h*0.35), self.w + 6, int(self.base_h*0.65))
        return pygame.Rect(int(self.x), int(self.y), self.w, self.base_h)

    def request_jump(self):
        self.jump_buffer = self.JUMP_BUFFER_MAX
        if self.sounds:
            self.sounds.play("jump", volume=0.55)

    def start_slide(self):
        if self.on_ground and not self.sliding:
            self.sliding = True
            self.slide_timer = self.SLIDE_MAX
            if self.sounds:
                self.sounds.play("slide", volume=0.6)

    def stop_slide(self):
        self.sliding = False
        self.slide_timer = 0.0

    def can_shoot(self):
        return self.overheat < self.OVERHEAT_MAX - 0.01

    def shoot(self, bullets):
        if not self.can_shoot():
            return
        heat = self.heat_per_shot * (0.65 if self.rapid_timer > 0 else 1.0)
        self.overheat = clamp(self.overheat + heat, 0.0, self.OVERHEAT_MAX)
        bullets.append(Bullet(self.x + self.w - 6, self.y + 30))
        if self.sounds:
            self.sounds.play("shoot", volume=0.6)

    def take_hit(self):
        if self.iframes > 0:
            return False
        if self.shield > 0:
            self.shield = 0.0
            self.iframes = 0.9
            return False
        return True

    def update(self, dt):
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self.coyote = max(0.0, self.coyote - dt)
        self.iframes = max(0.0, self.iframes - dt)

        if self.rapid_timer > 0:
            self.rapid_timer = max(0.0, self.rapid_timer - dt)
        if self.magnet > 0:
            self.magnet = max(0.0, self.magnet - dt)
        if self.shield > 0:
            self.shield = max(0.0, self.shield - dt)

        self.overheat = clamp(self.overheat - self.cool_rate * dt, 0.0, self.OVERHEAT_MAX)

        if self.sliding:
            self.slide_timer -= dt
            if self.slide_timer <= 0:
                self.stop_slide()

        self.vy += self.gravity * dt
        self.y += self.vy * dt

        if self.y >= GROUND_Y - self.base_h:
            self.y = GROUND_Y - self.base_h
            self.vy = 0.0
            if not self.on_ground:
                self.on_ground = True
            self.coyote = self.COYOTE_MAX
        else:
            if self.on_ground:
                self.on_ground = False

        if self.jump_buffer > 0 and (self.on_ground or self.coyote > 0):
            self.jump_buffer = 0
            self.vy = -self.jump_v
            self.on_ground = False
            self.coyote = 0

    def draw(self, surf, shake=(0,0)):
        sx, sy = shake
        r = self.rect.move(sx, sy)
        blink = (self.iframes > 0 and int(self.iframes * 18) % 2 == 0)
        if blink:
            return

        base_col = (255, 250, 240)
        outline = (80, 70, 60)
        wing_col = (245, 235, 225)
        comb_col = (210, 70, 70)
        eye_col = (35, 35, 35)
        beak_col = (250, 185, 70)

        lean = clamp(-self.vy / 1200.0, -0.12, 0.18)
        if self.sliding:
            lean = -0.20

        body = r.inflate(10, 6).move(-4, 0)
        if self.sliding:
            body = body.inflate(6, -10).move(2, 8)

        # tail
        tail = pygame.Rect(body.left - int(body.w * 0.35), body.top + int(body.h * 0.35), int(body.w * 0.35), int(body.h * 0.35))
        pygame.draw.ellipse(surf, (235, 220, 205), tail)

        # body
        pygame.draw.ellipse(surf, base_col, body)
        pygame.draw.ellipse(surf, outline, body, 2)

        # wing
        wing = pygame.Rect(body.left + int(body.w * 0.22), body.top + int(body.h * 0.42), int(body.w * 0.42), int(body.h * 0.36))
        pygame.draw.ellipse(surf, wing_col, wing)
        pygame.draw.ellipse(surf, outline, wing, 2)

        # head
        head = pygame.Rect(body.right - int(body.w * 0.55), body.top - int(body.h * 0.05) + int(lean * 10), int(body.w * 0.52), int(body.h * 0.52))
        pygame.draw.ellipse(surf, base_col, head)
        pygame.draw.ellipse(surf, outline, head, 2)

        # comb
        comb = pygame.Rect(head.left + int(head.w * 0.15), head.top - int(head.h * 0.18), int(head.w * 0.38), int(head.h * 0.32))
        pygame.draw.ellipse(surf, comb_col, comb)

        # beak
        beak = pygame.Rect(head.right - 12, head.centery + int(lean * 6), 16, 10)
        pygame.draw.rect(surf, beak_col, beak, border_radius=3)

        # eye
        eye = pygame.Rect(head.left + int(head.w * 0.62), head.top + int(head.h * 0.32), 8, 8)
        pygame.draw.ellipse(surf, eye_col, eye)
        pygame.draw.ellipse(surf, (255, 255, 255), eye.inflate(-4, -4))

        # legs
        leg_y = body.bottom - 2
        for off in (-8, 8):
            pygame.draw.line(surf, (210, 150, 60), (body.centerx + off, leg_y), (body.centerx + off, leg_y + 12), 4)
            pygame.draw.line(surf, (210, 150, 60), (body.centerx + off, leg_y + 12), (body.centerx + off + 6, leg_y + 12), 4)

        if self.shield > 0:
            pygame.draw.circle(surf, (60, 160, 255), r.center, max(r.w, r.h)//2 + 10, 3)

import pygame


class StartMenu:
    def __init__(self, screen_size):
        self.w, self.h = screen_size
        self.title_font = pygame.font.Font(None, 96)
        self.btn_font = pygame.font.Font(None, 44)
        self.small_font = pygame.font.Font(None, 28)

        # Button rect
        self.btn = pygame.Rect(0, 0, 320, 70)
        self.btn.center = (self.w // 2, int(self.h * 0.62))

    def handle_event(self, event):
        # returns True when user wants to start the game
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn.collidepoint(event.pos):
                return True
        return False

    def draw(self, surf):
        surf.fill((18, 18, 24))

        # Title
        title = self.title_font.render("Killa Chickens", True, (255, 235, 120))
        surf.blit(title, title.get_rect(center=(self.w//2, int(self.h*0.25))))

        # Subtitle
        sub = self.small_font.render("Press ENTER / SPACE or click Start", True, (220, 220, 220))
        surf.blit(sub, sub.get_rect(center=(self.w//2, int(self.h*0.35))))

        # Button
        pygame.draw.rect(surf, (255, 235, 120), self.btn, border_radius=16)
        pygame.draw.rect(surf, (30, 30, 30), self.btn, 3, border_radius=16)

        txt = self.btn_font.render("START", True, (20, 20, 20))
        surf.blit(txt, txt.get_rect(center=self.btn.center))

        # Controls
        c1 = self.small_font.render("Jump: W / ↑  |  Slide: S / ↓  |  Shoot: Space", True, (200, 200, 200))
        surf.blit(c1, c1.get_rect(center=(self.w//2, int(self.h*0.80))))

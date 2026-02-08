import pygame

W, H = 960, 540
GROUND_Y = int(H * 0.78)

FPS = 60
TITLE = "Killa Chicken — Ultra Run"

SAVE_PATH = "save.json"
HIGH_PATH = "highscore.txt"


def _pick_font(names, size, bold=False):
    """Try a list of font names and fall back gracefully to default."""
    if isinstance(names, str):
        names = [names]
    return pygame.font.SysFont(names, size, bold=bold)


def get_fonts():
    pygame.font.init()
    headline = ["bahnschrift", "futura", "gill sans", "arial"]
    body = ["segoe ui", "gill sans", "arial"]
    return {
        "FONT": _pick_font(headline, 40, bold=True),
        "SMALL": _pick_font(body, 24, bold=False),
        "TINY": _pick_font(body, 18, bold=False),
    }
5

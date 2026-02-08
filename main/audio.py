import os
import pygame
from utils import asset_path

# Expected file names (drop royalty-free audio in assets/audio/ to enable)
SOUND_FILES = {
    "jump": "assets/audio/jump.wav",
    "slide": "assets/audio/slide.wav",
    "shoot": "assets/audio/shoot.wav",
    "pickup": "assets/audio/pickup.wav",
    "hit": "assets/audio/hit.wav",
    "crack": "assets/audio/crack.wav",
    "mission": "assets/audio/mission.wav",
}

MUSIC_FILES = {
    "music": "assets/audio/music.ogg",
}


class SoundBank:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.music_channel = None
        self.sfx_volume = 0.8
        self.music_volume = 0.6

        try:
            pygame.mixer.init()
            self.enabled = True
        except Exception:
            self.enabled = False

        if not self.enabled:
            return

        for name, path in SOUND_FILES.items():
            full = asset_path(path)
            if os.path.exists(full):
                try:
                    s = pygame.mixer.Sound(full)
                    s.set_volume(0.8)
                    self.sounds[name] = s
                except Exception:
                    continue

    def play(self, name, volume=None):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if not s:
            return
        vol = self.sfx_volume if volume is None else volume
        old = s.get_volume()
        s.set_volume(vol)
        s.play()
        s.set_volume(old)

    def play_music(self, name="music", loops=-1, volume=0.6):
        if not self.enabled:
            return
        path = MUSIC_FILES.get(name)
        if not path:
            return
        full = asset_path(path)
        if not os.path.exists(full):
            return
        try:
            pygame.mixer.music.load(full)
            pygame.mixer.music.set_volume(self.music_volume if volume is None else volume)
            pygame.mixer.music.play(loops)
        except Exception:
            pass

    def stop_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_sfx_volume(self, v):
        self.sfx_volume = max(0.0, min(1.0, v))

    def set_music_volume(self, v):
        self.music_volume = max(0.0, min(1.0, v))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass


def load_sound_bank():
    sb = SoundBank()
    if sb.enabled:
        return sb
    return None

import pygame
import random
from settings import W, H, GROUND_Y
from save_system import load_save, load_highscore, save_highscore
from missions import load_or_create_daily, update_progress, all_done
from biomes import BIOMES, BIOME_DURATION, pick_weighted
from background import Parallax
from effects import Particles, ScreenShake
from entities import Player, EnemyChicken, Obstacle, Pickup
from audio import load_sound_bank
from utils import asset_path
import os

class Game:
    def __init__(self, fonts):
        self.fonts = fonts
        self.start_img = pygame.image.load(asset_path("assets/ui/start.png")).convert_alpha()
        self.start_img = pygame.transform.smoothscale(self.start_img, (W, H))
        self.gameover_img = self._load_ui_image("assets/ui/game_over.png")
        self.blink_t = 0.0
        self.show_press = True
        self.sounds = load_sound_bank()
        self.reset()

    def reset(self):
        self.save_data = load_save()
        self.daily = load_or_create_daily(self.save_data)

        self.bg = Parallax()
        self.particles = Particles()
        self.shake = ScreenShake()

        self.player = Player(sounds=self.sounds)
        self.obstacles = []
        self.enemies = []
        self.eggs = []
        self.bullets = []
        self.pickups = []

        self.alive = True
        self.paused = False
        self.dying = False
        self.dying_timer = 0.0

        self.time = 0.0
        self.speed = 420.0

        self.spawn_timer = 0.0
        self.spawn_delay = 1.15

        self.pickup_timer = 0.0
        self.pickup_delay = 1.75

        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.kills = 0
        self.menu_mode = "home"
        self.menu_slider_drag = None  # ("music"|"sfx", grab_offset)

        self.boss_timer = 0.0
        self.boss_active = False

        self.highscore = load_highscore()

        self.biome_idx = 0
        self.biome_timer = 0.0

        self.corn_collected = 0
        self.eggs_dodged = 0
        self.max_combo = 0

        self.blink_t = 0.0
        self.show_press = True

        self.gameover_fade = 0.0  # 0 -> 1
        self.gameover_show_panel = False

        if self.sounds:
            self.sounds.play_music("music")

    def get_image_menu_buttons(self):
        # Hitboxes tuned for your start.png when scaled to 960x540
        # (x, y, w, h)
        return {
            "start": pygame.Rect(375, 282, 208, 37),
            "missions": pygame.Rect(373, 322, 211, 37),
            "settings": pygame.Rect(373, 363, 211, 37),
        }

    def get_gameover_buttons(self):
        # Match the panel geometry used in draw_gameover_overlay
        panel_w = int(W * 0.46)
        panel_h = int(H * 0.34)
        panel_y = int(H * 0.54)
        panel = pygame.Rect(W // 2 - panel_w // 2, panel_y, panel_w, panel_h)

        margin = int(panel_w * 0.08)
        bw = panel_w - margin * 2
        bh = int(panel_h * 0.24)
        gap = int(panel_h * 0.10)

        x = panel.x + margin
        y0 = panel.y + int(panel_h * 0.42)  # push below title area

        return {
            "restart": pygame.Rect(x, y0, bw, bh),
            "menu": pygame.Rect(x, y0 + (bh + gap), bw, bh),
        }

    def get_quit_rect(self):
        w, h = 70, 26
        return pygame.Rect(W - w - 14, 14, w, h)

    def get_pause_buttons(self):
        # Compact buttons centered
        bw = int(W * 0.22)
        bh = int(H * 0.07)
        gap = int(H * 0.025)

        x = W // 2 - bw // 2
        y0 = int(H * 0.52)

        return {
            "resume": pygame.Rect(x, y0, bw, bh),
            "menu": pygame.Rect(x, y0 + (bh + gap), bw, bh),
        }

    def update_overlays(self, dt):
        # Called every frame (even when paused/gameover) to animate fades.
        if not self.alive:
            # fade in over 0.6s
            self.gameover_fade = min(1.0, self.gameover_fade + dt / 0.6)

            # show buttons slightly after fade starts (feels smoother)
            if self.gameover_fade >= 0.35:
                self.gameover_show_panel = True
    def draw_gameover_overlay(self, surf):
        # Light dim instead of heavy blackout
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 90))
        surf.blit(dim, (0, 0))

        # Floating panel (tall enough to host title + buttons cleanly)
        panel_w = int(W * 0.46)
        panel_h = int(H * 0.34)
        panel_y = int(H * 0.54)
        panel = pygame.Rect(W // 2 - panel_w // 2, panel_y, panel_w, panel_h)

        pygame.draw.rect(surf, (255, 255, 255), panel, border_radius=14)
        pygame.draw.rect(surf, (20, 20, 20), panel, 2, border_radius=14)

        title_font = self.fonts.get("FONT") or pygame.font.SysFont(None, 46)
        small_font = self.fonts.get("SMALL") or pygame.font.SysFont(None, 24)

        title = title_font.render("GAME OVER", True, (20, 20, 20))
        surf.blit(title, (W // 2 - title.get_width() // 2, panel.y + 12))

        # Buttons (hover)
        btns = self.get_gameover_buttons()
        mx, my = pygame.mouse.get_pos()

        for key, rect in btns.items():
            hovered = rect.collidepoint((mx, my))

            pygame.draw.rect(surf, (70, 90, 160), rect, border_radius=10)

            if hovered:
                glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 40))
                surf.blit(glow, rect.topleft)

            pygame.draw.rect(surf, (20, 20, 20), rect, 2, border_radius=10)

            label = "Restart" if key == "restart" else "Menu"
            text = small_font.render(label, True, (255, 255, 255))
            surf.blit(text, (rect.centerx - text.get_width() // 2,
                             rect.centery - text.get_height() // 2))

        self.draw_quit_button(surf)

        self.draw_quit_button(surf)
        # Quit button
        self.draw_quit_button(surf)



    def draw_pause_overlay(self, surf):
        # Light dim so the game is still visible
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 85))
        surf.blit(dim, (0, 0))

        # Small panel
        panel_w = int(W * 0.38)
        panel_h = int(H * 0.28)
        panel = pygame.Rect(W // 2 - panel_w // 2, int(H * 0.22), panel_w, panel_h)

        pygame.draw.rect(surf, (255, 255, 255), panel, border_radius=14)
        pygame.draw.rect(surf, (20, 20, 20), panel, 2, border_radius=14)

        title_font = self.fonts.get("FONT") or pygame.font.SysFont(None, 46)
        small_font = self.fonts.get("SMALL") or pygame.font.SysFont(None, 24)

        title = title_font.render("PAUSED", True, (20, 20, 20))
        surf.blit(title, (W // 2 - title.get_width() // 2, panel.y + 14))

        # Buttons + hover
        btns = self.get_pause_buttons()
        mx, my = pygame.mouse.get_pos()

        for key, rect in btns.items():
            hovered = rect.collidepoint((mx, my))

            pygame.draw.rect(surf, (70, 90, 160), rect, border_radius=10)

            if hovered:
                glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 40))
                surf.blit(glow, rect.topleft)

            pygame.draw.rect(surf, (20, 20, 20), rect, 2, border_radius=10)

            label = "Resume" if key == "resume" else "Menu"
            text = small_font.render(label, True, (255, 255, 255))
            surf.blit(text, (rect.centerx - text.get_width() // 2,
                             rect.centery - text.get_height() // 2))

        hint = small_font.render("P = Resume   ESC/M = Menu", True, (40, 40, 40))
        surf.blit(hint, (W // 2 - hint.get_width() // 2, panel.bottom - 32))

        self.draw_quit_button(surf)

        self.draw_quit_button(surf)
        # Quit button
        self.draw_quit_button(surf)

    def biome(self):
        return BIOMES[self.biome_idx]

    def advance_biome(self):
        self.biome_idx = (self.biome_idx + 1) % len(BIOMES)
        self.biome_timer = 0.0
        self.score += 100
        self.particles.burst(W*0.5, 120, n=18, speed=280, life=0.6)
        self.shake.add(0.10)

    def spawn_logic(self, dt):
        b = self.biome()

        self.biome_timer += dt
        if self.biome_timer >= BIOME_DURATION:
            self.advance_biome()
            b = self.biome()

        t = self.time
        self.speed = 420 + t * 25
        self.spawn_delay = max(0.48, 1.15 - t * 0.022)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0.0
            enemy_chance = min(0.40, 0.14 + 0.012 * min(t, 40))
            killer_unlocked = t > 35.0

            if not self.boss_active and random.random() < enemy_chance:
                spawn_killer = killer_unlocked and random.random() < 0.25
                e = EnemyChicken(boss=False, killer=spawn_killer)
                e.spawn(W + 80, GROUND_Y)
                self.enemies.append(e)
            else:
                o = Obstacle(color=b["obstacle_color"])
                o.spawn(W + 60, GROUND_Y)
                self.obstacles.append(o)

        self.pickup_timer += dt
        self.pickup_delay = max(0.95, 1.75 - t * 0.012)
        if self.pickup_timer >= self.pickup_delay:
            self.pickup_timer = 0.0
            kind = pick_weighted(b["pickup_weights"], random.random())
            pu = Pickup(kind)
            pu.spawn(W + 60, GROUND_Y)
            self.pickups.append(pu)

        self.boss_timer += dt
        if not self.boss_active and self.boss_timer >= 60.0:
            self.boss_timer = 0.0
            self.boss_active = True
            boss = EnemyChicken(boss=True)
            boss.spawn(W + 120, GROUND_Y)
            self.enemies.append(boss)
    def _load_ui_image(self, path):
        # Loads image and scales to screen size (W,H). If missing, returns None.
        try:
            img = pygame.image.load(asset_path(path)).convert_alpha()
            return pygame.transform.smoothscale(img, (W, H))
        except Exception:
            return None

    def draw_start_menu(self, surf):
        b = self.biome()
        self.bg.draw(surf, b)

        if getattr(self, "start_img", None):
            surf.blit(self.start_img, (0, 0))

        btns = self.get_image_menu_buttons()
        mx, my = pygame.mouse.get_pos()

        # Hover highlight (drawn ON TOP of the image)
        for name, rect in btns.items():
            if rect.collidepoint((mx, my)):
                # translucent fill
                overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 40))
                surf.blit(overlay, rect.topleft)

                # outline
                pygame.draw.rect(surf, (255, 255, 255), rect, 2, border_radius=8)

        # Overlay modal for missions/settings
        if self.menu_mode in ("missions", "settings"):
            self.draw_start_overlay(surf)

        # Quit text button (top-right)
        self.draw_quit_button(surf)

        # Blinking instruction text
        blink_on = (pygame.time.get_ticks() // 500) % 2 == 0
        if blink_on:
            msg = "Press ENTER or Click Start"
            font = self.fonts.get("SMALL") or self.fonts.get("FONT") or pygame.font.SysFont(None, 28)

            text = font.render(msg, True, (255, 255, 255))
            shadow = font.render(msg, True, (0, 0, 0))

            x = W // 2 - text.get_width() // 2
            y = int(H * 0.90)

            surf.blit(shadow, (x + 2, y + 2))
            surf.blit(text, (x, y))

    def start_overlay_rects(self):
        panel_w, panel_h = 420, 280
        panel = pygame.Rect(W // 2 - panel_w // 2, H // 2 - panel_h // 2, panel_w, panel_h)
        close = pygame.Rect(panel.right - 34, panel.y + 10, 24, 24)
        return panel, close

    def draw_start_overlay(self, surf):
        SMALL = self.fonts["SMALL"]
        TINY = self.fonts.get("TINY", SMALL)

        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 110))
        surf.blit(dim, (0, 0))

        panel, close = self.start_overlay_rects()
        pygame.draw.rect(surf, (248, 248, 252), panel, border_radius=12)
        pygame.draw.rect(surf, (30, 30, 40), panel, 2, border_radius=12)

        title = "Daily Missions" if self.menu_mode == "missions" else "Settings"
        surf.blit(SMALL.render(title, True, (30, 30, 40)), (panel.x + 14, panel.y + 10))

        # close button
        pygame.draw.rect(surf, (230, 230, 235), close, border_radius=6)
        pygame.draw.rect(surf, (50, 50, 60), close, 2, border_radius=6)
        x1, y1 = close.x + 6, close.y + 6
        x2, y2 = close.right - 6, close.bottom - 6
        pygame.draw.line(surf, (50, 50, 60), (x1, y1), (x2, y2), 2)
        pygame.draw.line(surf, (50, 50, 60), (x1, y2), (x2, y1), 2)

        y = panel.y + 46
        content_w = panel.w - 32
        if self.menu_mode == "missions":
            surf.blit(TINY.render(f"Date: {self.daily['date']}", True, (60, 60, 70)), (panel.x + 16, y))
            y += 22
            bar_w = content_w
            for m in self.daily["missions"]:
                done = m["done"]
                frac = m["progress"] / m["target"] if m["target"] else 0
                frac = max(0.0, min(1.0, frac))

                label = TINY.render(m["text"], True, (30, 30, 40))
                surf.blit(label, (panel.x + 16, y))
                y += label.get_height() + 2

                prog_text = TINY.render(f"{m['progress']} / {m['target']}", True, (60, 60, 70))
                surf.blit(prog_text, (panel.x + 16, y))
                y += prog_text.get_height() + 2

                bar_bg = pygame.Rect(panel.x + 16, y, bar_w, 12)
                pygame.draw.rect(surf, (230, 232, 238), bar_bg, border_radius=6)
                fg_col = (90, 170, 90) if done else (80, 120, 200)
                if frac > 0:
                    fg = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_bg.w * frac), bar_bg.h)
                    pygame.draw.rect(surf, fg_col, fg, border_radius=6)
                pygame.draw.rect(surf, (40, 40, 50), bar_bg, 1, border_radius=6)

                y = bar_bg.bottom + 16

            if all_done(self.daily):
                surf.blit(TINY.render("All done! +250 bonus", True, (30, 110, 70)), (panel.x + 16, panel.bottom - 28))

        else:  # settings
            surf.blit(TINY.render("Audio", True, (30, 30, 40)), (panel.x + 16, y))
            y += 18
            self.draw_slider(surf, panel.x + 16, y, content_w, "Music", "music")
            y += 36
            self.draw_slider(surf, panel.x + 16, y, content_w, "SFX", "sfx")
            y += 42

            surf.blit(TINY.render("Controls", True, (30, 30, 40)), (panel.x + 16, y))
            y += 18
            controls = [
                "SPACE jump | S slide | F shoot | P pause",
                "ESC/M: menu, R: restart on game over",
            ]
            for line in controls:
                surf.blit(TINY.render(line, True, (40, 40, 50)), (panel.x + 16, y))
                y += 18

    def draw_slider(self, surf, x, y, w, label, kind):
        TINY = self.fonts.get("TINY", self.fonts["SMALL"])
        sb = self.sounds
        val = 0.0
        if sb:
            val = sb.music_volume if kind == "music" else sb.sfx_volume
        track = pygame.Rect(x, y + 10, w, 10)
        pygame.draw.rect(surf, (230, 230, 236), track, border_radius=6)
        pygame.draw.rect(surf, (50, 50, 60), track, 1, border_radius=6)
        knob_x = track.x + int(track.w * val)
        knob = pygame.Rect(knob_x - 8, track.y - 6, 16, 22)
        pygame.draw.rect(surf, (90, 140, 220), knob, border_radius=6)
        pygame.draw.rect(surf, (30, 30, 40), knob, 1, border_radius=6)

        surf.blit(TINY.render(f"{label} {int(val*100)}%", True, (40, 40, 50)), (x, y - 4))

    def set_volume_from_click(self, kind, x, track_rect):
        sb = self.sounds
        if not sb or not track_rect:
            return
        frac = (x - track_rect.x) / track_rect.w
        frac = max(0.0, min(1.0, frac))
        if kind == "music":
            sb.set_music_volume(frac)
        else:
            sb.set_sfx_volume(frac)

    def apply_pickup(self, kind):
        p = self.player
        if kind == "corn":
            self.combo += 1
            self.combo_timer = 2.0
            self.score += 10 + 3 * self.combo
            self.corn_collected += 1
            update_progress(self, "corn", 1)
            if self.sounds:
                self.sounds.play("pickup", volume=0.65)

            self.max_combo = max(self.max_combo, self.combo)
            update_progress(self, "combo", self.max_combo, absolute=True)
        elif kind == "shield":
            p.shield = 18.0
            self.score += 30
            if self.sounds:
                self.sounds.play("pickup", volume=0.7)
        elif kind == "rapid":
            p.rapid_timer = 10.0
            self.score += 35
            if self.sounds:
                self.sounds.play("pickup", volume=0.7)
        elif kind == "magnet":
            p.magnet = 10.0
            self.score += 35
            if self.sounds:
                self.sounds.play("pickup", volume=0.7)

    def egg_near_miss(self):
        pr = self.player.rect
        px, py = pr.centerx, pr.centery
        for eg in self.eggs:
            if -30 < (eg.x - px) < 40:
                dist = abs(eg.y - py)
                if 40 < dist < 70 and not eg.counted:
                    eg.counted = True
                    self.eggs_dodged += 1
                    update_progress(self, "dodges", 1)
                    self.score += 2

    def update(self, dt, keys_pressed):
        if not self.alive or self.paused:
            return

        if self.dying:
            self.dying_timer = max(0.0, self.dying_timer - dt)
            # Keep particles/shake alive while frozen
            self.particles.update(dt)
            self.shake.update(dt)
            if self.dying_timer == 0.0:
                self.alive = False
                self.paused = False
                self.gameover_fade = 0.0
                self.gameover_show_panel = False
            return

        self.time += dt
        self.spawn_logic(dt)

        self.bg.update(dt, self.speed)
        self.player.update(dt)

        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        # hold-to-shoot for rapid
        if keys_pressed[pygame.K_f] and self.player.rapid_timer > 0:
            self.player.shoot(self.bullets)

        for o in self.obstacles:
            o.update(dt, self.speed)
        self.obstacles = [o for o in self.obstacles if o.x + o.w > -80]

        for e in self.enemies:
            e.update(dt, self.speed, self.eggs, self.biome(), GROUND_Y)
        self.enemies = [e for e in self.enemies if e.x + e.w > -200]
        self.boss_active = any(e.boss for e in self.enemies)

        for eg in self.eggs:
            eg.update(dt, self.speed)
        self.eggs = [eg for eg in self.eggs if eg.alive and eg.x > -120 and eg.y < H + 120]

        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.x < W + 80]

        for pu in self.pickups:
            pu.update(dt, self.speed, self.player)
        self.pickups = [pu for pu in self.pickups if pu.x > -120 and -120 < pu.y < H + 120]

        self.particles.update(dt)
        self.shake.update(dt)

        # score + survive mission
        self.score = max(self.score, int(self.time * 12))
        update_progress(self, "survive", int(self.time), absolute=True)

        self.egg_near_miss()

        self.handle_collisions()

        # daily completion bonus
        if all_done(self.daily) and not self.daily.get("bonus_claimed", False):
            self.daily["bonus_claimed"] = True
            self.score += 250
            self.save_data["daily"] = self.daily
            if self.sounds:
                self.sounds.play("mission", volume=0.8)

        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def handle_collisions(self):
        pr = self.player.rect

        # pickups
        keep = []
        for pu in self.pickups:
            if pr.colliderect(pu.rect):
                self.apply_pickup(pu.kind)
                self.particles.burst(pu.x, pu.y, n=10, speed=220, life=0.35)
            else:
                keep.append(pu)
        self.pickups = keep

        # bullets vs enemies
        new_enemies = []
        for e in self.enemies:
            hit = False
            for b in list(self.bullets):
                if b.rect.colliderect(e.rect):
                    hit = True
                    self.bullets.remove(b)
                    dead = e.take_damage(1)
                    self.particles.burst(e.x + e.w*0.5, e.y + e.h*0.5, n=14 if not e.boss else 18, speed=320, life=0.5)
                    self.shake.add(0.06 if not e.boss else 0.09)
                    self.score += 35 if not e.boss else 12
                    if dead:
                        self.kills += 1
                        update_progress(self, "kills", 1)
                        self.score += 85 if not e.boss else 500
                        self.shake.add(0.16 if e.boss else 0.10)
                        if self.sounds:
                            self.sounds.play("hit", volume=0.65)
                    else:
                        new_enemies.append(e)
                    break
            if not hit:
                new_enemies.append(e)
        self.enemies = new_enemies

        # bullets vs obstacles (egg rocks)
        new_obstacles = []
        for o in self.obstacles:
            hit = False
            for b in list(self.bullets):
                if b.rect.colliderect(o.rect):
                    self.bullets.remove(b)
                    hit = True
                    o.cracked = True  # show yolk/white splat
                    o.crack_timer = 0.4
                    o.harmless = True  # no longer hurts player
                    self.particles.burst(o.x + o.w * 0.5, o.y + o.h * 0.5, n=12, speed=280, life=0.4)
                    if self.sounds:
                        self.sounds.play("crack", volume=0.7)
                    self.score += 8
                    break
            # keep cracked eggs on screen; only discard when offscreen in update loop
            new_obstacles.append(o)
        self.obstacles = new_obstacles

        # bullets vs eggs (clear hazards)
        keep_eggs = []
        for eg in self.eggs:
            hit = False
            for b in list(self.bullets):
                if b.rect.colliderect(eg.rect):
                    self.bullets.remove(b)
                    hit = True
                    self.particles.burst(eg.x, eg.y, n=10, speed=280, life=0.35)
                    if self.sounds:
                        self.sounds.play("crack", volume=0.7)
                    self.score += 6
                    eg.alive = False
                    break
            if not hit:
                keep_eggs.append(eg)
        self.eggs = keep_eggs

        # fatal collisions
        for o in self.obstacles:
            if pr.colliderect(o.rect) and not self.dying and not o.harmless:
                o.cracked = True
                o.crack_timer = 0.6
                o.harmless = True
                self.particles.burst(pr.centerx, pr.centery, n=18, speed=360, life=0.6)
                if self.sounds:
                    self.sounds.play("hit", volume=0.75)
                if self.player.take_hit():
                    self.dying = True
                    self.dying_timer = 0.5
                return

        for e in self.enemies:
            if pr.colliderect(e.rect) and not self.dying:
                self.particles.burst(pr.centerx, pr.centery, n=18, speed=360, life=0.6)
                if self.sounds:
                    self.sounds.play("hit", volume=0.75)
                if self.player.take_hit():
                    self.dying = True
                    self.dying_timer = 0.5
                return

        for eg in self.eggs:
            if pr.colliderect(eg.rect) and not self.dying:
                self.shake.add(0.16)
                self.particles.burst(eg.x, eg.y, n=14, speed=300, life=0.5)
                if self.sounds:
                    self.sounds.play("hit", volume=0.75)
                if self.player.take_hit():
                    self.dying = True
                    self.dying_timer = 0.5
                return

    def draw(self, surf):
        b = self.biome()
        self.bg.draw(surf, b)
        shake = self.shake.offset()

        self.player.draw(surf, shake)
        for o in self.obstacles:
            o.draw(surf, shake)
        for e in self.enemies:
            e.draw(surf, shake, fonts=self.fonts)
        for eg in self.eggs:
            eg.draw(surf, shake)
        for bl in self.bullets:
            bl.draw(surf, shake)
        for pu in self.pickups:
            pu.draw(surf, shake)
        self.particles.draw(surf, shake)

        self.draw_ui(surf)

    def update_blink(self, dt):
        # Toggle every 0.5s
        self.blink_t += dt
        if self.blink_t >= 0.5:
            self.blink_t = 0.0
            self.show_press = not self.show_press

    def draw_ui(self, surf):
        # --- GAME OVER takes priority over pause ---
        if not self.alive:
            # 1) Fade in the gameover background image (if you have one)
            if getattr(self, "gameover_img", None):
                img = self.gameover_img.copy()
                img.set_alpha(int(255 * self.gameover_fade))
                surf.blit(img, (0, 0))

            # 2) Fade in the dim layer (tied to the same fade)
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, int(140 * self.gameover_fade)))  # max 140 alpha
            surf.blit(dim, (0, 0))

            # 3) Show the panel/buttons after a short delay
            if self.gameover_show_panel:
                self.draw_gameover_overlay(surf)

            return

        # --- PAUSE overlay (only if alive) ---
        if self.paused:
            self.draw_pause_overlay(surf)
            return

        # --- NORMAL UI ---
        FONT = self.fonts["FONT"]
        SMALL = self.fonts["SMALL"]
        TINY = self.fonts.get("TINY", SMALL)

        # HUD card for core stats
        card = pygame.Rect(14, 10, 230, 130)
        pygame.draw.rect(surf, (250, 250, 250), card, border_radius=14)
        pygame.draw.rect(surf, (30, 30, 40), card, 2, border_radius=14)
        surf.blit(FONT.render(f"{self.score:05}", True, (30, 30, 40)), (card.x + 12, card.y + 10))
        surf.blit(SMALL.render(f"High {self.highscore}", True, (70, 70, 80)), (card.x + 14, card.y + 50))
        surf.blit(SMALL.render(f"Kills {self.kills}   Combo {self.combo}", True, (70, 70, 80)), (card.x + 14, card.y + 74))

        remaining = max(0, int(BIOME_DURATION - self.biome_timer))
        b = self.biome()
        surf.blit(SMALL.render(f"{b['name']} biome · {remaining}s", True, (70, 70, 80)), (card.x + 14, card.y + 98))

        # Missions panel
        mx, my = W - 360, 95
        missions = self.daily["missions"]
        label_h = SMALL.get_height()
        bar_h = 12
        per_row = label_h + bar_h + 18  # padding below each bar
        panel_h = 40 + len(missions) * per_row + 26

        panel = pygame.Rect(mx, my, 340, panel_h)
        pygame.draw.rect(surf, (250, 250, 255), panel, border_radius=14)
        pygame.draw.rect(surf, (40, 40, 50), panel, 2, border_radius=14)
        surf.blit(SMALL.render(f"Daily Missions · {self.daily['date']}", True, (30, 30, 40)), (mx + 12, my + 10))

        yy = my + 36
        bar_w = panel.w - 24
        for m in missions:
            done = m["done"]
            frac = m["progress"] / m["target"] if m["target"] else 0
            frac = max(0.0, min(1.0, frac))

            label = SMALL.render(m["text"], True, (25, 25, 30))
            surf.blit(label, (mx + 12, yy))

            bar_y = yy + label_h + 4
            bar_bg = pygame.Rect(mx + 12, bar_y, bar_w, bar_h)
            pygame.draw.rect(surf, (230, 232, 238), bar_bg, border_radius=6)
            fg_col = (90, 170, 90) if done else (80, 120, 200)
            if frac > 0:
                fg = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_bg.w * frac), bar_bg.h)
                pygame.draw.rect(surf, fg_col, fg, border_radius=6)
            pygame.draw.rect(surf, (40, 40, 50), bar_bg, 1, border_radius=6)

            prog_text = TINY.render(f"{m['progress']} / {m['target']}", True, (60, 60, 70))
            surf.blit(prog_text, (bar_bg.right - prog_text.get_width(), bar_bg.y - 2))

            if done:
                check = TINY.render("DONE", True, (40, 120, 50))
                surf.blit(check, (bar_bg.x, bar_bg.y - 2))

            yy = bar_y + bar_h + 14

        if all_done(self.daily):
            surf.blit(SMALL.render("All done! +250 bonus", True, (30, 110, 70)), (mx + 12, panel.bottom - 22))

        # Heat card (top-right)
        heat_w, heat_h = 200, 64
        heat_rect = pygame.Rect(W - heat_w - 16, 16, heat_w, heat_h)
        pygame.draw.rect(surf, (250, 245, 245), heat_rect, border_radius=12)
        pygame.draw.rect(surf, (40, 30, 30), heat_rect, 2, border_radius=12)

        label = SMALL.render("Weapon Heat", True, (40, 30, 30))
        surf.blit(label, (heat_rect.x + 12, heat_rect.y + 8))

        self._bar(
            surf,
            heat_rect.x + 12, heat_rect.y + 32,
            heat_rect.w - 24, 12,
            self.player.overheat / self.player.OVERHEAT_MAX,
            fg=(240, 90, 70),
        )

        # Bottom hint
        hint = "SPACE jump | S slide | F shoot | P pause"
        surf.blit(SMALL.render(hint, True, (20, 20, 20)),
                  (W // 2 - SMALL.size(hint)[0] // 2, H - 28))

    def _bar(self, surf, x, y, w, h, frac, bg=(20, 20, 20), fg=(60, 160, 255)):
        pygame.draw.rect(surf, bg, (x - 2, y - 2, w + 4, h + 4), border_radius=8)
        pygame.draw.rect(surf, (245, 245, 245), (x, y, w, h), border_radius=8)
        pygame.draw.rect(surf, fg, (x, y, int(w * max(0.0, min(1.0, frac))), h), border_radius=8)

    def draw_quit_button(self, surf):
        quit_rect = self.get_quit_rect()
        quit_bg = pygame.Surface((quit_rect.w, quit_rect.h), pygame.SRCALPHA)
        hover = quit_rect.collidepoint(pygame.mouse.get_pos())
        quit_bg.fill((10, 10, 14, 200 if hover else 160))
        surf.blit(quit_bg, quit_rect.topleft)

        label = self.fonts.get("TINY", self.fonts["SMALL"]).render("Quit", True, (245, 245, 245))
        surf.blit(label, (quit_rect.centerx - label.get_width() // 2, quit_rect.centery - label.get_height() // 2))

        pygame.draw.rect(surf, (255, 255, 255), quit_rect, 1, border_radius=6)

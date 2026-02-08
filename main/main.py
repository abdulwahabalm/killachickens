import pygame
import sys
from settings import W, H, FPS, TITLE, get_fonts
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    fonts = get_fonts()
    game = Game(fonts)

    state = "start"  # start -> play -> gameover

    while True:
        dt = clock.tick(FPS) / 1000.0
        game.update_overlays(dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Global: go to menu anytime (play or gameover)
                if event.key in (pygame.K_ESCAPE, pygame.K_m):
                    if state == "start" or state == "gameover" or (state == "play" and game.paused):
                        state = "start"
                        game.menu_mode = "home"
                        game.paused = False
                        continue

                # -------- START SCREEN --------
                if state == "start":
                    if game.menu_mode in ("missions", "settings") and event.key in (pygame.K_ESCAPE, pygame.K_m):
                        game.menu_mode = "home"
                        continue
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.reset()
                        game.menu_mode = "home"
                        state = "play"

                # -------- PLAYING --------
                elif state == "play":
                    if event.key == pygame.K_p:
                        game.paused = not game.paused

                    if game.paused and event.key in (pygame.K_ESCAPE, pygame.K_m):
                        state = "start"
                        game.paused = False
                        continue

                    if game.alive and not game.paused:
                        if event.key == pygame.K_SPACE:
                            game.player.request_jump()
                        if event.key == pygame.K_s:
                            game.player.start_slide()
                        if event.key == pygame.K_f:
                            game.player.shoot(game.bullets)

                # -------- GAME OVER --------
                elif state == "gameover":
                    if event.key == pygame.K_r:
                        game.reset()
                        state = "play"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "start":
                    # Quit button (works even with overlay)
                    if game.get_quit_rect().collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    # If overlay open, handle close first
                    if game.menu_mode in ("missions", "settings"):
                        panel, close = game.start_overlay_rects()
                        if close.collidepoint(event.pos) or not panel.collidepoint(event.pos):
                            game.menu_mode = "home"
                            game.menu_slider_drag = None
                        else:
                            # slider hit testing
                            track_w = panel.w - 32
                            music_track = pygame.Rect(panel.x + 16, panel.y + 46 + 10, track_w, 10)
                            sfx_track = pygame.Rect(panel.x + 16, panel.y + 46 + 36 + 10, track_w, 10)
                            if game.menu_mode == "settings":
                                if music_track.inflate(0, 20).collidepoint(event.pos):
                                    game.menu_slider_drag = ("music", event.pos[0] - music_track.x)
                                    game.set_volume_from_click("music", event.pos[0], music_track)
                                elif sfx_track.inflate(0, 20).collidepoint(event.pos):
                                    game.menu_slider_drag = ("sfx", event.pos[0] - sfx_track.x)
                                    game.set_volume_from_click("sfx", event.pos[0], sfx_track)
                        continue

                    btns = game.get_image_menu_buttons()
                    if btns["start"].collidepoint(event.pos):
                        game.reset()
                        game.menu_mode = "home"
                        state = "play"
                    elif btns["missions"].collidepoint(event.pos):
                        game.menu_mode = "missions"
                    elif btns["settings"].collidepoint(event.pos):
                        game.menu_mode = "settings"
                if state == "gameover":
                    if game.get_quit_rect().collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    btns = game.get_gameover_buttons()
                    if btns["restart"].collidepoint(event.pos):
                        game.reset()
                        state = "play"
                    elif btns["menu"].collidepoint(event.pos):
                        state = "start"
                        game.menu_mode = "home"
                        game.paused = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "play" and game.paused:
                    if game.get_quit_rect().collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    btns = game.get_pause_buttons()
                    if btns["resume"].collidepoint(event.pos):
                        game.paused = False
                    elif btns["menu"].collidepoint(event.pos):
                        state = "start"
                        game.paused = False


            if event.type == pygame.KEYUP:
                if state == "play" and event.key == pygame.K_s:
                    game.player.stop_slide()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if state == "start" and game.menu_slider_drag:
                    game.menu_slider_drag = None

            if event.type == pygame.MOUSEMOTION:
                if state == "start" and game.menu_slider_drag and event.buttons[0]:
                    kind, grab = game.menu_slider_drag
                    panel, _ = game.start_overlay_rects()
                    track_w = panel.w - 32
                    y_offset = 46 + (10 if kind == "music" else 36 + 10)
                    track = pygame.Rect(panel.x + 16, panel.y + y_offset, track_w, 10)
                    game.set_volume_from_click(kind, event.pos[0], track)


        keys = pygame.key.get_pressed()


        # --- Update game only while playing ---
        if state == "play":
            game.update(dt, keys)
            if not game.alive:
                state = "gameover"

        # --- Draw ---
        if state == "start":
            game.draw_start_menu(screen)
        else:
            game.draw(screen)  # draw world + UI (gameover image handled in draw_ui)

        if state == "start":
            hover_any = any(r.collidepoint(pygame.mouse.get_pos()) for r in game.get_image_menu_buttons().values())
            if game.get_quit_rect().collidepoint(pygame.mouse.get_pos()):
                hover_any = True
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()


if __name__ == "__main__":
    main()

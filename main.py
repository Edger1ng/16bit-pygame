import pygame
import sys
import random
import time
from settings import WIDTH, HEIGHT, FPS, BG_COLOR, TILE_SIZE, MAP_COLS, MAP_ROWS
from player import Player
from enemy import Enemy
from tilemap import TileMap

def reset_game(level=1):
    tilemap = TileMap()
    player_size = pygame.Vector2(20, 25)
    enemy_size = pygame.Vector2(20, 35)

    def center_pos_in_tile(tx, ty, size):
        return (tx * TILE_SIZE + (TILE_SIZE - size.x) / 2,
                ty * TILE_SIZE + (TILE_SIZE - size.y) / 2)

    player_start = center_pos_in_tile(1, 1, player_size)
    free_tiles = [t for t in tilemap.get_free_tiles() if t != (1, 1)]
    enemy_tile = random.choice(free_tiles)
    enemy_pos = center_pos_in_tile(enemy_tile[0], enemy_tile[1], enemy_size)

    player = Player(player_start, tilemap)

    enemy_speed = min(2.0 + level * 0.2, 5.0)
    enemy_chase_speed = min(3.0 + level * 0.3, 7.0)
    enemy_detect_radius = min(100 + level * 20, 300)
    enemy_lose_radius = enemy_detect_radius + 50

    enemy = Enemy(enemy_pos, tilemap, speed=enemy_speed, chase_speed=enemy_chase_speed,
                  detect_radius=enemy_detect_radius, lose_radius=enemy_lose_radius)

    goal_rect = pygame.Rect((MAP_COLS - 2) * TILE_SIZE + 5, (MAP_ROWS - 2) * TILE_SIZE + 5,
                            TILE_SIZE - 10, TILE_SIZE - 10)

    return tilemap, player, enemy, goal_rect

def get_vision_radius(level):
    steps = [float('inf'), 8, 6, 4, 2]
    index = level // 5
    return steps[min(index, len(steps)-1)]

def draw_console(screen, font, history, input_text):
    overlay = pygame.Surface((WIDTH, HEIGHT // 3))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)

    for i, line in enumerate(reversed(history[-8:])):
        text = font.render(line, True, (0, 255, 0))
        overlay.blit(text, (10, 5 + i * 24))

    input_render = font.render("> " + input_text, True, (255, 255, 255))
    overlay.blit(input_render, (10, HEIGHT // 3 - 28))
    screen.blit(overlay, (0, HEIGHT - HEIGHT // 3))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 24)

    level = 1
    tilemap, player, enemy, goal_rect = reset_game(level)
    collected_goal = False
    victory_display_time = 0

    last_super_time = time.time()
    enemy_disabled_until = 0
    slow_until = 0
    player_in_trap = 0
    last_remove_trap_time = 0

    console_active = False
    console_history = []
    console_input = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if console_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        console_history.append("> " + console_input)
                        cmd = console_input.strip().lower()

                        if cmd.startswith("level "):
                            try:
                                level = int(cmd.split()[1])
                                tilemap, player, enemy, goal_rect = reset_game(level)
                                console_history.append(f"Level set to {level}")
                            except:
                                console_history.append("Invalid level")
                        elif cmd == "next":
                            level += 1
                            tilemap, player, enemy, goal_rect = reset_game(level)
                            console_history.append(f"Skipped to level {level}")
                        elif cmd == "reset":
                            tilemap, player, enemy, goal_rect = reset_game(level)
                            console_history.append("Level reset")
                        elif cmd == "heal":
                            player.hp = player.max_hp
                            console_history.append("Player healed")
                        elif cmd == "help":
                            console_history.append("Available: level [n], next, reset, heal, help")
                        else:
                            console_history.append(f"Unknown command: {cmd}")
                        console_input = ""

                    elif event.key == pygame.K_BACKSPACE:
                        console_input = console_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        console_active = False
                        console_input = ""
                    else:
                        if event.unicode.isprintable():
                            console_input += event.unicode

            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    console_active = True
                    console_input = ""

                if event.type == pygame.KEYDOWN and time.time() - last_super_time >= 10:
                    if event.key == pygame.K_1:
                        px, py = int(player.pos.x // TILE_SIZE), int(player.pos.y // TILE_SIZE)
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = px + dx, py + dy
                            if tilemap.is_wall(nx, ny):
                                tilemap.remove_wall(nx, ny)
                                break
                        last_super_time = time.time()
                    elif event.key == pygame.K_2:
                        enemy_disabled_until = time.time() + 2
                        last_super_time = time.time()
                    elif event.key == pygame.K_3:
                        slow_until = time.time() + 5
                        last_super_time = time.time()
                    elif event.key == pygame.K_4:
                        player.pos = pygame.Vector2(*random.choice(tilemap.get_free_tiles())) * TILE_SIZE + pygame.Vector2(5, 5)
                        last_super_time = time.time()
                    elif event.key == pygame.K_5:
                        enemy.pos = pygame.Vector2(*random.choice(tilemap.get_free_tiles())) * TILE_SIZE + pygame.Vector2(5, 5)
                        last_super_time = time.time()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_6 and time.time() - last_remove_trap_time >= 3:
                    px, py = int(player.pos.x // TILE_SIZE), int(player.pos.y // TILE_SIZE)
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny = px + dx, py + dy
                        if tilemap.is_trap(nx, ny) and not tilemap.is_wall(nx, ny):
                            tilemap.remove_trap(nx, ny)
                            last_remove_trap_time = time.time()
                            break

        if not collected_goal and not console_active:
            player.handle_input()
            if time.time() > enemy_disabled_until:
                speed_mod = 0.5 if time.time() < slow_until else 1.0
                enemy.update(player.pos, speed_mod)

        player.regenerate()

        player_rect = pygame.Rect(player.pos.x, player.pos.y, player.size.x, player.size.y)
        enemy_rect = pygame.Rect(enemy.pos.x, enemy.pos.y, enemy.size.x, enemy.size.y)

        if not collected_goal and player_rect.colliderect(goal_rect):
            collected_goal = True
            victory_display_time = pygame.time.get_ticks()

        if player_rect.colliderect(enemy_rect) and not collected_goal and time.time() > enemy_disabled_until:
            tilemap, player, enemy, goal_rect = reset_game(level)
            collected_goal = False
            enemy_disabled_until = 0
            slow_until = 0
            player_in_trap = 0
            continue

        tile_x = int(player.pos.x // TILE_SIZE)
        tile_y = int(player.pos.y // TILE_SIZE)
        if tilemap.is_trap(tile_x, tile_y):
            if time.time() > player_in_trap:
                player.take_damage(40)
                player_in_trap = time.time() + 1
                if player.hp <= 0:
                    tilemap, player, enemy, goal_rect = reset_game(level)
                    collected_goal = False
                    continue

        base_detect = min(100 + level * 20, 300)
        hp_ratio = player.hp / player.max_hp
        detect_radius = base_detect + (1 - hp_ratio) * 0.5 * base_detect
        enemy.detect_radius = detect_radius
        enemy.lose_radius = detect_radius + 50

        screen.fill(BG_COLOR)
        tilemap.draw(screen, player.pos, vision_radius=get_vision_radius(level))
        if not collected_goal:
            pygame.draw.rect(screen, (255, 215, 0), goal_rect)
        player.draw(screen)
        if time.time() > enemy_disabled_until:
            enemy.draw(screen)

        if console_active:
            draw_console(screen, font, console_history, console_input)

        if collected_goal:
            text = font.render(f"Level {level} complete!", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            if pygame.time.get_ticks() - victory_display_time > 1500:
                level += 1
                tilemap, player, enemy, goal_rect = reset_game(level)
                collected_goal = False

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

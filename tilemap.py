import pygame
import random
from settings import TILE_SIZE, MAP_COLS, MAP_ROWS, WALL_COLOR, PATH_COLOR

class TileMap:
    def __init__(self, use_custom_map=True):
        if use_custom_map:
            self.map = []
            

            self.traps = {}
            

            self.portals = []
        else:

            self.map = [[1 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
            self.generate_maze()
            self.traps = set(random.sample(self.get_free_tiles(), k=10))
            self.portals = random.sample(self.get_free_tiles(), k=4)
        
        self.wall_surface = self.create_wall_surface()
        self.path_surface = self.create_path_surface()

    def generate_maze(self):
        def carve_passages(cx, cy):
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < MAP_COLS-1 and 0 < ny < MAP_ROWS-1:
                    if self.map[ny][nx] == 1:
                        self.map[cy + dy//2][cx + dx//2] = 0
                        self.map[ny][nx] = 0
                        carve_passages(nx, ny)

        self.map[1][1] = 0
        carve_passages(1, 1)
        self.map[MAP_ROWS-2][MAP_COLS-2] = 0

    def create_wall_surface(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(WALL_COLOR)
        for i in range(0, TILE_SIZE, 4):
            pygame.draw.line(surf, (50, 50, 70), (i, 0), (i, TILE_SIZE))
            pygame.draw.line(surf, (50, 50, 70), (0, i), (TILE_SIZE, i))
        return surf

    def create_path_surface(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(PATH_COLOR)
        return surf

    def draw(self, screen, player_pos=None, vision_radius=5):
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                draw_tile = True
                if player_pos:
                    dx = abs(x * TILE_SIZE - player_pos.x)
                    dy = abs(y * TILE_SIZE - player_pos.y)
                    if dx > vision_radius * TILE_SIZE or dy > vision_radius * TILE_SIZE:
                        draw_tile = False

                if draw_tile:
                    pos = (x * TILE_SIZE, y * TILE_SIZE)
                    if tile == 1:
                        screen.blit(self.wall_surface, pos)
                    else:
                        screen.blit(self.path_surface, pos)

                    if (x, y) in self.traps:
                        pygame.draw.circle(screen, (200, 0, 0), (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), 5)

                    if (x, y) in self.portals:
                        pygame.draw.circle(screen, (100, 255, 255), (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), 5)

    def is_wall(self, x, y):
        if x < 0 or x >= MAP_COLS or y < 0 or y >= MAP_ROWS:
            return True
        return self.map[y][x] == 1

    def remove_wall(self, x, y):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            self.map[y][x] = 0

    def get_free_tiles(self):
        free_tiles = []
        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                if self.map[y][x] == 0:
                    free_tiles.append((x, y))
        return free_tiles

    def is_trap(self, x, y):
        return (x, y) in self.traps

    def is_portal(self, x, y):
        return (x, y) in self.portals

    def get_random_portal_except(self, current):
        other_portals = [p for p in self.portals if p != current]
        if other_portals:
            return random.choice(other_portals)
        return None

    def remove_trap(self, x, y):
        if (x, y) in self.traps:
            self.traps.remove((x, y))
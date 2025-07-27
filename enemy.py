import pygame
import time
from typing import List, Tuple
from astar import astar
from settings import (
    TILE_SIZE, ENEMY_COLOR, SHADOW_COLOR, 
    MAP_COLS, SHADOW_OFFSET, MAP_ROWS
)

class Enemy:
    def __init__(
        self, 
        pos: Tuple[float, float], 
        tilemap: object,
        speed: float = 2.0,
        chase_speed: float = 3.5,
        detect_radius: float = 150,
        lose_radius: float = 200
    ):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.size = pygame.Vector2(20, 20)
        self.max_acceleration = 0.15
        self.base_speed = speed
        self.chase_speed = chase_speed
        self.detect_radius = detect_radius
        self.lose_radius = lose_radius
        self.tilemap = tilemap
        self._setup_visuals()
        self.state = "patrol"
        self.patrol_points = [
            pygame.Vector2(TILE_SIZE + 5, TILE_SIZE + 5),
            pygame.Vector2((MAP_COLS - 2) * TILE_SIZE + 5, TILE_SIZE + 5)
        ]
        self.current_patrol_index = 0
        self.chase_target_pos = None
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.last_path_calc_time = 0
        self.path_recalc_interval = 0.6
        self.last_explosion_time = 0
        self.explosion_cooldown = 15
        self.last_player_seen_time = 0

    def _setup_visuals(self) -> None:
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, ENEMY_COLOR, (0, 0, *self.size))
        self.shadow = pygame.Surface(self.size, pygame.SRCALPHA)
        shadow_color = (*SHADOW_COLOR[:3], SHADOW_COLOR[3])
        pygame.draw.rect(self.shadow, shadow_color, (0, 0, *self.size))
        self.wait_time = 0  
        self.wait_duration = 1.0  

    def update(self, player_pos, player_hp=100, speed_multiplier=1.0):
        now = time.time()
        dist_to_player = self.pos.distance_to(player_pos)
        dynamic_detect_radius = self.detect_radius + (100 - player_hp) * 1.5 
        dynamic_lose_radius = self.lose_radius + (100 - player_hp) * 1.5

        if dist_to_player <= dynamic_detect_radius:
            self.last_player_seen_time = now

        if now - self.last_explosion_time >= self.explosion_cooldown:
            self.explode_walls_around()
            self.last_explosion_time = now

        if self.state != "chase" and (
            dist_to_player <= dynamic_detect_radius or 
            now - self.last_player_seen_time < 3.0
        ):
            self.state = "chase"
            self.path = []
            self.path_index = 0
        elif self.state == "chase" and (
            dist_to_player > dynamic_lose_radius and 
            now - self.last_player_seen_time >= 3.0
        ):
            self.state = "return"
            self.path = []
            self.path_index = 0
            self.chase_target_pos = self.patrol_points[self.current_patrol_index]

        if self.state == "patrol":
            self.patrol(speed_multiplier)
        elif self.state == "chase":
            self.chase(player_pos, speed_multiplier, now)
        elif self.state == "return":
            self.return_to_patrol(speed_multiplier, now)
        elif self.state == "wait":
            self.wait(now)

    def explode_walls_around(self):
        tile_x = int(self.pos.x // TILE_SIZE)
        tile_y = int(self.pos.y // TILE_SIZE)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  
                nx = tile_x + dx
                ny = tile_y + dy
                if 0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS:
                    if self.tilemap.is_wall(nx, ny):
                        self.tilemap.remove_wall(nx, ny)

    def patrol(self, speed_multiplier):
        target = self.patrol_points[self.current_patrol_index]
        arrived = self.move_smooth(target, self.base_speed * speed_multiplier)
        if arrived:
            self.state = "wait"
            self.wait_time = time.time()

    def wait(self, now):
        if now - self.wait_time >= self.wait_duration:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.state = "patrol"

    def chase(self, player_pos, speed_multiplier, now):
        if now - self.last_path_calc_time > self.path_recalc_interval or not self.path:
            start_cell = (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
            goal_cell = (int(player_pos.x // TILE_SIZE), int(player_pos.y // TILE_SIZE))
            self.path = astar(self.tilemap.map, start_cell, goal_cell)
            self.path_index = 0
            self.last_path_calc_time = now
        if self.path and self.path_index < len(self.path):
            target_cell = self.path[self.path_index]
            target_pos = pygame.Vector2(target_cell[0] * TILE_SIZE + TILE_SIZE/2, target_cell[1] * TILE_SIZE + TILE_SIZE/2)
            arrived = self.move_smooth(target_pos, self.chase_speed * speed_multiplier)
            if arrived:
                self.path_index += 1
        else:
            direction = (player_pos - self.pos)
            if direction.length() > 0:
                predicted_pos = player_pos + direction.normalize() * 10  
                self.move_smooth(predicted_pos, self.chase_speed * speed_multiplier)

    def return_to_patrol(self, speed_multiplier, now):
        if not self.path or self.path_index >= len(self.path):
            start_cell = (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
            goal_cell = (int(self.chase_target_pos.x // TILE_SIZE), int(self.chase_target_pos.y // TILE_SIZE))
            self.path = astar(self.tilemap.map, start_cell, goal_cell)
            self.path_index = 0
            self.last_path_calc_time = now
        if self.path and self.path_index < len(self.path):
            target_cell = self.path[self.path_index]
            target_pos = pygame.Vector2(target_cell[0] * TILE_SIZE + TILE_SIZE/2, target_cell[1] * TILE_SIZE + TILE_SIZE/2)
            arrived = self.move_smooth(target_pos, self.base_speed)
            if arrived:
                self.state = "patrol"
        else:
            self.state = "patrol"

    def move_smooth(self, target, max_speed):
        desired_velocity = (target - self.pos)
        distance = desired_velocity.length()
        if distance == 0:
            return True
        desired_velocity = desired_velocity.normalize() * max_speed
        steering = desired_velocity - self.velocity
        if steering.length() > self.max_acceleration:
            steering.scale_to_length(self.max_acceleration)
        self.velocity += steering
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)
        next_pos = self.pos + self.velocity
        if not self.collides(next_pos):
            self.pos = next_pos
        else:
            if not self.collides(self.pos + pygame.Vector2(self.velocity.x, 0)):
                self.pos.x += self.velocity.x
                self.velocity.y = 0
            elif not self.collides(self.pos + pygame.Vector2(0, self.velocity.y)):
                self.pos.y += self.velocity.y
                self.velocity.x = 0
            else:
                self.velocity = pygame.Vector2(0, 0)
        return distance < max_speed

    def collides(self, pos):
        corners = [
            pos,
            pos + pygame.Vector2(self.size.x, 0),
            pos + pygame.Vector2(0, self.size.y),
            pos + self.size
        ]
        for corner in corners:
            tile_x = int(corner.x // TILE_SIZE)
            tile_y = int(corner.y // TILE_SIZE)
            if self.tilemap.is_wall(tile_x, tile_y):
                return True
        return False

    def draw(self, screen):
        shadow_pos = self.pos + pygame.Vector2(SHADOW_OFFSET)
        screen.blit(self.shadow, shadow_pos)
        screen.blit(self.image, self.pos)

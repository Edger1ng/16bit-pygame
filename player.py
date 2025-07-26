import pygame
from settings import PLAYER_SPEED, SHADOW_OFFSET, PLAYER_COLOR, SHADOW_COLOR, TILE_SIZE

class Player:
    def __init__(self, pos, tilemap):
        self.pos = pygame.Vector2(pos)
        self.size = pygame.Vector2(20, 20)
        self.tilemap = tilemap

        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, PLAYER_COLOR, (0, 0, *self.size))

        self.shadow = pygame.Surface(self.size, pygame.SRCALPHA)
        shadow_color = (*SHADOW_COLOR[:3], SHADOW_COLOR[3])
        pygame.draw.rect(self.shadow, shadow_color, (0, 0, *self.size))

        self.max_hp = 100
        self.hp = self.max_hp
        self.last_regen_time = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def regenerate(self):
        now = pygame.time.get_ticks()
        if now - self.last_regen_time > 5000:
            self.hp += 20
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            self.last_regen_time = now

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            move.y = -1
        if keys[pygame.K_s]:
            move.y = 1
        if keys[pygame.K_a]:
            move.x = -1
        if keys[pygame.K_d]:
            move.x = 1
        if move.length() > 0:
            move = move.normalize() * PLAYER_SPEED
            self.try_move(move)

    def try_move(self, move):
        new_pos = self.pos + move
        if not self.collides(new_pos):
            self.pos = new_pos
        else:
            if not self.collides(self.pos + pygame.Vector2(move.x, 0)):
                self.pos.x += move.x
            elif not self.collides(self.pos + pygame.Vector2(0, move.y)):
                self.pos.y += move.y

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


        bar_width = 150
        bar_height = 20
        x, y = 10, 10

        pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))

        current_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, current_width, bar_height))

        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

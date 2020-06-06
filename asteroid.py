import pygame
import random
vec2 = pygame.math.Vector2

DEBUG = False
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
AST_SPEED_MAX = 25
AST_SPEED_MIN = 10


class Asteroid:

    color = (255, 255, 255)
    radii = [10, 30, 60, 120]  # Radius size for each level of asteroid
    split_angle_max = 120
    split_angle_min = 80
    vel_lim = 50

    def __init__(self, surface, pos, vel, level):
        self.surface = surface
        self.pos = vec2(pos)
        self.vel = vec2(vel)
        if vel.magnitude_squared() > Asteroid.vel_lim * Asteroid.vel_lim:
            self.vel.scale_to_length(Asteroid.vel_lim)
        self.level = level  # Which level asteroid this is
        self.radius = Asteroid.radii[level]
        self.rect = pygame.Rect(self.pos.x, self.pos.y,
                                self.radius * 2 + 1, self.radius * 2 + 1)
        self.reenter = \
            self.pos.x + self.radius < 0 or \
            self.pos.x - self.radius > SCREEN_WIDTH or \
            self.pos.y + self.radius < 0 or \
            self.pos.y - self.radius > SCREEN_HEIGHT

    def update(self, dt):
        self.pos += self.vel * dt
        # Wrap screen
        if not self.reenter and self.pos.x + self.radius < 0:
            self.reenter = True
            self.pos.x = SCREEN_WIDTH + self.radius
        elif not self.reenter and self.pos.x - self.radius > SCREEN_WIDTH:
            self.reenter = True
            self.pos.x = 0 - self.radius

        if not self.reenter and self.pos.y + self.radius < 0:
            self.reenter = True
            self.pos.y = SCREEN_HEIGHT + self.radius
        elif not self.reenter and self.pos.y - self.radius > SCREEN_HEIGHT:
            self.reenter = True
            self.pos.y = 0 - self.radius

        self.rect.center = self.pos

        if self.reenter:
            self.reenter = \
                self.pos.x + self.radius >= 0 and \
                self.pos.x - self.radius <= SCREEN_WIDTH and \
                self.pos.y + self.radius >= 0 and \
                self.pos.y - self.radius <= SCREEN_HEIGHT

    def show(self):
        int_pos = (int(self.pos.x), int(self.pos.y))
        self.rect = pygame.draw.circle(self.surface, Asteroid.color,
                                       int_pos, self.radius, 1)
        self.rect.w += 1
        self.rect.h += 1
        if DEBUG:
            pygame.draw.line(self.surface, (0, 255, 0),
                             self.pos, self.pos + self.vel)
        return self.rect

    def split(self):
        new_level = self.level - 1
        if new_level < 0:
            return []
        new_radius = Asteroid.radii[new_level]
        num_to_create = self.radius // new_radius
        spawn_angle = random.randrange(
            Asteroid.split_angle_min, Asteroid.split_angle_max)
        base_vec = vec2(self.vel).rotate(spawn_angle / 2)
        to_ret = []
        new_vel_mag = (len(Asteroid.radii) - new_level)*(self.radius * self.vel.magnitude()) / \
            (num_to_create * new_radius)
        for i in range(num_to_create):
            spawn_vel = vec2(base_vec).rotate(-i*(spawn_angle //
                                                  num_to_create))
            spawn_vel.scale_to_length(new_vel_mag)
            to_ret.append(
                Asteroid(self.surface, self.pos, spawn_vel, new_level))
        return to_ret

    def getupperleft(self):
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        return self.rect

    @classmethod
    def genAsteroid(cls, surface):
        # Create a randomized asteroid
        side = random.randrange(4)  # Choose what side to start on
        x = random.randrange(SCREEN_WIDTH)  # Choose random position on screen
        y = random.randrange(SCREEN_HEIGHT)
        level = random.randrange(len(cls.radii))  # Choose radius level
        div_by = level + 1  # Scale velocity by radius of asteroid
        vel = None
        if side == 0:  # Top
            y = -cls.radii[level]
            vel = (random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by),
                   random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by))
        elif side == 1:  # Right
            x = SCREEN_WIDTH + cls.radii[level]
            vel = (-random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by),
                   random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by))
        elif side == 2:  # Bottom
            y = SCREEN_HEIGHT + cls.radii[level]
            vel = (random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by), -
                   random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by))
        else:  # Left
            x = -cls.radii[level]
            vel = (random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by),
                   random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by))
        return cls(surface, vec2(x, y), vec2(vel), level)

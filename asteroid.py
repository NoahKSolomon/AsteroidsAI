import pygame
import random
vec2 = pygame.math.Vector2

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
AST_SPEED_MAX = 25
AST_SPEED_MIN = 10
BUMP_PERCENTAGE = 0.1  # What percentage of the radii the random bumps can be
NUM_VERTS = 15


class Asteroid:

    color = (255, 255, 255)
    radii = [10, 30, 60, 120]  # Radius size for each level of asteroid
    split_angle_max = 120
    split_angle_min = 80
    vel_lim = 50
    rot_vel_lim = 5

    def __init__(self, surface, pos, vel, rot_vel, level):
        """Create an Asteroid object

        Arguments:
        surface -- pygame.Surface to draw the Asteroid on
        pos -- initial position of Asteroid
        vel -- inital velocity of Asteroid
        rot_vel -- rotational velocity of Asteroid
        level -- which level of radius Asteroid is
        """
        self.surface = surface
        self.pos = vec2(pos)
        self.vel = vec2(vel)
        self.rot_vel = max(  # Clamp rotational speed
            min(rot_vel, Asteroid.rot_vel_lim), -Asteroid.rot_vel_lim)
        if vel.magnitude_squared() > Asteroid.vel_lim * Asteroid.vel_lim:
            self.vel.scale_to_length(Asteroid.vel_lim)
        self.level = level  # Which level asteroid this is
        self.radius = Asteroid.radii[level]
        self.verts = []
        angle = 0
        angle_inc = 360 / NUM_VERTS
        x_min, x_max, y_min, y_max = None, None, None, None  # Track for rect
        for i in range(NUM_VERTS):
            new_radius = self.radius + self.radius * \
                ((random.random() * 2 * BUMP_PERCENTAGE) - BUMP_PERCENTAGE)
            vert_vec = vec2(0, 1)
            vert_vec.scale_to_length(new_radius)  # Scale to new radius
            vert_vec = vert_vec.rotate(angle)  # Rotate to proper position
            vert_vec = self.pos + vert_vec  # Translate to screen position
            x_min = vert_vec.x if x_min == None or vert_vec.x < x_min else x_min
            x_max = vert_vec.x if x_max == None or vert_vec.x > x_max else x_max
            y_min = vert_vec.y if y_min == None or vert_vec.y < y_min else y_min
            y_max = vert_vec.y if y_max == None or vert_vec.y > y_max else y_max
            self.verts.append(vert_vec)
            angle += angle_inc
        self.rect = pygame.Rect(x_min, y_min, x_max - x_min, y_max - y_min)
        self.reenter = \
            x_max < 0 or x_min > SCREEN_WIDTH or \
            y_max < 0 or y_min > SCREEN_HEIGHT

    def update(self, dt):
        """Update state of Asteroid

        Arguments:
        dt -- the delta time to update with
        """
        self.pos += self.vel * dt
        x_min, x_max, y_min, y_max = None, None, None, None  # Track for rect
        for i in range(len(self.verts)):
            self.verts[i] += self.vel * dt
            temp = self.verts[i] - self.pos
            temp = temp.rotate(self.rot_vel)
            self.verts[i] = self.pos + temp
            x_min = self.verts[i].x if x_min == None or self.verts[i].x < x_min else x_min
            x_max = self.verts[i].x if x_max == None or self.verts[i].x > x_max else x_max
            y_min = self.verts[i].y if y_min == None or self.verts[i].y < y_min else y_min
            y_max = self.verts[i].y if y_max == None or self.verts[i].y > y_max else y_max
        self.rect.left = x_min
        self.rect.right = x_max
        self.rect.top = y_min
        self.rect.bottom = y_max

        # Wrap screen
        if not self.reenter and self.rect.right < 0:
            self.reenter = True
            self.pos.x += SCREEN_WIDTH + self.rect.width
            for vert in self.verts:
                vert.x += SCREEN_WIDTH + self.rect.width
        elif not self.reenter and self.rect.left > SCREEN_WIDTH:
            self.reenter = True
            self.pos.x -= SCREEN_WIDTH + self.rect.width
            for vert in self.verts:
                vert.x -= SCREEN_WIDTH + self.rect.width

        if not self.reenter and self.rect.top < 0:
            self.reenter = True
            self.pos.y += SCREEN_HEIGHT + self.rect.height
            for vert in self.verts:
                vert.y += SCREEN_HEIGHT + self.rect.height
        elif not self.reenter and self.rect.bottom > SCREEN_HEIGHT:
            self.reenter = True
            self.pos.y -= SCREEN_HEIGHT + self.rect.height
            for vert in self.verts:
                vert.y -= SCREEN_HEIGHT + self.rect.height

        self.rect.center = self.pos

        if self.reenter:
            self.reenter = \
                self.pos.x + self.radius >= 0 and \
                self.pos.x - self.radius <= SCREEN_WIDTH and \
                self.pos.y + self.radius >= 0 and \
                self.pos.y - self.radius <= SCREEN_HEIGHT

    def show(self):
        """Draw the Asteroid to the given surface based on Asteroid state"""
        int_pos = (int(self.pos.x), int(self.pos.y))
        self.rect = pygame.draw.polygon(
            self.surface, Asteroid.color, self.verts, 1)
        return self.rect

    def split(self):
        """Split Asteroid into smaller Asteroids and return a list"""
        new_level = self.level - 1
        if new_level < 0:
            return []
        new_radius = Asteroid.radii[new_level]
        num_to_create = self.radius // new_radius
        spawn_angle = random.randrange(
            Asteroid.split_angle_min, Asteroid.split_angle_max)
        base_vec = None
        if self.vel.xy != (0, 0):
            base_vec = vec2(self.vel).rotate(spawn_angle / 2)
        to_ret = []
        new_vel_mag = (len(Asteroid.radii) - new_level)*(self.radius * self.vel.magnitude()) / \
            (num_to_create * new_radius)
        for i in range(num_to_create):
            spawn_vel = vec2(base_vec).rotate(-i*(spawn_angle //
                                                  num_to_create)) if base_vec != None else vec2(0, 0)
            if spawn_vel.xy != (0, 0):
                spawn_vel.scale_to_length(new_vel_mag)
            new_rot_vel = (spawn_vel.magnitude_squared() /
                           self.vel.magnitude_squared()) * self.rot_vel
            to_ret.append(
                Asteroid(self.surface, self.pos, spawn_vel, new_rot_vel, new_level))
        return to_ret

    def getupperleft(self):
        """Get the upper left corner of the bouning rectangle of Asteroid"""
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        """Get the bounding rectangle of Asteroid"""
        return pygame.Rect(self.rect)

    @classmethod
    def genAsteroid(cls, surface):
        """Create a randomized asteroid

        Arguments:
        surface -- pygame.Surface to draw asteroid to
        """
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
        vel_vec = vec2(vel)
        rot_vel = \
            cls.rot_vel_lim * (vel_vec.magnitude_squared() /
                               (AST_SPEED_MAX * AST_SPEED_MAX))
        return cls(surface, vec2(x, y), vel_vec, rot_vel, level)

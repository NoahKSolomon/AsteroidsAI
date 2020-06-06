import pygame
import math
import time
from controller import Player
vec2 = pygame.math.Vector2

# Ship variables
DEBUG = False
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


class Ship:

    color = (250, 250, 250)
    font = None
    size = 25
    acc_mag = 25
    rot_vel = 75
    vel_lim = 100
    shots_per_sec = 3

    def __init__(self, surface, pos, dir=(1, 0)):
        # Draw state
        self.surface = surface  # surface to draw ship to
        # Movement state
        self.pos = vec2(pos)
        self.vel = vec2((0, 0))  # velocity of ship
        self.acc = 0  # Acceleration of ship along dir
        self.dir = vec2(dir).normalize()  # direction ship is pointing
        self.rect = pygame.Rect(self.pos.x - (Ship.size / 2), self.pos.y - (Ship.size / 2),
                                Ship.size, Ship.size)
        # Movement control state
        self.controller = Player(self)
        self.left = False
        self.right = False
        # Shooting state
        self.shooting = False
        self.last_shot_time = -1
        self.spawnBullet = None  # Callback to spawn bullet
        # Wrapping state
        self.reenter = \
            self.pos.x + Ship.size < 0 or \
            self.pos.x - Ship.size > SCREEN_WIDTH or \
            self.pos.y + Ship.size < 0 or \
            self.pos.y - Ship.size > SCREEN_HEIGHT

    def update(self, dt):
        # Update direction
        angle = Ship.rot_vel if self.left else 0
        angle = angle - Ship.rot_vel if self.right else angle
        self.dir.rotate_ip(angle * dt)

        # Update velocity
        self.vel += self.acc * self.dir * dt

        # Limit top speed
        if self.vel.magnitude() > Ship.vel_lim:
            self.vel.scale_to_length(Ship.vel_lim)

        # Update position
        self.pos += self.vel * dt

        # Wrap screen
        if not self.reenter and self.pos.x + Ship.size < 0:
            self.reenter = True
            self.pos.x = SCREEN_WIDTH + Ship.size
        elif not self.reenter and self.pos.x - Ship.size > SCREEN_WIDTH:
            self.reenter = True
            self.pos.x = 0 - Ship.size

        if not self.reenter and self.pos.y + Ship.size < 0:
            self.reenter = True
            self.pos.y = SCREEN_HEIGHT + Ship.size
        elif not self.reenter and self.pos.y - Ship.size > SCREEN_HEIGHT:
            self.reenter = True
            self.pos.y = 0 - Ship.size

        self.rect.center = self.pos

        if self.reenter:
            self.reenter = \
                self.pos.x + Ship.size >= 0 and \
                self.pos.x - Ship.size <= SCREEN_WIDTH and \
                self.pos.y + Ship.size >= 0 and \
                self.pos.y - Ship.size <= SCREEN_HEIGHT

        # Spawn bullets
        if self.shooting:
            cur_time = time.time()
            since_last = cur_time - self.last_shot_time if self.last_shot_time != -1 else 0
            if self.last_shot_time == -1 or since_last >= 1 / Ship.shots_per_sec:
                nose = self.pos + self.dir * (Ship.size / 2)
                if self.spawnBullet != None:
                    self.spawnBullet(nose, self.dir)
                self.last_shot_time = cur_time

    def show(self):
        # Draw the ship to the screen
        # Make vectors from center of ship to verts and rotate them through self.angle
        vec_1 = self.dir * (Ship.size / 2)
        vec_2 = vec2(vec_1).rotate(360 / 2.75)
        vec_3 = vec2(vec_1).rotate(-360 / 2.75)

        vecs = [vec_1, vec_2, vec_3]
        draw_verts = [self.pos + vec for vec in vecs]
        self.rect = pygame.draw.polygon(self.surface, Ship.color, draw_verts, 1)

        if DEBUG:
            pygame.draw.line(self.surface, (255, 0, 0),  # Draw nose vector
                             self.pos, self.pos + 1.5 * vec_1)
            pygame.draw.line(self.surface, (0, 255, 0),  # Draw velocity vector
                             self.pos, self.pos + 1.5 * self.vel)
        return self.rect

    def accelerate(self, accel=True):
        # Set the acceleration of the ship
        if accel:
            self.acc += Ship.acc_mag
        else:
            self.acc -= Ship.acc_mag

    def turn(self, direction, enable=True):
        # Set the rotational velocity of the ship
        if direction == "right":
            self.right = enable
        elif direction == "left":
            self.left = enable

    def shoot(self, start=True):
        self.shooting = start

    def handle_event(self, event):
        self.controller.handle_event(event)

    def setSpawnBullet(self, func):
        self.spawnBullet = func

    def reset(self, resetPos):
        # Reset movement state
        self.pos = vec2(resetPos)
        self.vel = vec2((0, 0))  # velocity of ship
        self.acc = 0  # Acceleration of ship along dir
        self.dir = vec2((1, 0)).normalize()  # direction ship is pointing
        # Reset movement control state
        self.left = False
        self.right = False
        # Reset shooting state
        self.controller.reset()
        self.shooting = False
        self.last_shot_time = -1
        # Reset wrapping state
        self.reenter = \
            self.pos.x + Ship.size < 0 or \
            self.pos.x - Ship.size > SCREEN_WIDTH or \
            self.pos.y + Ship.size < 0 or \
            self.pos.y - Ship.size > SCREEN_HEIGHT

    def getupperleft(self):
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        return pygame.Rect(self.rect)

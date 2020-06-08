import pygame
import math
import time
from controller import Player
vec2 = pygame.math.Vector2

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
GOD_MODE = True


class Ship:

    color = (250, 250, 250)
    font = None
    size = 25
    acc_mag = 25
    rot_vel = 75
    vel_lim = 100
    shots_per_sec = 10

    def __init__(self, surface, pos, dir=(1, 0)):
        """Create a Ship object

        Arguments:
        surface -- pygame.Surface to draw Ship to
        pos -- Initial position of Ship
        dir -- Initial direction Ship is facing. Default is to right
        """
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
        # Dead state
        self.dead = False
        # Wrapping state
        self.reenter = \
            self.pos.x + Ship.size < 0 or \
            self.pos.x - Ship.size > SCREEN_WIDTH or \
            self.pos.y + Ship.size < 0 or \
            self.pos.y - Ship.size > SCREEN_HEIGHT

    def update(self, dt):
        """Update state of Ship

        Arguments:
        dt -- Delta time to modify state calculations
        """
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
        """Draw Ship to surface"""
        # Make vectors from center of ship to verts and rotate them through self.angle
        vec_1 = self.dir * (Ship.size / 2)
        vec_2 = vec2(vec_1).rotate(360 / 2.75)
        vec_3 = vec2(vec_1).rotate(-360 / 2.75)

        vecs = [vec_1, vec_2, vec_3]
        draw_verts = [self.pos + vec for vec in vecs]
        self.rect = pygame.draw.polygon(self.surface, Ship.color, draw_verts, 1)
        return self.rect

    def accelerate(self, accel=True):
        """Cause Ship to de/accelerate in direction Ship is facing

        Arguments:
        accel -- Whether to accelerate in positive or negative fashion
        """
        # Set the acceleration of the ship
        if accel:
            self.acc += Ship.acc_mag
        else:
            self.acc -= Ship.acc_mag

    def turn(self, direction, enable=True):
        """Turn the Ship in a certain direction

        Arguments:
        direction -- String of which direction to turn
        enable -- Whether to begin or end the turning action
        """
        # Set the rotational velocity of the ship
        if direction == "right":
            self.right = enable
        elif direction == "left":
            self.left = enable

    def shoot(self, start=True):
        """Shoot a Bullet from Ship"""
        self.shooting = start

    def handle_event(self, event):
        """Handle an event through Controller

        Arguments:
        event -- pygame.event to handle
        """
        self.controller.handle_event(event)

    def setSpawnBullet(self, func):
        """Set spawnBullet callback

        Arguments:
        func -- Callback to set to
        """
        self.spawnBullet = func

    def reset(self, resetPos):
        """Reset Ship to initial state

        Arguments:
        resetPos -- Position to reset Ship position to
        """
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

    def setDead(self, val):
        """Set the dead state of the Ship to 'val'"""
        self.dead = val if not GOD_MODE else False  # Godmode override

    def isDead(self):
        """Return if this Ship is dead"""
        return self.dead

    def getupperleft(self):
        """Get the upper left corner of bounding rectangle of Ship"""
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        """Get bounding rectangle of Ship"""
        return pygame.Rect(self.rect)

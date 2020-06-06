import pygame
vec2 = pygame.math.Vector2

DEBUG = False
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


class Bullet:

    radius = 2
    color = (255, 255, 255)
    vel = 0.5

    def __init__(self, surface, pos, dir):
        self.surface = surface
        self.pos = vec2(pos)
        self.dir = vec2(dir).normalize()
        self.rect = pygame.Rect(
            pos.x, pos.y, Bullet.radius * 2, Bullet.radius * 2)

    def show(self):
        int_pos = (int(self.pos.x), int(self.pos.y))
        self.rect = pygame.draw.circle(self.surface, (255, 255, 255),
                                       int_pos, Bullet.radius)
        if DEBUG:
            pygame.draw.line(self.surface, (0, 255, 0),
                             int_pos, int_pos + Bullet.vel * self.dir)
        return self.rect

    def update(self, dt):
        self.pos += self.dir * Bullet.vel * dt
        self.rect.center = self.pos
        if self.pos.x + Bullet.radius < 0 or \
                self.pos.x - Bullet.radius > SCREEN_WIDTH or \
                self.pos.y + Bullet.radius < 0 or \
                self.pos.y - Bullet.radius > SCREEN_HEIGHT:
            return True
        return False

    def getupperleft(self):
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        return self.rect

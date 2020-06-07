import pygame
vec2 = pygame.math.Vector2

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


class Bullet:

    radius = 2
    color = (255, 255, 255)
    vel = 125

    def __init__(self, surface, pos, dir):
        """Create a Bullet object

        Arguments:
        surface -- pygame.Surface to draw Bullet to
        pos -- Initial position of Bullet
        dir -- Direction Bullet is traveling
        """
        self.surface = surface
        self.pos = vec2(pos)
        self.dir = vec2(dir).normalize()
        self.rect = pygame.Rect(
            pos.x, pos.y, Bullet.radius * 2, Bullet.radius * 2)

    def show(self):
        """Draw Bullet to surface"""
        int_pos = (int(self.pos.x), int(self.pos.y))
        self.rect = pygame.draw.circle(self.surface, (255, 255, 255),
                                       int_pos, Bullet.radius)
        return self.rect

    def update(self, dt):
        """Update state of Bullet

        Arguments:
        dt -- Delta time to modify state calculations
        """
        self.pos += self.dir * Bullet.vel * dt
        self.rect.center = self.pos
        if self.pos.x + Bullet.radius < 0 or \
                self.pos.x - Bullet.radius > SCREEN_WIDTH or \
                self.pos.y + Bullet.radius < 0 or \
                self.pos.y - Bullet.radius > SCREEN_HEIGHT:
            return True
        return False

    def getupperleft(self):
        """Get the upper left corner of bounding rectangle of Bullet"""
        return (self.rect.x, self.rect.y)

    def getbounds(self):
        """Get bounding rectangle of Bullet"""
        return self.rect

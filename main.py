import pygame
import random
from ship import Ship
from asteroid import Asteroid
from bullet import Bullet
vec2 = pygame.math.Vector2

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
AST_SPEED_MAX = 25
AST_SPEED_MIN = 10
MIN_ASTEROIDS = 5
SCORE_FONT_SIZE = 20
FONT_COLOR = (255, 255, 255)
SCOREBOARD_POS = (10, 10)
BESTSCORE_POS = (SCOREBOARD_POS[0], SCOREBOARD_POS[1] + SCORE_FONT_SIZE)
PAUSE_CENTER = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")
background = pygame.Surface(screen.get_size())
background = background.convert()
scorefont = pygame.font.Font("Hyperspace Bold Italic.otf", SCORE_FONT_SIZE)
currentscoreboard = None
bestscoreboard = None
ship = None
score = 0
maxscore = 0
bullets = []
asteroids = []


def genAsteroid():
    # Create a randomized asteroid
    side = random.randrange(4)  # Choose what side to start on
    x = random.randrange(SCREEN_WIDTH)
    y = random.randrange(SCREEN_HEIGHT)
    level = random.randrange(len(Asteroid.radii))
    div_by = level + 1
    vel = None
    if side == 0:  # Top
        y = -Asteroid.radii[level]
        vel = (random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by),
               random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by))
    elif side == 1:  # Right
        x = SCREEN_WIDTH + Asteroid.radii[level]
        vel = (-random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by),
               random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by))
    elif side == 2:  # Bottom
        y = SCREEN_HEIGHT + Asteroid.radii[level]
        vel = (random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by), -
               random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by))
    else:  # Left
        x = -Asteroid.radii[level]
        vel = (random.randrange(AST_SPEED_MIN // div_by, AST_SPEED_MAX // div_by),
               random.randrange(-AST_SPEED_MAX // div_by, AST_SPEED_MAX // div_by))
    return Asteroid(screen, pygame.math.Vector2(x, y),
                    pygame.math.Vector2(vel), level)


def spawnBullet(pos, vel):
    bullets.append(Bullet(screen, pos, vel))


def checkCollisions():
    # Return true if game is still active, false if player has died
    global asteroids
    global ship
    global bullets
    global score, maxscore
    to_split = []
    for ast in asteroids:
        # Check ship collisions
        if ship.pos.distance_to(ast.pos) < (Ship.size / 2) + ast.radius:
            return False
        for bullet in bullets:
            if bullet.pos.distance_to(ast.pos) < Bullet.radius + ast.radius:
                to_split.append((ast, bullet))
    for ast, bullet in to_split:
        if bullet in bullets:
            bullets.remove(bullet)
        if ast in asteroids:
            asteroids.remove(ast)
            score += 1
            maxscore = score if score > maxscore else maxscore
            asteroids += ast.split()
    return True


def init():
    screen.blit(background, (0, 0))
    pygame.display.update()
    global ship, asteroids, bullets, score
    if ship:
        ship.reset(vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    else:
        ship = Ship(screen, vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        ship.setSpawnBullet(spawnBullet)
    bullets = []
    score = 0
    asteroids = []
    for i in range(MIN_ASTEROIDS):
        asteroids.append(genAsteroid())


def pause():
    global background, screen
    # Create paused screen display
    paused_font = pygame.font.Font("Hyperspace Bold Italic.otf", 100)
    continue_font = pygame.font.Font("Hyperspace Bold Italic.otf", 25)
    paused_surface = paused_font.render("Paused", False, FONT_COLOR)
    continue_surface = continue_font.render(
        "Press P to Continue", False, FONT_COLOR)
    p_size = paused_font.size("Paused")
    c_size = continue_font.size("Press P to Continue")
    p_pos = (PAUSE_CENTER[0] - (p_size[0] / 2),
             PAUSE_CENTER[1] - (p_size[1] / 2))
    c_pos = (PAUSE_CENTER[0] - (c_size[0] / 2),
             PAUSE_CENTER[1] + (p_size[1] / 2) + 10)
    # Draw pause display to screen
    pygame.display.update([screen.blit(paused_surface, p_pos),
                           screen.blit(continue_surface, c_pos)])
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                    # Erase paused display from screen
                    pygame.display.update([
                        screen.blit(background, p_pos,
                                    pygame.Rect(p_pos, p_size)),
                        screen.blit(background, c_pos,
                                    pygame.Rect(c_pos, c_size))])
                    return False


def main():
    global ship, asteroids, bullets, currentscoreboard, bestscoreboard
    running = True
    clock = pygame.time.Clock()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                if pause():  # Returns true if the game is quit
                    return True
            else:
                ship.handle_event(event)

        dirty_rects = []  # For updating screen

        # Erase entities froms screen
        if currentscoreboard != None:
            dirty_rects.append(screen.blit(
                background, SCOREBOARD_POS, currentscoreboard.get_rect()))
        if bestscoreboard != None:
            dirty_rects.append(screen.blit(
                background, BESTSCORE_POS, bestscoreboard.get_rect()))

        dirty_rects.append(screen.blit(
            background, ship.getupperleft(), ship.getbounds()))
        for bullet in bullets:
            dirty_rects.append(screen.blit(
                background, bullet.getupperleft(), bullet.getbounds()))
        for ast in asteroids:
            dirty_rects.append(screen.blit(
                background, ast.getupperleft(), ast.getbounds()))

        # Update entities
        dt = clock.tick(60)
        speed = 1 / float(dt)
        ship.update(speed)
        for ast in asteroids:
            ast.update(speed)
        for i in range(len(bullets)-1, -1, -1):
            if bullets[i].update(dt):
                bullets.remove(bullets[i])

        if running:  # running may be set to false in quit event
            running = checkCollisions()

        if len(asteroids) < MIN_ASTEROIDS:
            for i in range(MIN_ASTEROIDS - len(asteroids)):
                asteroids.append(genAsteroid())

        # Show entities
        dirty_rects.append(ship.show())
        for ast in asteroids:
            dirty_rects.append(ast.show())
        for bullet in bullets:
            dirty_rects.append(bullet.show())

        currentscoreboard = scorefont.render(
            f"Score: {score}", False, FONT_COLOR)
        bestscoreboard = scorefont.render(
            f"Best: {maxscore}", False, FONT_COLOR)
        dirty_rects.append(screen.blit(currentscoreboard, SCOREBOARD_POS))
        dirty_rects.append(screen.blit(bestscoreboard, BESTSCORE_POS))

        pygame.display.update(dirty_rects)
    return False


quit = False
while not quit:
    init()
    quit = main()

pygame.font.quit()
pygame.quit()

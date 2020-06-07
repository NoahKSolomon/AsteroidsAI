"""Run the game Asteroids"""

import pygame
import random
from ship import Ship
from asteroid import Asteroid
from bullet import Bullet
from gamestate import GameState
vec2 = pygame.math.Vector2

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
MIN_ASTEROIDS = 7
DIFFICULTY_INCREASE_THRESHOLD = 15
ASTEROID_DIFFICULTY_INCREMENT = 3
SCORE_FONT_SIZE = 20
FONT_COLOR = (255, 255, 255)
SCOREBOARD_POS = (10, 10)
BESTSCORE_POS = (SCOREBOARD_POS[0], SCOREBOARD_POS[1] + SCORE_FONT_SIZE)
PAUSE_CENTER = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
TITLE_CENTER = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
TITLE_SIZE = 150
SUBTITLE_CENTER = (TITLE_CENTER[0], TITLE_CENTER[1] + TITLE_SIZE)
SUBTITLE_SIZE = 50

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroids")
background = pygame.Surface(screen.get_size())
background = background.convert()
scorefont = pygame.font.Font("Hyperspace Bold Italic.otf", SCORE_FONT_SIZE)
score = 0
maxscore = 0
asteroid_spawn_count = MIN_ASTEROIDS
currentscoreboard = None
bestscoreboard = None
ship = None
bullets = []
asteroids = []
state = GameState.MAIN_MENU


def checkCollisions():
    """Handle collisions between entities"""
    # Return true if game is still active, false if player has died
    global asteroids, ship, bullets, score, maxscore, asteroid_spawn_count
    to_split = []
    for ast in asteroids:
        # Check ship collisions
        if ship.pos.distance_to(ast.pos) < (Ship.size / 2) + ast.radius:
            ship.setDead(True)
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
            if score % DIFFICULTY_INCREASE_THRESHOLD == 0:
                asteroid_spawn_count += ASTEROID_DIFFICULTY_INCREMENT
            maxscore = score if score > maxscore else maxscore
            asteroids += ast.split()
    return True


def reset():
    """Reset the screen and reset entities"""
    screen.blit(background, (0, 0))  # Erase screen
    pygame.display.update()
    global ship, asteroids, bullets, score, asteroid_spawn_count
    if ship:
        ship.reset(vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    else:
        ship = Ship(screen, vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        ship.setSpawnBullet(
            lambda pos, vel: bullets.append(Bullet(screen, pos, vel)))
    bullets = []
    score = 0
    asteroids = []
    asteroid_spawn_count = MIN_ASTEROIDS
    for i in range(asteroid_spawn_count):
        asteroids.append(Asteroid.genAsteroid(screen))


def mainmenu():
    global screen, background, state
    # Erase screen
    screen.blit(background, (0, 0))

    title_font = pygame.font.Font("Hyperspace Bold Italic.otf", TITLE_SIZE)
    subtitle_font = pygame.font.Font(
        "Hyperspace Bold Italic.otf", SUBTITLE_SIZE)

    title_surface = title_font.render("ASTEROIDS", False, FONT_COLOR)
    subtitle_surface = subtitle_font.render(
        "Press any key to play", False, FONT_COLOR)

    title_size = title_font.size("ASTEROIDS")
    subtitle_size = subtitle_font.size("Press any key to play")

    title_pos = (TITLE_CENTER[0] - (title_size[0] / 2),
                 TITLE_CENTER[1] - (title_size[1] / 2))
    subtitle_pos = (TITLE_CENTER[0] - (subtitle_size[0] / 2),
                    TITLE_CENTER[1] + (title_size[1] / 2))

    screen.blit(title_surface, title_pos)
    screen.blit(subtitle_surface, subtitle_pos)
    pygame.display.update()

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = GameState.QUIT
                return
            if event.type == pygame.KEYUP:  # Start game on keyup
                state = GameState.PLAY
                return


def pause():
    """Pause the game"""
    global background, screen, state
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
                state = GameState.QUIT
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    state = GameState.PLAY
                    # Erase paused display from screen
                    pygame.display.update([
                        screen.blit(background, p_pos,
                                    pygame.Rect(p_pos, p_size)),
                        screen.blit(background, c_pos,
                                    pygame.Rect(c_pos, c_size))])
                    return


def quit():
    """Quit the program entirely"""
    pygame.font.quit()
    pygame.quit()


def play():
    """Run the main game loop of Asteroids"""
    global ship, asteroids, bullets, currentscoreboard, bestscoreboard, state
    running = True
    clock = pygame.time.Clock()
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                state = GameState.QUIT
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = GameState.PAUSE
                return
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

        # Spawn more Asteroids if too few exist
        if len(asteroids) < asteroid_spawn_count:
            for i in range(asteroid_spawn_count - len(asteroids)):
                asteroids.append(Asteroid.genAsteroid(screen))

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


while True:
    if state is GameState.MAIN_MENU:
        mainmenu()
    elif state is GameState.PLAY:
        if ship == None or ship.isDead():
            reset()
        play()
    elif state is GameState.PAUSE:
        pause()
    elif state is GameState.QUIT:
        quit()
        break

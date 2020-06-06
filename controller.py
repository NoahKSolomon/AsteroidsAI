import pygame


class Controller:

    def __init__(self, object):
        self.object = object  # The object to be controlled

    def handle_event(self, event):
        pass  # Do nothing on events


class Player(Controller):

    def __init__(self, object):
        Controller.__init__(self, object)
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.space = False

    def reset(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.space = False

    def handle_event(self, event):
        # Handle one event at a time
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.w = True
                self.object.accelerate()
            elif event.key == pygame.K_s:
                self.s = True
                self.object.accelerate(False)
            elif event.key == pygame.K_a:
                self.a = True
                self.object.turn("right")
            elif event.key == pygame.K_d:
                self.d = True
                self.object.turn("left")
            elif event.key == pygame.K_SPACE:
                self.space = True
                self.object.shoot()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                if self.w:
                    self.object.accelerate(False)
                    self.w = False
            elif event.key == pygame.K_s:
                if self.s:
                    self.object.accelerate()
                    self.s = False
            elif event.key == pygame.K_a:
                if self.a:
                    self.object.turn("right", False)
                    self.a = False
            elif event.key == pygame.K_d:
                if self.d:
                    self.object.turn("left", False)
                    self.d = False
            elif event.key == pygame.K_SPACE:
                if self.space:
                    self.object.shoot(False)
                    self.space = False

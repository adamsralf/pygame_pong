import os
from random import choice
from time import time
from typing import Any, Tuple

import pygame


class Settings:
    WINDOW = pygame.rect.Rect(0, 0, 1000, 600)
    FPS = 60
    DELTATIME = 1.0 / FPS
    POINTS = [0, 0]


class Background(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.surface.Surface(Settings.WINDOW.size).convert()
        self.rect = self.image.get_rect()
        self.image.fill("darkred")
        self._paint_net()

    def _paint_net(self):
        rect = pygame.rect.Rect(0, 0, 3, 30)
        rect.centerx = Settings.WINDOW.centerx
        rect.top = 50
        while rect.bottom < Settings.WINDOW.bottom:
            pygame.draw.rect(self.image, "grey", rect, 0)
            rect.move_ip(0, 40)


class Paddle(pygame.sprite.Sprite):
    BORDERDISTANCE = {"horizontal": 50, "vertical": 10}
    DIRECTION = {"up": -1, "down": 1, "halt": 0}

    def __init__(self, player: str, *groups: Tuple[pygame.sprite.Group]) -> None:
        super().__init__(*groups)
        self.rect = pygame.rect.FRect(0, 0, 15, Settings.WINDOW.height // 10)
        self.rect.centery = Settings.WINDOW.centery
        self._player = player
        if player == "left":
            self.rect.left = Paddle.BORDERDISTANCE["horizontal"]
        else:
            self.rect.right = Settings.WINDOW.right - Paddle.BORDERDISTANCE["horizontal"]
        self._speed = Settings.WINDOW.height // 2
        self._direction = Paddle.DIRECTION["halt"]
        self.image = pygame.surface.Surface(self.rect.size).convert()
        self.image.fill("yellow")

    def update(self, *args: Any, **kwargs: Any) -> None:
        if "action" in kwargs.keys():
            if kwargs["action"] == "move":
                self._move()
            elif kwargs["action"] in Paddle.DIRECTION:
                self._direction = Paddle.DIRECTION[kwargs["action"]]
        return super().update(*args, **kwargs)

    def _move(self) -> None:
        if self._direction != Paddle.DIRECTION["halt"]:
            self.rect.move_ip(0, self._speed * self._direction * Settings.DELTATIME)
            if self._direction == Paddle.DIRECTION["up"]:
                self.rect.top = max(self.rect.top, Paddle.BORDERDISTANCE["vertical"])
            elif self._direction == Paddle.DIRECTION["down"]:
                self.rect.bottom = min(self.rect.bottom, Settings.WINDOW.bottom - Paddle.BORDERDISTANCE["vertical"])


class Ball(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.FRect(0, 0, 20, 20)
        self.image = pygame.surface.Surface(self.rect.size).convert()
        self.image.set_colorkey("black")
        pygame.draw.circle(self.image, "green", self.rect.center, self.rect.width // 2)
        self.speed = Settings.WINDOW.width // 3
        self.speedxy = pygame.Vector2()
        self._service()

    def update(self, *args, **kwargs):
        self._move()
        return super().update(*args, **kwargs)

    def _service(self) -> None:
        self.rect.center = Settings.WINDOW.center
        self.speedxy.x = choice([-1, 1])
        self.speedxy.y = choice([-1, 1])
        print(f"Links: {Settings.POINTS[0]} - Rechts: {Settings.POINTS[1]}")

    def _move(self) -> None:
        self.rect.move_ip(self.speedxy * self.speed * Settings.DELTATIME)
        if self.rect.top <= Settings.WINDOW.top:
            self.speedxy.y *= -1
            self.rect.top = Settings.WINDOW.top
        elif self.rect.bottom >= Settings.WINDOW.bottom:
            self.speedxy.y *= -1
            self.rect.bottom = Settings.WINDOW.bottom
        elif self.rect.right <= Settings.WINDOW.left:
            Settings.POINTS[1] += 1
            self._service()
        elif self.rect.left >= Settings.WINDOW.right:
            Settings.POINTS[0] += 1
            self._service()


class Game:
    def __init__(self):
        pygame.init()
        self._display = pygame.display.set_mode(Settings.WINDOW.size)
        pygame.display.set_window_position((30, 40))
        pygame.display.set_caption("My Kind of Pong")
        self._clock = pygame.time.Clock()
        self._background = pygame.sprite.GroupSingle(Background())
        self._all_sprites = pygame.sprite.Group()
        self._paddle = {}
        self._paddle["left"] = Paddle("left", self._all_sprites)
        self._paddle["right"] = Paddle("right", self._all_sprites)
        self._ball = Ball(self._all_sprites)
        self._running = True

    def run(self):
        time_previous = time()
        while self._running:
            self.watch_for_events()
            self.update()
            self.draw()
            time_current = time()
            Settings.DELTATIME = time_current - time_previous
            time_previous = time_current
        pygame.quit()

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                elif event.key == pygame.K_UP:
                    self._paddle["right"].update(action="up")
                elif event.key == pygame.K_DOWN:
                    self._paddle["right"].update(action="down")
                elif event.key == pygame.K_w:
                    self._paddle["left"].update(action="up")
                elif event.key == pygame.K_s:
                    self._paddle["left"].update(action="down")
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self._paddle["right"].update(action="halt")
                elif event.key in (pygame.K_w, pygame.K_s):
                    self._paddle["left"].update(action="halt")

    def update(self):
        self._all_sprites.update(action="move")

    def draw(self):
        self._background.draw(self._display)
        self._all_sprites.draw(self._display)
        pygame.display.flip()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

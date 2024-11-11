import os
from random import choice, randrange
from time import time
from typing import Any, Tuple

import pygame


class Settings:
    WINDOW = pygame.rect.Rect(0, 0, 1000, 600)
    FPS = 60
    DELTATIME = 1.0 / FPS
    KI = {"left": False, "right": False}
    SOUND = True
    PATH = {}
    PATH["file"] = os.path.dirname(os.path.abspath(__file__))
    PATH["sound"] = os.path.join(PATH["file"], "sounds")

    @staticmethod
    def get_sound(filename: str) -> str:
        return os.path.join(Settings.PATH["sound"], filename)


class MyEvents:
    POINT_FOR = pygame.USEREVENT
    MYEVENT = pygame.event.Event(POINT_FOR, player=0)


class Background(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.surface.Surface(Settings.WINDOW.size).convert()
        self.rect = self.image.get_rect()
        self.image.fill("darkred")
        self._paint_net()

    def _paint_net(self) -> None:
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
        self._speed = Settings.WINDOW.height // 1.5
        self._direction = Paddle.DIRECTION["halt"]
        self.image = pygame.surface.Surface(self.rect.size).convert()
        self.image.fill("yellow")

    def update(self, *args: Any, **kwargs: Any) -> None:
        if "action" in kwargs.keys():
            if kwargs["action"] == "move":
                self._move()
            elif kwargs["action"] in Paddle.DIRECTION:
                self._direction = Paddle.DIRECTION[kwargs["action"]]
            elif kwargs["action"] == "repaint":
                if Settings.KI[self._player]:
                    self.image.fill("lightblue")
                else:
                    self.image.fill("yellow")
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
        self._sounds = {}
        self._sounds["left"] = pygame.mixer.Sound(Settings.get_sound("playerl.mp3"))
        self._sounds["right"] = pygame.mixer.Sound(Settings.get_sound("playerr.mp3"))
        self._sounds["bounce"] = pygame.mixer.Sound(Settings.get_sound("bounce.mp3"))
        self.speed = Settings.WINDOW.width // 3
        self.speedxy = pygame.Vector2()
        self._service()

    def update(self, *args, **kwargs):
        if "action" in kwargs.keys():
            if kwargs["action"] == "move":
                self._move()
            elif kwargs["action"] == "hflip":
                self._hflip()
        return super().update(*args, **kwargs)

    def _service(self) -> None:
        self.rect.center = Settings.WINDOW.center
        self.speedxy.x = choice([-1, 1])
        self.speedxy.y = choice([-1, 1])
        self.speed = Settings.WINDOW.width // 3

    def _move(self) -> None:
        self.rect.move_ip(self.speedxy * self.speed * Settings.DELTATIME)
        if self.rect.top <= Settings.WINDOW.top:
            self._vflip("top")
        elif self.rect.bottom >= Settings.WINDOW.bottom:
            self._vflip("bottom")
        elif self.rect.right <= Settings.WINDOW.left:
            MyEvents.MYEVENT.player = 2
            pygame.event.post(MyEvents.MYEVENT)
            self._service()
        elif self.rect.left >= Settings.WINDOW.right:
            MyEvents.MYEVENT.player = 1
            pygame.event.post(MyEvents.MYEVENT)
            self._service()

    def _hflip(self) -> None:
        if Settings.SOUND:
            channel = pygame.mixer.find_channel(True)
            if self.speedxy.x < 0:
                channel.set_volume(0.9, 0.1)
                channel.play(self._sounds["left"])
            else:
                channel.set_volume(0.1, 0.9)
                channel.play(self._sounds["right"])
        self.speedxy.x *= -1
        self.speed += randrange(0, 50)

    def _vflip(self, where: str) -> None:
        if Settings.SOUND:
            rel_pos = self.rect.centerx / Settings.WINDOW.width
            channel = pygame.mixer.find_channel(True)
            channel.set_volume(1.0 - rel_pos, rel_pos)
            channel.play(self._sounds["bounce"])
        self.speedxy.y *= -1
        if where == "top":
            self.rect.top = Settings.WINDOW.top
        else:
            self.rect.bottom = Settings.WINDOW.bottom


class Score(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self._font = pygame.font.SysFont(None, 30)
        self._score = {1: 0, 2: 0}
        self.image = None
        self.rect = None
        self._render()

    def update(self, *args, **kwargs) -> None:
        if "player" in kwargs.keys():
            self._score[kwargs["player"]] += 1
            self._render()
        return super().update(*args, **kwargs)

    def _render(self) -> None:
        self.image = self._font.render(f"{self._score[1]} : {self._score[2]}", True, "white")
        self.rect = self.image.get_frect(centerx=Settings.WINDOW.centerx, top=15)


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
        self._score = Score(self._all_sprites)
        self._sound = {}
        self._sound["roar"] = pygame.mixer.Sound(Settings.get_sound("roar.mp3"))
        self._running = True

    def run(self) -> None:
        time_previous = time()
        while self._running:
            self.watch_for_events()
            self.update()
            self.draw()
            time_current = time()
            Settings.DELTATIME = time_current - time_previous
            time_previous = time_current
        pygame.quit()

    def watch_for_events(self) -> None:
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
                elif event.key == pygame.K_1:
                    Settings.KI["left"] = not Settings.KI["left"]
                    self._paddle["left"].update(action="repaint")
                    if not Settings.KI["left"]:
                        self._paddle["left"].update(action="halt")
                elif event.key == pygame.K_2:
                    Settings.KI["right"] = not Settings.KI["right"]
                    self._paddle["right"].update(action="repaint")
                    if not Settings.KI["right"]:
                        self._paddle["right"].update(action="halt")
                elif event.key == pygame.K_F2:
                    Settings.SOUND = not Settings.SOUND
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self._paddle["right"].update(action="halt")
                elif event.key in (pygame.K_w, pygame.K_s):
                    self._paddle["left"].update(action="halt")
            elif event.type == MyEvents.POINT_FOR:
                if Settings.SOUND:
                    channel = pygame.mixer.find_channel(True)
                    channel.play(self._sound["roar"])
                self._score.update(player=event.player)

    def update(self) -> None:
        for i in Settings.KI.keys():
            if Settings.KI[i]:
                self._paddlecontroler(self._paddle[i])
        self._all_sprites.update(action="move")
        self._check_collision()

    def draw(self) -> None:
        self._background.draw(self._display)
        self._all_sprites.draw(self._display)
        pygame.display.flip()

    def _check_collision(self) -> None:
        if pygame.sprite.collide_rect(self._ball, self._paddle["left"]):
            self._ball.update(action="hflip")
            self._ball.rect.left = self._paddle["left"].rect.right + 1
        elif pygame.sprite.collide_rect(self._ball, self._paddle["right"]):
            self._ball.update(action="hflip")
            self._ball.rect.right = self._paddle["right"].rect.left - 1

    def _paddlecontroler(self, paddle: Paddle) -> None:
        if paddle.rect.top < self._ball.rect.top:
            paddle.update(action="down")
        elif paddle.rect.bottom > self._ball.rect.bottom:
            paddle.update(action="up")
        else:
            paddle.update(action="halt")


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

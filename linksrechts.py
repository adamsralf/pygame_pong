import os
from time import time
from typing import Tuple

import pygame


class MyEvents:
    NEW_X_POS = pygame.USEREVENT
    EVENT_X_POS = pygame.event.Event(NEW_X_POS, x=0)


class Settings:
    WINDOW = pygame.rect.Rect(0, 0, 1000, 200)
    FPS = 60
    PATH = {}
    PATH["file"] = os.path.dirname(os.path.abspath(__file__))
    PATH["sound"] = os.path.join(PATH["file"], "sounds")

    @staticmethod
    def get_sound(filename: str) -> str:
        return os.path.join(Settings.PATH["sound"], filename)


class Background(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.surface.Surface(Settings.WINDOW.size).convert()
        self.rect = self.image.get_rect()
        self.image.fill("darkblue")


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, fontsize: int, fontcolor: list[int], center: Tuple[int, int], text: str = "") -> None:
        super().__init__()
        self.image = None
        self.rect = None
        self._fontsize = fontsize
        self._fontcolor = fontcolor
        self._font = pygame.font.SysFont("lucidaconsole", self._fontsize)
        self._text = text
        self.center = center
        self._render()

    def _render(self) -> None:
        self.image = self._font.render(self._text, True, self._fontcolor)
        self.rect = self.image.get_rect()
        self.rect.center = self.center

    def update(self, *args, **kwargs):
        if "centerx" in kwargs.keys():
            self.center = (kwargs["centerx"], self.center[1])
        if "text" in kwargs.keys():
            self._text = kwargs["text"]
        self._render()
        return super().update(*args, **kwargs)


class Ball(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.FRect(0, 0, 20, 20)
        self.image = pygame.surface.Surface((self.rect.width, self.rect.height)).convert()
        self.image.set_colorkey("black")
        pygame.draw.circle(self.image, "green", self.rect.center, self.rect.width // 2)
        self.rect.center = Settings.WINDOW.center
        self._sound = pygame.mixer.Sound(Settings.get_sound("bounce.mp3"))
        self._channel = pygame.mixer.find_channel()
        self._channel.set_volume(1, 1)

    def update(self, *args, **kwargs) -> None:
        if "action" in kwargs.keys():
            if kwargs["action"] == "left":
                self.rect.move_ip(-50, 0)
                if self.rect.left < Settings.WINDOW.left:
                    self.rect.left = Settings.WINDOW.left
            elif kwargs["action"] == "right":
                self.rect.move_ip(+50, 0)
                if self.rect.right >= Settings.WINDOW.right:
                    self.rect.right = Settings.WINDOW.right
            rel_pos = self.rect.centerx / Settings.WINDOW.width
            MyEvents.EVENT_X_POS.x = self.rect.centerx
            pygame.event.post(MyEvents.EVENT_X_POS)
            self._channel.set_volume(1 - rel_pos, rel_pos)
            self._channel.play(self._sound)
        return super().update(*args, **kwargs)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self._display = pygame.display.set_mode(Settings.WINDOW.size)
        pygame.display.set_caption("Demo Sound Links-/Rechtsverteilung ")
        pygame.display.set_window_position((10, 50))
        self._clock = pygame.time.Clock()
        self._background = pygame.sprite.GroupSingle(Background())
        self._ball = pygame.sprite.GroupSingle(Ball())
        self._all_text = pygame.sprite.Group()
        self._textdict = {}
        self._init_textsprites()
        self._running = True

    def run(self) -> None:
        time_previous = time()
        while self._running:
            self.watch_for_events()
            # self.update()
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
                elif event.key == pygame.K_LEFT:
                    self._ball.update(action="left")
                elif event.key == pygame.K_RIGHT:
                    self._ball.update(action="right")
            elif event.type == MyEvents.NEW_X_POS:
                self.update(event.x)

    def update(self, x: int) -> None:
        self._textdict["co"].update(centerx=x, text=f"pos={int(x):d}")
        self._textdict["cu"].update(centerx=x, text=f"rel_pos={x/Settings.WINDOW.width:.2f}")
        self._textdict["vl"].update(text=f"Volume Left={1 - x/Settings.WINDOW.width:.2f}")
        self._textdict["vr"].update(text=f"Volume Right={x/Settings.WINDOW.width:.2f}")

    def draw(self) -> None:
        self._background.draw(self._display)
        self._ball.draw(self._display)
        self._all_text.draw(self._display)
        pygame.display.flip()

    def _init_textsprites(self) -> None:
        fontsize = 20
        self._textdict["co"] = TextSprite(
            fontsize,
            "white",
            (Settings.WINDOW.centerx, self._ball.sprite.rect.top - 20),
            text=f"pos={Settings.WINDOW.centerx:d}",
        )
        self._textdict["cu"] = TextSprite(
            fontsize,
            "white",
            (Settings.WINDOW.centerx, self._ball.sprite.rect.bottom + 20),
            text=f"rel_pos={Settings.WINDOW.centerx/Settings.WINDOW.width:.2f}",
        )
        self._textdict["vl"] = TextSprite(
            fontsize,
            "white",
            (Settings.WINDOW.left + 100, Settings.WINDOW.top + 20),
            text=f"Volume Left={1 - Settings.WINDOW.centerx/Settings.WINDOW.width:.2f}",
        )
        self._textdict["vr"] = TextSprite(
            fontsize,
            "white",
            (Settings.WINDOW.right - 110, Settings.WINDOW.top + 20),
            text=f"Volume Right={Settings.WINDOW.centerx/Settings.WINDOW.width:.2f}",
        )
        for v in self._textdict.values():
            self._all_text.add(v)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

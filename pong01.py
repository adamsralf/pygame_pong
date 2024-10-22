from time import time

import pygame


class Settings:
    WINDOW = pygame.rect.Rect(0, 0, 1000, 600)
    FPS = 60
    DELTATIME = 1.0 / FPS


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


class Game:
    def __init__(self) -> None:
        pygame.init()
        self._display = pygame.display.set_mode(Settings.WINDOW.size)
        pygame.display.set_caption("My Kind of Pong")
        self._clock = pygame.time.Clock()
        self._background = pygame.sprite.GroupSingle(Background())
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

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self._background.draw(self._display)
        pygame.display.flip()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

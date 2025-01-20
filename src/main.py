import sys
import pygame
import random
from pathlib import Path
from itertools import cycle


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, upper: bool) -> None:
        super().__init__(pipes)
        image = sprites.load("pipe")
        if upper:
            self.image = pygame.transform.flip(image, False, True)
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self) -> None:
        self.rect.x -= 1
        screen.blit(self.image, self.rect)
        if self.rect.x <= -60:
            self.kill()


class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        ls = []
        for entry in IMAGE_PATH.glob("bird*.png"):
            ls.append(pygame.image.load(entry).convert())
        self.images = cycle(ls)
        self.image = next(self.images)
        self.rect = self.image.get_rect()
        self.rect.center = (144, 256)
        self.speed_y = 0
        self.float_y = 0
        self.frame_count = 0

    def update(self) -> None:
        self.update_image()
        self.speed_y += GRAVITY
        self.float_y += self.speed_y
        self.rect.y = int(self.float_y)
        screen.blit(self.image, self.rect)

    def jump(self) -> None:
        self.speed_y = -5

    def update_image(self) -> None:
        if self.frame_count >= 6:
            self.image = next(self.images)
            self.frame_count = 0
        self.frame_count += 1
    def die(self) -> None:
        global gameover
        gameover = True
        sound.play("hit")



class Background(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.image = sprites.load("background")

    def update(self) -> None:
        screen.blit(self.image, (0, 0))


class Ground(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.image = sprites.load("base")
        self.rect = self.image.get_rect()
        self.rect.y = 400

    def update(self) -> None:
        self.rect.x -= 1
        if self.rect.x <= -48:
            self.rect.x = 0
        screen.blit(self.image, self.rect)


class Pipes(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.frame_count = 0

    def create_pipe(self) -> None:
        upper_pipe = Pipe(288, random.randint(-300, -30), True)
        lower_pipe = Pipe(288, upper_pipe.rect.y + 430, False)
        self.add(upper_pipe, lower_pipe)

    def update(self) -> None:
        super().update()
        if self.frame_count >= 180:
            self.create_pipe()
            self.frame_count = 0
        self.frame_count += 1


class Sound:
    def __init__(self) -> None:
        self.content = {}
        for entry in SOUND_PATH.glob("*.ogg"):
            self.content[entry.stem] = pygame.mixer.Sound(entry)

    def play(self, name) -> None:
        self.content[name].play()

class Sprites:
    def __init__(self) -> None:
        self.content = {}
        for entry in IMAGE_PATH.glob("*.png"):
            self.content[entry.stem] = pygame.image.load(entry).convert()

    def load(self, name) -> pygame.Surface:
        return self.content[name]





BLACK = (0, 0, 0)
IMAGE_PATH = Path("assets", "sprites")
SOUND_PATH = Path("assets", "audio")
GRAVITY = 0.2

pygame.init()
screen = pygame.display.set_mode((288, 512))
pygame.display.set_caption("flappy bird")
clock = pygame.time.Clock()
sprites = Sprites()
bird = Bird()
backround = Background()
ground = Ground()
pipes = Pipes()
sound = Sound()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sound.play("wing")
                bird.jump()

    backround.update()
    pipes.update()
    ground.update()
    bird.update()

    if pygame.sprite.collide_rect(bird, ground):
        bird.die()
    for pipe in pipes:
        if pygame.sprite.collide_rect(bird, pipe):
            bird.die()

    pygame.display.flip()
    clock.tick(60)

import sys
import pygame
from pathlib import Path
from itertools import cycle


class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        ls = []
        for entry in IMAGE_PATH.glob("yellowbird*.png"):
            ls.append(pygame.image.load(entry).convert())
        self.images = cycle(ls)
        self.image = next(self.images)
        rotated_image = pygame.transform.rotate(self.image, -30)
        self.rect = rotated_image.get_rect()
        self.rect.center = (144, 256)
        self.speed_y = 0
        self.float_y = 0
        self.frame_count = 0

    def update(self) -> None:
        self.update_image()
        self.speed_y += GRAVITY
        self.float_y += self.speed_y
        self.rect.y = int(self.float_y)
        if self.speed_y >= 2:
            rotated_image = pygame.transform.rotate(self.image, -30)
        else:
            rotated_image = pygame.transform.rotate(self.image,  30)
        screen.blit(rotated_image, self.rect)

    def jump(self) -> None:
        self.speed_y = -5

    def update_image(self) -> None:
        if self.frame_count >= 6:
            self.image = next(self.images)
            self.frame_count = 0
        self.frame_count += 1


class Background(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.image = pygame.image.load(BACKGROUND_PATH).convert()

    def update(self) -> None:
        screen.blit(self.image, (0, 0))


class Ground(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.image = pygame.image.load(GROUND_PATH).convert()
        self.rect = self.image.get_rect()
        self.rect.y = 400

    def update(self) -> None:
        self.rect.x -= 1
        if self.rect.x <= -48:
            self.rect.x = 0
        screen.blit(self.image, self.rect)


SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
BLACK = (0, 0, 0)
IMAGE_PATH = Path("assets", "sprites")
BACKGROUND_PATH = Path("assets", "sprites", "background-day.png")
GROUND_PATH = Path("assets", "sprites", "base.png")
GRAVITY = 0.2
BIRD_IMAGE_UPDATE = pygame.USEREVENT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("flappy bird")
clock = pygame.time.Clock()
bird = Bird()
backround = Background()
ground = Ground()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()

    backround.update()
    ground.update()
    bird.update()

    if pygame.sprite.collide_rect(bird, ground):
        print("gameover")

    pygame.display.flip()
    clock.tick(60)

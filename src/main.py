import sys
import pygame
import random
from pathlib import Path
from itertools import cycle


class ScoreLabel(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.image = font.render("0", True, WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (144, 50)
        self.font_shadow = font.render("0", True, BLACK)
        self.shadow_rect = self.rect.copy()
        self.shadow_rect.x += 2
        self.shadow_rect.y += 2


    def update(self) -> None:
        self.font_shadow = font.render(str(score), True, BLACK)
        screen.blit(self.font_shadow, self.shadow_rect)
        self.image = font.render(str(score), True, WHITE)
        screen.blit(self.image, self.rect)


class ScoreArea(pygame.sprite.Sprite):
    def __init__(self, *rect) -> None:
        super().__init__(score_areas)
        self.rect = pygame.Rect(*rect)

    def update(self) -> None:
        if not gameover:
            self.rect.x -= 1
        if self.rect.x <= -60:
            self.kill()


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
        if not gameover:
            self.rect.x -= 1
        screen.blit(self.image, self.rect)
        if self.rect.x <= -60:
            self.kill()
            del self


class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.images = cycle((
            sprites.load("bird1"),
            sprites.load("bird2"),
            sprites.load("bird3"),
        ))
        self.image = next(self.images)
        self.rect = self.image.get_rect()
        self.rect.center = (144, 256)
        self.speed_y = 0
        self.float_y = self.rect.y
        self.frame_count = 0

    def update(self) -> None:
        self.update_image()
        self.speed_y += 0.2
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
        if not gameover:
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
        lower_pipe = Pipe(288, upper_pipe.rect.bottom + 100, False)
        self.add(upper_pipe, lower_pipe)
        score_area = ScoreArea(288, upper_pipe.rect.bottom, 1, 100)
        score_areas.add(score_area)

    def update(self) -> None:
        super().update()
        if self.frame_count >= 180 and not gameover:
            self.create_pipe()
            self.frame_count = 0
        self.frame_count += 1


class Sound:
    def __init__(self) -> None:
        self.content = {}
        for entry in SOUND_PATH.glob("*.ogg"):
            self.content[entry.stem] = pygame.mixer.Sound(entry)

    def play(self, name: str) -> None:
        self.content[name].play()


class Sprites:
    def __init__(self) -> None:
        self.content = {}
        for entry in IMAGE_PATH.glob("*.png"):
            self.content[entry.stem] = pygame.image.load(entry).convert()

    def load(self, name: str) -> pygame.Surface:
        return self.content[name]


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IMAGE_PATH = Path("assets", "sprites")
SOUND_PATH = Path("assets", "audio")

pygame.init()
screen = pygame.display.set_mode((288, 512))
pygame.display.set_caption("flappy bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("bauhaus93", 40)

score_areas = pygame.sprite.Group()
sprites = Sprites()
sound = Sound()
bird = Bird()
backround = Background()
ground = Ground()
pipes = Pipes()
score_label = ScoreLabel()
score = 0
gameover = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if gameover:
                    bird = Bird()
                    backround = Background()
                    ground = Ground()
                    pipes = Pipes()
                    gameover = False
                    score = 0
                else:
                    sound.play("wing")
                    bird.jump()

    backround.update()
    pipes.update()
    ground.update()
    bird.update()
    score_label.update()
    score_areas.update()

    if not gameover:
        if pygame.sprite.collide_rect(bird, ground):
            gameover = True
            sound.play("hit")
        for pipe in pipes:
            if pygame.sprite.collide_rect(bird, pipe):
                gameover = True
                sound.play("hit")
        for score_area in score_areas:
            if pygame.sprite.collide_rect(bird, score_area):
                score += 1
                sound.play("point")
                score_area.kill()
                del score_area

    pygame.display.flip()
    clock.tick(60)

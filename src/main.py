import re
import sys
import pygame
import random
from pathlib import Path
from itertools import cycle


def scene_title() -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
        
        message = sprites.load("message")
        message_rect = message.get_rect()
        message_rect.center = (144, 256)
        backround.update()
        ground.update()
        screen.blit(message, message_rect)

        pygame.display.flip()
        clock.tick(60)

class ScoreLabel(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.score = 0
        self.font_shadow = font.render(str(self.score), True, BLACK)
        self.image = font.render(str(self.score), True, WHITE)
        self.move_to_center()

    def move_to_center(self) -> None:
        self.rect = self.image.get_rect()
        self.rect.center = (144, 50)
        self.shadow_rect = self.rect.copy()
        self.shadow_rect.x += 2
        self.shadow_rect.y += 2


    def update(self) -> None:
        screen.blit(self.font_shadow, self.shadow_rect)
        screen.blit(self.image, self.rect)

    def add_score(self) -> None:
        self.score += 1
        self.font_shadow = font.render(str(self.score), True, BLACK)
        self.image = font.render(str(self.score), True, WHITE)
        self.move_to_center()
        


class ScoreArea(pygame.sprite.Sprite):
    def __init__(self, *rect) -> None:
        super().__init__(score_areas)
        self.rect = pygame.Rect(*rect)

    def update(self) -> None:
        if not bird.dead:
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
        if not bird.dead:
            self.rect.x -= 1
        screen.blit(self.image, self.rect)
        if self.rect.x <= -60:
            self.kill()


class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        self.images = cycle(sprites.load_anima("bird"))
        self.image = next(self.images)
        self.rect = self.image.get_rect()
        self.rect.center = (144, 256)
        self.speed_y = 0
        self.float_y = self.rect.y
        self.frame_count = 0
        self.dead = False

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
        if not bird.dead:
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
        lower_pipe = Pipe(288, upper_pipe.rect.bottom + 150, False)
        self.add(upper_pipe, lower_pipe)
        score_area = ScoreArea(288, upper_pipe.rect.bottom, 1, 150)
        score_areas.add(score_area)

    def update(self) -> None:
        super().update()
        if self.frame_count >= 180 and not bird.dead:
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
        self.animations = {}
        for entry in IMAGE_PATH.glob("*.png"):
            animation_match = re.match(r"(\w+)(\d+)", entry.stem)
            if animation_match:
                self.add_animation(animation_match.group(1), entry)
            else:
                self.content[entry.stem] = pygame.image.load(entry).convert_alpha()

    def load(self, name: str) -> pygame.Surface:
        return self.content[name]
    
    def load_anima(self, name: str) -> list[pygame.Surface]:
        return self.animations[name]
    
    def add_animation(self, anima_name: str, filepath: Path) -> None:
        image = pygame.image.load(filepath).convert_alpha()
        if anima_name in self.animations:
            self.animations[anima_name].append(image)
        else:
            self.animations[anima_name] = [image]
        


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IMAGE_PATH = Path("assets", "sprites")
SOUND_PATH = Path("assets", "audio")

pygame.init()
screen = pygame.display.set_mode((288, 512))
pygame.display.set_caption("flappy bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("", 60, bold=True)

sprites = Sprites()
sound = Sound()
bird = Bird()
backround = Background()
ground = Ground()
pipes = Pipes()
score_label = ScoreLabel()
score_areas = pygame.sprite.Group()


scene_title()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if bird.dead:
                    bird.__init__()
                    score_label.__init__()
                    pipes.empty()
                    score_areas.empty()
                else:
                    sound.play("wing")
                    bird.jump()

    backround.update()
    pipes.update()
    ground.update()
    bird.update()
    score_label.update()
    score_areas.update()

    if not bird.dead:
        if pygame.sprite.collide_rect(bird, ground):
            bird.dead = True
            sound.play("hit")
        for pipe in pipes:
            if pygame.sprite.collide_rect(bird, pipe):
                bird.dead = True
                sound.play("hit")
        for score_area in score_areas:
            if pygame.sprite.collide_rect(bird, score_area):
                score_label.add_score()
                sound.play("point")
                score_area.kill()

    pygame.display.flip()
    clock.tick(60)

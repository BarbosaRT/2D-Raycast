import pygame
import pygame.gfxdraw
from pygame.locals import *
import sys
import math
import numpy
from raycaster import shoot_ray
from light import Light

# PyGame Info ------------------------------------------------------ #
WINDOW_SIZE = [800, 600]
GAME_SIZE = [800, 600]
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Rays')
game_display = pygame.Surface(GAME_SIZE)
screen = pygame.display.set_mode(WINDOW_SIZE, RESIZABLE)

# Variables ---------------------------------------------------------- #
GRAY = pygame.Color(40, 40, 40)
GRAY_2 = pygame.Color(20, 20, 20)
GREEN = pygame.Color(0, 156, 59)  # 009C3B
YELLOW = pygame.Color(255, 223, 0)  # FFDF00
WHITE = pygame.Color(255, 255, 255)  # FFFFFF
ORANGE = pygame.Color(205, 75, 0)

COLORS = [ORANGE, GREEN, YELLOW, WHITE]
current_index = 0

CURRENT_COLOR = COLORS[current_index]

LIMIT = int(math.sqrt(math.pow(GAME_SIZE[0], 2) + math.pow(GAME_SIZE[1], 2)))  # You can change it
NUM_LINES = 4200  # Number of lines
FOV = 90
START_ANGLE = 45

TEXTURE1 = pygame.image.load('radial.png').convert_alpha()
NO_SHADOW_TEXTURE1 = pygame.Surface(GAME_SIZE)


def fill(surf, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    surface = surf.copy()
    w, h = surface.get_size()
    r, g, b, _ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))
    return surface


def create_texture(image, size):
    texture = pygame.transform.smoothscale(image, size)
    return texture.copy()


def create_rays(num_lines, start_angle, fov):
    lines = []
    for i in range(num_lines):
        angle = math.radians(start_angle + fov / num_lines * i)
        lines.append([angle, math.cos(angle), math.sin(angle)])
    return lines


def create_rects(size, color):
    rectangle = pygame.Surface(size)
    rect = pygame.Rect(0, 0, size[0], size[1])
    pygame.draw.rect(rectangle, color, rect, 0)
    rectangle.set_colorkey((0, 0, 0))
    mask = pygame.mask.from_surface(rectangle)
    return rectangle, mask


# Create the masks
def create_masks(color):
    top_rectangle, top_mask = create_rects((GAME_SIZE[0], 50), color)
    left_rectangle, left_mask = create_rects((50, GAME_SIZE[1]), color)

    middle_rectangle, middle_mask = create_rects((100, 100), color)
    masks = [{'mask': middle_mask, 'position': [300, 200], 'image': middle_rectangle}]
    x_pos = [[-150, 0], [0, 550]]
    y_pos = [[0, 0], [750, 0]]
    for p in x_pos:
        masks.append({'mask': top_mask, 'position': p, 'image': top_rectangle})
    for p in y_pos:
        masks.append({'mask': left_mask, 'position': p, 'image': left_rectangle})

    return masks


all_masks = create_masks(GRAY_2)

# Create the surfarray (numpy.ndarray) of the screen
# It basically combines all the masks into an image, and then transform the image to an array
mask_surface = pygame.Surface(GAME_SIZE)
mask_surface.set_colorkey('#000000')
for MASK in all_masks:
    position = MASK['position']
    mask_surf = MASK['mask'].to_surface()
    mask_surf.set_colorkey('#000000')
    mask_surface.blit(mask_surf, position)
array = pygame.surfarray.pixels2d(mask_surface).astype(dtype=numpy.int32)


def main():
    global game_display
    global START_ANGLE, current_index, CURRENT_COLOR
    scale = (GAME_SIZE[0] / WINDOW_SIZE[0], GAME_SIZE[1] / WINDOW_SIZE[1])
    origin = [0, 0]

    light = Light(origin, FOV, START_ANGLE, CURRENT_COLOR, GAME_SIZE, NUM_LINES, LIMIT)
    bulb = Light(origin, 361, 0, CURRENT_COLOR, GAME_SIZE, 360, 60)

    while 1:
        game_display.fill(GRAY)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # Changes the color
                if event.key == K_j:
                    current_index += 1
                    if current_index >= len(COLORS):
                        current_index = 0
                    CURRENT_COLOR = COLORS[current_index]
                    texture2 = fill(TEXTURE1, CURRENT_COLOR)

                    light.texture2 = texture2
                    light.texture = create_texture(texture2, (LIMIT, LIMIT))

                    bulb.texture2 = texture2
                    bulb.texture = create_texture(texture2, (60, 60))

        keys = pygame.key.get_pressed()
        if keys[K_l]:
            START_ANGLE += 1
            light.angles = create_rays(NUM_LINES, START_ANGLE, FOV)
        if keys[K_k]:
            START_ANGLE -= 1
            light.angles = create_rays(NUM_LINES, START_ANGLE, FOV)

        # Draws
        origin = pygame.mouse.get_pos()
        origin = (int(origin[0] * scale[0]), int(origin[1] * scale[1]))

        light.origin = origin
        bulb.origin = origin
        light.render(game_display, array)
        bulb.render(game_display, array)

        for mask in all_masks:
            game_display.blit(mask['image'], mask['position'])
        pygame.draw.circle(game_display, WHITE, origin, 5)

        # Manages Window
        pygame.display.set_caption(f'Rays: {clock.get_fps()}')
        pygame.transform.scale(game_display, (screen.get_width(), screen.get_height()), screen)
        clock.tick(120)
        pygame.display.update()


if __name__ == '__main__':
    main()

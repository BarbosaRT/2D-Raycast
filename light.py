import math
from pygame.locals import *
import numpy
import pygame
import pygame.gfxdraw

from raycaster import shoot_ray

pygame.init()
ORANGE = pygame.Color(205, 105, 0)


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


def shoot_rays(origin, lines, limit, texture, size, shadow, a, display):
    points = [origin]
    x, y = origin
    texture_rect = pygame.Rect(0, 0, texture.get_width(), texture.get_height())
    texture_rect.center = origin
    shadow.fill((0, 0, 0))
    shadow.blit(texture, texture_rect)

    for line in lines:
        # Calculates the distance
        distance = shoot_ray(x, y, line[0], limit, a, 1)
        # Calculates here it hits
        point = [int(origin[0] + line[1] * distance),
                 int(origin[1] + line[2] * distance)]
        # print(distance)
        # pygame.draw.circle(display, "red", point, 2)
        points.append(point)
    polygon = pygame.Surface(size)
    polygon.set_colorkey((0, 0, 0))
    pygame.gfxdraw.textured_polygon(polygon, points, shadow, 0, 0)
    if display:
        display.blit(polygon, (0, 0), special_flags=BLEND_RGBA_ADD)


class Light:
    def __init__(self, origin, fov=60, start_angle=60, color=ORANGE, size=(320, 240), lines=100, limit=1000):
        self.limit = limit
        self.fov = fov
        self.start_angle = start_angle
        self.origin = origin
        self.color = color
        self.lines = lines
        self.angles = self.create_rays(self.lines, self.start_angle, self.fov)

        # Textures --------------------------------------------------------------------- #
        self.texture1 = pygame.image.load('radial.png').convert_alpha()
        self.texture1.set_colorkey(0)
        self.no_shadow_texture1 = pygame.Surface(size)
        self.no_shadow_texture1.set_colorkey(0)
        self.texture2 = fill(self.texture1, self.color)
        self.texture = self.create_texture(self.texture2, [self.limit, self.limit])

    @staticmethod
    def create_texture(image, size):
        texture = pygame.transform.smoothscale(image, size)
        return texture.copy()

    def create_rays(self, num_lines, start_angle, fov):
        lines = []
        for i in range(num_lines):
            angle = math.radians(start_angle + fov / self.lines * i)
            lines.append([angle, math.cos(angle), math.sin(angle)])
        return lines

    def render(self, display: pygame.Surface, array):
        # THIS NEEDS TO BE INTEGER
        pos = (int(self.origin[0]), int(self.origin[1]))

        size = display.get_size()
        self.limit = int(math.sqrt(math.pow(size[0], 2) + math.pow(size[1], 2)))

        rect = pygame.Rect(pos[0], pos[1], 50, 50)
        display_r = display.get_rect()

        # THIS NEEDS TO BE INSIDE THE SCREEN
        if display_r.colliderect(rect):
            shoot_rays(pos, self.angles, self.limit, self.texture, display.get_size(), self.no_shadow_texture1,
                       array, display)


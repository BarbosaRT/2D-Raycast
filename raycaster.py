import numpy
import math
from numba import njit, prange


@njit(fastmath=True)
def shoot_ray(x: int, y: int, radians: float, max_distance: int, array: numpy.ndarray, accuracy: int = 1):
    distance: int = 0  # Length of the ray
    cosine: float = math.cos(radians)  # Cosine of the angle
    sine: float = math.sin(radians)  # Sine of the angle
    for distance in prange(0, max_distance, accuracy):
        target_x = int(x + cosine * distance)  # defines the target x position
        target_y = int(y + sine * distance)  # defines the target x position
        if target_x < 0 or target_y < 0:
            continue
        if target_x >= array.shape[0] or target_y >= array.shape[1]:
            distance = max_distance
            break
        if array[target_x, target_y]:
            break
    return distance

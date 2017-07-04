import math
import numpy as np
import scipy.ndimage.filters as filters


class Point(object):
    """
    Simple carthesian coordinates class.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return "{0}:{1}".format(str(self.x), str(self.y))

    def distance(self, b) -> float:
        dis_x = abs(self.x - b.x)
        dis_y = abs(self.y - b.y)

        return math.sqrt(pow(dis_x, 2) + pow(dis_y, 2))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))


class Area(object):

    def __init__(self, a: Point, b: Point) -> None:
        self.a = a
        self.b = b

    def __str__(self):
        return "[{0}]:[{1}]".format(str(self.a), str(self.b))

    def contains(self, point: Point) -> bool:
        return point.x >= self.a.x and point.x <= self.b.x \
               and point.y >= self.a.y and point.y <= self.b.y

def matrix(points: list, max_x=1920, max_y=1080) -> np.ndarray:
    """
    Places the **gravities** gravity points in a newly created **max_x** *
    **max_y** matrix of zeros.

    :param gravities:   The computed gravity points as computed in
                        **self.fixation()**.
    :param max_x:       The length -1 of the x axis of the support on
                        which the data was recorded.
                        Default is set to 1919.
    :param max_y:       The length -1 of the y axis of the support on
                        which the data was recorded.
                        Default is set to 1079.
    """
    base = np.zeros((max_y, max_x))
    for point in points:
        if float(point["x"]) > max_x - 1 or \
            float(point["y"]) > max_y - 1:
            continue
        base[int(point["y"]), int(point["x"])] = point["time"]
    return base

def circle_matrix(radius: int, gradient: bool = False) -> np.ndarray:
    """
    Creates a disc matrix with the given **r** radius.

    :param r:   The disc radius.
    :type r:    int
    :return:    The computed gradient disc matrix.
    :rtype:     np.ndarray
    """
    if gradient:
        grd = np.arange(0., 1. + 1./radius, 1./radius)
    else:
        grd = np.zeros(2 * radius + 2)
        grd[-1] = 1.0
    cpt = radius * 2 + 1
    retval = np.zeros((cpt, cpt))
    for i in range(cpt):
        for j in range(cpt):
            delta_i = radius + 1 - i
            delta_j = radius + 1 - j
            delta = math.sqrt(pow(delta_i, 2) + pow(delta_j, 2))
            if delta > radius:
                delta = len(grd) - 1
            retval[i-1, j-1] = 1 - grd[int(delta)]
    return retval

def draw_line(target: np.ndarray, vertical: bool, c1: int, c2: int, axe: int) -> None:
    def set_cell(a, b, val):
        if vertical:
            target[b, a] = val
        else:
            target[a, b] = val

    cpt = c1
    while cpt <= c2:
        set_cell(axe, cpt, 1.0)
        cpt += 1

def square(target: np.ndarray, x1: float, y1: float, x2: float, y2: float) -> None:
    draw_line(target, False, x1, x2, y1)
    draw_line(target, False, x1, x2, y2)
    draw_line(target, True, y1, y2, x1)
    draw_line(target, True, y1, y2, x2)

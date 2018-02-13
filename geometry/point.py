import numpy as np


class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = np.array([
            [x],
            [y]
        ])

    def __eq__(self, other):
        return True if self.x == other.x and self.y == other.y else False

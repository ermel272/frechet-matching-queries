import numpy as np


class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = np.array([
            [x],
            [y]
        ])

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return True if self.x == other.x and self.y == other.y else False

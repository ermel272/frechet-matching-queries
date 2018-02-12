import numpy as np


class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = np.array([
            [x],
            [y]
        ])

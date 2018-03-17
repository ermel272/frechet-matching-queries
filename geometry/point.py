import numpy as np


class Point2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = np.array([
            [x],
            [y]
        ])

    def is_on_edge(self, edge):
        if self.y == (edge.slope * self.x) + edge.y_int:
            if edge.p1.x < edge.p2.x:
                return edge.p1.x <= self.x <= edge.p2.x
            elif edge.p2.x < edge.p1.x:
                return edge.p2.c <= self.x <= edge.p1.x
            elif edge.p1.y < edge.p2.y:
                return edge.p1.y <= self.y <= edge.p2.y
            elif edge.p2.y < edge.p1.y:
                return edge.p2.y <= self.y <= edge.p1.y

        return False

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return True if self.x == other.x and self.y == other.y else False

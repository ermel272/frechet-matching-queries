from __future__ import division

from math import floor

from geometry.frechet_grid import FrechetGrid2D


class PolygonalCurve2D(object):
    def __init__(self, points):
        assert len(points) >= 2, 'Need at least 2 points to define a polygonal curve.'
        self.__points = points

    def add_point(self, point):
        return self.__points.append(point)

    def get_point(self, i):
        return self.__points[i] if i < len(self.__points) else None

    def get_spine(self):
        return self.__points[0], self.__points[-1]

    def size(self):
        return len(self.__points)

    def left_curve(self):
        median = int(floor(self.size() / 2))
        return PolygonalCurve2D(self.__points[:median + 1])

    def right_curve(self):
        median = int(floor(self.size() / 2))
        return PolygonalCurve2D(self.__points[median:])


class CurveRangeTree2D(object):
    def __init__(self, curve, error):
        self.__error = error
        self.root = self.__build_tree(curve)

    class Node(object):
        def __init__(self, curve, error):
            self.curve = curve
            self.left = None
            self.right = None
            self.grid = FrechetGrid2D(curve, error)

    def __build_tree(self, curve):
        node = self.Node(curve, self.__error / 2)

        if curve.size() == 2:
            return node

        node.left = self.__build_tree(curve.left_curve)
        node.right = self.__build_tree(curve.right_curve)
        return node

from __future__ import division

from math import floor

from geometry.frechet_grid import FrechetGrid2D
from geometry.tree import Tree


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
        return PolygonalCurve2D(self.__points[:median + 1]) if self.size() > 2 else self

    def right_curve(self):
        median = int(floor(self.size() / 2))
        return PolygonalCurve2D(self.__points[median:]) if self.size() > 2 else self


class CurveRangeTree2D(Tree):
    def __init__(self, curve, error):
        super(CurveRangeTree2D, self).__init__(self.__build_tree(curve))
        self.__error = error

    class Node(object):
        def __init__(self, curve, error, parent=None):
            self.parent = parent
            self.curve = curve
            self.left = None
            self.right = None
            self.grid = FrechetGrid2D(curve, error)

        def is_leaf(self):
            return True if not (self.left or self.right) else False

        # noinspection PyUnreachableCode
        def adjacent_nodes(self):
            if self.parent:
                yield self.parent

            for child in self.children():
                yield child

            return
            yield

        # noinspection PyUnreachableCode
        def children(self):
            if self.left:
                yield self.left

            if self.right:
                yield self.right

            return
            yield

    def __build_tree(self, curve, parent=None):
        node = self.Node(curve, self.__error / 2, parent)

        if curve.size() == 2:
            return node

        node.left = self.__build_tree(curve.left_curve, node)
        node.right = self.__build_tree(curve.right_curve, node)
        return node

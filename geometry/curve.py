from __future__ import division

import numpy as np
from math import floor, sqrt

from geometry.frechet_grid import FrechetGrid2D
from geometry.point import Point2D
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

    def contains(self, edge):
        p1 = self.__points[0]

        for point in self.__points[1:]:
            p2 = point
            if edge.get_point(0) == p1 and edge.get_point(1) == p2:
                return True
            p1 = p2

        return False

    def is_in_left_curve(self, edge):
        return self.left_curve().contains(edge)

    def is_in_right_curve(self, edge):
        return self.right_curve().contains(edge)


class Edge2D(PolygonalCurve2D):
    def __init__(self, p1, p2):
        super(Edge2D, self).__init__([p1, p2])
        self.p1 = p1
        self.p2 = p2

        # Although this is a line segment, define some line properties
        self.slope = (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)
        self.y_int = self.p1.y - (self.slope * self.p1.x)
        self.d = np.linalg.norm(self.p1.v - self.p2.v)

    def partition(self, d_t, x_i, delta):
        assert d_t > 0, "Distance for line partition must be greater than 0."
        pi = self.__compute_pi(d_t)

        points = list()
        for point in pi:
            if np.linalg.norm(point.v - x_i.v) <= (2 * delta):
                points.append(point)

        return points

    def __compute_pi(self, d_t):
        # https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
        pi = list()
        pi.append(self.p1)
        curr_t = t = d_t / self.d

        while curr_t < 1:
            pi.append(Point2D(
                (1 - curr_t) * self.p1.x + (curr_t * self.p2.x),
                (1 - curr_t) * self.p1.y + (curr_t * self.p2.y)
            ))

            curr_t += t

        pi.append(self.p2)
        return pi


class CurveRangeTree2D(Tree):
    def __init__(self, curve, error, delta):
        super(CurveRangeTree2D, self).__init__(self.__build_tree(curve))
        self.__error = error
        self.__delta = delta

    class Node(object):
        def __init__(self, curve, error, parent=None):
            self.parent = parent
            self.curve = curve
            self.left = None
            self.right = None
            self.grid = FrechetGrid2D(curve, error)
            self.gpar = None

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

    def is_approximate(self, q_edge, x, y, x_edge, y_edge):
        pass

    # noinspection PyUnreachableCode
    def __partition_path(self, x, y, x_edge, y_edge):
        # Assumes x located on the left side of the path w.r.t. y
        x_node = self.__find_node(self.root, x_edge)
        y_node = self.__find_node(self.root, y_edge)

        # Assumes tree has already been decomposed
        lca = self.lowest_common_ancestor(x_node, y_node)

        # noinspection PyUnreachableCode
        def __walk_left(node, edge):
            if node.is_leaf():
                yield node
            elif node.curve.is_in_left_curve(edge):
                for n in __walk_left(node.left, edge):
                    yield n

                yield node.right
            elif node.curve.is_in_right_curve(edge):
                for n in __walk_left(node.right, edge):
                    yield n
            else:
                return
                yield

        # noinspection PyUnreachableCode
        def __walk_right(node, edge):
            if node.is_leaf():
                yield node
            elif node.curve.is_in_left_curve(edge):
                for n in __walk_right(node.left, edge):
                    yield n
            elif node.curve.is_in_right_curve(edge):
                for n in __walk_right(node.right, edge):
                    yield n

                yield node.left
            else:
                return
                yield

        subpaths = list()

        if lca.left:
            for node in __walk_left(lca.left, x_edge):
                if node == x_node:
                    node = self.Node(
                        Edge2D(x, node.curve.get_point(1)),
                        self.__error / 2
                    )

                subpaths.append(node)

        if lca.right:
            right_subpaths = list()

            for node in __walk_right(lca.right, y_edge):
                if node == y_node:
                    node = self.Node(
                        Edge2D(node.curve.get_point(0), y),
                        self.__error / 2
                    )

                right_subpaths.append(node)

            subpaths += right_subpaths[::-1]

        return subpaths

    def __build_tree(self, curve, parent=None):
        node = self.Node(curve, self.__error / 2, parent)

        if curve.size() == 2:
            return node

        node.left = self.__build_tree(curve.left_curve, node)
        node.right = self.__build_tree(curve.right_curve, node)
        return node

    def __find_node(self, node, edge):
        if node.is_leaf():
            return node
        elif node.curve.is_in_left_curve(edge):
            return self.__find_node(node.left, edge)
        elif node.curve.is_in_right_curve(edge):
            return self.__find_node(node.right, edge)
        else:
            return None

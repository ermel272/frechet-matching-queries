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

    def __partition_path(self, x, y, x_edge, y_edge):
        x_node = self.__find_node(self.root, x_edge)
        y_node = self.__find_node(self.root, y_edge)

        # Assumes tree has already been decomposed
        lca = self.lowest_common_ancestor(x_node, y_node)

        # TODO: Walk down separate paths, reporting nodes in partition

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

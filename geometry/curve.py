from __future__ import division

from math import floor

import numpy as np

from geometry.point import Point2D


class PolygonalCurve2D(object):
    def __init__(self, points):
        assert len(points) >= 2, 'Need at least 2 points to define a polygonal curve.'
        self.points = points

    def add_point(self, point):
        return self.points.append(point)

    def get_point(self, i):
        return self.points[i] if i < len(self.points) else None

    def get_spine(self):
        return self.points[0], self.points[-1]

    def size(self):
        return len(self.points)

    def left_curve(self):
        median = int(floor(self.size() / 2))
        return PolygonalCurve2D(self.points[:median + 1]) if self.size() > 2 else self

    def right_curve(self):
        median = int(floor(self.size() / 2))
        return PolygonalCurve2D(self.points[median:]) if self.size() > 2 else self

    def contains(self, edge):
        p1 = self.points[0]

        for point in self.points[1:]:
            p2 = point
            if edge.get_point(0) == p1 and edge.get_point(1) == p2:
                return True
            p1 = p2

        return False

    def is_in_left_curve(self, edge):
        return self.left_curve().contains(edge)

    def is_in_right_curve(self, edge):
        return self.right_curve().contains(edge)

    def sub_divide(self, d_t):
        assert d_t > 0, "Distance for line partition must be greater than 0."
        pi = list()
        p1 = self.points[0]

        for point in self.points[1:]:
            p2 = point
            pi += Edge2D(p1, p2).sub_divide(d_t)
            p1 = p2

        return pi

    def get_steiner_curve(self, d_t):
        return PolygonalCurve2D(self.sub_divide(d_t))


class Edge2D(PolygonalCurve2D):
    def __init__(self, p1, p2):
        super(Edge2D, self).__init__([p1, p2])
        assert p1 != p2, 'An edge cannot be defined by the same two points'
        self.p1 = p1
        self.p2 = p2

        # Although this is a line segment, define some line properties
        slope_den = (self.p1.x - self.p2.x)
        self.slope = (self.p1.y - self.p2.y) / slope_den if slope_den != 0 else 0
        self.y_int = self.p1.y - (self.slope * self.p1.x)
        self.d = np.linalg.norm(self.p1.v - self.p2.v)

    @staticmethod
    def partition(pi, x_i, delta):
        points = list()
        for point in pi:
            if np.linalg.norm(point.v - x_i.v) <= delta:
                points.append(point)

        return points

    def sub_divide(self, d_t):
        assert d_t > 0, "Distance for line partition must be greater than 0."
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

    def get_steiner_edge(self, d_t):
        return PolygonalCurve2D(self.sub_divide(d_t))

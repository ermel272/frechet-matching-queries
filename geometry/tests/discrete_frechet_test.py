import unittest
from random import randint

import numpy as np

from geometry.curve import PolygonalCurve2D, Edge2D
from geometry.frechet_distance import discrete_frechet
from geometry.point import Point2D


class TestDiscreteFrechet(unittest.TestCase):
    def test_symmetric_curves(self):
        c1 = PolygonalCurve2D([
            Point2D(0.0, 1.0),
            Point2D(3.0, 2.0),
            Point2D(5.0, 2.0),
            Point2D(7.0, 1.0)
        ])

        c2 = PolygonalCurve2D([
            Point2D(0.0, 0.0),
            Point2D(3.0, 1.0),
            Point2D(5.0, 1.0),
            Point2D(7.0, 0.0)
        ])

        self.perform_test(c1, c2, 1.0)

    def test_asymmetric_curves(self):
        c1 = PolygonalCurve2D([
            Point2D(-5.0, 1.0),
            Point2D(-4.0, 4.0),
            Point2D(-2.0, -1.0)
        ])

        c2 = PolygonalCurve2D([
            Point2D(-6.0, 0.0),
            Point2D(-3.0, -2.0),
            Point2D(-2.0, 1.0)
        ])

        self.perform_test(c1, c2, 6.08)

    @staticmethod
    def perform_test(c1, c2, dist):
        frechet = discrete_frechet(c1, c2)
        assert round(frechet, 2) == dist

    def test_edge_property(self):
        """
        Small experimental test to verify whether the Frechet Distance
        between any two edges is defined my the maximum distance between
        both pairs of endpoints.
        """
        spacing = 0.5
        fixed = Edge2D(Point2D(0.0, 0.0), Point2D(0.0, 1.0)).get_steiner_edge(spacing)
        u, v = fixed.get_spine()

        def almost_equal(estimate, real):
            return real + 1 >= estimate >= real - 1

        for i in range(0, 10000):
            p1 = Point2D(float(randint(-20, 20)), float(randint(-20, 20)))
            p2 = Point2D(float(randint(-20, 20)), float(randint(-20, 20)))

            # Ensure points aren't the same
            if p1 == p2:
                p2 = Point2D(p2.x + 0.1, p2.y)

            rand_edge = Edge2D(p1, p2).get_steiner_edge(spacing)
            x, y = rand_edge.get_spine()
            r = min(
                max(np.linalg.norm(x.v - u.v), np.linalg.norm(y.v - v.v)),
                max(np.linalg.norm(y.v - u.v), np.linalg.norm(x.v - v.v))
            )
            frechet_estimate = discrete_frechet(fixed, rand_edge)

            assert almost_equal(r, frechet_estimate)


if __name__ == '__main__':
    unittest.main()

import unittest

from geometry.curve import PolygonalCurve2D
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


if __name__ == '__main__':
    unittest.main()

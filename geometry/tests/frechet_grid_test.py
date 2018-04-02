import unittest

from geometry import STEINER_SPACING
from geometry.curve import PolygonalCurve2D, Edge2D
from geometry.frechet_distance import discrete_frechet
from geometry.frechet_grid import FrechetGrid2D
from geometry.point import Point2D


class TestFrechetGrid(unittest.TestCase):

    def setUp(self):
        self.error = 1.0

    def test_curve(self):
        curve = PolygonalCurve2D([
            Point2D(-5.0, 1.0),
            Point2D(-4.0, 4.0),
            Point2D(-2.0, -1.0)
        ])
        e = Edge2D(Point2D(-20.0, -22.0), Point2D(5.0, 5.0))
        grid = FrechetGrid2D(curve, self.error)

        real = discrete_frechet(
            e.get_steiner_curve(STEINER_SPACING),
            curve.get_steiner_curve(STEINER_SPACING))
        estimate = grid.approximate_frechet(e)

        # Test for (1 + epsilon) property of grid estimate
        assert estimate <= real or \
            real <= (1 + self.error) * estimate

    def test_edge(self):
        curve = Edge2D(
            Point2D(-5.0, 1.0),
            Point2D(-4.0, 4.0)
        )
        e = Edge2D(Point2D(-3.0, 1.0), Point2D(-3.0, 3.0))
        grid = FrechetGrid2D(curve, self.error)

        real = discrete_frechet(
            e.get_steiner_curve(STEINER_SPACING),
            curve.get_steiner_curve(STEINER_SPACING))
        estimate = grid.approximate_frechet(e)

        # Test for (1 + epsilon) property of grid estimate
        assert estimate <= real or \
            real <= (1 + self.error) * estimate

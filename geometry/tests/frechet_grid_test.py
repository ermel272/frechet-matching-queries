import unittest

from geometry.curve import PolygonalCurve2D
from geometry.frechet_grid import FrechetGrid2D
from geometry.point import Point2D


class TestFrechetGrid(unittest.TestCase):

    def test_init(self):
        curve = PolygonalCurve2D([
            Point2D(-5.0, 1.0),
            Point2D(-4.0, 4.0),
            Point2D(-2.0, -1.0)
        ])
        grid = FrechetGrid2D(curve, 0.3)

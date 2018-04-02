import unittest

from geometry.curve import PolygonalCurve2D
from geometry.point import Point2D
from geometry.tree import CurveRangeTree2D


class TestCurveRangeTree(unittest.TestCase):

    def setUp(self):
        self.error = 1.0
        self.delta = 15.0

    def test_init(self):
        curve = PolygonalCurve2D([
            Point2D(-5.0, 1.0),
            Point2D(-4.0, 4.0),
            Point2D(-2.0, -1.0)
        ])
        tree = CurveRangeTree2D(curve, self.error, self.delta)

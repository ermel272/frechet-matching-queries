import unittest

from geometry.curve import PolygonalCurve2D, Edge2D
from geometry.point import Point2D
from geometry.tree import CurveRangeTree2D


class TestCurveRangeTree(unittest.TestCase):

    def setUp(self):
        self.error = 1.0
        self.delta = 1.0

    def test_query_small_curve(self):
        tree = CurveRangeTree2D(
            PolygonalCurve2D([
                Point2D(0.0, 0.0),
                Point2D(3.0, 0.0),
                Point2D(3.0, 3.0)
            ])
            , self.error, self.delta)

        # Create query parameters
        q_edge = Edge2D(Point2D(0.0, -1.0), Point2D(3.0, -1.0))
        x = Point2D(0.25, 0.0)
        x_edge = Edge2D(Point2D(0.0, 0.0), Point2D(3.0, 0.0))
        y = Point2D(3.0, 2.5)
        y_edge = Edge2D(Point2D(3.0, 0.0), Point2D(3.0, 3.0))

        assert tree.is_approximate(q_edge, x, y, x_edge, y_edge)

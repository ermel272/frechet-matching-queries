import unittest

from geometry.data_structures.graph import DirectedAcyclicGraph
from geometry.data_structures.point import Point2D


class TestCurveRangeTree(unittest.TestCase):

    def test_bottleneck_weight_easy_dag(self):
        dag = DirectedAcyclicGraph()

        p1 = Point2D(0, 0)
        p2 = Point2D(1, 0)
        p3 = Point2D(2, 0)

        dag.add_edge(p1, p2, 1)
        dag.add_edge(p2, p3, 2)

        assert dag.bottleneck_path_weight(p1, p3) == 2

    def test_bottleneck_weight_hard_dag(self):
        dag = DirectedAcyclicGraph()

        p1 = Point2D(0, 0)
        p2 = Point2D(1, 0)
        p3 = Point2D(2, 0)
        p4 = Point2D(3, 0)
        p5 = Point2D(1, -1)
        p6 = Point2D(2, -1)

        dag.add_edge(p1, p2, 1)
        dag.add_edge(p2, p3, 2)
        dag.add_edge(p3, p4, 1)
        dag.add_edge(p2, p6, 3)
        dag.add_edge(p1, p5, 2)
        dag.add_edge(p5, p6, 5)
        dag.add_edge(p6, p4, 6)

        assert dag.bottleneck_path_weight(p1, p4) == 2

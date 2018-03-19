from __future__ import division
import unittest

import numpy as np

from geometry.exponential_grid import ExponentialGrid2D
from geometry.point import Point2D


class TestExponentialGrid(unittest.TestCase):
    def setUp(self):
        self.error = 0.05

    def test_approximation(self):
        u = Point2D(0.0, 0.0)
        grid = ExponentialGrid2D(u, self.error, 1.0, 20.0)
        p = Point2D(1.0, 18.0)
        p_prime = grid.approximate_point(p)

        # Test for error property
        assert np.linalg.norm(p.v - p_prime.v) <= \
            (self.error / 2) * np.linalg.norm(p.v - u.v)


if __name__ == '__main__':
    unittest.main()

from __future__ import division
import numpy as np

from geometry import STEINER_SPACING
from geometry.curve import Edge2D
from geometry.exponential_grid import ExponentialGrid2D
from geometry.frechet_distance import discrete_frechet


class FrechetGrid2D(object):
    """
    Implements the data structure described in Lemma 4.2.4 of
    Realistic Analysis for Algorithmic Problems on Geographical Data by Anne Driemel.

    The data structure computes the exponential grids G(u) and G(v) of the spine of the
    curve uv and, for each segment in G(u) x G(v), pre-computes the Frechet distance between
    that segment and the given curve. This allows for (1 + error)-approximate Frechet matching
    queries to execute in O(1) time.

    Note that construction of the data structure takes O(X ** 2 * n * log(n)) time, where
    X = error ** -2 * log(1 / error).

    Implementation note: Although in the paper's analysis the pre-processing
    time is O(X ** 2 * n * log(n)), the current implementation actually pre-processes in
    O(X ** 2 * n) time. This is because the analysis relies on a result from Computing
    the Frechet Distance Between Two Polygonal Curves by Helmut Alt and Michael Godau that shows
    it is possible in O(n * log(n)) time to compute the continuous Frechet distance between a line
    segment and a curve with n segments. The implementation, however, relies on parametric searching
    and therefore lends itself to high constant values. We therefore save time in place of accuracy
    by computing the Discrete Frechet distance in O(n) time.
    """

    def __init__(self, curve, error):
        assert 0 < error <= 1, 'Error rate specified must be greater than 0 and at most 1.'
        self.__u, self.__v = curve.get_spine()
        self.__steiner_curve = curve.get_steiner_curve(STEINER_SPACING)
        self.__L = self.__init_L(curve)
        self.__error = error
        self.grid_u = ExponentialGrid2D(self.__u, error, error * self.__L / 2, self.__L / error)
        self.grid_v = ExponentialGrid2D(self.__v, error, error * self.__L / 2, self.__L / error)
        self.distances = self.__init_distances(curve)

    def approximate_frechet(self, edge):
        p = edge.p1
        q = edge.p2

        r = max(np.linalg.norm(p.v - self.__u.v), np.linalg.norm(q.v - self.__v.v))

        if r <= self.__error * self.__L / 2:
            return self.__L - r
        elif r >= self.__L / self.__error:
            return r

        p_prime = self.grid_u.approximate_point(p)
        q_prime = self.grid_v.approximate_point(q)

        return self.distances[str(p_prime)][str(q_prime)] - \
            max(np.linalg.norm(p.v - p_prime.v), np.linalg.norm(q.v - q_prime.v))

    def __init_L(self, curve):
        distance = discrete_frechet(Edge2D(self.__u, self.__v).get_steiner_curve(STEINER_SPACING),
                                    curve.get_steiner_curve(STEINER_SPACING))

        return 1 if distance == 0 else distance

    def __init_distances(self, curve):
        distances = dict()

        for p_prime in self.grid_u.points:
            distances[str(p_prime)] = dict()

            for q_prime in self.grid_v.points:
                distances[str(p_prime)][str(q_prime)] = \
                    discrete_frechet(Edge2D(p_prime, q_prime).get_steiner_curve(STEINER_SPACING),
                                     curve.get_steiner_curve(STEINER_SPACING))

        return distances

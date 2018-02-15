from __future__ import division
import numpy as np
from math import ceil, log, sqrt

from geometry.point import Point2D


class ExponentialGrid2D(object):
    """
    Implements the data structure described in Lemma 4.2.3 of
    Realistic Analysis for Algorithmic Problems on Geographical Data by Anne Driemel.

    The data structure defines an exponential grid centered around a point u and bounded
    by parameters alpha and beta. It supports the following type of query: Given a point
    p such that alpha <= ||p - u|| <= beta, we can retrieve in O(1) time a grid point p'
    such that ||p - p'|| <= (error / 2) * ||p - u||.

    Note that construction of the data structure takes O(error ** -2 * log(beta / alpha)) time.
    """

    def __init__(self, point, error, alpha, beta):
        assert 0 < error <= 1, 'Error rate specified must be greater than 0 and at most 1.'
        self.__alpha = alpha if alpha <= beta else beta
        self.__beta = beta if beta >= alpha else alpha
        self.center = point
        self.hcubes = self.__init_hcubes(point)
        self.grids = self.__init_grids(error)

    def approximate_point(self, point):
        assert self.__alpha <= np.linalg.norm(point.v - self.center.v) <= self.__beta, \
            'Point given falls outside of the grid.'

        # Compute index of grid containing the point
        i = int(max(
            ceil(log(abs(point.x - self.center.x) / self.__alpha) - 1),
            ceil(log(abs(point.y - self.center.y) / self.__alpha) - 1)
        ))

        return self.grids[i].get_cell(point).find_closest(point)

    def points(self):
        for grid in self.grids:
            for point in grid.points():
                yield point

    def __init_hcubes(self, point):
        hcubes = list()

        for i in range(0, int(ceil(log(self.__beta / self.__alpha, 2)))):
            hcubes.append(HyperCube2D(2 ** (i + 2) * self.__alpha, point))

        return hcubes

    def __init_grids(self, error):
        grids = list()

        for hcube in self.hcubes:
            cell_width = (error * hcube.sidelength) / (4 * sqrt(2))
            grids.append(Grid2D(hcube, cell_width))

        return grids


class HyperCube2D(object):
    def __init__(self, sidelength, point):
        half_sl = sidelength / 2
        self.tl = Point2D(point.x - half_sl, point.y - half_sl)
        self.tr = Point2D(point.x + half_sl, point.y - half_sl)
        self.bl = Point2D(point.x - half_sl, point.y + half_sl)
        self.br = Point2D(point.x + half_sl, point.y + half_sl)
        self.sidelength = sidelength


class Grid2D(object):
    def __init__(self, hcube, cell_width):
        self.cell_width = cell_width
        self.grid = self.__init_grid(hcube, cell_width)

    def get_cell(self, point):
        return self.grid[
            int(ceil(point.y / self.cell_width - 1))
        ][
            int(ceil(point.x / self.cell_width - 1))
        ]

    def points(self):
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                yield self.grid[i][j].points

    @staticmethod
    def __init_grid(hcube, cell_width):
        grid = list()

        num_cells = int(ceil(hcube.sidelength / cell_width))
        assert num_cells > 0, 'Invalid hypercube side length and grid cell width specified.'

        last = hcube.tl
        for i in range(0, num_cells):
            grid.append(list())

            for j in range(0, num_cells):
                grid[i].append(Grid2D.__GridCell2D(cell_width, last))
                last = grid[i][j].tr

            last = grid[i][0].bl

        return grid

    class __GridCell2D(object):
        def __init__(self, sidelength, tl_point):
            self.points = [
                tl_point,
                Point2D(tl_point.x + sidelength, tl_point.y),
                Point2D(tl_point.x, tl_point.y + sidelength),
                Point2D(tl_point.x + sidelength, tl_point.y + sidelength)
            ]

        def find_closest(self, point):
            closest = self.points[0]
            min_dist = np.linalg.norm(point.v - closest.v)

            for p in self.points[1:]:
                dist = np.linalg.norm(point.v - p.v)

                if dist < min_dist:
                    closest = p
                    min_dist - dist

            return closest

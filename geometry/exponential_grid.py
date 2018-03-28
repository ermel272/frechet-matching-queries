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
        self.grids, self.points = self.__init_grids(error)

    def approximate_point(self, point):
        assert self.__alpha <= np.linalg.norm(point.v - self.center.v) <= self.__beta, \
            'Point given falls outside of the grid.'

        # Compute index of grid containing the point
        i = int(max(
            ceil(log(abs(point.x - self.center.x) / self.__alpha, 2) - 1),
            ceil(log(abs(point.y - self.center.y) / self.__alpha, 2) - 1)
        ))

        # FIXME: Logarithm error when point.x/y == self.center.x/y

        return self.grids[i].get_cell(point).find_closest(point)

    def points_iter(self):
        for grid in self.grids:
            for point in grid.points:
                yield point

    def __init_hcubes(self, point):
        hcubes = list()

        for i in range(0, int(ceil(log(self.__beta / self.__alpha, 2)))):
            hcubes.append(HyperCube2D(2 ** (i + 2) * self.__alpha, point))

        return hcubes

    def __init_grids(self, error):
        grids = list()
        points = list()
        last_hcube = None

        hcubes = self.__init_hcubes(self.center)
        for hcube in hcubes:
            cell_width = (error * hcube.sidelength) / (4 * sqrt(2))
            grids.append(Grid2D(hcube, cell_width, last_hcube))
            points += [pt for pt in grids[-1].points]
            last_hcube = hcube

        return grids, np.array(points)


class HyperCube2D(object):
    def __init__(self, sidelength, point):
        half_sl = sidelength / 2
        self.tl = Point2D(point.x - half_sl, point.y - half_sl)
        self.tr = Point2D(point.x + half_sl, point.y - half_sl)
        self.bl = Point2D(point.x - half_sl, point.y + half_sl)
        self.br = Point2D(point.x + half_sl, point.y + half_sl)
        self.sidelength = sidelength


class Grid2D(object):
    def __init__(self, hcube, cell_width, last_hcube=None):
        self.tl = hcube.tl
        self.cell_width = cell_width
        self.grid, self.points = self.__init_grid(hcube, cell_width, last_hcube)

    def get_cell(self, point):
        return self.grid[
            int(ceil(abs(self.tl.y - point.y) / self.cell_width) - 1)
        ][
            int(ceil(abs(self.tl.x - point.x) / self.cell_width) - 1)
        ]

    def points_iter(self):
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if self.grid[i][j]:
                    for point in self.grid[i][j].points:
                        yield point

    @staticmethod
    def __init_grid(hcube, cell_width, last_hcube):
        grid = list()
        points = set()

        num_cells = int(ceil(hcube.sidelength / cell_width))
        assert num_cells > 0, 'Invalid hypercube side length and grid cell width specified.'

        last = hcube.tl
        for i in range(0, num_cells):
            grid.append(list())

            for j in range(0, num_cells):
                new_cell = Grid2D.__GridCell2D(cell_width, last)

                if last_hcube and new_cell.is_in(last_hcube):
                    grid[i].append(None)
                else:
                    grid[i].append(new_cell)

                    # Add cell points to the grid's point set
                    points.add(new_cell.tl)
                    points.add(new_cell.tr)
                    points.add(new_cell.bl)
                    points.add(new_cell.br)

                last = new_cell.tr

            last = grid[i][0].bl

        return grid, np.array(list(points))

    class __GridCell2D(object):
        def __init__(self, sidelength, tl_point):
            self.tl = tl_point
            self.tr = Point2D(tl_point.x + sidelength, tl_point.y)
            self.bl = Point2D(tl_point.x, tl_point.y + sidelength)
            self.br = Point2D(tl_point.x + sidelength, tl_point.y + sidelength)
            self.points = [
                self.tl,
                self.tr,
                self.bl,
                self.br
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

        def is_in(self, hcube):
            if hcube.tl.x <= self.tl.x <= self.tr.x <= hcube.tr.x and \
                    hcube.tl.y <= self.tl.y <= self.bl.y <= hcube.bl.y:
                return True

            return False

import numpy as np


def discrete_frechet(p, q):
    """
    Implements the algorithm described in Table 1 of Computing the
    Discrete Frechet Distance by Thomas Eiter and Heikki Mannila.

    Computes the discrete Frechet distance between polygonal curves p and q
    in O(|p| * |q|) time, where |x| denotes the number of vertices in a
    polygonal curve.
    """
    ca = [[-1.0 for _ in range(0, q.size())] for _ in range(0, p.size())]

    def distance(p1, p2):
        return np.linalg.norm(p1.v - p2.v)

    def __c(i, j):
        if ca[i][j] > -1.0:
            return ca[i][j]

        elif i == 1 and j == 1:
            ca[i][j] = distance(p.get_point(1), q.get_point(1))

        elif i > 1 and j == 1:
            ca[i][j] = max(
                __c(i - 1, 1),
                distance(p.get_point(i), q.get_point(1))
            )

        elif i == 1 and j > 1:
            ca[i][j] = max(
                __c(1, j - 1),
                distance(p.get_point(1), q.get_point(j))
            )

        elif i > 1 and j > 1:
            ca[i][j] = max(
                min(
                    __c(i - 1, j),
                    __c(i - 1, j - 1),
                    __c(i, j - 1)
                ),
                distance(p.get_point(i), q.get_point(j))
            )

        else:
            ca[i][j] = float('inf')

        return ca[i][j]

    return __c(p.size() - 1, q.size() - 1)

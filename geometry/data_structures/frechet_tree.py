from geometry.data_structures.curve import Edge2D, PolygonalCurve2D
from geometry.data_structures.curve_range_tree import CurveRangeTree2D


class FrechetTree(object):
    """
    Attempts to implement the data structure described in Lemma 4 of Fast Algorithms for Approximate Frechet
    Matching Queries in Geometric Trees by Michiel Smid and Joachim Gudmundsson.

    This implementation does not yet work.

    The data structure decomposes an input geometric tree T a collection of paths, building Curve Range Trees
    for each path in the decomposition. The data structure supports the following type of query:
    Given a query line segment Q and two points x and y on T along with the edges of T containing x and y,
    we return in O((log ** 2 (n)) / error ** 2) time whether or not the Frechet Distance from Q to T[x, y] is at most
    (1 + error) * delta, for some predetermined constant delta. Note that T[x, y] denotes the subpath of T from
    x to y.

    Note that construction of the data structure takes O((1 / error ** 4) * log ** 2 (n / error) * log ** 2 (n)) time.
    """

    def __init__(self, tree, error, delta):
        self.__error = error
        self.__delta = delta
        self.tree = tree
        self.path_trees = dict()

        self.tree.decompose(embedded_nodes=True)
        for path in self.tree.decomposition:
            self.path_trees[str(path)] = CurveRangeTree2D(path, error, delta)

    def is_approximate(self, q_edge, x, y, x_node, y_node):
        # Assume tree node data stores Point2D objects
        x_edge = Edge2D(x_node.point, x_node.parent.point)
        y_edge = Edge2D(y_node.point, y_node.parent.point)

        lca = self.tree.lowest_common_ancestor(x_node, y_node)
        paths = self.__find_decomposed_curves(x_node, lca) + self.__find_decomposed_curves(y_node, lca)[::-1]

        subpaths = list()
        for i in range(0, len(paths)):
            path = paths[i]
            curve_tree = self.path_trees.get(str(path))

            end = path.get_point(-1)
            if i == 0:
                subpaths += curve_tree.partition_path(x, end, x_edge, Edge2D(path.get_point(-2), end))
            elif i == len(paths) - 1:
                subpaths += curve_tree.partition_path(y, end, y_edge, Edge2D(path.get_point(-2), end))
            else:
                start = path.get_point(0)
                subpaths += curve_tree.partition_path(start, end,
                                                      Edge2D(start, path.get_point(1)), Edge2D(path.get_point(-2), end))

        return self.path_trees.values()[0].find_frechet_bottleneck(q_edge, subpaths)

    @staticmethod
    def __find_decomposed_curves(start, end):
        paths = list()

        searching = True
        stack = list()
        prev = None
        curr = start
        while searching:
            if curr == end:
                searching = False

            stack.append(curr)

            if prev and prev.gpar == curr:
                paths.append(PolygonalCurve2D([n.point for n in stack]))
                stack = [curr]

            prev = curr
            curr = curr.parent

        return paths

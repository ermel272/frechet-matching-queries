from geometry.data_structures.curve import Edge2D
from geometry.data_structures.frechet_grid import FrechetGrid2D
from geometry.data_structures.graph import DirectedAcyclicGraph
from geometry.data_structures.tree import Tree


class CurveRangeTree2D(Tree):
    """
    Implements the data structure described in Lemma 2 of Fast Algorithms for Approximate Frechet
    Matching Queries in Geometric Trees by Michiel Smid and Joachim Gudmundsson.

    The data structure decomposes an input polygonal curve P into a binary tree, building Frechet Grids
    at each node for the subpath stored there. The data structure supports the following type of query:
    Given a query line segment Q and two points x and y on P along with the edges of P containing x and y,
    we return in O((log n) / error ** 2) time whether or not the Frechet Distance from Q to P[x, y] is at most
    (1 + error) * delta, for some predetermined constant delta. Note that P[x, y] denotes the subpath of P from
    x to y.

    Note that construction of the data structure takes O((1 / error ** 4) * log ** 2 (n / error) * log ** 2 (n)) time.
    """

    def __init__(self, curve, error, delta):
        self.__error = error
        self.__delta = delta
        super(CurveRangeTree2D, self).__init__(self.__build_tree(curve))
        self.decompose()

    class Node(object):
        def __init__(self, curve, error, parent=None):
            self.parent = parent
            self.curve = curve
            self.left = None
            self.right = None
            self.grid = FrechetGrid2D(curve, error)
            self.gpar = None
            self.point = None

        def is_leaf(self):
            return True if not (self.left or self.right) else False

        # noinspection PyUnreachableCode
        def adjacent_nodes(self):
            if self.parent:
                yield self.parent

            for child in self.children():
                yield child

            return
            yield

        # noinspection PyUnreachableCode
        def children(self):
            if self.left:
                yield self.left

            if self.right:
                yield self.right

            return
            yield

    def is_approximate(self, q_edge, x, y, x_edge, y_edge):
        # Step 1: Partition path in O(log n) subpaths
        subpaths = self.partition_path(x, y, x_edge, y_edge)

        # Refactored for reusability
        return self.find_frechet_bottleneck(q_edge, subpaths)

    def find_frechet_bottleneck(self, q_edge, subpaths):
        # Step 2: Partition q_edge and compute partitioning point sets
        partitions = list()
        pi = q_edge.sub_divide(self.__error * self.__delta / 3)
        for subpath in subpaths[1:]:
            dag_points = Edge2D.partition(
                pi,
                subpath.curve.get_point(0),
                2 * self.__delta
            )

            if len(dag_points) > 0:
                partitions.append(dag_points)

        # Step 3: Construct the Directed Acyclic Graph
        dag = DirectedAcyclicGraph()
        for i in range(0, len(partitions) - 1):
            j = i + 1

            for u in partitions[i]:
                for v in partitions[j]:
                    if u == v:
                        continue
                    elif u != q_edge.p2 and v.is_on_edge(Edge2D(u, q_edge.p2)):
                        dag.add_edge(u, v, subpaths[i + 1].grid.approximate_frechet(Edge2D(u, v)))

        if len(partitions) > 0:
            for v in partitions[0]:
                if v == q_edge.p1:
                    continue
                dag.add_edge(q_edge.p1, v, subpaths[0].grid.approximate_frechet(Edge2D(q_edge.p1, v)))

            for u in partitions[len(partitions) - 1]:
                if u == q_edge.p2:
                    continue
                dag.add_edge(u, q_edge.p2, subpaths[len(partitions) - 1].grid.approximate_frechet(Edge2D(u, q_edge.p2)))
        else:
            dag.add_edge(q_edge.p1, q_edge.p2, subpaths[0].grid.approximate_frechet(Edge2D(q_edge.p1, q_edge.p2)))
            dag.add_edge(q_edge.p1, q_edge.p2,
                         subpaths[len(partitions) - 1].grid.approximate_frechet(Edge2D(q_edge.p1, q_edge.p2)))

        # Step 4: Find the heaviest weighted edge on the bottleneck path of the DAG
        delta_prime = dag.bottleneck_path_weight(q_edge.p1, q_edge.p2)
        return delta_prime <= (1 + self.__error) * self.__delta

    # noinspection PyUnreachableCode
    def partition_path(self, x, y, x_edge, y_edge):
        # Assumes x located on the left side of the path w.r.t. y
        x_node = self.__find_node(self.root, x_edge)
        y_node = self.__find_node(self.root, y_edge)

        # Assumes tree has already been decomposed
        lca = self.lowest_common_ancestor(x_node, y_node)

        # noinspection PyUnreachableCode
        def __walk_left(node, edge):
            if node.is_leaf():
                yield node
            elif node.curve.is_in_left_curve(edge):
                for n in __walk_left(node.left, edge):
                    yield n

                yield node.right
            elif node.curve.is_in_right_curve(edge):
                for n in __walk_left(node.right, edge):
                    yield n
            else:
                return
                yield

        # noinspection PyUnreachableCode
        def __walk_right(node, edge):
            if node.is_leaf():
                yield node
            elif node.curve.is_in_left_curve(edge):
                for n in __walk_right(node.left, edge):
                    yield n
            elif node.curve.is_in_right_curve(edge):
                for n in __walk_right(node.right, edge):
                    yield n

                yield node.left
            else:
                return
                yield

        subpaths = list()

        if lca.left:
            for node in __walk_left(lca.left, x_edge):
                if node == x_node:
                    node = self.Node(
                        Edge2D(x, node.curve.get_point(1)),
                        self.__error
                    )

                subpaths.append(node)

        if lca.right:
            right_subpaths = list()

            for node in __walk_right(lca.right, y_edge):
                if node == y_node:
                    node = self.Node(
                        Edge2D(node.curve.get_point(0), y),
                        self.__error
                    )

                right_subpaths.append(node)

            subpaths += right_subpaths[::-1]

        return subpaths

    def __build_tree(self, curve, parent=None):
        # Note: Not passing error / 2 for performance reasons
        node = self.Node(curve, self.__error, parent)

        if curve.size() == 2:
            return node

        node.left = self.__build_tree(curve.left_curve(), node)
        node.right = self.__build_tree(curve.right_curve(), node)
        return node

    def __find_node(self, node, edge):
        if node.is_leaf():
            return node
        elif node.curve.is_in_left_curve(edge):
            return self.__find_node(node.left, edge)
        elif node.curve.is_in_right_curve(edge):
            return self.__find_node(node.right, edge)
        else:
            return None
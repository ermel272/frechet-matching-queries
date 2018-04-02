from math import floor, log

from geometry.curve import PolygonalCurve2D, Edge2D
from geometry.frechet_grid import FrechetGrid2D
from geometry.graph import DirectedAcyclicGraph


class Tree(object):
    def __init__(self, root=None):
        self.root = root
        self.decomposition = None

    class Node(object):
        def __init__(self, data, parent=None):
            self.parent = parent
            self.data = data
            self.left_child = None
            self.right_sibling = None
            self.gpar = None

        def is_leaf(self):
            return True if not self.left_child else False

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
            if self.left_child:
                yield self.left_child

                child = self.left_child.right_sibling
                while child is not None:
                    yield child
                    child = child.right_sibling

            return
            yield

    # noinspection PyUnreachableCode
    @staticmethod
    def depth_first_search(node):
        if not node:
            return
            yield

        stack = list()
        visited = set()

        stack.append(node)
        while len(stack) > 0:
            nxt = stack.pop()

            if nxt not in visited:
                visited.add(nxt)
                yield nxt

                for future_node in nxt.adjacent_nodes():
                    stack.append(future_node)

    # noinspection PyUnreachableCode
    @staticmethod
    def post_order_traversal(node):
        def __iter(n):
            for child in n.children():
                for i in __iter(child):
                    yield i
            yield n

        if node:
            for nd in __iter(node):
                yield nd

        return
        yield

    # noinspection PyUnreachableCode
    def leaves(self, node):
        for n in self.post_order_traversal(node):
            if n.is_leaf():
                yield n

        return
        yield

    def decompose(self):
        curves = list()

        # Step 1: Compute size & magnitude of each subtree
        for node in self.post_order_traversal(self.root):
            if node.is_leaf():
                node.size = 1
            else:
                node.size = sum(n.size for n in node.children())
            node.ell = int(floor(log(node.size, 2)))

        def create_curve(s):
            s.insert(0, s[0].parent)
            curves.append(s)

            for n in s:
                n.gpar = s[0]

        # Step 2: Create tree decomposition while performing DFS
        stack = list()
        last = None
        for node in self.depth_first_search(self.root):
            if node == self.root:
                last = node
                continue
            elif len(stack) > 0 and (node.ell != stack[-1].ell or node.parent != last):
                create_curve(stack)
                stack = list()

            last = node
            stack.append(node)

        # Loop above may terminate without creating the final curve
        if len(stack) > 0:
            create_curve(stack)

        self.decomposition = curves
        return curves

    def lowest_common_ancestor(self, u, v):
        assert u != self.root and v != self.root, 'Input nodes cannot be the root node.'
        assert u != v, 'Input nodes must be distinct'
        assert u.gpar and v.gpar, 'Tree must be decomposed prior to computing LCA.'

        def compute_parent_sequence(node):
            seq = list()
            seq.append(node)
            seq.append(node.gpar)

            while seq[-1].parent is not None:
                seq.append(seq[-1].parent.gpar)

            seq.append(seq[-1])

            return seq

        u_seq = compute_parent_sequence(u)
        v_seq = compute_parent_sequence(v)

        k = 0
        while u_seq[-(1 + k)] == v_seq[-(1 + k)]:
            k += 1

        i = len(u_seq)
        j = len(v_seq)

        if i == j == k:
            return u if u.size >= v.size else v
        elif i != j and k == i:
            return u if u.size >= v_seq[j - 1 - k].parent.size else v
        elif i != j and k == j:
            return v if v.size >= u_seq[i - 1 - k].parent.size else u

        # k != i and k != j:
        return u_seq[i - 1 - k].parent if u_seq[i - 1 - k].parent.size >= v_seq[j - 1 - k].parent.size \
            else v_seq[j - 1 - k].parent


class FrechetTree(object):
    def __init__(self, tree, error, delta):
        self.__error = error
        self.__delta = error
        self.paths = tree.decompose()
        self.path_trees = list()

        for path in self.paths:
            self.path_trees.append(CurveRangeTree2D(path, error, delta))


class CurveRangeTree2D(Tree):
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
        subpaths = self.__partition_path(x, y, x_edge, y_edge)

        # Step 2: Partition q_edge and compute partitioning point sets
        partitions = list()
        pi = q_edge.sub_divide(self.__error * self.__delta / 3)
        for subpath in subpaths[1:]:
            partitions.append(
                q_edge.partition(
                    pi,
                    subpath.curve.get_point(0),
                    2 * self.__delta
                )
            )

        # Construct the Directed Acyclic Graph
        dag = DirectedAcyclicGraph()
        for i in range(0, len(partitions) - 1):
            j = i + 1

            for u in partitions[i]:
                for v in partitions[j]:
                    if v.is_on_edge(Edge2D(u, q_edge.p2)):
                        dag.add_edge(u, v, subpaths[i + 1].grid.approximate_frechet(u, v))

        for v in partitions[0]:
            dag.add_edge(q_edge.p1, v, subpaths[0].grid.approximate_frechet(q_edge.p1, v))

        for u in partitions[len(partitions) - 1]:
            dag.add_edge(u, q_edge.p2, subpaths[len(partitions) - 1].grid.approximate_frechet(u, q_edge.p2))

        delta_prime = dag.bottleneck_path(q_edge.p1, q_edge.p2)
        return delta_prime <= (1 + self.__error) * self.__delta

    # noinspection PyUnreachableCode
    def __partition_path(self, x, y, x_edge, y_edge):
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
                        self.__error / 2
                    )

                subpaths.append(node)

        if lca.right:
            right_subpaths = list()

            for node in __walk_right(lca.right, y_edge):
                if node == y_node:
                    node = self.Node(
                        Edge2D(node.curve.get_point(0), y),
                        self.__error / 2
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

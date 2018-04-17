from math import floor, log

from geometry.data_structures.curve import PolygonalCurve2D


class Tree(object):
    def __init__(self, root=None):
        self.root = root
        self.decomposition = None

    class Node(object):
        def __init__(self, point, parent=None):
            self.parent = parent
            self.point = point
            self.left_child = None
            self.right_sibling = None
            self.gpar = None
            self.decomp_curves = list()

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

    def decompose(self, embedded_nodes=False):
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

            if embedded_nodes:
                curve = PolygonalCurve2D([n.point for n in s])
                curves.append(curve)

                # Fix a pointer to the curve for each node in the stack
                for n in s:
                    n.decomp_curves.append(curve)
            else:
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

from math import floor, log

from geometry.curve import PolygonalCurve2D


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
            yield nxt

            if nxt not in visited:
                visited.add(nxt)

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

        # Step 2: Create tree decomposition while performing DFS
        stack = list()
        for node in self.depth_first_search(self.root):
            if node == self.root:
                continue
            elif len(stack) > 0 and node.ell != stack[-1].ell:
                stack.insert(0, stack[0].parent)
                curves.append(PolygonalCurve2D(stack))
                stack = list()

            stack.append(node)

        self.decomposition = curves
        return curves

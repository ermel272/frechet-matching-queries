from geometry.data_structures.tree import Tree
from geometry.data_structures.point import Point2D


def create_tree(json):
    root = Tree.Node(Point2D(json['root']['x'], json['root']['x']))

    def create_children(children, parent):
        prev = None
        first = None
        for child in children:
            new = Tree.Node(Point2D(child['x'], child['y']), parent=parent)
            new.left_child = create_children(child['children'], new)

            if prev:
                prev.right_sibling = new
            if not first:
                first = new

            prev = new

        return first

    root.left_child = create_children(json['root']['children'], root)
    return Tree(root=root)

class Graph(object):
    def __init__(self):
        self.graph = dict()

    def add_vertex(self, point):
        if not self.graph.get(str(point)):
            self.graph[str(point)] = self.__AdjacencyContainer()
            return True

        return False

    def add_edge(self, p1, p2):
        self.add_vertex(p1)
        self.graph[str(p1)].add(p2)

    class __AdjacencyContainer(object):
        def __init__(self):
            self.points = list()
            self.point_set = set()

        def add(self, point):
            if point not in self.point_set:
                self.points.append(point)
                self.point_set.add(point)

        def is_in(self, point):
            return point in self.point_set

from point import Point
from edge import Edge


class Graph:
    def __init__(self):
        self.points = []
        self.edges = []

    def add_point(self, x, y):
        point = Point(x, y, len(self.points))
        self.points.append(point)
        return point

    def add_edge(self, source, dest, weight=1.0):
        # Проверяем, существует ли уже такое ребро
        for edge in self.edges:
            if (edge.source == source and edge.dest == dest) or \
                    (edge.source == dest and edge.dest == source):
                return None

        edge = Edge(source, dest, weight)
        self.edges.append(edge)
        source.add_edge(edge)
        dest.add_edge(edge)
        return edge

    def remove_point(self, point):
        for edge in point.edges[:]:
            self.remove_edge(edge)
        self.points.remove(point)

    def remove_edge(self, edge):
        edge.source.remove_edge(edge)
        edge.dest.remove_edge(edge)
        self.edges.remove(edge)

    def prim(self):
        if not self.points:
            return []


        visited = set()
        edges_used = []

        # Обрабатываем все компоненты связности
        for point in self.points:
            if point in visited:
                continue

            # Начинаем с текущей точки, если она еще не посещена
            start_point = point
            visited.add(start_point)

            # Обрабатываем текущую компоненту связности
            while True:
                min_edge = None
                for node in visited:
                    for edge in node.edges:
                        other_node = edge.dest if edge.source == node else edge.source
                        if other_node not in visited:
                            if min_edge is None or edge.weight < min_edge.weight:
                                min_edge = edge

                if min_edge is None:
                    # В текущей компоненте связности больше нет ребер для добавления
                    break

                edges_used.append(min_edge)
                other_node = min_edge.dest if min_edge.source in visited else min_edge.source
                visited.add(other_node)

        return edges_used

    def kruskal(self):
        if not self.points:
            return []


        edges_sorted = sorted(self.edges, key=lambda x: x.weight)
        parent = {point: point for point in self.points}

        def find(point):
            if parent[point] != point:
                parent[point] = find(parent[point])
            return parent[point]

        def union(point1, point2):
            root1 = find(point1)
            root2 = find(point2)
            if root1 != root2:
                parent[root2] = root1
                return True
            return False

        mst_edges = []
        for edge in edges_sorted:
            if union(edge.source, edge.dest):
                mst_edges.append(edge)

        return mst_edges

    def clear(self):
        self.points.clear()
        self.edges.clear()
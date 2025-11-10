import pytest

from point import Point
from edge import Edge
from graph import Graph


class TestPoint:
    def test_point_creation(self):
        point = Point(10, 20, 0)
        assert point.x == 10
        assert point.y == 20
        assert point.index == 0
        assert point.edges == []
    
    def test_point_repr(self):
        point = Point(10, 20, 0)
        repr_str = repr(point)
        assert "Point(0" in repr_str
        assert "x=10" in repr_str
        assert "y=20" in repr_str
    
    def test_add_remove_edge(self):
        point1 = Point(10, 20, 0)
        point2 = Point(30, 40, 1)
        edge = Edge(point1, point2, 1.0)
        
        point1.add_edge(edge)
        assert edge in point1.edges
        
        point1.remove_edge(edge)
        assert edge not in point1.edges


class TestEdge:
    def test_edge_creation(self):
        point1 = Point(10, 20, 0)
        point2 = Point(30, 40, 1)
        edge = Edge(point1, point2, 2.5)
        
        assert edge.source == point1
        assert edge.dest == point2
        assert edge.weight == 2.5
    
    def test_edge_repr(self):
        point1 = Point(10, 20, 0)
        point2 = Point(30, 40, 1)
        edge = Edge(point1, point2, 2.5)
        
        repr_str = repr(edge)
        assert "Ребро(0 - 1" in repr_str
        assert "вес=2.5" in repr_str


class TestGraph:
    def test_graph_creation(self):
        graph = Graph()
        assert graph.points == []
        assert graph.edges == []
    
    def test_add_point(self):
        graph = Graph()
        point = graph.add_point(10, 20)
        
        assert point in graph.points
        assert point.x == 10
        assert point.y == 20
        assert point.index == 0
        
        point2 = graph.add_point(30, 40)
        assert point2 in graph.points
        assert point2.index == 1
    
    def test_add_edge(self):
        graph = Graph()
        point1 = graph.add_point(10, 20)
        point2 = graph.add_point(30, 40)
        
        edge = graph.add_edge(point1, point2, 2.5)
        
        assert edge in graph.edges
        assert edge.source == point1
        assert edge.dest == point2
        assert edge.weight == 2.5
        assert edge in point1.edges
        assert edge in point2.edges
    
    def test_add_duplicate_edge(self):
        graph = Graph()
        point1 = graph.add_point(10, 20)
        point2 = graph.add_point(30, 40)
        
        edge1 = graph.add_edge(point1, point2, 2.5)
        edge2 = graph.add_edge(point1, point2, 3.0)
        
        assert edge2 is None
        assert len(graph.edges) == 1
    
    def test_remove_point(self):
        graph = Graph()
        point1 = graph.add_point(10, 20)
        point2 = graph.add_point(30, 40)
        edge = graph.add_edge(point1, point2, 2.5)
        
        graph.remove_point(point1)
        
        assert point1 not in graph.points
        assert edge not in graph.edges
        assert edge not in point2.edges
    
    def test_remove_edge(self):
        graph = Graph()
        point1 = graph.add_point(10, 20)
        point2 = graph.add_point(30, 40)
        edge = graph.add_edge(point1, point2, 2.5)
        
        graph.remove_edge(edge)
        
        assert edge not in graph.edges
        assert edge not in point1.edges
        assert edge not in point2.edges
    
    def test_clear(self):
        graph = Graph()
        point1 = graph.add_point(10, 20)
        point2 = graph.add_point(30, 40)
        graph.add_edge(point1, point2, 2.5)
        
        graph.clear()
        
        assert graph.points == []
        assert graph.edges == []

    def test_prim_single_component(self):
        graph = Graph()
        points = []
        for i in range(3):
            points.append(graph.add_point(i * 50, i * 50))
        
        graph.add_edge(points[0], points[1], 1.0)
        graph.add_edge(points[1], points[2], 2.0)
        graph.add_edge(points[0], points[2], 3.0)
        
        mst_edges = graph.prim()
        
        assert len(mst_edges) == 2
        
        weights = [edge.weight for edge in mst_edges]
        assert 1.0 in weights
        assert 2.0 in weights
        assert 3.0 not in weights
    
    def test_prim_multiple_components(self):
        graph = Graph()
        
        points_comp1 = [graph.add_point(i * 50, 0) for i in range(2)]
        points_comp2 = [graph.add_point(i * 50, 100) for i in range(2)]
        
        graph.add_edge(points_comp1[0], points_comp1[1], 1.0)
        graph.add_edge(points_comp2[0], points_comp2[1], 1.0)
        
        mst_edges = graph.prim()
        
        assert len(mst_edges) == 2
    
    def test_kruskal_single_component(self):
        graph = Graph()
        
        points = []
        for i in range(3):
            points.append(graph.add_point(i * 50, i * 50))
        
        graph.add_edge(points[0], points[1], 1.0)
        graph.add_edge(points[1], points[2], 2.0)
        graph.add_edge(points[0], points[2], 3.0)
        
        mst_edges = graph.kruskal()
        
        assert len(mst_edges) == 2
        weights = [edge.weight for edge in mst_edges]
        assert 1.0 in weights
        assert 2.0 in weights
        assert 3.0 not in weights
    
    def test_kruskal_multiple_components(self):
        graph = Graph()
        
        points_comp1 = [graph.add_point(i * 50, 0) for i in range(2)]
        points_comp2 = [graph.add_point(i * 50, 100) for i in range(2)]
        
        graph.add_edge(points_comp1[0], points_comp1[1], 1.0)
        graph.add_edge(points_comp2[0], points_comp2[1], 1.0)
        
        mst_edges = graph.kruskal()
        
        assert len(mst_edges) == 2
    
    def test_empty_graph(self):
        graph = Graph()
        
        prim_edges = graph.prim()
        kruskal_edges = graph.kruskal()
        
        assert prim_edges == []
        assert kruskal_edges == []
    
    def test_single_node_graph(self):
        graph = Graph()
        graph.add_point(0, 0)
        
        prim_edges = graph.prim()
        kruskal_edges = graph.kruskal()
        
        assert prim_edges == []
        assert kruskal_edges == []
    
    def test_prim_vs_kruskal(self):
        graph = Graph()
        
        points = [graph.add_point(i * 100, 0) for i in range(4)]
        
        edges = [
            (points[0], points[1], 1.0),
            (points[1], points[2], 2.0),
            (points[2], points[3], 1.0),
            (points[0], points[2], 3.0),
            (points[1], points[3], 4.0)
        ]
        
        for source, dest, weight in edges:
            graph.add_edge(source, dest, weight)
        
        prim_edges = graph.prim()
        kruskal_edges = graph.kruskal()
        
        assert len(prim_edges) == len(kruskal_edges) == 3
        
        prim_weight = sum(edge.weight for edge in prim_edges)
        kruskal_weight = sum(edge.weight for edge in kruskal_edges)
        assert prim_weight == kruskal_weight
        
        assert prim_weight == 4.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
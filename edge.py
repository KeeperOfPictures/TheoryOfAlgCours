from point import Point

class Edge:
    def __init__(self, source: Point, dest: Point, weight=1.0):
        self.source = source
        self.dest = dest
        self.weight = weight
    
    def __repr__(self):
        return f"Ребро({self.source.index} - {self.dest.index}, вес={self.weight})"

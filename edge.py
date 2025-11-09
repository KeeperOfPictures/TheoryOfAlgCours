class Edge:
    def __init__(self, source, dest, weight=1.0):
        self.source = source
        self.dest = dest
        self.weight = weight
    
    def __repr__(self):
        return f"Edge({self.source.index} -> {self.dest.index}, weight={self.weight})"
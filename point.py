class Point:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index
        self.edges = []
        
    def add_edge(self, edge):
        self.edges.append(edge)
    
    def remove_edge(self, edge):
        self.edges.remove(edge)
    
    def __repr__(self):
        return f"Point({self.index}, x={self.x}, y={self.y})"
import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from graphics_items import *

class GraphicsScene(QGraphicsScene):
    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.mode = "выбрать"
        self.temp_edge = None
        self.temp_weight_input = None
        self.current_algorithm = None
        self.drag_node = None
        self.is_dragging_edge = False
        
        self.node_items = {}
        self.edge_items = {}

    def set_mode(self, mode):
        self.mode = mode
        
        if mode == "удалить":
            for node in self.node_items.values():
                node.setFlag(QGraphicsItem.ItemIsMovable, False)
        else:
            for node in self.node_items.values():
                node.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        
        if event.button() == Qt.LeftButton:
            if self.mode == "добавить_ноду":
                point = self.graph.add_point(pos.x(), pos.y())
                if point:
                    self.add_node(point)
                event.accept()
                return
            elif self.mode == "добавить_ребро":
                node = self.find_node_at(pos)
                if node:
                    self.start_edge(node)
                    event.accept()
                    return
            elif self.mode == "удалить":
                item = self.itemAt(pos, QTransform())
                if isinstance(item, Node):
                    self.remove_node(item)
                    event.accept()
                    return
                elif isinstance(item, GraphicsEdge):
                    self.remove_edge(item)
                    event.accept()
                    return
                elif isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), GraphicsEdge):
                    self.remove_edge(item.parentItem())
                    event.accept()
                    return
        
        super().mousePressEvent(event)

    def find_node_at(self, pos):
        for node in self.node_items.values():
            node_center = node.pos()
            distance = math.sqrt((node_center.x() - pos.x())**2 + (node_center.y() - pos.y())**2)
            if distance <= 20:
                return node
        return None

    def add_node(self, point):
        node = Node(point)
        self.node_items[point] = node
        self.addItem(node)
        
        if self.mode == "удалить":
            node.setFlag(QGraphicsItem.ItemIsMovable, False)

    def add_edge(self, edge):
        graphics_edge = GraphicsEdge(edge)
        self.edge_items[edge] = graphics_edge
        self.addItem(graphics_edge)

    def start_edge(self, node):
        self.drag_node = node
        self.is_dragging_edge = True
        
        for n in self.node_items.values():
            n.setFlag(QGraphicsItem.ItemIsMovable, False)
        
        self.temp_edge = QGraphicsLineItem(QLineF(node.pos(), node.pos()))
        self.temp_edge.setPen(QPen(Qt.gray, 2, Qt.DashLine))
        self.addItem(self.temp_edge)
        
        self.temp_weight_input = QGraphicsTextItem()
        self.temp_weight_input.setPlainText("1.0")
        self.temp_weight_input.setDefaultTextColor(Qt.blue)
        self.temp_weight_input.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.temp_weight_input.setFlag(QGraphicsItem.ItemIsFocusable)
        self.addItem(self.temp_weight_input)
        self.update_temp_weight_pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging_edge and self.temp_edge:
            pos = event.scenePos()
            self.temp_edge.setLine(QLineF(self.drag_node.pos(), pos))
            self.update_temp_weight_pos()
        
        super().mouseMoveEvent(event)

    def update_temp_weight_pos(self):
        if self.temp_edge and self.temp_weight_input:
            line = self.temp_edge.line()
            center = line.pointAt(0.5)
            self.temp_weight_input.setPos(center.x() - 15, center.y() - 10)

    def mouseReleaseEvent(self, event):
        if self.is_dragging_edge and event.button() == Qt.LeftButton:
            pos = event.scenePos()
            target_node = self.find_node_at(pos)
            
            if target_node and target_node != self.drag_node:
                try:
                    weight = float(self.temp_weight_input.toPlainText())
                except ValueError:
                    weight = 1.0
                
                edge = self.graph.add_edge(self.drag_node.point, target_node.point, weight)
                if edge:
                    self.add_edge(edge)
            
            if self.mode != "удалить":
                for node in self.node_items.values():
                    node.setFlag(QGraphicsItem.ItemIsMovable, True)
            
            self.cleanup_temp_items()
        
        super().mouseReleaseEvent(event)
    
    def cleanup_temp_items(self):
        if self.temp_edge:
            self.removeItem(self.temp_edge)
            self.temp_edge = None
            
        if self.temp_weight_input:
            self.removeItem(self.temp_weight_input)
            self.temp_weight_input = None
            
        self.drag_node = None
        self.is_dragging_edge = False

    def remove_node(self, node):
        edges_to_remove = []
        for edge, graphics_edge in self.edge_items.items():
            if edge.source == node.point or edge.dest == node.point:
                edges_to_remove.append(graphics_edge)
        
        for graphics_edge in edges_to_remove:
            self.remove_edge(graphics_edge)
        
        self.graph.remove_point(node.point)
        self.removeItem(node)
        if node.point in self.node_items:
            del self.node_items[node.point]

    def remove_edge(self, graphics_edge):
        self.graph.remove_edge(graphics_edge.edge)
        self.removeItem(graphics_edge)
        if graphics_edge.edge in self.edge_items:
            del self.edge_items[graphics_edge.edge]

    def run_algorithm(self):
        if self.current_algorithm == "прим":
            mst_edges = self.graph.prim()
        elif self.current_algorithm == "краскал":
            mst_edges = self.graph.kruskal()
        else:
            return

        for graphics_edge in self.edge_items.values():
            graphics_edge.setPen(QPen(Qt.black, 2))

        for edge in mst_edges:
            if edge in self.edge_items:
                self.edge_items[edge].setPen(QPen(Qt.red, 3))

    def clear(self):
        self.graph.clear()
        self.node_items.clear()
        self.edge_items.clear()
        super().clear()
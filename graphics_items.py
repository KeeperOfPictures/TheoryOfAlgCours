from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from point import Point
from edge import Edge

class WeightTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        
    def focusOutEvent(self, event):
        if self.parentItem():
            self.parentItem().update_weight()
        super().focusOutEvent(event)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.clearFocus()
            return
        super().keyPressEvent(event)

class Node(QGraphicsEllipseItem):
    def __init__(self, point):
        super().__init__(-15, -15, 30, 30)
        self.point = point
        self.setPos(point.x, point.y)
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.label = QGraphicsTextItem(str(point.index), self)
        self.label.setPos(-5, -8)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value
            self.point.x = new_pos.x()
            self.point.y = new_pos.y()
            
            for edge in self.point.edges:
                if hasattr(edge, 'graphics_item'):
                    edge.graphics_item.adjust()
                    edge.graphics_item.update_text_pos()
        return super().itemChange(change, value)

class GraphicsEdge(QGraphicsLineItem):
    def __init__(self, edge):
        super().__init__()
        self.edge = edge
        edge.graphics_item = self
        self.setPen(QPen(Qt.black, 2))
        self.adjust()
        
        self.weight_text = WeightTextItem(f"{self.edge.weight:.1f}", self)
        self.update_text_pos()

    def adjust(self):
        p1 = self.edge.source
        p2 = self.edge.dest
        self.setLine(p1.x, p1.y, p2.x, p2.y)

    def update_text_pos(self):
        p1 = self.edge.source
        p2 = self.edge.dest
        self.weight_text.setPos((p1.x + p2.x)/2, (p1.y + p2.y)/2)
        
    def update_weight(self):
        try:
            new_weight = float(self.weight_text.toPlainText())
            self.edge.weight = new_weight
            self.weight_text.setPlainText(f"{self.edge.weight:.1f}")
        except ValueError:
            self.weight_text.setPlainText(f"{self.edge.weight:.1f}")
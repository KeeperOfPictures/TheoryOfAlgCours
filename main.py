import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from graph import Graph
from graphics_scene import GraphicsScene

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Минимальное остовное дерево")
        self.setGeometry(100, 100, 800, 600)
        
        self.graph = Graph()
        self.scene = GraphicsScene(self.graph)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.create_toolbar()
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        self.select_action = QAction("Выбрать", self)
        self.select_action.setCheckable(True)
        self.select_action.setChecked(True)
        self.select_action.triggered.connect(lambda: self.set_mode("выбрать"))
        
        self.add_node_action = QAction("Добавить ноду", self)
        self.add_node_action.setCheckable(True)
        self.add_node_action.triggered.connect(lambda: self.set_mode("добавить_ноду"))
        
        self.add_edge_action = QAction("Добавить ребро", self)
        self.add_edge_action.setCheckable(True)
        self.add_edge_action.triggered.connect(lambda: self.set_mode("добавить_ребро"))
        
        self.remove_action = QAction("Удалить", self)
        self.remove_action.setCheckable(True)
        self.remove_action.triggered.connect(lambda: self.set_mode("удалить"))
        
        self.mode_group = QActionGroup(self)
        self.mode_group.addAction(self.select_action)
        self.mode_group.addAction(self.add_node_action)
        self.mode_group.addAction(self.add_edge_action)
        self.mode_group.addAction(self.remove_action)
        
        toolbar.addAction(self.select_action)
        toolbar.addAction(self.add_node_action)
        toolbar.addAction(self.add_edge_action)
        toolbar.addAction(self.remove_action)
        
        toolbar.addSeparator()
        
        self.prim_action = QAction("Прим", self)
        self.prim_action.triggered.connect(lambda: self.set_algorithm("прим"))
        
        self.kruskal_action = QAction("Краскал", self)
        self.kruskal_action.triggered.connect(lambda: self.set_algorithm("краскал"))
        
        toolbar.addAction(self.prim_action)
        toolbar.addAction(self.kruskal_action)
        
        toolbar.addSeparator()
        
        self.run_algorithm_action = QAction("Запуск алгоритма", self)
        self.run_algorithm_action.triggered.connect(self.run_algorithm)
        toolbar.addAction(self.run_algorithm_action)
        
        self.clear_action = QAction("Очистить", self)
        self.clear_action.triggered.connect(self.clear_scene)
        toolbar.addAction(self.clear_action)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
    def set_mode(self, mode):
        self.scene.set_mode(mode)
        self.update_status()
        
    def set_algorithm(self, algorithm):
        self.scene.current_algorithm = algorithm
        self.status_bar.showMessage(f"Выбранный алгоритм: {algorithm.capitalize()}")
        
    def run_algorithm(self):
        if self.scene.current_algorithm:
            self.scene.run_algorithm()
            self.status_bar.showMessage(f"Запуск {self.scene.current_algorithm.capitalize()} алгоритма")
        else:
            self.status_bar.showMessage("Сперва выберите алгоритм")
        
    def clear_scene(self):
        self.scene.clear()
        self.status_bar.showMessage("Сцена очищена")
        
    def update_status(self):
        mode = self.scene.mode
        mode_text = {
            "выбрать": "Выбрать: Кликните на ноду и двигайте её. Кликните на веса, чтобы их редактировать.",
            "добавить_ноду": "Добавить ноду: кликните чтобы создать вершину",
            "добавить_ребро": "Добавить ребро: Кликните чтобы создать ребро, соединяющее две вершины.",
            "удалить": "Кликните чтобы удалиьт ребро или вершину"
        }
        self.status_bar.showMessage(mode_text.get(mode, ""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
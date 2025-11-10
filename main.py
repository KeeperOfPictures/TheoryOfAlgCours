import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from graph import Graph
from graphics_scene import GraphicsScene

class GraphListWidget(QWidget):
    def __init__(self, graph, scene):
        super().__init__()
        self.graph = graph
        self.scene = scene
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Структура графа")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)
        
        vertices_label = QLabel("Вершины:")
        vertices_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(vertices_label)
        
        self.vertices_list = QListWidget()
        self.vertices_list.setMaximumHeight(150)
        layout.addWidget(self.vertices_list)
        
        edges_label = QLabel("Рёбра:")
        edges_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(edges_label)
        
        self.edges_list = QListWidget()
        self.edges_list.setMaximumHeight(200)
        layout.addWidget(self.edges_list)
        
        info_label = QLabel("Информация:")
        info_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        self.setLayout(layout)
        
    def update_graph_info(self):
        self.vertices_list.clear()
        for point in self.graph.points:
            item = QListWidgetItem(f"Вершина {point.index}: ({point.x:.1f}, {point.y:.1f})")
            self.vertices_list.addItem(item)
        
        self.edges_list.clear()
        for edge in self.graph.edges:
            item = QListWidgetItem(
                f"Ребро {edge.source.index}-{edge.dest.index}: вес = {edge.weight:.1f}"
            )
            self.edges_list.addItem(item)
        
        vertex_count = len(self.graph.points)
        edge_count = len(self.graph.edges)
        info_text = f"Вершин: {vertex_count}\nРёбер: {edge_count}"
        
        self.info_text.setPlainText(info_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Минимальное остовное дерево")
        self.setGeometry(100, 100, 1000, 600)
        
        self.graph = Graph()
        self.scene = GraphicsScene(self.graph)
        self.view = QGraphicsView(self.scene)
        
        self.graph_list_widget = GraphListWidget(self.graph, self.scene)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.graph_list_widget)
        splitter.addWidget(self.view)
        splitter.setSizes([300, 700])
        
        self.setCentralWidget(splitter)
        
        self.create_toolbar()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.graph_list_widget.update_graph_info)
        self.update_timer.start(500)
        
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
        
        # Новые кнопки для импорта и экспорта
        self.export_action = QAction("Экспорт", self)
        self.export_action.triggered.connect(self.export_graph)
        toolbar.addAction(self.export_action)
        
        self.import_action = QAction("Импорт", self)
        self.import_action.triggered.connect(self.import_graph)
        toolbar.addAction(self.import_action)
        
        toolbar.addSeparator()
        
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
            
            self.graph_list_widget.update_graph_info()
        else:
            self.status_bar.showMessage("Сперва выберите алгоритм")
    
    def export_graph(self):
        """Экспорт графа в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт графа", "", "Graph Files (*.json)"
        )
        
        if file_path:
            try:
                graph_data = {
                    'points': [],
                    'edges': []
                }
                
                # Сохраняем вершины
                for point in self.graph.points:
                    graph_data['points'].append({
                        'index': point.index,
                        'x': point.x,
                        'y': point.y
                    })
                
                # Сохраняем рёбра
                for edge in self.graph.edges:
                    graph_data['edges'].append({
                        'source_index': edge.source.index,
                        'dest_index': edge.dest.index,
                        'weight': edge.weight
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"Граф экспортирован в {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось экспортировать граф: {str(e)}")
    
    def import_graph(self):
        """Импорт графа из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт графа", "", "Graph Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                
                # Очищаем текущий граф
                self.scene.clear()
                
                # Восстанавливаем вершины
                points_map = {}
                for point_data in graph_data['points']:
                    point = self.graph.add_point(point_data['x'], point_data['y'])
                    points_map[point_data['index']] = point
                    self.scene.add_node(point)
                
                # Восстанавливаем рёбра
                for edge_data in graph_data['edges']:
                    source = points_map[edge_data['source_index']]
                    dest = points_map[edge_data['dest_index']]
                    weight = edge_data['weight']
                    
                    edge = self.graph.add_edge(source, dest, weight)
                    if edge:
                        self.scene.add_edge(edge)
                
                self.status_bar.showMessage(f"Граф импортирован из {file_path}")
                self.graph_list_widget.update_graph_info()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать граф: {str(e)}")
        
    def clear_scene(self):
        self.scene.clear()
        self.status_bar.showMessage("Сцена очищена")
        
    def update_status(self):
        mode = self.scene.mode
        mode_text = {
            "выбрать": "Выбрать: Кликните на ноду и двигайте её. Кликните на веса, чтобы их редактировать.",
            "добавить_ноду": "Добавить ноду: кликните чтобы создать вершину",
            "добавить_ребро": "Добавить ребро: Кликните чтобы создать ребро, соединяющее две вершины.",
            "удалить": "Кликните чтобы удалить ребро или вершину"
        }
        self.status_bar.showMessage(mode_text.get(mode, ""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
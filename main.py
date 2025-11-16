import sys
import json
import time
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from graph import Graph
from graphics_scene import GraphicsScene
from database import GraphDatabase

class GraphListWidget(QWidget):
    def __init__(self, graph, scene):
        super().__init__()
        self.graph = graph
        self.scene = scene
        self.algorithm_name = None
        self.mst_weight = None
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
        
        if self.algorithm_name and self.mst_weight is not None:
            info_text += f"\n\nАлгоритм: {self.algorithm_name}\nВес MST: {self.mst_weight:.2f}"
        
        self.info_text.setPlainText(info_text)
    
    def set_algorithm_result(self, algorithm_name, mst_weight):
        self.algorithm_name = algorithm_name
        self.mst_weight = mst_weight
        self.update_graph_info()
    
    def clear_algorithm_result(self):
        self.algorithm_name = None
        self.mst_weight = None
        self.update_graph_info()

class DatabaseDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("История алгоритмов")
        self.setGeometry(200, 200, 900, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Граф", "Алгоритм", "Вес MST", "Время (сек)", "Дата", "Вершин/Рёбер"
        ])
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.doubleClicked.connect(self.load_result)
        
        layout.addWidget(QLabel("История запусков алгоритмов:"))
        layout.addWidget(self.results_table)
        
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Загрузить граф")
        self.delete_button = QPushButton("Удалить запись")
        self.clear_button = QPushButton("Очистить всё")
        self.close_button = QPushButton("Закрыть")
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.load_button.clicked.connect(self.load_selected)
        self.delete_button.clicked.connect(self.delete_selected)
        self.clear_button.clicked.connect(self.clear_all)
        self.close_button.clicked.connect(self.reject)
        
        self.load_data()
    
    def load_data(self):
        results = self.database.get_all_results()
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            graph_data = result['graph_data']
            vertex_count = len(graph_data['points'])
            edge_count = len(graph_data['edges'])
            
            self.results_table.setItem(i, 0, QTableWidgetItem(str(result['id'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(result['graph_name']))
            self.results_table.setItem(i, 2, QTableWidgetItem(result['algorithm_name']))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{result['mst_weight']:.2f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(
                f"{result['execution_time']:.4f}" if result['execution_time'] else "N/A"
            ))
            self.results_table.setItem(i, 5, QTableWidgetItem(
                result['timestamp'].split('.')[0] if isinstance(result['timestamp'], str) else str(result['timestamp'])
            ))
            self.results_table.setItem(i, 6, QTableWidgetItem(f"{vertex_count}/{edge_count}"))
        
        self.results_table.resizeColumnsToContents()
    
    def load_selected(self):
        self.load_result(self.results_table.currentIndex())
    
    def load_result(self, index):
        if index.isValid():
            row = index.row()
            result_id = int(self.results_table.item(row, 0).text())
            self.parent().load_graph_from_database(result_id)
            self.accept()
    
    def delete_selected(self):
        selected = self.results_table.currentRow()
        if selected >= 0:
            result_id = int(self.results_table.item(selected, 0).text())
            graph_name = self.results_table.item(selected, 1).text()
            algorithm_name = self.results_table.item(selected, 2).text()
            
            reply = QMessageBox.question(
                self, "Подтверждение", 
                f"Удалить запись для графа '{graph_name}' (алгоритм {algorithm_name})?"
            )
            
            if reply == QMessageBox.Yes:
                self.database.delete_result(result_id)
                self.load_data()
    
    def clear_all(self):
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите удалить все записи истории?"
        )
        
        if reply == QMessageBox.Yes:
            self.database.clear_all_results()
            self.load_data()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Минимальное остовное дерево")
        self.setGeometry(100, 100, 1000, 600)
        
        self.graph = Graph()
        self.scene = GraphicsScene(self.graph)
        self.view = QGraphicsView(self.scene)
        
        try:
            self.database = GraphDatabase(use_docker_api=True, api_url="http://localhost:5000")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка подключения", 
                              f"Не удалось подключиться к Docker Database API: {str(e)}\n"
                              f"Будет использована локальная SQLite база.")
            self.database = GraphDatabase()
        
        self.graph_list_widget = GraphListWidget(self.graph, self.scene)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.graph_list_widget)
        splitter.addWidget(self.view)
        splitter.setSizes([300, 700])
        
        self.setCentralWidget(splitter)
        
        self.create_toolbar()
        self.create_menubar()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.graph_list_widget.update_graph_info)
        self.update_timer.start(500)
        
    def create_menubar(self):
        menubar = self.menuBar()
        
        db_menu = menubar.addMenu("База данных")
        
        history_action = QAction("История алгоритмов", self)
        history_action.triggered.connect(self.show_algorithm_history)
        db_menu.addAction(history_action)
        
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
        
        self.algorithm_group = QActionGroup(self)
        self.algorithm_group.setExclusive(True)
        
        self.prim_action = QAction("Прим", self)
        self.prim_action.setCheckable(True)
        self.prim_action.triggered.connect(lambda: self.set_algorithm("Прим"))
        self.algorithm_group.addAction(self.prim_action)
        
        self.kruskal_action = QAction("Краскал", self)
        self.kruskal_action.setCheckable(True)
        self.kruskal_action.triggered.connect(lambda: self.set_algorithm("Краскал"))
        self.algorithm_group.addAction(self.kruskal_action)
        
        toolbar.addAction(self.prim_action)
        toolbar.addAction(self.kruskal_action)
        
        toolbar.addSeparator()
        
        self.run_algorithm_action = QAction("Запуск алгоритма", self)
        self.run_algorithm_action.triggered.connect(self.run_algorithm)
        toolbar.addAction(self.run_algorithm_action)
        
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
        self.scene.current_algorithm = algorithm.lower()
        if algorithm == "Прим":
            self.prim_action.setChecked(True)
        elif algorithm == "Краскал":
            self.kruskal_action.setChecked(True)
        self.status_bar.showMessage(f"Выбранный алгоритм: {algorithm}")
        
    def run_algorithm(self):
        if self.scene.current_algorithm:
            graph_name, ok = QInputDialog.getText(
                self, "Сохранение результата", 
                "Введите название для этого графа:",
                text=f"Граф_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if not ok or not graph_name:
                return
            
            start_time = time.time()
            mst_edges = self.scene.run_algorithm()
            execution_time = time.time() - start_time
            
            if mst_edges is not None:
                total_weight = sum(edge.weight for edge in mst_edges)
                
                algorithm_name = self.scene.current_algorithm.capitalize()
                self.graph_list_widget.set_algorithm_result(algorithm_name, total_weight)
                
                graph_data = self.get_graph_data()
                
                mst_edges_data = []
                for edge in mst_edges:
                    mst_edges_data.append({
                        'source_index': edge.source.index,
                        'dest_index': edge.dest.index,
                        'weight': edge.weight
                    })
                
                self.database.save_algorithm_result(
                    graph_name=graph_name,
                    graph_data=graph_data,
                    algorithm_name=algorithm_name,
                    mst_weight=total_weight,
                    mst_edges=mst_edges_data,
                    execution_time=execution_time
                )
                
                self.status_bar.showMessage(
                    f"Алгоритм {algorithm_name} выполнен. Вес MST: {total_weight:.2f}. Результат сохранен в БД."
                )
            else:
                self.status_bar.showMessage(f"Запуск {self.scene.current_algorithm.capitalize()} алгоритма")
            
            self.graph_list_widget.update_graph_info()
        else:
            self.status_bar.showMessage("Сперва выберите алгоритм")
    
    def export_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт графа", "", "Graph Files (*.json)"
        )
        
        if file_path:
            try:
                graph_data = self.get_graph_data()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"Граф экспортирован в {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка экспорта", f"Не удалось экспортировать граф: {str(e)}")
    
    def import_graph(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт графа", "", "Graph Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                
                self.load_graph_data(graph_data)
                
                self.status_bar.showMessage(f"Граф импортирован из {file_path}")
                self.graph_list_widget.update_graph_info()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать граф: {str(e)}")
    
    def get_graph_data(self):
        graph_data = {
            'points': [],
            'edges': []
        }
        
        for point in self.graph.points:
            graph_data['points'].append({
                'index': point.index,
                'x': point.x,
                'y': point.y
            })
        
        for edge in self.graph.edges:
            graph_data['edges'].append({
                'source_index': edge.source.index,
                'dest_index': edge.dest.index,
                'weight': edge.weight
            })
        
        return graph_data
    
    def load_graph_data(self, graph_data):
        self.scene.clear()
        self.graph_list_widget.clear_algorithm_result()
        
        points_map = {}
        for point_data in graph_data['points']:
            point = self.graph.add_point(point_data['x'], point_data['y'])
            points_map[point_data['index']] = point
            self.scene.add_node(point)
        
        for edge_data in graph_data['edges']:
            source = points_map[edge_data['source_index']]
            dest = points_map[edge_data['dest_index']]
            weight = edge_data['weight']
            
            edge = self.graph.add_edge(source, dest, weight)
            if edge:
                self.scene.add_edge(edge)
    
    def show_algorithm_history(self):
        dialog = DatabaseDialog(self.database, self)
        dialog.exec()
    
    def load_graph_from_database(self, result_id):
        result = self.database.get_result(result_id)
        if result:
            self.load_graph_data(result['graph_data'])
            
            self.graph_list_widget.set_algorithm_result(
                result['algorithm_name'], 
                result['mst_weight']
            )
            
            mst_edges_data = result['mst_edges']
            for edge in self.graph.edges:
                for mst_edge in mst_edges_data:
                    if (edge.source.index == mst_edge['source_index'] and 
                        edge.dest.index == mst_edge['dest_index']):
                        if edge in self.scene.edge_items:
                            self.scene.edge_items[edge].setPen(QPen(Qt.red, 3))
            
            self.status_bar.showMessage(
                f"Загружен граф '{result['graph_name']}'. " +
                f"Алгоритм: {result['algorithm_name']}, Вес MST: {result['mst_weight']:.2f}"
            )
        
    def clear_scene(self):
        self.scene.clear()
        self.graph_list_widget.clear_algorithm_result()
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
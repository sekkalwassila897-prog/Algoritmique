# dsatur_app.py
import sys
import math
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QHeaderView,
    QGroupBox, QMessageBox, QProgressBar, QFrame, QGridLayout,
    QGraphicsTextItem, QSplitter  
)
from PyQt5.QtCore import Qt, QTimer, QPointF, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QPainter

# ================================
# GRAPH COMPONENTS FOR DSATUR
# ================================

class GraphNode(QGraphicsEllipseItem):
    def __init__(self, node_id, x, y, radius=30):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.node_id = node_id
        self.radius = radius
        self.setPos(x - radius, y - radius)
        
        self.setBrush(QBrush(QColor(100, 149, 237)))  # Cornflower blue
        self.setPen(QPen(QColor(255, 255, 255), 2))
        
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.setZValue(2)
        
        self.color = -1
        self.saturation = 0
        self.degree = 0
        self.neighbors = set()
        self.text_item = None
        self.original_color = QColor(100, 149, 237)
        
        self.setAcceptHoverEvents(True)
        
    def add_neighbor(self, neighbor_id):
        if neighbor_id not in self.neighbors:
            self.neighbors.add(neighbor_id)
            self.degree = len(self.neighbors)
        
    def remove_neighbor(self, neighbor_id):
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)
            self.degree = len(self.neighbors)
        
    def update_saturation(self, graph):
        neighbor_colors = set()
        for neighbor_id in self.neighbors:
            neighbor_color = graph.nodes[neighbor_id].color
            if neighbor_color != -1:
                neighbor_colors.add(neighbor_color)
        self.saturation = len(neighbor_colors)
        return self.saturation

    def set_text_item(self, text_item):
        self.text_item = text_item
        
    def update_text_color(self, background_color):
        if self.text_item:
            brightness = (background_color.red() * 299 + 
                         background_color.green() * 587 + 
                         background_color.blue() * 114) / 1000
            self.text_item.setDefaultTextColor(Qt.white if brightness < 180 else Qt.black)
    
    def hoverEnterEvent(self, event):
        if self.color == -1:
            self.setPen(QPen(QColor(255, 255, 255), 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255), 2))
        super().hoverLeaveEvent(event)
    
    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionChange:
            if self.text_item:
                center = self.pos() + QPointF(self.radius, self.radius)
                text_rect = self.text_item.boundingRect()
                self.text_item.setPos(
                    center.x() - text_rect.width()/2,
                    center.y() - text_rect.height()/2
                )
        return super().itemChange(change, value)
    
    def get_center(self):
        return self.pos() + QPointF(self.radius, self.radius)

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.next_node_id = 1
        self.scene = None
        self.edge_items = {}
        
    def set_scene(self, scene):
        self.scene = scene
        
    def add_node(self, x, y, scene, radius=30):
        node_id = self.next_node_id
        self.nodes[node_id] = GraphNode(node_id, x, y, radius)
        self.next_node_id += 1
        
        scene.addItem(self.nodes[node_id])
        
        text_item = QGraphicsTextItem(str(node_id))
        text_item.setDefaultTextColor(Qt.white)
        text_item.setFont(QFont("Arial", 12, QFont.Bold))
        
        text_rect = text_item.boundingRect()
        text_item.setPos(
            x - text_rect.width()/2,
            y - text_rect.height()/2
        )
        text_item.setZValue(3)
        
        scene.addItem(text_item)
        self.nodes[node_id].set_text_item(text_item)
        return node_id
        
    def add_edge(self, node1_id, node2_id, scene):
        for edge in self.edges:
            if (edge[0] == node1_id and edge[1] == node2_id) or \
               (edge[0] == node2_id and edge[1] == node1_id):
                return False
        
        if (node1_id in self.nodes and node2_id in self.nodes and 
            node1_id != node2_id):
            
            self.edges.append((node1_id, node2_id))
            self.nodes[node1_id].add_neighbor(node2_id)
            self.nodes[node2_id].add_neighbor(node1_id)
            
            self.draw_edge_line(node1_id, node2_id, scene)
            return True
        return False
    
    def draw_edge_line(self, node1_id, node2_id, scene):
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        
        center1 = node1.get_center()
        center2 = node2.get_center()
        
        dx = center2.x() - center1.x()
        dy = center2.y() - center1.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            start_x = center1.x() + (dx * node1.radius / distance)
            start_y = center1.y() + (dy * node1.radius / distance)
            end_x = center2.x() - (dx * node2.radius / distance)
            end_y = center2.y() - (dy * node2.radius / distance)
            
            line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
            line.setPen(QPen(QColor(140, 140, 160), 2, Qt.SolidLine, Qt.RoundCap))
            line.setZValue(1)
            scene.addItem(line)
            
            edge_key = (min(node1_id, node2_id), max(node1_id, node2_id))
            self.edge_items[edge_key] = line
    
    def remove_edge(self, node1_id, node2_id, scene):
        edge_to_remove = None
        edge_key = None
        
        for edge in self.edges:
            if (edge[0] == node1_id and edge[1] == node2_id) or \
               (edge[0] == node2_id and edge[1] == node1_id):
                edge_to_remove = edge
                edge_key = (min(node1_id, node2_id), max(node1_id, node2_id))
                break
        
        if edge_to_remove:
            self.edges.remove(edge_to_remove)
            
            if edge_key in self.edge_items:
                scene.removeItem(self.edge_items[edge_key])
                del self.edge_items[edge_key]
            
            if node1_id in self.nodes:
                self.nodes[node1_id].remove_neighbor(node2_id)
            if node2_id in self.nodes:
                self.nodes[node2_id].remove_neighbor(node1_id)
            
            return True
        return False
    
    def redraw_all_edges(self, scene):
        for edge_key, line_item in list(self.edge_items.items()):
            scene.removeItem(line_item)
        self.edge_items.clear()
        
        for edge in self.edges:
            self.draw_edge_line(edge[0], edge[1], scene)
    
    def remove_node(self, node_id, scene):
        if node_id in self.nodes:
            edges_to_remove = []
            for edge in self.edges[:]:
                if edge[0] == node_id or edge[1] == node_id:
                    edges_to_remove.append(edge)
            
            for edge in edges_to_remove:
                self.edges.remove(edge)
                edge_key = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                if edge_key in self.edge_items:
                    scene.removeItem(self.edge_items[edge_key])
                    del self.edge_items[edge_key]
                
                if edge[0] in self.nodes:
                    self.nodes[edge[0]].remove_neighbor(edge[1])
                if edge[1] in self.nodes:
                    self.nodes[edge[1]].remove_neighbor(edge[0])
            
            if self.nodes[node_id].text_item:
                scene.removeItem(self.nodes[node_id].text_item)
            
            scene.removeItem(self.nodes[node_id])
            del self.nodes[node_id]
            
            return True
        return False
            
    def reset_colors(self):
        for node_id, node in self.nodes.items():
            node.color = -1
            node.saturation = 0
            node.setBrush(QBrush(QColor(100, 149, 237)))
            node.original_color = QColor(100, 149, 237)
            if node.text_item:
                node.text_item.setDefaultTextColor(Qt.white)

# ================================
# GRAPH VISUALIZERS
# ================================

class GraphVisualizerDSATUR(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        self.scene.setBackgroundBrush(QBrush(QColor(248, 249, 250)))
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        self.graph = Graph()
        self.graph.set_scene(self.scene)
        
        self.add_node_mode = False
        self.add_edge_mode = False
        self.delete_edge_mode = False
        self.edge_start_node = None
        self.temp_line = None
        self.is_drawing_edge = False
        
        self.colors = [
            QColor(255, 87, 34),   # Rouge/Orange
            QColor(33, 150, 243),  # Bleu
            QColor(76, 175, 80),   # Vert
            QColor(255, 235, 59),  # Jaune
            QColor(156, 39, 176),  # Violet
            QColor(255, 193, 7),   # Orange
            QColor(233, 30, 99),   # Rose
            QColor(0, 188, 212),   # Cyan
            QColor(121, 85, 72),   # Marron
            QColor(158, 158, 158), # Gris
        ]
        
        self.create_empty_graph()
    
    def create_empty_graph(self):
        self.scene.clear()
        self.graph = Graph()
        self.graph.set_scene(self.scene)
        self.add_node_mode = False
        self.add_edge_mode = False
        self.delete_edge_mode = False
        self.edge_start_node = None
        self.is_drawing_edge = False
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
    
    def create_random_graph(self):
        self.create_empty_graph()
        
        num_nodes = random.randint(5, 8)
        node_ids = []
        
        for i in range(num_nodes):
            angle = 2 * math.pi * i / num_nodes
            radius = 150
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            node_id = self.graph.add_node(x, y, self.scene, 28)
            node_ids.append(node_id)
            
        for i in range(num_nodes):
            for j in range(i+1, num_nodes):
                if random.random() < 0.4:
                    self.graph.add_edge(node_ids[i], node_ids[j], self.scene)
        
        self.fit_view()
    
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.transform())
        
        if self.add_node_mode:
            node_id = self.graph.add_node(scene_pos.x(), scene_pos.y(), self.scene, 28)
            self.add_node_mode = False
            self.disable_interaction_mode()
            
        elif self.add_edge_mode:
            if isinstance(item, GraphNode):
                if self.edge_start_node is None:
                    self.edge_start_node = item
                    self.is_drawing_edge = True
                    item.setBrush(QBrush(QColor(255, 183, 77)))
                    
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                    self.temp_line = QGraphicsLineItem()
                    self.temp_line.setPen(QPen(QColor(255, 183, 77), 2, Qt.DashLine))
                    self.temp_line.setZValue(1)
                    self.scene.addItem(self.temp_line)
                    
                    start_center = self.edge_start_node.get_center()
                    self.temp_line.setLine(
                        start_center.x(), start_center.y(), 
                        scene_pos.x(), scene_pos.y()
                    )
                else:
                    if self.edge_start_node != item:
                        node1_id = self.edge_start_node.node_id
                        node2_id = item.node_id
                        
                        success = self.graph.add_edge(node1_id, node2_id, self.scene)
                        
                        if success:
                            self.graph.redraw_all_edges(self.scene)
                            self.scene.update()
                            
                    self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
                    self.edge_start_node = None
                    self.is_drawing_edge = False
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None
                    
            elif self.edge_start_node:
                self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
                self.edge_start_node = None
                self.is_drawing_edge = False
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None
                    
        elif self.delete_edge_mode:
            if isinstance(item, GraphNode):
                if self.edge_start_node is None:
                    self.edge_start_node = item
                    item.setBrush(QBrush(QColor(239, 83, 80)))
                else:
                    if self.edge_start_node != item:
                        node1_id = self.edge_start_node.node_id
                        node2_id = item.node_id
                        
                        if self.graph.remove_edge(node1_id, node2_id, self.scene):
                            self.scene.update()
                    
                    self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
                    self.edge_start_node = None
                    self.delete_edge_mode = False
                    self.disable_interaction_mode()
                    
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.add_edge_mode and self.is_drawing_edge and self.edge_start_node and self.temp_line:
            scene_pos = self.mapToScene(event.pos())
            start_center = self.edge_start_node.get_center()
            self.temp_line.setLine(
                start_center.x(), start_center.y(), 
                scene_pos.x(), scene_pos.y()
            )
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
    
    def enable_add_node_mode(self):
        self.cleanup_edge_mode()
        self.add_node_mode = True
        self.add_edge_mode = False
        self.delete_edge_mode = False
        self.setCursor(Qt.CrossCursor)
        
    def enable_add_edge_mode(self):
        if len(self.graph.nodes) < 2:
            QMessageBox.warning(self, "Error", "Besoin d'au moins 2 sommets pour ajouter des arêtes!")
            return
        
        self.cleanup_edge_mode()
        self.add_node_mode = False
        self.add_edge_mode = True
        self.delete_edge_mode = False
        self.setCursor(Qt.PointingHandCursor)
        
    def enable_delete_edge_mode(self):
        if len(self.graph.edges) == 0:
            QMessageBox.warning(self, "Error", "Pas d'arêtes à supprimer!")
            return
        
        self.cleanup_edge_mode()
        self.add_node_mode = False
        self.add_edge_mode = False
        self.delete_edge_mode = True
        self.setCursor(Qt.ForbiddenCursor)
    
    def cleanup_edge_mode(self):
        if self.edge_start_node:
            self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
            self.edge_start_node = None
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        self.is_drawing_edge = False
        
    def disable_interaction_mode(self):
        self.add_node_mode = False
        self.add_edge_mode = False
        self.delete_edge_mode = False
        self.cleanup_edge_mode()
        self.setCursor(Qt.ArrowCursor)
        
    def delete_selected_node(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, GraphNode):
                if QMessageBox.question(self, "Confirmer suppression", 
                                       f"Supprimer le sommet {item.node_id} et toutes ses arêtes?",
                                       QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.graph.remove_node(item.node_id, self.scene)
                break
        else:
            QMessageBox.warning(self, "Erreur", "Aucun sommet sélectionné!")
    
    def color_node(self, node_id, color_index):
        if 0 <= color_index < len(self.colors):
            self.graph.nodes[node_id].color = color_index
            color = self.colors[color_index]
            self.graph.nodes[node_id].setBrush(QBrush(color))
            self.graph.nodes[node_id].original_color = color
            self.graph.nodes[node_id].update_text_color(color)
            
    def reset_graph(self):
        self.graph.reset_colors()
        self.disable_interaction_mode()
        
    def fit_view(self):
        if self.graph.nodes:
            rect = self.scene.itemsBoundingRect()
            rect.adjust(-50, -50, 50, 50)
            self.fitInView(rect, Qt.KeepAspectRatio)
        else:
            self.fitInView(QRectF(-200, -200, 400, 400), Qt.KeepAspectRatio)
        
        self.scale(0.9, 0.9)

# ================================
# DSATUR ALGORITHM INTERFACE
# ================================

class DSATURAlgorithmApp(QMainWindow):
    back_to_main_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.dsatur_state = {
            'uncolored': [],
            'colored': [],
            'current_node': None,
            'step': 0,
            'is_running': False,
            'colors_used': set(),
            'nodes_history': []
        }
        self.init_ui()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.dsatur_step)
        
    def init_ui(self):
        self.setWindowTitle("Algorithme DSATUR - Coloration de Graphes")
        self.showMaximized()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
            }
        """)
        
        left_panel = self.create_graph_panel()
        right_panel = self.create_control_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([self.width() * 2 // 3, self.width() // 3])
        
        main_layout.addWidget(splitter)
        
    def create_graph_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header = QFrame()
        header.setStyleSheet("""
            background: #66bb6a;
            border-radius: 8px;
            padding: 12px;
        """)
        header_layout = QHBoxLayout(header)
        
        back_btn = QPushButton("← Retour au Menu")
        back_btn.clicked.connect(self.back_to_main)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        title = QLabel("Algorithme DSATUR - Coloration de Graphes")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        instructions = QLabel("Cliquez 'Ajouter Sommet' puis sur le canvas pour ajouter des sommets. Cliquez 'Ajouter Arête' puis cliquez deux sommets pour les connecter.")
        instructions.setFont(QFont("Segoe UI", 10))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            color: #5c6bc0;
            background-color: #e8eaf6;
            padding: 8px;
            border-radius: 5px;
            margin: 5px;
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.graph_view = GraphVisualizerDSATUR()
        self.graph_view.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
        """)
        layout.addWidget(self.graph_view)
        
        controls = QHBoxLayout()
        
        zoom_in = QPushButton("🔍 Zoom In")
        zoom_in.clicked.connect(lambda: self.graph_view.scale(1.2, 1.2))
        zoom_in.setStyleSheet("""
            QPushButton {
                background-color: #90caf9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #64b5f6;
            }
        """)
        
        zoom_out = QPushButton("🔎 Zoom Out")
        zoom_out.clicked.connect(lambda: self.graph_view.scale(0.8, 0.8))
        zoom_out.setStyleSheet("""
            QPushButton {
                background-color: #ce93d8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #ba68c8;
            }
        """)
        
        fit = QPushButton("📐 Ajuster la Vue")
        fit.clicked.connect(self.graph_view.fit_view)
        fit.setStyleSheet("""
            QPushButton {
                background-color: #80cbc4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4db6ac;
            }
        """)
        
        controls.addWidget(zoom_in)
        controls.addWidget(zoom_out)
        controls.addWidget(fit)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        return panel
        
    def create_control_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #f5f7fa;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        tools_group = QGroupBox("🛠️ Outils du Graphe")
        tools_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        tools_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #c5cae9;
                border-radius: 8px;
                padding-top: 15px;
                background: white;
            }
            QGroupBox::title {
                color: #5c6bc0;
            }
        """)
        tools_layout = QVBoxLayout(tools_group)
        
        graph_btns = QHBoxLayout()
        
        new_btn = QPushButton("🆕 Nouveau Graphe")
        new_btn.clicked.connect(self.create_empty_graph)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #b0bec5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90a4ae;
            }
        """)
        
        random_btn = QPushButton("🎲 Graphe Aléatoire")
        random_btn.clicked.connect(self.create_random_graph)
        random_btn.setStyleSheet("""
            QPushButton {
                background-color: #b39ddb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9575cd;
            }
        """)
        
        graph_btns.addWidget(new_btn)
        graph_btns.addWidget(random_btn)
        tools_layout.addLayout(graph_btns)
        
        int_btns = QGridLayout()
        int_btns.setSpacing(8)
        
        add_node = QPushButton("➕ Ajouter Sommet")
        add_node.clicked.connect(self.enable_add_node_mode)
        add_node.setStyleSheet("""
            QPushButton {
                background-color: #80deea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4dd0e1;
            }
        """)
        
        add_edge = QPushButton("🔗 Ajouter Arête")
        add_edge.clicked.connect(self.enable_add_edge_mode)
        add_edge.setStyleSheet("""
            QPushButton {
                background-color: #a5d6a7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81c784;
            }
        """)
        
        del_edge = QPushButton("✂️ Supprimer Arête")
        del_edge.clicked.connect(self.enable_delete_edge_mode)
        del_edge.setStyleSheet("""
            QPushButton {
                background-color: #ffcc80;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffb74d;
            }
        """)
        
        del_node = QPushButton("🗑️ Supprimer Sommet")
        del_node.clicked.connect(self.delete_selected_node)
        del_node.setStyleSheet("""
            QPushButton {
                background-color: #ef9a9a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e57373;
            }
        """)
        
        int_btns.addWidget(add_node, 0, 0)
        int_btns.addWidget(add_edge, 0, 1)
        int_btns.addWidget(del_edge, 1, 0)
        int_btns.addWidget(del_node, 1, 1)
        tools_layout.addLayout(int_btns)
        
        cancel_btn = QPushButton("🚫 Annuler Mode")
        cancel_btn.clicked.connect(self.cancel_interaction_mode)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #b0bec5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90a4ae;
            }
        """)
        tools_layout.addWidget(cancel_btn)
        
        layout.addWidget(tools_group)
        
        algo_group = QGroupBox("🎨 Algorithme DSATUR")
        algo_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        algo_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #c8e6c9;
                border-radius: 8px;
                padding-top: 15px;
                background: white;
            }
            QGroupBox::title {
                color: #66bb6a;
            }
        """)
        algo_layout = QVBoxLayout(algo_group)
        
        ctrl_btns = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Démarrer Algorithme")
        self.start_btn.clicked.connect(self.start_dsatur)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4caf50;
            }
            QPushButton:disabled {
                background-color: #c8e6c9;
                color: #81c784;
            }
        """)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.pause_dsatur)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffb74d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffa726;
            }
        """)
        
        self.step_btn = QPushButton("↪ Étape")
        self.step_btn.clicked.connect(self.dsatur_single_step)
        self.step_btn.setStyleSheet("""
            QPushButton {
                background-color: #64b5f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
        """)
        
        ctrl_btns.addWidget(self.start_btn)
        ctrl_btns.addWidget(self.pause_btn)
        ctrl_btns.addWidget(self.step_btn)
        algo_layout.addLayout(ctrl_btns)
        
        reset_btn = QPushButton("⟲ Réinitialiser Couleurs")
        reset_btn.clicked.connect(self.reset_all)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef9a9a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e57373;
            }
        """)
        algo_layout.addWidget(reset_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("Progression: %p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #c5cae9;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                color: #5c6bc0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #9fa8da;
                border-radius: 5px;
            }
        """)
        algo_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Prêt à démarrer")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("""
            color: #5c6bc0;
            padding: 8px;
            background-color: #e8eaf6;
            border-radius: 5px;
            border: 1px solid #c5cae9;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        algo_layout.addWidget(self.status_label)
        
        layout.addWidget(algo_group)
        
        # ========== جدول DSATUR ==========
        results_group = QGroupBox("📊 Table DSATUR - État des Sommets")
        results_group.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #c5cae9;
                border-radius: 8px;
                padding-top: 15px;
                background: white;
            }
            QGroupBox::title {
                color: #7986cb;
            }
        """)
        results_layout = QVBoxLayout(results_group)
        
        self.dsatur_table = QTableWidget()
        self.dsatur_table.setColumnCount(7)
        self.dsatur_table.setHorizontalHeaderLabels(["Sommet", "Degré", "Dsat", "Couleur", "Voisins", "Couleurs Voisins", "État"])
        
        header = self.dsatur_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.dsatur_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 10px;
                background: white;
            }
            QTableWidget::item {
                padding: 3px;
            }
        """)
        self.dsatur_table.setMaximumHeight(400)
        results_layout.addWidget(self.dsatur_table)
        
        self.summary_label = QLabel("Aucun résultat encore")
        self.summary_label.setFont(QFont("Segoe UI", 10))
        self.summary_label.setStyleSheet("""
            color: #5c6bc0;
            background-color: #e8eaf6;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #c5cae9;
        """)
        self.summary_label.setAlignment(Qt.AlignCenter)
        self.summary_label.setWordWrap(True)
        results_layout.addWidget(self.summary_label)
        
        layout.addWidget(results_group)
        
        layout.addStretch()
        
        return panel
    
    def back_to_main(self):
        self.back_to_main_signal.emit()
        self.close()
        
    def create_empty_graph(self):
        self.graph_view.create_empty_graph()
        self.reset_all()
        self.graph_view.fit_view()
        
    def create_random_graph(self):
        self.graph_view.create_random_graph()
        self.reset_all()
        
    def enable_add_node_mode(self):
        self.graph_view.enable_add_node_mode()
        
    def enable_add_edge_mode(self):
        self.graph_view.enable_add_edge_mode()
        
    def enable_delete_edge_mode(self):
        self.graph_view.enable_delete_edge_mode()
        
    def cancel_interaction_mode(self):
        self.graph_view.disable_interaction_mode()
        
    def delete_selected_node(self):
        self.graph_view.delete_selected_node()
        self.reset_all()
        
    def start_dsatur(self):
        if not self.graph_view.graph.nodes:
            QMessageBox.warning(self, "Erreur", "Veuillez créer un graphe d'abord!")
            return
            
        if not self.dsatur_state['is_running']:
            self.initialize_dsatur()
            
        self.dsatur_state['is_running'] = True
        self.animation_timer.start(1500)
        self.start_btn.setEnabled(False)
        self.graph_view.disable_interaction_mode()
        
    def pause_dsatur(self):
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.dsatur_state['is_running'] = False
            self.start_btn.setEnabled(True)
            self.status_label.setText(f"Pause - Étape {self.dsatur_state['step']}")
        else:
            self.start_dsatur()
            
    def dsatur_single_step(self):
        if not self.graph_view.graph.nodes:
            QMessageBox.warning(self, "Erreur", "Veuillez créer un graphe d'abord!")
            return
            
        if not self.dsatur_state['uncolored'] and self.dsatur_state['step'] == 0:
            self.initialize_dsatur()
            
        self.dsatur_step()
        
    def initialize_dsatur(self):
        self.graph_view.graph.reset_colors()
        nodes = list(self.graph_view.graph.nodes.keys())
        
        for node_id in nodes:
            self.graph_view.graph.nodes[node_id].update_saturation(self.graph_view.graph)
            
        self.dsatur_state = {
            'uncolored': nodes.copy(),
            'colored': [],
            'current_node': None,
            'step': 0,
            'is_running': True,
            'colors_used': set(),
            'nodes_history': []
        }
        
        self.update_dsatur_table()
        
        self.progress_bar.setMaximum(len(nodes))
        self.progress_bar.setValue(0)
        self.status_label.setText("Prêt à démarrer l'algorithme")
        self.summary_label.setText(f"Graphe initial avec {len(nodes)} sommets. Prêt à démarrer l'algorithme DSATUR.")
        
    def update_dsatur_table(self):
        """تحديث جدول DSATUR"""
        nodes = sorted(self.graph_view.graph.nodes.keys())
        self.dsatur_table.setRowCount(len(nodes))
        
        for i, node_id in enumerate(nodes):
            node = self.graph_view.graph.nodes[node_id]
            
            # Sommet
            self.dsatur_table.setItem(i, 0, QTableWidgetItem(f"Sommet {node_id}"))
            
            # Degré
            self.dsatur_table.setItem(i, 1, QTableWidgetItem(str(node.degree)))
            
            # Dsat
            self.dsatur_table.setItem(i, 2, QTableWidgetItem(str(node.saturation)))
            
            # Couleur
            if node.color == -1:
                color_item = QTableWidgetItem("Non coloré")
                color_item.setBackground(QColor(255, 255, 255))
            else:
                color_names = ["Rouge", "Bleu", "Vert", "Jaune", "Orange", 
                              "Violet", "Rose", "Cyan", "Marron", "Gris"]
                color_name = color_names[node.color % len(color_names)]
                color_item = QTableWidgetItem(color_name)
                color_item.setBackground(self.graph_view.colors[node.color])
                color_item.setForeground(Qt.white)
            self.dsatur_table.setItem(i, 3, color_item)
            
            # Voisins
            neighbors_info = ", ".join([str(n) for n in sorted(node.neighbors)])
            self.dsatur_table.setItem(i, 4, QTableWidgetItem(neighbors_info if neighbors_info else "Aucun"))
            
            # Couleurs des voisins
            neighbor_colors = set()
            for neighbor_id in node.neighbors:
                neighbor_color = self.graph_view.graph.nodes[neighbor_id].color
                if neighbor_color != -1:
                    neighbor_colors.add(neighbor_color)
            
            if neighbor_colors:
                color_list = ", ".join([str(c) for c in sorted(neighbor_colors)])
                self.dsatur_table.setItem(i, 5, QTableWidgetItem(color_list))
            else:
                self.dsatur_table.setItem(i, 5, QTableWidgetItem("Aucune"))
            
            # État
            if node_id in self.dsatur_state['uncolored']:
                state = "Non coloré"
                bg_color = QColor(255, 235, 238)  # Rouge clair
            else:
                state = "Coloré"
                bg_color = QColor(232, 245, 233)  # Vert clair
            
            state_item = QTableWidgetItem(state)
            state_item.setBackground(bg_color)
            self.dsatur_table.setItem(i, 6, state_item)
    
    def dsatur_step(self):
        if not self.dsatur_state['uncolored']:
            self.animation_timer.stop()
            self.dsatur_state['is_running'] = False
            self.start_btn.setEnabled(True)
            self.complete_algorithm()
            return
            
        max_saturation = -1
        candidates = []
        
        for node_id in self.dsatur_state['uncolored']:
            node = self.graph_view.graph.nodes[node_id]
            if node.saturation > max_saturation:
                max_saturation = node.saturation
                candidates = [node_id]
            elif node.saturation == max_saturation:
                candidates.append(node_id)
                
        if len(candidates) > 1:
            max_degree = -1
            selected_node = candidates[0]
            for node_id in candidates:
                degree = self.graph_view.graph.nodes[node_id].degree
                if degree > max_degree:
                    max_degree = degree
                    selected_node = node_id
        else:
            selected_node = candidates[0]
            
        selected_color = self.color_node_dsatur(selected_node)
        
        self.dsatur_state['current_node'] = selected_node
        self.dsatur_state['uncolored'].remove(selected_node)
        self.dsatur_state['colored'].append(selected_node)
        if selected_color != -1:
            self.dsatur_state['colors_used'].add(selected_color)
        
        self.update_dsatur_table()
        
        self.progress_bar.setValue(len(self.dsatur_state['colored']))
        self.status_label.setText(f"Étape {self.dsatur_state['step'] + 1}: Sommet {selected_node} coloré")
        
        self.dsatur_state['step'] += 1
        
    def color_node_dsatur(self, node_id):
        node = self.graph_view.graph.nodes[node_id]
        
        used_colors = set()
        for neighbor_id in node.neighbors:
            neighbor_color = self.graph_view.graph.nodes[neighbor_id].color
            if neighbor_color != -1:
                used_colors.add(neighbor_color)
                
        selected_color = -1
        for color_index in range(len(self.graph_view.colors)):
            if color_index not in used_colors:
                selected_color = color_index
                break
                
        self.graph_view.color_node(node_id, selected_color)
        
        for neighbor_id in node.neighbors:
            if neighbor_id in self.dsatur_state['uncolored']:
                self.graph_view.graph.nodes[neighbor_id].update_saturation(self.graph_view.graph)
        
        return selected_color
        
    def complete_algorithm(self):
        colors_used = len(self.dsatur_state['colors_used'])
        
        self.summary_label.setText(
            f"✅ Algorithme terminé avec succès!\n"
            f"Nombre total d'étapes: {self.dsatur_state['step']}\n"
            f"Couleurs utilisées: {colors_used}\n"
            f"Sommets colorés: {len(self.dsatur_state['colored'])}"
        )
        
        QMessageBox.information(self, "Algorithme Terminé", 
                               f"Graphe coloré avec succès!\n\n"
                               f"Étapes: {self.dsatur_state['step']}\n"
                               f"Couleurs utilisées: {colors_used}\n"
                               f"Sommets colorés: {len(self.dsatur_state['colored'])}")
        
        self.status_label.setText(f"Algorithme terminé - {colors_used} couleurs utilisées")
        
    def reset_all(self):
        self.animation_timer.stop()
        if hasattr(self, 'graph_view'):
            self.graph_view.reset_graph()
        self.dsatur_state = {
            'uncolored': [],
            'colored': [],
            'current_node': None,
            'step': 0,
            'is_running': False,
            'colors_used': set(),
            'nodes_history': []
        }
        self.dsatur_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.status_label.setText("Prêt à démarrer")
        self.summary_label.setText("Aucun résultat encore")
        self.start_btn.setEnabled(True)
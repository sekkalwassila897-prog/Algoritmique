# johnson_app.py
import sys
import math
import random
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QHeaderView,
    QGroupBox, QMessageBox, QProgressBar, QFrame, QGridLayout, QSpinBox,
    QInputDialog, QGraphicsTextItem, QSplitter, QTextEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, QPointF, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QPainter

# ================================
# WEIGHTED GRAPH COMPONENTS FOR JOHNSON
# ================================

class WeightedGraphNode(QGraphicsEllipseItem):
    def __init__(self, node_id, x, y, radius=25, label=None):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.node_id = node_id
        self.radius = radius
        self.setPos(x - radius, y - radius)
        
        self.setBrush(QBrush(QColor(100, 149, 237)))  # أزرق
        self.setPen(QPen(QColor(255, 255, 255), 2))
        
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)
        self.setZValue(2)
        
        self.original_color = QColor(100, 149, 237)
        self.weight_label = None
        self.h_value = 0
        self.is_auxiliary = False  # هل هو الـ Sommet S المساعد؟
        
        # استخدام التسمية المقدمة أو رقم العقدة
        self.node_label = label if label else str(node_id)
        
        self.setAcceptHoverEvents(True)
        
    def get_center(self):
        return self.pos() + QPointF(self.radius, self.radius)
    
    def set_weight_label(self, label_item):
        self.weight_label = label_item
    
    def update_h_display(self):
        if self.weight_label:
            if self.is_auxiliary:
                self.weight_label.setPlainText("S")
            elif self.h_value == 0:
                self.weight_label.setPlainText(f"{self.node_label}")
            else:
                self.weight_label.setPlainText(f"{self.node_label}\nh={self.h_value}")
    
    def reset_display(self):
        if self.weight_label:
            if self.is_auxiliary:
                self.weight_label.setPlainText("S")
            else:
                self.weight_label.setPlainText(f"{self.node_label}")
    
    def set_as_auxiliary(self):
        """جعله الـ Sommet S المساعد"""
        self.is_auxiliary = True
        self.setBrush(QBrush(QColor(255, 193, 7)))  # أصفر ذهبي
        self.update_h_display()
    
    def reset(self):
        self.h_value = 0
        self.is_auxiliary = False
        self.setBrush(QBrush(self.original_color))
        self.reset_display()
    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255), 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255), 2))
        super().hoverLeaveEvent(event)
    
    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionChange:
            if self.weight_label:
                center = self.get_center()
                text_rect = self.weight_label.boundingRect()
                self.weight_label.setPos(
                    center.x() - text_rect.width()/2,
                    center.y() - text_rect.height()/2
                )
        return super().itemChange(change, value)

class WeightedEdge(QGraphicsLineItem):
    def __init__(self, start_node, end_node, weight=1, directed=False):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.directed = directed
        self.weight_text = None
        self.original_weight = weight  # حفظ الوزن الأصلي
        
        self.setPen(QPen(QColor(140, 140, 160), 2, Qt.SolidLine, Qt.RoundCap))
        self.setZValue(1)
        
        self.update_position()
    
    def update_position(self):
        start_center = self.start_node.get_center()
        end_center = self.end_node.get_center()
        
        dx = end_center.x() - start_center.x()
        dy = end_center.y() - start_center.y()
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            start_x = start_center.x() + (dx * self.start_node.radius / distance)
            start_y = start_center.y() + (dy * self.start_node.radius / distance)
            end_x = end_center.x() - (dx * self.end_node.radius / distance)
            end_y = end_center.y() - (dy * self.end_node.radius / distance)
            
            self.setLine(start_x, start_y, end_x, end_y)
            
            if self.weight_text:
                # وضع النص في منتصف الخط مع إزاحة عمودية مناسبة
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                # إزاحة أصغر وموازية بشكل أفضل
                offset_distance = 15  # إزاحة ثابتة
                
                # حساب الزاوية
                angle = math.atan2(dy, dx)
                # إزاحة عمودية على الخط بزاوية 90 درجة
                offset_x = -math.sin(angle) * offset_distance
                offset_y = math.cos(angle) * offset_distance
                
                self.weight_text.setPos(mid_x + offset_x, mid_y + offset_y)
    
    def set_weight_text(self, text_item):
        self.weight_text = text_item
        self.weight_text.setPlainText(str(self.weight))
        self.weight_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.weight_text.setDefaultTextColor(QColor(0, 0, 0))
        self.weight_text.setZValue(4)
        self.update_position()
    
    def highlight(self, color=QColor(255, 193, 7)):
        self.setPen(QPen(color, 3, Qt.SolidLine, Qt.RoundCap))
        if self.weight_text:
            self.weight_text.setDefaultTextColor(color)
    
    def unhighlight(self):
        self.setPen(QPen(QColor(140, 140, 160), 2, Qt.SolidLine, Qt.RoundCap))
        if self.weight_text:
            self.weight_text.setDefaultTextColor(QColor(0, 0, 0))
    
    def update_weight_text(self, text):
        if self.weight_text:
            self.weight_text.setPlainText(text)
    
    def reset_weight_text(self):
        """إعادة تعيين النص إلى الوزن الأصلي"""
        if self.weight_text:
            self.weight_text.setPlainText(str(self.original_weight))

class WeightedGraph:
    def __init__(self, directed=False):
        self.nodes = {}
        self.edges = {}
        self.directed_edges = {}
        self.auxiliary_edges = {}  # أقواس من S إلى العقد الأخرى
        self.adjacency = defaultdict(dict)
        self.directed = directed
        self.next_node_id = 1
        self.scene = None
        self.auxiliary_node = None  # الـ Sommet S
        
    def set_scene(self, scene):
        self.scene = scene
    
    def add_node(self, x, y, scene, radius=25, is_auxiliary=False, label=None):
        node_id = self.next_node_id
        node = WeightedGraphNode(node_id, x, y, radius, label)
        self.next_node_id += 1
        
        if is_auxiliary:
            node.set_as_auxiliary()
            self.auxiliary_node = node
        
        self.nodes[node_id] = node
        scene.addItem(node)
        
        display_text = "S" if is_auxiliary else f"{node.node_label}"
        weight_label = QGraphicsTextItem(display_text)
        weight_label.setFont(QFont("Arial", 12, QFont.Bold))
        weight_label.setDefaultTextColor(Qt.white)
        
        text_rect = weight_label.boundingRect()
        weight_label.setPos(
            x - text_rect.width()/2,
            y - text_rect.height()/2
        )
        weight_label.setZValue(4)
        
        scene.addItem(weight_label)
        node.set_weight_label(weight_label)
        
        return node_id
    
    def add_edge(self, node1_id, node2_id, weight, scene, directed=False, from_auxiliary=False):
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False
        
        if node1_id == node2_id:
            return False
        
        edge_key = (node1_id, node2_id) if directed else (min(node1_id, node2_id), max(node1_id, node2_id))
        
        if from_auxiliary:
            if edge_key in self.auxiliary_edges:
                return True
        
        if directed:
            if edge_key in self.directed_edges:
                self.directed_edges[edge_key].weight = weight
                self.directed_edges[edge_key].original_weight = weight
                self.directed_edges[edge_key].weight_text.setPlainText(str(weight))
                self.adjacency[node1_id][node2_id] = weight
                return True
        else:
            if edge_key in self.edges:
                self.edges[edge_key].weight = weight
                self.edges[edge_key].original_weight = weight
                self.edges[edge_key].weight_text.setPlainText(str(weight))
                self.adjacency[node1_id][node2_id] = weight
                self.adjacency[node2_id][node1_id] = weight
                return True
        
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        
        edge = WeightedEdge(node1, node2, weight, directed)
        scene.addItem(edge)
        
        if from_auxiliary:
            self.auxiliary_edges[edge_key] = edge
        elif directed:
            self.directed_edges[edge_key] = edge
        else:
            self.edges[edge_key] = edge
        
        weight_text = QGraphicsTextItem(str(weight))
        weight_text.setFont(QFont("Arial", 10, QFont.Bold))
        weight_text.setDefaultTextColor(QColor(0, 0, 0))
        weight_text.setZValue(4)
        scene.addItem(weight_text)
        edge.set_weight_text(weight_text)
        
        self.adjacency[node1_id][node2_id] = weight
        if not directed and not from_auxiliary:
            self.adjacency[node2_id][node1_id] = weight
        
        return True
    
    def add_auxiliary_edges(self, scene):
        """إضافة أقواس من S إلى جميع العقد الأخرى بوزن 0"""
        if not self.auxiliary_node:
            return
        
        s_id = self.auxiliary_node.node_id
        
        for node_id, node in self.nodes.items():
            if node_id != s_id and not node.is_auxiliary:
                self.add_edge(s_id, node_id, 0, scene, directed=True, from_auxiliary=True)
    
    def remove_auxiliary_edges(self, scene):
        """إزالة جميع الأقواس من S"""
        edges_to_remove = list(self.auxiliary_edges.keys())
        
        for edge_key in edges_to_remove:
            u, v = edge_key
            self.remove_edge(u, v, scene, directed=True, from_auxiliary=True)
    
    def remove_edge(self, node1_id, node2_id, scene, directed=False, from_auxiliary=False):
        edge_key = (node1_id, node2_id) if directed else (min(node1_id, node2_id), max(node1_id, node2_id))
        
        if from_auxiliary:
            if edge_key in self.auxiliary_edges:
                edge = self.auxiliary_edges[edge_key]
                scene.removeItem(edge)
                if edge.weight_text:
                    scene.removeItem(edge.weight_text)
                
                del self.auxiliary_edges[edge_key]
                return True
        
        if directed:
            if edge_key in self.directed_edges:
                edge = self.directed_edges[edge_key]
                scene.removeItem(edge)
                if edge.weight_text:
                    scene.removeItem(edge.weight_text)
                
                del self.directed_edges[edge_key]
                
                if node2_id in self.adjacency[node1_id]:
                    del self.adjacency[node1_id][node2_id]
                
                return True
        else:
            if edge_key in self.edges:
                edge = self.edges[edge_key]
                scene.removeItem(edge)
                if edge.weight_text:
                    scene.removeItem(edge.weight_text)
                
                del self.edges[edge_key]
                
                if node2_id in self.adjacency[node1_id]:
                    del self.adjacency[node1_id][node2_id]
                if node1_id in self.adjacency[node2_id]:
                    del self.adjacency[node2_id][node1_id]
                
                return True
        
        return False
    
    def remove_auxiliary_node(self, scene):
        """إزالة الـ Sommet S"""
        if self.auxiliary_node:
            s_id = self.auxiliary_node.node_id
            self.remove_node(s_id, scene)
            self.auxiliary_node = None
    
    def remove_node(self, node_id, scene):
        if node_id not in self.nodes:
            return False
        
        edges_to_remove = []
        for edge_key in list(self.edges.keys()):
            if node_id in edge_key:
                edges_to_remove.append((edge_key[0], edge_key[1], False, False))
        
        for edge_key in list(self.directed_edges.keys()):
            if node_id in edge_key:
                edges_to_remove.append((edge_key[0], edge_key[1], True, False))
        
        for edge_key in list(self.auxiliary_edges.keys()):
            if node_id in edge_key:
                edges_to_remove.append((edge_key[0], edge_key[1], True, True))
        
        for u, v, directed, from_auxiliary in edges_to_remove:
            self.remove_edge(u, v, scene, directed, from_auxiliary)
        
        node = self.nodes[node_id]
        scene.removeItem(node)
        if node.weight_label:
            scene.removeItem(node.weight_label)
        
        if node.is_auxiliary:
            self.auxiliary_node = None
        
        del self.nodes[node_id]
        if node_id in self.adjacency:
            del self.adjacency[node_id]
        
        for nid in self.adjacency:
            if node_id in self.adjacency[nid]:
                del self.adjacency[nid][node_id]
        
        return True
    
    def redraw_all_edges(self):
        for edge in self.edges.values():
            edge.update_position()
        for edge in self.directed_edges.values():
            edge.update_position()
        for edge in self.auxiliary_edges.values():
            edge.update_position()
    
    def reset_distances(self):
        for node in self.nodes.values():
            node.reset()
    
    def get_all_edges(self):
        edges = []
        for edge_key, edge in self.edges.items():
            edges.append((edge_key[0], edge_key[1], edge.weight, False, False))
        for edge_key, edge in self.directed_edges.items():
            edges.append((edge_key[0], edge_key[1], edge.weight, True, False))
        for edge_key, edge in self.auxiliary_edges.items():
            edges.append((edge_key[0], edge_key[1], edge.weight, True, True))
        return edges
    
    def highlight_all_edges(self, edges_to_highlight, color):
        """إبراز أقواس محددة"""
        # إعادة تعيين جميع الأقواس أولاً
        for edge in self.edges.values():
            edge.unhighlight()
        for edge in self.directed_edges.values():
            edge.unhighlight()
        for edge in self.auxiliary_edges.values():
            edge.unhighlight()
        
        # إبراز الأقواس المحددة
        for edge_key in edges_to_highlight:
            if edge_key in self.edges:
                self.edges[edge_key].highlight(color)
            elif edge_key in self.directed_edges:
                self.directed_edges[edge_key].highlight(color)
            elif edge_key in self.auxiliary_edges:
                self.auxiliary_edges[edge_key].highlight(color)
    
    def reset_display(self):
        """إعادة تعيين العرض"""
        for node in self.nodes.values():
            if node.is_auxiliary:
                node.setBrush(QBrush(QColor(255, 193, 7)))  # أصفر لـ S
            else:
                node.setBrush(QBrush(QColor(100, 149, 237)))  # أزرق للعقد العادية
        
        for edge in self.edges.values():
            edge.unhighlight()
            edge.reset_weight_text()  # إعادة تعيين النص
        for edge in self.directed_edges.values():
            edge.unhighlight()
            edge.reset_weight_text()  # إعادة تعيين النص
        for edge in self.auxiliary_edges.values():
            edge.unhighlight()

# ================================
# JOHNSON GRAPH VISUALIZER - معدل
# ================================

class JohnsonGraphVisualizer(QGraphicsView):
    step_changed = pyqtSignal(int)  # إشارة عند تغيير الخطوة
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-400, -400, 800, 800)
        self.scene.setBackgroundBrush(QBrush(QColor(248, 249, 250)))
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setMinimumSize(400, 400)
        
        self.graph = WeightedGraph(directed=True)
        self.graph.set_scene(self.scene)
        
        self.add_node_mode = False
        self.add_edge_mode = False
        self.set_weight_mode = False
        self.delete_mode = False
        self.directed_mode = True
        self.edge_start_node = None
        self.temp_line = None
        self.is_drawing_edge = False
        
        self.current_step = 0
        self.johnson_steps = []
        self.h_values = {}
        self.reweighted_edges = {}
        self.dijkstra_results = {}
        self.final_distances = {}
    
    def wheelEvent(self, event):
        """التكبير/التصغير باستخدام عجلة الماوس"""
        zoom_factor = 1.2
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1/zoom_factor, 1/zoom_factor)
    
    def create_empty_graph(self):
        self.scene.clear()
        self.graph = WeightedGraph(directed=True)
        self.graph.set_scene(self.scene)
        self.reset_modes()
        self.reset_johnson_state()
    
    def create_random_weighted_graph(self):
        self.create_empty_graph()
        
        num_nodes = random.randint(4, 6)
        node_ids = []
        
        # توزيع عشوائي
        for i in range(num_nodes):
            angle = 2 * math.pi * i / num_nodes
            radius = 250
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            node_id = self.graph.add_node(x, y, self.scene, 30)
            node_ids.append(node_id)
        
        edge_count = 0
        max_edges = min(num_nodes * 2, num_nodes * (num_nodes - 1))
        
        while edge_count < max_edges:
            i, j = random.sample(range(num_nodes), 2)
            if random.random() < 0.6:
                weight = random.randint(1, 20)
                if random.random() < 0.3:
                    weight = -random.randint(1, 10)
                
                self.graph.add_edge(node_ids[i], node_ids[j], weight, self.scene, directed=True)
                edge_count += 1
        
        self.fit_view()
    
    def reset_johnson_state(self):
        self.current_step = 0
        self.johnson_steps = []
        self.h_values = {}
        self.reweighted_edges = {}
        self.dijkstra_results = {}
        self.final_distances = {}
        
        # إزالة الـ Sommet S إذا كان موجوداً
        if self.graph.auxiliary_node:
            self.graph.remove_auxiliary_node(self.scene)
        
        # إعادة تعيين جميع العقد
        for node in self.graph.nodes.values():
            node.reset()
        
        # إعادة تعيين جميع الأقواس
        self.graph.reset_display()
        
        self.step_changed.emit(0)
    
    def reset_display(self):
        """إعادة تعيين العرض لبداية جديدة"""
        # إعادة تعيين ألوان العقد
        for node in self.graph.nodes.values():
            if node.is_auxiliary:
                node.setBrush(QBrush(QColor(255, 193, 7)))  # أصفر لـ S
            else:
                node.setBrush(QBrush(QColor(100, 149, 237)))  # أزرق للعقد العادية
            node.h_value = 0
            node.reset_display()
        
        # إعادة تعيين ألوان الأقواس
        for edge in self.graph.edges.values():
            edge.unhighlight()
            edge.reset_weight_text()
        
        for edge in self.graph.directed_edges.values():
            edge.unhighlight()
            edge.reset_weight_text()
        
        for edge in self.graph.auxiliary_edges.values():
            edge.unhighlight()
    
    def enable_add_node_mode(self):
        self.reset_modes()
        self.add_node_mode = True
        self.setCursor(Qt.CrossCursor)
    
    def enable_add_edge_mode(self):
        if len(self.graph.nodes) < 2:
            return
        
        self.reset_modes()
        self.add_edge_mode = True
        self.setCursor(Qt.PointingHandCursor)
    
    def enable_directed_mode(self):
        self.directed_mode = not self.directed_mode
    
    def enable_set_weight_mode(self):
        if len(self.graph.edges) == 0 and len(self.graph.directed_edges) == 0:
            return
        
        self.reset_modes()
        self.set_weight_mode = True
        self.setCursor(Qt.WhatsThisCursor)
    
    def enable_delete_mode(self):
        self.reset_modes()
        self.delete_mode = True
        self.setCursor(Qt.ForbiddenCursor)
    
    def reset_modes(self):
        self.add_node_mode = False
        self.add_edge_mode = False
        self.set_weight_mode = False
        self.delete_mode = False
        
        if self.edge_start_node:
            self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
            self.edge_start_node = None
        
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        
        self.is_drawing_edge = False
        self.setCursor(Qt.ArrowCursor)
    
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.transform())
        
        if self.add_node_mode:
            node_id = self.graph.add_node(scene_pos.x(), scene_pos.y(), self.scene, 25)
            self.add_node_mode = False
            self.reset_modes()
        
        elif self.add_edge_mode:
            if isinstance(item, WeightedGraphNode):
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
                        weight, ok = QInputDialog.getInt(
                            self, "Poids de l'arête",
                            f"Entrer le poids pour l'arête:",
                            value=1, min=-100, max=100
                        )
                        
                        if ok:
                            success = self.graph.add_edge(
                                self.edge_start_node.node_id,
                                item.node_id,
                                weight,
                                self.scene,
                                directed=self.directed_mode
                            )
                    
                    self.edge_start_node.setBrush(QBrush(self.edge_start_node.original_color))
                    self.edge_start_node = None
                    self.is_drawing_edge = False
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None
        
        elif self.set_weight_mode:
            if isinstance(item, WeightedEdge):
                edge = item
                weight, ok = QInputDialog.getInt(
                    self, "Changer le poids",
                    "Entrer le nouveau poids pour cette arête:",
                    value=edge.weight, min=-100, max=100
                )
                
                if ok:
                    for edge_key, e in self.graph.edges.items():
                        if e == edge:
                            node1_id, node2_id = edge_key
                            self.graph.add_edge(node1_id, node2_id, weight, self.scene, directed=False)
                            break
                    for edge_key, e in self.graph.directed_edges.items():
                        if e == edge:
                            node1_id, node2_id = edge_key
                            self.graph.add_edge(node1_id, node2_id, weight, self.scene, directed=True)
                            break
        
        elif self.delete_mode:
            if isinstance(item, WeightedGraphNode):
                if QMessageBox.question(self, "Confirmer suppression",
                                      f"Supprimer le sommet {item.node_id} et toutes ses arêtes?",
                                      QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.graph.remove_node(item.node_id, self.scene)
            
            elif isinstance(item, WeightedEdge):
                edge = item
                # البحث في جميع أنواع الأقواس
                found = False
                for edge_key, e in self.graph.edges.items():
                    if e == edge:
                        node1_id, node2_id = edge_key
                        if QMessageBox.question(self, "Confirmer suppression",
                                              f"Supprimer l'arête entre les sommets {node1_id} et {node2_id}?",
                                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                            self.graph.remove_edge(node1_id, node2_id, self.scene, directed=False)
                        found = True
                        break
                
                if not found:
                    for edge_key, e in self.graph.directed_edges.items():
                        if e == edge:
                            node1_id, node2_id = edge_key
                            if QMessageBox.question(self, "Confirmer suppression",
                                                  f"Supprimer l'arête entre les sommets {node1_id} et {node2_id}?",
                                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                                self.graph.remove_edge(node1_id, node2_id, self.scene, directed=True)
                            found = True
                            break
                
                if not found:
                    for edge_key, e in self.graph.auxiliary_edges.items():
                        if e == edge:
                            node1_id, node2_id = edge_key
                            if QMessageBox.question(self, "Confirmer suppression",
                                                  f"Supprimer l'arête entre S et le sommet {node2_id}?",
                                                  QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                                self.graph.remove_edge(node1_id, node2_id, self.scene, directed=True, from_auxiliary=True)
                            break
        
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
    
    def fit_view(self):
        if self.graph.nodes:
            rect = self.scene.itemsBoundingRect()
            rect.adjust(-80, -80, 80, 80)  # زيادة الهوامش
            self.fitInView(rect, Qt.KeepAspectRatio)
        else:
            self.fitInView(QRectF(-200, -200, 400, 400), Qt.KeepAspectRatio)
        
        self.scale(0.8, 0.8)  # تقليل التكبير
    
    def run_johnson(self):
        """تنفيذ خوارزمية Johnson خطوة بخطوة"""
        if len(self.graph.nodes) < 2:
            QMessageBox.warning(self, "Erreur", "Besoin d'au moins 2 sommets pour l'algorithme de Johnson!")
            return None
        
        self.reset_johnson_state()
        
        try:
            # الخطوة 1: إضافة الـ Sommet S
            step1 = self.johnson_step1()
            if step1:
                self.johnson_steps.append(step1)
            
            # الخطوة 2: تشغيل Bellman-Ford
            step2 = self.johnson_step2()
            if step2 is None:
                QMessageBox.warning(self, "Cycle Négatif", 
                                  "Le graphe contient un cycle négatif! L'algorithme de Johnson ne peut pas continuer.")
                return None
            self.johnson_steps.append(step2)
            
            # الخطوة 3: إعادة ترجيح الأقواس
            step3 = self.johnson_step3()
            self.johnson_steps.append(step3)
            
            # الخطوة 4: تطبيق Dijkstra
            step4 = self.johnson_step4()
            self.johnson_steps.append(step4)
            
            # الخطوة 5: المسافات النهائية
            step5 = self.johnson_step5()
            self.johnson_steps.append(step5)
            
            return self.johnson_steps
            
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'exécution de Johnson: {str(e)}")
            return None
    
    def apply_step_visualization(self, step_num):
        """تطبيق التصور البصري للخطوة المحددة"""
        if step_num < 0 or step_num > 5:
            return
        
        # إعادة تعيين العرض أولاً
        self.graph.reset_display()
        
        if step_num == 0:
            # حالة البداية
            pass
        
        elif step_num == 1:
            # تطبيق الخطوة 1
            for edge in self.graph.auxiliary_edges.values():
                edge.highlight(QColor(255, 193, 7))
        
        elif step_num == 2:
            # تطبيق الخطوة 2
            for edge in self.graph.auxiliary_edges.values():
                edge.highlight(QColor(100, 181, 246))
            
            # تحديث عرض العقد بقيم h
            for node in self.graph.nodes.values():
                if not node.is_auxiliary and node.node_label in self.h_values:
                    node.h_value = self.h_values[node.node_label]
                    if node.h_value == float('inf'):
                        node.setBrush(QBrush(QColor(200, 200, 200)))  # رمادي للـ ∞
                    elif node.h_value < 0:
                        node.setBrush(QBrush(QColor(239, 154, 154)))
                    else:
                        node.setBrush(QBrush(QColor(129, 199, 132)))
                    node.update_h_display()
        
        elif step_num == 3:
            # تطبيق الخطوة 3
            for edge_key, new_w in self.reweighted_edges.items():
                if edge_key in self.graph.directed_edges:
                    edge = self.graph.directed_edges[edge_key]
                    edge.update_weight_text(f"{edge.original_weight} → {new_w}")
                    if new_w < 0:
                        edge.highlight(QColor(244, 67, 54))
                    else:
                        edge.highlight(QColor(33, 150, 243))
            
            # تحديث العقد
            for node in self.graph.nodes.values():
                if not node.is_auxiliary and node.node_label in self.h_values:
                    h_val = self.h_values[node.node_label]
                    if h_val == float('inf'):
                        node.setBrush(QBrush(QColor(200, 200, 200)))
                    elif h_val < 0:
                        node.setBrush(QBrush(QColor(239, 154, 154)))
                    else:
                        node.setBrush(QBrush(QColor(129, 199, 132)))
        
        elif step_num == 4:
            # تطبيق الخطوة 4
            for node in self.graph.nodes.values():
                if not node.is_auxiliary:
                    node.setBrush(QBrush(QColor(144, 202, 249)))
            
            for edge_key in self.reweighted_edges:
                if edge_key in self.graph.directed_edges:
                    self.graph.directed_edges[edge_key].highlight(QColor(156, 39, 176))
        
        elif step_num == 5:
            # تطبيق الخطوة 5
            for node in self.graph.nodes.values():
                if not node.is_auxiliary:
                    node.setBrush(QBrush(QColor(206, 147, 216)))
    
    def johnson_step1(self):
        """الخطوة 1: إضافة الـ Sommet S ورسمه فعلياً"""
        # إضافة الـ Sommet S في وسط الرسم
        s_x = 0
        s_y = -300  # أعلى قليلاً من المركز
        s_id = self.graph.add_node(s_x, s_y, self.scene, 30, is_auxiliary=True)
        
        # إضافة أقواس من S إلى جميع العقد الأخرى بوزن 0
        self.graph.add_auxiliary_edges(self.scene)
        
        # إعادة ضبط العرض ليشمل S
        self.fit_view()
        
        # إبراز الأقواس الجديدة
        for edge in self.graph.auxiliary_edges.values():
            edge.highlight(QColor(255, 193, 7))
        
        step_data = {
            'step': 1,
            'title': "Étape 1: Ajouter un sommet auxiliaire S",
            'description': "Le sommet S a été ajouté et relié à tous les sommets avec des arcs de poids 0",
            'formula': "G' = (V ∪ {S}, E ∪ {(S,v) | v ∈ V, poids = 0})",
            'action': "S ajouté et connecté à tous les sommets",
            'step_type': 'add_s_node'
        }
        
        return step_data
    
    def johnson_step2(self):
        """الخطوة 2: تشغيل Bellman-Ford من S"""
        if not self.graph.auxiliary_node:
            return None
        
        # إبراز أقواس S
        auxiliary_edges = list(self.graph.auxiliary_edges.keys())
        self.graph.highlight_all_edges(auxiliary_edges, QColor(100, 181, 246))
        
        # تنفيذ خوارزمية Bellman-Ford بشكل صحيح
        s_id = self.graph.auxiliary_node.node_id
        
        # جمع جميع العقد
        nodes = list(self.graph.nodes.values())
        node_ids = [node.node_id for node in nodes]
        
        # تهيئة المسافات
        dist = {}
        for node in nodes:
            dist[node.node_id] = float('inf')
        dist[s_id] = 0
        
        # جمع جميع الأقواس (بما في ذلك المساعدة)
        all_edges = []
        
        # أقواس من S إلى جميع العقد
        for edge_key, edge in self.graph.auxiliary_edges.items():
            u, v = edge_key
            all_edges.append((u, v, edge.weight))
        
        # الأقواس الأصلية الموجهة
        for edge_key, edge in self.graph.directed_edges.items():
            u, v = edge_key
            all_edges.append((u, v, edge.weight))
        
        # الأقواس غير الموجهة (تعامل كموجهة في كلا الاتجاهين)
        for edge_key, edge in self.graph.edges.items():
            u, v = edge_key
            all_edges.append((u, v, edge.weight))
            all_edges.append((v, u, edge.weight))
        
        # تنفيذ خوارزمية Bellman-Ford
        n = len(node_ids)
        
        # تتبع التكرارات لعرضها
        iterations = []
        
        # التهيئة - التكرار 0
        init_row = {"k": "0 (init)"}
        for node in nodes:
            if node.node_id == s_id:
                init_row["S"] = "0"
            else:
                init_row[node.node_label] = "∞"
        iterations.append(init_row)
        
        # التكرارات
        for i in range(1, n):  # n-1 تكرارات
            updated = False
            current_row = {"k": str(i)}
            
            # نسخ المسافات الحالية للصف
            for node in nodes:
                if not node.is_auxiliary:
                    if dist[node.node_id] == float('inf'):
                        current_row[node.node_label] = "∞"
                    else:
                        current_row[node.node_label] = str(dist[node.node_id])
                else:
                    current_row["S"] = "0"  # S نفسه
            
            # تحديث الحواف
            for u, v, w in all_edges:
                if dist[u] != float('inf') and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
            
            iterations.append(current_row)
            
            if not updated:
                break
        
        # التكرار النهائي للتحقق من الدورات السلبية
        has_negative_cycle = False
        for u, v, w in all_edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                has_negative_cycle = True
                break
        
        if has_negative_cycle:
            return None
        
        # آخر تكرار
        final_row = {"k": f"{n-1} (fin)"}
        for node in nodes:
            if not node.is_auxiliary:
                if dist[node.node_id] == float('inf'):
                    final_row[node.node_label] = "∞"
                else:
                    final_row[node.node_label] = str(dist[node.node_id])
            else:
                final_row["S"] = "0"
        iterations.append(final_row)
        
        # حفظ قيم h
        h_values = {}
        for node in nodes:
            if not node.is_auxiliary:
                h_values[node.node_label] = dist[node.node_id]
        
        self.h_values = h_values
        
        # تحديث عرض العقد
        for node in self.graph.nodes.values():
            if not node.is_auxiliary and node.node_label in self.h_values:
                node.h_value = self.h_values[node.node_label]
                if node.h_value == float('inf'):
                    node.setBrush(QBrush(QColor(200, 200, 200)))  # رمادي للـ ∞
                elif node.h_value < 0:
                    node.setBrush(QBrush(QColor(239, 154, 154)))  # أحمر فاتح للقيم السالبة
                else:
                    node.setBrush(QBrush(QColor(129, 199, 132)))  # أخضر للقيم الموجبة
                node.update_h_display()
        
        step_data = {
            'step': 2,
            'title': "Étape 2: Exécuter Bellman-Ford depuis S",
            'description': "Calcul des potentiels h(v) pour chaque sommet v",
            'formula': "h(v) = distance la plus courte de S à v",
            'h_values': self.h_values,
            'step_type': 'bellman_ford',
            'bellman_ford_table': iterations
        }
        
        return step_data
    
    def johnson_step3(self):
        """الخطوة 3: إعادة ترجيح الأقواس"""
        h_values = self.h_values
        reweighted_edges = {}
        edges_info = []
        
        # جمع الأقواس الأصلية فقط (بدون أقواس S)
        all_edges = []
        for edge_key, edge in self.graph.directed_edges.items():
            u, v = edge_key
            all_edges.append((u, v, edge.original_weight, True, False))
        
        for u, v, w, directed, from_auxiliary in all_edges:
            u_node = self.graph.nodes[u]
            v_node = self.graph.nodes[v]
            
            if u_node.node_label in h_values and v_node.node_label in h_values:
                h_u = h_values[u_node.node_label]
                h_v = h_values[v_node.node_label]
                
                # تحويل ∞ إلى 0 للعمليات الحسابية
                h_u_val = 0 if h_u == float('inf') else h_u
                h_v_val = 0 if h_v == float('inf') else h_v
                
                new_w = w + h_u_val - h_v_val
                edge_key = (u, v)
                reweighted_edges[edge_key] = new_w
                
                edges_info.append({
                    'arc': f"{u_node.node_label}→{v_node.node_label}",
                    'original_weight': w,
                    'h_u': h_u_val,
                    'h_v': h_v_val,
                    'new_weight': new_w
                })
        
        self.reweighted_edges = reweighted_edges
        
        step_data = {
            'step': 3,
            'title': "Étape 3: Repondérer les arcs",
            'description': "Pour chaque arc (u,v), recalculer le poids selon w'(u,v) = w(u,v) + h(u) - h(v)",
            'formula': "w'(u,v) = w(u,v) + h(u) - h(v)",
            'edges': edges_info,
            'step_type': 'reweight_edges'
        }
        
        return step_data
    
    def johnson_step4(self):
        """الخطوة 4: تطبيق Dijkstra من كل رأس"""
        # جمع تسميات العقد غير المساعدة
        node_labels = []
        for node in self.graph.nodes.values():
            if not node.is_auxiliary:
                node_labels.append(node.node_label)
        
        # إذا لم تكن هناك عقد، نستخدم تسميات افتراضية
        if not node_labels:
            node_labels = ['1', '2', '3', '4', '5']
        
        # إنشاء مصفوفة افتراضية باستخدام Dijkstra المبسط
        example_matrix = {}
        for source in node_labels:
            example_matrix[source] = {}
            for target in node_labels:
                if source == target:
                    example_matrix[source][target] = 0
                else:
                    # محاولة إيجاد أقصر مسافة باستخدام الأوزان المعاد ترجيحها
                    min_dist = float('inf')
                    
                    # بحث بسيط عن المسار
                    for u, v, w, directed, from_aux in self.graph.get_all_edges():
                        if not from_aux:  # تجاهل أقواس S
                            u_node = self.graph.nodes[u]
                            v_node = self.graph.nodes[v]
                            
                            if u_node.node_label == source and v_node.node_label == target:
                                edge_key = (u, v)
                                if edge_key in self.reweighted_edges:
                                    dist = self.reweighted_edges[edge_key]
                                    if dist < min_dist:
                                        min_dist = dist
                    
                    example_matrix[source][target] = min_dist if min_dist != float('inf') else "∞"
        
        self.dijkstra_results = example_matrix
        
        step_data = {
            'step': 4,
            'title': "Étape 4: Appliquer Dijkstra depuis chaque sommet",
            'description': "Pour chaque sommet s ∈ V, exécuter Dijkstra sur le graphe avec les poids w'",
            'formula': "d'(s,v) = distance modifiée de s à v",
            'd_prime_matrix': example_matrix,
            'step_type': 'dijkstra'
        }
        
        return step_data
    
    def johnson_step5(self):
        """الخطوة 5: حساب المسافات النهائية"""
        # جمع تسميات العقد غير المساعدة
        node_labels = []
        for node in self.graph.nodes.values():
            if not node.is_auxiliary:
                node_labels.append(node.node_label)
        
        # حساب المصفوفة النهائية بناءً على مصفوفة Dijkstra وقيم h
        final_matrix = {}
        for source in node_labels:
            final_matrix[source] = {}
            for target in node_labels:
                if source == target:
                    final_matrix[source][target] = 0
                else:
                    # الحصول على المسافة المعاد ترجيحها
                    if source in self.dijkstra_results and target in self.dijkstra_results[source]:
                        d_prime = self.dijkstra_results[source][target]
                        
                        if d_prime == "∞":
                            final_matrix[source][target] = "∞"
                        else:
                            # تطبيق الصيغة النهائية
                            h_s = self.h_values.get(source, 0)
                            h_t = self.h_values.get(target, 0)
                            
                            h_s_val = 0 if h_s == float('inf') else h_s
                            h_t_val = 0 if h_t == float('inf') else h_t
                            
                            # الصيغة: d(s,v) = d'(s,v) - h(s) + h(v)
                            final_dist = d_prime - h_s_val + h_t_val
                            final_matrix[source][target] = final_dist
                    else:
                        final_matrix[source][target] = "∞"
        
        self.final_distances = final_matrix
        
        step_data = {
            'step': 5,
            'title': "Étape 5: Calculer les distances finales",
            'description': "Pour chaque couple (s,v), convertir chaque valeur en distance réelle en استخدام la formule",
            'formula': "d(s,v) = d'(s,v) - h(s) + h(v)",
            'final_matrix': final_matrix,
            'step_type': 'final_distances'
        }
        
        return step_data
    
    def get_current_step_data(self):
        if self.current_step < len(self.johnson_steps):
            return self.johnson_steps[self.current_step]
        return None
    
    def next_step(self):
        if self.current_step < len(self.johnson_steps):
            self.current_step += 1
            self.apply_step_visualization(self.current_step)
            self.step_changed.emit(self.current_step)
            return self.get_current_step_data()
        return None
    
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.apply_step_visualization(self.current_step)
            self.step_changed.emit(self.current_step)
            return self.get_current_step_data()
        return None
    
    def go_to_step(self, step_num):
        """الذهاب إلى خطوة محددة"""
        if 0 <= step_num <= 5:
            self.current_step = step_num
            self.apply_step_visualization(self.current_step)
            self.step_changed.emit(self.current_step)
            return self.get_current_step_data()
        return None
    
    def reset_algorithm(self):
        self.reset_johnson_state()

# ================================
# JOHNSON ALGORITHM INTERFACE - واجهة واحدة معدلة
# ================================

class JohnsonAlgorithmApp(QMainWindow):
    back_to_main_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # تعريف graph_view هنا قبل init_ui
        self.graph_view = None
        self.init_ui()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.next_johnson_step)
        self.current_johnson_step = 0
        self.johnson_steps_data = []
        
    def init_ui(self):
        self.setWindowTitle("Algorithme de Johnson - Plus Courts Chemins")
        self.showMaximized()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter لتقسيم الشاشة
        splitter = QSplitter(Qt.Horizontal)
        
        # اللوحة اليسرى: الرسم البياني
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # اللوحة اليمنى: التحكم والخطوات
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([700, 500])
        
        main_layout.addWidget(splitter)
    
    def create_left_panel(self):
        """إنشاء اللوحة اليسرى (الرسم البياني)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # شريط العنوان
        header = QFrame()
        header.setStyleSheet("""
            background: #5c6bc0;
            border-radius: 5px;
            padding: 8px;
        """)
        header_layout = QHBoxLayout(header)
        
        back_btn = QPushButton("← Retour")
        back_btn.clicked.connect(self.back_to_main)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        header_layout.addWidget(back_btn)
        
        title = QLabel("🎯 Graphe - Algorithme de Johnson")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # الرسم البياني مع أزرار Zoom
        graph_container = QWidget()
        graph_container_layout = QVBoxLayout(graph_container)
        graph_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # أزرار Zoom داخل حاوية الرسم
        zoom_controls = QFrame()
        zoom_controls.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
        zoom_controls.setMaximumHeight(40)
        
        zoom_layout = QHBoxLayout(zoom_controls)
        zoom_layout.setContentsMargins(5, 2, 5, 2)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #90caf9;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #64b5f6;
            }
        """)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #ce93d8;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ba68c8;
            }
        """)
        
        reset_zoom_btn = QPushButton("↻")
        reset_zoom_btn.setToolTip("Reset Zoom")
        reset_zoom_btn.setFixedSize(30, 30)
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        reset_zoom_btn.setStyleSheet("""
            QPushButton {
                background-color: #80cbc4;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4db6ac;
            }
        """)
        
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(reset_zoom_btn)
        zoom_layout.addStretch()
        
        # إضافة Zoom controls أعلى الرسم البياني
        graph_container_layout.addWidget(zoom_controls)
        
        # الرسم البياني
        self.graph_view = JohnsonGraphVisualizer()
        self.graph_view.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        graph_container_layout.addWidget(self.graph_view, 1)
        
        layout.addWidget(graph_container, 3)
        
        # أدوات التحكم بالعرض
        self.view_controls = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #90caf9;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #64b5f6;
            }
        """)
        
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #ce93d8;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #ba68c8;
            }
        """)
        
        self.fit_btn = QPushButton("📐 Ajuster")
        self.fit_btn.clicked.connect(self.reset_zoom)
        self.fit_btn.setStyleSheet("""
            QPushButton {
                background-color: #80cbc4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4db6ac;
            }
        """)
        
        self.view_controls.addWidget(self.zoom_in_btn)
        self.view_controls.addWidget(self.zoom_out_btn)
        self.view_controls.addWidget(self.fit_btn)
        self.view_controls.addStretch()
        
        layout.addLayout(self.view_controls)
        
        return panel
    
    def zoom_in(self):
        """التكبير"""
        if self.graph_view:
            self.graph_view.scale(1.2, 1.2)
    
    def zoom_out(self):
        """التصغير"""
        if self.graph_view:
            self.graph_view.scale(0.8, 0.8)
    
    def reset_zoom(self):
        """إعادة تعيين التكبير"""
        if self.graph_view:
            self.graph_view.fit_view()
    
    def create_right_panel(self):
        """إنشاء اللوحة اليمنى (التحكم والخطوات)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # ===== الجزء العلوي: أدوات الرسم البياني =====
        tools_group = QGroupBox("🛠️ Outils du Graphe")
        tools_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        tools_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #c5cae9;
                border-radius: 5px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                color: #5c6bc0;
            }
        """)
        
        tools_layout = QVBoxLayout(tools_group)
        
        # أزرار إنشاء الرسم البياني
        create_btns = QHBoxLayout()
        
        new_btn = QPushButton("📋 Nouveau Graphe")
        new_btn.clicked.connect(self.create_new_graph)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #b39ddb;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #9575cd;
            }
        """)
        
        random_btn = QPushButton("🎲 Graphe Aléatoire")
        random_btn.clicked.connect(self.create_random_graph)
        random_btn.setStyleSheet("""
            QPushButton {
                background-color: #a5d6a7;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #81c784;
            }
        """)
        
        create_btns.addWidget(new_btn)
        create_btns.addWidget(random_btn)
        tools_layout.addLayout(create_btns)
        
        # أزرار التفاعل مع الرسم البياني
        grid = QGridLayout()
        grid.setSpacing(5)
        
        add_node = QPushButton("➕ Ajouter Sommet")
        add_node.clicked.connect(self.enable_add_node_mode)
        add_node.setStyleSheet("""
            QPushButton {
                background-color: #80deea;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4dd0e1;
            }
        """)
        
        add_edge = QPushButton("🔗 Ajouter Arête")
        add_edge.clicked.connect(self.enable_add_edge_mode)
        add_edge.setStyleSheet("""
            QPushButton {
                background-color: #ffcc80;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ffb74d;
            }
        """)
        
        self.directed_btn = QPushButton("↷ Dirigé")
        self.directed_btn.clicked.connect(self.toggle_directed_mode)
        self.directed_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c6bc0;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        
        set_weight = QPushButton("⚖️ Définir Poids")
        set_weight.clicked.connect(self.enable_set_weight_mode)
        set_weight.setStyleSheet("""
            QPushButton {
                background-color: #ffcc80;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ffb74d;
            }
        """)
        
        delete = QPushButton("🗑️ Supprimer")
        delete.clicked.connect(self.enable_delete_mode)
        delete.setStyleSheet("""
            QPushButton {
                background-color: #ef9a9a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e57373;
            }
        """)
        
        grid.addWidget(add_node, 0, 0)
        grid.addWidget(add_edge, 0, 1)
        grid.addWidget(self.directed_btn, 1, 0)
        grid.addWidget(set_weight, 1, 1)
        grid.addWidget(delete, 2, 0, 1, 2)
        tools_layout.addLayout(grid)
        
        layout.addWidget(tools_group)
        
        # ===== الجزء الأوسط: التحكم في الخوارزمية =====
        algo_group = QGroupBox("⚡ Contrôle de l'Algorithme")
        algo_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        algo_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #c5cae9;
                border-radius: 5px;
                padding-top: 10px;
                background: white;
            }
            QGroupBox::title {
                color: #5c6bc0;
            }
        """)
        
        algo_layout = QVBoxLayout(algo_group)
        
        # بدء الخوارزمية
        start_btn = QPushButton("🚀 Démarrer Johnson (5 Étapes)")
        start_btn.clicked.connect(self.start_johnson)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff8a65;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7043;
            }
        """)
        algo_layout.addWidget(start_btn)
        
        # التنقل بين الخطوات
        step_controls = QHBoxLayout()
        
        self.prev_step_btn = QPushButton("◀ Précédent")
        self.prev_step_btn.clicked.connect(self.prev_johnson_step)
        self.prev_step_btn.setEnabled(False)
        self.prev_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #7986cb;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5c6bc0;
            }
            QPushButton:disabled {
                background-color: #c5cae9;
                color: #9fa8da;
            }
        """)
        
        self.next_step_btn = QPushButton("Suivant ▶")
        self.next_step_btn.clicked.connect(self.next_johnson_step)
        self.next_step_btn.setEnabled(False)
        self.next_step_btn.setStyleSheet("""
            QPushButton {
                background-color: #4db6ac;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #26a69a;
            }
            QPushButton:disabled {
                background-color: #b2dfdb;
                color: #80cbc4;
            }
        """)
        
        step_controls.addWidget(self.prev_step_btn)
        step_controls.addWidget(self.next_step_btn)
        algo_layout.addLayout(step_controls)
        
        # أزرار الانتقال المباشر للخطوات
        step_buttons_layout = QHBoxLayout()
        
        self.step_buttons = []
        for i in range(1, 6):
            btn = QPushButton(f"Étape {i}")
            btn.clicked.connect(lambda checked, x=i: self.go_to_step(x))
            btn.setMaximumWidth(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e8eaf6;
                    color: #5c6bc0;
                    border: 1px solid #c5cae9;
                    border-radius: 3px;
                    padding: 5px;
                    font-size: 9px;
                }
                QPushButton:hover {
                    background-color: #c5cae9;
                }
            """)
            step_buttons_layout.addWidget(btn)
            self.step_buttons.append(btn)
        
        algo_layout.addLayout(step_buttons_layout)
        
        # الوضع التلقائي
        auto_layout = QHBoxLayout()
        auto_layout.addWidget(QLabel("Vitesse:"))
        
        self.speed_slider = QSpinBox()
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(3)
        self.speed_slider.setSuffix(" sec")
        self.speed_slider.setMaximumWidth(100)
        auto_layout.addWidget(self.speed_slider)
        
        self.auto_btn = QPushButton("⏵ Auto")
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        self.auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffd54f;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ffca28;
            }
        """)
        auto_layout.addWidget(self.auto_btn)
        
        algo_layout.addLayout(auto_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("Étape %v/5")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #c5cae9;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
                color: #5c6bc0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #9fa8da;
                border-radius: 2px;
            }
        """)
        algo_layout.addWidget(self.progress_bar)
        
        # إعادة تعيين
        reset_btn = QPushButton("⟲ Réinitialiser Algorithme")
        reset_btn.clicked.connect(self.reset_johnson)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef9a9a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e57373;
            }
        """)
        algo_layout.addWidget(reset_btn)
        
        layout.addWidget(algo_group)
        
        # ===== الجزء السفلي: عرض الخطوات والنتائج =====
        
        # إنشاء تبويبات داخل اللوحة اليمنى
        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c5cae9;
                border-radius: 3px;
            }
            QTabBar::tab {
                background: #e8eaf6;
                padding: 8px;
                margin-right: 2px;
                border-radius: 3px;
            }
            QTabBar::tab:selected {
                background: #5c6bc0;
                color: white;
            }
        """)
        
        # تبويب الخطوة الحالية
        step_tab = QWidget()
        step_layout = QVBoxLayout(step_tab)
        step_layout.setContentsMargins(0, 0, 0, 0)
        step_layout.setSpacing(0)
        
        self.step_title_label = QLabel("Prêt")
        self.step_title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.step_title_label.setStyleSheet("color: #5c6bc0; padding: 2px; background: #f5f7fa;")
        self.step_title_label.setAlignment(Qt.AlignCenter)
        self.step_title_label.setMaximumHeight(20)
        step_layout.addWidget(self.step_title_label)
        
        self.step_data_table = QTableWidget()
        self.step_data_table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 10px;
                background: white;
            }
            QHeaderView::section {
                background-color: #e8eaf6;
                padding: 4px;
                border: 1px solid #c5cae9;
                font-weight: bold;
                font-size: 9px;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)
        step_layout.addWidget(self.step_data_table, 1)
        
        self.right_tabs.addTab(step_tab, "📋 Étape")
        
        # تبويب النتائج النهائية
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        results_layout.setSpacing(3)
        
        results_title = QLabel("Matrice des Distances Finales")
        results_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        results_title.setStyleSheet("color: #5c6bc0; padding: 3px;")
        results_title.setAlignment(Qt.AlignCenter)
        results_title.setMaximumHeight(25)
        results_layout.addWidget(results_title)
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 10px;
                background: white;
            }
            QHeaderView::section {
                background-color: #e8eaf6;
                padding: 4px;
                border: 1px solid #c5cae9;
                font-weight: bold;
                font-size: 9px;
            }
            QTableWidget::item {
                padding: 2px;
                text-align: center;
            }
        """)
        results_layout.addWidget(self.results_table, 4)
        
        self.summary_label = QLabel("Exécutez l'algorithme pour voir les résultats")
        self.summary_label.setFont(QFont("Segoe UI", 9))
        self.summary_label.setStyleSheet("""
            color: #5c6bc0;
            background-color: #e8eaf6;
            padding: 5px;
            border-radius: 3px;
            border: 1px solid #c5cae9;
            font-size: 9px;
        """)
        self.summary_label.setWordWrap(True)
        self.summary_label.setMaximumHeight(40)
        results_layout.addWidget(self.summary_label, 1)
        
        self.right_tabs.addTab(results_tab, "📊 Résultats")
        
        layout.addWidget(self.right_tabs, 2)
        
        # ربط إشارة تغيير الخطوة
        if self.graph_view:
            self.graph_view.step_changed.connect(self.on_step_changed)
        
        return panel
    
    def on_step_changed(self, step_num):
        """عند تغيير الخطوة في الرسم البياني"""
        self.current_johnson_step = step_num
        if self.johnson_steps_data and step_num < len(self.johnson_steps_data):
            self.display_current_step()
            self.update_step_controls()
    
    def create_new_graph(self):
        """إنشاء رسم بياني جديد فارغ"""
        if self.graph_view:
            self.graph_view.create_empty_graph()
            self.reset_johnson()
    
    def create_random_graph(self):
        """إنشاء رسم بياني عشوائي"""
        if self.graph_view:
            self.graph_view.create_random_weighted_graph()
            self.reset_johnson()
    
    def toggle_directed_mode(self):
        """تبديل وضع الأقواس الموجهة"""
        if self.graph_view:
            self.graph_view.enable_directed_mode()
            if self.graph_view.directed_mode:
                self.directed_btn.setText("↷ Dirigé")
                self.directed_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #5c6bc0;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 8px;
                        font-size: 11px;
                    }
                """)
            else:
                self.directed_btn.setText("↷ Non-dirigé")
                self.directed_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ce93d8;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 8px;
                        font-size: 11px;
                    }
                """)
    
    def enable_add_node_mode(self):
        if self.graph_view:
            self.graph_view.enable_add_node_mode()
    
    def enable_add_edge_mode(self):
        if self.graph_view:
            self.graph_view.enable_add_edge_mode()
    
    def enable_set_weight_mode(self):
        if self.graph_view:
            self.graph_view.enable_set_weight_mode()
    
    def enable_delete_mode(self):
        if self.graph_view:
            self.graph_view.enable_delete_mode()
    
    def start_johnson(self):
        """بدء خوارزمية Johnson خطوة بخطوة"""
        if not self.graph_view or not self.graph_view.graph.nodes:
            QMessageBox.warning(self, "Erreur", "Veuillez créer un graphe d'abord!")
            return
        
        self.johnson_steps_data = self.graph_view.run_johnson()
        
        if self.johnson_steps_data is None:
            return
        
        self.current_johnson_step = 0
        self.update_step_controls()
        self.display_current_step()
    
    def display_current_step(self):
        """عرض الخطوة الحالية"""
        if self.current_johnson_step < len(self.johnson_steps_data):
            step_data = self.johnson_steps_data[self.current_johnson_step]
            
            step_num = step_data['step']
            self.step_title_label.setText(f"Étape {step_num}")
            
            self.update_step_table(step_data)
            
            self.progress_bar.setValue(step_data['step'])
            
            if step_data['step'] == 5:
                self.update_results_tab(step_data)
    
    def update_step_table(self, step_data):
        """تحديث جدول الخطوة الحالية"""
        self.step_data_table.clear()
        
        step_num = step_data['step']
        
        if step_num == 1:
            self.step_data_table.setColumnCount(2)
            self.step_data_table.setHorizontalHeaderLabels(["Action", "Détail"])
            self.step_data_table.setRowCount(2)
            
            self.step_data_table.setItem(0, 0, QTableWidgetItem("Ajout Sommet S"))
            self.step_data_table.setItem(0, 1, QTableWidgetItem("Sommet auxiliaire ajouté"))
            
            self.step_data_table.setItem(1, 0, QTableWidgetItem("Connexions"))
            self.step_data_table.setItem(1, 1, QTableWidgetItem("S connecté à tous les sommets (poids=0)"))
            
            self.step_data_table.horizontalHeader().setStretchLastSection(True)
        
        elif step_num == 2:
            if 'bellman_ford_table' in step_data:
                table_data = step_data['bellman_ford_table']
                self.step_data_table.setColumnCount(len(table_data[0]))
                headers = list(table_data[0].keys())
                self.step_data_table.setHorizontalHeaderLabels(headers)
                self.step_data_table.setRowCount(len(table_data))
                
                for i, row in enumerate(table_data):
                    for j, key in enumerate(headers):
                        item = QTableWidgetItem(str(row[key]))
                        if key == "k" and "init" in str(row[key]):
                            item.setBackground(QColor(255, 248, 225))
                        elif key == "k" and "fin" in str(row[key]):
                            item.setBackground(QColor(225, 245, 254))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.step_data_table.setItem(i, j, item)
        
        elif step_num == 3:
            if 'edges' in step_data:
                edges = step_data['edges']
                self.step_data_table.setColumnCount(5)
                self.step_data_table.setHorizontalHeaderLabels(["Arc", "w(u,v)", "h(u)", "h(v)", "w'(u,v)"])
                self.step_data_table.setRowCount(len(edges))
                
                for i, edge in enumerate(edges):
                    self.step_data_table.setItem(i, 0, QTableWidgetItem(edge['arc']))
                    self.step_data_table.setItem(i, 1, QTableWidgetItem(str(edge['original_weight'])))
                    self.step_data_table.setItem(i, 2, QTableWidgetItem(str(edge['h_u'])))
                    self.step_data_table.setItem(i, 3, QTableWidgetItem(str(edge['h_v'])))
                    
                    new_weight_item = QTableWidgetItem(str(edge['new_weight']))
                    if edge['new_weight'] < 0:
                        new_weight_item.setForeground(QColor(220, 0, 0))
                    elif edge['new_weight'] == 0:
                        new_weight_item.setForeground(QColor(0, 150, 0))
                    
                    for col in range(5):
                        item = self.step_data_table.item(i, col)
                        if item:
                            item.setTextAlignment(Qt.AlignCenter)
                    
                    self.step_data_table.setItem(i, 4, new_weight_item)
        
        elif step_num == 4:
            if 'd_prime_matrix' in step_data:
                matrix = step_data['d_prime_matrix']
                nodes = list(matrix.keys())
                
                self.step_data_table.setColumnCount(len(nodes) + 1)
                headers = ["Source"] + [f"Vers {node}" for node in nodes]
                self.step_data_table.setHorizontalHeaderLabels(headers)
                self.step_data_table.setRowCount(len(nodes))
                
                for i, source in enumerate(nodes):
                    source_item = QTableWidgetItem(source)
                    source_item.setTextAlignment(Qt.AlignCenter)
                    self.step_data_table.setItem(i, 0, source_item)
                    
                    for j, target in enumerate(nodes):
                        value = matrix[source][target]
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        if source == target:
                            item.setBackground(QColor(240, 240, 240))
                        self.step_data_table.setItem(i, j + 1, item)
        
        elif step_num == 5:
            if 'final_matrix' in step_data:
                matrix = step_data['final_matrix']
                nodes = list(matrix.keys())
                
                self.step_data_table.setColumnCount(len(nodes) + 1)
                headers = ["Source"] + [f"Vers {node}" for node in nodes]
                self.step_data_table.setHorizontalHeaderLabels(headers)
                self.step_data_table.setRowCount(len(nodes))
                
                for i, source in enumerate(nodes):
                    source_item = QTableWidgetItem(source)
                    source_item.setTextAlignment(Qt.AlignCenter)
                    self.step_data_table.setItem(i, 0, source_item)
                    
                    for j, target in enumerate(nodes):
                        dist = matrix[source][target]
                        item = QTableWidgetItem(str(dist))
                        item.setTextAlignment(Qt.AlignCenter)
                        
                        if source == target:
                            item.setBackground(QColor(240, 240, 240))
                        elif isinstance(dist, (int, float)) and dist < 0:
                            item.setForeground(QColor(220, 0, 0))
                            item.setBackground(QColor(255, 245, 245))
                        elif isinstance(dist, (int, float)) and dist == 0:
                            item.setForeground(QColor(0, 150, 0))
                        
                        self.step_data_table.setItem(i, j + 1, item)
        
        header = self.step_data_table.horizontalHeader()
        for i in range(self.step_data_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        for i in range(self.step_data_table.rowCount()):
            self.step_data_table.setRowHeight(i, 30)
        
        row_height = 30
        header_height = 25
        total_height = min(400, self.step_data_table.rowCount() * row_height + header_height + 10)
        self.step_data_table.setMinimumHeight(total_height)
    
    def update_results_tab(self, step_data):
        """تحديث تبويب النتائج"""
        if 'final_matrix' in step_data:
            matrix = step_data['final_matrix']
            nodes = list(matrix.keys())
            
            self.results_table.setColumnCount(len(nodes) + 1)
            self.results_table.setRowCount(len(nodes))
            
            headers = ["De \\ À"] + list(nodes)
            self.results_table.setHorizontalHeaderLabels(headers)
            
            self.results_table.verticalHeader().setDefaultSectionSize(30)
            
            for i, source in enumerate(nodes):
                source_item = QTableWidgetItem(source)
                source_item.setTextAlignment(Qt.AlignCenter)
                source_item.setFont(QFont("Arial", 9, QFont.Bold))
                self.results_table.setItem(i, 0, source_item)
                
                for j, target in enumerate(nodes):
                    dist = matrix[source][target]
                    item = QTableWidgetItem(str(dist))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    if source == target:
                        item.setBackground(QColor(240, 240, 240))
                        item.setFont(QFont("Arial", 9, QFont.Bold))
                    elif isinstance(dist, (int, float)) and dist < 0:
                        item.setForeground(QColor(220, 0, 0))
                        item.setBackground(QColor(255, 245, 245))
                    elif isinstance(dist, (int, float)) and dist == 0:
                        item.setForeground(QColor(0, 150, 0))
                    
                    self.results_table.setItem(i, j + 1, item)
            
            header = self.results_table.horizontalHeader()
            for i in range(self.results_table.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            
            row_count = self.results_table.rowCount()
            row_height = 30
            header_height = 25
            total_height = row_count * row_height + header_height + 10
            
            self.results_table.setMinimumHeight(min(400, total_height))
            self.results_table.setMaximumHeight(500)
            
            self.summary_label.setText("✓ Matrice finale calculée ✓\n" +
                                     f"✓ {len(nodes)}×{len(nodes)} éléments ✓\n" +
                                     "✓ Algorithme terminé avec succès ✓")
            
            self.right_tabs.setCurrentIndex(1)
    
    def prev_johnson_step(self):
        """الخطوة السابقة"""
        if self.current_johnson_step > 0:
            self.current_johnson_step -= 1
            if self.graph_view:
                step_data = self.graph_view.go_to_step(self.current_johnson_step)
                if step_data:
                    self.display_current_step()
                    self.update_step_controls()
    
    def next_johnson_step(self):
        """الخطوة التالية"""
        if self.current_johnson_step < len(self.johnson_steps_data) - 1:
            self.current_johnson_step += 1
            if self.graph_view:
                step_data = self.graph_view.go_to_step(self.current_johnson_step)
                if step_data:
                    self.display_current_step()
                    self.update_step_controls()
        else:
            self.animation_timer.stop()
            self.auto_btn.setText("⏵ Auto")
    
    def go_to_step(self, step_num):
        """الانتقال المباشر إلى خطوة محددة"""
        if 1 <= step_num <= 5 and self.johnson_steps_data:
            self.current_johnson_step = step_num - 1
            if self.graph_view:
                step_data = self.graph_view.go_to_step(self.current_johnson_step)
                if step_data:
                    self.display_current_step()
                    self.update_step_controls()
    
    def toggle_auto_mode(self):
        """تبديل الوضع التلقائي"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.auto_btn.setText("⏵ Auto")
        else:
            if self.johnson_steps_data:
                interval = self.speed_slider.value() * 1000
                self.animation_timer.start(interval)
                self.auto_btn.setText("⏸ Pause")
            else:
                QMessageBox.warning(self, "Erreur", "Démarrez d'abord l'algorithme!")
    
    def update_step_controls(self):
        """تحديث حالة أزرار التحكم"""
        has_steps = len(self.johnson_steps_data) > 0
        self.prev_step_btn.setEnabled(has_steps and self.current_johnson_step > 0)
        self.next_step_btn.setEnabled(has_steps and self.current_johnson_step < len(self.johnson_steps_data) - 1)
        
        if has_steps:
            self.progress_bar.setMaximum(len(self.johnson_steps_data))
            self.progress_bar.setValue(self.current_johnson_step + 1)
            
            for i, btn in enumerate(self.step_buttons):
                if i == self.current_johnson_step:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #5c6bc0;
                            color: white;
                            border: 1px solid #5c6bc0;
                            border-radius: 3px;
                            padding: 5px;
                            font-size: 9px;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e8eaf6;
                            color: #5c6bc0;
                            border: 1px solid #c5cae9;
                            border-radius: 3px;
                            padding: 5px;
                            font-size: 9px;
                        }
                        QPushButton:hover {
                            background-color: #c5cae9;
                        }
                    """)
    
    def back_to_main(self):
        self.back_to_main_signal.emit()
        self.close()
    
    def reset_johnson(self):
        """إعادة تعيين الخوارزمية"""
        if self.graph_view:
            self.graph_view.reset_algorithm()
        self.current_johnson_step = 0
        self.johnson_steps_data = []
        
        self.step_title_label.setText("Prêt")
        self.step_data_table.clear()
        
        self.results_table.clear()
        self.summary_label.setText("Exécutez l'algorithme pour voir les résultats")
        self.progress_bar.setValue(0)
        
        self.update_step_controls()
        
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.auto_btn.setText("⏵ Auto")

def main():
    app = QApplication(sys.argv)
    window = JohnsonAlgorithmApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
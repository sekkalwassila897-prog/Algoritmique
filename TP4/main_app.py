# main_app.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QDesktopWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QPalette

# استيراد تطبيقات الخوارزميتين
from dsatur_app import DSATURAlgorithmApp
from johnson_app import JohnsonAlgorithmApp

class AlgorithmSelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Visualisation des Algorithmes de Graphes")
        
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                      stop:0 #6a11cb, stop:1 #2575fc);
        """)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        title = QLabel("VISUALISATION DES ALGORITHMES DE GRAPHES")
        title.setFont(QFont("Segoe UI", 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Sélectionnez un algorithme à visualiser")
        subtitle.setFont(QFont("Segoe UI", 24))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 80px;
        """)
        layout.addWidget(subtitle)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(80)
        buttons_layout.setContentsMargins(100, 0, 100, 0)
        
        dsatur_color = QColor(102, 187, 106)
        johnson_color = QColor(121, 134, 203)
        
        dsatur_btn = self.create_algorithm_button(
            "ALGORITHME DSATUR",
            "Coloration de Graphes",
            dsatur_color,
            "🎨",
            "dsatur"
        )
        
        johnson_btn = self.create_algorithm_button(
            "ALGORITHME JOHNSON",
            "Plus Courts Chemins",
            johnson_color,
            "🔄",
            "johnson"
        )
        
        buttons_layout.addWidget(dsatur_btn)
        buttons_layout.addWidget(johnson_btn)
        
        layout.addLayout(buttons_layout)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            margin-top: 80px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_label = QLabel(
            "<p style='color: rgba(255, 255, 255, 0.9); font-size: 16px; line-height: 1.6;'>"
            "Outil interactif de visualisation pour apprendre les algorithmes de graphes. "
            "Créez des graphes, exécutez des algorithmes et voyez l'exécution étape par étape."
            "</p>"
        )
        info_label.setFont(QFont("Segoe UI", 14))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
        
        instructions = QLabel("Cliquez sur un bouton ci-dessus pour commencer")
        instructions.setFont(QFont("Segoe UI", 16))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            margin-top: 30px;
            padding: 15px;
        """)
        layout.addWidget(instructions)
        
    def create_algorithm_button(self, title, description, color, emoji, algorithm_type):
        btn_frame = QFrame()
        btn_frame.setMinimumSize(400, 300)
        
        btn_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 rgba({color.red()}, {color.green()}, {color.blue()}, 0.8),
                                          stop:1 rgba({color.red()-20}, {color.green()-20}, {color.blue()-20}, 0.9));
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 rgba({color.red()+20}, {color.green()+20}, {color.blue()+20}, 0.9),
                                          stop:1 rgba({color.red()}, {color.green()}, {color.blue()}, 1.0));
                border: 2px solid rgba(255, 255, 255, 0.5);
            }}
        """)
        
        layout = QVBoxLayout(btn_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        icon_label = QLabel(emoji)
        icon_label.setFont(QFont("Arial", 50))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("background: transparent; color: white;")
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("""
            color: white;
            text-align: center;
            background: transparent;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 14))
        desc_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
            text-align: center;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        btn = QPushButton("DÉMARRER LA VISUALISATION")
        btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.9);
                color: rgba({color.red()-40}, {color.green()-40}, {color.blue()-40}, 255);
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: white;
                color: rgba({color.red()-60}, {color.green()-60}, {color.blue()-60}, 255);
            }}
        """)
        btn.clicked.connect(lambda: self.select_algorithm(algorithm_type))
        layout.addWidget(btn)
        
        return btn_frame
        
    def select_algorithm(self, algorithm_type):
        if algorithm_type == "dsatur":
            self.dsatur_window = DSATURAlgorithmApp()
            self.dsatur_window.showMaximized()
            self.dsatur_window.back_to_main_signal.connect(self.show_main_window)
            self.hide()
        elif algorithm_type == "johnson":
            # إضافة تعريف johnson_window كسمة للكائن
            self.johnson_window = JohnsonAlgorithmApp()
            self.johnson_window.showMaximized()
            self.johnson_window.back_to_main_signal.connect(self.show_main_window)
            self.hide()
            
    def show_main_window(self):
        self.showMaximized()

# ================================
# MAIN EXECUTION
# ================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = AlgorithmSelectionWindow()
    window.showMaximized()
    
    sys.exit(app.exec_())
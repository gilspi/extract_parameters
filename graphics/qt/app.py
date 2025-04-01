import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QFileDialog,
    QProgressBar, QCheckBox, QGridLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPalette, QColor, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from config import DIRECTORY, INITIAL_LOG_SCALE, INITIAL_GRID
from graphics.qt.handlers import QtHandlers
from graphics.qt.model_selector import QtModelSelectorHandler
from graphics.qt.progress_bar import QtProgressBar
from graphics.factory.base import BaseApp

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #E0E0E0;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NGSPICE Simulator")
        self.setMinimumSize(1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Левая панель
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Правая панель
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание директорий
        self.setup_directories()
        
    def create_left_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Кнопка выбора файла
        self.file_button = ModernButton("Выбрать файл")
        layout.addWidget(self.file_button)
        
        # Кнопки действий
        action_layout = QGridLayout()
        self.apply_button = ModernButton("Применить изменения")
        self.simulate_button = ModernButton("Запустить симуляцию")
        action_layout.addWidget(self.apply_button, 0, 0)
        action_layout.addWidget(self.simulate_button, 0, 1)
        layout.addLayout(action_layout)
        
        # Переключатели
        switches_layout = QHBoxLayout()
        self.log_scale_switch = QCheckBox("Логарифмическая шкала")
        self.grid_switch = QCheckBox("Сетка")
        switches_layout.addWidget(self.log_scale_switch)
        switches_layout.addWidget(self.grid_switch)
        layout.addLayout(switches_layout)
        
        # Контейнер для параметров
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        scroll.setWidget(self.params_container)
        layout.addWidget(scroll)
        
        return panel
    
    def create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # График
        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Прогресс-бар
        self.progress_bar = QtProgressBar()
        layout.addWidget(self.progress_bar)
        
        return panel
    
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLabel {
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QCheckBox {
                font-family: "Segoe UI";
                font-size: 12px;
            }
        """)
    
    def setup_directories(self):
        for directory in DIRECTORY:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def setup_handlers(self):
        # Инициализация обработчиков
        self.handlers = QtHandlers(
            self.params_container,
            self.file_button,
            self.fig,
            self.ax,
            self.canvas,
            self.progress_bar,
            parent_window=self
        )
        
        self.model_selector = QtModelSelectorHandler(self, self.handlers)
        
        # Подключение сигналов
        self.connect_signals()
    
    def connect_signals(self):
        self.apply_button.clicked.connect(self.handlers.apply_changes)
        self.simulate_button.clicked.connect(self.handlers.start_simulation)
        self.log_scale_switch.stateChanged.connect(
            lambda state: self.handlers.toggle_log_scale(self.log_scale_switch, state == Qt.CheckState.Checked)
        )
        self.grid_switch.stateChanged.connect(
            lambda state: self.handlers.toggle_grid(self.grid_switch, state == Qt.CheckState.Checked)
        )
        self.file_button.clicked.connect(self.handlers.choose_parsing_file)

class QtApp(BaseApp):
    """
    Реализация приложения для PyQt6
    """
    
    def create_app(self) -> QApplication:
        if not QApplication.instance():
            return QApplication(sys.argv)
        return QApplication.instance()
    
    def create_window(self) -> QMainWindow:
        window = MainWindow()
        window.setup_handlers()  # Инициализируем обработчики после создания окна
        return window
    
    def run(self) -> None:
        if self.window:
            self.window.show()
            sys.exit(self.app.exec())
    
    def setup_directories(self, directories: list) -> None:
        self.create_directories(directories)

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import os
from datetime import datetime

class BaseHandlers(ABC):
    """
    Базовый абстрактный класс для обработчиков GUI.
    Определяет общий интерфейс для всех реализаций.
    """
    
    def __init__(self, params_box: Any, file_button: Any, fig: Any, ax: Any, 
                 canvas_plot: Any, progress_bar: Any, parent_window: Any):
        self.parent_window = parent_window
        self.params_box = params_box
        self.file_button = file_button
        self.fig = fig
        self.ax = ax
        self.canvas_plot = canvas_plot
        self.progress_bar = progress_bar
        
        self.parameter_entries: List[Dict[str, Any]] = []
        self.start_point = None
        self.selection_rect = None
        self.original_xlim = None
        self.original_ylim = None
        
    @abstractmethod
    def set_configuration(self, model_name: str) -> None:
        """Устанавливает конфигурацию для выбранной модели"""
        pass
    
    @abstractmethod
    def update_parameters(self, parsing_file: str) -> None:
        """Обновляет параметры на основе выбранного файла"""
        pass
    
    @abstractmethod
    def choose_parsing_file(self, widget: Any) -> None:
        """Выбор файла параметров"""
        pass
    
    @abstractmethod
    def choose_model(self, widget: Any) -> None:
        """Выбор файла модели"""
        pass
    
    @abstractmethod
    def choose_spice_file(self, widget: Any) -> None:
        """Выбор SPICE-файла"""
        pass
    
    @abstractmethod
    def apply_changes(self, widget: Any) -> None:
        """Применяет изменения к файлу параметров"""
        pass
    
    @abstractmethod
    def start_simulation(self, button: Any) -> None:
        """Запускает симуляцию"""
        pass
    
    @abstractmethod
    def toggle_log_scale(self, widget: Any, state: bool) -> None:
        """Переключение логарифмической шкалы"""
        pass
    
    @abstractmethod
    def toggle_grid(self, widget: Any, state: bool) -> None:
        """Переключение отображения сетки"""
        pass
    
    @abstractmethod
    def save_plot(self, widget: Any) -> None:
        """Сохранение графика"""
        pass
    
    @abstractmethod
    def reset_zoom(self, widget: Any) -> None:
        """Сброс масштаба графика"""
        pass
    
    def create_directories(self, directories: List[str]) -> None:
        """Создает директории, если они не существуют"""
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory) 
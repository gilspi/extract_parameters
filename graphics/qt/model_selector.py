from PyQt6.QtWidgets import QComboBox, QLabel, QWidget, QVBoxLayout

from config import CONFIG_OPTIONS
from graphics.factory.model_selector import ModelSelectorHandler

class QtModelSelectorHandler(ModelSelectorHandler):
    """
    Реализация селектора модели для Qt
    """
    def __init__(self, parent_window, handlers):
        super().__init__(parent_window, handlers)
        self.widget = self.create_widget()
        
    def create_widget(self):
        """Создание виджета выбора модели"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel("Выберите модель:")
        self.combo = self.create_combo()
        self.setup_combo()
        
        layout.addWidget(label)
        layout.addWidget(self.combo)
        
        return widget
        
    def get_widget(self):
        """Получение виджета"""
        return self.widget
        
    def create_combo(self) -> QComboBox:
        return QComboBox()

    def setup_combo(self) -> None:
        for model_name in CONFIG_OPTIONS.keys():
            self.combo.addItem(model_name)
        self.combo.setCurrentIndex(0)
        self.combo.currentTextChanged.connect(self.on_model_changed)

    def get_active_text(self) -> str:
        return self.combo.currentText()

    def on_model_changed(self, index):
        """Обработчик изменения модели"""
        try:
            # Здесь должна быть логика изменения модели
            pass
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.parent_window,
                "Ошибка",
                f"Не удалось изменить модель: {str(e)}"
            ) 
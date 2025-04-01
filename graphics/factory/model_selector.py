from abc import ABC, abstractmethod
from typing import Any

from config import CONFIG_OPTIONS


class ModelSelectorHandler(ABC):
    """
    Базовый класс для создания селектора модели.
    При изменении выбранной модели вызывается set_configuration у обработчиков.
    """
    def __init__(self, app: Any, handlers: Any):
        self.app = app
        self.handlers = handlers
        self.combo = self.create_combo()
        self.setup_combo()
        self.handlers.set_configuration(self.get_active_text())

    @abstractmethod
    def create_combo(self) -> Any:
        """
        Создает виджет комбобокса
        """
        pass

    @abstractmethod
    def setup_combo(self) -> None:
        """
        Настраивает комбобокс (добавляет элементы, подключает сигналы)
        """
        pass

    @abstractmethod
    def get_active_text(self) -> str:
        """
        Возвращает текст выбранного элемента
        """
        pass

    def on_model_changed(self, widget: Any) -> None:
        """
        Обработчик изменения выбранной модели
        """
        model_name = self.get_active_text()
        if model_name:
            self.handlers.set_configuration(model_name)

    def get_widget(self) -> Any:
        """
        Возвращает виджет комбобокса
        """
        return self.combo 
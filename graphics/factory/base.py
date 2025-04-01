from abc import ABC, abstractmethod
import os
from typing import Tuple, Any

class BaseApp(ABC):
    """
    Базовый абстрактный класс для всех GUI реализаций.
    Определяет общий интерфейс для всех приложений.
    """
    
    def __init__(self):
        self.window = None
        self.app = None
        
    @abstractmethod
    def create_window(self) -> Any:
        """
        Создает главное окно приложения
        """
        pass
    
    @abstractmethod
    def create_app(self) -> Any:
        """
        Создает экземпляр приложения
        """
        pass
    
    @abstractmethod
    def run(self) -> None:
        """
        Запускает приложение
        """
        pass
    
    @abstractmethod
    def setup_directories(self, directories: list) -> None:
        """
        Создает необходимые директории
        """
        pass
    
    def initialize(self) -> Tuple[Any, Any]:
        """
        Инициализирует приложение и окно
        """
        self.app = self.create_app()
        self.window = self.create_window()
        return self.app, self.window
    
    def create_directories(self, directories: list) -> None:
        """
        Создает директории, если они не существуют
        """
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory) 
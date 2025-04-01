from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import QTimer

from graphics.factory.progress_bar import BaseProgressBar


class QtProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        QProgressBar.__init__(self, *args, **kwargs)
        
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
        
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(100)

    def set_fraction(self, fraction: float) -> None:
        self.progress_fraction = fraction
        self.setValue(int(fraction * 100))

    def start_animation(self) -> None:
        if not self.animating:
            self.animating = True
            self.animation_timer.start()

    def stop_animation(self) -> None:
        self.animating = False
        self.animation_timer.stop()

    def get_widget(self) -> QProgressBar:
        return self

    def update_animation(self) -> None:
        if not self.animating:
            return
        current_value = self.value()
        if current_value < 100:
            self.setValue(current_value + 1) 
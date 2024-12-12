from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from matplotlib.widgets import Cursor
from ui import Ui_MainWindow  # Импортируем UI из .ui
import matplotlib.pyplot as plt

class Handler(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Создание объекта для графика
        self.fig, self.ax = plt.subplots()  # Создание объекта фигуры и осей
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)  # Инициализация курсора для зума

        # Подключаем обработчики кнопок
        self.choose_file_btn.clicked.connect(self.choose_file)
        self.choose_model_btn.clicked.connect(self.choose_model)
        self.accept_changes_btn.clicked.connect(self.apply_changes)
        self.choose_spice_schema_btn.clicked.connect(self.choose_spice_file)
        self.start_simulation_btn.clicked.connect(self.run_simulation)
        # self.reset_scale_btn.clicked.connect(self.reset_plot_scale)
        self.log_scale_checkbox.stateChanged.connect(self.toggle_log_scale)

    def choose_file(self):
        """Обработчик выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Все файлы (*)")
        if file_path:
            QMessageBox.information(self, "Файл выбран", f"Выбранный файл: {file_path}")

    def choose_model(self):
        """Обработчик выбора модели"""
        QMessageBox.information(self, "Выбор модели", "Модель выбрана.")

    def apply_changes(self):
        """Применение изменений"""
        QMessageBox.information(self, "Изменения", "Изменения применены.")

    def choose_spice_file(self):
        """Выбор SPICE-файла"""
        spice_file, _ = QFileDialog.getOpenFileName(self, "Выберите SPICE-файл", "", "SPICE файлы (*.sp *.cir);;Все файлы (*)")
        if spice_file:
            QMessageBox.information(self, "SPICE файл", f"Выбранный файл: {spice_file}")

    def run_simulation(self):
        """Запуск симуляции"""
        QMessageBox.information(self, "Симуляция", "Симуляция выполнена успешно.")

    def reset_plot_scale(self):
        """Сброс масштаба графика"""
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.fig.canvas.draw()

    def toggle_log_scale(self, state):
        """Переключение логарифмического масштаба"""
        self.ax.set_yscale("log" if state else "linear")
        self.fig.canvas.draw()

if __name__ == "__main__":
    app = QApplication([])
    window = Handler()
    window.show()
    app.exec_()

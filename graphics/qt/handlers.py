from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
import os
import threading
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QDoubleSpinBox, QLineEdit
from PyQt6.QtCore import QThread, pyqtSignal

from core.file_manager import FileManager
from core.simulation_runner import SimulationRunner
from plotting.plot_simulation import SimulationManager
from utils.parameter_parser import ParameterParser, FileIgnoreParamsLoader
from config import (MODEL_CODE_PATH, SPICE_EXAMPLES_PATH, IGNORE_PARAMS_FILE, 
                   OUTPUT_DATA_PATH, SIMULATION_RAW_DATA_PATH, CONFIG_OPTIONS, PICS_PATH)
from utils import shorten_file_path
from graphics.factory.handlers import BaseHandlers

class SimulationThread(QThread):
    progress = pyqtSignal(float)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, simulation_runner, spice_file, canvas, fig):
        super().__init__()
        self.simulation_runner = simulation_runner
        self.spice_file = spice_file
        self.canvas = canvas
        self.fig = fig

    def run(self):
        try:
            for progress in self.simulation_runner.run_simulation(
                    spice_file=self.spice_file,
                    canvas=self.canvas,
                    fig=self.fig):
                if isinstance(progress, str):
                    self.error.emit(progress)
                    return
                self.progress.emit(progress)
            self.finished.emit()
        except RuntimeError as warning:
            self.error.emit(str(warning))
        except Exception as e:
            self.error.emit(f"Ошибка симуляции: {str(e)}")

class QtHandlers(BaseHandlers):
    def __init__(self, params_box, file_button, fig, ax, canvas_plot, progress_bar, parent_window):
        super().__init__(params_box, file_button, fig, ax, canvas_plot, progress_bar, parent_window)
        
        self.simulation_manager = SimulationManager()
        self.user_result_file = os.path.join(SIMULATION_RAW_DATA_PATH, "simulation_data.txt")
        self.parsing_file = "No File Selected"
        self.spice_file = None
        self.simulation_runner = None
        self.file_manager = FileManager()
        self.simulation_thread = None

    def set_configuration(self, model_name: str) -> None:
        config = CONFIG_OPTIONS.get(model_name)
        if not config:
            self.__show_message_dialog("Ошибка", "Неверная конфигурация.", QMessageBox.Icon.Critical)
            return

        self.parsing_file = os.path.abspath(config["parameters"])
        model_file = os.path.abspath(config["model"])
        self.spice_file = os.path.abspath(config["spice"])

        if self.file_button:
            short_path = shorten_file_path(self.parsing_file, max_length=40)
            self.file_button.setText("File: " + short_path)

        self.update_parameters(self.parsing_file)
        self.simulation_runner = SimulationRunner(self.parsing_file, self.simulation_manager, self.user_result_file)
        self.simulation_runner.set_model(model_file)

    def update_parameters(self, parsing_file: str) -> None:
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=parsing_file, ignore_params_loader=ignore_params_loader)
            parameters = parser.parse()

            # Очищаем существующие виджеты
            for i in reversed(range(self.params_box.layout().count())): 
                self.params_box.layout().itemAt(i).widget().setParent(None)
            self.parameter_entries = []

            for param in parameters:
                self.__add_parameter_row(param["name"], str(param["default_value"]))

            self.simulation_runner = SimulationRunner(parsing_file, self.simulation_manager, self.user_result_file)
        except Exception as e:
            self.__show_message_dialog("Ошибка", "Ошибка при загрузке параметров.", QMessageBox.Icon.Critical)

    def __add_parameter_row(self, param_name: str, default_value: str) -> None:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(param_name)
        entry = QLineEdit(default_value)
        entry.setMinimumWidth(100)
        
        layout.addWidget(label)
        layout.addWidget(entry)
        
        self.params_box.layout().addWidget(row)
        self.parameter_entries.append({
            "name": param_name,
            "entry": entry
        })

    def choose_parsing_file(self, widget) -> None:
        initial_dir = MODEL_CODE_PATH
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Выберите файл параметров",
            initial_dir
        )
        if file_name:
            self.parsing_file = file_name
            self.update_parameters(self.parsing_file)
            short_path = shorten_file_path(self.parsing_file, max_length=40)
            self.file_button.setText("File: " + short_path)

    def choose_model(self, widget) -> None:
        if not self.simulation_runner:
            self.__show_message_dialog("Ошибка", "Сначала выберите файл параметров.", QMessageBox.Icon.Critical)
            return
        initial_dir = os.path.dirname(self.parsing_file) if self.parsing_file else SPICE_EXAMPLES_PATH
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Выберите модель (.va)",
            initial_dir
        )
        if file_name:
            self.simulation_runner.set_model(file_name)
            self.__show_message_dialog("Уведомление",
                                     "Модель выбрана: " + os.path.basename(file_name),
                                     QMessageBox.Icon.Information)

    def choose_spice_file(self, widget) -> None:
        if not self.parsing_file:
            self.__show_message_dialog("Ошибка", "Сначала выберите файл параметров.", QMessageBox.Icon.Critical)
            return
        parent_dir_name = os.path.basename(os.path.dirname(os.path.dirname(self.parsing_file)))
        initial_dir = os.path.join(SPICE_EXAMPLES_PATH, parent_dir_name)
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent_window,
            "Выберите SPICE-файл",
            initial_dir
        )
        if file_name:
            self.spice_file = file_name
            self.__show_message_dialog("Уведомление",
                                     "Spice-схема выбрана: " + self.spice_file,
                                     QMessageBox.Icon.Information)

    def apply_changes(self, widget) -> None:
        if not self.simulation_runner:
            self.__show_message_dialog("Ошибка", "Модель не выбрана.", QMessageBox.Icon.Critical)
            return
        current_parameters = {}
        for param in self.parameter_entries:
            current_parameters[param["name"]] = param["entry"].text()
        try:
            self.file_manager.apply_changes_to_file(current_parameters, self.parsing_file)
            self.__show_message_dialog(
                "Успех",
                "Изменения успешно применены в " + self.parsing_file + ".",
                QMessageBox.Icon.Information
            )
        except Exception as e:
            self.__show_message_dialog(
                "Ошибка",
                f"Не удалось применить изменения: {str(e)}",
                QMessageBox.Icon.Critical
            )

    def start_simulation(self, button) -> None:
        if not self.simulation_runner:
            self.__show_message_dialog("Ошибка", "Сначала выберите файл параметров.", QMessageBox.Icon.Critical)
            return
        if not self.spice_file:
            self.__show_message_dialog("Ошибка", "Сначала выберите SPICE-файл.", QMessageBox.Icon.Critical)
            return

        self.simulation_thread = SimulationThread(
            self.simulation_runner,
            self.spice_file,
            self.canvas_plot,
            self.fig
        )
        self.simulation_thread.progress.connect(self.__update_progress_bar)
        self.simulation_thread.error.connect(self.__show_error_dialog)
        self.simulation_thread.finished.connect(self.__simulation_finished)
        self.simulation_thread.start()

    def toggle_log_scale(self, widget, state: bool) -> None:
        current_xlim, current_ylim = self.ax.get_xlim(), self.ax.get_ylim()
        self.ax.set_yscale("log" if state else "linear")
        
        if not self.ax.get_lines():
            print("Warning: No data on graph, switching scale but no effect on plot.")
            self.canvas_plot.draw()
            return

        for line in self.ax.get_lines():
            line.set_ydata(line.get_ydata())

        self.ax.set_xlim(current_xlim)
        self.ax.set_ylim(current_ylim)
        self.canvas_plot.draw()

    def toggle_grid(self, widget, state: bool) -> None:
        if state:
            self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        else:
            self.ax.grid(False)
        self.canvas_plot.draw()

    def save_plot(self, widget) -> None:
        os.makedirs(PICS_PATH, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(PICS_PATH, f'plot_{current_time}.png')
        self.fig.savefig(file_path)

        self.__show_message_dialog(
            "Сохранение графика",
            f"График успешно сохранён в:\n{file_path}",
            QMessageBox.Icon.Information
        )

    def reset_zoom(self, widget) -> None:
        if not self.fig or not self.fig.axes:
            return

        ax = self.fig.axes[0]
        ax.set_xlim(self.original_xlim)
        ax.set_ylim(self.original_ylim)

        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

        self.canvas_plot.draw()

    def __show_error_dialog(self, error_message: str) -> None:
        QMessageBox(
            QMessageBox.Icon.Critical,
            "Ошибка",
            error_message,
            QMessageBox.StandardButton.Ok,
            self.parent_window
        ).exec()

    def __show_message_dialog(self, title: str, message: str, icon: QMessageBox.Icon):
        QMessageBox(
            icon,
            title,
            message,
            QMessageBox.StandardButton.Ok,
            self.parent_window
        ).exec()

    def __update_progress_bar(self, progress: float) -> None:
        if hasattr(self.parent_window, 'progress_bar'):
            self.progress_bar.setValue(int(progress * 100))

    def __simulation_finished(self) -> None:
        if hasattr(self.parent_window, 'progress_bar'):
            self.progress_bar.setValue(100) 
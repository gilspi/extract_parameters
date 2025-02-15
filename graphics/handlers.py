import time

import threading

import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ios_switch import IosStyleSwitch

from core.file_manager import FileManager
from core.simulation_runner import SimulationRunner
from utils.parameter_parser import ParameterParser, FileIgnoreParamsLoader
from config import MODEL_CODE_PATH, SPICE_EXAMPLES_PATH, IGNORE_PARAMS_FILE


def shorten_file_path(full_path, max_length=40):
    """
    Если длина пути больше max_length, возвращает строку вида:
    начало пути + "..." + имя файла
    """
    if len(full_path) <= max_length:
        return full_path
    filename = os.path.basename(full_path)
    # Вычитаем длину файла и троеточия
    remaining = max_length - len(filename) - 3
    if remaining < 1:
        # Если места совсем мало, возвращаем только имя файла с троеточием спереди
        return "..." + filename[-(max_length-3):]
    shortened = full_path[:remaining] + "..." + filename
    return shortened

class SimulatorHandlers:
    def __init__(self, app):
        self.app = app  # ссылка на главное приложение
        self.progress_fraction = 0.0  # прогресс заполнения (0.0 - 1.0)

    """ 
        parsing file button, it can be files with extensions -> .va/.inc 
        if you see empty screen -> choose other file
    """

    def choose_parsing_file(self, wigdet):
        """Выбор файла параметров с установленной директорией."""
        initial_dir = MODEL_CODE_PATH
        dialog = Gtk.FileChooserDialog(
            title="Выберите файл параметров", 
            parent=self.app,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.set_current_folder(initial_dir)  # установка директории
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            self.app.parsing_file = dialog.get_filename()
            print(f"Parsing file selected: {self.app.parsing_file}")
            self.update_parameters(self.app.parsing_file)
            # Используем функцию для сокращения длинного пути
            short_path = shorten_file_path(self.app.parsing_file, max_length=40)
            self.app.file_button.set_label(f"File: {short_path}")
        dialog.destroy()

    def update_parameters(self, parsing_file):
        """Обновление параметров на основе выбранного файла."""
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=parsing_file, ignore_params_loader=ignore_params_loader)
            parameters = parser.parse()

            for widget in self.app.params_box.get_children():
                self.app.params_box.remove(widget)

            self.app.parameter_entries = []

            for param in parameters:
                self.__add_parameter_row(self.app.params_box, param["name"], str(param["default_value"]))

            self.app.params_box.show_all()
            self.app.simulation_runner = SimulationRunner(parsing_file)

        except Exception as e:
            print(f"Ошибка при загрузке параметров: {e}")

    def __add_parameter_row(self, params_box, param_name, default_value):
        """Добавляет строку параметра в params_box."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=param_name)
        entry = Gtk.Entry()
        entry.set_text(default_value)
        entry.set_size_request(100, -1)
        switch = IosStyleSwitch(size=(50, 25))  # размеры переключателя
        switch.set_valign(Gtk.Align.CENTER)
        row.pack_start(label, False, False, 5)
        row.pack_start(entry, True, True, 5)
        row.pack_start(switch, False, False, 5)
        params_box.pack_start(row, False, False, 5)
        self.app.parameter_entries.append({"name": param_name, "entry": entry, "switch": switch})
    
    """ end of first file button """

    """2nd button"""
    def choose_model(self, widget):
        """Выбор конкретной .va модели для использования."""
        if not self.app.simulation_runner:
            print("Ошибка: Сначала выберите файл параметров.")
            return

        initial_dir = os.path.dirname(self.app.parsing_file) if self.app.parsing_file else SPICE_EXAMPLES_PATH
        
        dialog = Gtk.FileChooserDialog(
            title="Выберите модель (.va)",
            parent=self.app,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.set_current_folder(initial_dir)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            model_file = dialog.get_filename()
            self.app.simulation_runner.set_model(model_file)
            print(f"Модель выбрана: {os.path.basename(model_file)}")

        dialog.destroy()
    """end 2nd button"""
   
    def apply_changes(self, widget):
        """Применяет изменения к выбранному файлу."""
        if not self.app.simulation_runner:
            print("Ошибка: Модель не выбрана.")
            return

        current_parameters = {}
        for param in self.app.parameter_entries:
            param_name = param["name"]
            param_value = param["entry"].get_text()
            current_parameters[param_name] = param_value

        target_file = self.app.parsing_file

        try:
            file_manager = FileManager()
            file_manager.apply_changes_to_file(current_parameters, target_file)
            print(f"Изменения успешно применены в {target_file}.")
        except Exception as e:
            print(f"Ошибка: Не удалось применить изменения: {e}")

    def choose_spice_file(self, widget):
        """Выбор SPICE-файла."""
        try:
            parsing_file_path = self.app.parsing_file
            if not parsing_file_path:
                print("Ошибка: Сначала выберите файл параметров.")
                return

            parent_dir_name = os.path.basename(os.path.dirname(os.path.dirname(parsing_file_path)))
            initial_dir = os.path.join(SPICE_EXAMPLES_PATH, parent_dir_name)

            dialog = Gtk.FileChooserDialog(
                title="Выберите SPICE-файл",
                parent=self.app,
                action=Gtk.FileChooserAction.OPEN
            )
            dialog.set_current_folder(initial_dir)  # установка директории для выбора файлов
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

            if dialog.run() == Gtk.ResponseType.OK:
                self.app.spice_file = dialog.get_filename()
                print(f"Spice-схема выбрана: {self.app.spice_file}")

            dialog.destroy()
        except Exception as e:
            print(f"Ошибка при выборе SPICE-файла: {e}")









    #FIXME: вернуть прогресс бар в работающее состояние уже с программой, отрисовку тоже сделать
    def start_simulation(self, button):
        """Запуск симуляции с реальным прогрессом."""
        if not self.app.simulation_runner:
            print("Ошибка: Сначала выберите файл параметров.")
            return
        if not self.app.spice_file:
            print("Ошибка: Сначала выберите SPICE-файл.")
            return

        if hasattr(self.app, "fig"):
            self.app.fig.clear()
            self.app.canvas_plot.draw()

        def simulate():
            """Фоновая симуляция с обновлением прогресса."""
            try:
                for progress in self.app.simulation_runner.run_simulation(
                    spice_file=self.app.spice_file,
                    canvas=self.app.canvas_plot,
                    fig=self.app.fig
                ):
                    GLib.idle_add(self.__update_progress_bar, progress)
                print("Симуляция завершена успешно!")
            except RuntimeError as warning:
                print(f"Предупреждение: {warning}")
            except Exception as e:
                print(f"Ошибка симуляции: {e}")

        threading.Thread(target=simulate, daemon=True).start()

    def __update_progress_bar(self, progress):
        """Обновляет прогресс-бар в главном потоке."""
        if hasattr(self.app, 'progress_bar'):
            self.app.progress_bar.set_fraction(progress)


    #TODO: это допилю сам

    # def on_scroll(self, event):
    #     """Обработчик масштабирования графика."""
    #     pass  # Реализация перенесется сюда

    # def on_press(self, event):
    #     """Обработчик нажатия на график."""
    #     pass  # Реализация перенесется сюда

    # def on_motion(self, event):
    #     """Обработчик движения мыши на графике."""
    #     pass  # Реализация перенесется сюда

    # def on_release(self, event):
    #     """Обработчик отпускания кнопки мыши."""
    #     pass  # Реализация перенесется сюда





    def toggle_parameter(self, switch, state):
        """Обработчик переключения параметра."""
        print(f"Parameter toggled. New state: {'Enabled' if state else 'Disabled'}")

        #TODO: над этим вообще не работал и не смотрел, просто оставил как есть, пока что
        # if state:
        #     label.set_text(label.get_text().replace("̶", ""))
        #     entry.set_sensitive(True)
        # else:
        #     label.set_text("̶" + label.get_text())
        #     entry.set_sensitive(False)

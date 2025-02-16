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

from utils import shorten_file_path



class SimulatorHandlers:
    def __init__(self, params_box, file_button, fig, ax, canvas_plot, progress_bar, parent_window):
        self.parent_window = parent_window  # ссылка на главное приложение
        self.progress_fraction = 0.0  # прогресс заполнения (0.0 - 1.0)   
        
        self.params_box = params_box
        self.file_button = file_button
        self.fig = fig
        self.ax = ax
        self.canvas_plot = canvas_plot
        self.progress_bar = progress_bar

        self.parsing_file = "No File Selected"
        self.spice_file = None  # Путь к SPICE-файлу, выбранному пользователем
        self.simulation_runner = None

        self.parameter_entries = []  # Список для хранения виджетов ввода параметров
                

    """ 
        parsing file button, it can be files with extensions -> .va/.inc 
        if you see empty screen -> choose other file
    """

    def choose_parsing_file(self, wigdet):
        """Выбор файла параметров с установленной директорией."""
        initial_dir = MODEL_CODE_PATH
        dialog = Gtk.FileChooserDialog(
            title="Выберите файл параметров", 
            parent=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.set_current_folder(initial_dir)  # установка директории
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            self.parsing_file = dialog.get_filename()
            print(f"Parsing file selected: {self.parsing_file}")
            self.update_parameters(self.parsing_file)
            # Используем функцию для сокращения длинного пути
            short_path = shorten_file_path(self.parsing_file, max_length=40)
            self.file_button.set_label(f"File: {short_path}")
        dialog.destroy()

    def update_parameters(self, parsing_file):
        """Обновление параметров на основе выбранного файла."""
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=parsing_file, ignore_params_loader=ignore_params_loader)
            parameters = parser.parse()

            for widget in self.params_box.get_children():
                self.params_box.remove(widget)

            self.parameter_entries = []

            for param in parameters:
                self.__add_parameter_row(self.params_box, param["name"], str(param["default_value"]))

            self.params_box.show_all()
            self.simulation_runner = SimulationRunner(parsing_file)

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
        self.parameter_entries.append({"name": param_name, "entry": entry, "switch": switch})
    
    """ end of first file button """

    """2nd button"""
    def choose_model(self, widget):
        """Выбор конкретной .va модели для использования."""
        if not self.simulation_runner:
            print("Ошибка: Сначала выберите файл параметров.")
            return

        initial_dir = os.path.dirname(self.parsing_file) if self.parsing_file else SPICE_EXAMPLES_PATH
        
        dialog = Gtk.FileChooserDialog(
            title="Выберите модель (.va)",
            parent=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.set_current_folder(initial_dir)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        if dialog.run() == Gtk.ResponseType.OK:
            model_file = dialog.get_filename()
            self.simulation_runner.set_model(model_file)
            print(f"Модель выбрана: {os.path.basename(model_file)}")

        dialog.destroy()
    """end 2nd button"""
   
    def apply_changes(self, widget):
        """Применяет изменения к выбранному файлу."""
        if not self.simulation_runner:
            print("Ошибка: Модель не выбрана.")
            return

        current_parameters = {}
        for param in self.parameter_entries:
            param_name = param["name"]
            param_value = param["entry"].get_text()
            current_parameters[param_name] = param_value

        target_file = self.parsing_file

        try:
            file_manager = FileManager()
            file_manager.apply_changes_to_file(current_parameters, target_file)
            print(f"Изменения успешно применены в {target_file}.")
        except Exception as e:
            print(f"Ошибка: Не удалось применить изменения: {e}")

    def choose_spice_file(self, widget):
        """Выбор SPICE-файла."""
        try:
            parsing_file_path = self.parsing_file
            if not parsing_file_path:
                print("Ошибка: Сначала выберите файл параметров.")
                return

            parent_dir_name = os.path.basename(os.path.dirname(os.path.dirname(parsing_file_path)))
            initial_dir = os.path.join(SPICE_EXAMPLES_PATH, parent_dir_name)

            dialog = Gtk.FileChooserDialog(
                title="Выберите SPICE-файл",
                parent=self.parent_window,
                action=Gtk.FileChooserAction.OPEN
            )
            dialog.set_current_folder(initial_dir)  # установка директории для выбора файлов
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

            if dialog.run() == Gtk.ResponseType.OK:
                self.spice_file = dialog.get_filename()
                print(f"Spice-схема выбрана: {self.spice_file}")

            dialog.destroy()
        except Exception as e:
            print(f"Ошибка при выборе SPICE-файла: {e}")









    #FIXME: вернуть прогресс бар в работающее состояние уже с программой, отрисовку тоже сделать
    def start_simulation(self, button):
        """Запуск симуляции с реальным прогрессом."""
        if not self.simulation_runner:
            print("Ошибка: Сначала выберите файл параметров.")
            return
        if not self.spice_file:
            print("Ошибка: Сначала выберите SPICE-файл.")
            return

        if hasattr(self.parent_window, "fig"):
            self.ax.clear()
            self.canvas_plot.draw()

        def simulate():
            """Фоновая симуляция с обновлением прогресса."""
            try:
                for progress in self.simulation_runner.run_simulation(
                    spice_file=self.spice_file,
                    canvas=self.canvas_plot,
                    fig=self.fig
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
        if hasattr(self.parent_window, 'progress_bar'):
            self.progress_bar.set_fraction(progress)


    def update_simulation_progress(self, progress):
        """
        Функция для обновления прогресса симуляции в прогресс-баре.
        
        Аргументы:
        progress (float): число от 0.0 до 1.0, отражающее процент выполнения симуляции.
        
        Эту функцию можно вызывать из кода моделирования (например, из отдельного потока).
        Она использует GLib.idle_add для того, чтобы обновление интерфейса происходило в главном потоке.
        """
        # GLib.idle_add гарантирует, что set_fraction будет вызван в главном цикле GTK.
        GLib.idle_add(self.progress_bar.set_fraction, progress)
    #В коде с моделированием нужно будет добавить эту функцию
    #self.update_simulation_progress(текущее_значение_прогресса)



    #TODO: это Никита

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

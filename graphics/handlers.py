import threading
import os
import gi

from datetime import datetime
import matplotlib.pyplot as plt
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

from ios_switch import IosStyleSwitch

from core.file_manager import FileManager
from core.simulation_runner import SimulationRunner
from plotting.plot_simulation import SimulationManager
from utils.parameter_parser import ParameterParser, FileIgnoreParamsLoader
from config import MODEL_CODE_PATH, SPICE_EXAMPLES_PATH, IGNORE_PARAMS_FILE, OUTPUT_DATA_PATH, SIMULATION_RAW_DATA_PATH, CONFIG_OPTIONS, PICS_PATH
from utils import shorten_file_path


class SimulatorHandlers:
    def __init__(self, params_box, file_button, fig, ax, canvas_plot, progress_bar, parent_window):
        self.parent_window = parent_window  # ссылка на главное приложение

        self.params_box = params_box
        self.file_button = file_button
        self.fig = fig
        self.ax = ax
        self.canvas_plot = canvas_plot
        self.progress_bar = progress_bar

        self.simulation_manager = SimulationManager()  # Создаём менеджер симуляции
        self.user_result_file = os.path.join(SIMULATION_RAW_DATA_PATH, "simulation_data.txt")

        self.parsing_file = ("No File Selected")
        self.spice_file = None
        self.simulation_runner = None
        self.file_manager = FileManager()

        self.parameter_entries = []  # Список для хранения виджетов параметров

        self.start_point = None
        self.selection_rect = None
        self.original_xlim = None
        self.original_ylim = None

    def set_configuration(self, model_name):
        """
        Обновляет конфигурацию симуляции по выбранной модели.
        По выбранному имени из CONFIG_OPTIONS устанавливаются абсолютные пути к файлам,
        затем производится обновление параметров и инициализация SimulationRunner с передачей
        simulation_manager и пути для сохранения результатов.
        """
        config = CONFIG_OPTIONS.get(model_name)
        if not config:
            self.__show_message_dialog(("Ошибка"), ("Неверная конфигурация."), Gtk.MessageType.ERROR)
            return

        self.parsing_file = os.path.abspath(config["parameters"])
        model_file = os.path.abspath(config["model"])
        self.spice_file = os.path.abspath(config["spice"])

        if self.file_button:
            short_path = shorten_file_path(self.parsing_file, max_length=40)
            self.file_button.set_label(("File: ") + short_path)

        self.update_parameters(self.parsing_file)

        self.simulation_runner = SimulationRunner(self.parsing_file, self.simulation_manager, self.user_result_file)
        self.simulation_runner.set_model(model_file)

        print(("Выбрана конфигурация:"), model_name)
        print(("Путь к файлу параметров:"), self.parsing_file)
        print(("Путь к модели:"), model_file)
        print(("Путь к spice-схеме:"), self.spice_file)

    def update_parameters(self, parsing_file):
        """Обновляет параметры на основе выбранного файла с использованием обновлённого парсера."""
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
            self.simulation_runner = SimulationRunner(parsing_file, self.simulation_manager, self.user_result_file)
        except Exception as e:
            self.__show_message_dialog(("Ошибка"), ("Ошибка при загрузке параметров."), Gtk.MessageType.ERROR)
            return

    def __add_parameter_row(self, params_box, param_name, default_value):
        """Добавляет строку параметра в params_box и сохраняет её в списке параметров."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=param_name)
        entry = Gtk.Entry()
        entry.set_text(default_value)
        entry.set_size_request(100, -1)
        # switch = IosStyleSwitch(size=(50, 25))
        # switch.set_valign(Gtk.Align.CENTER)
        row.pack_start(label, False, False, 5)
        row.pack_start(entry, True, True, 5)
        # row.pack_start(switch, False, False, 5)
        params_box.pack_start(row, False, False, 5)
        self.parameter_entries.append({
            "name": param_name,
            "entry": entry,
            # "switch": switch
        })

    def choose_parsing_file(self, widget):
        """Выбор файла параметров через диалог."""
        initial_dir = MODEL_CODE_PATH
        dialog = Gtk.FileChooserDialog(title=("Выберите файл параметров"),
                                       parent=self.parent_window,
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.set_current_folder(initial_dir)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            self.parsing_file = dialog.get_filename()
            print(("Parsing file selected:"), self.parsing_file)
            self.update_parameters(self.parsing_file)
            short_path = shorten_file_path(self.parsing_file, max_length=40)
            self.file_button.set_label(("File: ") + short_path)
        dialog.destroy()

    def choose_model(self, widget):
        """Позволяет вручную выбрать файл модели (.va) – если требуется."""
        if not self.simulation_runner:
            self.__show_message_dialog(("Ошибка"), ("Сначала выберите файл параметров."), Gtk.MessageType.ERROR)
            return
        initial_dir = os.path.dirname(self.parsing_file) if self.parsing_file else SPICE_EXAMPLES_PATH
        dialog = Gtk.FileChooserDialog(title=("Выберите модель (.va)"),
                                       parent=self.parent_window,
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.set_current_folder(initial_dir)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            model_file = dialog.get_filename()
            self.simulation_runner.set_model(model_file)
            print(_("Модель выбрана:"), os.path.basename(model_file))
            dialog.destroy()
            self.__show_message_dialog(("Уведомление"),
                                       ("Модель выбрана: ") + os.path.basename(model_file),
                                       Gtk.MessageType.INFO)
        else:
            dialog.destroy()

    def choose_spice_file(self, widget):
        """Выбор SPICE-файла через диалог."""
        try:
            if not self.parsing_file:
                self.__show_message_dialog(("Ошибка"), ("Сначала выберите файл параметров."), Gtk.MessageType.ERROR)
                return
            parent_dir_name = os.path.basename(os.path.dirname(os.path.dirname(self.parsing_file)))
            initial_dir = os.path.join(SPICE_EXAMPLES_PATH, parent_dir_name)
            dialog = Gtk.FileChooserDialog(title=_("Выберите SPICE-файл"),
                                           parent=self.parent_window,
                                           action=Gtk.FileChooserAction.OPEN)
            dialog.set_current_folder(initial_dir)
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                               Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
            if dialog.run() == Gtk.ResponseType.OK:
                self.spice_file = dialog.get_filename()
                print(_("Spice-схема выбрана:"), self.spice_file)
                dialog.destroy()
                self.__show_message_dialog(_("Уведомление"),
                                           _("Spice-схема выбрана ") + self.spice_file,
                                           Gtk.MessageType.INFO)
            else:
                dialog.destroy()
        except Exception as e:
            self.__show_message_dialog(("Ошибка"), ("Ошибка при загрузке параметров: ") + str(e), Gtk.MessageType.ERROR)
            return

    def apply_changes(self, widget):
        """Применяет изменения к файлу параметров."""
        if not self.simulation_runner:
            self.__show_message_dialog(_("Ошибка"), ("Модель не выбрана."), Gtk.MessageType.ERROR)
            return
        current_parameters = {}
        for param in self.parameter_entries:
            current_parameters[param["name"]] = param["entry"].get_text()
        try:
            self.file_manager.apply_changes_to_file(current_parameters, self.parsing_file)
            self.__show_message_dialog(("Уведомление"),
                                       ("Изменения успешно применены в ") + self.parsing_file + ".",
                                       Gtk.MessageType.INFO)
        except Exception as e:
            self.__show_message_dialog(("Ошибка"), ("Не удалось применить изменения."), Gtk.MessageType.ERROR)
            return

    def start_simulation(self, button):
        """Запускает симуляцию с обновлением прогресса и обработкой ошибок."""
        if not self.simulation_runner:
            self.__show_message_dialog(_("Ошибка"), ("Сначала выберите файл параметров."), Gtk.MessageType.ERROR)
            return
        if not self.spice_file:
            self.__show_message_dialog(_("Ошибка"), ("Сначала выберите SPICE-файл."), Gtk.MessageType.ERROR)
            return

        def simulate():
            try:
                for progress in self.simulation_runner.run_simulation(
                        spice_file=self.spice_file,
                        canvas=self.canvas_plot,
                        fig=self.fig):
                    if isinstance(progress, str):
                        GLib.idle_add(self.__show_error_dialog, progress)
                        return
                    GLib.idle_add(self.__update_progress_bar, progress)
            except RuntimeError as warning:
                GLib.idle_add(self.__show_message_dialog, ("Предупреждение"), str(warning), Gtk.MessageType.WARNING)
            except Exception as e:
                message = ("Ошибка симуляции: %s") % str(e)
                # GLib.idle_add(self.__show_message_dialog, _("Ошибка"), message, Gtk.MessageType.ERROR)

        threading.Thread(target=simulate, daemon=True).start()

    def on_save_csv(self, widget):
        if not os.path.exists(self.user_result_file) or os.path.getsize(self.user_result_file) == 0:
            dialog = Gtk.MessageDialog(transient_for=self.parent_window,
                                       flags=0,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK,
                                       text=_("Сохранение CSV"))
            dialog.format_secondary_text(_("Симуляция не была выполнена, нет данных для сохранения."))
            dialog.run()
            dialog.destroy()
            return
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=self.parsing_file, ignore_params_loader=ignore_params_loader)
            parser.save_simulation_results(input_file=self.user_result_file, directory=OUTPUT_DATA_PATH)
        except Exception as e:
            print(_("Ошибка сохранения CSV:"), e)

    def __show_error_dialog(self, error_message):
        """Выводит окно с ошибкой симуляции."""
        dialog = Gtk.MessageDialog(parent=self.parent_window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=error_message)
        dialog.run()
        dialog.destroy()

    def __show_message_dialog(self, title, message, message_type):
        dialog = Gtk.MessageDialog(parent=self.parent_window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     type=message_type,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def __update_progress_bar(self, progress):
        if hasattr(self.parent_window, 'progress_bar'):
            self.progress_bar.set_fraction(progress)

    def toggle_log_scale(self, widget, state):
        """Переключение логарифмической шкалы без сброса масштаба."""
        current_xlim, current_ylim = self.ax.get_xlim(), self.ax.get_ylim()
        
        self.ax.set_yscale("log" if state else "linear")

        if not self.ax.get_lines():
            print("Warning: No data on graph, switching scale but no effect on plot.")
            self.canvas_plot.draw_idle()
            return

        for line in self.ax.get_lines():
            line.set_ydata(line.get_ydata())

        self.ax.set_xlim(current_xlim)
        self.ax.set_ylim(current_ylim)

        self.canvas_plot.draw_idle()

    def toggle_grid(self, switch, state):
        if state:
            self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        else:
            self.ax.grid(False)
        self.canvas_plot.draw_idle()
        return True
    
    def save_plot(self, widget):
        """Сохранение графика в папку и вывод уведомления."""
        os.makedirs(PICS_PATH, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(PICS_PATH, f'plot_{current_time}.png')
        self.fig.savefig(file_path)

        dialog = Gtk.MessageDialog(
            parent=self.parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=f"График успешно сохранён в:\n{file_path}"
        )
        dialog.set_title("Сохранение графика")
        dialog.run()
        dialog.destroy()

    def on_press(self, widget, event):
        """Начало выделения области на графике."""
        if self.original_xlim is None or self.original_ylim is None:
            self.original_xlim, self.original_ylim = self.ax.get_xlim(), self.ax.get_ylim()

        if event.button == Gdk.BUTTON_PRIMARY:
            allocation = self.canvas_plot.get_allocation()
            ax = self.fig.axes[0]
            x_lim, y_lim = ax.get_xlim(), ax.get_ylim()
            self.start_point = (
                x_lim[0] + (event.x / allocation.width) * (x_lim[1] - x_lim[0]),
                y_lim[0] + ((allocation.height - event.y) / allocation.height) * (y_lim[1] - y_lim[0])
            )

    def on_release(self, widget, event):
        """При отпускании мыши область приближается."""
        if not self.start_point:
            return

        allocation = self.canvas_plot.get_allocation()
        ax = self.fig.axes[0]
        x_lim, y_lim = ax.get_xlim(), ax.get_ylim()
        x1, y1 = (
            x_lim[0] + (event.x / allocation.width) * (x_lim[1] - x_lim[0]),
            y_lim[0] + ((allocation.height - event.y) / allocation.height) * (y_lim[1] - y_lim[0])
        )

        x0, y0 = self.start_point
        if x0 != x1 and y0 != y1:
            ax.set_xlim(min(x0, x1), max(x0, x1))
            ax.set_ylim(min(y0, y1), max(y0, y1))
            self.canvas_plot.draw()
        
        self.start_point = None

    def on_motion(self, widget, event):
        """Обновление прямоугольника выделения."""
        if not self.start_point:
            return

        allocation = self.canvas_plot.get_allocation()
        ax = self.fig.axes[0]
        x_lim, y_lim = ax.get_xlim(), ax.get_ylim()
        
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None
        
        x1, y1 = (
            x_lim[0] + (event.x / allocation.width) * (x_lim[1] - x_lim[0]),
            y_lim[0] + ((allocation.height - event.y) / allocation.height) * (y_lim[1] - y_lim[0])
        )

        self.selection_rect = plt.Rectangle(
            (self.start_point[0], self.start_point[1]),
            x1 - self.start_point[0], y1 - self.start_point[1],
            edgecolor="red", facecolor="none", linewidth=1.5
        )

        ax.add_patch(self.selection_rect)
        self.canvas_plot.draw()

    def on_scroll(self, widget, event):
        """Handle mouse scroll events to zoom in or out on the plot."""
        if not self.fig or not self.fig.axes:
            return

        ax = self.fig.axes[0]
        x_lim, y_lim = ax.get_xlim(), ax.get_ylim()

        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

        ZOOM_IN_FACTOR, ZOOM_OUT_FACTOR = 0.8, 1.25
        zoom_factor = ZOOM_IN_FACTOR if event.direction == Gdk.ScrollDirection.UP else ZOOM_OUT_FACTOR

        allocation = self.canvas_plot.get_allocation()
        x_center = x_lim[0] + (event.x / allocation.width) * (x_lim[1] - x_lim[0])
        y_center = y_lim[0] + ((allocation.height - event.y) / allocation.height) * (y_lim[1] - y_lim[0])

        x_range = (x_lim[1] - x_lim[0]) * zoom_factor
        y_range = (y_lim[1] - y_lim[0]) * zoom_factor

        ax.set_xlim([x_center - x_range / 2, x_center + x_range / 2])
        ax.set_ylim([y_center - y_range / 2, y_center + y_range / 2])
        self.canvas_plot.draw()

    def reset_zoom(self, widget):
        """Сбрасывает масштаб графика до исходного состояния и удаляет выделение."""
        if not self.fig or not self.fig.axes:
            return

        ax = self.fig.axes[0]
        ax.set_xlim(self.original_xlim)
        ax.set_ylim(self.original_ylim)

        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

        self.canvas_plot.draw_idle()    

    # def toggle_parameter(self, switch, state):
    #     """Обработчик переключения параметра."""
    #     print(f"Parameter toggled. New state: {'Enabled' if state else 'Disabled'}")

    #     #TODO: над этим вообще не работал и не смотрел, просто оставил как есть, пока что
    #     #сама функция задумывалась именно дляя изменения параметров в списке. В ios_swtich есть функция on_toggle, отвечающая за визуал и анимацию переключения, так что можешь это использовать
    #     if state:
    #         label.set_text(label.get_text().replace("̶", ""))
    #         entry.set_sensitive(True)
    #     else:
    #         label.set_text("̶" + label.get_text())
    #         entry.set_sensitive(False)
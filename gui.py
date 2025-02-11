import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from config import COLORS, DIRECTORY
from graphics.handlers import SimulatorHandlers


import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from config import DIRECTORY


class NGSPICESimulatorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="NGSPICE Simulator")
        self.set_default_size(1360, 640)
        self.set_border_width(10)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.73, 0.76, 0.79, 1.0))  # #BAC3C9

        self.parsing_file = "No File Selected"
        self.simulation_runner = None
        # self.file_manager = FileManager()
        self.parameter_entries = []
        self.spice_file = None
        
        self.handlers = SimulatorHandlers(self)  # инициализация обработчиков

        self.fig, self.ax = plt.subplots()  # полотно для графика
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)
        self.canvas_plot = FigureCanvas(self.fig)

        # Создаем params_box перед вызовом create_left_panel
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        
        #TODO: лучше перенести все что со стилями в отдельный модуль style.css (например)
        self.apply_styles()  # Стили кнопки для строки файла


        self.create_interface()  # создание интерфейса

        self.__setup_directories()

    def __setup_directories(self):
        for directory in DIRECTORY:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def create_interface(self):
        """Создание интерфейса."""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(container)  # основной контейнер с возможностью масштабирования панелей

        left_panel = self.create_left_panel()
        left_panel.set_hexpand(False)
        container.pack_start(left_panel, False, False, 0)

        right_panel = self.create_right_panel()  # правая панель (графики и прогресс-бар)
        right_panel.set_hexpand(True)
        container.pack_start(right_panel, True, True, 0)

    def create_left_panel(self):
        # Создает левую панель с кнопками, параметрами и строкой файла
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(300, -1)



        self.file_button = Gtk.Button(label="File:/...")  # кнопка для отображения пути файла
        self.file_button.set_hexpand(True)
        self.file_button.set_halign(Gtk.Align.FILL)  # Растягиваем на всю ширину
        self.file_button.get_style_context().add_class("file-display-button")  # Для кастомного стиля
        self.file_button.connect("clicked", self.handlers.choose_parsing_file)
        left_panel.pack_start(self.file_button, False, False, 0)




        button_frame = Gtk.Frame()  # блок кнопок с общим фоном
        button_frame.set_shadow_type(Gtk.ShadowType.NONE)  # убираем рамку, оставляем только фон
        button_frame.get_style_context().add_class("rounded-block")
        button_frame.set_hexpand(True)

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(5)
        button_grid.set_row_spacing(5)
        button_grid.set_margin_top(10)  # Внутренние отступы
        button_grid.set_margin_bottom(10)
        button_grid.set_margin_start(10)
        button_grid.set_margin_end(10)
        button_grid.set_hexpand(True)  # Растягиваем сетку по ширине

        button_labels = ["Выбрать модель", "Применить изменения", "Выбрать SPICE-файл", "Запустить симуляцию"]
        button_callbacks = [
            self.handlers.choose_model,
            self.handlers.apply_changes,
            self.handlers.choose_spice_file,
            self.handlers.start_simulation
        ]
        for i, (label, callback) in enumerate(zip(button_labels, button_callbacks)):
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.set_hexpand(True)  # Растягиваем кнопки по ширине
            button_grid.attach(button, i % 2, i // 2, 1, 1)
        button_frame.add(button_grid)
        left_panel.pack_start(button_frame, False, False, 0)


        # Секция параметров
        params_scroller = Gtk.ScrolledWindow()
        params_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        params_scroller.add(self.params_box)
        left_panel.pack_start(params_scroller, True, True, 0)

        return left_panel

    


    def create_right_panel(self):
        """Создает правую панель с графиком и прогресс-баром."""
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        right_panel.set_hexpand(True)

        self.progress_bar = Gtk.ProgressBar()
        right_panel.pack_start(self.progress_bar, False, False, 0)
        right_panel.pack_start(self.canvas_plot, True, True, 0)

        return right_panel


    

#FIXME лучше под стили сделать отдельный модуль, style.css и там уже делать
    def apply_styles(self):
        # Применяет стили для кнопки и блоков
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
        button.file-display-button {
            background: rgba(217, 217, 217, 1);
            border-radius: 10px;
            border: none;
            padding: 5px 10px;
            color: black;
            font-size: 14px;
            font-family: "Sans";
        }
        button.file-display-button:hover {
            background: rgba(200, 200, 200, 1);
        }
        frame.rounded-block {
            background: rgba(217, 217, 217, 1); /* Мягкий серый фон */
            border-radius: 10px;
        }
        label.graph-title {
            font-size: 16px;
            font-weight: bold;
            color: #333;
        }
        button.control-button {
            background: rgba(217, 217, 217, 1);
            border-radius: 5px;
            padding: 5px 10px;
        }
        button.control-button:hover {
            background: rgba(200, 200, 200, 1);
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
    
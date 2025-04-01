import os
import gi

gi.require_version("Gtk", "3.0")  # Требуемая версия GTK
from gi.repository import Gtk, Gdk, GLib
from config import DIRECTORY, INITIAL_LOG_SCALE, INITIAL_GRID
from graphics.gtk.handlers import SimulatorHandlers
from graphics.gtk.model_selector import ModelSelectorHandler
from graphics.ios_switch import IosStyleSwitch
from graphics.factory.base import BaseApp
from graphics.gtk.progress_bar import ProgressBar

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


class NGSPICESimulatorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title=_("NGSPICE Simulator"))
        self.set_default_size(1360, 740)
        self.set_border_width(10)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.73, 0.76, 0.79, 1.0))  #BAC3C9

        self.file_button = Gtk.Button(label=_("File:/..."))  # кнопка для отображения пути файла
        self.file_button.get_style_context().add_class("ios-button")
        
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.fig, self.ax = plt.subplots()
        self.canvas_plot = FigureCanvas(self.fig)
        self.fig.set_layout_engine("tight")
        self.canvas_plot.set_size_request(-1, -1)

        self.log_scale_switch = IosStyleSwitch(active=INITIAL_LOG_SCALE)
        self.grid_switch = IosStyleSwitch(active=INITIAL_GRID)

        self.progress_bar = ProgressBar()
        self.handlers = SimulatorHandlers(
                            self.params_box,
                            self.file_button,
                            self.fig,
                            self.ax,
                            self.canvas_plot,
                            self.progress_bar,
                            parent_window=self)  # инициализация обработчиков

        self.model_selector = ModelSelectorHandler(self, self.handlers)

        self.__setup_directories()  # создание необходимых директорий, если они не существуют
        
        self.create_interface()  # создание интерфейса
        self.apply_styles()  # стили кнопки для строки файла

        self.handlers.toggle_log_scale(self.log_scale_switch, INITIAL_LOG_SCALE)
        self.handlers.toggle_grid(self.grid_switch, INITIAL_GRID)

        visual = self.get_screen().get_rgba_visual()
        if visual and self.get_screen().is_composited():
            self.set_visual(visual)

        self.canvas_plot.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.canvas_plot.connect("scroll-event", self.handlers.on_scroll)
        self.canvas_plot.connect("button-press-event", self.handlers.on_press)
        self.canvas_plot.connect("button-release-event", self.handlers.on_release)
        self.canvas_plot.connect("motion-notify-event", self.handlers.on_motion)

    def __setup_directories(self):
        """
        Проверяет наличие директорий, указанных в DIRECTORY, и создаёт их при необходимости.
        """
        for directory in DIRECTORY:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def create_interface(self):
        """Создание интерфейса."""
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)  # основной контейнер с горизонтальной ориентацией для размещения левой и правой панелей
        self.add(container)

        left_panel = self.create_left_panel()
        left_panel.set_hexpand(False)
        container.pack_start(left_panel, False, False, 0)

        right_panel = self.create_right_panel()
        right_panel.set_hexpand(True)
        container.pack_start(right_panel, True, True, 0)

    def create_left_panel(self):
        """Создает левую панель с кнопками, параметрами и строкой файла."""
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, width_request=300)
        left_panel.pack_start(self.model_selector.get_widget(), False, False, 0)

        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        for margin in ("top", "bottom", "start", "end"):
            getattr(action_box, f"set_margin_{margin}")(5)

        button_grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        button_grid.get_style_context().add_class("rounded-block")
        for margin in ("top", "bottom", "start", "end"):
            getattr(button_grid, f"set_margin_{margin}")(5)

        buttons = [
            (_("Применить изменения"), self.handlers.apply_changes),
            (_("Запустить симуляцию"), self.handlers.start_simulation)
        ]
        
        for idx, (label, callback) in enumerate(buttons):
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.set_hexpand(True)
            button.set_alignment(0.5, 0.75)
            button.get_style_context().add_class("ios-button")
            button_grid.attach(button, idx % 2, idx // 2, 1, 1)

        left_panel.pack_start(button_grid, False, False, 0)

        params_scroller = Gtk.ScrolledWindow()
        params_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        params_scroller.add(self.params_box)
        left_panel.pack_start(params_scroller, True, True, 0)
        return left_panel

    def create_right_panel(self):
        """Создает правую панель с графиком и прогресс-баром."""
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, hexpand=True)

        self.progress_bar.set_size_request(200, 30)
        self.progress_bar.progress_fraction = 0.0

        canvas_container = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        canvas_container.get_style_context().add_class("transparent-container")
        canvas_container.add(self.canvas_plot)

        graph_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        graph_container.pack_start(self.progress_bar, False, False, 0)
        graph_container.get_style_context().add_class("no-shadow-box")
        graph_container.pack_start(canvas_container, True, True, 10)

        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5, valign=Gtk.Align.CENTER)
        for margin in ("top", "bottom", "start", "end"):
            getattr(control_box, f"set_margin_{margin}")(5)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        left_controls = [
            (_("Log Scale:"), self.log_scale_switch),
            (_("Grid:"), self.grid_switch)
        ]

        for label_text, widget in left_controls:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_valign(Gtk.Align.CENTER)
            label = Gtk.Label(label=label_text, xalign=0)
            label.set_valign(Gtk.Align.CENTER)
            widget.set_valign(Gtk.Align.CENTER)
            widget.set_size_request(50, 25)

            if label_text == _("Log Scale:"):
                widget.connect("state-set", self.handlers.toggle_log_scale)
            elif label_text == _("Grid:"):
                widget.connect("state-set", self.handlers.toggle_grid)

            hbox.pack_start(label, False, False, 5)
            hbox.pack_start(widget, False, False, 5)
            left_box.pack_start(hbox, False, False, 5)

        reset_button = Gtk.Button(label="Reset Scale")
        reset_button.get_style_context().add_class("ios-button")
        reset_button.set_alignment(0.5, 0.75)
        reset_button.connect("clicked", self.handlers.reset_zoom)

        save_button = Gtk.Button(label=("Save Graph"))
        save_button.get_style_context().add_class("ios-button")
        save_button.set_alignment(0.5, 0.75)
        save_button.connect("clicked", self.handlers.save_plot)

        save_csv_button = Gtk.Button(label=_("Save CSV"))
        save_csv_button.get_style_context().add_class("ios-button")
        save_csv_button.set_alignment(0.5, 0.75)
        save_csv_button.connect("clicked", self.handlers.on_save_csv)

        right_box.pack_start(reset_button, False, False, 5)
        right_box.pack_start(save_csv_button, False, False, 5)
        right_box.pack_start(save_button, False, False, 5)

        control_box.pack_start(left_box, False, False, 5)
        control_box.pack_end(right_box, False, False, 5)

        right_panel.pack_start(graph_container, True, True, 0)
        right_panel.pack_end(control_box, False, False, 10)

        return right_panel

    def apply_styles(self):
        """
        Применяет CSS-стили к элементам интерфейса.
        Загружает файл стилей из директории graphics.
        """
        css_provider = Gtk.CssProvider()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_file = os.path.join(current_dir, "graphics", "style.css")
        css_provider.load_from_path(css_file)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

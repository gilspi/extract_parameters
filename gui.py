import os

import gi
gi.require_version("Gtk", "3.0")  # Требуемая версия GTK
from gi.repository import Gtk, Gdk
from config import DIRECTORY
from graphics.handlers import SimulatorHandlers
from ios_switch import IosStyleSwitch

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


class ProgressBar(Gtk.DrawingArea):
    """Класс кастомного прогресс-бара, наследуется от Gtk.DrawingArea для возможности рисования"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_fraction = 0.0  # Инициализация прогресса (от 0 до 1)
        self.connect("draw", self.on_draw)  # Подключаем обработчик события рисования

    def set_fraction(self, fraction):
        """Обновляет значение прогресса и перерисовывает виджет."""
        self.progress_fraction = fraction  # Обновление внутреннего значения прогресса
        self.queue_draw()  # Запрос перерисовки виджета

    def on_draw(self, widget, cr):
        """Обработчик события рисования. Отвечает за визуальное представление прогресс-бара."""
        width = widget.get_allocated_width()   # Получение текущей ширины виджета
        height = widget.get_allocated_height()   # Получение текущей высоты виджета
        radius = height / 2  # Вычисление радиуса для закруглённых углов

        # Рисуем фон
        cr.set_source_rgb(0.85, 0.85, 0.85)  # Установка цвета фона (светло-серый)
        # Рисуем дуги по углам для создания закруглённого прямоугольника
        cr.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        cr.arc(width - radius, radius, radius, 1.5 * 3.14, 0)
        cr.arc(width - radius, height - radius, radius, 0, 0.5 * 3.14)
        cr.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        cr.close_path()  # Замыкаем контур
        cr.fill()  # Заполняем фигуру выбранным цветом

        # Рисуем заполненную часть, используя widget.progress_fraction
        cr.set_source_rgb(0.66, 0.87, 0.68)  # Устанавливаем цвет заполненной части (оттенок зелёного)
        # Определяем ширину заполненной области (не менее двойного радиуса, чтобы сохранить закругление)
        fill_width = max(radius * 2, width * widget.progress_fraction)
        # Рисуем заполненную часть аналогично фону, но с шириной fill_width
        cr.arc(radius, radius, radius, 3.14, 1.5 * 3.14)
        cr.arc(fill_width - radius, radius, radius, 1.5 * 3.14, 0)
        cr.arc(fill_width - radius, height - radius, radius, 0, 0.5 * 3.14)
        cr.arc(radius, height - radius, radius, 0.5 * 3.14, 3.14)
        cr.close_path()
        cr.fill()

        # Рисуем текст прогресса
        cr.set_source_rgb(0, 0, 0)  # Цвет текста - чёрный
        cr.select_font_face("Code", 0, 0)  # Выбор шрифта (можно заменить на другой, если требуется)
        cr.set_font_size(16)  # Размер шрифта
        progress_text = f"{int(widget.progress_fraction * 100)}%"  # Формирование текста с процентами
        text_extents = cr.text_extents(progress_text)  # Получение размеров текста для центрирования
        text_x = (width - text_extents.width) / 2  # Вычисление горизонтальной позиции текста
        text_y = (height - text_extents.height) / 2 - text_extents.y_bearing  # Вычисление вертикальной позиции текста
        cr.move_to(text_x, text_y)  # Перемещение "перо" в позицию текста
        cr.show_text(progress_text)  # Отображение текста


class NGSPICESimulatorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="NGSPICE Simulator")
        self.set_default_size(1360, 740)
        self.set_border_width(10)
        
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.73, 0.76, 0.79, 1.0))  #BAC3C9

        
        # self.file_manager = FileManager()  # Комментарий: возможно, управление файлами планируется реализовать позднее
        
        self.file_button = Gtk.Button(label="File:/...")  # кнопка для отображения пути файла
        
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.fig, self.ax = plt.subplots()
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)  # Добавление сетки на график
        self.fig.set_layout_engine("tight")  # Использование плотного расположения элементов
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # Настройка отступов для графика
        self.canvas_plot = FigureCanvas(self.fig)
        self.canvas_plot.set_size_request(-1, -1)

        
        self.progress_bar = ProgressBar()
        self.handlers = SimulatorHandlers(self.params_box, self.file_button, self.fig, self.ax, self.canvas_plot, self.progress_bar, parent_window=self)  # инициализация обработчиков

        self.apply_styles()  # стили кнопки для строки файла

        self.create_interface()  # создание интерфейса

        self.__setup_directories()  # создание необходимых директорий, если они не существуют

        visual = self.get_screen().get_rgba_visual()
        if visual and self.get_screen().is_composited():
            self.set_visual(visual)

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

        self.file_button.set_hexpand(True)
        self.file_button.set_halign(Gtk.Align.FILL)
        self.file_button.get_style_context().add_class("file-display-button")
        self.file_button.connect("clicked", self.handlers.choose_parsing_file)
        left_panel.pack_start(self.file_button, False, False, 0)

        button_grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        for margin in ("top", "bottom", "start", "end"):
            getattr(button_grid, f"set_margin_{margin}")(5)

        buttons = [
            ("Выбрать модель", self.handlers.choose_model),
            ("Применить изменения", self.handlers.apply_changes),
            ("Выбрать SPICE-файл", self.handlers.choose_spice_file),
            ("Запустить симуляцию", self.handlers.start_simulation)
        ]
        for idx, (label, callback) in enumerate(buttons):
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.set_hexpand(True)
            button.get_style_context().add_class("button")
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

        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5, valign=Gtk.Align.CENTER) # Control Box с элементами управления
        control_box.set_size_request(200, 50)
        control_box.get_style_context().add_class("control-box")

        for margin in ("top", "bottom", "start", "end"):  # устанавливаем одинаковые отступы
            getattr(control_box, f"set_margin_{margin}")(5)

        controls = [
            ("Log Scale:", IosStyleSwitch()),
            ("Grid:", IosStyleSwitch()),
            ("", Gtk.Button(label="Reset Scale"))
        ]  # создаём элементы управления (Log Scale, Grid, Reset)

        for label_text, widget in controls:
            if label_text:
                label = Gtk.Label(label=label_text, xalign=0, valign=Gtk.Align.CENTER)
                control_box.pack_start(label, False, False, 5)
            widget.set_size_request(50, 25) if isinstance(widget, IosStyleSwitch) else widget.get_style_context().add_class("control-button")
            control_box.pack_start(widget, False, False, 5)

        # Собираем всё в `right_panel`
        right_panel.pack_start(graph_container, True, True, 0)
        right_panel.pack_end(control_box, False, False, 10)

        return right_panel


    def apply_styles(self):
        """
        Применяет CSS-стили к элементам интерфейса.
        Загружает файл стилей из директории graphics.
        """
        css_provider = Gtk.CssProvider()
        # Определяем путь к файлу стилей, предполагается, что он находится в папке graphics рядом с gui.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_file = os.path.join(current_dir, "graphics", "style.css")
        css_provider.load_from_path(css_file)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

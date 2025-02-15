import os  # Модуль для работы с файловой системой

import gi  # PyGObject для работы с библиотекой GTK
gi.require_version("Gtk", "3.0")  # Требуемая версия GTK
from gi.repository import Gtk, Gdk, GLib  # Импорт необходимых компонентов GTK и вспомогательных библиотек
from config import COLORS, DIRECTORY  # Импорт цветовой схемы и списка директорий из конфигурационного файла
from graphics.handlers import SimulatorHandlers  # Импорт обработчиков событий для симулятора
from ios_switch import IosStyleSwitch


import matplotlib.pyplot as plt  # Библиотека для построения графиков
from datetime import datetime  # Для работы с датой и временем
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas  # Интеграция matplotlib с GTK
from config import DIRECTORY  # Импорт списка директорий из конфигурационного файла (дублируется, возможно, для удобства)

# Класс кастомного прогресс-бара, наследуется от Gtk.DrawingArea для возможности рисования
class ProgressBar(Gtk.DrawingArea):
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

# Основной класс приложения симулятора, наследуется от Gtk.Window
class NGSPICESimulatorApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="NGSPICE Simulator")  # Установка заголовка окна
        self.set_default_size(1360, 740)  # Установка размера окна по умолчанию
        self.set_border_width(10)  # Отступы вокруг содержимого окна
        # Задание фонового цвета окна
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.73, 0.76, 0.79, 1.0))  # #BAC3C9

        # Инициализация переменных для работы с файлами и симуляцией
        self.parsing_file = "No File Selected"
        self.simulation_runner = None
        # self.file_manager = FileManager()  # Комментарий: возможно, управление файлами планируется реализовать позднее
        self.parameter_entries = []  # Список для хранения виджетов ввода параметров
        self.spice_file = None  # Путь к SPICE-файлу, выбранному пользователем
        
        self.handlers = SimulatorHandlers(self)  # инициализация обработчиков

        # Инициализация области для графиков с использованием matplotlib
        self.fig, self.ax = plt.subplots()  # Создание фигуры и оси для построения графика
        self.fig.patch.set_facecolor((0, 0, 0, 0))  # Установка прозрачного фона для фигуры
        self.ax.patch.set_alpha(0)            # Фон области построения прозрачный
        self.ax.set_facecolor((0, 0, 0, 0))
        self.ax.grid(True, which="both", linestyle="--", linewidth=0.5)  # Добавление сетки на график
        self.fig.set_layout_engine("tight")  # Использование плотного расположения элементов
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # Настройка отступов для графика
        self.canvas_plot = FigureCanvas(self.fig)  # Создание GTK-виджета для отображения графика
        
        # Создаем params_box перед вызовом create_left_panel
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.apply_styles()  # Стили кнопки для строки файла

        self.create_interface()  # создание интерфейса

        self.__setup_directories()  # Создание необходимых директорий, если они не существуют

        # Настройка прозрачности окна (если поддерживается композитинг)
        visual = self.get_screen().get_rgba_visual()
        if visual and self.get_screen().is_composited():
            self.set_visual(visual)

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

    def __setup_directories(self):
        """
        Проверяет наличие директорий, указанных в DIRECTORY, и создаёт их при необходимости.
        """
        for directory in DIRECTORY:
            if not os.path.exists(directory):
                os.makedirs(directory)  # Создание директории, если она не существует

    def create_interface(self):
        """Создание интерфейса."""
        # Основной контейнер с горизонтальной ориентацией для размещения левой и правой панелей
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(container)  # Добавление контейнера в окно

        left_panel = self.create_left_panel()  # Создание левой панели (с кнопками, параметрами и файлом)
        left_panel.set_hexpand(False)
        container.pack_start(left_panel, False, False, 0)

        right_panel = self.create_right_panel()  # Правая панель (с графиком и прогресс-баром)
        right_panel.set_hexpand(True)
        container.pack_start(right_panel, True, True, 0)

    def create_left_panel(self):
        """
        Создает левую панель с кнопками, параметрами и строкой файла.
        Возвращает Gtk.Box, содержащий все элементы левой панели.
        """
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(300, -1)  # Фиксированная ширина панели

        # Кнопка для отображения пути файла
        self.file_button = Gtk.Button(label="File:/...")  # кнопка для отображения пути файла
        self.file_button.set_hexpand(True)
        self.file_button.set_size_request(300, 30)
        self.file_button.set_halign(Gtk.Align.FILL)  # Растягиваем на всю ширину
        self.file_button.get_style_context().add_class("file-display-button")  # Для кастомного стиля
        self.file_button.connect("clicked", self.handlers.choose_parsing_file)
        left_panel.pack_start(self.file_button, False, False, 0)

        # Блок кнопок с общим фоном
        button_frame = Gtk.Frame()  # блок кнопок с общим фоном
        button_frame.set_shadow_type(Gtk.ShadowType.NONE)  # убираем рамку, оставляем только фон
        button_frame.get_style_context().add_class("rounded-block")
        button_frame.set_hexpand(True)

        # Создание сетки для размещения кнопок в два столбца
        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(5)
        button_grid.set_row_spacing(5)
        button_grid.set_margin_top(5)  # Внутренние отступы
        button_grid.set_margin_bottom(5)
        button_grid.set_margin_start(5)
        button_grid.set_margin_end(5)
        button_grid.set_hexpand(True)  # Растягиваем сетку по ширине

        # Определение меток кнопок и соответствующих обработчиков
        button_labels = ["Выбрать модель", "Применить изменения", "Выбрать SPICE-файл", "Запустить симуляцию"]
        button_callbacks = [
            self.handlers.choose_model,
            self.handlers.apply_changes,
            self.handlers.choose_spice_file,
            self.handlers.start_simulation
        ]
        # Создание и размещение кнопок в сетке
        for i, (label, callback) in enumerate(zip(button_labels, button_callbacks)):
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.set_hexpand(True)  # Растягиваем кнопки по ширине
            button.get_style_context().add_class("button")  # Для кастомного стиля
            button_grid.attach(button, i % 2, i // 2, 1, 1)
        button_frame.add(button_grid)
        left_panel.pack_start(button_frame, False, False, 0)

        # Секция параметров с возможностью прокрутки
        params_scroller = Gtk.ScrolledWindow()
        params_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        params_scroller.add(self.params_box)
        left_panel.pack_start(params_scroller, True, True, 0)

        return left_panel

    def create_right_panel(self):
        """Создает правую панель с графиком и прогресс-баром."""
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        right_panel.set_hexpand(True)

        # Инициализация кастомного прогресс-бара
        self.progress_bar = ProgressBar()
        self.progress_bar.set_size_request(200, 30)
        self.progress_bar.progress_fraction = 0.0  # начальное значение

        # Создаем контейнер для canvas_plot и задаем ему CSS-класс
        canvas_container = Gtk.Frame()
        canvas_container.set_shadow_type(Gtk.ShadowType.NONE)
        canvas_container.add(self.canvas_plot)
        canvas_container.get_style_context().add_class("canvas-container")

        # Контейнер для размещения прогресс-бара и области графика
        graph_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        graph_container.pack_start(self.progress_bar, False, False, 0)
        graph_container.get_style_context().add_class("no-shadow-box")
        # Последний параметр в pack_start — это padding (в пикселях), увеличиваем его
        graph_container.pack_start(canvas_container, True, True, 10)

        # Настройка растяжения для контейнеров и canvas_plot
        canvas_container.set_hexpand(True)
        canvas_container.set_vexpand(True)
        self.canvas_plot.set_hexpand(True)
        self.canvas_plot.set_vexpand(True)
        right_panel.pack_start(graph_container, True, True, 0)

       # Создаём control_box с нужными отступами, выравниванием и фиксированной высотой
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        control_box.set_margin_top(0)
        control_box.set_margin_bottom(5)
        control_box.set_margin_start(0)
        control_box.set_margin_end(0)
        control_box.set_size_request(200, 50)  # Фиксированная высота 50 пикселей
        control_box.set_valign(Gtk.Align.CENTER)
        control_box.get_style_context().add_class("control-box")

        # Создаем элементы управления
        logscale_label = Gtk.Label(label="Log Scale:")
        logscale_label.set_xalign(0)
        logscale_label.set_valign(Gtk.Align.CENTER)

        logscale_switch = IosStyleSwitch()
        logscale_switch.set_size_request(50, 25)
        logscale_switch.set_valign(Gtk.Align.CENTER)

        grid_label = Gtk.Label(label="Grid:")
        grid_label.set_xalign(0)
        grid_label.set_valign(Gtk.Align.CENTER)

        grid_switch = IosStyleSwitch()
        grid_switch.set_size_request(50, 25)
        grid_switch.set_valign(Gtk.Align.CENTER)

        reset_button = Gtk.Button(label="Reset Scale")
        reset_button.get_style_context().add_class("control-button")
        reset_button.set_valign(Gtk.Align.CENTER)

        # Упаковываем виджеты в control_box
        control_box.pack_start(logscale_label, False, False, padding=5)
        control_box.pack_start(logscale_switch, False, False, padding=5)
        control_box.pack_start(grid_label, False, False, padding=5)
        control_box.pack_start(grid_switch, False, False, padding=5)
        control_box.pack_end(reset_button, False, False, padding=5)

        # Добавляем graph_container и control_box в right_panel.
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

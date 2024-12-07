import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from core.simulation_runner import SimulationRunner
from core.parameter_parser import ParameterParser, FileIgnoreParamsLoader
from core.file_manager import FileManager
from matplotlib.backend_bases import MouseEvent
from config import IGNORE_PARAMS_FILE


class NGSPICESimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NGSPICE Симулятор")
        self.root.geometry("1360x640")  # Размер окна
        self.root.resizable(False, False)  # Отключение изменения размера окна

        # Переменные для отображения файлов и работы с параметрами
        self.parsing_file = tk.StringVar(value="Не выбран")
        self.simulation_runner = None
        self.file_manager = FileManager()
        self.parameter_entries = []

        # Переменные для сброса масштаба
        self.original_xlim = None
        self.original_ylim = None

        # Переменные для перемещения графика
        self.pan_start = None  # Начальная позиция для панорамирования
        self.pan_dx = 0
        self.pan_dy = 0

        # Создание интерфейса
        self.create_interface()

        # Слушаем события мыши на графике
        self.canvas_plot.mpl_connect('button_press_event', self.on_press)
        self.canvas_plot.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas_plot.mpl_connect('button_release_event', self.on_release)
        self.canvas_plot.mpl_connect('scroll_event', self.on_scroll)

    def create_sliders(self):
        """Создание слайдеров для управления пределами осей."""
        # Слайдер для X-оси
        self.x_max_slider = tk.Scale(
            self.root, from_=0, to=100, orient="horizontal", command=self.update_plot_from_sliders
        )
        self.x_max_slider.grid(row=5, column=3, sticky="ew")

        # Слайдер для Y-оси
        self.y_max_slider = tk.Scale(
            self.root, from_=100, to=0, orient="vertical", command=self.update_plot_from_sliders
        )
        self.y_max_slider.grid(row=1, column=2, rowspan=4, sticky="ns")

        # Установка начальных значений
        self.update_sliders_from_plot()

    def update_sliders_from_plot(self):
        """Обновление слайдеров на основе текущих значений пределов графика."""
        if self.fig:
            ax = self.fig.axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # Обновляем значения слайдеров
            self.x_max_slider.config(from_=xlim[0], to=xlim[1])
            self.y_max_slider.config(from_=ylim[1], to=ylim[0])

            self.x_max_slider.set(xlim[1])
            self.y_max_slider.set(ylim[0])

    def update_plot_from_sliders(self, event=None):
        """Обновление графика на основе значений слайдеров."""
        if self.fig:
            ax = self.fig.axes[0]

            # Получаем значения слайдеров
            x_max = self.x_max_slider.get()
            y_max = self.y_max_slider.get()

            # Обновляем пределы графика
            ax.set_xlim(right=x_max)
            ax.set_ylim(top=y_max)

            self.canvas_plot.draw()

    def on_scroll(self, event):
        """Обработка прокрутки мыши для зума."""
        ax = self.fig.axes[0]
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()

        # Определяем направление прокрутки
        if event.button == 'up':  # Вверх - приближаем
            zoom_factor = 0.8
        elif event.button == 'down':  # Вниз - отдаляем
            zoom_factor = 1.2
        else:
            zoom_factor = 1

        # Уменьшаем или увеличиваем диапазон осей
        ax.set_xlim([x_lim[0] * zoom_factor, x_lim[1] * zoom_factor])
        ax.set_ylim([y_lim[0] * zoom_factor, y_lim[1] * zoom_factor])

        # Обновляем слайдеры
        self.update_sliders_from_plot()
        self.canvas_plot.draw()

    def on_motion(self, event: MouseEvent):
        """Обработка перемещения мыши для перемещения графика."""
        if self.pan_start is not None and event.inaxes:
            dx = event.xdata - self.pan_start[0]
            dy = event.ydata - self.pan_start[1]

            if (dx != self.pan_dx) or (dy != self.pan_dy):
                ax = event.inaxes
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()

                ax.set_xlim([xlim[0] - dx, xlim[1] - dx])
                ax.set_ylim([ylim[0] - dy, ylim[1] - dy])

                # Обновляем слайдеры
                self.update_sliders_from_plot()
                self.canvas_plot.draw()

                self.pan_dx = dx
                self.pan_dy = dy

    def reset_plot_scale(self):
        """Сброс масштаба графика на исходное значение."""
        if self.original_xlim is None or self.original_ylim is None:
            ax = self.fig.axes[0]
            self.original_xlim = ax.get_xlim()
            self.original_ylim = ax.get_ylim()

        ax = self.fig.axes[0]
        ax.set_xlim(self.original_xlim)
        ax.set_ylim(self.original_ylim)

        # Обновляем слайдеры
        self.update_sliders_from_plot()
        self.canvas_plot.draw()

    def on_press(self, event: MouseEvent):
        """Обработка нажатия мыши для начала перемещения графика."""
        if event.inaxes:
            self.pan_start = (event.xdata, event.ydata)  # Сохраняем начальную точку для панорамирования

    def on_click(self, event: MouseEvent):
        """Обработка нажатия на график для активации зума."""
        if event.inaxes:
            ax = event.inaxes
            # Фокусируемся на точке клика, например, приближаем на 20% в том месте
            x_center = event.xdata
            y_center = event.ydata

            if x_center is not None and y_center is not None:
                ax.set_xlim([x_center - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.2, 
                             x_center + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.2])
                ax.set_ylim([y_center - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.2, 
                             y_center + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.2])

                self.canvas_plot.draw()

    def create_interface(self):
        """Создание интерфейса пользователя."""
        # Выбор файла для парсинга параметров
        tk.Label(self.root, text=f"Файл:").grid(row=0, column=0, sticky="ew")
        tk.Label(self.root, textvariable=self.parsing_file).grid(row=0, column=1, sticky="w")
        tk.Button(self.root, text="Выбрать файл", command=self.choose_parsing_file).grid(row=0, column=2, sticky="s")

        # Создаем область параметров
        self.scrollable_frame = None
        self.canvas_frame = None
        self.canvas_scrollbar = None
        self.create_scrollable_frame()

        # Кнопки управления
        tk.Button(self.root, text="Выбрать модель", command=self.choose_model).grid(
            row=2, column=0, columnspan=2, pady=5, sticky="ew"
        )
        tk.Button(self.root, text="Применить изменения", command=self.apply_changes).grid(
            row=3, column=0, columnspan=2, pady=5, sticky="ew"
        )
        tk.Button(self.root, text="Выбрать SPICE-файл", command=self.choose_spice_file).grid(
            row=4, column=0, columnspan=2, pady=5, sticky="ew"
        )
        tk.Button(self.root, text="Запустить симуляцию", command=self.start_simulation).grid(
            row=5, column=0, columnspan=2, pady=5, sticky="ew"
        )

        # Добавление чекбокса для логарифмического масштаба
        self.log_scale = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Log Scale", variable=self.log_scale, command=self.update_plot_scale).grid(
            row=0, column=3, sticky="w"
        )

        # Создание области для графика (должно быть вызвано перед слайдерами)
        self.fig, self.canvas_plot = self.create_plot_area()

        # Кнопка для сброса масштаба
        tk.Button(self.root, text="Сбросить масштаб", command=self.reset_plot_scale).grid(
            row=6, column=3, sticky="ew"
        )

        # Создание слайдеров после инициализации графика
        self.create_sliders()

    def on_release(self, event: MouseEvent):
        """Обработка отпускания кнопки мыши для завершения перемещения."""
        self.pan_start = None  # Завершаем процесс панорамирования

    def create_scrollable_frame(self):
        """Создание области с прокруткой для параметров."""
        if self.scrollable_frame:
            self.scrollable_frame.destroy()

        # Canvas для параметров и Scrollbar
        self.canvas_frame = tk.Canvas(self.root, borderwidth=0, highlightthickness=0)
        self.scrollable_frame = ttk.Frame(self.canvas_frame)
        self.canvas_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas_frame.yview)

        self.canvas_frame.configure(yscrollcommand=self.canvas_scrollbar.set)
        self.canvas_frame.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Размещение: Canvas и Scrollbar вплотную
        self.canvas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(5, 0), pady=5)  # TODO понять что за падинги
        self.canvas_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 0))  # TODO понять что за падинги

        # Привязка событий прокрутки
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas_frame.configure(scrollregion=self.canvas_frame.bbox("all"))
        )
        self.canvas_frame.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        """Обработка прокрутки мышью."""
        self.canvas_frame.yview_scroll(-1 * (event.delta // 120), "units")

    def create_plot_area(self):
        """Создание области для отображения графика."""
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=1, column=3, rowspan=4, padx=10, pady=5)

        ax = fig.add_subplot(111)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Добавляем курсор для приближения/отдаления
        self.cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

        return fig, canvas

    def choose_parsing_file(self):
        """Выбор файла параметров."""
        parsing_file = filedialog.askopenfilename(
            title="Выберите файл параметров",
            filetypes=(("INC and VA files", "*.inc *.va"), ("All files", "*.*"))
        )
        if parsing_file:
            self.parsing_file.set(parsing_file)  # Сохраняем полный путь
            try:
                self.update_parameters(parsing_file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке файла параметров: {e}")

    def update_parameters(self, parsing_file):
        """Обновление параметров на основе выбранного файла."""
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=parsing_file, ignore_params_loader=ignore_params_loader)
            parameters = parser.parse()

            # Если параметров > 15, создаем область прокрутки
            if len(parameters) > 15:
                self.create_scrollable_frame()
                parent_frame = self.scrollable_frame
            else:
                parent_frame = self.root

            # Очищаем текущие параметры
            for widget in parent_frame.winfo_children():
                widget.destroy()

            self.parameter_entries = []  # Очистка списка параметров

            # Добавляем новые параметры
            for i, param in enumerate(parameters):
                tk.Label(parent_frame, text=param["name"]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
                entry = tk.Entry(parent_frame)
                entry.insert(0, str(param["default_value"]))
                entry.grid(row=i, column=1, padx=5, pady=2)

                # Сохраняем ссылку на имя и поле ввода
                self.parameter_entries.append({"name": param["name"], "entry": entry})

            self.simulation_runner = SimulationRunner(parsing_file)

        except Exception as e:
            raise RuntimeError(f"Ошибка парсинга параметров: {e}")

    def apply_changes(self):
        """Применяет изменения к выбранному файлу."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Модель не выбрана.")
            return

        # Сбор текущих параметров из GUI
        current_parameters = {}
        for param in self.parameter_entries:
            param_name = param["name"]
            param_value = param["entry"].get()
            current_parameters[param_name] = param_value

        # Получаем полный путь к выбранному файлу
        target_file = self.parsing_file.get()

        try:
            self.file_manager.apply_changes_to_file(current_parameters, target_file)
            messagebox.showinfo("Успех", f"Изменения успешно применены в {target_file}.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить изменения: {e}")
    
    def choose_model(self):
        """Выбор конкретной .va модели для использования."""
        if not self.simulation_runner or not self.simulation_runner.model_path:
            messagebox.showerror("Ошибка", "Сначала выберите файл параметров.")
            return

        model_file = filedialog.askopenfilename(
            initialdir=self.simulation_runner.model_path,  # TODO сделать улучшения по поиску файлов в папке
            title="Выберите модель (.va)",
            filetypes=(("VA Model files", "*.va"), ("All files", "*.*"))
        )

        if model_file:
            self.simulation_runner.set_model(model_file)
            messagebox.showinfo("Модель выбрана", f"Модель: {os.path.basename(model_file)}")
        else:
            messagebox.showerror("Ошибка", "Выбор модели отменён.")

    def choose_spice_file(self):
        """Выбор SPICE-файла."""
        spice_file = filedialog.askopenfilename(
            title="Выберите SPICE-файл",
            filetypes=(("SPICE files", "*.sp *.cir"), ("All files", "*.*"))
        )
        if spice_file:
            self.spice_file = spice_file
            messagebox.showinfo("Файл выбран", f"Выбранный файл: {spice_file}")

    def start_simulation(self):
        """Запуск симуляции."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Сначала выберите файл параметров.")
            return
        if not self.spice_file:
            messagebox.showerror("Ошибка", "Сначала выберите SPICE-файл.")
            return

        try:
            self.simulation_runner.run_simulation(
                spice_file=self.spice_file,
                canvas=self.canvas_plot,
                fig=self.fig
            )
            messagebox.showinfo("Успех", "Симуляция завершена успешно.")
        except Exception as e:
            messagebox.showerror("Ошибка симуляции", f"Ошибка симуляции: {e}")

    def create_parameter_entries(self, parameters):
        """Создаёт поля ввода для параметров."""
        if self.parameter_entries:
            for param in self.parameter_entries:
                param["entry"].destroy()  # Удаляем старые поля ввода
            self.parameter_entries.clear()

        for i, param in enumerate(parameters):
            # Имя параметра
            tk.Label(self.scrollable_frame, text=param["name"]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Поле ввода
            entry = tk.Entry(self.scrollable_frame)
            entry.insert(0, str(param["default_value"]))  # Заполняем значением по умолчанию
            entry.grid(row=i, column=1, padx=5, pady=2)

            # Сохраняем ссылки на имя и поле ввода
            self.parameter_entries.append({"name": param["name"], "entry": entry})

    def update_plot_scale(self):
        """Обновление масштаба графика."""
        if self.fig:
            ax = self.fig.axes[0]
            ax.set_yscale("log" if self.log_scale.get() else "linear")
            self.canvas_plot.draw()

    def update_plot_limits(self, event=None):
        """Обновление пределов графика."""
        if self.fig:
            ax = self.fig.axes[0]
            
            x_max = self.x_max_slider.get()
            y_max = self.y_max_slider.get()

            if x_max == 0:
                x_max = 0.1

            if y_max == 0:
                y_max = 0.1

            ax.set_xlim(right=x_max)
            ax.set_ylim(top=y_max)

            self.canvas_plot.draw()
        else:
            print("Параметр 'fig' не должен быть None")


if __name__ == "__main__":
    root = tk.Tk()
    app = NGSPICESimulatorApp(root)
    root.mainloop()

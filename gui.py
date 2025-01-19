import os
from datetime import datetime
import time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from matplotlib.patches import Rectangle
from core.simulation_runner import SimulationRunner
from utils.parameter_parser import ParameterParser, FileIgnoreParamsLoader
from core.file_manager import FileManager
from matplotlib.backend_bases import MouseEvent
from config import DIRECTORY, IGNORE_PARAMS_FILE, PICS_PATH, MODEL_CODE_PATH, SPICE_EXAMPLES_PATH


class NGSPICESimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NGSPICE Симулятор")
        self.root.geometry("1360x640")
        self.root.resizable(False, False)

        self.parsing_file = tk.StringVar(value="Не выбран")
        self.simulation_runner = None
        self.file_manager = FileManager()
        self.parameter_entries = []

        self.spice_file = None

        self.scrollable_frame = None
        self.canvas_frame = None
        self.canvas_scrollbar = None
        self.create_interface()

        """Область отвечающая за обработку zoom на графике"""
        self.canvas_plot.mpl_connect('scroll_event', self.on_scroll)

        """Область отвечающая за обработку действий на графике"""
        self.start_point = None
        self.selection_rect = None
        self.canvas_plot.mpl_connect('button_press_event', self.on_press)
        self.canvas_plot.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas_plot.mpl_connect('button_release_event', self.on_release)

        self.__setup_directroies()

    def __setup_directroies(self):
        for directory in DIRECTORY:
            if not os.path.exists(directory):
                os.makedirs(directory)

    # def reset_plot_scale(self):
    #     """Сброс масштаба графика на исходное значение."""
    #     if self.original_xlim is None or self.original_ylim is None:
    #         ax = self.fig.axes[0]
    #         self.original_xlim = ax.get_xlim()
    #         self.original_ylim = ax.get_ylim()

    #     ax = self.fig.axes[0]
    #     ax.set_xlim(self.original_xlim)
    #     ax.set_ylim(self.original_ylim)

    #     # Обновляем слайдеры
    #     self.update_sliders_from_plot()
    #     self.canvas_plot.draw()

    def on_scroll(self, event):
        """Handle mouse scroll events to zoom in or out on the plot."""
        if not self.fig or not self.fig.axes:
            return

        ax = self.fig.axes[0]
        x_lim, y_lim = ax.get_xlim(), ax.get_ylim()

        ZOOM_IN_FACTOR, ZOOM_OUT_FACTOR = 0.5, 2
        zoom_factor = ZOOM_IN_FACTOR if event.button == 'up' else ZOOM_OUT_FACTOR

        x_center = event.xdata if event.xdata is not None else (x_lim[0] + x_lim[1]) / 2
        y_center = event.ydata if event.ydata is not None else (y_lim[0] + y_lim[1]) / 2

        x_range = (x_lim[1] - x_lim[0]) * zoom_factor
        y_range = (y_lim[1] - y_lim[0]) * zoom_factor

        new_x_min, new_x_max = x_center - x_range / 2, x_center + x_range / 2
        new_y_min, new_y_max = y_center - y_range / 2, y_center + y_range / 2

        ax.set_xlim([new_x_min, new_x_max])
        ax.set_ylim([new_y_min, new_y_max])

        self.canvas_plot.draw()

    def on_press(self, event: MouseEvent):
        """Начало выделения области на графике."""
        if event.inaxes:
            self.start_point = (event.xdata, event.ydata)

            if self.selection_rect is None:
                self.selection_rect = Rectangle(
                    (event.xdata, event.ydata), 0, 0,
                    edgecolor="red", facecolor="none", linewidth=1.5
                )
                event.inaxes.add_patch(self.selection_rect)

    def on_motion(self, event: MouseEvent):
        """Обновление прямоугольника выделения."""
        if not self.start_point or not event.inaxes:
            return
        
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata

        self.selection_rect.set_width(x1 - x0)
        self.selection_rect.set_height(y1 - y0)
        self.selection_rect.set_xy((x0, y0))
        self.canvas_plot.draw()

    def on_release(self, event: MouseEvent):
        """При отпускании мыши область приближается."""
        if not self.start_point or not event.inaxes:
            return
        
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata

        if x0 != x1 and y0 != y1:
            ax = event.inaxes
            ax.set_xlim(min(x0, x1), max(x0, x1))
            ax.set_ylim(min(y0, y1), max(y0, y1))
            self.canvas_plot.draw()
        
        self.start_point = None
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

    def create_interface(self):
        """Sets up the GUI interface for the NGSPICESimulatorApp."""
        tk.Label(self.root, text="Файл:").grid(row=0, column=0, sticky="ew")
        tk.Label(self.root, textvariable=self.parsing_file).grid(row=0, column=1, sticky="w")
        tk.Button(self.root, text="Выбрать файл", command=self.choose_parsing_file).grid(row=0, column=2, sticky="s")

        self.create_scrollable_frame()

        button_config = [
            ("Выбрать модель", self.choose_model, 2),
            ("Применить изменения", self.apply_changes, 3),
            ("Выбрать SPICE-файл", self.choose_spice_file, 4),
            ("Запустить симуляцию", self.start_simulation, 5)
        ]
        for text, command, row in button_config:
            tk.Button(self.root, text=text, command=command).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")

        self.log_scale = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Log Scale", variable=self.log_scale, command=self.update_plot_scale).grid(
            row=0, column=3, sticky="w"
        )

        self.fig, self.canvas_plot = self.create_plot_area()
        tk.Button(self.root, text="Сохранить график", command=self.save_plot).grid(row=7, column=3, sticky="ew")

        # self.create_sliders()

    def create_scrollable_frame(self):
        """Создание области с прокруткой для параметров."""
        if self.scrollable_frame:
            self.scrollable_frame.destroy()

        self.canvas_frame = tk.Canvas(self.root, borderwidth=0, highlightthickness=0)
        self.scrollable_frame = ttk.Frame(self.canvas_frame)
        self.canvas_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas_frame.yview)

        self.canvas_frame.configure(yscrollcommand=self.canvas_scrollbar.set)
        self.canvas_frame.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(5, 0), pady=5)
        self.canvas_scrollbar.grid(row=1, column=1, sticky="ns")

        # Привязка событий прокрутки
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas_frame.configure(scrollregion=self.canvas_frame.bbox("all"))
        )
        self.canvas_frame.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        """Обработка прокрутки мышью."""
        self.canvas_frame.yview_scroll(-1 * (event.delta // 120), "units")

    def create_plot_area(self):
        """Initialize a plotting area within the Tkinter application."""
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=4, padx=10, pady=5)

        ax = fig.add_subplot(111)
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        self.original_xlim = ax.get_xlim()
        self.original_ylim = ax.get_ylim()

        self.cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

        return fig, canvas

    def choose_parsing_file(self):
        """Выбор файла параметров."""
        try:
            parsing_file = filedialog.askopenfilename(
                title="Выберите файл параметров",
                initialdir=MODEL_CODE_PATH,
                filetypes=(("INC and VA files", "parameters.inc *.va"), ("All files", "*.*"))
            )
            if parsing_file:
                self.parsing_file.set(parsing_file)  # Сохраняем полный путь
                # print(f"parsing file path: {parsing_file}")
                self.update_parameters(parsing_file)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке файла параметров: {e}")

    def choose_model(self):
        """Выбор конкретной .va модели для использования."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Сначала выберите файл параметров.")
            return

        model_file = filedialog.askopenfilename(
            initialfile=self.parsing_file,
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
        try:
            parsing_file_path = self.parsing_file.get()
            parent_dir_name = os.path.basename(os.path.dirname(os.path.dirname(parsing_file_path)))
            initial_dir = os.path.join(SPICE_EXAMPLES_PATH, parent_dir_name)
        
            spice_file = filedialog.askopenfilename(
                title="Выберите SPICE-файл",
                initialdir=initial_dir,
                filetypes=(("SPICE files", "*.sp *.cir"), ("All files", "*.*"))
            )
        
            if spice_file:
                self.spice_file = spice_file
                messagebox.showinfo("Файл выбран", f"Выбранный файл: {spice_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выборе SPICE-файла: {e}")

    def update_parameters(self, parsing_file):
        """Обновление параметров на основе выбранного файла."""
        try:
            ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
            parser = ParameterParser(file_path=parsing_file, ignore_params_loader=ignore_params_loader)
            parameters = parser.parse()

            if len(parameters) > 15:
                self.create_scrollable_frame()
                parent_frame = self.scrollable_frame
            else:
                parent_frame = self.root

            for widget in parent_frame.winfo_children():
                widget.destroy()

            self.parameter_entries = []

            for i, param in enumerate(parameters):
                tk.Label(parent_frame, text=param["name"]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
                entry = tk.Entry(parent_frame)
                entry.insert(0, str(param["default_value"]))
                entry.grid(row=i, column=1, padx=5, pady=2)

                self.parameter_entries.append({"name": param["name"], "entry": entry})

            self.simulation_runner = SimulationRunner(parsing_file)

        except Exception as e:
            raise RuntimeError(f"Ошибка парсинга параметров: {e}")

    def apply_changes(self):
        """Применяет изменения к выбранному файлу."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Модель не выбрана.")
            return

        current_parameters = {}
        for param in self.parameter_entries:
            param_name = param["name"]
            param_value = param["entry"].get()
            current_parameters[param_name] = param_value

        target_file = self.parsing_file.get()

        try:
            self.file_manager.apply_changes_to_file(current_parameters, target_file)
            messagebox.showinfo("Успех", f"Изменения успешно применены в {target_file}.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить изменения: {e}")

    def start_simulation(self):
        """Запуск симуляции."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Сначала выберите файл параметров.")
            return
        if not self.spice_file:
            messagebox.showerror("Ошибка", "Сначала выберите SPICE-файл.")
            return

        if self.fig:  # clean canvas/fig
            self.fig.clear()
            self.canvas_plot.draw()
        


        try:
            self.simulation_runner.run_simulation(
                spice_file=self.spice_file,
                canvas=self.canvas_plot,
                fig=self.fig,
            )
            messagebox.showinfo("Успех", "Симуляция завершена успешно.")
        except RuntimeError as warning:
            messagebox.showwarning(f"Предупреждение", f"{warning}")
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
        if not self.fig:
            return
        
        ax = self.fig.axes[0]
        y_scale = "log" if self.log_scale.get() else "linear"
        ax.set_yscale(y_scale)
        self.canvas_plot.draw()

    def update_plot_limits(self, event=None):
        """Обновление пределов графика."""
        if self.fig and self.fig.axes:
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
    
    def save_plot(self):
        """Сохранение графика в папку. Название, содержит дату и время."""
        os.makedirs(PICS_PATH, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(PICS_PATH, f'plot_{current_time}.png')
        self.fig.savefig(file_path)
        messagebox.showinfo("Сохранение графика", f"График сохранён в {file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NGSPICESimulatorApp(root)
    root.mainloop()

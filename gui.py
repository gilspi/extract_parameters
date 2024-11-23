import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from simulation_runner import SimulationRunner
from parameter_parser import ParameterParser
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
        self.parameter_entries = {}

        # Создание интерфейса
        self.create_interface()

    def create_interface(self):
        """Создание интерфейса пользователя."""
        # Выбор файла для парсинга параметров
        tk.Label(self.root, text=f"Файл:").grid(row=0, column=0, sticky="w")
        tk.Label(self.root, textvariable=self.parsing_file).grid(row=0, column=1, sticky="w")
        tk.Button(self.root, text="Выбрать файл", command=self.choose_parsing_file).grid(row=0, column=2, sticky="w")

        # Создаем область параметров
        self.scrollable_frame = None
        self.canvas_frame = None
        self.canvas_scrollbar = None
        self.create_scrollable_frame()

        # Кнопки управления
        tk.Button(self.root, text="Применить изменения", command=self.apply_changes).grid(
            row=2, column=0, columnspan=2, pady=5, sticky="ew"
        )
        tk.Button(self.root, text="Выбрать SPICE-файл", command=self.choose_spice_file).grid(
            row=3, column=0, columnspan=2, pady=5, sticky="ew"
        )
        tk.Button(self.root, text="Запустить симуляцию", command=self.start_simulation).grid(
            row=4, column=0, columnspan=2, pady=5, sticky="ew"
        )

        # Поле для графика
        self.fig, self.canvas_plot = self.create_plot_area()

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
        self.canvas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(5, 0), pady=5)
        self.canvas_scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 0))

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
        fig = plt.Figure(figsize=(6, 4), dpi=100)  # TODO: изменить размер окна графика
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=4, padx=10, pady=5)
        return fig, canvas

    def choose_parsing_file(self):
        """Выбор файла параметров."""
        parsing_file = filedialog.askopenfilename(
            title="Выберите файл параметров",
            filetypes=(("INC and VA files", "*.inc *.va"), ("All files", "*.*"))
        )
        if parsing_file:
            self.parsing_file.set(os.path.basename(parsing_file))
            try:
                self.update_parameters(parsing_file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обработке файла параметров: {e}")

    def update_parameters(self, parsing_file):
        """Обновление параметров на основе выбранного файла."""
        try:
            parser = ParameterParser(parsing_file, IGNORE_PARAMS_FILE)
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

            self.parameter_entries = {}

            # Добавляем новые параметры
            for i, param in enumerate(parameters):
                tk.Label(parent_frame, text=param["name"]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
                entry = tk.Entry(parent_frame)
                entry.insert(0, str(param["default_value"]))
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.parameter_entries[param["name"]] = entry

            # Устанавливаем SimulationRunner
            model_path = os.path.dirname(parsing_file)
            vamodel_name = os.path.basename(parsing_file)
            self.simulation_runner = SimulationRunner(model_path, vamodel_name)

        except Exception as e:
            raise RuntimeError(f"Ошибка парсинга параметров: {e}")

    def apply_changes(self):
        """Применение изменений к выбранному файлу параметров."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Сначала выберите файл параметров.")
            return

        # Собираем параметры
        parameters = {}
        for name, entry in self.parameter_entries.items():
            parameters[name] = entry.get()

        try:
            self.simulation_runner.apply_changes_to_file(parameters)
            messagebox.showinfo("Успех", "Изменения успешно применены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка применения изменений: {e}")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = NGSPICESimulatorApp(root)
    root.mainloop()

import os
# установленные библиотеки
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# пользовательские библиотеки
from simulation_runner import SimulationRunner


class NGSPICESimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NGSPICE Симулятор")

        # Переменные для модели и SPICE-файла
        self.current_model = tk.StringVar(value="Не выбрана")
        self.spice_file = None
        self.model_path = None  # Путь к модели

        # Инициализация SimulationRunner
        self.simulation_runner = None  # Инициализируем позже при выборе модели

        # Создание интерфейса
        self.create_interface()

    def create_interface(self):
        """Создание интерфейса пользователя."""
        # Поле выбора модели
        tk.Label(self.root, text="Текущая модель:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self.root, textvariable=self.current_model).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Button(self.root, text="Выбрать модель", command=self.choose_model).grid(row=0, column=2, padx=5, pady=5)

        # Параметры симуляции
        tk.Label(self.root, text="is:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_is = tk.Entry(self.root)
        self.entry_is.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="nff:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_nff = tk.Entry(self.root)
        self.entry_nff.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.root, text="nfr:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_nfr = tk.Entry(self.root)
        self.entry_nfr.grid(row=3, column=1, padx=5, pady=5)

        # Кнопки управления
        tk.Button(self.root, text="Выбрать SPICE-файл", command=self.choose_spice_file).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(self.root, text="Запустить симуляцию", command=self.start_simulation).grid(row=5, column=0, columnspan=2, pady=5)

        # Поле для графика
        self.fig, self.canvas = self.create_plot_area()

    def create_plot_area(self):
        """Создание области для отображения графика."""
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=0, column=3, rowspan=6, padx=10, pady=5)
        return fig, canvas

    def choose_model(self):
        """Выбор модели (ищет .va в папке vacode)."""
        model_dir = filedialog.askdirectory(
            initialdir="./code", title="Выберите папку с моделью"
        )
        if model_dir:
            model_name = os.path.basename(model_dir)  # Имя модели = название папки
            vacode_dir = os.path.join(model_dir, "vacode")  # Папка vacode внутри модели
            parameters_file = os.path.join(vacode_dir, "parameters.inc")
            va_files = [f for f in os.listdir(vacode_dir) if f.endswith('.va')] if os.path.exists(vacode_dir) else []

            if not va_files and not os.path.exists(parameters_file):
                messagebox.showerror("Ошибка", f"В папке '{model_name}/vacode' нет ни файлов .va, ни parameters.inc")
                return

            if os.path.exists(parameters_file):
                selected_file = parameters_file
            elif len(va_files) == 1:
                selected_file = os.path.join(vacode_dir, va_files[0])  # Единственный файл .va
            else:
                selected_file = filedialog.askopenfilename(
                    initialdir=vacode_dir, title="Выберите VA-модель",
                    filetypes=(("VA Model files", "*.va"), ("All files", "*.*"))
                )

            if selected_file:
                self.current_model.set(model_name)
                self.model_path = vacode_dir
                try:
                    # Инициализируем SimulationRunner с выбранной моделью
                    self.simulation_runner = SimulationRunner(
                        model_path=self.model_path,
                        vamodel_name=os.path.basename(selected_file)
                    )
                    messagebox.showinfo("Успех", f"Модель '{model_name}' выбрана: {selected_file}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось установить модель: {e}")

    def choose_spice_file(self):
        """Выбор SPICE-файла."""
        spice_file = filedialog.askopenfilename(
            initialdir="./examples", title="Выберите SPICE-файл",
            filetypes=(("SPICE files", "*.sp *.cir"), ("All files", "*.*"))
        )
        if spice_file:
            self.spice_file = spice_file
            messagebox.showinfo("Файл выбран", f"Выбранный файл: {spice_file}")

    def start_simulation(self):
        """Запуск симуляции."""
        if not self.simulation_runner:
            messagebox.showerror("Ошибка", "Сначала выберите модель.")
            return
        if not self.spice_file:
            messagebox.showerror("Ошибка", "Сначала выберите SPICE-файл.")
            return

        # Получаем параметры
        is_value = self.entry_is.get() or "1.0e-15"
        nff_value = self.entry_nff.get() or "1.0"
        nfr_value = self.entry_nfr.get() or "1.0"

        try:
            self.simulation_runner.run_simulation(
                spice_file=self.spice_file,
                is_value=is_value,
                nff_value=nff_value,
                nfr_value=nfr_value,
                canvas=self.canvas,
                fig=self.fig
            )
            messagebox.showinfo("Успех", "Симуляция завершена успешно.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка симуляции: {e}")


if __name__ == "__main__":
    import os
    root = tk.Tk()
    app = NGSPICESimulatorApp(root)
    root.mainloop()
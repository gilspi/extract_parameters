"""
TODO: модуль не работает с разными моделями, потому в некоторых моделях при записи в simulation_data.txt
почему-то выскакивают непонятные предупреждения
"""

import subprocess
import config
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Optional
import re


class SimulationRunner:
    def __init__(self, config_file, output_file="simulation_data.txt", column_names=None):
        """
        Initializes the SimulationRunner with a config file for SPICE and an output file for data.
        
        Args:
            config_file (str): Path to the SPICE simulation file.
            output_file (str): Path where simulation data will be saved.
            column_names (list): List of expected column names in the output data file.
        """
        self.config_file = config_file
        self.output_file = output_file
        self.column_names = column_names or ["Index", "v_sweep", "i_vc", "i_vb", "i_vs"]
        self.data = None

    def run_simulation(self):
        """Runs the SPICE simulation and outputs data to the specified file."""
        try:
            command = ["ngspice", "-b", self.config_file, "-o", self.output_file]
            subprocess.run(command, check=True)
            print(f"Simulation completed successfully. Output saved to {self.output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error running simulation: {e}")

    def load_data(self, skiprows=5, delimiter='\s+'):
        """Loads simulation data from the output file."""
        try:
            self.data = pd.read_csv(
                self.output_file, sep=delimiter, skiprows=skiprows, 
                names=self.column_names, comment="I"
            )
            for column in self.column_names[1:]:  # Ensure all columns are numeric except Index
                self.data[column] = pd.to_numeric(self.data[column], errors='coerce')
            self.data.dropna(inplace=True)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def filter_data(self, v_min=None, v_max=None):
        """Applies filtering to restrict the voltage range and positive currents only if columns are available."""
        if self.data is not None:
            if v_min is not None and "v_sweep" in self.data.columns:
                self.data = self.data[(self.data["v_sweep"] >= v_min)]
            if v_max is not None and "v_sweep" in self.data.columns:
                self.data = self.data[(self.data["v_sweep"] <= v_max)]
            if "i_vc" in self.data.columns:
                self.data = self.data[self.data["i_vc"] > 0]
            if "i_vb" in self.data.columns:
                self.data = self.data[self.data["i_vb"] > 0]
            if "i_vs" in self.data.columns:
                self.data = self.data[self.data["i_vs"] > 0]
            print("Data filtered successfully.")

    def plot_data(self, title="SPICE Simulation Results", y_min=1e-12, y_max=1):
        """Plots the data with specified y-axis limits and log scale."""
        if self.data is not None:
            plt.figure(figsize=(10, 6))
            # Check for columns and plot accordingly
            if "v_sweep" in self.data.columns and "i_vc" in self.data.columns:
                plt.plot(self.data["v_sweep"], self.data["i_vc"], label="abs(i(vc))", color='red')
            if "v_sweep" in self.data.columns and "i_vb" in self.data.columns:
                plt.plot(self.data["v_sweep"], self.data["i_vb"], label="abs(i(vb))", color='blue')
            if "v_sweep" in self.data.columns and "i_vs" in self.data.columns:
                plt.plot(self.data["v_sweep"], self.data["i_vs"], label="abs(i(vs))", color='orange')
            if "v_dt" in self.data.columns and "i_vc" in self.data.columns:
                plt.plot(self.data["v_dt"], self.data["i_vc"], label="abs(i(vc))", color='green')
            
            plt.ylim(y_min, y_max)
            plt.yscale("log")
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current (A)")
            plt.title(title)
            plt.legend()
            plt.grid(True, which="both", linestyle="--", linewidth=0.5)
            plt.show()
        else:
            print("No data to plot.")

# Example usage:
# Specify the config file and columns based on your SPICE simulation
# runner = SimulationRunner(
#     config_file=config.EXAMPLES_PATH + "npn_ic_vc_ib.sp", 
#     column_names=["Index", "v_dt", "i_vc"]
# )
# runner.run_simulation()
# runner.load_data()
# runner.filter_data(v_min=0, v_max=5)
# runner.plot_data(title="SPICE Simulation")


def plot_simulation_data(canvas, fig, filename="simulation_data.txt"):
    """Загружает данные из файла и отображает график на canvas."""
    try:
        print(f"Чтение файла: {filename}")
        with open(filename, 'r') as f:
            lines = f.readlines()
            print(f"Строки из файла: {len(lines)}")

            # Попытка найти строку заголовка
            header_line_index = None
            for i, line in enumerate(lines):
                if 'Index' in line and 'v-sweep' in line:
                    header_line_index = i
                    break

            if header_line_index is None:
                raise ValueError("Не удалось найти строку заголовка в файле")

            header_line = lines[header_line_index].strip()
            print(f"Заголовок: {header_line}")
            column_names = re.split(r'\s+', header_line)
            print(f"Имена колонок: {column_names}")

            # Загрузка данных из файла симуляции
            data = pd.read_csv(filename, sep='\s+', comment='I', skiprows=header_line_index + 1, names=column_names)
            print(f"Данные загружены: {data.head()}")

            # Преобразование колонок в числовой формат и удаление некорректных данных
            for column in column_names[1:]:
                data[column] = pd.to_numeric(data[column], errors='coerce')
            print(f"Данные после преобразования: {data.head()}")

            # Фильтрация данных
            data = data.dropna()
            print(f"Данные после фильтрации: {data.head()}")

            # Проверка, что fig не None
            if fig is None:
                raise ValueError("Параметр 'fig' не должен быть None")

            # Построение графика
            print("Построение графика")
            fig.clear()
            ax = fig.add_subplot(111)

            for column in column_names[2:]:
                ax.plot(data[column_names[1]], data[column], label=column)

            # Настройки графика
            ax.set_yscale("log")
            ax.set_xlabel(column_names[1])
            ax.set_ylabel("Current (A)")
            ax.set_title("Current vs. Voltage Sweep")
            ax.legend()
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)

            # Обновление canvas
            if canvas:
                canvas.draw()
            else:
                print("Параметр 'canvas' равен None, пропуск обновления")

    except Exception as e:
        print(f"Ошибка построения графика: {e}")

if __name__ == "__main__":
    # Для отладки лучше использовать реальные объекты canvas и fig, например:
    fig = plt.figure()
    plot_simulation_data(None, fig)  # Используем 'fig' для отладки
    plt.show()  # Показываем график для проверки

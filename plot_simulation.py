"""
TODO: модуль не работает с разными моделями, потому в некоторых моделях при записи в simulation_data.txt
почему-то выскакивают непонятные предупреждения
"""

import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import config


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
        # Загрузка данных из файла симуляции
        data = pd.read_csv(filename, sep='\s+', comment='I', skiprows=5, 
                           names=["Index", "v_sweep", "i_vc", "i_vb", "i_vs"])
        
        # Преобразование колонок в числовой формат и удаление некорректных данных
        data["v_sweep"] = pd.to_numeric(data["v_sweep"], errors='coerce')
        data["i_vc"] = pd.to_numeric(data["i_vc"], errors='coerce')
        data["i_vb"] = pd.to_numeric(data["i_vb"], errors='coerce')
        data["i_vs"] = pd.to_numeric(data["i_vs"], errors='coerce')
        
        # Фильтрация данных
        data = data.dropna()
        data = data[(data["i_vc"] > 0) & (data["i_vb"] > 0) & (data["i_vs"] > 0)]
        data = data[(data["v_sweep"] >= 0.2) & (data["v_sweep"] <= 1.4)]

        # Построение графика
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(data["v_sweep"], data["i_vb"], label="abs(i(vb))", color='blue')
        ax.plot(data["v_sweep"], data["i_vs"], label="abs(i(vs))", color='orange')
        ax.plot(data["v_sweep"], data["i_vc"], label="abs(i(vc))", color='red')
        
        # Настройки графика
        ax.set_yscale("log")
        ax.set_ylim(1e-12, 1)
        ax.set_xlim(0.2, 1.4)
        ax.set_xlabel("v-sweep (V)")
        ax.set_ylabel("Current (A)")
        ax.set_title("Current vs. Voltage Sweep")
        ax.legend()
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Обновление canvas
        canvas.draw()
    except Exception as e:
        # messagebox.showerror("Ошибка построения графика", f"Не удалось построить график: {e}")
        print(f"Ошибка построения графика: {e}")

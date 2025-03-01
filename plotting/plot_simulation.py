import pandas as pd
import numpy as np
from typing import List, Optional, Protocol
import re


class DataLoader(Protocol):
    def load_data(self, filename: str) -> pd.DataFrame:
        pass


class DataPlotter(Protocol):
    def plot(self, data: pd.DataFrame, fig, canvas=None):
        pass


class Loader(DataLoader):
    def load_data(self, filename: str) -> pd.DataFrame:
        with open(filename, 'r') as f:
            lines = f.readlines()

            header_line_index = None  # ищем строку заголовка
            for i, line in enumerate(lines):
                if ('Index' in line and 'v-sweep' in line) or ('Index' in line and 'time' in line):  # FIXME переделать условие
                    header_line_index = i
                    break

            if header_line_index is None:
                raise ValueError("Не удалось найти строку заголовка в файле")

            header_line = lines[header_line_index].strip()
            column_names = re.split(r'\s+', header_line)

            data = pd.read_csv(filename, sep='\s+', comment='I', skiprows=header_line_index + 1, names=column_names) # загрузка данных из файла симуляции

            for column in column_names[1:]:  # преобразование колонок в числовой формат и удаление некорректных данных
                data[column] = pd.to_numeric(data[column], errors='coerce')
    
        return data.dropna()


class Plotter(DataPlotter):
    def plot(self, data: pd.DataFrame, ax, label: str, color: str, linestyle: str):
        column_names = data.columns

        for column in column_names[2:]:
            x = data[column_names[1]]
            y = data[column]
            
            mask = np.where(x.values[:-1] > x.values[1:], True, False)
            x_segmented = np.insert(x.values, np.where(mask)[0] + 1, np.nan)
            y_segmented = np.insert(y.values, np.where(mask)[0] + 1, np.nan)

            ax.plot(x_segmented, y_segmented, label=label, color=color, linestyle=linestyle)
        
        ax.legend()
        ax.grid(True)
        ax.relim()
        ax.autoscale()


class SimulationManager:
    def __init__(self):
        self.data_loader = Loader()
        self.data_plotter = Plotter()

    def run(self, fig, canvas, user_filename: str, reference_filename: str):
        """
        Отображает два графика: эталонный и пользовательский.
        """
        try:
            ax = fig.gca()
            ax.clear()
            reference_data = self.data_loader.load_data(reference_filename)
            user_data = self.data_loader.load_data(user_filename)

            self.data_plotter.plot(reference_data, ax, label="Эталонный график", color="blue", linestyle="--")
            self.data_plotter.plot(user_data, ax, label="Пользовательский график", color="red", linestyle="-")

            fig.tight_layout()
            canvas.draw_idle()
        except Exception as e:
            print(f"Ошибка построения графика: {e}")

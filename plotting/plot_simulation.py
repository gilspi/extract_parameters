import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Optional, Protocol
import re
from config import SIMULATION_RAW_DATA_PATH


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
            print(f"Строки из файла: {len(lines)}")

            header_line_index = None  # ищем строку заголовка
            for i, line in enumerate(lines):
                if ('Index' in line and 'v-sweep' in line) or ('Index' in line and 'time' in line):  # FIXME переделать условие
                    header_line_index = i
                    break

            if header_line_index is None:
                raise ValueError("Не удалось найти строку заголовка в файле")

            header_line = lines[header_line_index].strip()
            print(f"Заголовок: {header_line}")
            column_names = re.split(r'\s+', header_line)
            print(f"Имена колонок: {column_names}")

            data = pd.read_csv(filename, sep='\s+', comment='I', skiprows=header_line_index + 1, names=column_names) # загрузка данных из файла симуляции
            print(f"Данные загружены: {data.head()}")

            for column in column_names[1:]:  # преобразование колонок в числовой формат и удаление некорректных данных
                data[column] = pd.to_numeric(data[column], errors='coerce')
            print(f"Данные после преобразования: {data.head()}")
    
        return data.dropna()


class Plotter(DataPlotter):
    def plot(self, data: pd.DataFrame, fig, canvas=None):
        fig.clear()
        ax = fig.add_subplot(111)

        column_names = data.columns
        for column in column_names[2:]:
            ax.plot(data[column_names[1]], data[column], label=column)

        ax.set_xlabel(column_names[1])
        ax.set_ylabel("Current (A)")
        ax.set_title("Current vs. Voltage Sweep")  # TODO сделать динамическое изменение название
        ax.legend()
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)  # TODO сделать выбор цвета динамически

        ax.set_yscale("log")

        if canvas:
            canvas.draw()
        else:
            print("Параметр 'canvas' равен None, пропуск обновления")


class SimulationManager:
    def __init__(self):
        self.data_loader = Loader()
        self.data_plotter = Plotter()

    def run(self, fig, canvas=None, filename="simulation_data.txt"):
        """
        TODO: добавить динамическое название для файла из GUI
        """
        try:
            print(f"Чтение файла: {filename}")
            data = self.data_loader.load_data(f"{SIMULATION_RAW_DATA_PATH}{filename}")
            print(f"Данные загружены: {data.head()}")

            print("Построение графика")
            if fig is None:
                raise ValueError("Параметр 'fig' не должен быть None")
            
            self.data_plotter.plot(data, fig, canvas)
        except Exception as e:
            print(f"Ошибка построения графика: {e}")


if __name__ == "__main__":
    fig = plt.figure()
    manager = SimulationManager()
    manager.run(fig)
    plt.show()

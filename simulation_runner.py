import os
import subprocess

# пользовательские библиотеки
from utils import find_file, modify_parameters
from plot_simulation import plot_simulation_data
from parameter_parser import ParameterParser
from config import PARAMETERS_FILE, VAMODEL_PATH, OSDILIBS_PATH


class SimulationRunner:
    def __init__(self, model_path, vamodel_name):
        """
        Инициализация симулятора.

        Args:
            model_path (str): Путь к папке модели (например, code/mextram/vacode).
        """
        self.model_path = model_path
        self.vamodel_name = vamodel_name
        self.parameters_file = os.path.join(model_path, "parameters.inc")

    def rebuild_osdi(self):
        """Пересборка osdi-модели."""
        va_files = [f for f in os.listdir(self.model_path) if f.endswith(".va")]
        if not va_files:
            raise FileNotFoundError("Файлы .va в указанной папке не найдены.")
        subprocess.run(["./openvaf", va_files[0]], cwd=self.model_path)

    def move_osdi_file(self, osdi_model):
        """Перемещение osdi-файла."""
        source_path = find_file(osdi_model, search_path=self.model_path)
        dst = os.path.join(self.model_path, "..", "osdilibs", osdi_model)
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(source_path, dst)

    def parse_parameters(self):
        """Парсинг параметров модели."""
        parser = ParameterParser(self.model_path)
        parameters = parser.parse()
        return parameters

    def run_simulation(self, spice_file, canvas, fig):
        """
        Запуск симуляции. 

        Параметры:
            - Параметры берутся из `parameters.inc` или `.va` файла.
        """
        # Получаем параметры из файла модели
        parameters = self.parse_parameters()
        
        # Формируем словарь параметров для изменения
        params_to_modify = {param["name"]: param["default_value"] for param in parameters}

        # Модифицируем файл parameters.inc
        modify_parameters(os.path.join(self.model_path, "parameters.inc"), params_to_modify)

        # Пересобираем osdi
        self.rebuild_osdi()
        self.move_osdi_file("bjt505.osdi")

        # Запускаем симуляцию в NGSPICE
        process = subprocess.Popen(["ngspice", "-b", spice_file])
        process.wait()

        # Отображаем график
        plot_simulation_data(canvas, fig)

import os
import subprocess
from utils import find_file, modify_parameters
from plot_simulation import plot_simulation_data
from parameter_parser import ParameterParser


class SimulationRunner:
    def __init__(self, model_path=None, vamodel_name=None):
        """
        Инициализация симулятора.

        Args:
            model_path (str): Путь к папке модели.
            vamodel_name (str): Имя .va файла.
        """
        self.model_path = model_path
        self.vamodel_name = vamodel_name
        self.parameters_file = os.path.join(model_path, "parameters.inc") if model_path else None

    def set_model(self, va_model_path):
        """Установка текущей модели."""
        self.vamodel_name = os.path.basename(va_model_path)
        self.model_path = os.path.dirname(va_model_path)
        self.parameters_file = os.path.join(self.model_path, "parameters.inc")

    def rebuild_osdi(self):
        """Пересборка osdi-модели."""
        if not self.vamodel_name:
            raise FileNotFoundError("Файл .va не выбран для модели.")
        
        try:
            subprocess.run(["./openvaf", self.vamodel_name], cwd=self.model_path, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка при пересборке osdi-модели: {e}")

    def move_osdi_file(self):
        """Перемещение osdi-файла."""
        osdi_name = self.vamodel_name.replace(".va", ".osdi")
        source_path = find_file(osdi_name, search_path=self.model_path)
        if not source_path:
            raise FileNotFoundError(f"Файл {osdi_name} не найден после пересборки.")
        
        osdilibs_path = os.path.join(self.model_path, "..", "osdilibs")
        os.makedirs(osdilibs_path, exist_ok=True)
        dst = os.path.join(osdilibs_path, osdi_name)

        if os.path.exists(dst):
            os.remove(dst)
        os.rename(source_path, dst)

    def parse_parameters(self):
        """Парсинг параметров модели."""
        try:
            parser = ParameterParser(self.model_path)
            parameters = parser.parse()
            if not parameters:
                raise ValueError("Файл parameters.inc или .va не содержит параметров.")
            return parameters
        except Exception as e:
            raise RuntimeError(f"Ошибка парсинга параметров: {e}")


    def run_simulation(self, spice_file, parameters, canvas, fig):
        """
        Запуск симуляции с пользовательскими параметрами.
        """
        try:
            # Модифицируем parameters.inc на основе переданных параметров
            modify_parameters(self.parameters_file, parameters)

            # Пересобираем osdi
            self.rebuild_osdi()
            self.move_osdi_file("bjt505.osdi")

            # Запускаем симуляцию
            process = subprocess.Popen(["ngspice", "-b", spice_file])
            process.wait()

            # Отображаем график
            plot_simulation_data(canvas, fig)
        except Exception as e:
            raise RuntimeError(f"Ошибка симуляции: {e}")

    def apply_changes_to_file(self, parameters):
        """
        Применяет изменения к выбранному файлу (parameters.inc или .va).

        Args:
            parameters (dict): Словарь параметров для записи.
        """
        file_path = os.path.join(self.model_path, self.vamodel_name)
        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                for name, value in parameters.items():
                    if line.strip().startswith(f"`MPR") and f"({name}" in line:
                        # Заменяем значение параметра
                        line = re.sub(r'(\w+)\s*,\s*([\d.eE+-]+)', f'{name}, {value}', line, count=1)
                file.write(line)

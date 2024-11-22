import os
import re

class ParameterParser:
    def __init__(self, model_path):
        """
        Инициализация парсера параметров.

        Args:
            model_path (str): Путь к папке модели (например, code/mextram/vacode).
        """
        self.model_path = model_path
        self.parameters = []

    def parse_parameters_file(self):
        """Парсинг файла parameters.inc."""
        parameters_file = os.path.join(self.model_path, "parameters.inc")
        if not os.path.exists(parameters_file):
            raise FileNotFoundError(f"Файл {parameters_file} не найден.")

        with open(parameters_file, "r") as file:
            for line in file:
                if line.startswith("MPR"):
                    match = re.match(
                        r'^MPR\w+\(\s*([\w]+)\s*,\s*([\w.+-]+)\s*,\s*"([^"]*)"\s*,\s*([\w.+-]+)\s*,\s*([\w.+-]+)\s*,\s*"(.*)"\s*\)',
                        line
                    )
                    if match:
                        self.parameters.append({
                            "name": match.group(1),
                            "default_value": match.group(2),
                            "units": match.group(3),
                            "min_value": match.group(4),
                            "max_value": match.group(5),
                            "description": match.group(6)
                        })
        return self.parameters

    def parse_va_file(self):
        """Парсинг модели .va."""
        va_files = [f for f in os.listdir(self.model_path) if f.endswith(".va")]
        if not va_files:
            raise FileNotFoundError("Файлы .va в указанной папке не найдены.")

        va_file_path = os.path.join(self.model_path, va_files[0])
        with open(va_file_path, "r") as file:
            for line in file:
                if line.startswith("MPR"):
                    match = re.match(
                        r'^MPR\w+\(\s*([\w]+)\s*,\s*([\w.+-]+)\s*,\s*"([^"]*)"\s*,\s*([\w.+-]+)\s*,\s*([\w.+-]+)\s*,\s*"(.*)"\s*\)',
                        line
                    )
                    if match:
                        self.parameters.append({
                            "name": match.group(1),
                            "default_value": match.group(2),
                            "units": match.group(3),
                            "min_value": match.group(4),
                            "max_value": match.group(5),
                            "description": match.group(6)
                        })
        return self.parameters

    def parse(self):
        """
        Основной метод парсинга. Сначала ищет parameters.inc,
        если файла нет, обрабатывает .va файл.
        """
        try:
            return self.parse_parameters_file()
        except FileNotFoundError:
            return self.parse_va_file()

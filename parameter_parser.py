import re
import os


class ParameterParser:
    def __init__(self, file_path, ignore_file=None):
        """
        Инициализация парсера параметров.

        Args:
            file_path (str): Путь к файлу parameters.inc или модели .va.
            ignore_file (str): Путь к файлу, содержащему параметры для игнорирования.
        """
        self.file_path = file_path
        self.ignore_file = ignore_file
        self.ignore_params = self._load_ignore_params()

    def _load_ignore_params(self):
        """
        Загружает список параметров для игнорирования из файла.

        Returns:
            set: Набор имен параметров для игнорирования.
        """
        if not self.ignore_file or not os.path.exists(self.ignore_file):
            return set()
        with open(self.ignore_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())

    def parse(self):
        """
        Парсит параметры из файла parameters.inc или модели .va.

        Returns:
            list: Список параметров в виде словарей.
        """
        parameters = []
        pattern = re.compile(
            r"`MPR\w+\(\s*(\w+)\s*,\s*([\d.eE+-]+)\s*,\s*\"(.*?)\"\s*,?\s*([\d.eE+-]*)\s*,?\s*([\d.eE+-]*)\s*,?\s*\"(.*?)\"\s*\)"
        )

        with open(self.file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    name, default_value, units, min_value, max_value, description = match.groups()

                    # Если параметр в списке игнорируемых, пропускаем его
                    if name in self.ignore_params:
                        continue

                    parameters.append({
                        "name": name,
                        "default_value": float(default_value),
                        "units": units,
                        "min_value": float(min_value) if min_value else None,
                        "max_value": float(max_value) if max_value else None,
                        "description": description,
                    })
        return parameters


# Пример использования
if __name__ == "__main__":
    parser = ParameterParser(
        "/home/gilspi/Desktop/progs/extract_parameters/code/mextram/vacode/parameters.inc",
        ignore_file="/home/gilspi/Desktop/progs/extract_parameters/ignore_params.txt"
    )
    result = parser.parse()
    print(result)

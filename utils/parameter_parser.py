import re
import os
from typing import List, Dict, Set, Optional, Protocol


class IgnoreParamsLoader(Protocol):
    def load_ignore_params(self) -> Set[str]:
        pass


class FileIgnoreParamsLoader(IgnoreParamsLoader):
    def __init__(self, ignore_file: Optional[str]) -> None:
        self.ignore_file = ignore_file

    def load_ignore_params(self) -> Set[str]:
        """
        Загружает список параметров для игнорирования из файла.

        Returns:
            Set[str]: Набор имен параметров для игнорирования.
        """
        if not self.ignore_file or not os.path.exists(self.ignore_file):
            return set()
        with open(self.ignore_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())
        

class ParameterParser:
    def __init__(self, file_path: str, ignore_params_loader: IgnoreParamsLoader) -> None:
        """
        Инициализация парсера параметров.

        Args:
            file_path (str): Путь к файлу parameters.inc или модели .va.
            ignore_file (str): Путь к файлу, содержащему параметры для игнорирования.
        """
        self.file_path = file_path
        self.ignore_params = ignore_params_loader.load_ignore_params()

    def parse(self) -> List[Dict[str, Optional[float]]]:
        """
        Парсит параметры из файла parameters.inc или модели .va.

        Returns:
            list: Список параметров в виде словарей.
        """
        parameters: List[Dict[str, Optional[float]]] = []
        pattern = re.compile(
            r"`MPR\w+\(\s*(\w+)\s*,\s*([\d.eE+-]+)\s*,\s*\"(.*?)\"\s*,?\s*([\d.eE+-]*)\s*,?\s*([\d.eE+-]*)\s*,?\s*\"(.*?)\"\s*\)"
        )

        with open(self.file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    name, default_value, units, min_value, max_value, description = match.groups()

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


if __name__ == "__main__":
    """
    Пример работы парсера
    """
    from config import PARAMETERS_FILE, IGNORE_PARAMS_FILE

    ignore_params_loader = FileIgnoreParamsLoader(ignore_file=IGNORE_PARAMS_FILE)
    parser = ParameterParser(
        file_path=PARAMETERS_FILE,
        ignore_params_loader=ignore_params_loader,
    )
    result = parser.parse()
    print(result)

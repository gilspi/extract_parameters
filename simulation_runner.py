import os
import re
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

    def apply_changes_to_file(self, current_parameters, target_file):
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"Файл {target_file} не найден.")

        # Чтение исходного содержимого файла
        with open(target_file, 'r') as file:
            lines = file.readlines()

        # Создаём карту для быстрого поиска строк по параметрам
        parameter_lines = {param_name: None for param_name in current_parameters}
        for i, line in enumerate(lines):
            for param_name in current_parameters:
                if re.search(rf"`MPR\w+\(\s*{re.escape(param_name)}\s*,", line):
                    parameter_lines[param_name] = i

        # Обновляем только строки с параметрами, которые нужно изменить
        for param_name, line_index in parameter_lines.items():
            if line_index is not None:
                line = lines[line_index]
                print(f"Найдена строка для обновления: {line.strip()}")  # Отладочная информация

                # Регулярное выражение для поиска и замены значения параметра
                match = re.search(
                    rf"(\s*`MPR\w+\(\s*{re.escape(param_name)}\s*,\s*)([-\d.eE+]+)",
                    line
                )
                if match:
                    prefix = match.group(1)  # Часть строки до значения
                    updated_line = f"{prefix}{current_parameters[param_name]}" + line[match.end():]
                    print(f"Обновлённая строка: {updated_line.strip()}")  # Отладочная информация
                    lines[line_index] = updated_line

        # Запись обратно в файл
        with open(target_file, 'w') as file:
            file.writelines(lines)

        print(f"Файл {target_file} успешно обновлён.")




if __name__ == "__main__":
    # Путь к тестовому файлу модели
    # test_model_path = "/home/gilspi/Desktop/progs/extract_parameters/code/ASMHEMT/vacode/asmhemt.va"
    test_model_path = "/home/gilspi/Desktop/progs/extract_parameters/code/mextram/vacode/parameters.inc"

    # Создаём параметры для изменения
    """test_parameters = {
        "voff": "3.0",  # Новое значение
        "ute": "-10.0",  # Новое значение
        "gamma0fp1": "2.23e-12",  # Новое значение
    }"""
    test_parameters = {
        "is": "3.0",  # Новое значение
        "nff": "-10.0",  # Новое значение
        "nfr": "2.23e-12",  # Новое значение
    }

    # Создаём экземпляр SimulationRunner
    runner = SimulationRunner(model_path=os.path.dirname(test_model_path), vamodel_name=os.path.basename(test_model_path))

    # Тестируем перезапись файла
    try:
        runner.apply_changes_to_file(current_parameters=test_parameters, target_file=test_model_path)
        print(f"Файл {test_model_path} успешно обновлён.")
    except Exception as e:
        print(f"Ошибка при обновлении файла: {e}")

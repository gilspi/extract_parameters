import os
import re
import subprocess
from utils import find_file, modify_parameters
from plot_simulation import plot_simulation_data
from parameter_parser import ParameterParser
from config import OSDILIBS_PATH


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
            print(self.vamodel_name)
            subprocess.run(["./openvaf", self.vamodel_name], cwd=self.model_path, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка при пересборке osdi-модели: {e}")

    def move_osdi_file(self):
        """Перемещение osdi-файла в директорию OSDILIBS_PATH."""
        osdi_name = self.vamodel_name.replace(".va", ".osdi")
        source_path = os.path.join(self.model_path, osdi_name)
        print(f"Ищем файл OSDI: {source_path}")

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Файл {osdi_name} не найден в {self.model_path} после пересборки.")

        os.makedirs(OSDILIBS_PATH, exist_ok=True)
        dst = os.path.join(OSDILIBS_PATH, osdi_name)

        print(f"Перемещаем файл OSDI в: {dst}")

        try:
            if os.path.exists(dst):
                print(f"Удаляем старый файл {dst}")
                os.remove(dst)

            os.rename(source_path, dst)
            print(f"Файл {osdi_name} успешно перемещён в {OSDILIBS_PATH}.")
        except Exception as e:
            raise RuntimeError(f"Ошибка при перемещении файла {osdi_name}: {e}")

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

    def run_simulation(self, spice_file, canvas, fig):
        try:
            print("Запускаем пересборку osdi")
            self.rebuild_osdi()
            print("Пытаемся переместить osdi файл")
            self.move_osdi_file()
            print("Перемещение завершено. Запускаем симуляцию.")
            process = subprocess.Popen(["ngspice", "-b", spice_file])
            process.wait()
            print("Симуляция завершена. Отображаем график.")
            plot_simulation_data(canvas, fig)
        except Exception as e:
            raise RuntimeError(f"Ошибка симуляции: {e}")

    def apply_changes_to_file(self, current_parameters, target_file):
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"Файл {target_file} не найден.")

        with open(target_file, 'r') as file:
            lines = file.readlines()
        
        parameter_lines = {param_name: None for param_name in current_parameters}  # Создаём карту для быстрого поиска строк по параметрам
        for i, line in enumerate(lines):
            for param_name in current_parameters:
                if re.search(rf"`MPR\w+\(\s*{re.escape(param_name)}\s*,", line):
                    parameter_lines[param_name] = i

        for param_name, line_index in parameter_lines.items():
            if line_index is not None:
                line = lines[line_index]
                print(f"Найдена строка для обновления: {line.strip()}")

                # Регулярное выражение для поиска и замены значения параметра
                match = re.search(
                    rf"(\s*`MPR\w+\(\s*{re.escape(param_name)}\s*,\s*)([-\d.eE+]+)",
                    line
                )
                if match:
                    prefix = match.group(1)  # Часть строки до значения
                    updated_line = f"{prefix}{current_parameters[param_name]}" + line[match.end():]
                    print(f"Обновлённая строка: {updated_line.strip()}")
                    lines[line_index] = updated_line

        with open(target_file, 'w') as file:
            file.writelines(lines)

        print(f"Файл {target_file} успешно обновлён.")



if __name__ == "__main__":
    # Путь к тестовому файлу модели
    test_model_path = "/home/nikita/Рабочий стол/extract_parameters/code/ASMHEMT/vacode/asmhemt.va"
    spice_file = "/home/nikita/Рабочий стол/extract_parameters/examples/ASMHEMT/nfet_id_vd_vg.sp"

    # Создаём параметры для изменения
    test_parameters = {
        "voff": "3.0",
        "ute": "-10.0",
        "gamma0fp1": "0.12",
    }

    runner = SimulationRunner(
        model_path=os.path.dirname(test_model_path),
        vamodel_name=os.path.basename(test_model_path)
    )

    try:
        print("=== Тест симуляции ===")

        runner.apply_changes_to_file(current_parameters=test_parameters, target_file=test_model_path)

        runner.run_simulation(spice_file, test_parameters, None, None)
        print("=== Тест завершён успешно ===")
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")



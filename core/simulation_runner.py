import os
import subprocess

from utils.parameter_parser import ParameterParser
from utils.utils import find_case_insensitive_path, remove_reference_line, duplicate_print_line, add_or_update_simulation_data_path_in_file
from core.osdi_manager import OSDIManager
from plotting.plot_simulation import SimulationManager

from config import REFERENCE_MODEL_CODE_PATH, SPICE_EXAMPLES_PATH, SIMULATION_RAW_DATA_PATH


class SimulationRunner:
    def __init__(self, model_path: str):
        """
        Инициализация симулятора.

        Args:
            model_path (str): Путь к папке модели.
            vamodel_name (str): Имя .va файла.
        """
        self.model_path = model_path
        self.vamodel_name = None
        self.manager = SimulationManager()
        self.osdi_manager = None

    def get_spice_file(self, model_name: str) -> str:
        """
        Возвращает путь к файлу схемы для модели из SPICE_EXAMPLES_PATH.
        """
        spice_file = os.path.join(SPICE_EXAMPLES_PATH, model_name, f"{model_name}.sp")

        if not os.path.exists(spice_file):
            raise FileNotFoundError(f"Схема для модели {model_name} не найдена: {spice_file}")
        
        return spice_file

    def set_model(self, va_model_path):
        """Установка текущей модели."""
        self.vamodel_name = os.path.basename(va_model_path)
        self.model_path = os.path.dirname(va_model_path)

    def parse_parameters(self):
        """Парсинг параметров модели."""
        try:
            parser = ParameterParser(self.model_path)
            parameters = parser.parse()
            if not parameters:
                raise ValueError(f"Файл {self.model_path} не содержит параметров.")
            return parameters
        except Exception as e:
            raise RuntimeError(f"Ошибка парсинга параметров: {e}")

    def run_simulation(self, spice_file: str, canvas, fig):
        """
        Запускает симуляцию с использованием указанных параметров.
        """
        try:
            self.osdi_manager = OSDIManager(model_path=self.model_path, vamodel_name=self.vamodel_name)
            # print("Запускаем пересборку osdi")
            self.osdi_manager.rebuild_osdi()
            # print("Пытаемся переместить osdi файл")
            self.osdi_manager.move_osdi_file()
            # print("Перемещение завершено. Запускаем симуляцию.")
            model_name = self.vamodel_name[:-3]
            reference_result_file = os.path.join(REFERENCE_MODEL_CODE_PATH, f"{model_name}_reference_data.txt")

            if not os.path.exists(reference_result_file) or os.path.getsize(reference_result_file) == 0:
                print("Эталонные данные отсутствуют. Добавляем строку в схему и запускаем симуляцию.")
                duplicate_print_line(spice_file=spice_file, new_path=reference_result_file)
                process_reference = subprocess.Popen(["ngspice", "-b", spice_file])
                process_reference.wait()

                print(f"Эталонные данные успешно созданы: {reference_result_file}")
                remove_reference_line(spice_file=spice_file)

            user_result_file = os.path.join(SIMULATION_RAW_DATA_PATH, "simulation_data.txt")   #TODO: изменить на дату имя файла
            
            if os.path.exists(user_result_file):
                with open(user_result_file, "w") as file:
                    pass
            
            add_or_update_simulation_data_path_in_file(spice_file, user_result_file)
            print("Запускаем симуляцию с пользовательскими параметрами.")
            process_user = subprocess.Popen(["ngspice", "-b", spice_file])
            process_user.wait()

            if not os.path.exists(user_result_file) or os.path.getsize(user_result_file) == 0:
                raise RuntimeError(
                "Simulation is complete, but the data file is missing or empty. Check the selected SP file and the model of the selected transistor."
                )

            print(f"Пользовательские данные успешно созданы: {user_result_file}")

            self.manager.run(
                fig=fig,
                canvas=canvas,
                user_filename=user_result_file,
                reference_filename=reference_result_file,
            )
            print("Графики успешно построены.")
        except Exception as e:
            raise RuntimeError(f"Ошибка симуляции: {e}")

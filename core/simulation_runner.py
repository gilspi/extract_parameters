import os
import subprocess

from utils.parameter_parser import ParameterParser
from utils.utils import find_case_insensitive_path, remove_reference_line, duplicate_print_line, add_or_update_simulation_data_path_in_file
from core.osdi_manager import OSDIManager
from plotting.plot_simulation import SimulationManager

from config import REFERENCE_MODEL_CODE_PATH, SPICE_EXAMPLES_PATH, SIMULATION_RAW_DATA_PATH


class SimulationRunner:
    def __init__(self, model_path: str, manager, user_result_file):
        """
        Инициализация симулятора.

        Args:
            model_path (str): Путь к папке модели.
            vamodel_name (str): Имя .va файла.
        """
        self.model_path = model_path
        self.vamodel_name = None
        self.manager = manager
        self.osdi_manager = None
        self.user_result_file = user_result_file

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

    def run_simulation(self, spice_file: str, canvas, fig):
        """
        Запускает симуляцию с отслеживанием прогресса и обработкой ошибок.
        """
        try:
            total_step = 5
            current_step = 0

            self.osdi_manager = OSDIManager(model_path=self.model_path, vamodel_name=self.vamodel_name)
            yield (current_step := current_step + 1) / total_step  # 20%

            self.osdi_manager.rebuild_osdi()
            yield (current_step := current_step + 1) / total_step  # 40%

            self.osdi_manager.move_osdi_file()
            yield (current_step := current_step + 1) / total_step  # 60%

            model_name = self.vamodel_name[:-3]
            reference_result_file = os.path.join(REFERENCE_MODEL_CODE_PATH, f"{model_name}_reference_data.txt")

            if not os.path.exists(reference_result_file) or os.path.getsize(reference_result_file) == 0:
                # print("Эталонные данные отсутствуют. Добавляем строку в схему и запускаем симуляцию.")
                duplicate_print_line(spice_file=spice_file, new_path=reference_result_file)
                process_reference = subprocess.Popen(["ngspice", "-b", spice_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process_reference.communicate()

                if process_reference.returncode != 0:
                    raise RuntimeError(f"Ошибка при создании эталонных данных:\n{stderr.decode('utf-8')}")

                # print(f"Эталонные данные успешно созданы: {reference_result_file}")
                remove_reference_line(spice_file=spice_file)

            # self.user_result_file = os.path.join(SIMULATION_RAW_DATA_PATH, "simulation_data.txt")

            if os.path.exists(self.user_result_file):
                with open(self.user_result_file, "w") as file:
                    pass

            add_or_update_simulation_data_path_in_file(spice_file, self.user_result_file)
            # print("Запускаем симуляцию с пользовательскими параметрами.")

            process_user = subprocess.Popen(["ngspice", "-b", spice_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process_user.communicate()

            if process_user.returncode != 0:
                raise RuntimeError(f"Ошибка симуляции:\n{stderr.decode('utf-8')}")

            yield (current_step := current_step + 1) / total_step  # 80%

            if not os.path.exists(self.user_result_file) or os.path.getsize(self.user_result_file) == 0:
                raise RuntimeError(
                    "Simulation is complete, but the data file is missing or empty. "
                    "Check the selected SP file and the model of the selected transistor."
                )

            # print(f"Пользовательские данные успешно созданы: {user_result_file}")

            self.manager.run(
                fig=fig,
                canvas=canvas,
                user_filename=self.user_result_file,
                reference_filename=reference_result_file,
            )
            yield 1.0  # 100%
            # print("Графики успешно построены.")

        except Exception as e:
            error_message = f"Ошибка симуляции: {str(e)}"
            # print(error_message)
            yield error_message


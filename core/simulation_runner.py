import os
import subprocess

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from utils.parameter_parser import ParameterParser
from core.osdi_manager import OSDIManager
from plotting.plot_simulation import SimulationManager
from utils.parameter_parser import ParameterParser


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
        # self.parameters_file = os.path.join(model_path, "parameters.inc") if model_path else None  # FIXME некорректная строка для поиска параметров ибо это не всегда будет parameters.inc
        self.manager = SimulationManager()
        self.osdi_manager = None
        # self.file_manager = FileManager()
    
    def set_model(self, va_model_path):
        """Установка текущей модели."""
        self.vamodel_name = os.path.basename(va_model_path)
        self.model_path = os.path.dirname(va_model_path)
        # self.parameters_file = os.path.join(self.model_path, "parameters.inc")  # FIXME убрать в дальнейшем

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

    def run_simulation(self, spice_file: str, canvas: FigureCanvas, fig: Figure) -> None:
        try:
            self.osdi_manager = OSDIManager(model_path=self.model_path, vamodel_name=self.vamodel_name)
            print("Запускаем пересборку osdi")
            self.osdi_manager.rebuild_osdi()
            print("Пытаемся переместить osdi файл")
            self.osdi_manager.move_osdi_file()
            print("Перемещение завершено. Запускаем симуляцию.")
            process = subprocess.Popen(["ngspice", "-b", spice_file])
            process.wait()
            print("Симуляция завершена. Отображаем график.")
            self.manager.run(canvas=canvas, fig=fig)
        except Exception as e:
            raise RuntimeError(f"Ошибка симуляции: {e}")


if __name__ == "__main__":
    from core.file_manager import FileManager
    # Путь к тестовому файлу модели
    # test_model_path = "/home/nikita/Рабочий стол/extract_parameters/code/ASMHEMT/vacode/asmhemt.va"
    # spice_file = "/home/nikita/Рабочий стол/extract_parameters/examples/ASMHEMT/nfet_id_vd_vg.sp"

    test_model_path = "/home/gilspi/Desktop/progs/extract_parameters/code/mextram/vacode/bjt505.va"
    spice_file = "/home/gilspi/Desktop/progs/extract_parameters/examples/mextram/ngspice/npn_ic_ib_is_vb.sp"

    # Создаём параметры для изменения
    test_parameters = {
    }

    try:
        print("=== Тест симуляции ===")
        runner = SimulationRunner(
                                model_path=test_model_path
                                )
        file_manager = FileManager()
        file_manager.apply_changes_to_file(current_parameters=test_parameters, target_file=test_model_path)

        runner.run_simulation(spice_file, None, None)
        print("=== Тест завершён успешно ===")
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")



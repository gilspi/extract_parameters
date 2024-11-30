import os
import subprocess

from config import OSDILIBS_PATH

# FIXME после нажатия на кнопку запустить симуляцию выполняется команда ./openvaf nfet.sp хотя модель я выбрал ранее
class OSDIManager:
    def __init__(self, model_path: str, vamodel_name: str) -> None:
        #FIXME переделать названия ибо они некорректные
        self.model_path = model_path  # os.path.dirname(model_path)
        self.vamodel_name = vamodel_name  # os.path.basename(model_path)
        self.parameters_file = os.path.join(model_path, "parameters.inc") if model_path else None  # FIXME некорректная строка для поиска параметров ибо это не всегда будет parameters.inc
        # FIXME скорее всего parameters_file можно убрать
        
    def rebuild_osdi(self):
        """Пересборка osdi-модели."""

        if not self.vamodel_name:
            raise FileNotFoundError("Файл .va не выбран для модели.")
        
        try:
            print(self.vamodel_name)
            print(self.model_path)
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
        print(OSDILIBS_PATH, osdi_name)
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


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    vamodel_name = "/home/gilspi/Desktop/progs/extract_parameters/code/ASMHEMT/vacode/asmhemt.va"
    vamodel_path = "/home/gilspi/Desktop/progs/extract_parameters/code/ASMHEMT/vacode/asmhemt.va"

    osdi_manager = OSDIManager(
        model_path=vamodel_name,
    )
    osdi_manager.rebuild_osdi()
    osdi_manager.move_osdi_file()

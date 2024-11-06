import os
import platform
import subprocess

from config import OSDILIBS_PATH


class OSDIManager:
    def __init__(self, model_path: str, vamodel_name: str) -> None:
        self.model_path = model_path
        self.vamodel_name = vamodel_name

    def rebuild_osdi(self):
        """Пересборка osdi-модели."""

        if not self.vamodel_name:
            raise FileNotFoundError("Файл .va не выбран для модели.")
        
        current_os = platform.system()
        if current_os == "Windows":
            command = "openvaf.exe"
        elif current_os == "Linux":
            command = "./openvaf"
        else:
            raise OSError("Unsupported operating system")
        
        try:
            subprocess.run([command, self.vamodel_name], cwd=self.model_path, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка при пересборке osdi-модели: {e}")

    def move_osdi_file(self):
        """Перемещение osdi-файла в директорию OSDILIBS_PATH."""
        osdi_name = self.vamodel_name.replace(".va", ".osdi")
        source_path = os.path.join(self.model_path, osdi_name)

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Файл {osdi_name} не найден в {self.model_path} после пересборки.")

        os.makedirs(OSDILIBS_PATH, exist_ok=True)
        dst = os.path.join(OSDILIBS_PATH, osdi_name)

        try:
            if os.path.exists(dst):
                os.remove(dst)

            os.rename(source_path, dst)
        except Exception as e:
            raise RuntimeError(f"Ошибка при перемещении файла {osdi_name}: {e}")

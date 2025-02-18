import platform
import subprocess
import shutil

from pathlib import Path

from config import OSDILIBS_PATH


class OSDIManager:
    def __init__(self, model_path: str, vamodel_name: str) -> None:
        self.model_path = Path(model_path)
        self.vamodel_name = vamodel_name
        self.osdi_name = Path(self.vamodel_name).with_suffix(".osdi").name
        self.source_path = Path(self.model_path) / self.osdi_name
        self.dst = Path(OSDILIBS_PATH) / self.osdi_name

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
            # print(self.vamodel_name)
            # print(self.model_path)
            subprocess.run([command, self.vamodel_name], cwd=self.model_path, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка при пересборке osdi-модели: {e}")

    def move_osdi_file(self):
        """Moving the osdi file to the OSDILIBS_PATH directory."""
        if not self.source_path.exists():
            raise FileNotFoundError(f"File: {self.osdi_name} not found in {self.model_path} after rebuild.")

        try:
            if self.dst.exists():
                self.dst.unlink()

            shutil.move(str(self.source_path), str(self.dst))
            print(f"File {self.osdi_name} successfully moved {OSDILIBS_PATH}.")
        except Exception as e:
            raise RuntimeError(f"Error when trying to move a file: {self.osdi_name}: {e}")

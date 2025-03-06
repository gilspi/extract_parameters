import os
import docker
from docker.errors import DockerException, ContainerError, NotFound, ImageNotFound

# from config import OSDILIBS_PATH
OSDILIBS_PATH = "B:\\Python\\extract_parameters\\osdilibs"

class OSDIManager:
    CONTAINER_NAME = "openvaf-instance"
    IMAGE_NAME = "openvaf-image"

    def __init__(self, model_path: str, vamodel_name: str) -> None:
        self.model_directory_path = os.path.abspath(model_path)
        self._parent_directory_model = os.path.dirname(self.model_directory_path)
        self._model_filename = vamodel_name
        self.client = docker.from_env()
        self.va_folder = os.path.basename(self.model_directory_path)
        self._va_file_path = f"/app/model/{self.va_folder}/{self._model_filename}"
        

    def build_image(self):
        """Проверяет, существует ли Docker-образ, и если нет, создает его."""
        try:
            self.client.images.get(self.IMAGE_NAME)
            print(f"Образ {self.IMAGE_NAME} уже существует.")
        except ImageNotFound:
            print(f"Образ {self.IMAGE_NAME} не найден. Создаем новый...")
            self.client.images.build(path=".", tag=self.IMAGE_NAME)
            print(f"Образ {self.IMAGE_NAME} успешно создан.")

    def ensure_container_running(self):
        try:
            container = self.client.containers.get(self.CONTAINER_NAME)
            if container.status != "running":
                print(f"Запускаем контейнер {self.CONTAINER_NAME}...")
                container.start()
        except NotFound:
            print(f"Контейнер {self.CONTAINER_NAME} не найден. Создаем...")
            self.start_container()
        except Exception as e:
            raise RuntimeError(f"Ошибка: {str(e)}")

    def start_container(self):
        """Запускает Docker-контейнер с монтированием папки."""
        try:
            print(f"Создаём контейнер {self.CONTAINER_NAME} с монтированием {self._parent_directory_model} -> /app/model...")

            self.client.containers.run(
                image=self.IMAGE_NAME,
                name=self.CONTAINER_NAME,
                command="sleep infinity",
                volumes={self._parent_directory_model: {'bind': '/app/model', 'mode': 'rw'}},
                working_dir="/app",
                detach=True,
            )

            print(f"Контейнер {self.CONTAINER_NAME} успешно создан и запущен.")

        except ImageNotFound:
            raise RuntimeError(f"Образ {self.IMAGE_NAME} не найден. Выполните `docker build -t {self.IMAGE_NAME} .`")
        except docker.errors.ContainerError as e:
            raise RuntimeError(f"Ошибка при запуске контейнера: {e}")

    def rebuild_osdi(self):
        """Пересборка osdi-модели с использованием Docker."""
        if not self._model_filename:
            raise FileNotFoundError("Файл .va не выбран для модели.")

        self.build_image()
        self.ensure_container_running()

        container = self.client.containers.get(self.CONTAINER_NAME)

        try:
            print(f"Запускаем пересборку модели {self._model_filename} внутри контейнера...")
            exec_result = container.exec_run(f"./openvaf {self._va_file_path} -o {self._va_file_path.replace('.va', '.osdi')}")
            print(exec_result.output.decode().strip())

            if exec_result.exit_code != 0:
                raise RuntimeError(f"Ошибка при пересборке osdi-модели: {exec_result.output.decode().strip()}")

            print(f"Модель {self._model_filename} успешно пересобрана.")
        except docker.errors.APIError as e:
            raise RuntimeError(f"Ошибка Docker: {e}")

    def move_osdi_file(self):
        """Перемещение osdi-файла в директорию OSDILIBS_PATH."""
        osdi_name = self._model_filename.replace(".va", ".osdi")
        source_path = os.path.join(self.model_directory_path, osdi_name)

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Файл {osdi_name} не найден в {self.model_directory_path} после пересборки.")

        os.makedirs(OSDILIBS_PATH, exist_ok=True)
        dst = os.path.join(OSDILIBS_PATH, osdi_name)

        try:
            if os.path.exists(dst):
                os.remove(dst)

            os.rename(source_path, dst)
        except Exception as e:
            raise RuntimeError(f"Ошибка при перемещении файла {osdi_name}: {e}")


if __name__ == "__main__":
    osdi_manager = OSDIManager(model_path="B:\Python\extract_parameters\data\code\mextram", vamodel_name="bjt505.va")
    osdi_manager.rebuild_osdi()
    osdi_manager.move_osdi_file()

import os
import docker
from docker.errors import DockerException, ContainerError, NotFound, ImageNotFound
import time

# from config import OSDILIBS_PATH
OSDILIBS_PATH = "B:\\Python\\extract_parameters\\osdilibs"

class OSDIManager:
    CONTAINER_NAME = "openvaf-instance"
    IMAGE_NAME = "openvaf-image"

    def __init__(self, model_path: str, vamodel_name: str) -> None:
        self.model_path = os.path.abspath(model_path)  # Абсолютный путь
        self.vamodel_name = vamodel_name
        self.client = docker.from_env()

    def ensure_image_exists(self):
        """Проверяет, существует ли Docker-образ, и если нет, создает его."""
        try:
            self.client.images.get(self.IMAGE_NAME)
            print(f"Образ {self.IMAGE_NAME} уже существует.")
        except ImageNotFound:
            print(f"Образ {self.IMAGE_NAME} не найден. Создаем новый...")
            self.build_docker_image()

    def build_docker_image(self):
        """Создает Docker-образ."""
        try:
            print("Начинаем сборку Docker-образа...")
            self.client.images.build(path=".", tag=self.IMAGE_NAME)
            print(f"Образ {self.IMAGE_NAME} успешно создан.")
        except docker.errors.BuildError as e:
            raise RuntimeError(f"Ошибка при создании Docker-образа: {e}")

    def ensure_container_running(self):
        """Проверяет, запущен ли контейнер, и если нет, запускает его."""
        try:
            container = self.client.containers.get(self.CONTAINER_NAME)
            if container.status != "running":
                print(f"Контейнер {self.CONTAINER_NAME} не запущен. Запускаем...")
                container.start()
                time.sleep(3)
                container.reload()
                if container.status != "running":
                    raise RuntimeError(f"Контейнер {self.CONTAINER_NAME} не запустился. Логи: {container.logs().decode()}")
        except NotFound:
            print(f"Контейнер {self.CONTAINER_NAME} не найден. Создаём новый...")
            self.start_container()

    def start_container(self):
        """Запускает Docker-контейнер с монтированием папки."""
        try:
            print(f"Создаём контейнер {self.CONTAINER_NAME} с монтированием {self.model_path} -> /app/model...")

            self.client.containers.run(
                image=self.IMAGE_NAME,
                name=self.CONTAINER_NAME,
                command="sleep infinity",
                volumes={os.path.dirname(self.model_path): {'bind': '/app/model', 'mode': 'rw'}},
                working_dir="/app",
                detach=True,
            )

            time.sleep(5)
            container = self.client.containers.get(self.CONTAINER_NAME)
            container.reload()

            if container.status != "running":
                raise RuntimeError(f"Контейнер {self.CONTAINER_NAME} не запустился. Логи: {container.logs().decode()}")

            print(f"Контейнер {self.CONTAINER_NAME} успешно создан и запущен.")

        except ImageNotFound:
            raise RuntimeError(f"Образ {self.IMAGE_NAME} не найден. Выполните `docker build -t {self.IMAGE_NAME} .`")
        except docker.errors.ContainerError as e:
            raise RuntimeError(f"Ошибка при запуске контейнера: {e}")

    def rebuild_osdi(self):
        """Пересборка osdi-модели с использованием Docker."""
        if not self.vamodel_name:
            raise FileNotFoundError("Файл .va не выбран для модели.")

        self.ensure_image_exists()
        self.ensure_container_running()

        container = self.client.containers.get(self.CONTAINER_NAME)
        container.reload()

        if container.status != "running":
            raise RuntimeError(f"Контейнер {self.CONTAINER_NAME} не работает! Логи: {container.logs().decode()}")

        va_folder = os.path.basename(self.model_path)
        va_file_path = f"/app/model/{va_folder}/{self.vamodel_name}"

        check_file_cmd = f"test -f {va_file_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        check_result = container.exec_run(check_file_cmd)
        check_output = check_result.output.decode().strip()

        if check_output == "NOT_FOUND":
            raise FileNotFoundError(f"Файл {va_file_path} отсутствует в контейнере")

        try:
            print(f"Запускаем пересборку модели {self.vamodel_name} внутри контейнера...")
            exec_result = container.exec_run(f"./openvaf {va_file_path} -o {va_file_path.replace('.va', '.osdi')}")
            output = exec_result.output.decode().strip()
            print(output)

            if exec_result.exit_code != 0:
                raise RuntimeError(f"Ошибка при пересборке osdi-модели: {output}")

            print(f"Модель {self.vamodel_name} успешно пересобрана.")
        except docker.errors.APIError as e:
            raise RuntimeError(f"Ошибка Docker: {e}")
        
    def check_files_in_container(self):
        """Проверяет, что файлы `.va` доступны внутри контейнера."""
        container = self.client.containers.get(self.CONTAINER_NAME)
        check_cmd = "ls -l /app/model"

        exec_result = container.exec_run(check_cmd)
        output = exec_result.output.decode().strip()

        if "total 0" in output or "No such file or directory" in output:
            raise FileNotFoundError(f"Ошибка! Папка /app/model пуста или не смонтирована!")

        print(f"Файлы в /app/model/:")
        print(output)


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


if __name__ == "__main__":
    osdi_manager = OSDIManager(model_path="B:\Python\extract_parameters\data\code\ASMHEMT", vamodel_name="asmhemt.va")
    osdi_manager.rebuild_osdi()
    osdi_manager.move_osdi_file()

import os
import re
from typing import Optional


import config


def find_file(filename: str, search_path: Optional[str] = None) -> Optional[str] :
    """
    Функция для поиска файла в указанной директории или в корневой директории проекта.
    
    :param filename: Имя файла для поиска.
    :param search_path: Директория для поиска (если None, используется корень проекта).
    :return: Путь к найденному файлу или None, если файл не найден.
    """
    if search_path is None:
        search_path = config.PROJECT_PATH

    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def modify_parameters(file_path: str, params_to_modify: dict):
    """
    Функция изменяет параметры модели в parameters.inc
    """
    with open(file_path, 'r') as file:
        content = file.read()

    for param, value in params_to_modify.items():
        regex = rf"(`\w+\(\s*{param}\s*,\s*)([^,]+)"
        def replace_value(match):
            return match.group(1) + value
        content = re.sub(regex, replace_value, content)
        
    with open(file_path, 'w') as file:
        file.write(content)

def find_case_insensitive_path(base_path: str, target_name: str) -> str:
    """
    Ищет директорию или файл внутри base_path, игнорируя регистр.
    Возвращает полный путь к найденному элементу.
    """
    try:
        for root, dirs, files in os.walk(base_path):
            for name in dirs + files:
                if name.lower() == target_name.lower():
                    return os.path.join(root, name)
        raise FileNotFoundError(f"Файл или директория {target_name} не найдены в {base_path}.")
    except Exception as e:
        raise RuntimeError(f"Ошибка при поиске файла: {e}")


def duplicate_print_line(spice_file: str, new_path: str):
    """
    Находит строку, начинающуюся с 'print', дублирует её с изменённым путём,
    если такая строка ещё не добавлена.

    Args:
        spice_file (str): Путь к файлу схемы.
        new_path (str): Новый путь для дублированной строки.
    """
    try:
        with open(spice_file, "r") as file:
            lines = file.readlines()

        # for line in lines:
        #     if line.strip().startswith("*print") and new_path in line:
        #         print(f"Строка с путём '{new_path}' уже существует. Пропуск добавления.")
        #         return

        updated_lines = []
        line_duplicated = False

        for line in lines:
            updated_lines.append(line)
            if line.strip().startswith("print"):
                parts = line.rsplit(">", 1)
                if len(parts) == 2:
                    new_line = f"{parts[0].strip()} > {new_path}\n"
                    updated_lines.append(new_line)
                    line_duplicated = True

        if not line_duplicated:
            print("Строка, начинающаяся с 'print', не найдена.")
            return
        
        with open(spice_file, "w") as file:
            file.writelines(updated_lines)

        print(f"Строка успешно дублирована с новым путём: {new_path}")

    except Exception as e:
        raise RuntimeError(f"Ошибка при дублировании строки в файле: {e}")


def comment_reference_line(spice_file: str):
    """
    Находит и комментирует строку, содержащую '/reference/'.

    Args:
        spice_file (str): Путь к файлу схемы.
    """
    try:
        with open(spice_file, "r") as file:
            lines = file.readlines()

        updated_lines = []

        for line in lines:
            if "/reference/" in line and not line.strip().startswith("*"):
                updated_lines.append(f"*{line}")
            else:
                updated_lines.append(line)

        with open(spice_file, "w") as file:
            file.writelines(updated_lines)

        print("Строка, содержащая '/reference/', успешно закомментирована.")

    except Exception as e:
        raise RuntimeError(f"Ошибка при комментировании строки: {e}")
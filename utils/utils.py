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


def remove_reference_line(spice_file: str):
    """
    Находит и удаляет строку, содержащую '/reference/'.

    Args:
        spice_file (str): Путь к файлу схемы.
    """
    try:
        with open(spice_file, "r") as file:
            lines = file.readlines()

        updated_lines = [
            line for line in lines if "/reference/" not in line
        ]

        with open(spice_file, "w") as file:
            file.writelines(updated_lines)

        print("Строка, содержащая '/reference/', успешно удалена.")

    except Exception as e:
        raise RuntimeError(f"Ошибка при удалении строки: {e}")

def add_or_update_simulation_data_path_in_file(scheme_file_path, simulation_data_path):
    """
    Ищет строку с командой *print и заменяет её на новую. Если строка не найдена, добавляет её перед .endc.

    Args:
        scheme_file_path (str): Путь к файлу схемы.
        simulation_data_path (str): Путь для сохранения данных симуляции.
    """
    try:
        with open(scheme_file_path, 'r') as scheme_file:
            lines = scheme_file.readlines()

        print_line = f"*print [add-pointers from plot and do other print like that] > {simulation_data_path}\n"
        print_line_found = False
        
        for i, line in enumerate(lines):
            if line.strip() == print_line.strip():
                print_line_found = True
                break
            if line.startswith("*print"):
                lines[i] = print_line
                print_line_found = True
                break

        if not print_line_found:
            endc_index = None
            for i, line in enumerate(lines):
                if '.endc' in line:
                    endc_index = i
                    break

            if endc_index is None:
                raise ValueError(".endc не найдено в файле")

            lines.insert(endc_index, print_line)

        with open(scheme_file_path, 'w') as scheme_file:
            scheme_file.writelines(lines)

        print(f"Строка с путем к файлу {simulation_data_path} успешно добавлена или обновлена в {scheme_file_path}")

    except Exception as e:
        print(f"Ошибка при добавлении или обновлении строки в файл: {e}")


def shorten_file_path(full_path, max_length=40):
    """
    Если длина пути больше max_length, возвращает строку вида:
    начало пути + "..." + имя файла
    """
    if len(full_path) <= max_length:
        return full_path
    filename = os.path.basename(full_path)
    # Вычитаем длину файла и троеточия
    remaining = max_length - len(filename) - 3
    if remaining < 1:
        # Если места совсем мало, возвращаем только имя файла с троеточием спереди
        return "..." + filename[-(max_length-3):]
    shortened = full_path[:remaining] + "..." + filename
    return shortened

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

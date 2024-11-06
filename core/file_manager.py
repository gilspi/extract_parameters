import os
import re

from typing import Dict


class FileManager:
    def apply_changes_to_file(self, current_parameters: Dict[str, str], target_file: str):
        if not os.path.exists(target_file):
            raise FileNotFoundError(f"Файл {target_file} не найден.")

        with open(target_file, 'r') as file:
            lines = file.readlines()
        
        parameter_lines = {param_name: None for param_name in current_parameters}  # создаём карту для быстрого поиска строк по параметрам
        for i, line in enumerate(lines):
            for param_name in current_parameters:
                if re.search(rf"`MPR\w+\(\s*{re.escape(param_name)}\s*,", line):
                    parameter_lines[param_name] = i

        for param_name, line_index in parameter_lines.items():
            if line_index is not None:
                line = lines[line_index]

                # регулярное выражение для поиска и замены значения параметра
                match = re.search(
                    rf"(\s*`MPR\w+\(\s*{re.escape(param_name)}\s*,\s*)([-\d.eE+]+)",
                    line
                )
                if match:
                    prefix = match.group(1)  # часть строки до значения
                    updated_line = f"{prefix}{current_parameters[param_name]}" + line[match.end():]
                    lines[line_index] = updated_line

        with open(target_file, 'w') as file:
            file.writelines(lines)

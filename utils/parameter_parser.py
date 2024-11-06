import re
import os
import csv
import datetime
from typing import List, Dict, Set, Optional, Protocol


class IgnoreParamsLoader(Protocol):
    def load_ignore_params(self) -> Set[str]:
        pass


class FileIgnoreParamsLoader(IgnoreParamsLoader):
    def __init__(self, ignore_file: Optional[str]) -> None:
        self.ignore_file = ignore_file

    def load_ignore_params(self) -> Set[str]:
        if not self.ignore_file or not os.path.exists(self.ignore_file):
            return set()
        with open(self.ignore_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())
        

class ParameterParser:
    def __init__(self, file_path: str, ignore_params_loader: IgnoreParamsLoader) -> None:
        self.file_path = file_path
        self.ignore_params = ignore_params_loader.load_ignore_params()
        self.model_name = os.path.splitext(os.path.basename(file_path))[0]

    def parse(self) -> List[Dict[str, Optional[float]]]:
        parameters: List[Dict[str, Optional[float]]] = []
        pattern = re.compile(
            r"`?(?:MPR|MPI|MPO|IPR|MPIsw|aliasparam)\w*\(\s*(\w+)\s*,\s*([-\d.eE+inf]+)\s*,\s*\"(.*?)\"\s*,\s*([-\d.eE+inf]*)\s*,\s*([-\d.eE+inf]*)\s*,\s*\"(.*?)\"\s*\)"
        )

        with open(self.file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    name, default_value, units, min_value, max_value, description = match.groups()

                    if name in self.ignore_params:
                        continue

                    parameters.append({
                        "name": name,
                        "default_value": float(default_value) if default_value.replace('.', '', 1).isdigit() else default_value,
                        "units": units,
                        "min_value": float(min_value) if min_value and min_value.replace('.', '', 1).isdigit() else None,
                        "max_value": float(max_value) if max_value and max_value.replace('.', '', 1).isdigit() else None,
                        "description": description,
                    })
        return parameters

    def save_simulation_results(self, input_file: str, directory: str):
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} not found.")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(directory, f"simulation_results_{timestamp}.csv")  #TODO: исправить название гибкое включает название модели
        
        with open(input_file, "r") as file:
            lines = file.readlines()
        
        start_index = None
        header = []
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if "Index" in parts:
                start_index = i + 1
                header = parts
                break
        
        if start_index is None:
            print("Error: Could not find data header in the file.")
            return
        
        data = []
        for line in lines[start_index:]:
            parts = line.strip().split()
            if len(parts) == len(header) and parts[0].isdigit():
                row = {header[i]: parts[i] for i in range(len(parts))}
                data.append(row)
        
        if not data:
            print("No valid simulation data found.")
            return
        
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Saved simulation results to {output_file}")


if __name__ == "__main__":
    from config import IGNORE_PARAMS_FILE, SIMULATION_RAW_DATA_PATH, REFERENCE_MODEL_CODE_PATH
    input_file = "/home/gilspi/Desktop/progs/extract_parameters/data/reference/asmhemt_reference_data.txt"
    output_directory = REFERENCE_MODEL_CODE_PATH
    os.makedirs(output_directory, exist_ok=True)
    
    parser = ParameterParser(file_path=input_file, ignore_params_loader="")
    parser.save_simulation_results(input_file, output_directory)
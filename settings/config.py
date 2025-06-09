import os  # TODO: remove

from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    root_dir: Field()
    osdilibs_dir: Field()
    ignore_params_path: Field()
    simulation_raw_data_path: Field()
    model_code_dir: Field()
    pics_path: Field()
    spice_dir: Field()
    reference_dir: Field()
    output_data_dir: Field()


class Model(Config):
    model: Field()
    spice: Field()
    parameters: Field()


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))  # определение корневого пути проекта
OSDILIBS_PATH = os.path.join(PROJECT_PATH, "data/osdilibs/")
IGNORE_PARAMS_FILE = os.path.join(PROJECT_PATH, "data/ignore_params.txt")
SIMULATION_RAW_DATA_PATH = os.path.join(PROJECT_PATH, "data/raw/")  # путь к точкам на графике, после выполненной симуляции
PICS_PATH = os.path.join(PROJECT_PATH, "pics/")
MODEL_CODE_PATH = os.path.join(PROJECT_PATH, "data/code/")
SPICE_EXAMPLES_PATH = os.path.join(PROJECT_PATH, "data/examples/")
REFERENCE_MODEL_CODE_PATH = os.path.join(PROJECT_PATH, "data/reference/")
OUTPUT_DATA_PATH = os.path.join(os.path.expanduser("~"), "Documents", "SimulationResults")
DIRECTORY = [REFERENCE_MODEL_CODE_PATH, SIMULATION_RAW_DATA_PATH, OUTPUT_DATA_PATH, PICS_PATH]

INITIAL_LOG_SCALE = False  # Логарифмическая шкала выключена при запуске
INITIAL_GRID = True        # Сетка включена при запуске


CONFIG_OPTIONS = {
    "BJT505": {
        "model": os.path.join("data", "code", "mextram", "vacode", "bjt505.va"),
        "spice": os.path.join("data", "examples", "mextram", "ngspice", "npn_ic_ib_is_vb.sp"),
        "parameters": os.path.join("data", "code", "mextram", "vacode", "parameters.inc")
    },
    "ASMHEMT": {
        "model": os.path.join("data", "code", "ASMHEMT", "vacode", "asmhemt.va"),
        "spice": os.path.join("data", "examples", "ASMHEMT", "nfet_id_vd_vg.sp"),
        "parameters": os.path.join("data", "code", "ASMHEMT", "vacode", "asmhemt.va")
    }
}
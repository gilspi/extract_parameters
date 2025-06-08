import os

"""
TODO: вместо .txt использовать .csv
"""

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))  # определение корневого пути проекта
# print(PROJECT_PATH)
OSDILIBS_PATH = os.path.join(PROJECT_PATH, "data/osdilibs/")
# print(OSDILIBS_PATH)
IGNORE_PARAMS_FILE = os.path.join(PROJECT_PATH, "data/ignore_params.txt")
# print(IGNORE_PARAMS_FILE)
SIMULATION_RAW_DATA_PATH = os.path.join(PROJECT_PATH, "data/raw/")  # путь к точкам на графике, после выполненной симуляции
# print(SIMULATION_DATA_PATH)
PICS_PATH = os.path.join(PROJECT_PATH, "pics/")
# print(PICS_PATH)
MODEL_CODE_PATH = os.path.join(PROJECT_PATH, "data/code/")
# print(MODEL_CODE_PATH)
SPICE_EXAMPLES_PATH = os.path.join(PROJECT_PATH, "data/examples/")
# print(SPICE_EXAMPLES_PATH)
REFERENCE_MODEL_CODE_PATH = os.path.join(PROJECT_PATH, "data/reference/")
# print(REFERENCE_MODEL_CODE_PATH)
OUTPUT_DATA_PATH = os.path.join(os.path.expanduser("~"), "Documents", "SimulationResults")
# print(OUTPUT_DATA_PATH)
DIRECTORY = [REFERENCE_MODEL_CODE_PATH, SIMULATION_RAW_DATA_PATH, OUTPUT_DATA_PATH, PICS_PATH]
# print(DIRECTORY)

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
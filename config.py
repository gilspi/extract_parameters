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
DIRECTORY = [REFERENCE_MODEL_CODE_PATH, SIMULATION_RAW_DATA_PATH]
# print(DIRECTORY)

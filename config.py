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
# TODO: нужно выполнять поиск файла с помощью os

# FOLDER_NAME = "mextram"  # FIXME: пока что код работает только с mextram

# PARAMETERS_FILE= os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/parameters.inc")
# VAMODEL_PATH = os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/")
# VAMODEL_NAME = "bjt505.va"
# OSDIMODEL_NAME = "bjt505.osdi"
# EXAMPLES_PATH = os.path.join(PROJECT_PATH, f"examples/{FOLDER_NAME}/ngspice/")
# SPICE_FILE = "npn_ic_ib_is_vb.sp"
# spice_file = None
# find_file(SPICE_FILE)

####################################################################################
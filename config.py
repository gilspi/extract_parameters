import os

# определение корневого пути проекта
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# print(PROJECT_PATH)
OSDILIBS_PATH = os.path.join(PROJECT_PATH, "osdilibs/")
# print(OSDILIBS_PATH)
IGNORE_PARAMS_FILE = os.path.join(PROJECT_PATH, "ignore_params.txt")

# TODO: нужно выполнять поиск файла с помощью os
# TODO: в дальнейшем пользователь должен просто подгружать модель из окна GUI
FOLDER_NAME = "mextram"  # FIXME: пока что код работает только с mextram

PARAMETERS_FILE= os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/parameters.inc")
VAMODEL_PATH = os.path.join(PROJECT_PATH, f"code/{FOLDER_NAME}/vacode/")
VAMODEL_NAME = "bjt505.va"
OSDIMODEL_NAME = "bjt505.osdi"
EXAMPLES_PATH = os.path.join(PROJECT_PATH, f"examples/{FOLDER_NAME}/ngspice/")
SPICE_FILE = "npn_ic_ib_is_vb.sp"  # FIXME: нужно сделать так чтобы можно было пользователь мог подгружать схему
####################################################################################

spice_file = None  # find_file(SPICE_FILE)
# print(spice_file)
from pathlib import Path

"""
TODO: вместо .txt использовать .csv
"""

# =============================== PROJECT PATHS ===============================
PROJECT_PATH = Path(__file__).resolve().parent  # корневой путь проекта

IGNORE_PARAMS_FILE = PROJECT_PATH / "data" / "ignore_params.txt"
MODEL_CODE_PATH = PROJECT_PATH / "data" / "code"
SPICE_EXAMPLES_PATH = PROJECT_PATH / "data" / "examples"

# =============================== CREATE DIRECTORIES ===============================
OSDILIBS_PATH = PROJECT_PATH / "data" / "osdilibs"
SIMULATION_RAW_DATA_PATH = PROJECT_PATH / "data" / "raw"
PICS_PATH = PROJECT_PATH / "pics"
REFERENCE_MODEL_CODE_PATH = PROJECT_PATH / "data" / "reference"

DIRECTORY = [REFERENCE_MODEL_CODE_PATH, SIMULATION_RAW_DATA_PATH, PICS_PATH, OSDILIBS_PATH]

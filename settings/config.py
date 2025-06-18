from typing import List, Union, Dict

from .model import Config, Model


config = Config()

MODEL_CONFIGS: Dict[str, Model] = {
    "BJT505": Model(
        model=config.model_code_dir / "mextram" / "vacode" / "bjt505.va",
        spice=config.spice_dir / "mextram" / "ngspice" / "npn_ic_ib_is_vb.sp",
        parameters=config.model_code_dir / "mextram" / "vacode" / "parameters.inc",
    ),
    "ASMHEMT": Model(
        model=config.model_code_dir / "ASMHEMT" / "vacode" / "asmhemt.va",
        spice=config.spice_dir / "ASMHEMT" / "nfet_id_vd_vg.sp",
        parameters=config.model_code_dir / "ASMHEMT" / "vacode" / "asmhemt.va",
    ),
}

DIRECTORY: List[config] = [
    config.reference_dir,
    config.simulation_raw_data_path,
    config.output_data_dir,
    config.pics_path,
]

INITIAL_LOG_SCALE: Union[bool] = False
INITIAL_GRID: Union[bool] = True

from pathlib import Path
from pydantic import BaseModel, Field


class Config(BaseModel):
    root_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent)
    osdilibs_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "data" / "osdilibs"
    )
    ignore_params_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent
        / "data"
        / "ignore_params.txt"
    )
    simulation_raw_data_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "data" / "raw"
    )
    model_code_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "data" / "code"
    )
    spice_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "data" / "examples"
    )
    reference_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "data" / "reference"
    )
    pics_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "pics"
    )
    output_data_dir: Path = Field(
        default_factory=lambda: Path.home() / "Documents" / "SimulationResults"
    )


class Model(Config):
    model: Path
    spice: Path
    parameters: Path

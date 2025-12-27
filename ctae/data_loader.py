"""Utility functions for loading data from CSV files."""
import os
import pandas as pd
from typing import Dict

# Cache for loaded data
_DATA_CACHE: Dict[str, pd.DataFrame] = {}


def get_data_path(filename: str) -> str:
    """Get the full path to a data file."""
    return os.path.join(os.path.dirname(__file__), "data", filename)


def load_parameters_lambert_ung() -> pd.DataFrame:
    """Load Lambert & Ung parameters."""
    if "lambert_ung" not in _DATA_CACHE:
        _DATA_CACHE["lambert_ung"] = pd.read_csv(
            get_data_path("parameters_LambertUng.csv")
        )
    return _DATA_CACHE["lambert_ung"]


def load_parameters_huang() -> pd.DataFrame:
    """Load Huang parameters."""
    if "huang" not in _DATA_CACHE:
        _DATA_CACHE["huang"] = pd.read_csv(get_data_path("parameters_HuangV.csv"))
    return _DATA_CACHE["huang"]


def load_parameters_v2b() -> Dict[str, pd.DataFrame]:
    """Load V2B parameters (returns a dictionary of dataframes)."""
    if "v2b" not in _DATA_CACHE:
        _DATA_CACHE["v2b"] = {
            "t3": pd.read_csv(get_data_path("parameters_V2B_t3.csv")),
            "t4": pd.read_csv(get_data_path("parameters_V2B_t4.csv")),
            "t5": pd.read_csv(get_data_path("parameters_V2B_t5.csv")),
            "t6_vol": pd.read_csv(get_data_path("parameters_V2B_t6_vol.csv")),
            "t6_bio": pd.read_csv(get_data_path("parameters_V2B_t6_bio.csv")),
            "t7_vol": pd.read_csv(get_data_path("parameters_V2B_t7_vol.csv")),
            "t7_bio": pd.read_csv(get_data_path("parameters_V2B_t7_bio.csv")),
        }
    return _DATA_CACHE["v2b"]


def load_params_vtot2vmerch() -> pd.DataFrame:
    """Load Vtot2Vmerch parameters."""
    if "vtot2vmerch" not in _DATA_CACHE:
        _DATA_CACHE["vtot2vmerch"] = pd.read_csv(
            get_data_path("params_Vtot2Vmerch.csv")
        )
    return _DATA_CACHE["vtot2vmerch"]


def load_codes_ecozones() -> pd.DataFrame:
    """Load ecozone codes."""
    if "ecozones" not in _DATA_CACHE:
        _DATA_CACHE["ecozones"] = pd.read_csv(get_data_path("CodesEcozones.csv"))
    return _DATA_CACHE["ecozones"]


def load_alberta_natural_subregions() -> pd.DataFrame:
    """Load Alberta natural subregion codes."""
    if "alberta_subregions" not in _DATA_CACHE:
        _DATA_CACHE["alberta_subregions"] = pd.read_csv(
            get_data_path("AlbertaNaturalRegSubreg.csv")
        )
    return _DATA_CACHE["alberta_subregions"]


def load_parameters_ung2009() -> Dict[str, pd.DataFrame]:
    """Load Ung2009 growth model parameters (Nat1 and Nat2 models)."""
    if "ung2009" not in _DATA_CACHE:
        _DATA_CACHE["ung2009"] = {
            "nat1": pd.read_csv(get_data_path("ung2009_nat1.csv")),
            "nat2": pd.read_csv(get_data_path("ung2009_nat2.csv")),
        }
    return _DATA_CACHE["ung2009"]

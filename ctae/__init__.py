"""
CTAE - Canadian Tree Allometric Equations

A collection of tools to calculate tree- or stand-level attributes
developed for Canadian forests.

Core Functions:
    - AGB_LambertUngDBH: Calculate tree-level AGB using DBH
    - AGB_LambertUngDBHHT: Calculate tree-level AGB using DBH and height
    - V_Huang: Calculate individual tree volume for Alberta species
    - V2B: Volume-to-biomass conversion
    - Vtot2Vmerch: Total volume to merchantable volume conversion
    - AGB_prop: Calculate AGB proportions for tree organs
    - Ung2009: Growth and yield model

Urban Ecosystem Services:
    - estimate_canopy_area: Estimate tree canopy area
    - estimate_stormwater_interception: Calculate stormwater benefits
    - estimate_cooling_savings: Calculate cooling energy savings
    - estimate_pollution_removal: Calculate air pollution removal
    - estimate_total_value: Calculate total ecosystem service value
    - estimate_values_for_dataframe: Batch process multiple trees

Validation:
    - validation: Input validation utilities (ctae.validation module)
"""

from .agb_lambert_ung import AGB_LambertUngDBH, AGB_LambertUngDBHHT
from .v_huang import V_Huang
from .v2b import V2B
from .vtot2vmerch import Vtot2Vmerch
from .agb_prop import AGB_prop
from .ung2009 import Ung2009
from .services import (
    estimate_canopy_area,
    estimate_stormwater_interception,
    estimate_cooling_savings,
    estimate_pollution_removal,
    estimate_total_value,
    estimate_values_for_dataframe,
)
from . import validation

__version__ = "0.4.4"

__all__ = [
    "AGB_LambertUngDBH",
    "AGB_LambertUngDBHHT",
    "V_Huang",
    "V2B",
    "Vtot2Vmerch",
    "AGB_prop",
    "Ung2009",
    "estimate_canopy_area",
    "estimate_stormwater_interception",
    "estimate_cooling_savings",
    "estimate_pollution_removal",
    "estimate_total_value",
    "estimate_values_for_dataframe",
    "validation",
]

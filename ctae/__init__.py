"""
CTAE - Canadian Tree Allometric Equations

A collection of tools to calculate tree- or stand-level attributes
developed for Canadian forests.
"""

from .agb_lambert_ung import AGB_LambertUngDBH, AGB_LambertUngDBHHT
from .v_huang import V_Huang
from .v2b import V2B
from .vtot2vmerch import Vtot2Vmerch
from .agb_prop import AGB_prop
from .ung2009 import Ung2009

__version__ = "0.4.3"

__all__ = [
    "AGB_LambertUngDBH",
    "AGB_LambertUngDBHHT",
    "V_Huang",
    "V2B",
    "Vtot2Vmerch",
    "AGB_prop",
    "Ung2009",
]

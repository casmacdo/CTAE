"""
CTAE - Canadian Tree Allometric Equations

A collection of tools to calculate tree- or stand-level attributes
developed for Canadian forests.

Core Biomass & Volume Functions:
    - AGB_LambertUngDBH: Calculate tree-level AGB using DBH
    - AGB_LambertUngDBHHT: Calculate tree-level AGB using DBH and height
    - V_Huang: Calculate individual tree volume for Alberta species
    - V2B: Volume-to-biomass conversion
    - Vtot2Vmerch: Total volume to merchantable volume conversion
    - AGB_prop: Calculate AGB proportions for tree organs
    - Ung2009: Growth and yield model

Carbon Accounting (ctae.carbon):
    - biomass_to_carbon: Convert biomass to carbon content
    - carbon_to_co2e: Convert carbon to CO2 equivalent
    - biomass_to_co2e: Direct biomass to CO2e conversion
    - calculate_carbon_stock: Full carbon stock calculation
    - volume_to_carbon: Volume to carbon (convenience function)
    - project_carbon_flux: Project carbon over time from growth model

Utilities (ctae.utils):
    - basal_area: Calculate tree basal area
    - tree_summary: Comprehensive single-tree summary
    - estimate_height_from_dbh: Height estimation from DBH
    - aggregate_to_stand: Aggregate trees to stand-level metrics
    - loreys_height: Calculate Lorey's mean height

Inventory Processing (ctae.inventory):
    - process_inventory: Batch process tree inventory
    - inventory_carbon_summary: Summarize inventory carbon
    - generate_carbon_report: Generate carbon reports
    - validate_inventory: Validate inventory data

Urban Ecosystem Services:
    - estimate_canopy_area: Estimate tree canopy area
    - estimate_stormwater_interception: Calculate stormwater benefits
    - estimate_cooling_savings: Calculate cooling energy savings
    - estimate_pollution_removal: Calculate air pollution removal
    - estimate_total_value: Calculate total ecosystem service value
    - estimate_values_for_dataframe: Batch process multiple trees

Validation (ctae.validation):
    - validate_dbh, validate_height, validate_age
    - validate_species_code, validate_jurisdiction, validate_ecozone
"""

# Core functions
from .agb_lambert_ung import AGB_LambertUngDBH, AGB_LambertUngDBHHT
from .v_huang import V_Huang
from .v2b import V2B
from .vtot2vmerch import Vtot2Vmerch
from .agb_prop import AGB_prop
from .ung2009 import Ung2009

# Ecosystem services
from .services import (
    estimate_canopy_area,
    estimate_stormwater_interception,
    estimate_cooling_savings,
    estimate_pollution_removal,
    estimate_total_value,
    estimate_values_for_dataframe,
)

# Carbon accounting
from .carbon import (
    biomass_to_carbon,
    carbon_to_co2e,
    biomass_to_co2e,
    calculate_carbon_stock,
    calculate_annual_sequestration,
    carbon_value,
    volume_to_carbon,
    project_carbon_flux,
)

# Utilities
from .utils import (
    basal_area,
    basal_area_per_hectare,
    estimate_height_from_dbh,
    stem_volume_quick,
    tree_summary,
    aggregate_to_stand,
    loreys_height,
)

# Inventory processing
from .inventory import (
    process_inventory,
    inventory_carbon_summary,
    generate_carbon_report,
    validate_inventory,
)

# Submodules
from . import validation
from . import carbon
from . import utils
from . import inventory

__version__ = "0.4.5"

__all__ = [
    # Core biomass/volume
    "AGB_LambertUngDBH",
    "AGB_LambertUngDBHHT",
    "V_Huang",
    "V2B",
    "Vtot2Vmerch",
    "AGB_prop",
    "Ung2009",
    # Carbon accounting
    "biomass_to_carbon",
    "carbon_to_co2e",
    "biomass_to_co2e",
    "calculate_carbon_stock",
    "calculate_annual_sequestration",
    "carbon_value",
    "volume_to_carbon",
    "project_carbon_flux",
    # Utilities
    "basal_area",
    "basal_area_per_hectare",
    "estimate_height_from_dbh",
    "stem_volume_quick",
    "tree_summary",
    "aggregate_to_stand",
    "loreys_height",
    # Inventory
    "process_inventory",
    "inventory_carbon_summary",
    "generate_carbon_report",
    "validate_inventory",
    # Ecosystem services
    "estimate_canopy_area",
    "estimate_stormwater_interception",
    "estimate_cooling_savings",
    "estimate_pollution_removal",
    "estimate_total_value",
    "estimate_values_for_dataframe",
    # Submodules
    "validation",
    "carbon",
    "utils",
    "inventory",
]

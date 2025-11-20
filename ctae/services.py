"""
ctae/services.py

Module: urban ecosystem services estimators to augment CTAE biomass outputs.
Provides:
- estimate_canopy_area
- estimate_stormwater_interception
- estimate_cooling_savings
- estimate_pollution_removal
- estimate_total_value
- estimate_values_for_dataframe

Assumes CTAE is available as `ctae` module with function:
  ctae.AGB_LambertUngDBH(DBH=<cm>, species=<ctae_code>) -> dict with 'Btotal' kg

Add this file to the CTAE package and import in examples or CLI.
"""
from typing import Dict, Tuple, Optional, Any
import math
import json
import os
import pandas as pd

# --- Defaults and a tiny starter species lookup (expand for production) ---
DEFAULTS = {
    "CARBON_PRICE_USD_PER_TON": 75.0,
    "STORMWATER_COST_USD_PER_M3": 1.0,
    "ELECTRICITY_RATE_USD_PER_KWH": 0.10,
    "ANNUAL_RAINFALL_MM": 1000.0,
    "CANOPY_MIN_AREA_M2": 1.0,
    "GENERIC_CROWN_A": 0.0,   # intercept (m)
    "GENERIC_CROWN_B": 0.35,  # slope (m per cm DBH)
    "GENERIC_MAX_RADIUS_M": 12.0,
    "DEFAULT_INTERCEPTION_RATE": 0.25,
    "BASE_KWH_PER_M2": 0.4
}

# Load species lookup from JSON file
def _load_species_lookup() -> Dict[str, Dict[str, Any]]:
    """Load species lookup data from JSON file."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    json_path = os.path.join(data_dir, 'species_lookup.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return empty dict if file not found, will use defaults
        return {}

SPECIES_LOOKUP: Dict[str, Dict[str, Any]] = _load_species_lookup()

# --- Helpers -----------------------------------------------------------------
def _get_species_props(species: Optional[str]) -> Dict[str, Any]:
    if species and species in SPECIES_LOOKUP:
        return SPECIES_LOOKUP[species]
    return {
        "crown_a": DEFAULTS["GENERIC_CROWN_A"],
        "crown_b": DEFAULTS["GENERIC_CROWN_B"],
        "max_radius_m": DEFAULTS["GENERIC_MAX_RADIUS_M"],
        "interception_rate": DEFAULTS["DEFAULT_INTERCEPTION_RATE"],
        "leaf_type": "unknown"
    }

# --- Core functions ----------------------------------------------------------
def estimate_canopy_area(DBH_cm: float, species: Optional[str] = None) -> Tuple[float, str]:
    """
    Estimate canopy area (m^2) from DBH in cm and species.
    Returns (canopy_area_m2, method_used) where method_used is 'species' or 'generic'.
    Uses linear crown diameter model: crown_d = a + b * DBH_cm, area = pi * (r^2)
    """
    if DBH_cm is None or DBH_cm <= 0:
        return 0.0, "invalid_dbh"

    props = _get_species_props(species)
    crown_a = props.get("crown_a", DEFAULTS["GENERIC_CROWN_A"])
    crown_b = props.get("crown_b", DEFAULTS["GENERIC_CROWN_B"])
    max_r = props.get("max_radius_m", DEFAULTS["GENERIC_MAX_RADIUS_M"])

    crown_d_m = crown_a + crown_b * DBH_cm
    crown_r_m = min(crown_d_m / 2.0, max_r)
    canopy_area = math.pi * crown_r_m * crown_r_m
    canopy_area = max(canopy_area, DEFAULTS["CANOPY_MIN_AREA_M2"])

    method = "species" if species and species in SPECIES_LOOKUP else "generic"
    return canopy_area, method

def estimate_stormwater_interception(canopy_area_m2: float,
                                    annual_rainfall_mm: Optional[float] = None,
                                    interception_rate: Optional[float] = None,
                                    species: Optional[str] = None,
                                    stormwater_cost_per_m3: Optional[float] = None) -> Tuple[float, float]:
    """
    Estimate annual intercepted volume (m^3) and monetary value ($).
    Volume = canopy_area_m2 * (annual_rainfall_mm / 1000) * interception_rate
    """
    if canopy_area_m2 <= 0:
        return 0.0, 0.0

    annual_rainfall_mm = annual_rainfall_mm if annual_rainfall_mm is not None else DEFAULTS["ANNUAL_RAINFALL_MM"]
    if interception_rate is None:
        props = _get_species_props(species)
        interception_rate = props.get("interception_rate", DEFAULTS["DEFAULT_INTERCEPTION_RATE"])
    interception_rate = max(0.0, min(1.0, interception_rate))

    stormwater_cost_per_m3 = stormwater_cost_per_m3 if stormwater_cost_per_m3 is not None else DEFAULTS["STORMWATER_COST_USD_PER_M3"]

    volume_m3 = canopy_area_m2 * (annual_rainfall_mm / 1000.0) * interception_rate
    value_usd = volume_m3 * stormwater_cost_per_m3
    return volume_m3, value_usd

def estimate_cooling_savings(canopy_area_m2: float,
                             proximity_factor: float = 1.0,
                             base_kwh_per_m2: Optional[float] = None,
                             electricity_rate: Optional[float] = None) -> Tuple[float, float]:
    """
    Estimate annual kWh saved and $ value due to shading/evapotranspiration.
    kWh = canopy_area_m2 * base_kwh_per_m2 * proximity_factor
    """
    if canopy_area_m2 <= 0:
        return 0.0, 0.0

    base_kwh_per_m2 = base_kwh_per_m2 if base_kwh_per_m2 is not None else DEFAULTS["BASE_KWH_PER_M2"]
    electricity_rate = electricity_rate if electricity_rate is not None else DEFAULTS["ELECTRICITY_RATE_USD_PER_KWH"]

    annual_kwh = canopy_area_m2 * base_kwh_per_m2 * max(0.0, proximity_factor)
    value_usd = annual_kwh * electricity_rate
    return annual_kwh, value_usd

def estimate_pollution_removal(canopy_area_m2: float,
                               removal_rates: Optional[Dict[str, float]] = None,
                               values_per_kg: Optional[Dict[str, float]] = None) -> Tuple[Dict[str, float], float]:
    """
    Estimate pollutant mass removed per year (kg) and total monetary value ($).
    removal_rates: dict e.g., {"PM2.5": 0.001, "NO2": 0.0002} (kg per m2 per year)
    values_per_kg: monetary values per pollutant kg removed
    Returns (totals_by_pollutant, total_value_usd)
    """
    if canopy_area_m2 <= 0:
        return {}, 0.0

    default_removal = {"PM2.5": 0.001, "NO2": 0.0002}
    default_values = {"PM2.5": 50.0, "NO2": 5.0}

    removal_rates = removal_rates if removal_rates is not None else default_removal
    values_per_kg = values_per_kg if values_per_kg is not None else default_values

    totals: Dict[str, float] = {}
    total_value = 0.0
    for pollutant, rate in removal_rates.items():
        mass_kg = canopy_area_m2 * rate
        value = mass_kg * values_per_kg.get(pollutant, 0.0)
        totals[pollutant] = mass_kg
        total_value += value

    return totals, total_value

# --- Orchestrator -----------------------------------------------------------
def estimate_total_value(tree_row: Dict[str, Any],
                         ctae_module,
                         params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Orchestrate per-tree ecosystem service valuation.
    tree_row: mapping with keys at least 'DHP' (DBH in cm) and 'Essence_latin' (species).
    ctae_module: imported CTAE module providing biomass estimator, e.g. ctae.AGB_LambertUngDBH
    params: overrides for defaults (carbon_price, rainfall, costs, etc.)

    Returns dict with detailed breakdown and assumptions.
    """
    params = params or {}
    carbon_price = params.get("carbon_price", DEFAULTS["CARBON_PRICE_USD_PER_TON"])
    stormwater_cost = params.get("stormwater_cost", DEFAULTS["STORMWATER_COST_USD_PER_M3"])
    electricity_rate = params.get("electricity_rate", DEFAULTS["ELECTRICITY_RATE_USD_PER_KWH"])
    annual_rainfall_mm = params.get("annual_rainfall_mm", DEFAULTS["ANNUAL_RAINFALL_MM"])
    proximity_factor = params.get("proximity_factor", 1.0)
    base_kwh_per_m2 = params.get("base_kwh_per_m2", DEFAULTS["BASE_KWH_PER_M2"])
    removal_rates = params.get("removal_rates", None)
    values_per_kg = params.get("values_per_kg", None)

    # Input extraction and validation
    try:
        DBH_cm = float(tree_row.get("DHP", tree_row.get("DBH", 0.0)))
    except Exception:
        DBH_cm = 0.0
    species = tree_row.get("Essence_latin", tree_row.get("species", None))

    # CTAE biomass: expect dict with 'Btotal' in kg
    ctae_species_code = params.get("map_species_to_ctae", lambda s: s)(species)
    biomass_kg = 0.0
    if DBH_cm > 0:
        try:
            agb = ctae_module.AGB_LambertUngDBH(DBH=DBH_cm, species=ctae_species_code)
            biomass_kg = float(agb.get("Btotal", agb.get("BTotal", 0.0)))
        except Exception:
            biomass_kg = 0.0

    # Carbon stock (tons C) and value (one-time stock valuation)
    carbon_tons = (biomass_kg * 0.5) / 1000.0
    carbon_value = carbon_tons * carbon_price

    # Canopy area
    canopy_area_m2, canopy_method = estimate_canopy_area(DBH_cm, species)

    # Stormwater
    intercepted_m3, stormwater_value = estimate_stormwater_interception(
        canopy_area_m2=canopy_area_m2,
        annual_rainfall_mm=annual_rainfall_mm,
        species=species,
        stormwater_cost_per_m3=stormwater_cost
    )

    # Cooling
    kwh_saved, cooling_value = estimate_cooling_savings(
        canopy_area_m2=canopy_area_m2,
        proximity_factor=proximity_factor,
        base_kwh_per_m2=base_kwh_per_m2,
        electricity_rate=electricity_rate
    )

    # Pollution
    pollutant_removed, pollution_value = estimate_pollution_removal(
        canopy_area_m2=canopy_area_m2,
        removal_rates=removal_rates,
        values_per_kg=values_per_kg
    )

    total_value = carbon_value + stormwater_value + cooling_value + pollution_value

    return {
        "input": {"DBH_cm": DBH_cm, "species": species},
        "biomass_kg": biomass_kg,
        "carbon_tons": carbon_tons,
        "carbon_value_usd": round(carbon_value, 2),
        "canopy_area_m2": round(canopy_area_m2, 2),
        "canopy_method": canopy_method,
        "intercepted_m3_per_year": round(intercepted_m3, 3),
        "stormwater_value_usd": round(stormwater_value, 2),
        "annual_kwh_saved": round(kwh_saved, 2),
        "cooling_value_usd": round(cooling_value, 2),
        "pollutant_removed_kg": {k: round(v, 6) for k, v in pollutant_removed.items()},
        "pollution_value_usd": round(pollution_value, 2),
        "total_value_usd": round(total_value, 2),
        "assumptions": {
            "carbon_price_usd_per_ton": carbon_price,
            "stormwater_cost_usd_per_m3": stormwater_cost,
            "electricity_rate_usd_per_kwh": electricity_rate,
            "annual_rainfall_mm": annual_rainfall_mm,
            "proximity_factor": proximity_factor,
            "base_kwh_per_m2": base_kwh_per_m2
        }
    }

# --- Batch processing -------------------------------------------------------
def estimate_values_for_dataframe(df: pd.DataFrame,
                                  ctae_module,
                                  params: Optional[Dict[str, Any]] = None,
                                  id_col: str = "ID_Arbre") -> pd.DataFrame:
    """
    Vectorized batch wrapper: runs estimate_total_value on each row.
    Returns a DataFrame with columns appended for the valuation results.
    """
    params = params or {}
    records = []
    for _, row in df.iterrows():
        tree_row = row.to_dict()
        out = estimate_total_value(tree_row, ctae_module, params=params)
        flat = {
            id_col: row.get(id_col),
            "biomass_kg": out["biomass_kg"],
            "carbon_tons": out["carbon_tons"],
            "carbon_value_usd": out["carbon_value_usd"],
            "canopy_area_m2": out["canopy_area_m2"],
            "intercepted_m3_per_year": out["intercepted_m3_per_year"],
            "stormwater_value_usd": out["stormwater_value_usd"],
            "annual_kwh_saved": out["annual_kwh_saved"],
            "cooling_value_usd": out["cooling_value_usd"],
            "pollution_value_usd": out["pollution_value_usd"],
            "total_value_usd": out["total_value_usd"],
            "assumptions": out["assumptions"]
        }
        records.append(flat)
    return pd.DataFrame.from_records(records)

# --- End of file ------------------------------------------------------------

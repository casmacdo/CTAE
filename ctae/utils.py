"""
Utility functions for common forestry calculations.

This module provides convenience functions for:
- Basic forestry metrics (basal area, stem density)
- Tree-level summaries combining multiple calculations
- Height estimation from DBH (allometric relationships)
- Stand-level aggregations
"""
import numpy as np
import pandas as pd
from typing import Union, Dict, Optional, List
import warnings


# Height-DBH allometric parameters by species group
# Based on Canadian literature (Huang et al., Sharma & Parton)
# Format: species_group -> (a, b) for Height = a * DBH^b
HEIGHT_DBH_PARAMS = {
    # Conifers
    "PINU": (1.35, 0.75),  # Pines
    "PICE": (1.25, 0.78),  # Spruces
    "ABIE": (1.30, 0.76),  # Firs
    "TSUG": (1.40, 0.74),  # Hemlocks
    "THUJ": (1.15, 0.80),  # Cedars
    "LARI": (1.45, 0.72),  # Larches
    "PSEU": (1.50, 0.73),  # Douglas-fir
    # Broadleaves
    "POPU": (1.60, 0.68),  # Poplars/Aspens
    "BETU": (1.55, 0.70),  # Birches
    "ACER": (1.45, 0.72),  # Maples
    "QUER": (1.35, 0.75),  # Oaks
    "FAGU": (1.40, 0.73),  # Beech
    "FRAX": (1.50, 0.71),  # Ash
    # Default for unknown
    "DEFAULT": (1.40, 0.73),
}


def basal_area(
    dbh_cm: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """
    Calculate basal area from diameter at breast height.

    Basal area = π × (DBH/2)² in square meters.

    Parameters
    ----------
    dbh_cm : float or array-like
        Diameter at breast height in centimeters.

    Returns
    -------
    float or ndarray
        Basal area in square meters (m²).

    Examples
    --------
    >>> round(basal_area(20), 4)  # 20 cm DBH
    0.0314
    >>> basal_area(np.array([10, 20, 30]))
    array([0.00785398, 0.03141593, 0.07068583])
    """
    dbh_m = np.asarray(dbh_cm) / 100.0
    return np.pi * (dbh_m / 2.0) ** 2


def basal_area_per_hectare(
    dbh_cm: Union[float, np.ndarray, List[float]],
    expansion_factor: Union[float, np.ndarray, List[float]] = 1.0,
) -> float:
    """
    Calculate basal area per hectare from tree measurements.

    Parameters
    ----------
    dbh_cm : float or array-like
        DBH values for individual trees in cm.
    expansion_factor : float or array-like
        Expansion factor for each tree (trees represented per hectare).
        If scalar, applied to all trees.

    Returns
    -------
    float
        Basal area in m²/ha.

    Examples
    --------
    >>> # 5 trees with expansion factor of 200 (fixed-area plot)
    >>> basal_area_per_hectare([20, 25, 30, 35, 40], expansion_factor=200)
    18.849...
    """
    ba = basal_area(dbh_cm)
    ef = np.asarray(expansion_factor)
    return float(np.sum(ba * ef))


def estimate_height_from_dbh(
    dbh_cm: Union[float, np.ndarray],
    species: Optional[str] = None,
    region: str = "boreal",
) -> Union[float, np.ndarray]:
    """
    Estimate tree height from DBH using allometric relationships.

    This is a simplified estimation for cases where height is not measured.
    For accurate calculations, measured heights should be used.

    Parameters
    ----------
    dbh_cm : float or array-like
        Diameter at breast height in cm.
    species : str, optional
        Species code (e.g., "PINU.CON"). If None, uses default parameters.
    region : str
        Forest region: "boreal", "temperate", or "coastal".
        Affects height predictions (coastal trees tend to be taller).

    Returns
    -------
    float or ndarray
        Estimated height in meters.

    Notes
    -----
    Height estimation adds uncertainty to calculations. When possible,
    use measured heights. This function provides estimates based on
    generalized Canadian height-DBH relationships.

    Examples
    --------
    >>> round(estimate_height_from_dbh(20, species="PINU.CON"), 1)
    12.8
    >>> round(estimate_height_from_dbh(40, species="PICE.GLA"), 1)
    21.6
    """
    dbh = np.asarray(dbh_cm)

    # Get species-specific parameters
    if species:
        genus = species.split(".")[0].upper()
        if genus in HEIGHT_DBH_PARAMS:
            a, b = HEIGHT_DBH_PARAMS[genus]
        else:
            a, b = HEIGHT_DBH_PARAMS["DEFAULT"]
            warnings.warn(
                f"No height-DBH parameters for genus '{genus}'. Using default parameters.",
                UserWarning,
            )
    else:
        a, b = HEIGHT_DBH_PARAMS["DEFAULT"]

    # Regional adjustment
    if region == "coastal":
        a *= 1.15  # Coastal trees typically 15% taller
    elif region == "temperate":
        a *= 1.05  # Temperate slightly taller than boreal

    height = a * np.power(dbh, b)

    # Ensure reasonable bounds
    height = np.clip(height, 1.3, 80.0)  # Min 1.3m (breast height), max 80m

    return height


def stem_volume_quick(
    dbh_cm: Union[float, np.ndarray],
    height_m: Optional[Union[float, np.ndarray]] = None,
    species: Optional[str] = None,
    form_factor: float = 0.42,
) -> Union[float, np.ndarray]:
    """
    Quick stem volume estimation using form factor method.

    Volume = BA × Height × Form Factor

    Parameters
    ----------
    dbh_cm : float or array-like
        DBH in centimeters.
    height_m : float or array-like, optional
        Tree height in meters. If None, estimated from DBH.
    species : str, optional
        Species code for height estimation if height not provided.
    form_factor : float
        Form factor (ratio of tree volume to cylinder volume).
        Default 0.42 is typical for many species.

    Returns
    -------
    float or ndarray
        Stem volume in cubic meters (m³).

    Notes
    -----
    This is a quick estimation. For accurate volumes, use V_Huang
    or other taper-based methods.

    Examples
    --------
    >>> round(stem_volume_quick(30, 20), 3)
    0.594
    """
    ba = basal_area(dbh_cm)

    if height_m is None:
        height_m = estimate_height_from_dbh(dbh_cm, species)

    return ba * np.asarray(height_m) * form_factor


def tree_summary(
    dbh_cm: float,
    height_m: Optional[float] = None,
    species: str = "UNKN.SPP",
    jurisdiction: Optional[str] = None,
    ecozone: Optional[int] = None,
    include_ecosystem_services: bool = True,
    carbon_price_per_tonne: float = 75.0,
) -> Dict:
    """
    Generate a comprehensive summary for a single tree.

    Combines biomass, volume, carbon, and ecosystem service calculations.

    Parameters
    ----------
    dbh_cm : float
        Diameter at breast height in cm.
    height_m : float, optional
        Tree height in meters. If None, estimated from DBH.
    species : str
        Species code (e.g., "PINU.CON").
    jurisdiction : str, optional
        Jurisdiction code for V2B calculations.
    ecozone : int, optional
        Ecozone number for V2B calculations.
    include_ecosystem_services : bool
        Whether to include ecosystem service valuations.
    carbon_price_per_tonne : float
        Carbon price for valuation ($/tonne CO2e).

    Returns
    -------
    dict
        Comprehensive tree summary including:
        - dimensions: DBH, height, basal_area
        - biomass: total, wood, bark, branches, foliage (kg)
        - carbon: carbon_kg, co2e_kg
        - volume: estimated volume (m³)
        - value: carbon value, total ecosystem value

    Examples
    --------
    >>> summary = tree_summary(30, 20, species="PINU.CON")
    >>> round(summary['biomass']['total_kg'], 1)
    247.9
    """
    from .agb_lambert_ung import AGB_LambertUngDBH, AGB_LambertUngDBHHT
    from .carbon import calculate_carbon_stock, carbon_value

    result = {
        "input": {
            "dbh_cm": dbh_cm,
            "height_m": height_m,
            "species": species,
        },
        "dimensions": {},
        "biomass": {},
        "carbon": {},
        "volume": {},
        "value": {},
    }

    # Estimate height if not provided
    if height_m is None:
        height_m = float(estimate_height_from_dbh(dbh_cm, species))
        result["input"]["height_m"] = height_m
        result["input"]["height_estimated"] = True
    else:
        result["input"]["height_estimated"] = False

    # Dimensions
    result["dimensions"] = {
        "dbh_cm": dbh_cm,
        "height_m": height_m,
        "basal_area_m2": float(basal_area(dbh_cm)),
    }

    # Biomass calculation
    try:
        if height_m:
            agb = AGB_LambertUngDBHHT(dbh_cm, height_m, species=species)
        else:
            agb = AGB_LambertUngDBH(dbh_cm, species=species)

        result["biomass"] = {
            "total_kg": float(agb["Btotal"]),
            "wood_kg": float(agb["Bwood"]),
            "bark_kg": float(agb["Bbark"]),
            "stem_kg": float(agb["Bstem"]),
            "branches_kg": float(agb["Bbranches"]),
            "foliage_kg": float(agb["Bfoliage"]),
            "crown_kg": float(agb["Bcrown"]),
        }
    except ValueError as e:
        # Species not found, try without species
        agb = AGB_LambertUngDBH(dbh_cm, species=None)
        result["biomass"] = {
            "total_kg": float(agb["Btotal"]),
            "wood_kg": float(agb["Bwood"]),
            "bark_kg": float(agb["Bbark"]),
            "note": f"Used generic parameters: {str(e)}",
        }

    # Carbon calculation
    conifer_genera = ["PINU", "PICE", "ABIE", "TSUG", "THUJ", "PSEU", "LARI"]
    genus = species.split(".")[0].upper() if species else "UNKN"
    is_conifer = genus in conifer_genera

    carbon_stock = calculate_carbon_stock(
        result["biomass"]["total_kg"],
        include_belowground=True,
        is_conifer=is_conifer,
    )

    result["carbon"] = {
        "aboveground_carbon_kg": carbon_stock.aboveground_carbon_kg,
        "belowground_carbon_kg": carbon_stock.belowground_carbon_kg,
        "total_carbon_kg": carbon_stock.total_carbon_kg,
        "total_co2e_kg": carbon_stock.total_co2e_kg,
    }

    # Quick volume estimate
    result["volume"] = {
        "stem_volume_m3": float(stem_volume_quick(dbh_cm, height_m, species)),
    }

    # Carbon value
    result["value"] = {
        "carbon_value_usd": float(
            carbon_value(carbon_stock.total_co2e_kg, carbon_price_per_tonne)
        ),
    }

    # Ecosystem services if requested
    if include_ecosystem_services:
        try:
            from .services import (
                estimate_canopy_area,
                estimate_stormwater_interception,
                estimate_cooling_savings,
                estimate_pollution_removal,
            )

            # Get Latin name for species lookup if possible
            canopy_area, method = estimate_canopy_area(dbh_cm)
            stormwater_vol, stormwater_val = estimate_stormwater_interception(canopy_area)
            cooling_kwh, cooling_val = estimate_cooling_savings(canopy_area)
            pollutants, pollution_val = estimate_pollution_removal(canopy_area)

            result["ecosystem_services"] = {
                "canopy_area_m2": canopy_area,
                "stormwater_intercepted_m3_year": stormwater_vol,
                "stormwater_value_usd_year": stormwater_val,
                "cooling_kwh_saved_year": cooling_kwh,
                "cooling_value_usd_year": cooling_val,
                "pollution_removed_kg": pollutants,
                "pollution_value_usd_year": pollution_val,
            }

            total_annual = stormwater_val + cooling_val + pollution_val
            result["value"]["ecosystem_services_usd_year"] = total_annual
            result["value"]["total_value_usd"] = (
                result["value"]["carbon_value_usd"] + total_annual
            )
        except Exception:
            result["ecosystem_services"] = {"error": "Could not calculate ecosystem services"}

    return result


def aggregate_to_stand(
    tree_data: pd.DataFrame,
    dbh_col: str = "DBH",
    species_col: str = "species",
    expansion_factor_col: Optional[str] = None,
    default_expansion_factor: float = 1.0,
    group_by: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Aggregate tree-level measurements to stand-level metrics.

    Parameters
    ----------
    tree_data : pd.DataFrame
        DataFrame with individual tree measurements.
    dbh_col : str
        Column name for DBH (cm).
    species_col : str
        Column name for species.
    expansion_factor_col : str, optional
        Column name for expansion factors (trees/ha represented).
        If None, uses default_expansion_factor.
    default_expansion_factor : float
        Default expansion factor if column not specified.
    group_by : list of str, optional
        Columns to group by (e.g., ['plot_id', 'year']).

    Returns
    -------
    pd.DataFrame
        Stand-level summary with:
        - trees_per_ha: Stem density
        - basal_area_m2_ha: Basal area per hectare
        - mean_dbh_cm: Arithmetic mean DBH
        - quadratic_mean_dbh_cm: Quadratic mean DBH

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'plot_id': [1, 1, 1, 2, 2],
    ...     'DBH': [20, 25, 30, 35, 40],
    ...     'species': ['PINU.CON'] * 5
    ... })
    >>> result = aggregate_to_stand(df, group_by=['plot_id'])
    """
    df = tree_data.copy()

    # Get expansion factors
    if expansion_factor_col and expansion_factor_col in df.columns:
        ef = df[expansion_factor_col]
    else:
        ef = default_expansion_factor

    # Calculate individual tree basal areas
    df["_ba"] = basal_area(df[dbh_col])
    df["_ef"] = ef
    df["_ba_expanded"] = df["_ba"] * df["_ef"]
    df["_dbh_sq"] = df[dbh_col] ** 2

    # Aggregation function
    def agg_func(group):
        n_trees = len(group)
        trees_per_ha = group["_ef"].sum()
        ba_per_ha = group["_ba_expanded"].sum()
        mean_dbh = group[dbh_col].mean()

        # Quadratic mean DBH (weighted by expansion factor)
        weighted_dbh_sq = (group["_dbh_sq"] * group["_ef"]).sum() / trees_per_ha
        qmd = np.sqrt(weighted_dbh_sq)

        # Dominant species
        species_counts = group[species_col].value_counts()
        dominant_species = species_counts.index[0] if len(species_counts) > 0 else None

        return pd.Series(
            {
                "n_trees_sample": n_trees,
                "trees_per_ha": trees_per_ha,
                "basal_area_m2_ha": ba_per_ha,
                "mean_dbh_cm": mean_dbh,
                "quadratic_mean_dbh_cm": qmd,
                "dominant_species": dominant_species,
            }
        )

    # Group and aggregate
    if group_by:
        result = df.groupby(group_by).apply(agg_func).reset_index()
    else:
        result = agg_func(df).to_frame().T

    return result


def loreys_height(
    heights_m: Union[np.ndarray, List[float]],
    basal_areas_m2: Union[np.ndarray, List[float]],
) -> float:
    """
    Calculate Lorey's mean height (basal area weighted).

    Lorey's height is a weighted average height where larger trees
    contribute more to the mean. It's commonly used in forestry
    for stand-level height characterization.

    Parameters
    ----------
    heights_m : array-like
        Tree heights in meters.
    basal_areas_m2 : array-like
        Tree basal areas in m².

    Returns
    -------
    float
        Lorey's mean height in meters.

    Examples
    --------
    >>> heights = [15, 18, 20, 22, 25]
    >>> dbhs = [20, 25, 30, 35, 40]
    >>> bas = [basal_area(d) for d in dbhs]
    >>> round(loreys_height(heights, bas), 1)
    21.1
    """
    heights = np.asarray(heights_m)
    bas = np.asarray(basal_areas_m2)

    return float(np.sum(heights * bas) / np.sum(bas))

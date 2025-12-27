"""
Carbon accounting utilities for forest carbon stock and flux calculations.

This module provides functions for:
- Converting biomass to carbon and CO2 equivalents
- Calculating carbon sequestration rates
- Projecting carbon fluxes over time
- Standard carbon reporting formats

References:
- IPCC Guidelines for National Greenhouse Gas Inventories (2006)
- Environment Canada Greenhouse Gas Reporting
"""
import numpy as np
import pandas as pd
from typing import Union, Dict, Optional, Tuple
from dataclasses import dataclass


# Carbon accounting constants
CARBON_FRACTION = 0.5  # Fraction of biomass that is carbon (IPCC default)
CO2_TO_C_RATIO = 44.0 / 12.0  # ~3.667 - molecular weight ratio
ROOT_TO_SHOOT_RATIO_CONIFER = 0.29  # IPCC default for temperate/boreal conifers
ROOT_TO_SHOOT_RATIO_BROADLEAF = 0.26  # IPCC default for temperate broadleaf


@dataclass
class CarbonStock:
    """Container for carbon stock values in various pools."""

    aboveground_biomass_kg: float
    aboveground_carbon_kg: float
    aboveground_co2e_kg: float
    belowground_carbon_kg: Optional[float] = None
    total_carbon_kg: Optional[float] = None
    total_co2e_kg: Optional[float] = None

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "aboveground_biomass_kg": self.aboveground_biomass_kg,
            "aboveground_carbon_kg": self.aboveground_carbon_kg,
            "aboveground_co2e_kg": self.aboveground_co2e_kg,
            "belowground_carbon_kg": self.belowground_carbon_kg,
            "total_carbon_kg": self.total_carbon_kg,
            "total_co2e_kg": self.total_co2e_kg,
        }

    def to_tonnes(self) -> Dict[str, float]:
        """Convert all values to tonnes."""
        d = self.to_dict()
        return {k: v / 1000.0 if v is not None else None for k, v in d.items()}


def biomass_to_carbon(
    biomass_kg: Union[float, np.ndarray],
    carbon_fraction: float = CARBON_FRACTION,
) -> Union[float, np.ndarray]:
    """
    Convert biomass to carbon content.

    Parameters
    ----------
    biomass_kg : float or array-like
        Biomass in kg (or tonnes, units preserved).
    carbon_fraction : float
        Fraction of biomass that is carbon. Default is 0.5 (IPCC).

    Returns
    -------
    float or ndarray
        Carbon content in same units as input.

    Examples
    --------
    >>> biomass_to_carbon(100)  # 100 kg biomass
    50.0
    >>> biomass_to_carbon(np.array([100, 200, 300]))
    array([ 50., 100., 150.])
    """
    return np.asarray(biomass_kg) * carbon_fraction


def carbon_to_co2e(
    carbon_kg: Union[float, np.ndarray],
) -> Union[float, np.ndarray]:
    """
    Convert carbon to CO2 equivalent.

    Uses the molecular weight ratio of CO2 to C (44/12 = 3.667).

    Parameters
    ----------
    carbon_kg : float or array-like
        Carbon content in kg (or tonnes, units preserved).

    Returns
    -------
    float or ndarray
        CO2 equivalent in same units as input.

    Examples
    --------
    >>> carbon_to_co2e(50)  # 50 kg carbon
    183.33333333333334
    >>> round(carbon_to_co2e(1), 2)  # 1 tonne C = 3.67 tonnes CO2e
    3.67
    """
    return np.asarray(carbon_kg) * CO2_TO_C_RATIO


def biomass_to_co2e(
    biomass_kg: Union[float, np.ndarray],
    carbon_fraction: float = CARBON_FRACTION,
) -> Union[float, np.ndarray]:
    """
    Convert biomass directly to CO2 equivalent.

    Parameters
    ----------
    biomass_kg : float or array-like
        Biomass in kg (or tonnes, units preserved).
    carbon_fraction : float
        Fraction of biomass that is carbon. Default is 0.5.

    Returns
    -------
    float or ndarray
        CO2 equivalent in same units as input.

    Examples
    --------
    >>> round(biomass_to_co2e(100), 2)  # 100 kg biomass
    183.33
    """
    carbon = biomass_to_carbon(biomass_kg, carbon_fraction)
    return carbon_to_co2e(carbon)


def calculate_root_biomass(
    aboveground_biomass_kg: Union[float, np.ndarray],
    is_conifer: bool = True,
    root_to_shoot_ratio: Optional[float] = None,
) -> Union[float, np.ndarray]:
    """
    Estimate belowground (root) biomass from aboveground biomass.

    Uses IPCC default root-to-shoot ratios for temperate/boreal forests.

    Parameters
    ----------
    aboveground_biomass_kg : float or array-like
        Aboveground biomass in kg.
    is_conifer : bool
        True for coniferous species, False for broadleaf/deciduous.
    root_to_shoot_ratio : float, optional
        Custom root-to-shoot ratio. If None, uses IPCC defaults.

    Returns
    -------
    float or ndarray
        Belowground biomass in kg.

    Examples
    --------
    >>> calculate_root_biomass(100, is_conifer=True)  # Conifer
    29.0
    >>> calculate_root_biomass(100, is_conifer=False)  # Broadleaf
    26.0
    """
    if root_to_shoot_ratio is None:
        root_to_shoot_ratio = (
            ROOT_TO_SHOOT_RATIO_CONIFER if is_conifer else ROOT_TO_SHOOT_RATIO_BROADLEAF
        )

    return np.asarray(aboveground_biomass_kg) * root_to_shoot_ratio


def calculate_carbon_stock(
    aboveground_biomass_kg: Union[float, np.ndarray],
    include_belowground: bool = True,
    is_conifer: bool = True,
    carbon_fraction: float = CARBON_FRACTION,
    root_to_shoot_ratio: Optional[float] = None,
) -> Union[CarbonStock, Dict[str, np.ndarray]]:
    """
    Calculate complete carbon stock from aboveground biomass.

    Parameters
    ----------
    aboveground_biomass_kg : float or array-like
        Aboveground biomass in kg.
    include_belowground : bool
        Whether to estimate belowground (root) carbon.
    is_conifer : bool
        True for coniferous species, False for broadleaf.
    carbon_fraction : float
        Fraction of biomass that is carbon.
    root_to_shoot_ratio : float, optional
        Custom root-to-shoot ratio.

    Returns
    -------
    CarbonStock or dict
        Carbon stock values. Returns CarbonStock for scalar input,
        dict of arrays for array input.

    Examples
    --------
    >>> stock = calculate_carbon_stock(100, is_conifer=True)
    >>> round(stock.total_co2e_kg, 1)
    236.5
    """
    agb = np.asarray(aboveground_biomass_kg)
    agc = biomass_to_carbon(agb, carbon_fraction)
    ag_co2e = carbon_to_co2e(agc)

    if include_belowground:
        bgb = calculate_root_biomass(agb, is_conifer, root_to_shoot_ratio)
        bgc = biomass_to_carbon(bgb, carbon_fraction)
        total_c = agc + bgc
        total_co2e = carbon_to_co2e(total_c)
    else:
        bgc = None
        total_c = agc
        total_co2e = ag_co2e

    # Return CarbonStock for scalar, dict for array
    if np.ndim(aboveground_biomass_kg) == 0:
        return CarbonStock(
            aboveground_biomass_kg=float(agb),
            aboveground_carbon_kg=float(agc),
            aboveground_co2e_kg=float(ag_co2e),
            belowground_carbon_kg=float(bgc) if bgc is not None else None,
            total_carbon_kg=float(total_c),
            total_co2e_kg=float(total_co2e),
        )
    else:
        return {
            "aboveground_biomass_kg": agb,
            "aboveground_carbon_kg": agc,
            "aboveground_co2e_kg": ag_co2e,
            "belowground_carbon_kg": bgc,
            "total_carbon_kg": total_c,
            "total_co2e_kg": total_co2e,
        }


def calculate_annual_sequestration(
    biomass_year1_kg: Union[float, np.ndarray],
    biomass_year2_kg: Union[float, np.ndarray],
    years: float = 1.0,
    include_belowground: bool = True,
    is_conifer: bool = True,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate annual carbon sequestration rate from biomass change.

    Parameters
    ----------
    biomass_year1_kg : float or array-like
        Biomass at start of period (kg).
    biomass_year2_kg : float or array-like
        Biomass at end of period (kg).
    years : float
        Number of years between measurements.
    include_belowground : bool
        Include belowground carbon in calculations.
    is_conifer : bool
        True for coniferous species.

    Returns
    -------
    dict
        Dictionary containing:
        - biomass_increment_kg_per_year: Annual biomass growth
        - carbon_sequestration_kg_per_year: Annual carbon sequestered
        - co2e_sequestration_kg_per_year: Annual CO2e sequestered

    Examples
    --------
    >>> result = calculate_annual_sequestration(100, 150, years=5)
    >>> round(result['carbon_sequestration_kg_per_year'], 2)
    6.45
    """
    biomass_increment = (np.asarray(biomass_year2_kg) - np.asarray(biomass_year1_kg)) / years

    if include_belowground:
        root_increment = calculate_root_biomass(biomass_increment, is_conifer)
        total_increment = biomass_increment + root_increment
    else:
        total_increment = biomass_increment

    carbon_seq = biomass_to_carbon(total_increment)
    co2e_seq = carbon_to_co2e(carbon_seq)

    return {
        "biomass_increment_kg_per_year": biomass_increment,
        "carbon_sequestration_kg_per_year": carbon_seq,
        "co2e_sequestration_kg_per_year": co2e_seq,
    }


def carbon_value(
    co2e_kg: Union[float, np.ndarray],
    price_per_tonne: float = 75.0,
) -> Union[float, np.ndarray]:
    """
    Calculate the monetary value of carbon stock or sequestration.

    Parameters
    ----------
    co2e_kg : float or array-like
        CO2 equivalent in kg.
    price_per_tonne : float
        Carbon price in currency units per tonne CO2e.
        Default is $75 USD/tonne (current voluntary market).

    Returns
    -------
    float or ndarray
        Value in currency units.

    Examples
    --------
    >>> carbon_value(1000)  # 1 tonne CO2e at $75/tonne
    75.0
    >>> carbon_value(3667)  # ~1 tonne C at $75/tonne
    274.975
    """
    tonnes = np.asarray(co2e_kg) / 1000.0
    return tonnes * price_per_tonne


def project_carbon_flux(
    growth_model_output: pd.DataFrame,
    volume_col: str = "V",
    age_col: str = "age",
    species: str = None,
    jurisdiction: str = None,
    ecozone: int = None,
    is_conifer: bool = True,
    include_belowground: bool = True,
) -> pd.DataFrame:
    """
    Project carbon flux from growth model output.

    Takes output from Ung2009 (or similar) and calculates carbon metrics.

    Parameters
    ----------
    growth_model_output : pd.DataFrame
        DataFrame with volume projections (e.g., from Ung2009).
    volume_col : str
        Column name for volume (m3/ha).
    age_col : str
        Column name for age.
    species : str, optional
        Species code for V2B conversion.
    jurisdiction : str, optional
        Jurisdiction code for V2B conversion.
    ecozone : int, optional
        Ecozone number for V2B conversion.
    is_conifer : bool
        True for coniferous species.
    include_belowground : bool
        Include belowground carbon.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with added carbon columns:
        - carbon_stock_tonnes_ha: Total carbon stock
        - co2e_stock_tonnes_ha: Total CO2e stock
        - annual_sequestration_co2e: Annual CO2e sequestration rate
        - cumulative_sequestration_co2e: Cumulative sequestration

    Notes
    -----
    If species/jurisdiction/ecozone not provided, uses a simple
    biomass expansion factor of 0.7 tonnes biomass per m3 volume.

    Examples
    --------
    >>> import ctae
    >>> growth = ctae.Ung2009("PINU.CON", age=range(1, 51), GDD=1500, PREC=800)
    >>> carbon_df = project_carbon_flux(growth, is_conifer=True)
    """
    df = growth_model_output.copy()

    # Get volume
    volume = df[volume_col].values

    # Convert volume to biomass
    if species and jurisdiction and ecozone:
        # Use full V2B model if parameters provided
        from .v2b import V2B

        try:
            v2b_result = V2B(volume, species=species, jurisdiction=jurisdiction, ecozone=ecozone)
            biomass_tonnes_ha = v2b_result["b_total"]
        except Exception:
            # Fallback to expansion factor
            biomass_tonnes_ha = volume * 0.7
    else:
        # Use simple biomass expansion factor
        # Typical range: 0.5-0.9 tonnes/m3 depending on species
        biomass_tonnes_ha = volume * 0.7

    # Calculate carbon stock
    carbon_tonnes = biomass_to_carbon(biomass_tonnes_ha * 1000) / 1000  # tonnes

    if include_belowground:
        root_biomass = calculate_root_biomass(biomass_tonnes_ha * 1000, is_conifer) / 1000
        root_carbon = biomass_to_carbon(root_biomass * 1000) / 1000
        total_carbon = carbon_tonnes + root_carbon
    else:
        total_carbon = carbon_tonnes

    co2e_tonnes = carbon_to_co2e(total_carbon)

    # Calculate annual sequestration (difference from previous year)
    annual_seq = np.zeros_like(co2e_tonnes)
    annual_seq[1:] = np.diff(co2e_tonnes)
    annual_seq[0] = co2e_tonnes[0]  # First year is the initial stock

    # Cumulative sequestration
    cumulative_seq = np.cumsum(annual_seq)

    # Add to DataFrame
    df["biomass_tonnes_ha"] = biomass_tonnes_ha
    df["carbon_stock_tonnes_ha"] = total_carbon
    df["co2e_stock_tonnes_ha"] = co2e_tonnes
    df["annual_sequestration_co2e"] = annual_seq
    df["cumulative_sequestration_co2e"] = cumulative_seq

    return df


def volume_to_carbon(
    volume_m3_ha: Union[float, np.ndarray],
    species: str,
    jurisdiction: str,
    ecozone: int,
    include_belowground: bool = True,
    is_conifer: Optional[bool] = None,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Convert volume directly to carbon stock (convenience function).

    Chains V2B biomass conversion with carbon calculations.

    Parameters
    ----------
    volume_m3_ha : float or array-like
        Gross merchantable volume per hectare (m3/ha).
    species : str
        Species code (e.g., "PINU.CON").
    jurisdiction : str
        Jurisdiction code (e.g., "BC").
    ecozone : int
        Ecozone number (1-15).
    include_belowground : bool
        Include belowground (root) carbon.
    is_conifer : bool, optional
        True for conifer, False for broadleaf. If None, inferred from species.

    Returns
    -------
    dict
        Dictionary with carbon metrics:
        - biomass_tonnes_ha: Total aboveground biomass
        - carbon_tonnes_ha: Total carbon stock
        - co2e_tonnes_ha: Total CO2 equivalent

    Examples
    --------
    >>> result = volume_to_carbon(350, "PINU.CON", "BC", 4)
    >>> round(result['co2e_tonnes_ha'], 1)
    390.2
    """
    from .v2b import V2B

    # Get biomass from V2B
    v2b_result = V2B(volume_m3_ha, species=species, jurisdiction=jurisdiction, ecozone=ecozone)
    biomass_tonnes = v2b_result["b_total"]

    # Infer conifer status from species if not provided
    if is_conifer is None:
        conifer_genera = ["PINU", "PICE", "ABIE", "TSUG", "THUJ", "PSEU", "LARI"]
        genus = species.split(".")[0].upper()
        is_conifer = genus in conifer_genera

    # Calculate carbon
    biomass_kg = np.asarray(biomass_tonnes) * 1000
    stock = calculate_carbon_stock(
        biomass_kg,
        include_belowground=include_belowground,
        is_conifer=is_conifer,
    )

    if isinstance(stock, CarbonStock):
        return {
            "biomass_tonnes_ha": float(biomass_tonnes),
            "carbon_tonnes_ha": stock.total_carbon_kg / 1000,
            "co2e_tonnes_ha": stock.total_co2e_kg / 1000,
        }
    else:
        return {
            "biomass_tonnes_ha": biomass_tonnes,
            "carbon_tonnes_ha": stock["total_carbon_kg"] / 1000,
            "co2e_tonnes_ha": stock["total_co2e_kg"] / 1000,
        }

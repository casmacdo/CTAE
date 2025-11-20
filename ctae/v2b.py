"""
Volume-to-biomass conversion.

Based on:
Boudewyn, P.A.; Song, X.; Magnussen, S.; Gillis, M.D. (2007). Model-based, 
volume-to-biomass conversion for forested and vegetated land in Canada. 
Natural Resources Canada, Canadian Forest Service, Pacific Forestry Centre, 
Victoria, BC. Information Report BC-X-411. 112 p.
"""
import numpy as np
from typing import Dict, Union
from .data_loader import load_parameters_v2b


def _get_v2b_params(genus: str, species: str, variety: str, jurisdiction: str, ecozone: int):
    """Internal function to get V2B parameters."""
    params = load_parameters_v2b()
    
    V2B_params_t3 = params["t3"]
    V2B_params_t4 = params["t4"]
    V2B_params_t5 = params["t5"]
    V2B_params_t6_vol = params["t6_vol"]
    V2B_params_t6_bio = params["t6_bio"]
    V2B_params_t7_vol = params["t7_vol"]
    V2B_params_t7_bio = params["t7_bio"]

    # Get B3 parameters
    B3 = V2B_params_t3[
        (V2B_params_t3["juris_id"] == jurisdiction)
        & (V2B_params_t3["genus"] == genus)
        & (V2B_params_t3["species"] == species)
        & (V2B_params_t3["ecozone"] == ecozone)
    ]
    
    if variety and not pd.isna(variety):
        B3 = B3[B3["variety"] == variety]
    else:
        B3 = B3[B3["variety"].isna()]
    
    if len(B3) != 1:
        raise ValueError("Error in parameter selection for B3")

    # Get B4 parameters
    B4 = V2B_params_t4[
        (V2B_params_t4["juris_id"] == jurisdiction)
        & (V2B_params_t4["ecozone"] == ecozone)
        & (V2B_params_t4["genus"] == genus)
        & (V2B_params_t4["species"] == species)
    ]
    
    if variety and not pd.isna(variety):
        B4 = B4[B4["variety"] == variety]
    else:
        B4 = B4[B4["variety"].isna()]
    
    if len(B4) != 1:
        raise ValueError("Error in parameter selection for B4")

    # Get B5 parameters (sapling factor - not available for all models)
    B5 = V2B_params_t5[
        (V2B_params_t5["juris_id"] == jurisdiction)
        & (V2B_params_t5["genus"] == genus)
        & (V2B_params_t5["ecozone"] == ecozone)
    ]
    
    if len(B5) != 1:
        B5 = None
    else:
        B5 = B5.iloc[0]

    # Get B6vol parameters
    B6vol = V2B_params_t6_vol[
        (V2B_params_t6_vol["juris_id"] == jurisdiction)
        & (V2B_params_t6_vol["ecozone"] == ecozone)
        & (V2B_params_t6_vol["genus"] == genus)
        & (V2B_params_t6_vol["species"] == species)
    ]
    
    if variety and not pd.isna(variety):
        B6vol = B6vol[B6vol["variety"] == variety]
    else:
        B6vol = B6vol[B6vol["variety"].isna()]

    # Get B6bio parameters
    B6bio = V2B_params_t6_bio[
        (V2B_params_t6_bio["juris_id"] == jurisdiction)
        & (V2B_params_t6_bio["ecozone"] == ecozone)
        & (V2B_params_t6_bio["genus"] == genus)
        & (V2B_params_t6_bio["species"] == species)
    ]
    
    if variety and not pd.isna(variety):
        B6bio = B6bio[B6bio["variety"] == variety]
    else:
        B6bio = B6bio[B6bio["variety"].isna()]

    # Get B7vol parameters
    B7vol = V2B_params_t7_vol[
        (V2B_params_t7_vol["genus"] == genus)
        & (V2B_params_t7_vol["species"] == species)
        & (V2B_params_t7_vol["juris_id"] == jurisdiction)
        & (V2B_params_t7_vol["ecozone"] == ecozone)
    ]
    
    if variety and not pd.isna(variety):
        B7vol = B7vol[B7vol["variety"] == variety]
    else:
        B7vol = B7vol[B7vol["variety"].isna()]

    # Get B7bio parameters
    B7bio = V2B_params_t7_bio[
        (V2B_params_t7_bio["genus"] == genus)
        & (V2B_params_t7_bio["species"] == species)
        & (V2B_params_t7_bio["juris_id"] == jurisdiction)
        & (V2B_params_t7_bio["ecozone"] == ecozone)
    ]
    
    if variety and not pd.isna(variety):
        B7bio = B7bio[B7bio["variety"] == variety]
    else:
        B7bio = B7bio[B7bio["variety"].isna()]

    if len(B6vol) != 1 or len(B6bio) != 1:
        raise ValueError("Error in parameter selection for B6")

    return {
        "B3": B3.iloc[0],
        "B4": B4.iloc[0],
        "B5": B5,
        "B6vol": B6vol.iloc[0],
        "B6bio": B6bio.iloc[0],
        "B7vol": B7vol.iloc[0] if len(B7vol) == 1 else None,
        "B7bio": B7bio.iloc[0] if len(B7bio) == 1 else None,
    }


def V2B(
    volume: Union[float, np.ndarray],
    species: str,
    jurisdiction: str,
    ecozone: int,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Volume-to-biomass conversion.

    Implementation of the model-based, volume-to-biomass conversion equations 
    by Boudewyn et al. (2007). Note - only scenarios 1 and 2 are currently implemented.

    Parameters
    ----------
    volume : float or array-like
        Gross merchantable volume/ha of all live trees.
        Note - Originally, parameters for BC were for net merchantable volume (not gross). 
        That has been updated in 2015 when new improved coefficients were made available. 
        Therefore, BC input data should also use **gross** merchantable volume from now on.
    species : str
        Species code in the NFI standard (e.g., "POPU.TRE", "PINU.CON")
    jurisdiction : str
        A two-letter code depicting jurisdiction (e.g., "AB", "BC")
    ecozone : int
        Ecozone number (1-15). See CodesEcozones for a list of ecozones names and codes.

    Returns
    -------
    dict
        Dictionary containing aboveground biomass values [tonnes/ha]:
        - b_m: Total stem wood biomass of merchantable-sized live trees
        - b_n: Stem wood biomass of live, nonmerchantable-sized trees
        - b_nm: b_m + b_n
        - b_s: Stem wood biomass of live, sapling-sized trees
        - b_total: Total tree biomass
        - b_bark: Total bark biomass
        - b_branches: Total branch biomass
        - b_foliage: Total foliage biomass

    Examples
    --------
    >>> V2B(350, species="PINU.CON", jurisdiction="BC", ecozone=4)
    """
    # Type checks
    if not isinstance(species, str):
        raise TypeError("'species' must be type str")
    if not isinstance(jurisdiction, str):
        raise TypeError("'jurisdiction' must be type str")
    if not isinstance(ecozone, int):
        raise TypeError("'ecozone' must be type int")

    # Import pandas here to avoid circular import
    import pandas as pd

    # Convert 'species' to: genus, species, variety
    species_parts = species.split(".")

    if len(species_parts) >= 2:
        genus = species_parts[0]
        spp = species_parts[1]
        variety = species_parts[2] if len(species_parts) > 2 else None
    else:
        raise ValueError("Wrong species format")

    # Get parameters
    B = _get_v2b_params(
        genus=genus, species=spp, variety=variety, jurisdiction=jurisdiction, ecozone=ecozone
    )

    B3 = B["B3"]
    B4 = B["B4"]
    B5 = B["B5"]
    B6 = B["B6vol"]

    # Calculations:
    volume = np.asarray(volume)

    # Merchantable-sized tree stem wood biomass (Eq1, based on a and b parameters from Table 3)
    b_m = B3["a"] * volume ** B3["b"]

    # Nonmerchantable-sized tree stem wood biomass
    # nonmerchfactor (Eq2, based on a, b, and k parameters from Table 4)
    nonmerchfactor = B4["k"] + B4["a"] * b_m ** B4["b"]

    # Check if nonmerchfactor is below the upper cap value
    nonmerchfactor = np.where(nonmerchfactor > B4["cap"], B4["cap"], nonmerchfactor)

    b_nm = nonmerchfactor * b_m
    b_n = b_nm - b_m  # stem wood biomass of live, nonmerchantable-sized trees (tonnes/ha)

    # Sapling-sized tree stem wood biomass
    # Not all species have sapling factor. Check whether the species in question has.
    if B5 is not None:
        # saplingfactor (Eq3, based on a, b, and k parameters from Table 5))
        saplingfactor = B5["k"] + B5["a"] * b_nm ** B5["b"]

        # check if samplingfactor is below the upper cap value
        saplingfactor = np.where(saplingfactor > B5["cap"], B5["cap"], saplingfactor)

        b_snm = saplingfactor * b_nm
        b_s = b_snm - b_nm  # stem wood biomass of live, sapling-sized trees
    else:
        b_s = 0

    # Proportions of total tree biomass in stemwood, stem bark, branch and foliage for live trees of all sizes
    # Equations 4-7
    lvol = np.log(volume + 5)

    p_a = np.exp(B6["a1"] + B6["a2"] * volume + B6["a3"] * lvol)
    p_b = np.exp(B6["b1"] + B6["b2"] * volume + B6["b3"] * lvol)
    p_c = np.exp(B6["c1"] + B6["c2"] * volume + B6["c3"] * lvol)
    p_abc = 1 + p_a + p_b + p_c

    Pstemwood = 1 / p_abc
    Pbark = p_a / p_abc
    Pbranches = p_b / p_abc
    Pfoliage = p_c / p_abc

    # total tree biomass
    b_total = (b_m + b_n + b_s) / Pstemwood

    # total bark biomass
    b_bark = b_total * Pbark

    # total branch biomass
    b_branches = b_total * Pbranches

    # total foliage biomass
    b_foliage = b_total * Pfoliage

    return {
        "b_m": b_m,
        "b_n": b_n,
        "b_nm": b_nm,
        "b_s": b_s,
        "b_total": b_total,
        "b_bark": b_bark,
        "b_branches": b_branches,
        "b_foliage": b_foliage,
    }

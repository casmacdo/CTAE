"""
Calculate AGB proportion of different tree organs using multinomial logit 
proportion equations.

Based on:
Boudewyn et al (2007). Model Based Volume-to-biomass Conversion for Forested 
and Vegetated Land in Canada.
"""
import warnings
import numpy as np
from typing import Dict, Union
from .v2b import _get_v2b_params


def AGB_prop(
    value_input: Union[float, np.ndarray],
    value_type: str,
    species: str,
    jurisdiction: str,
    ecozone: int,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate AGB proportion of different tree organs using multinomial logit 
    proportion equations using tree volume as input.

    This routine is the same as the one used in V2B() but returns only the 
    proportions and not the biomass values.

    Parameters
    ----------
    value_input : float or array-like
        Gross merchantable volume/ha (net in BC) or Above ground biomass 
        (stem wood + stem bark + branches + foliage as per Boudewyn et al (2007)) 
        in tonnes/ha of all live trees
    value_type : str
        Specify whether using biomass or volume as input. 
        Accepts partials 'vol' or 'bio'.
    species : str
        Species code in the NFI standard (e.g., "POPU.TRE", "PINU.CON")
    jurisdiction : str
        A two-letter code depicting jurisdiction (e.g., "AB", "BC")
    ecozone : int
        Ecozone number (1-15). See CodesEcozones for a list of ecozones names and codes.

    Returns
    -------
    dict
        Dictionary containing aboveground biomass proportion (0-1) for the tree 
        components:
        - Pstemwood: Biomass proportion allocated to the stem wood
        - Pbark: Biomass proportion allocated to the bark
        - Pbranches: Biomass proportion allocated to the branches
        - Pfoliage: Biomass proportion allocated to the foliage

    Examples
    --------
    >>> AGB_prop(350, value_type="vol", species="PINU.CON", jurisdiction="BC", ecozone=4)

    Notes
    -----
    A warning is displayed if the input volume is above (below) the maximum 
    (minimum) volume used to calibrate the equations parameters.
    """
    # Type checks
    if not isinstance(species, str):
        raise TypeError("'species' must be type str")
    if not isinstance(jurisdiction, str):
        raise TypeError("'jurisdiction' must be type str")
    if not isinstance(ecozone, int):
        raise TypeError("'ecozone' must be type int")
    if value_type not in ["biomass", "volume", "bio", "vol"]:
        raise ValueError("Must specify what is the type of input. Either 'biomass' or 'volume'.")

    # Import pandas here
    import pandas as pd

    # Split species into genus and species
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

    # Select appropriate parameters based on value_type
    if value_type in ["biomass", "bio"]:
        B6 = B["B6bio"]
        B7 = B["B7bio"]
        if B7 is not None:
            value_max = B7["biom_max"]
            value_min = B7["biom_min"]
        else:
            value_max = np.inf
            value_min = -np.inf
    elif value_type in ["volume", "vol"]:
        B6 = B["B6vol"]
        B7 = B["B7vol"]
        if B7 is not None:
            value_max = B7["vol_max"]
            value_min = B7["vol_min"]
        else:
            value_max = np.inf
            value_min = -np.inf
    else:
        raise ValueError("Something wrong with value_type specified.")

    # Convert to array
    value_input = np.asarray(value_input)

    # Apply equations
    lvalue = np.log(value_input + 5)
    p_a = np.exp(B6["a1"] + B6["a2"] * value_input + B6["a3"] * lvalue)
    p_b = np.exp(B6["b1"] + B6["b2"] * value_input + B6["b3"] * lvalue)
    p_c = np.exp(B6["c1"] + B6["c2"] * value_input + B6["c3"] * lvalue)
    p_abc = 1 + p_a + p_b + p_c

    # Check whether volume is within modelled range. If not apply cap and warn.
    if B7 is not None:
        cap_check = np.where(
            (value_input > value_min) & (value_input < value_max),
            "good",
            np.where(value_input < value_min, "below", "above"),
        )

        # Initialize output arrays
        Pstemwood = 1 / p_abc
        Pbark = p_a / p_abc
        Pbranches = p_b / p_abc
        Pfoliage = p_c / p_abc

        # Apply caps if needed
        below_mask = cap_check == "below"
        above_mask = cap_check == "above"

        if np.any(below_mask):
            Pstemwood = np.where(below_mask, B7["p_sw_low"], Pstemwood)
            Pbark = np.where(below_mask, B7["p_sb_low"], Pbark)
            Pbranches = np.where(below_mask, B7["p_br_low"], Pbranches)
            Pfoliage = np.where(below_mask, B7["p_fl_low"], Pfoliage)

        if np.any(above_mask):
            Pstemwood = np.where(above_mask, B7["p_sw_high"], Pstemwood)
            Pbark = np.where(above_mask, B7["p_sb_high"], Pbark)
            Pbranches = np.where(above_mask, B7["p_br_high"], Pbranches)
            Pfoliage = np.where(above_mask, B7["p_fl_high"], Pfoliage)

        # Warn if any values are outside range
        if np.any(below_mask) or np.any(above_mask):
            warnings.warn(
                f"\n{value_type.title()} outside model range. "
                f"\n{value_type.title()} value: {value_input}"
                f"\nModel range: {value_min:.2f} - {value_max:.2f}"
                f"\nProportion was capped following publication instructions."
            )
    else:
        # No caps available
        Pstemwood = 1 / p_abc
        Pbark = p_a / p_abc
        Pbranches = p_b / p_abc
        Pfoliage = p_c / p_abc

    return {
        "Pstemwood": Pstemwood,
        "Pbark": Pbark,
        "Pbranches": Pbranches,
        "Pfoliage": Pfoliage,
    }

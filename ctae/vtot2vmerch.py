"""
Total volume to gross (net in B.C.) merchantable volume conversion.

Based on Appendix 6 in Boudewyn et al. 2007.
"""
import numpy as np
from typing import Union
from .data_loader import load_params_vtot2vmerch


def Vtot2Vmerch(
    total_volume: Union[float, np.ndarray],
    species: str,
    jurisdiction: str,
    ecozone: int,
) -> Union[float, np.ndarray]:
    """
    Total volume to gross (net in B.C.) merchantable volume conversion.

    Based on Appendix 6 in Boudewyn et al. 2007.

    Parameters
    ----------
    total_volume : float or array-like
        Gross merchantable volume/ha (net in BC) of all live trees
    species : str
        Species code in the NFI standard (e.g., "POPU.TRE", "PINU.CON").
        Only genus is required.
    jurisdiction : str
        A two-letter code depicting jurisdiction (e.g., "AB", "BC")
    ecozone : int
        Ecozone number (1-15). See CodesEcozones for a list of ecozones names and codes.

    Returns
    -------
    float or array-like
        Merchantable volume

    Examples
    --------
    >>> Vtot2Vmerch(total_volume=300, species="PINU.CON", jurisdiction="AB", ecozone=4)
    """
    # Type checks
    if not isinstance(species, str):
        raise TypeError("'species' must be type str")
    if not isinstance(jurisdiction, str):
        raise TypeError("'jurisdiction' must be type str")
    if not isinstance(ecozone, int):
        raise TypeError("'ecozone' must be type int")

    # Convert 'species' to: genus, species, variety
    species_parts = species.split(".")

    if len(species_parts) >= 2:
        genus = species_parts[0]
        spp = species_parts[1]
        variety = species_parts[2] if len(species_parts) > 2 else None
    else:
        raise ValueError("Wrong species format")

    # Get parameters
    params = load_params_vtot2vmerch()
    B = params[
        (params["juris_id"] == jurisdiction)
        & (params["genus"] == genus)
        & (params["ecozone"] == ecozone)
    ]

    if len(B) != 1:
        raise ValueError("Error in parameter selection")

    B = B.iloc[0]

    # merchantable_volume = proportion × total_volume
    # proportion = k + a × (1 – exp(b × total_volume))^c

    # Calculations:
    total_volume = np.asarray(total_volume)
    proportion = B["k"] + B["a"] * (1 - np.exp(B["b"] * total_volume)) ** B["c"]
    merchantable_volume = proportion * total_volume

    return merchantable_volume

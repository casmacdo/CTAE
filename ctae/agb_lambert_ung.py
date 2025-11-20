"""
Calculate tree-level AGB using Canadian national tree aboveground biomass equations.

Based on:
- Lambert, M. C., Ung, C. H., & Raulier, F. (2005). Canadian national tree 
  aboveground biomass equations. Canadian Journal of Forest Research, 35(8), 
  1996–2018. https://doi.org/10.1139/x05-112

- Ung, C.-H., Bernier, P., & Guo, X.-J. (2008). Canadian national biomass 
  equations: new parameter estimates that include British Columbia data. 
  Canadian Journal of Forest Research, 38(5), 1123–1132. 
  https://doi.org/10.1139/X07-224
"""
import warnings
import numpy as np
from typing import Union, Dict
from .data_loader import load_parameters_lambert_ung


def AGB_LambertUngDBH(
    DBH: Union[float, np.ndarray], species: str = None
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate tree-level AGB using Canadian national tree aboveground biomass 
    equations using tree DBH as input.

    Parameters
    ----------
    DBH : float or array-like
        Tree diameter at breast height (cm)
    species : str, optional
        Tree species code in the NFI standard (e.g., "POPU.TRE", "PINU.CON")
        If None, uses coefficients for all species (UNKN.SPP)

    Returns
    -------
    dict
        Dictionary containing aboveground biomass values [kg] for tree components:
        - Bwood: Wood biomass
        - Bbark: Bark biomass
        - Bstem: Stem biomass (wood + bark)
        - Bfoliage: Foliage biomass
        - Bbranches: Branch biomass
        - Bcrown: Crown biomass (foliage + branches)
        - Btotal: Total tree aboveground biomass

    Examples
    --------
    >>> AGB_LambertUngDBH(20)
    >>> AGB_LambertUngDBH(20, species="PINU.CON")
    >>> AGB_LambertUngDBH(np.array([10, 15, 20, 25, 30]), species="PINU.CON")
    """
    params = load_parameters_lambert_ung()
    params = params[params["model"] == "DBH"]

    if species is None:
        warnings.warn("No species provided. Using coefficients for all species.")
        species = "UNKN.SPP"

    # Convert species to uppercase
    species = species.upper()

    # Check if species is included in the coefficients table
    if species not in params["species"].unique():
        raise ValueError(f"Wrong species: {species}")

    # Subset parameters for the current species
    B = params[params["species"] == species]

    # Create a dictionary of coefficients
    coeffs = {}
    for _, row in B.iterrows():
        coeffs[row["parameter"]] = row["estimate"]

    # Calculate biomass components
    DBH = np.asarray(DBH)
    
    Ywood = coeffs["bwood1"] * DBH ** coeffs["bwood2"]
    Ybark = coeffs["bbark1"] * DBH ** coeffs["bbark2"]
    Ystem = Ywood + Ybark
    Yfoliage = coeffs["bfoliage1"] * DBH ** coeffs["bfoliage2"]
    Ybranches = coeffs["bbranches1"] * DBH ** coeffs["bbranches2"]
    Ycrown = Yfoliage + Ybranches
    Ytotal = Ywood + Ybark + Yfoliage + Ybranches

    return {
        "Bwood": Ywood,
        "Bbark": Ybark,
        "Bstem": Ystem,
        "Bfoliage": Yfoliage,
        "Bbranches": Ybranches,
        "Bcrown": Ycrown,
        "Btotal": Ytotal,
    }


def AGB_LambertUngDBHHT(
    DBH: Union[float, np.ndarray],
    height: Union[float, np.ndarray],
    species: str = None,
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate tree-level AGB using Canadian national tree aboveground biomass 
    equations using tree DBH and height as input.

    Parameters
    ----------
    DBH : float or array-like
        Tree diameter at breast height (cm)
    height : float or array-like
        Tree height (m)
    species : str, optional
        Tree species code in the NFI standard (e.g., "POPU.TRE", "PINU.CON")
        If None, uses coefficients for all species (UNKN.SPP)

    Returns
    -------
    dict
        Dictionary containing aboveground biomass values [kg] for tree components:
        - Bwood: Wood biomass
        - Bbark: Bark biomass
        - Bstem: Stem biomass (wood + bark)
        - Bfoliage: Foliage biomass
        - Bbranches: Branch biomass
        - Bcrown: Crown biomass (foliage + branches)
        - Btotal: Total tree aboveground biomass

    Examples
    --------
    >>> AGB_LambertUngDBHHT(20, 17)
    >>> AGB_LambertUngDBHHT(20, 17, species="PINU.CON")
    >>> AGB_LambertUngDBHHT(DBH=[10, 15, 20], height=[12, 15, 17], species="PINU.CON")
    """
    params = load_parameters_lambert_ung()
    params = params[params["model"] == "DBHHT"]

    if species is None:
        warnings.warn("No species provided. Using coefficients for all species.")
        species = "UNKN.SPP"

    # Convert species to uppercase
    species = species.upper()

    # Check if species is included in the coefficients table
    if species not in params["species"].unique():
        raise ValueError(f"Wrong species: {species}")

    # Subset parameters for the current species
    B = params[params["species"] == species]

    # Create a dictionary of coefficients
    coeffs = {}
    for _, row in B.iterrows():
        coeffs[row["parameter"]] = row["estimate"]

    # Calculate biomass components
    DBH = np.asarray(DBH)
    height = np.asarray(height)
    
    Ywood = coeffs["bwood1"] * DBH ** coeffs["bwood2"] * height ** coeffs["bwood3"]
    Ybark = coeffs["bbark1"] * DBH ** coeffs["bbark2"] * height ** coeffs["bbark3"]
    Ystem = Ywood + Ybark
    Yfoliage = (
        coeffs["bfoliage1"] * DBH ** coeffs["bfoliage2"] * height ** coeffs["bfoliage3"]
    )
    Ybranches = (
        coeffs["bbranches1"]
        * DBH ** coeffs["bbranches2"]
        * height ** coeffs["bbranches3"]
    )
    Ycrown = Yfoliage + Ybranches
    Ytotal = Ywood + Ybark + Yfoliage + Ybranches

    return {
        "Bwood": Ywood,
        "Bbark": Ybark,
        "Bstem": Ystem,
        "Bfoliage": Yfoliage,
        "Bbranches": Ybranches,
        "Bcrown": Ycrown,
        "Btotal": Ytotal,
    }

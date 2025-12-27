"""
Ung2009 Growth and Yield Model.

Based on:
Ung, C.-H., Bernier, P.Y., Guo, X.J., Lambert, M.-C. (2009).
"A simple growth and yield model for assessing changes in standing volume
across Canada's forests." The Forestry Chronicle, 85, 57-64.
https://doi.org/10.5558/tfc85057-1
"""
import numpy as np
import pandas as pd
from typing import Union
from .data_loader import load_parameters_ung2009


def Ung2009(
    species: str,
    age: Union[int, float, np.ndarray, list],
    GDD: Union[int, float],
    PREC: Union[int, float],
    model: str = "both",
) -> pd.DataFrame:
    """
    Ung2009 Growth and Yield Model.

    This function implements the models described in Ung et al. (2009).
    Two models (Nat1 and Nat2) are available:
    - Nat1: A multi-equation system predicting tree height (H), basal area (BA),
            and volume (V) based on stand age, growth degree days (GDD),
            precipitation (PREC), and species-specific parameters.
    - Nat2: A single equation that focuses on predicting stand volume (V)
            using age, GDD, and PREC.

    Parameters
    ----------
    species : str
        A valid species name as defined in the parameter table of the model.
        Supported species include: ABIE.BAL, ABIE.LAS, ACER.RUB, ACER.SAC,
        BETU.ALL, BETU.PAP, FAGU.GRA, LARI.LAR, LARI.OCC, PICE.ENG, PICE.GLA,
        PICE.MAR, PICE.RUB, PINU.BAN, PINU.CON, PINU.RES, PINU.STR, POPU.BAL,
        POPU.GRA, POPU.TRE, PSEU.MEN, QUER.RUB, THUJ.OCC, TSUG.CAN, TSUG.HET.
    age : int, float, or array-like
        The age(s) of the stand in years. Must be greater than 0.
    GDD : int or float
        Growth degree days. Typical range: 500-2500.
    PREC : int or float
        Annual precipitation in mm. Typical range: 300-1500.
    model : str, optional
        Which model(s) to use. One of "Nat1", "Nat2", or "both".
        Defaults to "both".

    Returns
    -------
    pandas.DataFrame
        DataFrame containing:
        - age
        - H (if Nat1 is used): Predicted tree height (m)
        - BA (if Nat1 is used): Predicted basal area (m2/ha)
        - V (if Nat1 is used): Predicted volume (m3/ha)
        - V2 (if Nat2 is used): Predicted volume (m3/ha) based on the Nat2 model

    Examples
    --------
    >>> # Use both models (default), returning columns: age, H, BA, V, V2
    >>> res_both = Ung2009(
    ...     species="ABIE.BAL",
    ...     age=range(1, 151),
    ...     GDD=1500,
    ...     PREC=800
    ... )
    >>>
    >>> # Use only the Nat1 model, returning columns: age, H, BA, V
    >>> res_nat1 = Ung2009(
    ...     species="ABIE.BAL",
    ...     age=range(1, 151),
    ...     GDD=1500,
    ...     PREC=800,
    ...     model="Nat1"
    ... )
    >>>
    >>> # Use only the Nat2 model, returning columns: age, V2
    >>> res_nat2 = Ung2009(
    ...     species="ABIE.BAL",
    ...     age=range(1, 151),
    ...     GDD=1500,
    ...     PREC=800,
    ...     model="Nat2"
    ... )
    """
    # Validate model parameter
    if model not in ["both", "Nat1", "Nat2"]:
        raise ValueError("model must be one of 'both', 'Nat1', or 'Nat2'")

    # Convert age to array
    age = np.atleast_1d(np.asarray(age, dtype=float))

    # Validate inputs
    if np.any(age <= 0):
        raise ValueError("Age must be greater than 0.")
    if not isinstance(GDD, (int, float)) or not isinstance(PREC, (int, float)):
        raise TypeError("GDD and PREC must be numeric.")
    if not isinstance(species, str):
        raise TypeError("Species must be a character string.")

    # Load parameters from CSV
    params = load_parameters_ung2009()
    _PARAMS_NAT1 = params["nat1"]
    _PARAMS_NAT2 = params["nat2"]

    # Look up species parameters
    param = _PARAMS_NAT1[_PARAMS_NAT1["Species"] == species]
    param2 = _PARAMS_NAT2[_PARAMS_NAT2["Species"] == species]

    if len(param) == 0 or len(param2) == 0:
        available_species = sorted(_PARAMS_NAT1["Species"].unique())
        raise ValueError(
            f"Invalid species '{species}'. "
            f"Available species: {', '.join(available_species)}"
        )

    param = param.iloc[0]
    param2 = param2.iloc[0]

    # Initialize output dataframe
    out = pd.DataFrame({"age": age})

    # Nat1 model
    if model in ["Nat1", "both"]:
        lnH = (param["h10"] + (param["h11"] * GDD) + (param["h12"] * PREC)) + (
            (param["h20"] + (param["h21"] * GDD) + (param["h22"] * PREC)) / age
        )
        H = np.exp(lnH) * param["CDh"]

        lnBA = (param["g10"] + (param["g11"] * GDD) + (param["g12"] * PREC)) + (
            (param["g20"] + (param["g21"] * GDD) + (param["g22"] * PREC)) / age
        )
        BA = np.exp(lnBA) * param["CDg"]

        lnV = param["v30"] + param["v31"] * lnH + param["v32"] * lnBA
        V = np.exp(lnV) * param["CDv"]

        out["H"] = H
        out["BA"] = BA
        out["V"] = V

    # Nat2 model
    if model in ["Nat2", "both"]:
        lnV2 = (param2["v10"] + (param2["v11"] * GDD) + (param2["v12"] * PREC)) + (
            (param2["v20"] + (param2["v21"] * GDD) + (param2["v22"] * PREC)) / age
        )
        V2 = np.exp(lnV2) * param2["Cd"]

        out["V2"] = V2

    return out

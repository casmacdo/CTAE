"""
Calculate individual tree volume for major Alberta tree species.

Based on:
Huang, S. (1994). Ecologically Based Individual Tree Volume Estimation for 
Major Alberta Tree Species. Report 1 - Individual tree volume estimation 
procedures for Alberta: Methods of Formulation and Statistical Foundations. 
Alberta Environmental Protection, Land and Forest Service, Forest Management 
Division, Edmonton, AB.
"""
import warnings
import numpy as np
from typing import Dict, Union
from .data_loader import load_parameters_huang


def V_Huang(
    DBH: Union[float, np.ndarray],
    height: Union[float, np.ndarray],
    species: str,
    subregion: str = "Province",
) -> Dict[str, Union[float, np.ndarray]]:
    """
    Calculate individual tree volume for major Alberta tree species.

    Parameters
    ----------
    DBH : float or array-like
        Tree diameter at breast height (cm)
    height : float or array-like
        Tree height (m)
    species : str
        Tree species code in the NFI standard (e.g., "POPU.TRE", "PICE.GLA")
    subregion : str, optional
        Code depicting natural subregion of Alberta (e.g., "LF" for Lower Foothills).
        'Province' (the default) indicates province-level parameters.
        Note: 'UB' (Upper Boreal Highlands) is automatically replaced with 'LBH'
        (Lower Boreal Highlands) as per original model specifications.

    Returns
    -------
    dict
        Dictionary containing volume values [m³]:
        - v_merch: Merchantable volume (to 2.0 cm top diameter inside bark)
        - v_total: Total volume

    Examples
    --------
    >>> V_Huang(20, 20, "PICE.GLA")
    >>> V_Huang(20, 20, "PICE.GLA", subregion="CP")

    Notes
    -----
    The function implements the taper equation and iterative merchantable height
    calculation as described in Huang (1994). A stump height of 0.30 m and a
    top diameter of 2.0 cm inside bark are assumed.
    """
    # Type checks
    if not isinstance(species, str):
        raise TypeError("'species' must be type str")
    if not isinstance(subregion, str):
        raise TypeError("'subregion' must be type str")

    # Load parameters
    parameters = load_parameters_huang()

    # Check if species is included in the coefficients table
    if species not in parameters["species"].unique():
        raise ValueError(f"No model parameters available for {species}")

    # Handle Upper Boreal Highlands -> Lower Boreal Highlands conversion
    if subregion == "UB":
        subregion = "LBH"

    # Check if subregion exists
    if subregion not in parameters["NaturalSubregionCode"].unique():
        raise ValueError(
            "Wrong subregion code. See AlbertaNaturalRegSubreg dataset for valid codes"
        )

    # Check species and region combination
    if subregion != "Province":
        is_available = (
            len(
                parameters[
                    (parameters["species"] == species)
                    & (parameters["NaturalSubregionCode"] == subregion)
                ]
            )
            > 0
        )

        if not is_available:
            warnings.warn(
                f"No model parameters available for {species} in {subregion}. "
                f"Using Province-level parameters."
            )
            subregion = "Province"

    # Get parameters
    params = parameters[
        (parameters["NaturalSubregionCode"] == subregion)
        & (parameters["species"] == species)
    ]

    # Check if number of parameters is correct (need to be 8)
    if len(params) != 8:
        raise ValueError("Error in parameter selection")

    # Create coefficient dictionary
    coeffs = {}
    for _, row in params.iterrows():
        coeffs[row["parameter"]] = row["estimate"]

    # Convert inputs to arrays for vectorization
    DBH = np.atleast_1d(np.asarray(DBH, dtype=float))
    height = np.atleast_1d(np.asarray(height, dtype=float))
    
    # Ensure DBH and height are broadcastable
    if DBH.shape != height.shape:
        if DBH.shape == (1,):
            DBH = np.full_like(height, DBH[0])
        elif height.shape == (1,):
            height = np.full_like(DBH, height[0])
        else:
            raise ValueError("DBH and height must have the same shape or be scalar")

    # Initialize result arrays
    mvol = np.zeros_like(DBH, dtype=float)
    tvol = np.zeros_like(DBH, dtype=float)

    # Process each tree
    for i in range(len(DBH)):
        dbh_i = DBH[i]
        ht_i = height[i]

        # Define g = h/height, set the initial value for g
        g0 = 0.9
        g1 = 0.0

        # Iteration to find merchantable height
        # A 2.0 cm top diameter inside bark is assumed
        iii = 0  # counter to protect against endless loops
        maxiter = 1000  # maximum number of iterations

        while abs(g0 - g1) > 0.00000001 and iii <= maxiter:
            cc = (
                coeffs["b1"] * g0**2
                + coeffs["b2"] * np.log(g0 + 0.001)
                + coeffs["b3"] * np.sqrt(g0)
                + coeffs["b4"] * np.exp(g0)
                + coeffs["b5"] * (dbh_i / ht_i)
            )

            g1 = (
                1
                - ((2 / (coeffs["a0"] * dbh_i ** coeffs["a1"] * coeffs["a2"] ** dbh_i)) ** (1 / cc))
                * (1 - np.sqrt(0.225))
            ) ** 2

            g0 = (g0 + g1) / 2
            iii += 1

        # If no convergence then assign NAs to results
        if iii > maxiter or not np.isfinite(g1) or not np.isfinite(g0):
            mvol[i] = np.nan
            tvol[i] = np.nan
            continue

        # Compute merchantable height (hi) and merchantable length (mlen)
        # A stump height of 0.30 m is assumed
        hi = g0 * ht_i

        # Divide merchantable length into 10 sections of equal length
        # Compute the height above the ground from the middle and the top of each section
        mlen = np.arange(1, 21) * (hi - 0.3) / 20 + 0.3

        # Prediction of diameter inside bark at the middle and top of each section
        z = mlen / ht_i
        x = (1 - np.sqrt(z)) / (1 - np.sqrt(0.225))

        # Diameter inside bark at stump height
        dibm0 = (
            (coeffs["a0"] * dbh_i ** coeffs["a1"])
            * (coeffs["a2"] ** dbh_i)
            * ((1 - np.sqrt(0.3 / ht_i)) / (1 - np.sqrt(0.225)))
            ** (
                coeffs["b1"] * (0.3 / ht_i) ** 2
                + coeffs["b2"] * np.log(0.3 / ht_i + 0.001)
                + coeffs["b3"] * np.sqrt(0.3 / ht_i)
                + coeffs["b4"] * np.exp(0.3 / ht_i)
                + coeffs["b5"] * dbh_i / ht_i
            )
        )

        # Diameter inside bark at sections
        dibx = (
            (coeffs["a0"] * dbh_i ** coeffs["a1"])
            * (coeffs["a2"] ** dbh_i)
            * x
            ** (
                coeffs["b1"] * z**2
                + coeffs["b2"] * np.log(z + 0.001)
                + coeffs["b3"] * np.sqrt(z)
                + coeffs["b4"] * np.exp(z)
                + coeffs["b5"] * dbh_i / ht_i
            )
        )

        dibm = np.concatenate([[dibm0], dibx])

        # Compute the merchantable volume using Newton's formula
        k = 0.00007854 * (((hi - 0.3) / 10) / 6)

        mvol_i = (
            k * (dibm[0] ** 2 + 4 * dibm[1] ** 2 + dibm[2] ** 2)
            + k * (dibm[2] ** 2 + 4 * dibm[3] ** 2 + dibm[4] ** 2)
            + k * (dibm[4] ** 2 + 4 * dibm[5] ** 2 + dibm[6] ** 2)
            + k * (dibm[6] ** 2 + 4 * dibm[7] ** 2 + dibm[8] ** 2)
            + k * (dibm[8] ** 2 + 4 * dibm[9] ** 2 + dibm[10] ** 2)
            + k * (dibm[10] ** 2 + 4 * dibm[11] ** 2 + dibm[12] ** 2)
            + k * (dibm[12] ** 2 + 4 * dibm[13] ** 2 + dibm[14] ** 2)
            + k * (dibm[14] ** 2 + 4 * dibm[15] ** 2 + dibm[16] ** 2)
            + k * (dibm[16] ** 2 + 4 * dibm[17] ** 2 + dibm[18] ** 2)
            + k * (dibm[18] ** 2 + 4 * dibm[19] ** 2 + dibm[20] ** 2)
        )

        # Compute tip volume, stump volume, and total volume
        tipvol = 0.00007854 * dibm[20] ** 2 * (ht_i - hi) / 3
        volstp = 0.00007854 * dibm[0] ** 2 * 0.3
        tvol_i = mvol_i + tipvol + volstp

        mvol[i] = mvol_i
        tvol[i] = tvol_i

    # Return scalar if input was scalar
    if mvol.shape == (1,):
        mvol = float(mvol[0])
        tvol = float(tvol[0])

    return {"v_merch": mvol, "v_total": tvol}

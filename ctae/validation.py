"""
Input validation utilities for CTAE functions.

This module provides validation functions to ensure input parameters
are within reasonable ranges for forestry calculations.
"""
import warnings
from typing import Union, Optional, List
import numpy as np


# Valid ranges for common forestry measurements
VALID_RANGES = {
    "DBH": {"min": 0.1, "max": 300, "unit": "cm", "description": "Diameter at breast height"},
    "height": {"min": 0.1, "max": 100, "unit": "m", "description": "Tree height"},
    "age": {"min": 1, "max": 500, "unit": "years", "description": "Stand/tree age"},
    "volume": {"min": 0, "max": 2000, "unit": "m3/ha", "description": "Volume per hectare"},
    "GDD": {"min": 0, "max": 5000, "unit": "degree-days", "description": "Growing degree days"},
    "PREC": {"min": 0, "max": 5000, "unit": "mm", "description": "Annual precipitation"},
    "ecozone": {"min": 1, "max": 15, "unit": "", "description": "Ecozone number"},
}

# Valid jurisdiction codes
VALID_JURISDICTIONS = ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


class ValidationWarning(UserWarning):
    """Warning raised when inputs are outside typical ranges but still valid."""
    pass


def validate_positive(
    value: Union[float, np.ndarray],
    name: str,
    allow_zero: bool = False
) -> None:
    """
    Validate that a value is positive.

    Parameters
    ----------
    value : float or array-like
        The value to validate.
    name : str
        Name of the parameter (for error messages).
    allow_zero : bool
        If True, zero is allowed. Defaults to False.

    Raises
    ------
    ValidationError
        If value is negative (or zero when not allowed).
    """
    arr = np.atleast_1d(np.asarray(value))
    if allow_zero:
        if np.any(arr < 0):
            raise ValidationError(f"'{name}' must be non-negative. Got values: {arr[arr < 0]}")
    else:
        if np.any(arr <= 0):
            raise ValidationError(f"'{name}' must be positive. Got values: {arr[arr <= 0]}")


def validate_range(
    value: Union[float, np.ndarray],
    name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    warn_only: bool = True
) -> None:
    """
    Validate that a value is within a specified range.

    Parameters
    ----------
    value : float or array-like
        The value to validate.
    name : str
        Name of the parameter (for error messages).
    min_val : float, optional
        Minimum allowed value.
    max_val : float, optional
        Maximum allowed value.
    warn_only : bool
        If True, issue warning instead of raising error for out-of-range values.

    Raises
    ------
    ValidationError
        If warn_only is False and value is out of range.
    """
    arr = np.atleast_1d(np.asarray(value))

    out_of_range = []
    if min_val is not None and np.any(arr < min_val):
        out_of_range.append(f"below minimum ({min_val})")
    if max_val is not None and np.any(arr > max_val):
        out_of_range.append(f"above maximum ({max_val})")

    if out_of_range:
        msg = f"'{name}' values are {' and '.join(out_of_range)}. Got: min={np.min(arr)}, max={np.max(arr)}"
        if warn_only:
            warnings.warn(msg, ValidationWarning)
        else:
            raise ValidationError(msg)


def validate_dbh(
    dbh: Union[float, np.ndarray],
    warn_only: bool = True
) -> None:
    """
    Validate DBH (diameter at breast height) values.

    Parameters
    ----------
    dbh : float or array-like
        DBH values in cm.
    warn_only : bool
        If True, issue warning for out-of-range values instead of error.

    Raises
    ------
    ValidationError
        If DBH is negative or zero.
    """
    validate_positive(dbh, "DBH")
    ranges = VALID_RANGES["DBH"]
    validate_range(dbh, "DBH", ranges["min"], ranges["max"], warn_only=warn_only)


def validate_height(
    height: Union[float, np.ndarray],
    warn_only: bool = True
) -> None:
    """
    Validate tree height values.

    Parameters
    ----------
    height : float or array-like
        Height values in meters.
    warn_only : bool
        If True, issue warning for out-of-range values instead of error.

    Raises
    ------
    ValidationError
        If height is negative or zero.
    """
    validate_positive(height, "height")
    ranges = VALID_RANGES["height"]
    validate_range(height, "height", ranges["min"], ranges["max"], warn_only=warn_only)


def validate_age(
    age: Union[float, np.ndarray],
    warn_only: bool = True
) -> None:
    """
    Validate stand/tree age values.

    Parameters
    ----------
    age : float or array-like
        Age values in years.
    warn_only : bool
        If True, issue warning for out-of-range values instead of error.

    Raises
    ------
    ValidationError
        If age is negative or zero.
    """
    validate_positive(age, "age")
    ranges = VALID_RANGES["age"]
    validate_range(age, "age", ranges["min"], ranges["max"], warn_only=warn_only)


def validate_volume(
    volume: Union[float, np.ndarray],
    warn_only: bool = True
) -> None:
    """
    Validate volume values.

    Parameters
    ----------
    volume : float or array-like
        Volume values in m3/ha.
    warn_only : bool
        If True, issue warning for out-of-range values instead of error.

    Raises
    ------
    ValidationError
        If volume is negative.
    """
    validate_positive(volume, "volume", allow_zero=True)
    ranges = VALID_RANGES["volume"]
    validate_range(volume, "volume", ranges["min"], ranges["max"], warn_only=warn_only)


def validate_species_code(
    species: str,
    valid_species: Optional[List[str]] = None
) -> None:
    """
    Validate species code format.

    Parameters
    ----------
    species : str
        Species code (e.g., "PINU.CON").
    valid_species : list of str, optional
        List of valid species codes to check against.

    Raises
    ------
    ValidationError
        If species format is invalid or not in valid list.
    """
    if not isinstance(species, str):
        raise ValidationError(f"'species' must be a string, got {type(species).__name__}")

    # Check format: GENUS.SPP or GENUS.SPP.VAR
    parts = species.split(".")
    if len(parts) < 2 or len(parts) > 3:
        raise ValidationError(
            f"Invalid species format '{species}'. "
            "Expected format: 'GENUS.SPECIES' (e.g., 'PINU.CON')"
        )

    if valid_species is not None and species.upper() not in [s.upper() for s in valid_species]:
        raise ValidationError(
            f"Unknown species '{species}'. "
            f"Valid species: {', '.join(sorted(valid_species)[:10])}..."
        )


def validate_jurisdiction(jurisdiction: str) -> None:
    """
    Validate Canadian jurisdiction code.

    Parameters
    ----------
    jurisdiction : str
        Two-letter jurisdiction code (e.g., "BC", "ON").

    Raises
    ------
    ValidationError
        If jurisdiction code is invalid.
    """
    if not isinstance(jurisdiction, str):
        raise ValidationError(f"'jurisdiction' must be a string, got {type(jurisdiction).__name__}")

    if jurisdiction.upper() not in VALID_JURISDICTIONS:
        raise ValidationError(
            f"Invalid jurisdiction '{jurisdiction}'. "
            f"Valid jurisdictions: {', '.join(VALID_JURISDICTIONS)}"
        )


def validate_ecozone(ecozone: int) -> None:
    """
    Validate ecozone number.

    Parameters
    ----------
    ecozone : int
        Ecozone number (1-15).

    Raises
    ------
    ValidationError
        If ecozone is not an integer or out of valid range.
    """
    if not isinstance(ecozone, int):
        raise ValidationError(f"'ecozone' must be an integer, got {type(ecozone).__name__}")

    ranges = VALID_RANGES["ecozone"]
    if ecozone < ranges["min"] or ecozone > ranges["max"]:
        raise ValidationError(
            f"Invalid ecozone {ecozone}. "
            f"Must be between {ranges['min']} and {ranges['max']}"
        )

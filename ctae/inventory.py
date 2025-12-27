"""
Forest inventory processing utilities.

This module provides functions for:
- Batch processing of tree inventories
- Forest carbon accounting workflows
- Standard report generation
"""
import numpy as np
import pandas as pd
from typing import Union, Dict, Optional, List, Callable
import warnings


def process_inventory(
    tree_data: pd.DataFrame,
    dbh_col: str = "DBH",
    height_col: Optional[str] = None,
    species_col: str = "species",
    jurisdiction_col: Optional[str] = None,
    ecozone_col: Optional[str] = None,
    default_jurisdiction: str = "ON",
    default_ecozone: int = 5,
    calculate: List[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> pd.DataFrame:
    """
    Process a forest inventory DataFrame to calculate biomass and carbon.

    Parameters
    ----------
    tree_data : pd.DataFrame
        DataFrame with individual tree measurements.
    dbh_col : str
        Column name for DBH (cm).
    height_col : str, optional
        Column name for height (m). If None, heights are estimated.
    species_col : str
        Column name for species codes.
    jurisdiction_col : str, optional
        Column for jurisdiction codes. If None, uses default.
    ecozone_col : str, optional
        Column for ecozone numbers. If None, uses default.
    default_jurisdiction : str
        Default jurisdiction if not specified per-tree.
    default_ecozone : int
        Default ecozone if not specified per-tree.
    calculate : list of str, optional
        What to calculate: ['biomass', 'carbon', 'volume', 'value'].
        Default is all.
    progress_callback : callable, optional
        Function called with (current, total) for progress tracking.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with added calculation columns.

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'tree_id': [1, 2, 3],
    ...     'DBH': [20, 30, 40],
    ...     'species': ['PINU.CON', 'PICE.GLA', 'POPU.TRE']
    ... })
    >>> result = process_inventory(df)
    >>> 'biomass_kg' in result.columns
    True
    """
    from .agb_lambert_ung import AGB_LambertUngDBH, AGB_LambertUngDBHHT
    from .carbon import calculate_carbon_stock, carbon_value
    from .utils import estimate_height_from_dbh, basal_area, stem_volume_quick

    if calculate is None:
        calculate = ["biomass", "carbon", "volume", "value"]

    df = tree_data.copy()
    n_rows = len(df)

    # Estimate heights if not provided
    if height_col is None or height_col not in df.columns:
        df["_height_est"] = df.apply(
            lambda row: estimate_height_from_dbh(row[dbh_col], row.get(species_col)),
            axis=1,
        )
        height_col = "_height_est"
        df["height_estimated"] = True
    else:
        df["height_estimated"] = False

    # Add basal area
    df["basal_area_m2"] = basal_area(df[dbh_col].values)

    # Process each tree
    biomass_results = []
    carbon_results = []
    volume_results = []
    value_results = []

    for idx, row in df.iterrows():
        if progress_callback:
            progress_callback(idx + 1, n_rows)

        dbh = row[dbh_col]
        height = row[height_col]
        species = row.get(species_col, "UNKN.SPP")

        # Biomass calculation
        if "biomass" in calculate or "carbon" in calculate:
            try:
                agb = AGB_LambertUngDBHHT(dbh, height, species=species)
                biomass_total = float(agb["Btotal"])
            except (ValueError, KeyError):
                try:
                    agb = AGB_LambertUngDBH(dbh, species=species)
                    biomass_total = float(agb["Btotal"])
                except (ValueError, KeyError):
                    agb = AGB_LambertUngDBH(dbh, species=None)
                    biomass_total = float(agb["Btotal"])

            biomass_results.append(biomass_total)

            # Carbon calculation
            if "carbon" in calculate:
                # Determine if conifer
                conifer_genera = ["PINU", "PICE", "ABIE", "TSUG", "THUJ", "PSEU", "LARI"]
                genus = species.split(".")[0].upper() if species else "UNKN"
                is_conifer = genus in conifer_genera

                stock = calculate_carbon_stock(
                    biomass_total,
                    include_belowground=True,
                    is_conifer=is_conifer,
                )
                carbon_results.append(
                    {
                        "carbon_kg": stock.total_carbon_kg,
                        "co2e_kg": stock.total_co2e_kg,
                    }
                )

        # Volume estimation
        if "volume" in calculate:
            vol = stem_volume_quick(dbh, height, species)
            volume_results.append(float(vol))

        # Value calculation
        if "value" in calculate and carbon_results:
            val = carbon_value(carbon_results[-1]["co2e_kg"])
            value_results.append(float(val))

    # Add results to DataFrame
    if biomass_results:
        df["biomass_kg"] = biomass_results

    if carbon_results:
        df["carbon_kg"] = [r["carbon_kg"] for r in carbon_results]
        df["co2e_kg"] = [r["co2e_kg"] for r in carbon_results]

    if volume_results:
        df["volume_m3"] = volume_results

    if value_results:
        df["carbon_value_usd"] = value_results

    # Clean up temporary columns
    if "_height_est" in df.columns:
        df = df.rename(columns={"_height_est": "height_m"})

    return df


def inventory_carbon_summary(
    processed_inventory: pd.DataFrame,
    group_by: Optional[List[str]] = None,
    expansion_factor_col: Optional[str] = None,
    default_expansion_factor: float = 1.0,
    area_ha: Optional[float] = None,
) -> pd.DataFrame:
    """
    Summarize carbon metrics from a processed inventory.

    Parameters
    ----------
    processed_inventory : pd.DataFrame
        DataFrame from process_inventory() with carbon columns.
    group_by : list of str, optional
        Columns to group by (e.g., ['plot_id', 'stand_type']).
    expansion_factor_col : str, optional
        Column with expansion factors (trees/ha).
    default_expansion_factor : float
        Default if no expansion factor column.
    area_ha : float, optional
        Total area in hectares for scaling.

    Returns
    -------
    pd.DataFrame
        Summary statistics by group.
    """
    df = processed_inventory.copy()

    # Get expansion factors
    if expansion_factor_col and expansion_factor_col in df.columns:
        ef = df[expansion_factor_col]
    else:
        ef = default_expansion_factor

    # Calculate expanded values
    df["_ef"] = ef
    df["_biomass_expanded"] = df["biomass_kg"] * df["_ef"] if "biomass_kg" in df.columns else 0
    df["_carbon_expanded"] = df["carbon_kg"] * df["_ef"] if "carbon_kg" in df.columns else 0
    df["_co2e_expanded"] = df["co2e_kg"] * df["_ef"] if "co2e_kg" in df.columns else 0

    def summarize(group):
        n_trees = len(group)
        trees_per_ha = group["_ef"].sum()

        result = {
            "n_trees_sample": n_trees,
            "trees_per_ha": trees_per_ha,
        }

        if "biomass_kg" in group.columns:
            result["biomass_kg_ha"] = group["_biomass_expanded"].sum()
            result["biomass_tonnes_ha"] = result["biomass_kg_ha"] / 1000

        if "carbon_kg" in group.columns:
            result["carbon_kg_ha"] = group["_carbon_expanded"].sum()
            result["carbon_tonnes_ha"] = result["carbon_kg_ha"] / 1000

        if "co2e_kg" in group.columns:
            result["co2e_kg_ha"] = group["_co2e_expanded"].sum()
            result["co2e_tonnes_ha"] = result["co2e_kg_ha"] / 1000

        if "carbon_value_usd" in group.columns:
            result["carbon_value_usd_ha"] = (
                group["carbon_value_usd"] * group["_ef"]
            ).sum()

        return pd.Series(result)

    if group_by:
        summary = df.groupby(group_by).apply(summarize).reset_index()
    else:
        summary = summarize(df).to_frame().T

    # Scale by area if provided
    if area_ha:
        for col in ["biomass_tonnes_ha", "carbon_tonnes_ha", "co2e_tonnes_ha"]:
            if col in summary.columns:
                total_col = col.replace("_ha", "_total")
                summary[total_col] = summary[col] * area_ha

    return summary


def generate_carbon_report(
    inventory_summary: pd.DataFrame,
    report_format: str = "dict",
    title: str = "Forest Carbon Inventory Report",
    methodology: str = "CTAE v0.4.4 (Lambert-Ung biomass equations)",
) -> Union[Dict, str]:
    """
    Generate a carbon inventory report from summary data.

    Parameters
    ----------
    inventory_summary : pd.DataFrame
        Summary from inventory_carbon_summary().
    report_format : str
        Output format: 'dict', 'json', 'markdown'.
    title : str
        Report title.
    methodology : str
        Methodology description.

    Returns
    -------
    dict or str
        Report in requested format.
    """
    import json
    from datetime import datetime

    # Build report structure
    report = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "methodology": methodology,
        "summary": {},
        "details": [],
    }

    # Overall summary
    total_cols = [c for c in inventory_summary.columns if "_total" in c or "_ha" in c]
    if total_cols:
        report["summary"] = {
            col: float(inventory_summary[col].sum()) for col in total_cols
        }

    # Key metrics
    if "co2e_tonnes_ha" in inventory_summary.columns:
        report["summary"]["mean_co2e_tonnes_ha"] = float(
            inventory_summary["co2e_tonnes_ha"].mean()
        )
    if "carbon_tonnes_ha" in inventory_summary.columns:
        report["summary"]["mean_carbon_tonnes_ha"] = float(
            inventory_summary["carbon_tonnes_ha"].mean()
        )

    # Detail rows
    report["details"] = inventory_summary.to_dict(orient="records")

    if report_format == "dict":
        return report
    elif report_format == "json":
        return json.dumps(report, indent=2, default=str)
    elif report_format == "markdown":
        md = f"# {title}\n\n"
        md += f"**Generated:** {report['generated_at']}\n\n"
        md += f"**Methodology:** {methodology}\n\n"
        md += "## Summary\n\n"
        for key, value in report["summary"].items():
            md += f"- **{key}:** {value:.2f}\n"
        md += "\n## Details\n\n"
        md += inventory_summary.to_markdown(index=False)
        return md
    else:
        raise ValueError(f"Unknown format: {report_format}")


def validate_inventory(
    tree_data: pd.DataFrame,
    dbh_col: str = "DBH",
    height_col: Optional[str] = None,
    species_col: str = "species",
) -> Dict[str, List]:
    """
    Validate inventory data and identify potential issues.

    Parameters
    ----------
    tree_data : pd.DataFrame
        Tree inventory data.
    dbh_col : str
        DBH column name.
    height_col : str, optional
        Height column name.
    species_col : str
        Species column name.

    Returns
    -------
    dict
        Dictionary with validation results:
        - errors: Critical issues that must be fixed
        - warnings: Potential issues to review
        - stats: Summary statistics
    """
    df = tree_data.copy()
    errors = []
    warnings_list = []

    # Check required columns
    if dbh_col not in df.columns:
        errors.append(f"Missing required column: {dbh_col}")
        return {"errors": errors, "warnings": [], "stats": {}}

    # Check DBH values
    dbh = df[dbh_col]
    if dbh.isna().any():
        errors.append(f"{dbh.isna().sum()} rows have missing DBH values")
    if (dbh <= 0).any():
        errors.append(f"{(dbh <= 0).sum()} rows have non-positive DBH values")
    if (dbh > 300).any():
        warnings_list.append(
            f"{(dbh > 300).sum()} trees have DBH > 300 cm (unusually large)"
        )

    # Check height values if present
    if height_col and height_col in df.columns:
        height = df[height_col]
        if height.isna().any():
            warnings_list.append(f"{height.isna().sum()} rows have missing height values")
        if (height <= 0).any():
            errors.append(f"{(height <= 0).sum()} rows have non-positive height values")
        if (height > 80).any():
            warnings_list.append(
                f"{(height > 80).sum()} trees have height > 80 m (unusually tall)"
            )

        # Check height-DBH ratio
        ratio = height / dbh
        if (ratio > 2).any():
            warnings_list.append(
                f"{(ratio > 2).sum()} trees have height/DBH ratio > 2 (unusual)"
            )

    # Check species
    if species_col in df.columns:
        species = df[species_col]
        if species.isna().any():
            warnings_list.append(f"{species.isna().sum()} rows have missing species")

        # Check species format
        valid_format = species.str.contains(r"^[A-Z]{4}\.[A-Z]{3}", na=False)
        if not valid_format.all():
            warnings_list.append(
                f"{(~valid_format).sum()} species codes don't match expected format (XXXX.XXX)"
            )

    # Summary stats
    stats = {
        "n_trees": len(df),
        "dbh_min": float(dbh.min()) if not dbh.empty else None,
        "dbh_max": float(dbh.max()) if not dbh.empty else None,
        "dbh_mean": float(dbh.mean()) if not dbh.empty else None,
    }

    if height_col and height_col in df.columns:
        height = df[height_col]
        stats["height_min"] = float(height.min()) if not height.empty else None
        stats["height_max"] = float(height.max()) if not height.empty else None
        stats["height_mean"] = float(height.mean()) if not height.empty else None

    if species_col in df.columns:
        stats["n_species"] = df[species_col].nunique()
        stats["species_list"] = df[species_col].unique().tolist()[:10]  # First 10

    return {
        "errors": errors,
        "warnings": warnings_list,
        "stats": stats,
        "is_valid": len(errors) == 0,
    }

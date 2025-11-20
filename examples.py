#!/usr/bin/env python3
"""
Example usage of the CTAE Python package.

This script demonstrates how to use the main functions of the CTAE package
for calculating tree biomass, volume, and other forestry attributes.
"""

import ctae
import numpy as np
import pandas as pd

print("=" * 70)
print("CTAE - Canadian Tree Allometric Equations - Examples")
print("=" * 70)
print()

# Example 1: Calculate aboveground biomass from DBH
print("Example 1: Calculate aboveground biomass from DBH")
print("-" * 70)
result = ctae.AGB_LambertUngDBH(DBH=20, species="PINU.CON")
print(f"Tree with DBH=20cm, species=PINU.CON (Lodgepole Pine)")
print(f"  Total biomass: {result['Btotal']:.2f} kg")
print(f"  Wood biomass: {result['Bwood']:.2f} kg")
print(f"  Bark biomass: {result['Bbark']:.2f} kg")
print(f"  Foliage biomass: {result['Bfoliage']:.2f} kg")
print(f"  Branch biomass: {result['Bbranches']:.2f} kg")
print()

# Example 2: Calculate aboveground biomass from DBH and height
print("Example 2: Calculate aboveground biomass from DBH and height")
print("-" * 70)
result = ctae.AGB_LambertUngDBHHT(DBH=20, height=17, species="PINU.CON")
print(f"Tree with DBH=20cm, height=17m, species=PINU.CON")
print(f"  Total biomass: {result['Btotal']:.2f} kg")
print()

# Example 3: Calculate tree volume (Huang model for Alberta)
print("Example 3: Calculate tree volume (Huang model for Alberta)")
print("-" * 70)
result = ctae.V_Huang(DBH=20, height=20, species="PICE.GLA", subregion="Province")
print(f"Tree with DBH=20cm, height=20m, species=PICE.GLA (White Spruce)")
print(f"  Merchantable volume: {result['v_merch']:.4f} m³")
print(f"  Total volume: {result['v_total']:.4f} m³")
print()

# Example 4: Volume-to-biomass conversion
print("Example 4: Volume-to-biomass conversion")
print("-" * 70)
result = ctae.V2B(volume=350, species="PINU.CON", jurisdiction="BC", ecozone=4)
print(f"Stand with volume=350 m³/ha, species=PINU.CON, BC, ecozone 4")
print(f"  Total biomass: {result['b_total']:.2f} tonnes/ha")
print(f"  Merchantable stem wood: {result['b_m']:.2f} tonnes/ha")
print(f"  Bark biomass: {result['b_bark']:.2f} tonnes/ha")
print(f"  Branch biomass: {result['b_branches']:.2f} tonnes/ha")
print(f"  Foliage biomass: {result['b_foliage']:.2f} tonnes/ha")
print()

# Example 5: Total to merchantable volume conversion
print("Example 5: Total to merchantable volume conversion")
print("-" * 70)
result = ctae.Vtot2Vmerch(
    total_volume=300, species="PINU.CON", jurisdiction="AB", ecozone=4
)
print(f"Stand with total volume=300 m³/ha, species=PINU.CON, AB, ecozone 4")
print(f"  Merchantable volume: {result:.2f} m³/ha")
print()

# Example 6: AGB proportions
print("Example 6: Calculate biomass proportions")
print("-" * 70)
result = ctae.AGB_prop(
    value_input=350, value_type="vol", species="PINU.CON", 
    jurisdiction="BC", ecozone=4
)
print(f"Stand with volume=350 m³/ha, species=PINU.CON, BC, ecozone 4")
print(f"  Stem wood proportion: {result['Pstemwood']:.4f} ({result['Pstemwood']*100:.2f}%)")
print(f"  Bark proportion: {result['Pbark']:.4f} ({result['Pbark']*100:.2f}%)")
print(f"  Branch proportion: {result['Pbranches']:.4f} ({result['Pbranches']*100:.2f}%)")
print(f"  Foliage proportion: {result['Pfoliage']:.4f} ({result['Pfoliage']*100:.2f}%)")
print()

# Example 7: Growth and yield model
print("Example 7: Growth and yield model (Ung 2009)")
print("-" * 70)
result = ctae.Ung2009(
    species="ABIE.BAL", age=range(10, 101, 10), GDD=1500, PREC=800, model="both"
)
print(f"Stand growth projection for ABIE.BAL (Balsam Fir)")
print(f"  GDD=1500, PREC=800")
print()
print(result.to_string(index=False))
print()

# Example 8: Multiple trees
print("Example 8: Calculate biomass for multiple trees")
print("-" * 70)
dbh_values = np.array([10, 15, 20, 25, 30])
result = ctae.AGB_LambertUngDBH(DBH=dbh_values, species="PINU.CON")
print(f"Trees with DBH={list(dbh_values)} cm, species=PINU.CON")
print(f"  Total biomass: {result['Btotal']}")
print()

# Example 9: Urban ecosystem services estimation
print("Example 9: Urban ecosystem services estimation")
print("-" * 70)
# Create a sample tree dataset
tree_data = pd.DataFrame({
    "ID_Arbre": [1, 2, 3],
    "DHP": [25.0, 35.0, 45.0],
    "Essence_latin": ["Acer saccharum", "Acer saccharum", "Acer rubrum"]
})

# Define species mapping for CTAE
def map_species_to_ctae(latin_name):
    """Map Latin species names to CTAE species codes."""
    mapping = {
        "Acer saccharum": "ACER.SAC",
        "Acer rubrum": "ACER.RUB",
    }
    return mapping.get(latin_name, None)

# Calculate ecosystem services for all trees
params = {
    "map_species_to_ctae": map_species_to_ctae,
    "annual_rainfall_mm": 1000.0,  # Montreal typical
    "carbon_price": 75.0,  # USD per ton
}
results = ctae.estimate_values_for_dataframe(tree_data, ctae_module=ctae, params=params)

print(f"Urban ecosystem services for {len(tree_data)} trees:")
print()
print(results[['ID_Arbre', 'biomass_kg', 'canopy_area_m2', 'total_value_usd']].to_string(index=False))
print()
print(f"Total ecosystem value: ${results['total_value_usd'].sum():.2f}")
print()

print("=" * 70)
print("For more information, see README_PYTHON.md")
print("=" * 70)

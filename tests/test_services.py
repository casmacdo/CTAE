"""Tests for the services module."""
import sys
sys.path.insert(0, '/home/runner/work/CTAE/CTAE')

import ctae
import pandas as pd


def test_estimate_canopy_area():
    """Test estimate_canopy_area function."""
    print("Testing estimate_canopy_area...")
    
    # Test with species in lookup
    area, method = ctae.estimate_canopy_area(DBH_cm=30, species="Acer saccharum")
    print(f"  DBH=30cm, species=Acer saccharum:")
    print(f"    Canopy area: {area:.2f} m²")
    print(f"    Method: {method}")
    assert area > 0, "Canopy area should be positive"
    assert method == "species", "Should use species-specific data"
    
    # Test with generic species
    area, method = ctae.estimate_canopy_area(DBH_cm=30, species="Unknown species")
    print(f"  DBH=30cm, species=Unknown species:")
    print(f"    Canopy area: {area:.2f} m²")
    print(f"    Method: {method}")
    assert area > 0, "Canopy area should be positive"
    assert method == "generic", "Should use generic data"
    
    # Test with zero DBH
    area, method = ctae.estimate_canopy_area(DBH_cm=0, species="Acer saccharum")
    print(f"  DBH=0cm:")
    print(f"    Canopy area: {area:.2f} m²")
    print(f"    Method: {method}")
    assert area == 0.0, "Zero DBH should return zero area"
    assert method == "invalid_dbh", "Should indicate invalid DBH"
    
    print("  ✓ Passed")


def test_estimate_stormwater_interception():
    """Test estimate_stormwater_interception function."""
    print("Testing estimate_stormwater_interception...")
    
    volume, value = ctae.estimate_stormwater_interception(
        canopy_area_m2=50.0,
        species="Acer saccharum"
    )
    print(f"  Canopy area=50 m², species=Acer saccharum:")
    print(f"    Volume intercepted: {volume:.2f} m³/year")
    print(f"    Stormwater value: ${value:.2f}/year")
    assert volume > 0, "Volume should be positive"
    assert value > 0, "Value should be positive"
    
    # Test with zero canopy
    volume, value = ctae.estimate_stormwater_interception(canopy_area_m2=0)
    assert volume == 0.0, "Zero canopy should return zero volume"
    assert value == 0.0, "Zero canopy should return zero value"
    
    print("  ✓ Passed")


def test_estimate_cooling_savings():
    """Test estimate_cooling_savings function."""
    print("Testing estimate_cooling_savings...")
    
    kwh, value = ctae.estimate_cooling_savings(canopy_area_m2=50.0)
    print(f"  Canopy area=50 m²:")
    print(f"    kWh saved: {kwh:.2f} kWh/year")
    print(f"    Cooling value: ${value:.2f}/year")
    assert kwh > 0, "kWh should be positive"
    assert value > 0, "Value should be positive"
    
    # Test with proximity factor
    kwh2, value2 = ctae.estimate_cooling_savings(
        canopy_area_m2=50.0,
        proximity_factor=0.5
    )
    print(f"  Canopy area=50 m², proximity_factor=0.5:")
    print(f"    kWh saved: {kwh2:.2f} kWh/year")
    assert kwh2 == kwh * 0.5, "Proximity factor should scale result"
    
    print("  ✓ Passed")


def test_estimate_pollution_removal():
    """Test estimate_pollution_removal function."""
    print("Testing estimate_pollution_removal...")
    
    pollutants, value = ctae.estimate_pollution_removal(canopy_area_m2=50.0)
    print(f"  Canopy area=50 m²:")
    print(f"    Pollutants removed: {pollutants}")
    print(f"    Pollution value: ${value:.2f}/year")
    assert len(pollutants) > 0, "Should have pollutants"
    assert value > 0, "Value should be positive"
    assert "PM2.5" in pollutants, "Should include PM2.5"
    assert "NO2" in pollutants, "Should include NO2"
    
    print("  ✓ Passed")


def test_estimate_total_value():
    """Test estimate_total_value function."""
    print("Testing estimate_total_value...")
    
    tree_row = {
        "DHP": 30.0,
        "Essence_latin": "Acer saccharum"
    }
    
    # Provide a mapping function from Latin names to CTAE codes
    def map_species(latin_name):
        mapping = {
            "Acer saccharum": "ACER.SAC",
            "Tilia americana": "TILIA.AM",
            "Acer platanoides": "ACER.PLA",
        }
        return mapping.get(latin_name, None)
    
    params = {"map_species_to_ctae": map_species}
    result = ctae.estimate_total_value(tree_row, ctae_module=ctae, params=params)
    
    print(f"  Tree: DBH=30cm, species=Acer saccharum")
    print(f"    Biomass: {result['biomass_kg']:.2f} kg")
    print(f"    Carbon: {result['carbon_tons']:.3f} tons")
    print(f"    Carbon value: ${result['carbon_value_usd']:.2f}")
    print(f"    Canopy area: {result['canopy_area_m2']:.2f} m²")
    print(f"    Stormwater value: ${result['stormwater_value_usd']:.2f}/year")
    print(f"    Cooling value: ${result['cooling_value_usd']:.2f}/year")
    print(f"    Pollution value: ${result['pollution_value_usd']:.2f}/year")
    print(f"    Total value: ${result['total_value_usd']:.2f}")
    
    assert result['biomass_kg'] > 0, "Biomass should be positive"
    assert result['carbon_tons'] > 0, "Carbon should be positive"
    assert result['total_value_usd'] > 0, "Total value should be positive"
    assert result['canopy_method'] == 'species', "Should use species-specific method"
    
    print("  ✓ Passed")


def test_estimate_values_for_dataframe():
    """Test estimate_values_for_dataframe function."""
    print("Testing estimate_values_for_dataframe...")
    
    # Create sample dataframe with species that exist in CTAE
    df = pd.DataFrame({
        "ID_Arbre": [1, 2, 3],
        "DHP": [20.0, 30.0, 40.0],
        "Essence_latin": ["Acer saccharum", "Acer saccharum", "Acer rubrum"]
    })
    
    # Provide a mapping function from Latin names to CTAE codes
    def map_species(latin_name):
        mapping = {
            "Acer saccharum": "ACER.SAC",
            "Acer rubrum": "ACER.RUB",
        }
        return mapping.get(latin_name, None)
    
    params = {"map_species_to_ctae": map_species}
    result_df = ctae.estimate_values_for_dataframe(df, ctae_module=ctae, params=params)
    
    print(f"  Input: {len(df)} trees")
    print(f"  Output: {len(result_df)} rows")
    print(f"  Columns: {list(result_df.columns)}")
    print(f"  Sample results:")
    print(result_df[['ID_Arbre', 'biomass_kg', 'total_value_usd']].to_string(index=False))
    
    assert len(result_df) == len(df), "Should have same number of rows"
    assert 'biomass_kg' in result_df.columns, "Should have biomass_kg column"
    assert 'total_value_usd' in result_df.columns, "Should have total_value_usd column"
    assert all(result_df['biomass_kg'] > 0), "All biomass values should be positive"
    assert all(result_df['total_value_usd'] > 0), "All total values should be positive"
    
    print("  ✓ Passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running CTAE Services Module Tests")
    print("="*60 + "\n")
    
    test_estimate_canopy_area()
    print()
    test_estimate_stormwater_interception()
    print()
    test_estimate_cooling_savings()
    print()
    test_estimate_pollution_removal()
    print()
    test_estimate_total_value()
    print()
    test_estimate_values_for_dataframe()
    
    print("\n" + "="*60)
    print("All services tests passed! ✓")
    print("="*60)

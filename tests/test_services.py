"""Tests for the services module using pytest."""
import pytest
import pandas as pd

import ctae


class TestEstimateCanopyArea:
    """Tests for estimate_canopy_area function."""

    def test_species_in_lookup(self):
        """Test with species in lookup table."""
        area, method = ctae.estimate_canopy_area(DBH_cm=30, species="Acer saccharum")
        assert area > 0, "Canopy area should be positive"
        assert method == "species", "Should use species-specific data"

    def test_generic_species(self):
        """Test with species not in lookup table."""
        area, method = ctae.estimate_canopy_area(DBH_cm=30, species="Unknown species")
        assert area > 0, "Canopy area should be positive"
        assert method == "generic", "Should use generic data"

    def test_zero_dbh(self):
        """Test with zero DBH returns zero area."""
        area, method = ctae.estimate_canopy_area(DBH_cm=0, species="Acer saccharum")
        assert area == 0.0, "Zero DBH should return zero area"
        assert method == "invalid_dbh", "Should indicate invalid DBH"

    def test_negative_dbh(self):
        """Test with negative DBH returns zero area."""
        area, method = ctae.estimate_canopy_area(DBH_cm=-10, species="Acer saccharum")
        assert area == 0.0, "Negative DBH should return zero area"
        assert method == "invalid_dbh", "Should indicate invalid DBH"


class TestEstimateStormwaterInterception:
    """Tests for estimate_stormwater_interception function."""

    def test_basic_calculation(self):
        """Test basic stormwater interception calculation."""
        volume, value = ctae.estimate_stormwater_interception(
            canopy_area_m2=50.0,
            species="Acer saccharum"
        )
        assert volume > 0, "Volume should be positive"
        assert value > 0, "Value should be positive"

    def test_zero_canopy(self):
        """Test with zero canopy area."""
        volume, value = ctae.estimate_stormwater_interception(canopy_area_m2=0)
        assert volume == 0.0, "Zero canopy should return zero volume"
        assert value == 0.0, "Zero canopy should return zero value"

    def test_custom_parameters(self):
        """Test with custom parameters."""
        volume, value = ctae.estimate_stormwater_interception(
            canopy_area_m2=50.0,
            annual_rainfall_mm=500.0,
            interception_rate=0.5,
            stormwater_cost_per_m3=2.0
        )
        # Expected: 50 * (500/1000) * 0.5 = 12.5 m3
        assert abs(volume - 12.5) < 0.01, "Volume calculation incorrect"
        # Expected: 12.5 * 2.0 = 25.0
        assert abs(value - 25.0) < 0.01, "Value calculation incorrect"


class TestEstimateCoolingSavings:
    """Tests for estimate_cooling_savings function."""

    def test_basic_calculation(self):
        """Test basic cooling savings calculation."""
        kwh, value = ctae.estimate_cooling_savings(canopy_area_m2=50.0)
        assert kwh > 0, "kWh should be positive"
        assert value > 0, "Value should be positive"

    def test_proximity_factor(self):
        """Test with proximity factor."""
        kwh1, _ = ctae.estimate_cooling_savings(canopy_area_m2=50.0, proximity_factor=1.0)
        kwh2, _ = ctae.estimate_cooling_savings(canopy_area_m2=50.0, proximity_factor=0.5)
        assert abs(kwh2 - kwh1 * 0.5) < 0.01, "Proximity factor should scale result"

    def test_zero_canopy(self):
        """Test with zero canopy area."""
        kwh, value = ctae.estimate_cooling_savings(canopy_area_m2=0)
        assert kwh == 0.0, "Zero canopy should return zero kWh"
        assert value == 0.0, "Zero canopy should return zero value"


class TestEstimatePollutionRemoval:
    """Tests for estimate_pollution_removal function."""

    def test_basic_calculation(self):
        """Test basic pollution removal calculation."""
        pollutants, value = ctae.estimate_pollution_removal(canopy_area_m2=50.0)
        assert len(pollutants) > 0, "Should have pollutants"
        assert value > 0, "Value should be positive"
        assert "PM2.5" in pollutants, "Should include PM2.5"
        assert "NO2" in pollutants, "Should include NO2"

    def test_zero_canopy(self):
        """Test with zero canopy area."""
        pollutants, value = ctae.estimate_pollution_removal(canopy_area_m2=0)
        assert len(pollutants) == 0, "Zero canopy should return empty pollutants"
        assert value == 0.0, "Zero canopy should return zero value"

    def test_custom_rates(self):
        """Test with custom removal rates."""
        custom_rates = {"CO2": 0.01}
        custom_values = {"CO2": 10.0}
        pollutants, value = ctae.estimate_pollution_removal(
            canopy_area_m2=100.0,
            removal_rates=custom_rates,
            values_per_kg=custom_values
        )
        assert "CO2" in pollutants, "Should include custom pollutant"
        # Expected: 100 * 0.01 = 1 kg, value = 1 * 10 = 10
        assert abs(pollutants["CO2"] - 1.0) < 0.01
        assert abs(value - 10.0) < 0.01


class TestEstimateTotalValue:
    """Tests for estimate_total_value function."""

    @pytest.fixture
    def species_mapper(self):
        """Provide a mapping function from Latin names to CTAE codes."""
        def map_species(latin_name):
            mapping = {
                "Acer saccharum": "ACER.SAC",
                "Tilia americana": "TILIA.AM",
                "Acer platanoides": "ACER.PLA",
                "Acer rubrum": "ACER.RUB",
            }
            return mapping.get(latin_name, None)
        return map_species

    def test_basic_calculation(self, species_mapper):
        """Test basic total value calculation."""
        tree_row = {
            "DHP": 30.0,
            "Essence_latin": "Acer saccharum"
        }
        params = {"map_species_to_ctae": species_mapper}
        result = ctae.estimate_total_value(tree_row, ctae_module=ctae, params=params)

        assert result["biomass_kg"] > 0, "Biomass should be positive"
        assert result["carbon_tons"] > 0, "Carbon should be positive"
        assert result["total_value_usd"] > 0, "Total value should be positive"
        assert result["canopy_method"] == "species", "Should use species-specific method"

    def test_all_fields_returned(self, species_mapper):
        """Test that all expected fields are returned."""
        tree_row = {"DHP": 30.0, "Essence_latin": "Acer saccharum"}
        params = {"map_species_to_ctae": species_mapper}
        result = ctae.estimate_total_value(tree_row, ctae_module=ctae, params=params)

        expected_keys = [
            "biomass_kg", "carbon_tons", "carbon_value_usd", "canopy_area_m2",
            "stormwater_value_usd", "cooling_value_usd", "pollution_value_usd",
            "total_value_usd", "assumptions"
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"


class TestEstimateValuesForDataframe:
    """Tests for estimate_values_for_dataframe function."""

    @pytest.fixture
    def species_mapper(self):
        """Provide a mapping function from Latin names to CTAE codes."""
        def map_species(latin_name):
            mapping = {
                "Acer saccharum": "ACER.SAC",
                "Acer rubrum": "ACER.RUB",
            }
            return mapping.get(latin_name, None)
        return map_species

    def test_basic_dataframe(self, species_mapper):
        """Test with basic DataFrame."""
        df = pd.DataFrame({
            "ID_Arbre": [1, 2, 3],
            "DHP": [20.0, 30.0, 40.0],
            "Essence_latin": ["Acer saccharum", "Acer saccharum", "Acer rubrum"]
        })

        params = {"map_species_to_ctae": species_mapper}
        result_df = ctae.estimate_values_for_dataframe(df, ctae_module=ctae, params=params)

        assert len(result_df) == len(df), "Should have same number of rows"
        assert "biomass_kg" in result_df.columns, "Should have biomass_kg column"
        assert "total_value_usd" in result_df.columns, "Should have total_value_usd column"
        assert all(result_df["biomass_kg"] > 0), "All biomass values should be positive"
        assert all(result_df["total_value_usd"] > 0), "All total values should be positive"

"""Basic tests for CTAE package using pytest."""
import numpy as np
import pytest

import ctae


class TestAGBLambertUngDBH:
    """Tests for AGB_LambertUngDBH function."""

    def test_single_value(self):
        """Test with single DBH value."""
        result = ctae.AGB_LambertUngDBH(20, species="PINU.CON")
        assert result["Btotal"] > 0, "Btotal should be positive"

    def test_array_input(self):
        """Test with array input."""
        result = ctae.AGB_LambertUngDBH(np.array([10, 20, 30]), species="PINU.CON")
        assert len(result["Btotal"]) == 3, "Should have 3 results"
        assert all(result["Btotal"] > 0), "All Btotal values should be positive"

    def test_all_components_returned(self):
        """Test that all biomass components are returned."""
        result = ctae.AGB_LambertUngDBH(20, species="PINU.CON")
        expected_keys = ["Bwood", "Bbark", "Bstem", "Bfoliage", "Bbranches", "Bcrown", "Btotal"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_invalid_species_raises(self):
        """Test that invalid species raises ValueError."""
        with pytest.raises(ValueError, match="Wrong species"):
            ctae.AGB_LambertUngDBH(20, species="INVALID.SPP")


class TestAGBLambertUngDBHHT:
    """Tests for AGB_LambertUngDBHHT function."""

    def test_single_value(self):
        """Test with single DBH and height value."""
        result = ctae.AGB_LambertUngDBHHT(20, 17, species="PINU.CON")
        assert result["Btotal"] > 0, "Btotal should be positive"

    def test_all_components_returned(self):
        """Test that all biomass components are returned."""
        result = ctae.AGB_LambertUngDBHHT(20, 17, species="PINU.CON")
        expected_keys = ["Bwood", "Bbark", "Bstem", "Bfoliage", "Bbranches", "Bcrown", "Btotal"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"


class TestVHuang:
    """Tests for V_Huang function."""

    def test_single_value(self):
        """Test with single DBH and height value."""
        result = ctae.V_Huang(20, 20, "PICE.GLA")
        assert result["v_merch"] > 0, "v_merch should be positive"
        assert result["v_total"] > result["v_merch"], "v_total should be greater than v_merch"

    def test_subregion_parameter(self):
        """Test with subregion parameter."""
        result = ctae.V_Huang(20, 20, "PICE.GLA", subregion="CP")
        assert result["v_merch"] > 0, "v_merch should be positive"

    def test_invalid_species_raises(self):
        """Test that invalid species raises ValueError."""
        with pytest.raises(ValueError, match="No model parameters available"):
            ctae.V_Huang(20, 20, "INVALID.SPP")


class TestV2B:
    """Tests for V2B function."""

    def test_single_value(self):
        """Test with single volume value."""
        result = ctae.V2B(350, species="PINU.CON", jurisdiction="BC", ecozone=4)
        assert result["b_total"] > 0, "b_total should be positive"

    def test_all_components_returned(self):
        """Test that all biomass components are returned."""
        result = ctae.V2B(350, species="PINU.CON", jurisdiction="BC", ecozone=4)
        expected_keys = ["b_m", "b_n", "b_nm", "b_s", "b_total", "b_bark", "b_branches", "b_foliage"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_invalid_species_format_raises(self):
        """Test that invalid species format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid species format"):
            ctae.V2B(350, species="INVALID", jurisdiction="BC", ecozone=4)


class TestVtot2Vmerch:
    """Tests for Vtot2Vmerch function."""

    def test_single_value(self):
        """Test with single volume value."""
        result = ctae.Vtot2Vmerch(300, species="PINU.CON", jurisdiction="AB", ecozone=4)
        assert result > 0, "merchantable_volume should be positive"
        assert result <= 300, "merchantable_volume should be <= total_volume"


class TestAGBProp:
    """Tests for AGB_prop function."""

    def test_proportions_sum_to_one(self):
        """Test that proportions sum to 1."""
        result = ctae.AGB_prop(350, value_type="vol", species="PINU.CON", jurisdiction="BC", ecozone=4)
        total_prop = result["Pstemwood"] + result["Pbark"] + result["Pbranches"] + result["Pfoliage"]
        assert abs(total_prop - 1.0) < 0.001, "Proportions should sum to 1"

    def test_all_proportions_returned(self):
        """Test that all proportion components are returned."""
        result = ctae.AGB_prop(350, value_type="vol", species="PINU.CON", jurisdiction="BC", ecozone=4)
        expected_keys = ["Pstemwood", "Pbark", "Pbranches", "Pfoliage"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_invalid_value_type_raises(self):
        """Test that invalid value_type raises ValueError."""
        with pytest.raises(ValueError, match="Must specify what is the type of input"):
            ctae.AGB_prop(350, value_type="invalid", species="PINU.CON", jurisdiction="BC", ecozone=4)


class TestUng2009:
    """Tests for Ung2009 function."""

    def test_basic_usage(self):
        """Test basic usage with default model."""
        result = ctae.Ung2009(species="ABIE.BAL", age=range(1, 10), GDD=1500, PREC=800)
        assert len(result) == 9, "Should have 9 rows"
        assert "H" in result.columns, "Should have H column"
        assert "V" in result.columns, "Should have V column"
        assert "V2" in result.columns, "Should have V2 column"

    def test_nat1_model_only(self):
        """Test using only Nat1 model."""
        result = ctae.Ung2009(species="ABIE.BAL", age=range(1, 10), GDD=1500, PREC=800, model="Nat1")
        assert "H" in result.columns, "Should have H column"
        assert "V" in result.columns, "Should have V column"
        assert "V2" not in result.columns, "Should not have V2 column"

    def test_nat2_model_only(self):
        """Test using only Nat2 model."""
        result = ctae.Ung2009(species="ABIE.BAL", age=range(1, 10), GDD=1500, PREC=800, model="Nat2")
        assert "V2" in result.columns, "Should have V2 column"
        assert "H" not in result.columns, "Should not have H column"

    def test_invalid_species_raises(self):
        """Test that invalid species raises ValueError."""
        with pytest.raises(ValueError, match="Invalid species"):
            ctae.Ung2009(species="INVALID.SPP", age=range(1, 10), GDD=1500, PREC=800)

    def test_invalid_model_raises(self):
        """Test that invalid model raises ValueError."""
        with pytest.raises(ValueError, match="model must be one of"):
            ctae.Ung2009(species="ABIE.BAL", age=range(1, 10), GDD=1500, PREC=800, model="invalid")

    def test_zero_age_raises(self):
        """Test that zero or negative age raises ValueError."""
        with pytest.raises(ValueError, match="Age must be greater than 0"):
            ctae.Ung2009(species="ABIE.BAL", age=[0, 1, 2], GDD=1500, PREC=800)

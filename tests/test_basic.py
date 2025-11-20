"""Basic tests for CTAE package."""
import sys
sys.path.insert(0, '/home/runner/work/CTAE/CTAE')

import numpy as np
import ctae


def test_agb_lambert_ung_dbh():
    """Test AGB_LambertUngDBH function."""
    print("Testing AGB_LambertUngDBH...")
    result = ctae.AGB_LambertUngDBH(20, species="PINU.CON")
    print(f"  DBH=20, species=PINU.CON:")
    print(f"    Btotal: {result['Btotal']}")
    assert result['Btotal'] > 0, "Btotal should be positive"
    
    # Test with array input
    result = ctae.AGB_LambertUngDBH(np.array([10, 20, 30]), species="PINU.CON")
    print(f"  DBH=[10, 20, 30], species=PINU.CON:")
    print(f"    Btotal: {result['Btotal']}")
    assert len(result['Btotal']) == 3, "Should have 3 results"
    print("  ✓ Passed")


def test_agb_lambert_ung_dbhht():
    """Test AGB_LambertUngDBHHT function."""
    print("Testing AGB_LambertUngDBHHT...")
    result = ctae.AGB_LambertUngDBHHT(20, 17, species="PINU.CON")
    print(f"  DBH=20, height=17, species=PINU.CON:")
    print(f"    Btotal: {result['Btotal']}")
    assert result['Btotal'] > 0, "Btotal should be positive"
    print("  ✓ Passed")


def test_v_huang():
    """Test V_Huang function."""
    print("Testing V_Huang...")
    result = ctae.V_Huang(20, 20, "PICE.GLA")
    print(f"  DBH=20, height=20, species=PICE.GLA:")
    print(f"    v_merch: {result['v_merch']}")
    print(f"    v_total: {result['v_total']}")
    assert result['v_merch'] > 0, "v_merch should be positive"
    assert result['v_total'] > result['v_merch'], "v_total should be greater than v_merch"
    print("  ✓ Passed")


def test_v2b():
    """Test V2B function."""
    print("Testing V2B...")
    result = ctae.V2B(350, species="PINU.CON", jurisdiction="BC", ecozone=4)
    print(f"  volume=350, species=PINU.CON, jurisdiction=BC, ecozone=4:")
    print(f"    b_total: {result['b_total']}")
    assert result['b_total'] > 0, "b_total should be positive"
    print("  ✓ Passed")


def test_vtot2vmerch():
    """Test Vtot2Vmerch function."""
    print("Testing Vtot2Vmerch...")
    result = ctae.Vtot2Vmerch(300, species="PINU.CON", jurisdiction="AB", ecozone=4)
    print(f"  total_volume=300, species=PINU.CON, jurisdiction=AB, ecozone=4:")
    print(f"    merchantable_volume: {result}")
    assert result > 0, "merchantable_volume should be positive"
    assert result <= 300, "merchantable_volume should be <= total_volume"
    print("  ✓ Passed")


def test_agb_prop():
    """Test AGB_prop function."""
    print("Testing AGB_prop...")
    result = ctae.AGB_prop(350, value_type="vol", species="PINU.CON", jurisdiction="BC", ecozone=4)
    print(f"  value=350, value_type=vol, species=PINU.CON, jurisdiction=BC, ecozone=4:")
    print(f"    Pstemwood: {result['Pstemwood']}")
    print(f"    Pbark: {result['Pbark']}")
    print(f"    Pbranches: {result['Pbranches']}")
    print(f"    Pfoliage: {result['Pfoliage']}")
    total_prop = result['Pstemwood'] + result['Pbark'] + result['Pbranches'] + result['Pfoliage']
    print(f"    Total proportion: {total_prop}")
    assert abs(total_prop - 1.0) < 0.001, "Proportions should sum to 1"
    print("  ✓ Passed")


def test_ung2009():
    """Test Ung2009 function."""
    print("Testing Ung2009...")
    result = ctae.Ung2009(species="ABIE.BAL", age=range(1, 10), GDD=1500, PREC=800)
    print(f"  species=ABIE.BAL, age=1-9, GDD=1500, PREC=800:")
    print(f"    Number of rows: {len(result)}")
    print(f"    Columns: {list(result.columns)}")
    print(f"    First few rows:")
    print(result.head())
    assert len(result) == 9, "Should have 9 rows"
    assert 'H' in result.columns, "Should have H column"
    assert 'V' in result.columns, "Should have V column"
    assert 'V2' in result.columns, "Should have V2 column"
    print("  ✓ Passed")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running CTAE Package Tests")
    print("="*60 + "\n")
    
    test_agb_lambert_ung_dbh()
    print()
    test_agb_lambert_ung_dbhht()
    print()
    test_v_huang()
    print()
    test_v2b()
    print()
    test_vtot2vmerch()
    print()
    test_agb_prop()
    print()
    test_ung2009()
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)

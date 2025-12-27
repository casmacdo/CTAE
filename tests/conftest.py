"""Pytest configuration and shared fixtures for CTAE tests."""
import pytest
import numpy as np


@pytest.fixture
def sample_dbh_values():
    """Provide sample DBH values for testing."""
    return np.array([10, 20, 30, 40, 50])


@pytest.fixture
def sample_height_values():
    """Provide sample height values for testing."""
    return np.array([10, 15, 20, 22, 25])


@pytest.fixture
def conifer_species():
    """Provide common conifer species codes."""
    return ["PINU.CON", "PICE.GLA", "PICE.MAR", "ABIE.BAL"]


@pytest.fixture
def deciduous_species():
    """Provide common deciduous species codes."""
    return ["POPU.TRE", "BETU.PAP", "ACER.SAC", "ACER.RUB"]

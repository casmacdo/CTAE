# CTAE - Canadian Tree Allometric Equations

A Python package providing tools to calculate tree- or stand-level attributes developed for Canadian forests.

## Models Included

- Canadian national tree aboveground biomass equations (Lambert et al. 2005, Ung et al. 2008)
- Individual tree volume equations for major Alberta tree species (Huang 1994)
- Volume-to-biomass conversions models (Boudewyn et al. 2007)
- Total volume to merchantable volume conversions models (Boudewyn et al. 2007)
- Simple growth and yield model (H, BA, V) (Ung et al. 2009)

Updated model parameters for models developed by Boudewyn et al (2007) downloaded from <https://nfi.nfis.org/en/biomass_models>.

## Installation

Install the package using pip:

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
import ctae

# Calculate tree aboveground biomass using DBH
result = ctae.AGB_LambertUngDBH(DBH=20, species="PINU.CON")
print(result)
# Output: {'Btotal': 131.84, 'Bstem': 80.21, 'Bbark': 13.46, 'Bbranch': 25.88, 'Bfoliage': 12.29}

# Calculate tree aboveground biomass using DBH and height
result = ctae.AGB_LambertUngDBHHT(DBH=20, height=17, species="PINU.CON")
print(result)
# Output: {'Btotal': 135.91, 'Bstem': 82.70, 'Bbark': 13.88, 'Bbranch': 26.69, 'Bfoliage': 12.67}

# Calculate tree volume (Huang model for Alberta species)
result = ctae.V_Huang(DBH=20, height=20, species="PICE.GLA", subregion="CP")
print(result)
# Output: {'v_merch': 0.2532, 'v_total': 0.2641}

# Volume-to-biomass conversion
result = ctae.V2B(volume=350, species="PINU.CON", jurisdiction="BC", ecozone=4)
print(result)
# Output: {'b_merch': 180.64, 'b_other': 26.20, 'b_total': 206.84}

# Total volume to merchantable volume conversion
result = ctae.Vtot2Vmerch(total_volume=350, species="PINU.CON", jurisdiction="BC", ecozone=4)
print(result)
# Output: {'v_merch': 295.23}

# Biomass proportions
result = ctae.AGB_prop(value_input=200, value_type="biomass", species="PINU.CON", 
                       jurisdiction="BC", ecozone=4)
print(result)

# Growth and yield model
import numpy as np
ages = np.arange(1, 151)
result = ctae.Ung2009(species="ABIE.BAL", age=ages, GDD=1500, PREC=800, model="all")
print(result.keys())
# Output: dict_keys(['age', 'H', 'BA', 'V'])
```

## Available Functions

### Biomass Equations

- **`AGB_LambertUngDBH(DBH, species)`** - Calculate tree aboveground biomass from diameter at breast height (DBH)
- **`AGB_LambertUngDBHHT(DBH, height, species)`** - Calculate tree aboveground biomass from DBH and height
- **`AGB_prop(value_input, value_type, species, jurisdiction, ecozone)`** - Calculate biomass component proportions

### Volume Equations

- **`V_Huang(DBH, height, species, subregion=None)`** - Calculate tree volume for Alberta tree species

### Conversion Functions

- **`V2B(volume, species, jurisdiction, ecozone)`** - Convert volume to biomass
- **`Vtot2Vmerch(total_volume, species, jurisdiction, ecozone)`** - Convert total volume to merchantable volume

### Growth Models

- **`Ung2009(species, age, GDD, PREC, model="all")`** - Simple growth and yield model (Height, Basal Area, Volume)

## Examples

See `examples.py` for more comprehensive usage examples.

## Data

The package includes parameter data files in CSV format located in `ctae/data/`. These files contain species-specific coefficients for the various allometric equations.

## References

Boudewyn, P.A.; Song, X.; Magnussen, S.; Gillis, M.D. (2007). Model-based, volume-to-biomass conversion for forested and vegetated land in Canada. Natural Resources Canada, Canadian Forest Service, Pacific Forestry Centre, Victoria, BC. Information Report BC-X-411. 112 p.

Huang, S. (1994). Ecologically Based Individual Tree Volume Estimation for Major Alberta Tree Species. Report 1 - Individual tree volume estimation procedures for Alberta: Methods of Formulation and Statistical Foundations. Alberta Environmental Protection, Land and Forest Service, Forest Management Division, Edmonton, AB.

Lambert, M. C., Ung, C. H., & Raulier, F. (2005). Canadian national tree aboveground biomass equations. Canadian Journal of Forest Research, 35(8), 1996–2018. <https://doi.org/10.1139/x05-112>

Ung, C.-H., Bernier, P., & Guo, X.-J. (2008). Canadian national biomass equations: new parameter estimates that include British Columbia data. Canadian Journal of Forest Research, 38(5), 1123–1132. <https://doi.org/10.1139/X07-224>

Ung, C.-H., Bernier, P.Y., Guo, X.J., Lambert, M.-C., 2009. A simple growth and yield model for assessing changes in standing volume across Canada's forests. The Forestry Chronicle 85, 57–64. <https://doi.org/10.5558/tfc85057-1>

## License

GPL-3

## Authors

- Piotr Tompalski (Original R package)
- Juha Metsaranta (Original R package)
- Vinicius Manvailer Goncalves (Original R package)

## History

This package was originally developed as an R package. It has been refactored to Python while maintaining the same functionality and accuracy. See `PYTHON_REFACTORING_SUMMARY.md` for details on the Python implementation.

# CTAE - Canadian Tree Allometric Equations (Python)

A Python implementation of tools to calculate tree- or stand-level attributes developed for Canadian forests.

This is a Python port of the [R CTAE package](https://github.com/ptompalski/CTAE).

## Models included

- Canadian national tree aboveground biomass equations (Lambert et al. 2005, Ung et al. 2008)
- Individual tree volume equations for major Alberta tree species (Huang 1994)
- Volume-to-biomass conversions models (Boudewyn et al. 2007)
- Total volume to merchantable volume conversions models (Boudewyn et al. 2007)
- Simple growth and yield model (H, BA, V) (Ung et al. 2009)

## Installation

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

# Calculate tree aboveground biomass using DBH and height
result = ctae.AGB_LambertUngDBHHT(DBH=20, height=17, species="PINU.CON")
print(result)

# Calculate tree volume (Huang model)
result = ctae.V_Huang(DBH=20, height=20, species="PICE.GLA", subregion="CP")
print(result)

# Volume-to-biomass conversion
result = ctae.V2B(volume=350, species="PINU.CON", jurisdiction="BC", ecozone=4)
print(result)

# Growth and yield model
result = ctae.Ung2009(species="ABIE.BAL", age=range(1, 151), GDD=1500, PREC=800)
print(result)
```

## References

- Boudewyn, P.A.; Song, X.; Magnussen, S.; Gillis, M.D. (2007). Model-based, volume-to-biomass conversion for forested and vegetated land in Canada. Natural Resources Canada, Canadian Forest Service, Pacific Forestry Centre, Victoria, BC. Information Report BC-X-411. 112 p.

- Huang, S. (1994). Ecologically Based Individual Tree Volume Estimation for Major Alberta Tree Species. Report 1 - Individual tree volume estimation procedures for Alberta: Methods of Formulation and Statistical Foundations. Alberta Environmental Protection, Land and Forest Service, Forest Management Division, Edmonton, AB.

- Lambert, M. C., Ung, C. H., & Raulier, F. (2005). Canadian national tree aboveground biomass equations. Canadian Journal of Forest Research, 35(8), 1996–2018. https://doi.org/10.1139/x05-112

- Ung, C.-H., Bernier, P., & Guo, X.-J. (2008). Canadian national biomass equations: new parameter estimates that include British Columbia data. Canadian Journal of Forest Research, 38(5), 1123–1132. https://doi.org/10.1139/X07-224

- Ung, C.-H., Bernier, P.Y., Guo, X.J., Lambert, M.-C., 2009. A simple growth and yield model for assessing changes in standing volume across Canada's forests. The Forestry Chronicle 85, 57–64. https://doi.org/10.5558/tfc85057-1

## License

GPL-3

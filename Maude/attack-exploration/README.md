# Automated Attack Discovery

## File Overview
- `src` contains the Python files for random zone generation, "compiling" to Maude, and running the attack exploration
  - `attack_exploration.py` is the main entry point
  - `random_zone.py` generates random zones
  - `groot_ec.py` generates the GRoot query Equivalence classes
  - All other files contain helper functions or data representations.
- `success_configs/` is where the Maude files of successful configurations will be stored
- `failure_configs/` is where the Maude files of failed configurations will be stored (e.g., when Maude simulation takes too long)
- `report_configs/` are the configurations used as illustration in the thesis report.

## Configuring Attack Exploration
- The parameters for attack exploration are split in two files:
  - `attack_exploration.py`: The "benign" part of the config and general model parameters, e.g., whether QNAME minimization should be used.
  - `random_zone.py`: Parameters for random zone generation, e.g., which RR types to allow or the probability for non-existent names as record values.

## Usage
- See examples in the `test()` function in `attack_exploration.py`.

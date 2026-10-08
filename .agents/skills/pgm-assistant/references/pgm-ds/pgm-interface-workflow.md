<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS to PGM Interface Workflow

## Role of `PowerGridModelInterface`
`PowerGridModelInterface` connects `Grid` objects to the PGM core calculation engine.
It handles:
- Conversion from grid arrays to PGM input data
- Calculation execution
- Mapping output values back into grid arrays

## Standard Workflow
```python
from power_grid_model_ds import PowerGridModelInterface

core = PowerGridModelInterface(grid=grid)
core.create_input_from_grid()
core.calculate_power_flow()
core.update_grid()
```

After `update_grid()`, output fields present in your grid arrays are filled.

## Constructor Modes
- `PowerGridModelInterface(grid=grid)`
- `PowerGridModelInterface(input_data=input_data)`

Use `create_grid_from_input_data()` when starting from raw PGM dataset.

## Interface Methods You Will Use Most
- `create_input_from_grid()`
- `setup_model()`
- `calculate_power_flow(calculation_method=..., update_data=..., **kwargs)`
- `update_model(update_data)`
- `update_grid()`
- `create_grid_from_input_data(check_ids=True)`

## Calculation with Explicit Method
```python
from power_grid_model import CalculationMethod

out = core.calculate_power_flow(
    calculation_method=CalculationMethod.newton_raphson,
)
```

## Batch Update Pattern
`update_model(update_data=...)` can be used to update model state before additional runs.
For batch calculations, pass update datasets to `calculate_power_flow(update_data=...)` and propagate selected outputs back with `update_grid()`.

## Practical Pattern for Extended Grids
1. Extend arrays with output fields you care about.
2. Build/modify grid.
3. `create_input_from_grid()`.
4. Run calculation.
5. `update_grid()` to fill custom output columns.

## When to Prefer PGM-DS Interface
Prefer `PowerGridModelInterface` over direct PGM calls when:
- Grid topology is being actively edited between runs
- You need graph-aware processing around each run
- You want output values immediately available on typed grid arrays

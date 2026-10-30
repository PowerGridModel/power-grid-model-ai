<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS to PGM Interface Workflow

`PowerGridModelInterface(grid=None, input_data=None, system_frequency=50.0)` converts a `Grid` to PGM input data, runs power flow and copies results back. Only columns whose names exist in both the `Grid` array and the PGM dataset are transferred; empty arrays are skipped.

## Standard Workflow
```python
from power_grid_model_ds import PowerGridModelInterface

core = PowerGridModelInterface(grid=grid)
core.create_input_from_grid()      # returns the PGM input dataset (a dict of structured arrays)
out = core.calculate_power_flow()  # also stored in core.output_data
core.update_grid()
```
`calculate_power_flow()` and `update_model()` build the model on first use (`setup_model()`), so `create_input_from_grid()` is optional when you do not need the dataset itself.

## Methods
- `calculate_power_flow(calculation_method=CalculationMethod.newton_raphson, update_data=None, **kwargs)`: `**kwargs` go to `PowerGridModel.calculate_power_flow` (`symmetric`, `error_tolerance`, `max_iterations`, ...). Power flow only; for state estimation or short circuit, pass `create_input_from_grid()` to `PowerGridModel` directly.
- `update_model(update_data)`: applies an update dataset to the cached model; the change persists for later calculations.
- `update_grid()`: copies output columns into the matching `Grid` arrays; raises `PGMCoreException` when there is no output. It needs a single-scenario output; batch output raises `ValueError` (shape mismatch).
- `create_grid_from_input_data(check_ids=True)`: appends the `input_data` passed to the constructor to `interface.grid` (an empty `Grid` unless `grid=` is given) and returns that grid. Missing columns take array defaults; components the `Grid` has no array for are ignored. Columnar input (`{"node": {"id": [...], "u_rated": [...]}}`) is accepted.
- `core.input_data` is deprecated (emits `DeprecationWarning`).

## Caching Pitfall
The input dataset and model are built once and reused. After editing the grid arrays, rebuild both before calculating again:
```python
core.create_input_from_grid()
core.setup_model()
```
or create a new `PowerGridModelInterface`. Otherwise `calculate_power_flow()` silently returns results for the old data.

## Batch Calculations
```python
out = core.calculate_power_flow(update_data=batch_update_data)  # does not change the cached model
```
Read batch results from `out`; `update_grid()` only handles single-scenario output.

## Output Columns
Default `Grid` arrays have no output columns. To receive results, use an extended grid (see overview-and-core-objects.md), then call `update_grid()` after the calculation.

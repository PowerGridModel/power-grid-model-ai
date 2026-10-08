<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Overview and Core Objects

## Purpose of PGM-DS
`power-grid-model-ds` provides an application-facing grid model on top of PGM.
Use it when you need:
- Safer grid mutations
- Graph-aware analysis
- Easier array handling with typed abstractions
- Tight integration with PGM calculations

## Core Types
- `Grid`: full network object with arrays and graph container
- `FancyArray`: typed structured-array wrapper
- `GraphContainer`: maintains active and complete graph views
- `PowerGridModelInterface`: bridge between `Grid` and `PowerGridModel`

## Building a Grid
```python
from power_grid_model_ds import Grid

grid = Grid.empty()
```

Other constructors:
- `Grid.from_txt(...)` and `Grid.from_txt_file(...)`
- `Grid.deserialize(path)` and `Grid.from_json_string(...)`
- `RadialGridGenerator(...).run(seed=...)`

## FancyArray Essentials
Common capabilities:
- `zeros(num)` and `empty(num)`
- `filter(...)`, `exclude(...)`, `get(...)`
- `update_by_id(...)`
- `as_df()`
- `check_ids()`

Design notes:
- Define custom arrays by subclassing `FancyArray`.
- Use `_defaults` for fill values.
- Prefer enums over string fields when possible for memory efficiency.

## Grid Container Behaviors
`Grid` tracks:
- Typed component arrays (`node`, `line`, `transformer`, sensors, etc.)
- `graphs` with active and complete topology views
- ID integrity across arrays

Available component arrays on `Grid` include: `node`, `line`, `link`, `transformer`, `three_winding_transformer`, `generic_branch`, `asym_line`, `source`, `sym_load`, `sym_gen`, `asym_load`, `asym_gen`, `shunt`, `voltage_regulator`, `transformer_tap_regulator`, the `sym_`/`asym_` `power`/`voltage`/`current` sensors, and `fault`. (`asym_load`, `asym_gen`, `shunt`, `voltage_regulator`, `fault`, and the asym power sensor array were added in PGM-DS v1.8.0; `shunt` uses `g1`/`b1` and has no `u_ref`.)

Useful properties/methods:
- `branch_arrays`, `branches`
- `append(array)`
- `rebuild_ids()`, `check_ids()`
- `rebuild_graphs()`
- `diff(other_grid)` for debugging

## Extending Grid with Custom Output Columns
PGM-DS supports extending arrays so output fields can be pushed back from calculation results.

Pattern:
1. Extend `NodeArray` / `LineArray` with extra columns.
2. Extend `Grid` dataclass using those array types.
3. Use `PowerGridModelInterface.update_grid()` after calculations.

## Safety Notes
- The pickle-based cache (`Grid.from_cache` / `grid.cache`) was removed in PGM-DS v1.10.0.
- Use JSON `serialize` / `deserialize` for portable, safe interchange.

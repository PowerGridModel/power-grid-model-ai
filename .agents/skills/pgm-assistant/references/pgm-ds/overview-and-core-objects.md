<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Overview and Core Objects

`power-grid-model-ds` wraps PGM with typed arrays (`FancyArray`), a `Grid` container that keeps arrays, ids and graphs consistent, and `PowerGridModelInterface` to run PGM calculations on a `Grid`.

Public imports: `from power_grid_model_ds import Grid, FancyArray, GraphContainer, PowerGridModelInterface`; plus `power_grid_model_ds.arrays` (`NodeArray`, `LineArray`, ...), `.enums` (`NodeType`), `.generators` (`RadialGridGenerator`), `.errors` (`MissingNodeError`, `NoPathBetweenNodes`, `RecordDoesNotExist`, `MultipleRecordsReturned`, `PGMCoreException`).

## Building a Grid
```python
grid = Grid.empty()
grid = Grid.from_txt("S1 2 11", "2 3 12,open", "3 4 13,transformer")  # also Grid.from_txt_file(path)
grid = Grid.deserialize(path)  # JSON, see mutations-serialization-visualizer.md
grid = RadialGridGenerator(grid_class=Grid, nr_nodes=20, nr_sources=1, nr_nops=2).run(seed=1)
```
- `from_txt` line format: `<from> <to> [comma-separated tags]`. A node written `S<id>` becomes a substation node (`node_type == NodeType.SUBSTATION_NODE`); other tags: an integer branch id, `open` (sets `to_status=0`), `transformer`, `link`, `generic_branch`, `asym_line`. Without a type tag the branch is a line. An id must not appear both as `S1` and `1`. `from_txt` also calls `set_feeder_ids()`; `str(grid)` writes the same format.
- `RadialGridGenerator` output has substation nodes and sources; a grid built from raw PGM input has `node_type == 0` everywhere (see substation-dependent functions in graph-and-topology-recipes.md).

## FancyArray
- Selection: `filter(*ids, mode_="AND"|"OR", **column_values)` and `exclude(...)` return copies; `get(...)` returns exactly one record and raises `RecordDoesNotExist` / `MultipleRecordsReturned` otherwise. `*_mask` variants return boolean masks. Pass these copies, not slices such as `grid.line[:3]`, to grid methods (see `reverse_branches` in graph-and-topology-recipes.md).
- `update_by_id(ids, allow_missing=False, **column_values)` updates in place; `as_df()` needs pandas.
- `zeros(n)` builds zero-filled rows; `empty(n)` fills every column with its empty marker (`NaN` floats, `-2147483648` ints) and applies `_defaults`. Both leave `id` empty; `grid.append` then assigns new ids.
- Custom arrays subclass an existing array and declare columns as `NDArray[...]` annotations. Class attributes: `_defaults` (fill values), `_id_columns` (columns that `grid.merge` must offset), `_str_lengths`. Prefer `IntEnum` columns over strings.

## Grid
Component arrays: `node`, `line`, `link`, `transformer`, `three_winding_transformer`, `generic_branch`, `asym_line`, `source`, `sym_load`, `sym_gen`, `asym_load`, `asym_gen`, `shunt` (`g1`/`b1`, no `u_ref`), `voltage_regulator`, `transformer_tap_regulator`, `{sym,asym}_{power,voltage,current}_sensor`, `fault`. Plus `graphs` (a `GraphContainer`).

- Arrays hold input attributes only, plus `feeder_branch_id`/`feeder_node_id` (nodes and branches) and `is_feeder` (branches). Calculation output columns do not exist until you add them (below).
- `grid.branches` concatenates all branch arrays into one `BranchArray`; `grid.branch_arrays` lists them. `grid.rebuild_ids()` / `grid.check_ids()` / `grid.rebuild_graphs()` resync the id tracker and graphs after direct array edits. `grid.diff(other)` prints differences.
- Ids are unique across all arrays of a grid.

## Extending a Grid with Output Columns
```python
import numpy as np
from dataclasses import dataclass
from numpy.typing import NDArray
from power_grid_model_ds import Grid
from power_grid_model_ds.arrays import NodeArray, LineArray

class ExtNodeArray(NodeArray):
    _defaults = {"u_pu": np.nan, "u": np.nan}
    u_pu: NDArray[np.float64]
    u: NDArray[np.float64]

class ExtLineArray(LineArray):
    _defaults = {"loading": np.nan}
    loading: NDArray[np.float64]

@dataclass
class ExtGrid(Grid):
    node: ExtNodeArray
    line: ExtLineArray
```
- Every added column needs a `_defaults` entry; without it, building the grid from PGM input data raises `Missing required columns`.
- `PowerGridModelInterface.update_grid()` copies output columns whose names match (see pgm-interface-workflow.md). `Grid.from_extended(ext_grid)` converts back to a plain `Grid`.

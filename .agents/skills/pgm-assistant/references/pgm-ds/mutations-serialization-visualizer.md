<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Mutations, Serialization, and Visualizer

## Topology Mutation APIs
Use these instead of manual array edits so arrays, id tracker and graphs stay consistent.

- `grid.append(array, check_max_id=True)`: adds rows of any component array and updates the graphs. Create rows with `grid.node.empty(n)` / `grid.line.empty(n)` and set columns; rows whose ids are all empty get new ids from `grid.max_id + 1`. Explicit ids that already exist raise `ValueError`; `check_max_id=False` skips that check (follow with `grid.check_ids()`). Append nodes before the branches that use them.
- `grid.delete_node(nodes)`: also removes the node's branches, appliances, sensors, regulators and faults.
- `grid.delete_branch(branches)` / `grid.delete_branch3(branch3s)`: also remove sensors and tap regulators attached to them.
- `grid.make_active(branch)`: sets both statuses to 1. `grid.make_inactive(branch, at_to_side=True)`: sets `to_status` (or `from_status` when `at_to_side=False`) to 0.

Argument rules:
- Pass typed arrays (`grid.line.filter(id=[...])`, `grid.transformer.get(id=3)`), not `grid.branches`, which raises `TypeError`. `grid.get_typed_branches(ids)` returns the typed array for branch ids of one type.
- The `delete_*` methods accept multi-row arrays; `make_active` / `make_inactive` need exactly one row.

`Grid.add_node`, `Grid.add_branch` and the pickle cache (`Grid.from_cache`, `grid.cache`) no longer exist; use `append` and JSON serialization.

## Merge Grids
```python
offset = grid.merge(other_grid, mode="recalculate_ids")
```
- `recalculate_ids`: adds `grid.max_id` (returned as `offset`) to every id and id-reference column of `other_grid`, including columns declared in a custom array's `_id_columns`.
- `keep_ids`: returns `None`; raises `ValueError` on id collisions.
- Both grids must be the same class, otherwise `TypeError`.

## Grid Serialization
```python
from pathlib import Path

grid.serialize(Path("grid.json"), mode="json", indent=2)  # returns the Path; extra kwargs go to json.dump
loaded = Grid.deserialize(Path("grid.json"))

json_text = grid.serialize(mode="json_string")
loaded = Grid.from_json_string(json_text)
```
- `serialize` and `deserialize` require a `Path`; a `str` raises `TypeError` / `AttributeError`.
- Format: `{"version": "1.0", "type": "grid", "data": {"node": [records...], ...}}`; `NaN` is written as `null`. Files without `version`/`type` still load.
- `deserialize` takes its target class from the caller: missing columns get defaults, extra columns are dropped with a warning. `ExtGrid.deserialize(path)` therefore loads a plain grid file into an extended grid and the reverse.
- `Grid.deserialize` also reads a PGM JSON input file (`"type": "input"`, as written by `power_grid_model.utils.json_serialize_to_file`).

## Visualizer
Requires `pip install 'power-grid-model-ds[visualizer]'`; importing `power_grid_model_ds.visualizer` without it raises `ImportError`.

```python
from power_grid_model_ds.visualizer import save_html, visualize

visualize(grid, update_data=None, output_data=None, debug=False, port=8050)
save_html(grid, "grid.html", layout="", include_appliances=False)
```
- `visualize` starts a blocking Dash server on `localhost:port`. `update_data` / `output_data` are PGM batch datasets whose columns and scenarios become inspectable in the dashboard.
- `save_html` writes a self-contained Cytoscape.js file without a server. Appliances (loads, generators, sources) are left out unless `include_appliances=True`; it has no `update_data` / `output_data`.
- Layout: with `x` and `y` columns on `grid.node` the preset layout uses them; otherwise breadthfirst rooted at the sources. `save_html(layout=...)` accepts `"random"`, `"circle"`, `"concentric"`, `"grid"`, `"cose"`, `"breadthfirst"`, `"preset"`.

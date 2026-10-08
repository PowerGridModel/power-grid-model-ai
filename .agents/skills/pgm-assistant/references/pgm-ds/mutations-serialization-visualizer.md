<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Mutations, Serialization, and Visualizer

## Topology Mutation APIs
Use these instead of manual array edits to keep graph consistency.

- `grid.append(array)` — add nodes/branches/other components
- `grid.delete_node(node)`
- `grid.delete_branch(branch)`
- `grid.delete_branch3(branch3)`
- `grid.make_active(branch)`
- `grid.make_inactive(branch, at_to_side=True)`

> Since PGM-DS v1.9.1, `grid.delete_node(...)` and `grid.delete_branch(...)` accept multi-row arrays, so multiple nodes/branches can be deleted in a single call.

> `Grid.add_node` and `Grid.add_branch` were removed in PGM-DS v1.10.0. Use `grid.append(array)` instead.

## Merge Grids
```python
offset = grid.merge(other_grid, mode="recalculate_ids")
```

Modes:
- `keep_ids`: fail on collisions
- `recalculate_ids`: offset IDs in incoming grid to avoid collisions

Since PGM-DS v1.10.0, `grid.merge` also works on extended grids: custom arrays declaring `_id_columns` have those columns offset during the merge, not just the standard PGM id columns.

## Grid Serialization
### Preferred portable format (JSON)
```python
grid.serialize(path_json, mode="json", indent=2)
loaded = Grid.deserialize(path_json)
```

### In-memory JSON string
```python
json_text = grid.serialize(mode="json_string")
loaded = Grid.from_json_string(json_text)
```

> The pickle-based cache (`grid.cache(...)` / `Grid.from_cache(...)`) was removed in PGM-DS v1.10.0. Use JSON `serialize` / `deserialize` for persistence.

## Visualizer Quickstart
```python
from power_grid_model_ds.visualizer import visualize

visualize(grid)
```

This starts a local dashboard (default localhost).

### Export to standalone HTML
```python
from power_grid_model_ds.visualizer import save_html

save_html(grid, "grid.html")
```

`save_html(grid, path)` writes a self-contained HTML file (Cytoscape.js) without starting the Dash server. Added in PGM-DS v1.10.0.

Optional dependency install:
```bash
pip install 'power-grid-model-ds[visualizer]'
```

## Visualizer Use Cases
- Quick structural inspection before/after topology mutations
- Highlight problematic nodes/branches during debugging
- Compare feeder structures under switching scenarios

## Recommended Mutation Loop
1. Apply topology changes via grid methods.
2. Recompute feeder IDs / branch orientation if needed.
3. Run calculation through interface.
4. Update grid output fields.
5. Visualize and inspect.

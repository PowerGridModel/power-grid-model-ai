<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Graph and Topology Recipes

## Graph Representations
`Grid.graphs` contains:
- `active_graph`: only active branches
- `complete_graph`: all branches

Use active graph for operational analysis and complete graph for structural analysis.

## Fast Graph Recipes

### Shortest path
```python
path, length = grid.graphs.active_graph.get_shortest_path(1, 4)
```

### All paths between two nodes
```python
all_paths = grid.graphs.active_graph.get_all_paths(56, 41)
```

### Connected components
```python
components = grid.graphs.active_graph.get_components()
```

### Temporarily remove nodes for what-if analysis
```python
with grid.graphs.active_graph.tmp_remove_nodes([1, 2, 3]):
    components = grid.graphs.active_graph.get_components()
```

### Temporarily remove branches for what-if analysis
```python
with grid.graphs.active_graph.tmp_remove_branches([branch_id_1, branch_id_2]):
    components = grid.graphs.active_graph.get_components()
```
If an exception occurs inside the block the graph is automatically restored to its original state. Added in PGM-DS v1.10.1.

### Adjacent nodes
```python
neighbors = grid.graphs.active_graph.adjacent(node_id=56)
# Exclude specific node IDs from the result
neighbors = grid.graphs.active_graph.adjacent(node_id=56, excluding=[1, 2])
```
Returns node IDs directly connected to the given node. Added in PGM-DS v1.10.1.

### Neighborhood traversal
```python
connected = grid.graphs.active_graph.get_connected(node_id=56)
```

## Feeder and Substation Utilities

### Assign feeder IDs
```python
grid.set_feeder_ids()
```

### Nearest substation node
```python
substation = grid.get_nearest_substation_node(node_id=102)
```

### Downstream nodes (radial assumptions)
```python
downstream = grid.get_downstream_nodes(node_id=102, inclusive=False)
```

## Branch Orientation Utilities
Use these when directional conventions matter (for plotting, protection studies, and deterministic traversal).

- `get_reversed_branches()`
- `set_branch_orientations()`
- `reverse_branches(...)`

Practical rule:
- Normalize branch orientation before repeated topology analyses to reduce ambiguity.

## Branch Path Extraction
```python
branches = grid.get_branches_in_path(nodes_in_path=[1, 16, 5, 4])
```

## Handling Parallel Edges and Cycles
Graph model methods support:
- Parallel edges
- Cycles
- Component queries under temporary topology changes

Useful checks:
- `has_parallel_edges()`
- `find_fundamental_cycles()`

## Mutation + Graph Consistency
Prefer grid methods instead of editing arrays manually:
- `append` for adding components (replaces the removed `add_node`/`add_branch`)
- `delete_branch`, `delete_node`
- `make_active`, `make_inactive`

These keep arrays and graph views consistent together.

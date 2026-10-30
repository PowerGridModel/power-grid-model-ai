<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-DS Graph and Topology Recipes

## Graph Representations
`grid.graphs` is a `GraphContainer` with two undirected `RustworkxGraphModel`s keyed by PGM node ids:
- `active_graph`: branches with `from_status == 1 and to_status == 1`
- `complete_graph`: all branches

Change topology through grid methods (see mutations-serialization-visualizer.md); editing a graph directly leaves the arrays out of sync.

## Graph Recipes
```python
graph = grid.graphs.active_graph
path, length = graph.get_shortest_path(1, 4)   # (node ids, edge count); raises NoPathBetweenNodes
paths = graph.get_all_paths(56, 41)            # list of node-id lists; [] when both ids are equal
components = graph.get_components()            # list of node-id lists
neighbors = graph.adjacent(56, excluding=[1, 2])
connected = graph.get_connected(56, nodes_to_ignore=[7], inclusive=False)  # sorted by distance
parents = graph.bfs(56)                        # also dfs([56, 57]); source: int or sequence
graph.has_parallel_edges(); graph.find_fundamental_cycles(); graph.nr_nodes; graph.nr_branches
```
- `get_connected` drops nodes that are reachable only through `nodes_to_ignore`.
- `bfs`/`dfs` return `dict[node_id, parent_id | None]` in discovery order; the parent is `None` for sources. An unknown node raises `MissingNodeError`.

### What-if analysis
```python
with graph.tmp_remove_nodes([1, 2, 3]):
    components = graph.get_components()

# (from_node, to_node) pairs, not branch ids
with graph.tmp_remove_branches([(from_node_1, to_node_1), (from_node_2, to_node_2)]):
    components = graph.get_components()
```
The graph is restored on exit, also when the block raises.

## Substation, Feeder and Downstream Functions
These depend on substation nodes (`node_type == NodeType.SUBSTATION_NODE`, from `power_grid_model_ds.enums`). Nodes converted from PGM input data all have `node_type == 0`, so mark them first:
```python
grid.node.update_by_id(substation_ids, node_type=NodeType.SUBSTATION_NODE)
grid.set_feeder_ids()
substation = grid.get_nearest_substation_node(node_id=102)    # NodeArray; RecordDoesNotExist if none connected
downstream = grid.get_downstream_nodes(node_id=102, inclusive=False)  # list of node ids
```
- `set_feeder_ids()` splits the active graph at the substation nodes. Each remaining component gets `feeder_branch_id` (the branch attached to the substation; the first one if several) and `feeder_node_id` (the substation) on its nodes and branches; `is_feeder` is set on lines, links and transformers touching a substation. Everything else, including the substation nodes themselves, keeps `-2147483648`.
- `get_downstream_nodes` assumes a radial grid and raises `NotImplementedError` for a substation node. The graph-level variant is `graph.get_downstream_nodes(node_id, start_node_ids, inclusive=False)`.

## Branch Orientation
- `grid.get_reversed_branches()` returns branches pointing towards the sources, plus open branches with `from_status == 0, to_status == 1`. Orientation follows `grid.source` nodes (not substation nodes) over the active graph.
- `grid.set_branch_orientations()` reverses exactly those branches and returns them.
- `grid.reverse_branches(branches)` swaps `from_node`/`to_node` and `from_status`/`to_status` and returns `None`. Pass a copy such as `grid.line.filter(id=[...])`; a slice like `grid.line[:3]` aliases the grid's data and ends up with `from_node == to_node`.

## Branch Path Extraction
```python
branches = grid.get_branches_in_path(nodes_in_path=[1, 16, 5, 4])
```
Returns every active branch whose `from_node` and `to_node` are both in the list, so list the nodes of the path only.

<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Data Model, Components, and Dataset Types

Primary sources (full attribute tables with units, required/optional, update mutability and valid values):

- [Component Type Hierarchy and Graph Data Model](https://power-grid-model.readthedocs.io/en/stable/user_manual/data-model.html)
- [Dataset Terminology](https://power-grid-model.readthedocs.io/en/stable/user_manual/dataset-terminology.html)
- [Components](https://power-grid-model.readthedocs.io/en/stable/user_manual/components.html)

Get the exact attribute names and dtypes from `attribute_dtype(...)` / `power_grid_meta_data[dataset_type][component_type].dtype` instead of handcrafting dtypes; never alter the structured dtype or add fields.

## Component Types

Concrete `ComponentType` names (metadata names match exactly):

- `node`
- branches (two nodes: `from_node`, `to_node`, `from_status`, `to_status`): `line`, `asym_line`, `link`, `transformer`, `generic_branch`
- branch3 (`node_1..3`, `status_1..3`): `three_winding_transformer`
- appliances (`node`, `status`): `source`, `shunt`, `sym_load`, `asym_load`, `sym_gen`, `asym_gen`
- sensors (`measured_object`): `sym_voltage_sensor`, `asym_voltage_sensor`, `sym_power_sensor`, `asym_power_sensor`, `sym_current_sensor`, `asym_current_sensor`
- `fault` (`fault_object` is a node)
- regulators (`regulated_object`, `status`): `transformer_tap_regulator`, `voltage_regulator`

`base`, `branch`, `branch3`, `appliance`, `generic_load_gen`, `generic_*_sensor`, `sensor` and `regulator` are documentation-only parent types and not valid `ComponentType` values.

## Symmetry and Reference Direction

- Symmetry of component type (`sym_*` / `asym_*`) is independent of symmetry of the calculation: symmetric calculations accept asymmetric components and vice versa. A `RealValueInput` is a scalar for `sym_*` components and a length-3 array for `asym_*` components; a `RealValueOutput` is scalar for symmetric calculation and length-3 for asymmetric and short-circuit calculation.
- Load direction (`sym_load`, `asym_load`, shunt, load-type sensors): positive power flows from node to appliance. Generator direction (`sym_gen`, `asym_gen`, `source`): positive power flows from appliance to node. Branches: positive `p_from`/`p_to` flows from the node into the branch. Node `p`/`q` output is injection in generator direction.

## Dataset Types and Structures

- `DatasetType`: `input`, `update`, `sym_output`, `asym_output`, `sc_output`. The `update` dtype of a component contains only its updatable attributes (e.g. `line`, `link`, `generic_branch`: statuses only; `transformer`: statuses and `tap_pos`; `node`: `id` only).
- A dataset is a `dict[ComponentType, ComponentData]`. Component data is row-based (structured array) or columnar (`dict[attribute, ndarray]`).
- Single dataset: 1D arrays (columnar attributes: 1D, or 2D `(n, 3)` for asymmetric attributes).
- Dense batch: 2D arrays `(n_scenarios, n_elements)` (columnar: 2D/3D).
- Sparse batch: `{"indptr": int64 array of length n_scenarios + 1, "data": flat array}`; scenario `k` is `data[indptr[k]:indptr[k+1]]`.
- Batch update `id`s may be omitted (or NaN) only for uniform updates (same elements in every scenario, e.g. every dense update); otherwise `id` is required and cannot change an element's identity.
- Component `id`s are unique across all component types within one scenario (`ConflictID` on construction otherwise).

## Component Notes

### Node and Branches

- Node output: `u_pu`, `u` (line-line for symmetric, line-neutral for asymmetric calculation), `u_angle` (rad), `p`, `q`. Short-circuit node output has only `u_pu`, `u`, `u_angle`.
- Branch output: `p/q/i/s_from`, `p/q/i/s_to`, `loading`. `loading` is `nan` when the rated current/power (`i_n`, `sn`) is missing.
- A branch's `from_node` and `to_node` (branch3: any two of the three nodes) may be identical; the validator accepts this (PGM v1.13.118).
- `line`: positive-sequence `r1, x1, c1, tan1` and zero-sequence `r0, x0, c0, tan0`. Zero-sequence values are required for asymmetric calculation and for non-three-phase faults; with NaN values the calculation raises `SparseMatrixError`.
- `link`: very high admittance connector. Nodes joined by links are merged internally unless node injection sensors are present, in which case a finite admittance is used. Power and current sensors cannot be attached to a link (`InvalidMeasuredObject`).
- `transformer`: tap range may be descending (`tap_min > tap_max`). Asymmetric studies may need explicit `i0_zero_sequence`.
- `generic_branch`: PI model from `r1, x1, g1, b1`; `k` is the off-nominal ratio (not the nominal voltage ratio). Asymmetric calculation is not implemented (`PowerGridError: Function not yet implemented`).
- `asym_line`: per-phase `r_*`/`x_*` matrices (optionally with neutral `*_n*`) and either the full `c_*` matrix or `c0`/`c1`; the manual defines the valid field combinations.

### Appliances

- `source`: Thevenin equivalent with `u_ref` (p.u.), `sk` (VA), `rx_ratio`, `z01_ratio`. NaN `sk` / `rx_ratio` default to `1e10` VA / `0.1`. `sk = inf` represents an ideal source (v1.13.208); it is accepted for power flow and state estimation, while short-circuit validation requires a finite `sk`.
- `sym_load`/`asym_load`/`sym_gen`/`asym_gen`: `type` is `LoadGenType` (`const_power`, `const_impedance`, `const_current`) with `p_specified`, `q_specified`.
- `shunt`: `g1, b1` and zero-sequence `g0, b0` (needed for asymmetric and non-three-phase fault studies).

### Sensors

- Sensor results exist only for state estimation (`*_residual` attributes); other calculations return no sensor output.
- Voltage sensor: magnitude and optional angle. Global-angle current sensors need at least one voltage angle measurement as reference.
- Power sensor: sigma attributes (`power_sigma`, or both `p_sigma` and `q_sigma`) have strict valid combinations; partial specification is invalid.
- Current sensor: `angle_measurement_type` is `local_angle` or `global_angle`; some magnitude/angle combinations (e.g. zero magnitude with certain angles) are invalid.
- Do not mix power and current sensors, or global-angle and local-angle current sensors, on the same terminal.

### Fault

- Located at a node; multiple faults per scenario are allowed within type/phase consistency constraints. If any scenario has a non-three-phase fault, short-circuit treatment is asymmetric. Output: `i_f`, `i_f_angle` (per phase).

### Regulators

- `transformer_tap_regulator`: regulates `transformer` or `three_winding_transformer` tap position at `control_side` toward `u_set` within the band `u_band` (both in volt), with optional line-drop compensation; the output `tap_pos` is the optimal tap and does not change the grid state (see `calculation-recipes.md` Recipe 5).
- `voltage_regulator`: controls reactive power of a generator/load (`regulated_object`) to hold `u_ref` at its node; supported for Newton-Raphson power flow only (other methods raise `InvalidCalculationMethod`). The regulated node acts as a PV node; if the required reactive power violates `q_min`/`q_max`, the object is clamped at the limit and the node switches from PV to PQ.
- Voltage regulator output: `limit_violated` (`-1` `q_min` reached, `0` none, `1` `q_max` reached); the Q value is on the regulated load/generator output. The node output reports the effective `bus_type` (`0` PQ, `1` PV, `2` source/slack).

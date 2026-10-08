<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Data Model, Components, and Dataset Types

This reference summarizes the most important information from the PGM user manual for understanding what the data actually means in practice.

Primary sources:

- [Component Type Hierarchy and Graph Data Model](https://power-grid-model.readthedocs.io/en/stable/user_manual/data-model.html)
- [Dataset Terminology](https://power-grid-model.readthedocs.io/en/stable/user_manual/dataset-terminology.html)
- [Components](https://power-grid-model.readthedocs.io/en/stable/user_manual/components.html)

## Graph Model and Component Hierarchy

PGM uses a graph-like data model:

- `node`: graph vertex.
- `branch`: graph edge between two nodes.
- `branch3`: three-terminal connector between three nodes.
- `appliance`: device coupled to a node.

Component families and concrete types documented in the manual:

- `base`
- `node`
- `branch` family:
  - `line`
  - `link`
  - `transformer`
  - `generic_branch`
  - `asym_line`
- `branch3` family:
  - `three_winding_transformer`
- `appliance` family:
  - `source`
  - `generic_load_gen` with concrete types:
    - `sym_load`
    - `sym_gen`
    - `asym_load`
    - `asym_gen`
  - `shunt`
- `sensor` family:
  - `generic_voltage_sensor` with concrete types:
    - `sym_voltage_sensor`
    - `asym_voltage_sensor`
  - `generic_power_sensor` with concrete types:
    - `sym_power_sensor`
    - `asym_power_sensor`
  - `generic_current_sensor` with concrete types:
    - `sym_current_sensor`
    - `asym_current_sensor`
- `fault`
- `regulator` family:
  - `transformer_tap_regulator`
  - `voltage_regulator`

Type names match metadata names in PGM exactly.

## Symmetry and Reference Direction

Symmetry of component data and symmetry of calculation are independent:

- Symmetric calculation can run with asymmetric component types.
- Asymmetric calculation can run with symmetric component types.

Reference direction drives sign interpretation of power values:

- Load direction: positive power means node to appliance/sensor.
- Generator direction: positive power means appliance/sensor to node.
- Branches: positive branch-side power means node to branch.

## Dataset Types and Terminology

### DatasetType categories

PGM dataset types include:

- `input`: grid configuration attributes.
- `update`: mutable scenario attributes.
- `sym_output`: symmetric steady-state output.
- `asym_output`: asymmetric steady-state output.
- `sc_output`: short-circuit output.

### Core structure terms

- Dataset: dictionary keyed by component type.
- SingleDataset: one-scenario dataset.
- BatchDataset: multi-scenario update/output dataset.
- ComponentData: data for one component type.
- DataArray: row-based structured numpy arrays.
- ColumnarData: attribute-keyed arrays.

### Dense and sparse batch formats

- Dense batch arrays: one component array per scenario with fixed shape.
- Sparse batch arrays: dictionary with:
  - `indptr` (index pointer)
  - `data` (flattened component records)

`indptr` slices scenario records in `data`.

### Dimensions

- SingleArray: 1D structured array for one scenario.
- DenseBatchArray: 2D structured array (`n_scenarios`, elements).
- SingleColumn: 1D or 2D values for one attribute (2D when asymmetric attribute values are phase-wise).
- BatchColumn: 2D or 3D values across scenarios (3D when asymmetric).

Asymmetric attributes add an optional phase dimension.

### Scenario and batch language

- Scenario: one operating state/time step/topology state.
- Batch: set of scenarios processed together.
- Batch size: number of scenarios (`n_scenarios`).

## Attribute Semantics

The component tables in the manual define each attribute by:

- name
- data type
- unit
- description
- required/optional
- update mutability
- valid-value constraints

Important data type semantics:

- `RealValueInput`:
  - symmetric component: scalar
  - asymmetric component: length-3 phase values
- `RealValueOutput`:
  - symmetric calculation: scalar
  - asymmetric/short-circuit calculation: phase-wise values

Optional attributes should use the defined null/default behavior when omitted.

## Base Rules You Should Not Violate

- Component `id` values must be unique across all components in one scenario.
- Update dataset IDs cannot change existing component identity.
- IDs in updates can be omitted only for uniform updates where mapping is implicit.
- Input arrays must exactly match required PGM dtype/meta definitions.
- Altering structured dtypes or injecting custom fields directly can cause undefined behavior.

## Component Families: Practical Meaning and Key Fields

### Base

- Common input key: `id`.
- Common outputs include `id` and `energized`.

### Node

- Key input: `u_rated`.
- Key outputs: `u_pu`, `u_angle`, `u`, `p`, `q`.
- Injection sign follows generator-direction convention in output.

### Branch family

Common branch inputs:

- `from_node`, `to_node`
- `from_status`, `to_status`
- `from_node` and `to_node` (branch3: all three nodes) may be identical; connecting a branch into itself is valid and no longer rejected by the validator (PGM v1.13.118).

Common branch outputs:

- power, current, apparent power on each side
- `loading`

Line highlights:

- Positive and zero-sequence electrical parameters.
- Zero-sequence data is required for asymmetric studies and for non-three-phase short-circuit cases.
- If rated current `i_n` is missing, loading may be `nan`.

Link highlights:

- High-admittance internal connector model.
- Sensors are intentionally not coupled to `link`.

Transformer highlights:

- Includes ratings, short-circuit and no-load parameters, winding types, clock, and tap attributes.
- Tap range can be ascending or descending (`tap_min` may be greater than `tap_max`).
- Zero-sequence magnetization behavior may require explicit tuning (`i0_zero_sequence`) in asymmetric studies.

Generic branch highlights:

- PI-model parameterized directly by equivalent-circuit values.
- `k` is off-nominal ratio (not nominal voltage ratio).
- Not supported for asymmetric calculation.

Asym line highlights:

- Per-phase resistance/reactance matrix representation (optionally including neutral).
- Supports full capacitance matrix or (`c0`, `c1`) representation.
- Manual defines strict valid field combinations for matrix inputs.

### Branch3 family

Common branch3 inputs:

- `node_1`, `node_2`, `node_3`
- `status_1`, `status_2`, `status_3`

Three-winding transformer highlights:

- Three-terminal transformer with side-specific ratings and pairwise short-circuit parameters.
- Tap changer support and side selection.
- Grounding impedance attributes by side.

### Appliance family

Common appliance inputs:

- `node`, `status`

Source highlights:

- Thevenin equivalent external network.
- Key control inputs include `u_ref`, short-circuit strength and impedance ratios.

Generic load/gen highlights:

- ZIP behavior controlled by load/gen type.
- Concrete types split by symmetry and reference direction (`sym_load`, `sym_gen`, `asym_load`, `asym_gen`).

Shunt highlights:

- Fixed admittance model.
- Zero-sequence attributes matter in asymmetric and non-three-phase fault studies.

### Sensor family

General sensor rule:

- Sensor outputs are defined for state estimation, not for other calculation types.

Voltage sensor highlights:

- Measures magnitude and optional angle.
- Global-angle current measurements require at least one voltage angle reference measurement.

Power sensor highlights:

- Measures appliance-terminal or branch-terminal power.
- Cannot be coupled to `link`.
- Sigma fields have strict valid combinations; partial sigma specification can be invalid/undefined.
- Do not mix power and current sensors on the same terminal.

Current sensor highlights:

- Measures current magnitude and angle with global or local angle interpretation.
- Cannot be coupled to `link`.
- Do not mix global-angle and local-angle current sensors on the same terminal.
- Special invalid measurement combinations exist (for example zero magnitude with certain angles).

### Fault

- Faults are located at nodes.
- Per scenario, multiple faults are allowed but type/phase consistency is constrained.
- If any scenario contains a non-three-phase fault, the short-circuit treatment is asymmetric.
- Key outputs include fault current magnitude and angle.

### Regulator family

Regulator common inputs:

- `regulated_object`, `status`

Transformer tap regulator highlights:

- Regulates tap position of transformer or three-winding transformer.
- Supports line-drop compensation as a virtual control correction.
- Output reports optimal tap; it does not itself mutate grid state post-calculation.

Voltage regulator highlights:

- Controls generator/load reactive power to hold node voltage setpoint.
- Supported for Newton-Raphson power flow.
- Reactive-limit behavior exists but full limit enforcement reporting is still evolving.

## High-Impact Modeling Gotchas

- Do not treat symmetry of component typing as equivalent to symmetry of calculation mode.
- Always confirm reference direction before interpreting sign of `p` and `q`.
- Keep IDs globally unique per scenario across all component types.
- Validate required zero-sequence parameters whenever asymmetric or non-three-phase faults are involved.
- Avoid sensors on `link` and avoid disallowed sensor-mixing patterns on one terminal.
- Use PGM metadata/dtype utilities (or PGM-DS abstractions) instead of handcrafted dtype edits.

## When to Use This Reference

Use this page when you need to answer:

- What components are valid in PGM input data.
- Which attributes are required and what they mean.
- How dataset and batch structures are represented.
- How to interpret output sign, phase dimensions, and component-level semantics.

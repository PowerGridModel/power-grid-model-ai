<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Calculation Recipes

Defaults and the valid `calculation_method` per calculation are in `overview-and-entrypoints.md`.

## Recipe 1: Power Flow

```python
from power_grid_model import ComponentType, PowerGridModel

model = PowerGridModel(input_data)
out = model.calculate_power_flow()  # symmetric, Newton-Raphson
node_result = out[ComponentType.node]
```

Pass `symmetric=False` for per-phase results (`u_pu` etc. get a trailing dimension of 3). Asymmetric calculation needs zero-sequence data (`r0`, `x0`, `c0`, `tan0` on lines): with NaN zero-sequence values it fails with `SparseMatrixError`.

## Recipe 2: Selected Outputs

```python
from power_grid_model import AttributeType, ComponentType

out = model.calculate_power_flow(
    output_component_types={
        ComponentType.node: None,  # row-based
        ComponentType.line: [AttributeType.id, AttributeType.p_from],  # columnar dict
    }
)
```

## Recipe 3: State Estimation

```python
out = model.calculate_state_estimation()  # iterative_linear; or calculation_method=CalculationMethod.newton_raphson
```

Needs at least one voltage sensor and enough independent measurements for the unknowns; otherwise it raises `NotObservableError` ("No voltage sensor found!" / "Not enough measurements") or `SparseMatrixError`. Sensor results are `*_residual` attributes.

## Recipe 4: Short Circuit

Short circuit needs `fault` components in `input_data`. Give every `source` a finite `sk` and an `rx_ratio`; NaN values silently default to `sk = 1e10` VA and `rx_ratio = 0.1` (and validation does not flag them), giving unrealistically large currents, so take `sk` from the user or state the assumed value.

```python
import numpy as np
from power_grid_model import (
    CalculationMethod, ComponentType, DatasetType, FaultPhase, FaultType,
    PowerGridModel, ShortCircuitVoltageScaling, initialize_array,
)

# One inactive fault per node, activated one scenario at a time (batch over nodes)
node_ids = input_data[ComponentType.node]["id"]
n = len(node_ids)
fault = initialize_array(DatasetType.input, ComponentType.fault, n)
fault["id"] = fault_ids  # n ids not used by any other component
fault["status"] = 0
fault["fault_type"] = FaultType.three_phase
fault["fault_phase"] = FaultPhase.abc
fault["fault_object"] = node_ids
model = PowerGridModel({**input_data, ComponentType.fault: fault})

update = initialize_array(DatasetType.update, ComponentType.fault, (n, n))
update["id"] = fault["id"]
update["status"] = np.eye(n, dtype=int)

out = model.calculate_short_circuit(
    update_data={ComponentType.fault: update},
    short_circuit_voltage_scaling=ShortCircuitVoltageScaling.maximum,  # .minimum for the c_min case
)
```

Output notes:
- Results are always per phase: `node["u_pu"]` is `(n_scenarios, n_nodes, 3)`, `line["i_from"]` is `(n_scenarios, n_lines, 3)`, `fault["i_f"]` is `(n_scenarios, n_faults, 3)`. Take the active fault's entry (`i_f[np.arange(n), np.arange(n)]`); a three-phase fault has equal values on all three phases, a single-phase-to-ground fault carries current on the faulted phase only. Node short-circuit output has no `p`/`q`.
- Non-three-phase faults need zero-sequence line data (`r0`, `x0`, ...). Without it the calculation raises `SparseMatrixError`; in a batch this surfaces as `PowerGridBatchError`, and with `continue_on_batch_error=True` each scenario's `SparseMatrixError` is in `model.batch_error.errors`. Ask for or state the zero-sequence assumption.

## Recipe 5: Regulated Power Flow (Tap Changing)

```python
from power_grid_model import ComponentType, TapChangingStrategy

out = model.calculate_power_flow(tap_changing_strategy=TapChangingStrategy.any_valid_tap)
tap_pos = out[ComponentType.transformer_tap_regulator]["tap_pos"]
```

- Requires `transformer_tap_regulator` components; `u_set` and `u_band` are in volt (on the `control_side`), not per unit. If no tap position within `tap_min..tap_max` meets the band, the calculation raises `MaxIterationReached`.
- Strategies: `disabled` (default; regulator `tap_pos` output is the null value -128), `any_valid_tap`, `min_voltage_tap`, `max_voltage_tap`, `fast_any_tap` (binary search).
- The result is the optimal tap in the regulator output; the transformer's input `tap_pos` stays unchanged.

## Recipe 6: Newton-Raphson Flat Start

```python
from power_grid_model import CalculationInitialization

out = model.calculate_power_flow(calculation_initialization=CalculationInitialization.flat)
```

Use `flat` when the default start (linear, for Newton-Raphson) diverges on meshed, transmission-like grids. Other members: `linear`, `average_source`, `default`. Only Newton-Raphson uses it. Available since v1.13.185.

## Method Selection

- Power flow: Newton-Raphson by default; `iterative_current` suits time-series batches on radial grids; `linear` and `linear_current` are approximations (verify against a nonlinear baseline).
- State estimation: `iterative_linear` by default; `newton_raphson` when measurement weighting with nonlinear effects matters.
- The symmetric (default) calculation returns one value per attribute; asymmetric returns per-phase values and needs per-phase/zero-sequence parameters. Short circuit is always per phase.

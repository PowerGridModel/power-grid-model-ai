<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Calculation Recipes

## Recipe 1: One-Time Power Flow (Symmetric)

```python
from power_grid_model import CalculationMethod, ComponentType, PowerGridModel

model = PowerGridModel(input_data)
out = model.calculate_power_flow(
    symmetric=True,
    calculation_method=CalculationMethod.newton_raphson,
    error_tolerance=1e-8,
    max_iterations=20,
)
node_result = out[ComponentType.node]
```

Use this as the default for robust general-purpose studies.

## Recipe 2: Power Flow with Selected Outputs

```python
from power_grid_model import AttributeType, ComponentType

out = model.calculate_power_flow(
    output_component_types={
        ComponentType.node: None,
        ComponentType.line: [AttributeType.id, AttributeType.p_from],
    }
)
```

Use when memory/time matters and only a few fields are required.

## Recipe 3: Asymmetric Power Flow

```python
out = model.calculate_power_flow(symmetric=False)
```

Use when per-phase effects or non-balanced conditions matter.

## Recipe 4: State Estimation

```python
from power_grid_model import CalculationMethod

out = model.calculate_state_estimation(
    symmetric=True,
    calculation_method=CalculationMethod.iterative_linear,
)
```

Switch to `CalculationMethod.newton_raphson` when measurement weighting and nonlinear effects need tighter treatment.

## Recipe 5: Short Circuit

```python
from power_grid_model import CalculationMethod, ShortCircuitVoltageScaling

out = model.calculate_short_circuit(
    calculation_method=CalculationMethod.iec60909,
    short_circuit_voltage_scaling=ShortCircuitVoltageScaling.maximum,
)
```

## Recipe 6: Regulated Power Flow with Tap Strategy

```python
from power_grid_model import TapChangingStrategy

out = model.calculate_power_flow(
    tap_changing_strategy=TapChangingStrategy.any_valid_tap,
)
```

Strategy options include:

- `disabled`
- `any_valid_tap`
- `min_voltage_tap`
- `max_voltage_tap`
- `fast_any_tap`

## Method Selection Guide

- Start with Newton-Raphson for power flow unless you have a clear speed reason.
- Use iterative current for time-series style batches on radial grids.
- Use linear and linear_current for high-volume approximations, and verify against a nonlinear baseline.
- For state estimation, iterative linear is default; Newton-Raphson is often preferred when nonlinear sensor weighting behavior matters.

## Symmetric vs Asymmetric Practical Rules

Symmetric:

- Faster
- Single value outputs per component attribute
- Good default for balanced networks

Asymmetric:

- Per-phase modeling and outputs
- Required for many non-three-phase short-circuit cases
- Requires proper zero-sequence/per-phase parameters

## State Estimation Observability Notes

Practical requirements to check before running:

- At least one voltage measurement available.
- Sufficient independent measurements relative to unknown states.
- If unobservable, expect `NotObservableError` or `SparseMatrixError`.


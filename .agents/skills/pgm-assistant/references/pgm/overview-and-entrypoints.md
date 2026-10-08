<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Overview and Entry Points

## Scope of This Layer

`power-grid-model` is the core steady-state calculation engine. For application work, treat it as:

- Dataset in (structured numpy arrays)
- Calculation call
- Dataset out

Core calculation types:

- Power flow
- State estimation
- Short circuit

## Canonical Imports

```python
from power_grid_model import (
    AttributeType,
    CalculationMethod,
    CalculationType,
    ComponentAttributeFilterOptions,
    ComponentType,
    DatasetType,
    PowerGridModel,
    attribute_dtype,
    initialize_array,
)
from power_grid_model.validation import (
    assert_valid_input_data,
    assert_valid_batch_data,
)
from power_grid_model.utils import (
    get_dataset_batch_size,
    get_dataset_scenario,
    json_deserialize_from_file,
    json_serialize_to_file,
)
```

## Primary Entry Points

- `PowerGridModel(input_data, system_frequency=50.0)`
- `model.update(update_data=...)`
- `model.calculate_power_flow(...)`
- `model.calculate_state_estimation(...)`
- `model.calculate_short_circuit(...)`

Supporting helpers:

- `initialize_array(data_type, component_type, shape, empty=False)`
- `attribute_dtype(data_type, component_type, attribute)`
- `attribute_empty_value(data_type, component_type, attribute)`
- `power_grid_meta_data`

## Data Model Reminders

- Dataset is a `dict[ComponentType, ComponentData]`.
- Component data can be row-based or columnar.
- Batch update supports dense and sparse forms.
- Batch can also be a list of datasets interpreted as a cartesian product.

For full component/attribute semantics and dataset terminology, see `data-model-components-and-datasets.md`.

## Standard Lifecycle

1. Build `input_data` with `initialize_array(...)`.
2. Validate with `assert_valid_input_data(...)`.
3. Construct model.
4. Run `calculate_*` call.
5. Optionally apply permanent `model.update(...)`.
6. For batch, provide `update_data` to `calculate_*`.

## Calculation Call Defaults (Application-Relevant)

- `calculate_power_flow`: `symmetric=True`, `calculation_method=CalculationMethod.newton_raphson`, `error_tolerance=1e-8`, `max_iterations=20`
- `calculate_state_estimation`: `symmetric=True`, `calculation_method=CalculationMethod.iterative_linear`, `error_tolerance=1e-8`, `max_iterations=20`
- `calculate_short_circuit`: `calculation_method=CalculationMethod.iec60909`, `short_circuit_voltage_scaling=maximum`

## Output Shaping

Use `output_component_types` to reduce compute/memory:

- `None`: all components, row-based
- `[ComponentType.node, ...]`: selected components
- `ComponentAttributeFilterOptions.everything`: all components, columnar
- `{ComponentType.line: [AttributeType.id, AttributeType.p_from], ...}`: per component and attributes

## Batch Controls

- `threading=-1`: sequential
- `threading=0`: all hardware threads
- `threading>0`: specific thread count
- `continue_on_batch_error=True`: returns partially valid output; inspect `model.batch_error`

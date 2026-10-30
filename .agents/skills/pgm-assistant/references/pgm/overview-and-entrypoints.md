<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Overview and Entry Points

`power-grid-model` is a steady-state engine: dataset in (structured numpy arrays) → `calculate_*` → dataset out.

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
    json_deserialize_from_file,  # takes a pathlib.Path, not str
    json_serialize_to_file,
)
```

## Entry Points

- `PowerGridModel(input_data, system_frequency=50.0)`
- `model.update(update_data=...)`: permanent update of the model.
- `model.calculate_power_flow(...)`, `model.calculate_state_estimation(...)`, `model.calculate_short_circuit(...)`: all arguments are keyword-only.
- `initialize_array(data_type, component_type, shape, empty=False)`: `shape` is an int (single) or `(n_scenarios, n)` (dense batch); unset attributes are NaN-style "null" values unless `empty=True` (uninitialized memory).
- `attribute_dtype(data_type, component_type, attribute)`, `attribute_empty_value(...)`, `power_grid_meta_data[dataset_type][component_type]` (numpy dtype of every attribute; `power_grid_meta_data["update"][c].dtype.names` lists the updatable attributes).

Dataset formats are described in `data-model-components-and-datasets.md`.

## Standard Lifecycle

1. Build `input_data` with `initialize_array(...)`.
2. `assert_valid_input_data(input_data, calculation_type=...)`.
3. `PowerGridModel(input_data)`.
4. `calculate_*`; for batch pass `update_data=...` to the call (the model itself is left unchanged).

## Calculation Defaults and Valid Methods

| Call | Extra defaults | Valid `calculation_method` |
| --- | --- | --- |
| `calculate_power_flow` | `symmetric=True`, `error_tolerance=1e-8`, `max_iterations=20`, `tap_changing_strategy=disabled`, `calculation_initialization=default` | `newton_raphson` (default), `linear`, `iterative_current`, `linear_current` |
| `calculate_state_estimation` | `symmetric=True`, `error_tolerance=1e-8`, `max_iterations=20` | `iterative_linear` (default), `newton_raphson` |
| `calculate_short_circuit` | no `symmetric` argument (output is always per phase), `short_circuit_voltage_scaling=maximum` | `iec60909` (only) |

Any other method raises `InvalidCalculationMethod`. `calculation_method` and the strategy/initialization arguments also accept the member name as a string.

## Output Shaping (`output_component_types`)

- `None`: all components that produce output for this calculation, row-based (sensors are returned only by state estimation, even if requested for other calculations).
- `[ComponentType.node, ...]` or a set: those components, row-based.
- `ComponentAttributeFilterOptions.everything`: all components, columnar (dict of attribute → array).
- `ComponentAttributeFilterOptions.relevant`: columnar, only non-empty components and attributes that contain non-NaN values.
- `{ComponentType.node: None, ComponentType.line: [AttributeType.id, AttributeType.p_from]}`: per component; `None` gives row-based, a list of attributes (or a filter option) gives columnar. The result can therefore mix row-based and columnar components.

## Batch Controls

- `threading`: `<0` sequential (default `-1`), `0` all hardware threads, `>0` that many threads.
- `continue_on_batch_error=True`: failed scenarios do not raise; inspect `model.batch_error` (`failed_scenarios`, `succeeded_scenarios`, `error_messages`, `errors`). Without it a failing scenario raises `PowerGridBatchError`.
- `update_data` may be a list of batch datasets: the scenarios form a cartesian product and the output is flattened to `(prod(batch sizes), n_elements)`.

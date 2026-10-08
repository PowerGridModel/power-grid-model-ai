<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Batch, Validation, and Serialization

For task-level validation workflow (scope, checkpoints, deliverables), start with `../tasks/data-validation.md`.

## Batch Dataset Forms

PGM accepts update batch data in multiple forms.

### Dense batch (uniform per scenario)

- Shape is `(n_scenarios, n_objects)` for each component array.
- Best when all scenarios update the same object set.

### Sparse batch (only changed records)

- Use a dict with keys `indptr` and `data`.
- `indptr` length is `n_scenarios + 1`.
- Scenario `k` uses slice `data[indptr[k]:indptr[k + 1]]`.

### Cartesian product batch

- Pass `update_data=[batch_a, batch_b, ...]`.
- Effective scenario count is product of individual batch sizes.
- Output is flattened over the cartesian product.

## Batch Execution Controls

- `threading=-1`: sequential
- `threading=0`: hardware threads
- `threading>0`: fixed thread count
- `continue_on_batch_error=False`: raise immediately on any failed scenario
- `continue_on_batch_error=True`: continue and inspect `model.batch_error`

## Validation Functions

Use these before expensive calculations.

### Input-only validation

```python
from power_grid_model.validation import validate_input_data, assert_valid_input_data

errors = validate_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)
assert_valid_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)
```

### Input + batch update validation

```python
from power_grid_model.validation import validate_batch_data, assert_valid_batch_data

errors = validate_batch_data(
    input_data,
    update_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)
assert_valid_batch_data(
    input_data,
    update_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)
```

Important nuance:

- In batch mode, base input may be incomplete if every missing value is overwritten by each scenario.
- In that case `validate_input_data` can fail while `validate_batch_data` succeeds.

## Error Text Rendering

```python
from power_grid_model.validation import errors_to_string

message = errors_to_string(errors, name="update_data", details=True)
print(message)
```

## Serialization APIs

### JSON

- `json_deserialize(...)`
- `json_serialize(...)`
- `json_deserialize_from_file(path)`
- `json_serialize_to_file(path, data, dataset_type=...)`

### Msgpack

- `msgpack_deserialize(...)`
- `msgpack_serialize(...)`
- `msgpack_deserialize_from_file(path)`
- `msgpack_serialize_to_file(path, data, dataset_type=...)`

## Dataset Utilities

- `get_dataset_type(data)`
- `get_dataset_batch_size(batch_dataset)`
- `get_dataset_scenario(batch_dataset, scenario)`
- `is_columnar(component_data)`
- `is_sparse(component_data)`

## Practical Sequence for Large Studies

1. Build `input_data`.
2. Build one or more batch datasets.
3. Validate batch datasets.
4. Execute `calculate_*` with output filtering.
5. On failure, inspect `model.batch_error` and rerun only failed slices if needed.
6. Persist input/output snapshots using JSON/msgpack utilities.

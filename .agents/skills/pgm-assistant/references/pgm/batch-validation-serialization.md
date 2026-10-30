<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Batch, Validation, and Serialization

For the validation workflow (stages, deliverables), see `../tasks/data-validation.md`. For exceptions, see `errors-and-debugging.md`.

## Batch Dataset Forms

- Dense: `(n_scenarios, n_objects)` array per component; every scenario updates the same objects.
- Sparse: `{"indptr": ..., "data": ...}` per component; `len(indptr) == n_scenarios + 1` and scenario `k` uses `data[indptr[k]:indptr[k + 1]]`.
- Cartesian product: `update_data=[batch_a, batch_b, ...]`; output is flattened to `(prod(batch sizes), n_objects)`. `validate_batch_data` does not accept a list; validate each dataset separately.

## Batch Execution Controls

- `threading`: `< 0` sequential (default `-1`), `0` all hardware threads, `> 0` that many threads.
- `continue_on_batch_error=False` (default): a failed scenario raises `PowerGridBatchError`.
- `continue_on_batch_error=True`: returns the output; every `calculate_*` call resets `model.batch_error` to `None` or the `PowerGridBatchError`. Reading it before the first calculation raises `AttributeError`. Rows of failed scenarios are uninitialised garbage; see `errors-and-debugging.md` for the filtering pattern.

## Validation Functions

```python
from power_grid_model import CalculationType  # not in power_grid_model.validation
from power_grid_model.validation import (
    assert_valid_batch_data, assert_valid_input_data, errors_to_string,
    validate_batch_data, validate_input_data, ValidationException,
)

errors = validate_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)
batch_errors = validate_batch_data(input_data, update_data, calculation_type=CalculationType.power_flow, symmetric=True)
assert_valid_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)
assert_valid_batch_data(input_data, update_data, calculation_type=CalculationType.power_flow, symmetric=True)
print(errors_to_string(batch_errors, name="update_data", details=True))
```

- `validate_input_data` returns `list[ValidationError] | None`; `validate_batch_data` returns `dict[int, list[ValidationError]] | None`, keyed by 0-based scenario index. `None` means valid, so test with `if errors is None` / `if errors:`, never `len(errors)`.
- `assert_valid_*` raise `ValidationException` (a `ValueError`, not a `PowerGridError`) with `.errors` and `.name`.
- Each `ValidationError` has `.component`, `.field`, `.ids` (component ids, not row indices) and `str(err)`.
- Wrong dtypes, unknown component names or malformed structure raise `KeyError`/`TypeError`/`ValueError` instead of returning errors.
- `calculation_type=None` (default) requires every field; pass the `CalculationType` to allow missing fields the calculation does not use.
- Batch validation checks required and value rules on each scenario merged into the base input, so the base input may be incomplete when every scenario fills the gaps; `validate_input_data` can then fail while `validate_batch_data` passes. Base-input id uniqueness errors are repeated under each scenario.
- Update ids missing from the input (including ids of a component of another type) come back as `IdNotInDatasetError`.
- The validators do not detect `ConflictVoltage` (mismatching `u_rated` across a line) or state-estimation observability problems; these only fail at calculation time.
- `errors_to_string(errors, name="the data", details=False, id_lookup=None)` accepts `None` (returns `"<name>: OK"`); `id_lookup` (list or `dict[int, str]`) shows custom labels for ids.

## Serialization

All from `power_grid_model.utils`. File functions take a `pathlib.Path`; a `str` raises `AttributeError`.

- `json_serialize(data, dataset_type=None, use_compact_list=False, indent=2) -> str`; `json_deserialize(data: str | bytes, data_filter=None)`
- `json_serialize_to_file(file_path, data, dataset_type=None, use_compact_list=False, indent=2)`; `json_deserialize_from_file(file_path, data_filter=None)`
- `msgpack_serialize(data, dataset_type=None, use_compact_list=False) -> bytes`; `msgpack_deserialize(data: bytes, data_filter=None)`
- `msgpack_serialize_to_file(file_path, data, dataset_type=None, use_compact_list=False)`; `msgpack_deserialize_from_file(file_path, data_filter=None)`

Deserialization returns the dataset dict; `data_filter` takes the same forms as `output_component_types`. `dataset_type` is deduced from row-based component data; pass `dataset_type=DatasetType.update` (or `input`, ...) for empty data, which otherwise raises `ValueError`.

## Dataset Utilities (`power_grid_model.utils`)

- `get_dataset_type(data)`, `get_dataset_batch_size(batch_dataset)`
- `get_dataset_scenario(batch_dataset, scenario) -> dict`: single-scenario dataset, also for sparse batches. Feed it to `model.update(update_data=...)`; passing it as `update_data=` of `calculate_*` raises `PowerGridError`.
- `is_columnar(component_data)`, `is_sparse(component_data)`

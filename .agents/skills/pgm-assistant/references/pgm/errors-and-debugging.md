<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Errors and Debugging

Run the validation-first flow in `../tasks/data-validation.md` before deep error triage.

## Exception Classes

Import from `power_grid_model.errors`. All derive from `PowerGridError` (a `RuntimeError`); catch the parent class to cover its children:

- `SparseMatrixError` > `NotObservableError`
- `IterationDiverge` > `MaxIterationReached`
- `InvalidID` > `IDNotFound`, `IDWrongType`, `ConflictID`, `InvalidMeasuredObject`, `InvalidRegulatedObject`

Messages are decoded into these classes; an unrecognised message becomes a plain `PowerGridError`. Validation failures raised by `assert_valid_*` are `ValidationException` (a `ValueError`), see `batch-validation-serialization.md`.

| Exception | Trigger | Action |
| --- | --- | --- |
| `IDNotFound` | Update references an id absent from the model. `IDWrongType` if the id belongs to another component type. | `validate_batch_data` reports both as `IdNotInDatasetError`. |
| `ConflictVoltage` | A line connects nodes with different `u_rated`. The validators do not flag this. | Check `u_rated` of the line's two nodes. |
| `NotObservableError` | State estimation without enough independent measurements, or no usable voltage sensor (none present, or all `u_sigma` = `inf`). The validators do not flag this. | Add a voltage sensor and enough power sensors; check for `inf` sigma. |
| `SparseMatrixError` | Singular system matrix (message: "possibly singular matrix"). | Look for floating or ill-defined parts of the grid; in state estimation see `NotObservableError`. |
| `IterationDiverge` | Iterative method (e.g. `newton_raphson`, `iterative_current`) does not converge in `max_iterations`. Linear methods do not iterate. | Validate data; adjust `error_tolerance` / `max_iterations`; compare with a linear method to isolate data problems. |
| `PowerGridBatchError` | One or more batch scenarios fail with `continue_on_batch_error=False`. | See below. |

## `PowerGridBatchError`

Attributes: `failed_scenarios` and `succeeded_scenarios` (index arrays), `error_messages` (`list[str]`), `errors` (typed exceptions, e.g. `IDNotFound`, aligned with `failed_scenarios`). Per-scenario causes (such as `IDNotFound` in an update) surface only inside `errors`; the raised class is always `PowerGridBatchError`.

```python
from power_grid_model import AttributeType, ComponentType
from power_grid_model.errors import PowerGridBatchError

try:
    out = model.calculate_power_flow(update_data=batch_update)
except PowerGridBatchError as e:
    print(e.failed_scenarios, e.error_messages)

# partial success: failed scenarios hold uninitialised rows
out = model.calculate_power_flow(update_data=batch_update, continue_on_batch_error=True)
e = model.batch_error  # None when every scenario succeeded
if e is not None:
    valid_u = out[ComponentType.node][AttributeType.u_pu][e.succeeded_scenarios]
```

## Gotchas

- A failed `model.update(...)` can leave the model in an invalid state; recreate it from known-good input.
- Reproduce one scenario with `model.update(update_data=get_dataset_scenario(update_data, k))` on a fresh model, then calculate without `update_data`.
- `InvalidCalculationMethod`: the method does not exist for that calculation type (e.g. `iterative_linear` in power flow); an unknown method string raises `KeyError`.

## Calculation Logger (Opt-in Diagnostics)

```python
from power_grid_model import Logger, LoggerType

with Logger(LoggerType.info) as logger:
    model.calculate_power_flow()
print(logger.output)
```

- `LoggerType.info` (default) yields timestamped lines; `LoggerType.benchmark` yields timing per calculation phase. The format is not stable; do not parse it.
- `output` stays readable after the `with` block. With `python_logger=<logging.Logger>` (level `python_logging_level`, default `logging.INFO`) the lines are forwarded and the buffer is cleared on exit, so read `output` inside the block.

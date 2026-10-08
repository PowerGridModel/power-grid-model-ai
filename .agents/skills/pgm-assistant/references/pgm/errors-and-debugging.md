<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Errors and Debugging

For validation-first troubleshooting flow, see `../tasks/data-validation.md` before deep error triage.

## High-Frequency Exceptions

### `PowerGridBatchError`

Typical trigger:

- Some batch scenarios fail while others succeed.

Inspect:

- `failed_scenarios`
- `succeeded_scenarios`
- `error_messages`
- `errors`

Use:

- Run with `continue_on_batch_error=True` to keep valid results.

### `IDNotFound`

Typical trigger:

- Update references IDs not present in base input.

Action:

- Validate with `assert_valid_batch_data` before calculation.
- Confirm id columns and type alignment.

### `ConflictVoltage`

Typical trigger:

- Inconsistent rated voltages across connected topology.

Action:

- Validate input data and inspect component-level voltage attributes.

### `NotObservableError` or `SparseMatrixError` in state estimation

Typical trigger:

- Missing or non-independent measurements.

Action:

- Re-check observability conditions.
- Ensure at least one valid voltage measurement.
- Check sensor sigma values for accidentally disabled measurements (`inf`).

### `MaxIterationReached` or `IterationDiverge`

Typical trigger:

- Iterative method cannot converge with current settings/data.

Action:

- Validate data.
- Relax tolerance or increase max iterations.
- Compare against linear method to identify data pathologies.

## Important Behavioral Edge Cases

- If `model.update(...)` fails, model can be left in an invalid state.
- Discard and recreate model from known-good input after failed updates.
- Batch results with failed scenarios can include unusable rows for those scenarios.
- Filter outputs by `succeeded_scenarios`.

## Debug Checklist

1. Run validation (`assert_valid_input_data` / `assert_valid_batch_data`).
2. Narrow output with `output_component_types` for focused inspection.
3. Reproduce with single scenario (`get_dataset_scenario`).
4. Check algorithm and mode assumptions (`symmetric` vs `asymmetric`, method compatibility).
5. Inspect IDs and component references for update datasets.
6. Recreate model if any update failed mid-run.

## Minimal Batch Error Pattern

```python
from power_grid_model.errors import PowerGridBatchError

try:
    out = model.calculate_power_flow(update_data=batch_update)
except PowerGridBatchError as e:
    print("failed:", e.failed_scenarios)
    print("ok:", e.succeeded_scenarios)
    print("messages:", e.error_messages)
```

## Minimal Partial-Success Pattern

```python
out = model.calculate_power_flow(
    update_data=batch_update,
    continue_on_batch_error=True,
)
e = model.batch_error
valid_u = out[ComponentType.node][AttributeType.u_pu][e.succeeded_scenarios]
```

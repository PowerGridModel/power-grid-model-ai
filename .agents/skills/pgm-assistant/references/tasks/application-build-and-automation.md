<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Application Build and Automation

Use this playbook to build or extend a PGM-based workflow or application (for example import -> validate -> run -> export), not for a one-off calculation.

## Layers

1. Ingestion and conversion (PGM-IO).
2. Validation gate (PGM validation APIs, then realism rules from `validation-rules.yml`).
3. Grid manipulation and topology (PGM-DS).
4. Calculation (PGM).
5. Output adaptation, KPIs and reporting.

## Workflow Skeleton

```python
from power_grid_model import CalculationType, PowerGridModel
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data

# 1) Convert to PGM datasets (PGM-IO); keep extra_info for traceability
input_data, extra_info = converter.load_input_data(raw_source)
update_data = converter.load_update_data(raw_update_source)  # optional

# 2) Validate inputs and, for batches, the combination with update data
assert_valid_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)
assert_valid_batch_data(input_data, update_data, calculation_type=CalculationType.power_flow, symmetric=True)

# 3) Run
model = PowerGridModel(input_data)
out = model.calculate_power_flow(update_data=update_data)

# 4) Export: PgmJsonConverter can save any converter's output plus extra_info
PgmJsonConverter(destination_file=destination).save(data=out, extra_info=extra_info)
```

`save` is not implemented for Vision, tabular or pandapower converters; see `references/pgm-io/overview-and-converter-selection.md` for what each converter supports.

To sync results into a PGM-DS `Grid`, use `PowerGridModelInterface(grid=grid)` with its own `calculate_power_flow()` followed by `update_grid()` (it takes no arguments and reads the interface's stored output); see `references/pgm-ds/pgm-interface-workflow.md`.

## Design Rules

- Keep conversion, validation, execution and reporting as separate steps; fail at the validation boundary.
- Wrap `calculate_*` in a task-specific function (calculation type, symmetric flag, algorithm, tolerance as parameters) instead of hard-coding one method.
- Handle partial batch failures explicitly (see `references/pgm/errors-and-debugging.md`).
- Persist `input_data`, `update_data`, outputs and assumptions for reproducibility.

## Primary References

- `references/pgm-io/overview-and-converter-selection.md`
- `references/pgm/overview-and-entrypoints.md`
- `references/pgm/batch-validation-serialization.md`
- `references/pgm-ds/pgm-interface-workflow.md`
- `references/pgm/errors-and-debugging.md`

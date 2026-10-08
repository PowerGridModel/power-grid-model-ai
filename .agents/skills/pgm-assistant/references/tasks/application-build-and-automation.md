<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Application Build and Automation

## Purpose

Use this playbook when the goal is to build or extend a PGM-based workflow or application, not only to run a one-off calculation.

## Typical Inputs

- A desired capability (for example import -> validate -> run -> export)
- Supported source data formats (PGM JSON, Vision, Pandapower, tabular)
- Runtime constraints (batch size, latency, reproducibility)

## Recommended Architecture

1. Ingestion and conversion layer (PGM-IO).
2. Validation gate (PGM validation APIs).
3. Grid manipulation and topology layer (PGM-DS).
4. Calculation layer (PGM).
5. Output adaptation and reporting layer.

## Build Sequence

1. Choose converter and normalize datasets.
2. Validate `input_data` and `update_data`.
3. Create a reusable model execution function.
4. Add task-specific post-processing (for example limits, KPIs, export adapters).
5. Add error handling for partial batch failures.
6. Persist reproducible artifacts (`input_data`, `update_data`, outputs, assumptions).

## Minimal Workflow Skeleton

```python
# 1) Convert to PGM-compatible data (PGM-IO)
input_data, extra_info = converter.load_input_data(raw_source)

# 2) Validate (PGM)
assert_valid_input_data(input_data, calculation_type=CalculationType.power_flow, symmetric=True)

# 3) Build and run (PGM)
model = PowerGridModel(input_data)
out = model.calculate_power_flow(update_data=update_data)

# 4) Optional grid sync and app-layer operations (PGM-DS)
pgm_interface.update_grid(out)

# 5) Export/adapt
converter.save(data=out, extra_info=extra_info)
```

## Design Rules

- Keep conversion, validation, execution, and reporting as separate steps.
- Fail early at validation boundaries; do not postpone malformed data errors.
- Use task-specific wrappers around `calculate_*` instead of hard-coding one method everywhere.
- Keep `extra_info` for traceability across converters and outputs.

## Primary References

- `references/pgm-io/overview-and-converter-selection.md`
- `references/pgm/overview-and-entrypoints.md`
- `references/pgm/batch-validation-serialization.md`
- `references/pgm-ds/pgm-interface-workflow.md`
- `references/pgm/errors-and-debugging.md`

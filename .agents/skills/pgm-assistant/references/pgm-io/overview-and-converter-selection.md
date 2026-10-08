<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-IO Overview and Converter Selection

## What PGM-IO Solves
`power-grid-model-io` converts external formats into native PGM datasets and back.
It also preserves non-PGM metadata in `extra_info` for traceability.

## Converter Selection
- `PgmJsonConverter`:
  - Use when source/target is native PGM JSON.
- `VisionExcelConverter`:
  - Use for Vision Excel exports.
  - Built on tabular converter infrastructure.
- `PandaPowerConverter`:
  - Use for pandapower `net` conversion and result roundtrip.
- `TabularConverter`:
  - Use for custom table-based formats via YAML mapping files.

## Common Converter Lifecycle
```python
converter = SomeConverter(...)
input_data, extra_info = converter.load_input_data(...)
# run PGM calculation
converted_or_saved = converter.convert(output_data, extra_info=extra_info)
# or
converter.save(output_data, extra_info=extra_info)
```

## BaseConverter Methods (Cross-Converter)
- `load_input_data(...)`
- `load_update_data(...)`
- `load_sym_output_data(...)`
- `load_asym_output_data(...)`
- `load_sc_output_data(...)`
- `convert(data, extra_info=...)`
- `save(data, extra_info=..., destination=...)`
- `set_log_level(...)` and `get_log_level()`

## Extra Info and Cross-Reference
`extra_info` stores identifiers and metadata not part of PGM calculation arrays.
Examples:
- original table/index in source format
- names/labels
- GUIDs from Vision

Keep `extra_info` through input -> output pipelines when possible.

## Data Store Layer (When Needed)
Converters can use data stores to load/save from specific media:
- `JsonFileStore`
- `ExcelFileStore`
- `VisionExcelFileStore`

For custom pipelines, you can swap source/destination stores without changing conversion logic.

## Logging Strategy
Converter logging is local to converter instance and interacts with Python logging config.
Set both:
- global logging config
- converter-level log level

## Practical Rule
- Prefer existing converters and their defaults first.
- Use custom mappings only when source schema differs from defaults.
- Preserve `extra_info` for result reconciliation.

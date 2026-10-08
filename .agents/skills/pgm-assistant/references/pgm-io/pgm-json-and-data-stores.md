<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM JSON and Data Stores (PGM-IO)

## PgmJsonConverter Quick Workflow
Use `PgmJsonConverter` for native PGM JSON with `extra_info` support.

```python
from power_grid_model_io.converters import PgmJsonConverter

converter = PgmJsonConverter(
    source_file="data/input.json",
    destination_file="data/output.json",
)
input_data, extra_info = converter.load_input_data()
# run PGM
converter.save(data=output_data, extra_info=extra_info)
```

## Why Use This Instead of Raw PGM Utils
- Compatible with PGM JSON structure
- Preserves metadata in `extra_info`
- Easy source/destination management through converter API

## Data Stores You Will Encounter
- `JsonFileStore`: structured JSON load/save with formatting control
- `ExcelFileStore`: tabular Excel read/write
- `VisionExcelFileStore`: Vision-specific Excel handling (unit row handling)

## JsonFileStore Notes
- Supports indent and compact output settings.
- Expects structured dictionary/list payload forms.

## TabularData Wrapper
`TabularData` is used in tabular converter flows and supports:
- `set_unit_multipliers(...)`
- `set_substitutions(...)`
- `get_column(table_name, column_name)` with automatic unit/substitution application

## Mapping Helper Types
- `FieldMapping`
- `MultiplierMapping`
- `TabularMapping`
- `UnitMapping`
- `ValueMapping`

These are useful when building custom conversion logic or debugging mapping behavior.

## Utility Functions Worth Knowing
- `AutoID` for stable external-to-internal ID mapping
- `merge_dicts(...)`
- download helpers for fetching and extracting datasets
- JSON helpers (`JsonEncoder`, compact dumping)
- module loader helper (`get_function`) for mapping functions

## Practical Interchange Pattern
1. Load source data via converter/store.
2. Preserve `extra_info`.
3. Run PGM.
4. Save/convert output to target format.
5. Keep output + metadata together for reproducibility and traceability.

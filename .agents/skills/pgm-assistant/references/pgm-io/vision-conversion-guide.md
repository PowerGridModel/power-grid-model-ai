<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Vision Conversion Guide (PGM-IO)

## Standard Vision Workflow
1. Export Vision model to Excel.
2. Create converter:
```python
from power_grid_model_io.converters import VisionExcelConverter

converter = VisionExcelConverter(source_file="path/to/vision.xlsx", language="en")
input_data, extra_info = converter.load_input_data()
```
3. Validate input data with PGM validation.
4. Run PGM calculation.
5. Save output with `PgmJsonConverter` or convert as needed.

## Cross-Reference Helpers
Use these to map generated PGM integer IDs back to Vision identifiers:
- `lookup_id(pgm_id)`
- `get_node_id(number)`
- `get_branch_id(table, number)`
- `get_appliance_id(table, node_number, sub_number)`
- `get_virtual_id(table, obj_name, node_number, sub_number)`

## Language and Term Variants
- Default mapping supports English and Dutch workflows.
- Use `terms_changed` when Vision export uses alternate column names.

## GUID Handling (Vision 9.7+)
Vision switched to GUID-based identifiers.
PGM-IO converts GUIDs to integer IDs internally and can keep GUID in `extra_info` when configured in mapping.

## Optional Extra Columns
Use `optional_extra` in mapping when metadata columns may be absent.
- Required `extra` fields fail if missing.
- `optional_extra` fields are included only when present.

## Known Modeling Differences
Expect minor differences against Vision due to model differences, including:
- Transformer load modeling details
- Angle handling in symmetric power flow (transformer clock effects)
- Unsupported or approximated features (for example PV behavior details)
- Different convergence criteria between tools

## Known Spreadsheet Issues
- Duplicate `P` columns can appear in exports.
  - Mapping may need manual adjustment to renamed columns (`P_2`, etc.).
- Sheet naming can vary between versions.
  - Unmapped sheets are ignored.

## Security Notes
Vision converter inherits tabular security controls:
- safe YAML loading
- explicit function import paths
- safe XML parsing behavior

## Practical Checklist Before Production Runs
1. Confirm correct language/mapping version.
2. Verify required sheets are mapped.
3. Add optional metadata fields (GUID, StationID) where useful.
4. Keep `extra_info` in output pipeline for traceability.

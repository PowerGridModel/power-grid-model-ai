<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Vision Conversion Guide (PGM-IO)

## Workflow
```python
from power_grid_model import PowerGridModel
from power_grid_model_io.converters import PgmJsonConverter, VisionExcelConverter

converter = VisionExcelConverter(source_file="path/to/vision.xlsx", language="en")
input_data, extra_info = converter.load_input_data()
# validate_input_data(input_data), then:
output_data = PowerGridModel(input_data).calculate_power_flow()
PgmJsonConverter(destination_file="result.json").save(output_data, extra_info=extra_info)
```
- `VisionExcelConverter(source_file=None, language="en", terms_changed=None, mapping_file=None, log_level=...)`: `language` is `"en"` or `"nl"` and selects the shipped `config/excel/vision_{language}.yaml`; other values raise `FileNotFoundError`.
- `convert(output_data)` returns `TabularData`, not Excel; extra_info is not supported there ([overview-and-converter-selection.md](overview-and-converter-selection.md)). Persist results with `PgmJsonConverter` as above or with `json_serialize_to_file`.
- The mapping logic (`grid`, `units`, `auto_id`, ...) is documented in [tabular-mapping-reference.md](tabular-mapping-reference.md); `VisionExcelFileStore` reads the second header row as units.
- Sheets without a mapping entry are ignored; a sheet name that differs between Vision versions or languages silently yields no components.

## Column and Term Variants
`terms_changed={"exported name": "name used in mapping"}` renames Excel columns before mapping, e.g. `VisionExcelConverter(source_file=..., terms_changed={"Un": "Unom"})`.
Duplicate column names on one sheet (for example two `P` columns) are renamed `P_2`, `P_3`, ... with a logged warning; point the mapping at the renamed column if the second one is needed.

## GUID Exports (Vision 9.7+)
- `ExcelFileStore` inserts an integer column after every column whose name ends with `GUID`: `GUID` -> `Number` (`Nummer` for `nl`) and `From.GUID` -> `From.Number`; on appliance sheets (Loads, Sources, Transformer loads, ...) a plain `GUID` column becomes `Subnumber`. Integers are assigned in order of first appearance, shared across sheets.
- The default `vision_en.yaml` / `vision_nl.yaml` mappings keep no GUID. Shipped GUID mappings: `config/excel/vision_en_9_7.yaml` and `vision_en_9_8.yaml` (both add `GUID` to the node `extra`; no `nl` variants in 2.0.27). Select one with `mapping_file`:
  ```python
  import power_grid_model_io
  from pathlib import Path
  mapping = Path(power_grid_model_io.__file__).parent / "config" / "excel" / "vision_en_9_8.yaml"
  converter = VisionExcelConverter(source_file="vision.xlsx", mapping_file=mapping)
  ```
- Under `extra`, `{optional_extra: [GUID, StationID]}` includes columns only when present; plain `extra` columns must exist or conversion fails.

## Cross-Reference Helpers
Available when the mapping has an `id_reference` block (the shipped ones do); PGM ids are sequential from 0:
- `lookup_id(pgm_id)` -> `{"table": ..., "key": {...}}` (plus `"name"` for virtual objects)
- `get_node_id(number)`, `get_branch_id(table, number)`
- `get_appliance_id(table, node_number, sub_number)`
- `get_virtual_id(table, obj_name, node_number, sub_number)`: generated objects such as the internal node of a `Transformer loads` row.

## Known Differences to Vision Results
Expect small deviations from Vision (model differences, not conversion bugs): transformer load modelling, voltage angles in symmetric power flow (transformer clock), approximated PV behaviour, and different convergence criteria.

<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM JSON and Data Stores (PGM-IO)

## Two JSON Layouts
| Layout | Shape | Loader / writer |
|---|---|---|
| Serialization envelope (e.g. `json_serialize_to_file`, `tests/data/generated/*`) | `{"version": "1.0", "type": "input", "is_batch": false, "attributes": {}, "data": {"node": [...]}}` | `power_grid_model.utils.json_deserialize_from_file(Path(...))` / `json_serialize_to_file` |
| PGM-IO layout | `{"node": [{"id": 1, "u_rated": 10500, "name": "N0"}], "line": [...]}`; batch: a list of such dicts | `PgmJsonConverter` |

- Loading the wrong layout fails: an envelope into `PgmJsonConverter` raises `PowerGridSerializationError: Array expected ... data/version`; a PGM-IO file into `json_deserialize_from_file` raises `Key version not found!`.
- Envelopes written with `use_compact_list=True` store `data` as lists plus a non-empty `attributes`; the PGM-IO layout is never compact.
- The PGM-IO file has no type marker: pick `load_input_data`, `load_update_data`, `load_sym_output_data`, ... per file.
- Extra (non-PGM) attributes of an object go to `extra_info[id]`; this needs an integer `id`. Unknown component names raise `PowerGridSerializationError`. Extra info is not extracted from batch files (`UserWarning`) and is not written for batch data.

### Convert Between Layouts
```python
from pathlib import Path
from power_grid_model.utils import json_deserialize_from_file, json_serialize_to_file
from power_grid_model_io.converters import PgmJsonConverter

# envelope -> PGM-IO layout (single and batch data)
data = json_deserialize_from_file(Path("envelope.json"))
PgmJsonConverter(destination_file="pgm_io.json").save(data)

# PGM-IO layout -> envelope (input data; use load_update_data / load_sym_output_data for other types)
data, extra_info = PgmJsonConverter(source_file="pgm_io.json").load_input_data()
json_serialize_to_file(Path("envelope.json"), data)
```
`load_input_data(python_dict)` and `convert(data)` give the PGM-IO layout in memory without files; `convert(data, extra_info=extra_info)` merges `extra_info` back into the objects.

## Data Stores
Stores live in `power_grid_model_io.data_stores.<module>` (`json_file_store`, `excel_file_store`, `vision_excel_file_store`, `csv_dir_store`). Pass them as `source=` / `destination=` to `TabularConverter`, or as `destination=` to `converter.save(...)`. All take `Path` objects.
- `JsonFileStore(file_path)`: `.json` only; payload is a dict or a list of dicts. `set_indent(n | None)` (default 2) and `set_compact(bool)` (default `True`, one object per line; only effective when indent is set) control output.
- `ExcelFileStore(file_path=None, *, language="en", terms_changed=None, **extra_paths)`: `.xls`/`.xlsx`; row 0 holds the column names. Each extra keyword file `name=Path(...)` adds sheets prefixed `name.<sheet>`. Duplicate column names get a `_2`, `_3`, ... suffix with a logged warning.
- `VisionExcelFileStore(file_path, language="en", terms_changed=None)`: also reads row 1 as the unit row, so columns become `(name, unit)` tuples.
- `CsvDirStore(dir_path, **pandas_read_csv_kwargs)`: every `*.csv` in the directory is a table named after the file stem.

## TabularData
`from power_grid_model_io.data_types import TabularData`; `TabularData(**{table_name: DataFrame | structured ndarray | callable returning a DataFrame})`. Stores return it with lazily loaded sheets; use it as a context manager (or call `close()`) to release Excel readers.
- `get_column(table_name, column_name)` applies unit conversion and value substitution (rules in [tabular-mapping-reference.md](tabular-mapping-reference.md)); `"index"` returns the DataFrame index.
- `set_unit_multipliers(UnitMapping)` and `set_substitutions(ValueMapping)` are set by the converter from the mapping file.

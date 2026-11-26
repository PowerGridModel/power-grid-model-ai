<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-IO Overview and Converter Selection

`power-grid-model-io` converts external formats to native PGM datasets and back. Non-PGM metadata (names, GUIDs, original table/index) is returned separately as `extra_info`, a dict keyed by PGM component id.

## Converter Selection
- Standard PGM serialization JSON (`version`/`type`/`data` envelope): no converter, use `power_grid_model.utils.json_deserialize_from_file(Path(...))`. See [pgm-json-and-data-stores.md](pgm-json-and-data-stores.md).
- `PgmJsonConverter(source_file=None, destination_file=None, log_level=...)`: PGM-IO JSON layout (components at top level, no envelope); keeps `extra_info`.
- `VisionExcelConverter(source_file=None, language="en", terms_changed=None, mapping_file=None, log_level=...)`: Vision Excel exports, see [vision-conversion-guide.md](vision-conversion-guide.md).
- `PandaPowerConverter(system_frequency=50.0, trafo_loading="current", log_level=...)`: pandapower nets, see [pandapower-conversion-guide.md](pandapower-conversion-guide.md).
- `TabularConverter(mapping_file: Path = None, source=None, destination=None, log_level=...)`: custom table formats via YAML mapping, see [tabular-mapping-reference.md](tabular-mapping-reference.md).

Import the first three from `power_grid_model_io.converters`; `TabularConverter` lives in `power_grid_model_io.converters.tabular_converter`.
File arguments of `PgmJsonConverter` and `VisionExcelConverter` accept `str` or `Path`; `TabularConverter(mapping_file=...)` and data stores need `Path` objects (a `str` raises `AttributeError: ... 'suffix'`).

## Converter Lifecycle
```python
converter = SomeConverter(...)
input_data, extra_info = converter.load_input_data()      # or load_input_data(data_in_source_format)
# run PGM calculation -> output_data
converted = converter.convert(output_data, extra_info=extra_info)   # returns target-format data
converter.save(output_data, extra_info=extra_info)                  # converts and writes to the destination store
```
- Loaders on every converter: `load_input_data(data=None, make_extra_info=True)`, `load_update_data`, `load_sym_output_data`, `load_asym_output_data`, `load_sc_output_data`. Without `data`, they read from the source store.
- `save` needs a destination: `destination_file` (`PgmJsonConverter`) or `destination=` store, else `ValueError: No destination supplied!`.
- Support differs per converter:

| Converter | Loaders | `convert` / `save` |
|---|---|---|
| `PgmJsonConverter` | all dataset types | `extra_info` supported for single (non-batch) data only |
| `VisionExcelConverter`, `TabularConverter` | all dataset types | `convert(data)` returns `TabularData`; `extra_info=` raises `NotImplementedError` |
| `PandaPowerConverter` | `load_input_data` only | `convert` only (no destination); see its guide for the `extra_info` rule |

- Log level: `set_log_level(level)` / `get_log_level()` act on the converter's own logger.

## extra_info
- Tabular and pandapower converters add `id_reference` (source table, key or index, optional `name`); tabular converters also add the columns listed under `extra` in the mapping; `PgmJsonConverter` stores every non-PGM attribute of an object.
- Generated ids (`AutoID`, pandapower) are sequential from 0 and unique across all components.

## CIM/CGMES
PGM-IO has no CIM/CGMES converter. Upstream docs point to external ones: `cgmes2pgm_converter` and the converter in `Sparlectra.jl`.

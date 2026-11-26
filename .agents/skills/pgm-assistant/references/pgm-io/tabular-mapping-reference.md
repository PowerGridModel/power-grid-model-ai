<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-IO Tabular Mapping Reference

`TabularConverter(mapping_file=Path("map.yaml"), source=<store>)` (import path and constructor: [overview-and-converter-selection.md](overview-and-converter-selection.md)). Shipped real-world mappings to copy from: `power_grid_model_io/config/excel/vision_*.yaml`; `config/examples/multipliers.yaml`.

## File Layout
Top-level keys: `grid` (required), `units`, `substitutions`, `multipliers` (all optional). Files are read with `yaml.safe_load` and must end in `.yaml`.

```yaml
grid:
  Nodes:                       # table (sheet) name, exact match
    node:                      # PGM component; a list of attribute dicts creates several components from one table
      id:
        auto_id: {key: Number}
      u_rated: Unom
      extra: [ID, Name, {optional_extra: [GUID]}]
  Lines:
    line:
      id: {auto_id: {key: Number}}
      from_node: {auto_id: {table: Nodes, key: {Number: From.Number}}}
      from_status: From.Switch state
      to_status: 1
      i_n: Inom | Inom'
      r0:
        power_grid_model_io.functions.both_zeros_to_nan: {value: R0, other_value: X0}
```
- `id` is required per component; every attribute must be a valid PGM attribute of that component, otherwise `KeyError` lists the valid ones.
- Tables missing from the data, empty tables and sheets without a mapping entry are skipped silently; a misspelled table name yields no components.

## Column Definitions
- `Unom`: column name. `A | B`: first existing column. A number, or a string that parses as float (`inf`), is a constant.
- `auto_id: {key, table, name}`: integer id per unique key. `key` is a column, a list of columns, or `{key_name: column}`. `table` (default: current table) is the id namespace, so `from_node` with `table: Nodes` and the node's own `id` with the same key give the same integer. `name` separates several entities created from one row (internal node, transformer, load).
- `reference: {other_table, query_column, key_column, value_column}` (all four required): value of `value_column` in the `other_table` row whose `key_column` equals this row's `query_column`.
- `extra: [...]`: columns copied to `extra_info` (not PGM arrays). `{optional_extra: [...]}` entries are skipped when the column is absent; plain `extra` columns must exist.
- `<function>: [col_defs]` calls a pandas function over the columns; `<function>: {kwarg: col_def}` calls a PGM-IO function per row.
- `filters: [{<function>: {kwargs}}]`: each function receives the row plus kwargs and returns `True` to keep it; filters combine with AND, and a component without remaining rows is not created.

## Allowed Functions (PGM-IO v2)
Custom functions in YAML mappings were removed in v2.0.0; only allow-listed ones work (anything else raises `ValueError`/`AttributeError`).
- Pandas, called as `name: [col_defs]`: `sum prod multiply(=prod) product min max mean median std var sem count nunique skew kurt kurtosis all any add radd sub subtract rsub mul div divide truediv rtruediv floordiv rfloordiv mod rmod pow rpow`. Binary ones (`divide: [num, den]`) combine the columns pairwise; the others reduce across columns per row.
- PGM-IO, called by full dotted path with parameter names as kwargs:
  - `power_grid_model_io.functions.`: `has_value value_or_default value_or_zero complex_inverse_real_part complex_inverse_imaginary_part get_winding degrees_to_clock is_greater_than both_zeros_to_nan`
  - `power_grid_model_io.functions.filters.`: `exclude_empty exclude_value exclude_all_columns_empty_or_zero include_only_empty` (`exclude_value: {col, value}` keeps rows where `col != value`)
  - `power_grid_model_io.functions.phase_to_phase.`: `relative_no_load_current reactive_power power_wind_speed get_winding_from get_winding_to get_winding_1 get_winding_2 get_winding_3 get_clock get_clock_12 get_clock_13 reactive_power_to_susceptance pvs_power_adjustment`
- Migrating a v1 mapping with a custom function: use a pandas equivalent, else a built-in function, else request it upstream.

## Units, Substitutions, Multipliers
All three apply whenever a column is read by name (also inside function arguments), not to constants or function results.
- `units`: `{si_unit: {header_unit: factor_to_si}}`, `null` for units that need no conversion. They act only on columns that carry a unit header (two-level `(name, unit)` columns, as from `VisionExcelFileStore`). A column unit missing from `units` raises `KeyError: Unknown unit`.
  ```yaml
  units:
    W: {kW: 1_000.0, MW: 1_000_000.0}
    A: null
  ```
- `substitutions` and `multipliers` match the column by key `<table>.<column>` first, then `<column>`; exact match first, then regex `fullmatch`.
- `substitutions`: `{column_regex: {source_value: target_value}}`. Every value in a matched column needs an entry, otherwise `KeyError: Unknown substitution`. Quote YAML 1.1 booleans (`"off"`, `"on"`, `"yes"`, `"no"`).
  ```yaml
  substitutions:
    ".*Switch state": {"off": 0, "in": 1, "on": 1}
  ```
- `multipliers`: `{column_regex: factor}`, applied after units and substitutions, e.g. `.+_percent: 0.01`, `.+_k(a|v|w): 1_000.0`.

## IDs and Cross-Reference
`AutoID` (`power_grid_model_io.utils.auto_id`) hands out sequential integers from 0 per unique key, shared across all tables (`AutoID()(item=None, key=None)`; `auto_id[i]` returns the stored item). `TabularConverter` (and `VisionExcelConverter`) expose it as:
- `get_id(table, key: dict, name=None)` -> int; `KeyError` if never generated. `get_ids(keys_dataframe, table=None, name=None)` -> list of ints.
- `lookup_id(pgm_id)` -> `{"table", "name"?, "key"}`; `lookup_ids(ids)` -> DataFrame.
- `extra_info[id]["id_reference"]` holds the same reference.

Set `log_level=logging.DEBUG` on the converter to trace mapping steps.

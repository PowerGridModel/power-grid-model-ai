<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM-IO Tabular Mapping Reference

## Mapping File Sections
A tabular mapping file (YAML) typically includes:
- `grid`: source tables to PGM components and fields
- `units`: non-SI to SI conversions
- `substitutions`: categorical value replacement
- `multipliers`: optional regex-based column multipliers

## Grid Section Essentials
Pattern:
- table name -> component name -> component field mapping

Examples:
- direct column mapping: `u_rated: Unom`
- constant assignment: `from_status: 1`
- fallback column: `p_specified: Inverter.Pnom | Inverter.Snom`

## Supported Field Definition Types
- Direct column name string
- First-existing expression with `|`
- Constant value
- `auto_id` references
- `reference` lookup against another table
- Built-in function call mapping (custom functions are not supported, see below)
- Nested function definitions

## AutoID Model
`AutoID` maps external identifiers to integer IDs used by PGM.
Common use:
- generate `id`
- map `from_node`, `to_node`, `node` references

Key ideas:
- Keys are scoped by table/name/key definition.
- Repeated keys map to same generated integer.
- `name` can disambiguate multiple generated IDs per row.

## Advanced AutoID Cases
Use `name` when one source row creates multiple PGM entities (for example internal node + transformer + load).

## Units
PGM expects SI units.
If source uses units in headers (for example with MultiIndex columns), define conversion factors under `units`.

## Substitutions
Use regex-based or exact attribute mapping to replace categorical source values.

Example intent:
- switch states `off/in/on` -> `0/1/1`

## Table Filters
Use filter functions in mapping to include/exclude rows per component generation.
This is key for optional component creation from shared source tables.

## Allowed Functions (PGM-IO v2)
Support for custom functions in YAML mappings was removed in PGM-IO v2.0.0. Allowed:
- common non-mutating `pandas.DataFrame` member functions (for example `divide`)
- functions in `power_grid_model_io.functions`, `power_grid_model_io.functions.filters` (for example `include_only_empty`, allowed in YAML as of v2.0.15) and `power_grid_model_io.functions.phase_to_phase`

Migrating a v1 mapping that fails on a custom function:
1. Replace it with an equivalent pandas call where possible.
2. Otherwise use a suitable function from `power_grid_model_io.functions`.
3. Otherwise request it via an issue or PR upstream.

## Security Guidance
- Mapping files are loaded with `yaml.safe_load`.
- No `eval` usage is allowed.
- Functions must be loadable by explicit import path (for example `numpy.max`, not alias shorthand) and be on the allowed list above.
- Treat mapping files as executable configuration with controlled write access.

## Troubleshooting Checklist
1. Confirm all required source tables are present.
2. Verify sheet names exactly match mapping keys.
3. Check units are declared for all non-SI columns.
4. Check substitutions for enum-like text values.
5. Validate AutoID key uniqueness assumptions.
6. Use converter log output at `INFO`/`DEBUG` during mapping development.

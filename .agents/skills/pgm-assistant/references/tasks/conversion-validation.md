<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Conversion Validation

Use this playbook to validate conversion of external datasets (Vision, pandapower, PGM JSON) into PGM datasets before model construction. Converter usage lives in `../pgm-io/`; PGM structural validation and realism screening are in `data-validation.md`.

## Stages

1. Run the converter and handle its failures (below).
2. Check converted data: `input_data` from `load_input_data()`, `update_data` from `load_update_data()`, and `extra_info` kept for traceability.
3. Hand off to `data-validation.md` before long batch studies.

## Converter Failure Modes

The cases below raise; wrap the load call and report the exception with its source record.

- PGM JSON: `PgmJsonConverter` expects the PGM-IO layout; a plain PGM-serialized file (top-level `version`/`type`/`data`) raises `PowerGridSerializationError`. Load such files with `power_grid_model.utils.json_deserialize_from_file(Path(...))`.
- Tabular/Vision (YAML mapping): a missing `grid` mapping, a mapping file that is not `.yaml`, or a mapped column absent from the source table raises `KeyError`/`ValueError` (message names the table and column).
- Pandapower: unsupported features raise `NotImplementedError` (delta loads, storage, impedance, extended ward, DC line) or `RuntimeError` (tap-dependent impedance, tap at star point). This list comes from reading `power_grid_model_io` 2.0.27; pandapower is not installed here, so it was not executed.

## Handoff Recipe

```python
from power_grid_model import CalculationType
from power_grid_model.validation import errors_to_string, validate_input_data

input_data, extra_info = converter.load_input_data()
errors = validate_input_data(input_data, calculation_type=CalculationType.power_flow)
labels = {pgm_id: info["name"] for pgm_id, info in extra_info.items() if "name" in info}
print(errors_to_string(errors, name="input_data", details=True, id_lookup=labels))
```

`extra_info` is keyed by PGM id, so `id_lookup` shows source labels instead of bare ids in the report. Verified with `PgmJsonConverter`; the attributes stored in `extra_info` (here `name`; Vision stores `Name`) differ per converter and mapping.

## Deliverables

- Pass/fail per source dataset, with converter exceptions and source-record context.
- Rejected or defaulted source records with reasons, and corrective actions (mapping fixes, missing parameters, source cleanup).
- Handoff package for PGM validation: `input_data`, optional `update_data`, `extra_info` and an assumptions log.

## Related References

- `references/pgm-io/overview-and-converter-selection.md`
- `references/pgm-io/vision-conversion-guide.md`
- `references/pgm-io/pandapower-conversion-guide.md`
- `references/tasks/data-validation.md`
- `references/tasks/engineering-plausibility-and-realism.md`

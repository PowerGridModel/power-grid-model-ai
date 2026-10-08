<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Conversion Validation

## Purpose

Use this playbook when the primary task is validating conversion/parsing from external datasets into PGM-compatible datasets before model construction and calculation runs.

## Scope

This playbook covers conversion-side checks only:

- Source parsing and mapping assumptions.
- Identifier continuity and optional vs required field handling.
- Converter-specific caveats and unsupported feature handling.
- Converted dataset type/schema consistency before model construction.

Out of scope:

- PGM structural validation via `validate_input_data` / `validate_batch_data`.
- Engineering realism screening driven by `validation-rules.yml`.

## Conversion Validation Stages

1. Source parsing and mapping validation (PGM-IO converter level).
2. Converted dataset integrity checks (required attributes, IDs, dataset types).
3. Handoff to PGM structural validation and realism screening.

## Conversion-Specific Validation Checkpoints

- Vision: mapping language, sheet coverage, GUID handling, optional vs required fields.
- Pandapower: required electrical parameters, unsupported features, roundtrip consistency.
- PGM JSON: dataset type and schema consistency before model construction.

After conversion checks, run `data-validation.md` (PGM structural + batch validation) and then realism checks from `validation-rules.yml` before long batch studies.

## Typical Conversion Deliverables

- Conversion status (pass/fail) per source dataset.
- Converter warnings/errors with source-record context.
- Rejected or defaulted source records with reasons.
- Corrective-action proposals (mapping fixes, missing parameter completion, source cleanup).
- Handoff package for PGM validation (`input_data`, optional `update_data`, and assumptions log).

## Related References

- `references/pgm-io/overview-and-converter-selection.md`
- `references/pgm-io/vision-conversion-guide.md`
- `references/pgm-io/pandapower-conversion-guide.md`
- `references/pgm-io/pgm-json-and-data-stores.md`
- `references/tasks/data-validation.md`
- `references/tasks/engineering-plausibility-and-realism.md`

<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Power Grid Analysis References

This folder is the fast lookup layer for application development with:

- `power-grid-model` (PGM): core calculations
- `power-grid-model-ds` (PGM-DS): modeling, graph, mutations, visualization
- `power-grid-model-io` (PGM-IO): conversion between external formats and PGM datasets

Use this index first, then jump to a focused file.

## Folder Map

- `references/tasks`: task playbooks (application build, validation, result explanation)
- `references/pgm`: calculation engine API, calculation recipes, validation, serialization, troubleshooting
- `references/pgm-ds`: grid objects, arrays, graph analysis, mutation workflows, interface to PGM
- `references/pgm-io`: converter selection, mapping model, Vision/Pandapower guides, data stores

## Fast Selection Guide

1. If your input is already native PGM JSON or close to PGM arrays: start with `references/pgm-io/pgm-json-and-data-stores.md`, then use `references/pgm/overview-and-entrypoints.md`.
2. If your input is Vision export: start with `references/pgm-io/vision-conversion-guide.md`.
3. If your input is Pandapower net: start with `references/pgm-io/pandapower-conversion-guide.md`.
4. If you need conversion-side validation before PGM model construction: start with `references/tasks/conversion-validation.md`.
5. If you need topology analysis, feeder operations, or branch orientation logic: start with `references/pgm-ds/graph-and-topology-recipes.md`.
6. If you need calculation method choices and options: start with `references/pgm/calculation-recipes.md`.
7. If you need result summaries, plots, or explanation narratives: start with `references/tasks/result-evaluation-and-explanation.md`.
8. If you need PGM-format data validation before or after running calculations: start with `references/tasks/data-validation.md`.
9. If you need realistic-value checks (possible in math, unlikely in operations): start with `references/tasks/engineering-plausibility-and-realism.md` and configure thresholds in `references/tasks/validation-rules.yml`.
10. If you are building or extending a PGM-based workflow/application: start with `references/tasks/application-build-and-automation.md`.
11. If batch runs fail or give partial results: start with `references/pgm/errors-and-debugging.md`.

## Recommended End-to-End Workflow

1. Convert/deserialize input to PGM-compatible datasets (PGM-IO).

2. Validate conversion assumptions and converter output when conversion is involved (`references/tasks/conversion-validation.md`).

3. Validate input/update datasets (`references/tasks/data-validation.md`).

4. Run realism checks (`references/tasks/engineering-plausibility-and-realism.md`).

5. Build or mutate grid representation (PGM-DS Grid where useful).

6. Run calculations (PGM directly or via PGM-DS interface).

7. Evaluate/explain outputs (`references/tasks/result-evaluation-and-explanation.md`).

8. Push outputs back to Grid/converter formats when needed.

## Dependency Guardrails

- Prefer only: PGM, PGM-DS, PGM-IO, numpy, pandas, matplotlib, seaborn.
- Prefer numpy over pandas when straightforward.
- Use PGM-DS graph utilities instead of external graph libraries.

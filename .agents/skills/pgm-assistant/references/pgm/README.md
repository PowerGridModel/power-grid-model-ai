<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Reference Index

Use this folder when you need core calculation-engine behavior.

## Files

- `overview-and-entrypoints.md`: imports, lifecycle, key APIs, defaults
- `data-model-components-and-datasets.md`: component hierarchy, dataset structures, attribute semantics, and modeling constraints
- `calculation-recipes.md`: power flow, state estimation, short circuit run patterns
- `batch-validation-serialization.md`: batch structures, validation APIs, serialization tools
- `errors-and-debugging.md`: common failures, exception patterns, troubleshooting

## Quick Routing

- Need method/options quickly -> `overview-and-entrypoints.md`
- Need full meaning of component/attribute data -> `data-model-components-and-datasets.md`
- Need runnable patterns -> `calculation-recipes.md`
- Need batch or persistence -> `batch-validation-serialization.md`
- Need failure triage -> `errors-and-debugging.md`
- Need task-level validation workflow -> `../tasks/data-validation.md`
- Need task-level result explanation workflow -> `../tasks/result-evaluation-and-explanation.md`

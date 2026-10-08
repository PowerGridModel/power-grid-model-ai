<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Task Playbooks Index

Use this folder when the user request is task-oriented (for example "build a workflow", "validate this dataset", "explain these outputs").

## Files

- `application-build-and-automation.md`: build or extend tooling/workflows using PGM, PGM-DS, and PGM-IO
- `conversion-validation.md`: converter-side validation workflow before PGM structural checks
- `data-validation.md`: PGM-format validation workflow, realism checks, and failure triage
- `result-evaluation-and-explanation.md`: summarize outputs, detect violations, and explain outcomes
- `engineering-plausibility-and-realism.md`: detect unrealistic-but-solvable values and combinations with confidence tags
- `validation-rules.yml`: configurable heuristic thresholds/rules for realism screening after PGM structural validation

## Quick Routing

- Need to implement or extend an application pipeline -> `application-build-and-automation.md`
- Need converter-side validation before PGM model construction -> `conversion-validation.md`
- Need to validate PGM-format data quality before/after calculations -> `data-validation.md`
- Need to explain and present calculation results -> `result-evaluation-and-explanation.md`
- Need realistic-value and engineering plausibility checks -> `engineering-plausibility-and-realism.md`
- Need configurable thresholds/rules -> `validation-rules.yml`

## Related Layer References

- Core calculations: `references/pgm/README.md`
- App-layer grid and topology: `references/pgm-ds/README.md`
- Converters and mappings: `references/pgm-io/README.md`

<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Data Validation

Use this playbook to validate input/update datasets before calculation and output plausibility after it. It starts after the data is in PGM format; for conversion-side checks use `conversion-validation.md`.

Two layers:

- Structural validity: decided by the PGM validators (`validate_*` / `assert_valid_*`; signatures, return values and gotchas in `../pgm/batch-validation-serialization.md`).
- Engineering plausibility: heuristic checks for data that solves but is unrealistic (`engineering-plausibility-and-realism.md`).

## Validation Stages

1. Input structural validation: `validate_input_data` / `assert_valid_input_data`.
2. Batch update validation: `validate_batch_data` / `assert_valid_batch_data`. For batch workflows this is the final structural gate.
3. Input realism screening (YAML rules with `stage: input`).
4. Update realism screening (`stage: update`): scenario deltas and topology state transitions.
5. Post-run realism screening (`stage: output`): after each calculation pass.

Report structural findings only from stages 1-2 and heuristic findings only from stages 3-5. Do not re-implement structural checks as YAML rules. Calculation-time failures that the validators cannot see (`ConflictVoltage`, observability) are triaged with `../pgm/errors-and-debugging.md`.

## Rule Configuration File

`.agents/skills/pgm-assistant/references/tasks/validation-rules.yml` is the single rule and threshold catalog; also use it for result evaluation.

- Each rule has `id`, `enabled`, `check_class` (always `heuristic`), `confidence` (`high`/`medium`/`low`), `severity`, `stage` (list drawn from `input`/`update`/`output`; some rules span several), `target` (component or topic group such as `line` or `sensors`), `description`, optional `thresholds` (references into `profiles`) and `recommended_action`.
- Profiles: `default`, `distribution_mv`, `distribution_hv`, `transmission`. Non-default profiles override thresholds of `default` (`threshold_overrides`). Report the profile used.
- When local operating practice is unclear, keep the finding and lower its confidence instead of rejecting the data.

## Plausibility-Driven Failures

- State estimation over-constrained by unrealistically tiny sigma, or under-informative with very large sigma.
- Topology anomalies that produce mass islanding.

## Deliverables

- Pass/fail per stage, with `errors_to_string(errors, name=..., details=True)` as the human-readable structural summary.
- Rejected records/scenarios with reasons, and corrective actions (parameter completion, id alignment, measurement improvements).
- Findings using the template in `engineering-plausibility-and-realism.md`. For a structural finding set `source: pgm_validator`, `component_type` = `err.component`, `component_id` = `err.ids`, `message` = `str(err)`.
- Active profile.

## Related References

- `references/pgm/batch-validation-serialization.md`
- `references/pgm/errors-and-debugging.md`
- `references/tasks/engineering-plausibility-and-realism.md`
- `references/tasks/validation-rules.yml`
- `references/tasks/conversion-validation.md`

<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Data Validation

## Purpose

Use this playbook when the primary task is validating input/update datasets before running calculations, or validating output plausibility after calculation.

This playbook starts after data is already in PGM format. For conversion-side checks (Vision/Pandapower/PGM JSON mapping), use `conversion-validation.md`.

This guide explicitly covers two layers:

- Structural validity (what PGM can validate directly).
- Engineering plausibility (what may be mathematically solvable but unrealistic in practice).

## Validation Classes and Confidence

Every finding should include:

- `check_class`: `heuristic` for realism checks from YAML.
- `confidence`: `high`, `medium`, or `low`.

Interpretation:

- `heuristic` + `high`: strongly suspicious in most practical grids.
- `heuristic` + `medium`: often suspicious but context-dependent.
- `heuristic` + `low`: context-dependent warning; request domain context before rejecting data.

Structural/concrete violations should come from PGM validator APIs in stages 1 and 2.

## Rule Configuration File

Use `.agents/skills/pgm-assistant/references/tasks/validation-rules.yml` as the configurable rule catalog.

This file contains:

- Tunable thresholds (voltage, loading, tap behavior, sigma ranges, sequence ratios, and more).
- Rule metadata (`id`, `stage`, `check_class`, `confidence`, `severity`, `target`).
- Suggested actions for each rule.

When uncertain about local operating practices, keep the finding but downgrade confidence rather than hard-failing.

What this file intentionally excludes:

- Structural checks already handled by `validate_input_data` / `validate_batch_data` and assert variants.
- Schema/reference rules that are already first-class validator output.

## Validation Stages

1. Input structural validation (PGM): `validate_input_data` / `assert_valid_input_data`.
2. Batch update validation (PGM): `validate_batch_data` / `assert_valid_batch_data`.
3. Input realism screening: parameter realism and cross-attribute consistency.
4. Update realism screening: scenario-step changes and system-wide pattern anomalies.
5. Post-run realism screening: physically implausible outcomes and weak-information conditions.

## Input Realism Screening (Examples)

Use `heuristic` checks with confidence where needed:

- Cable/line values that are possible but suspicious in context (for example very high `r1`/`x1`).
- Transformer voltage levels/ratios that are unrealistic for expected grid level.
- Transformer tap regulator settings that are operationally odd (`u_set`, `u_band`, control side).
- Weird winding/clock combinations.
- Weird tap settings (`tap_min`, `tap_max`, `tap_pos`, `tap_nom`, `tap_size`).
- Weird off-nominal settings (`k`, `theta`) for `generic_branch`.
- Asymmetric line matrix values that are numerically valid but physically doubtful.
- Source parameters (`sk`, `rx_ratio`, `z01_ratio`) inconsistent with expected TSO/DSO coupling.
- Zero-sequence values with implausible relation to positive-sequence values.
- Sensor sigma values too low (numerical dominance) or too high (near-zero information value).
- Load/gen combinations with odd power-factor or phase-imbalance patterns.
- Shunt conductance/susceptance mixes that suggest mis-modeled equipment type.

## Update Realism Screening (Examples)

- Mass de-energization in one scenario step.
- Large fractions of status flips in one update.
- Large tap jumps between neighboring scenarios.
- Abrupt bulk load/generation changes without known event context.

## Output Realism Screening (Examples)

- Mass de-energized islands and likely causes.
- Extreme low/high voltages, currents, and loading values.
- Source burdening or aggregate injections inconsistent with practical operation.
- State estimation residual patterns indicating unrealistic sensor trust setup.
- Net losses that are implausibly high relative to served load.

## YAML-First Rule Routing

After stages 1 and 2 (PGM structural validation), run YAML rules by stage:

- `input` rules against normalized `input_data`.
- `update` rules against scenario deltas and topology state transitions.
- `output` rules after each calculation pass.

Use the same YAML for result-evaluation to avoid duplicated threshold logic.

## Core Validation APIs

```python
from power_grid_model import CalculationType
from power_grid_model.validation import (
    assert_valid_batch_data,
    assert_valid_input_data,
    errors_to_string,
    validate_batch_data,
    validate_input_data,
)

input_errors = validate_input_data(
    input_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)

batch_errors = validate_batch_data(
    input_data,
    update_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)

assert_valid_input_data(
    input_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)

assert_valid_batch_data(
    input_data,
    update_data,
    calculation_type=CalculationType.power_flow,
    symmetric=True,
)

print(errors_to_string(batch_errors, name="update_data", details=True))
```

## Important Nuance for Batch Work

- Base input can be incomplete when every missing value is overwritten by every batch scenario.
- In this case, `validate_input_data` may fail while `validate_batch_data` succeeds.
- For batch-heavy workflows, treat batch validation as the final gate.

## Scope Boundary

- This task only covers PGM-format validation and realism screening.
- For conversion-side validation (source parsing, mapping assumptions, and converter caveats), use `conversion-validation.md`.

## Failure Triage

- `IDNotFound`: update IDs do not exist in base input.
- `ConflictVoltage`: inconsistent rated voltages across connected topology.
- `NotObservableError` or `SparseMatrixError`: insufficient or dependent measurements in state estimation.
- `MaxIterationReached` or `IterationDiverge`: likely data-quality issue, unsuitable method, or poor initialization.

Also triage plausibility-driven failures:

- Over-constrained state estimation due to unrealistic tiny sigma.
- Under-informative state estimation due to very large sigma.
- Topology-side anomalies producing mass islanding.

## Validation Deliverables

- Validation status (pass/fail) per dataset stage.
- Human-readable error summary (`errors_to_string`).
- Rejected records/scenarios with reasons.
- Corrective-action proposals (parameter completion, ID alignment fixes, measurement improvements).
- Finding list with `check_class` and `confidence` for each issue.
- Active profile and threshold source (`default`/`distribution_mv`/`distribution_hv`/`transmission`).

## Recommended Finding Schema

- `id`
- `check_class`
- `confidence`
- `severity`
- `stage`
- `component_type`
- `component_id`
- `message`
- `evidence`
- `recommended_action`

## Related References

- `references/pgm/batch-validation-serialization.md`
- `references/pgm/errors-and-debugging.md`
- `references/tasks/engineering-plausibility-and-realism.md`
- `references/tasks/validation-rules.yml`
- `references/tasks/conversion-validation.md`

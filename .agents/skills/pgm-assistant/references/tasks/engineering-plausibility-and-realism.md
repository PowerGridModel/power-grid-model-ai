<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Engineering Plausibility and Realism Screening

## Purpose

Use this playbook when you need to catch values and combinations that are mathematically solvable but operationally unrealistic.

This layer complements (not replaces) PGM structural validation.

Structural/concrete checks should be reported from `validate_input_data` and `validate_batch_data` outputs, not duplicated in YAML realism checks.

## Validation Classes and Confidence

Use two explicit classes for every finding:

- `heuristic`: context-dependent plausibility checks based on typical grid practice.
  - Typical confidence: `medium` or `low`.

Confidence meaning:

- `high`: highly suspicious across most practical grids.
- `medium`: often suspicious, but could be valid in specific contexts.
- `low`: weak prior; requires project context confirmation.

## Scope by Stage

### Input stage (before model construction)

Focus on physically meaningful parameterization:

- Extreme cable/branch impedance values.
- Implausible transformer voltage levels and ratios.
- Weird winding and clock combinations.
- Weird tap settings (`tap_min`, `tap_max`, `tap_pos`, `tap_size`, `tap_nom`).
- Unrealistic off-nominal ratio `k` and phase shift `theta` for `generic_branch`.
- Source parameters (`sk`, `rx_ratio`, `z01_ratio`) inconsistent with expected grid connection strength.
- Zero-sequence values inconsistent with positive-sequence values.
- Asymmetric line matrix values that are numerically possible but physically odd.
- Sensor sigma values too small (numerical risk) or too large (low information value).

### Update stage (scenario changes)

Focus on operational continuity and switching realism:

- Sudden mass de-energization and widespread status flips.
- Large tap jumps between neighboring scenarios.
- Large load or generation step changes without known event markers.
- Widespread regulator setpoint shifts (`u_set`, `u_band`) beyond operational norms.

### Output stage (post-calculation)

Focus on outcome realism and anomaly explanation:

- Mass de-energized islands and likely causes.
- Extreme voltage/current/loading values by absolute and relative criteria.
- Implausible aggregate net injections or source burdening.
- State estimation residual patterns indicating untrusted measurements.
- Results that satisfy equations but violate expected grid operating behavior.

## Recommended Workflow

1. Run PGM structural validation first.
2. Run realism checks using `.agents/skills/pgm-assistant/references/tasks/validation-rules.yml`.
3. Tag findings as `heuristic` with confidence (`high`, `medium`, `low`).
4. Report both component-level findings and system-level findings.
5. Provide likely causes and targeted corrective actions.

## Finding Record Template

Use this schema in reports:

- `id`: unique rule ID.
- `source`: `pgm_validator` or `yaml_realism`.
- `check_class`: use `heuristic` for YAML findings.
- `confidence`: `high`/`medium`/`low`.
- `severity`: `error`/`warning`/`info`.
- `stage`: `input`/`update`/`output`.
- `component_type`: for example `line`, `transformer`, `source`, `sym_load`.
- `component_id`: affected ID if applicable.
- `message`: concise issue statement.
- `evidence`: key values and thresholds.
- `recommended_action`: what to fix or verify next.

## Practical Notes

- Do not auto-reject all `heuristic` findings; present them as review-required.
- Keep profile-specific thresholds (distribution vs transmission) in YAML, not hard-coded in prose.
- If context is missing, lower confidence rather than over-asserting.

## Related References

- `.agents/skills/pgm-assistant/references/tasks/data-validation.md`
- `.agents/skills/pgm-assistant/references/tasks/result-evaluation-and-explanation.md`
- `.agents/skills/pgm-assistant/references/tasks/validation-rules.yml`
- `.agents/skills/pgm-assistant/references/pgm/data-model-components-and-datasets.md`

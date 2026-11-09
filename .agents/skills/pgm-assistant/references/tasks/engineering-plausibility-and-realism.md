<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Engineering Plausibility and Realism Screening

Realism screening catches data and results that PGM solves but that are operationally implausible. It complements PGM structural validation (`validate_input_data` / `validate_batch_data`); never re-implement structural checks as realism rules.

`validation-rules.yml` is the single source of truth for rules (`id`, `stage`, `target`, `confidence`, `severity`, `recommended_action`), thresholds, profiles (`default`, `distribution_mv`, `distribution_hv`, `transmission`), confidence meanings and required report fields. Do not copy numeric thresholds into prose or code.

## Workflow

1. Run PGM structural validation first; report its findings with `source=pgm_validator`.
2. Resolve the active profile (below) and run the YAML rules for the relevant `stage` (`input`, `update`, `output`).
3. Report YAML findings with `source=yaml_realism`, `check_class=heuristic` and the rule's `confidence`; when local context is missing, lower confidence instead of over-asserting.
4. Report component-level and system-level findings with likely cause and corrective action.
5. Present heuristic findings as review-required; do not auto-reject data.

## Resolving Thresholds

```python
import copy, yaml

cfg = yaml.safe_load(open(".agents/skills/pgm-assistant/references/tasks/validation-rules.yml"))

def thresholds(profile="default"):
    t = copy.deepcopy(cfg["profiles"]["default"]["thresholds"])
    for group, values in cfg["profiles"][profile].get("threshold_overrides", {}).items():
        t[group].update(values)
    return t
```

A rule's `thresholds` values are paths into the default profile; read the effective value from `thresholds(profile)`.

## PGM Gotchas for Rule Implementation

- Units are SI (V, A, W, var, VA, ohm). Per-unit thresholds need conversion: `u_pu` is an output attribute, but `transformer_tap_regulator.u_set`/`u_band` (V) and `tap_size` (V) must be divided by the relevant `u_rated`/tap-side voltage.
- Asymmetric line matrices are lower-triangular by construction (`r_ba`, `r_ca`, `r_cb`, ...), so they cannot be non-reciprocal.
- Sensor sigma attributes: `u_sigma`; `p_sigma`/`q_sigma`/`power_sigma`; `i_sigma`/`i_angle_sigma`. Unused ones are NaN; skip NaN before range checks.
- Sensor outputs carry raw residuals (`u_residual`, `p_residual`, `q_residual`, `i_residual`, and `*_angle_residual`), in measurement units. Normalized residual = residual / matching sigma and must be computed by the caller.
- Nodes without a path to a source have `energized == 0` and `u_pu == 0`; mask them before voltage rules and count them for the islanding rule.
- Reference directions: positive `p_specified` of `sym_load`/`asym_load` is consumption, of `sym_gen` and `source` is injection; output `p` follows the same direction per appliance. Branch `p_from`/`p_to` are positive into the branch, so `p_from + p_to` is the branch loss.
- `loading` is defined for branches only (line, transformer, link, generic_branch, and three-winding transformer where it is the maximum of `loading_1/2/3`): `max(i_from, i_to) / i_n` for lines, `max(s_from, s_to) / sn` for transformers. Short-circuit outputs contain no `loading`, `p` or `q`.

## Finding Record

Fields are listed in `validation-rules.yml` under `reporting.required_fields`. Values: `source` is `pgm_validator` or `yaml_realism`; `check_class` is `heuristic` for YAML findings; `severity` is `error`/`warning`/`info`; `stage` is `input`/`update`/`output`; `evidence` holds key values and thresholds.

## Related References

- `.agents/skills/pgm-assistant/references/tasks/data-validation.md`
- `.agents/skills/pgm-assistant/references/tasks/result-evaluation-and-explanation.md`
- `.agents/skills/pgm-assistant/references/tasks/validation-rules.yml`
- `.agents/skills/pgm-assistant/references/pgm/data-model-components-and-datasets.md`

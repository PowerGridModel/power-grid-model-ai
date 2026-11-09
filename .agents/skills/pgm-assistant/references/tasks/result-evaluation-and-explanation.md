<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Result Evaluation and Explanation

Use this playbook to evaluate, summarize, visualize and explain PGM outputs (`calculate_power_flow`, `calculate_state_estimation`, `calculate_short_circuit`), for a single run or a batch. Limit checks and realism screening belong in the same report. Rule semantics, units, reference directions and `energized` handling are in `engineering-plausibility-and-realism.md`; thresholds come only from `validation-rules.yml`.

## Workflow

1. Establish the scenario index (plain scenario ID, time index or custom grouping) and state whether scenarios are chronological.
2. Select the output components/attributes for the user goal; resolve the threshold profile (state which one).
3. Compute KPIs, limit violations and the output-stage realism rules (`stage: output`).
4. Add at least one non-plot analytic (persistence, ranking, trend, anomaly explanation).
5. Build the summary tables and the plots that answer the user's question.
6. Interpret with assumptions and confidence.

## Output Shapes and Recipes

Batch outputs have shape `(n_scenarios, n_components)`; asymmetric outputs add a trailing phase axis for node/appliance/branch quantities (`u_pu`, `p`, `i_from`) while branch `loading` stays one value per branch. Short-circuit outputs have no `loading`, `p` or `q`.

```python
import numpy as np
from power_grid_model import ComponentType as C

th = thresholds("distribution_mv")  # helper in engineering-plausibility-and-realism.md

node, line = out[C.node], out[C.line]
u = np.where(node["energized"] == 1, node["u_pu"], np.nan)
under_frac = np.nanmean(u < th["voltage"]["u_pu_low_warn"], axis=0)   # per node, over scenarios
overload_frac = (line["loading"] > th["loading"]["branch_warn"]).mean(axis=0)

# branch losses; sum p_from + p_to over every branch type present in `out`
loss = sum((out[c]["p_from"] + out[c]["p_to"]).sum(axis=-1) for c in (C.line, C.transformer) if c in out)
loss_ratio = loss / np.abs(out[C.sym_load]["p"].sum(axis=-1))

# state estimation: normalized residual = residual / sigma from the input data
z_p = np.abs(out[C.sym_power_sensor]["p_residual"]) / input_data[C.sym_power_sensor]["p_sigma"]
```

## Minimum Deliverables

- Scope and index context (scenario-only, time-indexed, or custom-indexed).
- Method assumptions: `symmetric`/`asymmetric`, algorithm, tolerance, and the threshold profile used.
- Key values (voltages, branch flows, loading extremes) and explicit violations (where and by how much) or confirmation of none.
- Realism findings tagged `source` and `confidence`; structural issues carried over from earlier stages use `source=pgm_validator`.
- At least one non-plot analytic and the interpretation with likely drivers, confidence caveats and next checks.
- Plots only when requested or when they answer a question.

## Plots

- Topology-sorted node profile (`u_pu`, `u_angle` vs node order grouped by feeder, ordered by graph distance from the source): spatial voltage quality. Meshed grids have no unique order; use shortest-path distance and state it.
- Histogram/KDE of `u_pu`, loading, current: spread and outliers.
- Ranked bar chart of worst components: prioritization.
- Heatmap (component x scenario): persistence and clustering.
- Duration curve: exceedance severity vs duration.
- Time-series lines (time-indexed): trends, ramps, regulator behavior; add rolling statistics and exceedance markers.
- Scatter (`u` vs `p`, loading vs voltage): stress relations.
- Without a time index, use distributions, ranking and heatmaps; for a categorical index (season, feeder class, operating mode) facet or group by category.
- Put units, thresholds and profile in titles/legends.

The PGM-DS visualizer (`visualize(grid, update_data=..., output_data=...)`) suits topology-first triage and quick tables; use matplotlib/seaborn for explanatory analytics.

## Analytics Beyond Plots

- Violation persistence: fraction of scenarios violating, per component.
- Severity-duration score and critical-component ranking (violations, losses).
- Weak nodes: lowest voltage and highest variance.
- Island impact: de-energized fraction, affected load/generation, likely switch causes.
- Loss-to-load ratio per scenario and its trend; source burden vs served load.
- Regulator behavior: tap movement counts, large jumps, hunting-like oscillation.
- State estimation quality: normalized residual statistics and concentration of bad measurements.
- Time index only: daily/weekly profiles, peak vs off-peak stress, ramps of net load and generation, event windows around switching or tap changes.

## Reporting Fields

Use the finding fields from `validation-rules.yml` (`reporting.required_fields`) and add `scope` (component/system), `index_context`, `impact`.

## Related References

- `references/pgm/calculation-recipes.md`
- `references/pgm/overview-and-entrypoints.md`
- `references/pgm-ds/mutations-serialization-visualizer.md`
- `references/pgm/errors-and-debugging.md`
- `references/tasks/data-validation.md`
- `references/tasks/engineering-plausibility-and-realism.md`
- `references/tasks/validation-rules.yml`

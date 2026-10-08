<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Result Evaluation and Explanation

## Purpose

Use this playbook when the task is to evaluate, summarize, visualize, and explain PGM outputs.

This content is intentionally separated from the main skill contract so result evaluation is one task among many, not the default workflow.

Result evaluation should include both limit violations and realism screening.

## Expected Inputs

- Calculation outputs from PGM (`calculate_power_flow`, `calculate_state_estimation`, `calculate_short_circuit`)
- Scenario context (single run or batch)
- Optional scenario index (most commonly time index for time-series studies)
- Optional threshold definitions (for example voltage bands, loading limits)

## Evaluation Workflow

1. Identify scenario indexing context (plain scenario ID, time index, or custom index).
2. Select relevant output components/attributes for the user goal.
3. Compute KPIs and detect out-of-limit values using YAML profile thresholds.
4. Run realism checks for mathematically possible but operationally unlikely outcomes using YAML rule IDs.
5. Build compact summary tables.
6. Build plot set appropriate to topology and index type.
7. Add analytics beyond plots (ranking, persistence, trends, root-cause hints).
8. Provide narrative interpretation tied to assumptions, method choices, and confidence.

## Minimum Deliverables

- A short summary of key metrics.
- Explicit list of violations or confirmation of none.
- Method assumptions (`symmetric`/`asymmetric`, solver, tolerance).
- If requested, a plot set (for example distribution and top violations).
- Findings tagged by source (`pgm_validator` or `yaml_realism`) and `confidence`.
- Explicit profile used from `validation-rules.yml`.
- Index assumptions (for example whether scenarios are chronological time steps).
- At least one non-plot analytic insight (for example persistence, ranking, trend, or anomaly explanation).

## Realism Screening on Outputs

Screen for patterns that may be calculation-feasible but rarely observed in operations:

- Mass de-energized islands and likely trigger chains.
- Extreme under/over-voltage patterns (`u_pu`).
- Extreme branch loading/current values relative to equipment ratings.
- Aggregate source vs total load/generation imbalance patterns.
- State estimation residual patterns suggesting weak measurement quality settings.

Use rule thresholds from `.agents/skills/pgm-assistant/references/tasks/validation-rules.yml`.

Do not hardcode operational limits in this page; prefer YAML profile values so validation and evaluation remain consistent.

## Summary Structure

1. Scope: what was analyzed and why.
2. Data/index context: scenario-only or time-indexed, and any additional grouping index.
3. Key values: node voltages, branch flows, loading extremes.
4. Violations: where and by how much.
5. Realism findings: what is implausible even if mathematically solved.
6. Plot-guided observations: what patterns are visible in network and index dimensions.
7. Analytics findings: persistent offenders, trend behavior, and likely causes.
8. Interpretation: likely drivers and confidence caveats.
9. Recommended next checks.

## Example Checks

```python
import numpy as np

u_low_warn = active_thresholds["voltage"]["u_pu_low_warn"]
u_high_warn = active_thresholds["voltage"]["u_pu_high_warn"]

u = out[ComponentType.node]["u_pu"]
under = np.where(u < u_low_warn)[0]
over = np.where(u > u_high_warn)[0]

line_loading = out[ComponentType.line]["loading"]
critical = np.where(line_loading > active_thresholds["loading"]["branch_warn"])[0]
```

Add confidence-tagged screening for report output:

- `heuristic/high`: strongly suspicious pattern in outputs.
- `heuristic/medium`: likely operational concern.
- `heuristic/low`: context-dependent anomaly requiring user confirmation.

When structural issues from earlier stages are included in the same report, mark them as `source=pgm_validator`.

## Rule Routing for Output Stage

Evaluate at least these output rule groups from YAML:

- `node` voltage realism.
- `branch_and_branch3` loading realism.
- `energization` and islanding realism.
- `aggregate_power` realism (source burden, loss ratio).
- `state_estimation_residuals` realism.

## Visualization Capability Notes

The built-in PGM-DS visualizer is useful but limited for deep analytics:

- It is strong for topology view (cytoscape graph).
- It can tabulate data quickly.
- It can plot a single ID-attribute across scenarios.

Use it for quick inspection, then switch to matplotlib/seaborn for insight-oriented analysis.

## Plot Selection Guide

Choose plots by question, not by default habit.

- Topology-sorted voltage profile: best for spatial voltage quality and angle consistency.
- Histogram or KDE of `u_pu`, loading, current: best for distribution spread and outliers.
- Ranked bar chart of worst components: best for maintenance/action prioritization.
- Scenario heatmap (`component` x `scenario`): best for persistence and temporal clustering.
- Duration curve (for voltage/loading/current): best for exceedance severity vs duration.
- Time-series line plots (when indexed by time): best for trend, ramps, and control behavior.
- Scatter plots (`u` vs `p`, loading vs voltage): best for relation and stress patterns.

## Topology-Sorted Node Profile (Voltage Magnitude and Angle)

Recommended workflow:

1. Compute feeder grouping and graph distance from source nodes.
2. Build node order using feeder then electrical/topological distance.
3. Plot `u_pu` and `u_angle` against ordered node index.
4. If multiple feeders exist, use one subplot per feeder.

Interpretation targets:

- Steep voltage drop sections.
- Angle discontinuities or unusual gradients.
- Feeder-level structural differences.

Practical note:

- In meshed grids, ordering is not unique; use shortest-path distance plus feeder grouping and state the method in the report.

## Index-Aware Plotting Strategy

Scenario index affects plot design and analytics.

If scenarios are time-indexed (most common):

- Use chronological line plots for `u_pu`, loading, source power, losses.
- Add rolling statistics (moving mean/std) for volatility.
- Add ramp plots (`delta` per step) for load/gen and regulator behavior.
- Add exceedance timelines (when thresholds are violated).

If scenarios are not time-indexed:

- Use distributions, ranked plots, and clustering-style heatmaps.
- Use grouped boxplots if there is a categorical index (for example season, feeder class, operating mode).

If additional indexing is present (for example weather, tariff window, topology state):

- Use faceting/small multiples by index category.
- Compare KPI distributions by category.
- Separate trend interpretation from category effects.

## Analytics Beyond Plots

Add numeric analyses that stand on their own:

- Violation persistence: fraction of scenarios violating per component.
- Severity-duration score: combine exceedance magnitude and duration.
- Critical component ranking: top contributors to violations and losses.
- Weak-node ranking: lowest-voltage and highest-variance nodes.
- Congestion recurrence: branches frequently above warning/severe thresholds.
- Island impact metrics: de-energized fraction, affected load/generation, likely switch causes.
- Loss analytics: loss-to-load ratio by scenario and its trend.
- Source adequacy: source burden vs served load over index progression.
- Regulator behavior: tap movement counts, large jumps, and hunting-like oscillation hints.
- State estimation quality: normalized residual statistics and bad-measurement concentration.

## Time-Series Specific Analytics

When scenario index is time:

- Daily/weekly profiles for voltage, loading, and source output.
- Peak/off-peak comparison for stress metrics.
- Ramping analytics for net load and generator behavior.
- Autocorrelation-style persistence checks for recurring violations.
- Event windows around switching/tap changes to assess impact propagation.

## Visualization Guidance

- Use PGM-DS visualizer for topology-first triage.
- Use matplotlib/seaborn for explanatory plots and multi-series analytics.
- Keep plots decision-oriented: each plot should answer one operational question.
- Include units, thresholds, and profile context directly in titles/legends.

## Reporting Template (Recommended)

For each major finding include:

- `id`
- `source`
- `check_class`
- `confidence`
- `severity`
- `scope` (component/system)
- `index_context` (scenario-only, time-indexed, or custom-indexed)
- `evidence` (value, threshold, scenario)
- `impact`
- `recommended_action`

## Related References

- `references/pgm/calculation-recipes.md`
- `references/pgm/overview-and-entrypoints.md`
- `references/pgm-ds/mutations-serialization-visualizer.md`
- `references/pgm/errors-and-debugging.md`
- `references/tasks/data-validation.md`
- `references/tasks/engineering-plausibility-and-realism.md`
- `references/tasks/validation-rules.yml`

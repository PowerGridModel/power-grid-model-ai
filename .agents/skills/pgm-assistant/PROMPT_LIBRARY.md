<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Power Grid Analysis Prompt Library

Use these prompts to trigger the `pgm-assistant` skill with clear intent.

## How to Use This Library

- Replace placeholders like `<path-to-input.json>` and `<target-file.py>`.
- Keep four details in your prompt: task, data source, expected output, and constraints.
- For best routing, explicitly mention PGM, PGM-DS, and/or PGM-IO when relevant.

## High-Signal Prompts (Best for This Skill)

These are particularly well answered by this skill because they map directly to the skill workflow (conversion -> validation -> calculation -> explanation/debugging).

1. "Build an end-to-end script that converts `<source-format>` data to PGM format, validates it, runs a symmetric power flow, and writes a concise summary report. Use only PGM, PGM-DS, PGM-IO, numpy, pandas, matplotlib, seaborn."
2. "I have `<path-to-input.json>`. Validate the dataset for power flow: first list structural errors from `validate_input_data` / `assert_valid_input_data`, then run engineering plausibility checks using `validation-rules.yml` thresholds. Return a table of findings keyed by component ID, rule ID, confidence level, and suggested fix."
3. "Create a converter selection decision for these inputs: `<format-description>`. Explain why the chosen PGM-IO path is correct and provide a runnable conversion snippet."
4. "Run a batch power flow on `<dataset-path>` with clear handling for partial failures. For failed steps, distinguish between non-finite node voltages, topological disconnection, and pure solver divergence. Return: total pass/fail count, a table of failed scenario indices with likely failure class, and ranked recommended fixes."
5. "Analyze topology from `<dataset-path>` using PGM-DS graph tools only (no external graph libraries). Identify islands, radial/meshed areas, and weakly connected sections."
6. "Debug this abnormal result set from `<results-path>`. Separate input-data issues from solver/configuration issues and propose the minimum change set to retest."
7. "Explain these PGM outputs for an operations audience: `<result-path>`. Include limit violations, loading hotspots, voltage concerns, and a plain-language conclusion."
8. "Compare Newton-Raphson and iterative-current methods for this network `<dataset-path>`. Show assumptions, option changes, and differences in key output metrics."
9. "Design a reusable validation gate for CI that blocks structurally invalid PGM datasets (using `assert_valid_input_data` / `assert_valid_batch_data`) and warns on realism violations using thresholds from `validation-rules.yml`. The gate should return a structured report with rule IDs, confidence levels, and a boolean pass/fail signal suitable for pipeline integration."
10. "Assess whether `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_input_data.json` and `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_update_data.json` define a credible state-estimation study. Summarize sensor coverage by component type, measurement sigma values against `validation-rules.yml` realism thresholds, estimated observability gaps, and the top 3 things to verify first in the estimated outputs."
11. "Validate `<se-input-path>` and `<se-update-path>` for state estimation readiness. Report: (a) structural errors from PGM's SE validator, (b) sensor coverage by component type as a table (voltage sensors, power sensors, current sensors — count and fraction of total components), (c) sigma field realism against `validation-rules.yml` thresholds, and (d) components with no sensor coverage and their observability risk."
12. "Run a batch state estimation on `<se-input-path>` + `<se-update-path>` using `iterative_linear` over all scenarios. Return: (a) a step-level convergence summary table (solved / non-finite / diverged), (b) per-step KPIs — RMS `u_pu`, worst-node voltage, max branch loading, and (c) a flag for any step where the solver returns non-finite estimated values. Use only PGM ecosystem dependencies."
13. "Compare SE output `<se-output-path>` against truth power flow `<truth-pf-path>` over all batch steps. Report: per-node RMSE of `u_pu`, top-10 nodes with the highest absolute error, a time-series plot of mean absolute voltage error across steps, and root-cause hypotheses for persistent high-error nodes."
14. "Analyze measurement residuals from `<se-output-path>`. For each sensor type (`sym_voltage_sensor`, `sym_power_sensor`), compute mean and standard deviation of normalized residuals across all batch steps. Flag sensors whose residuals exceed 3-sigma limits. Identify whether outlier sensors cluster at specific nodes, branches, or time windows."
15. "Rerun the state estimation on `<se-input-path>` + `<se-update-path>` twice: once with `iterative_linear` and once with `newton_raphson`. Compare: step-level convergence rate, mean `u_pu` RMSE against `<truth-pf-path>`, and worst-node voltage error. Conclude when each method is preferred given this network's characteristics."

## Prompt Templates by Task

### 1) Application Build / Workflow Automation

"Create `<target-file.py>` that:
1) loads `<input-path>`,
2) converts/deserializes to PGM-compatible arrays,
3) validates input/update data,
4) runs `<calculation-type>` with `<method/options>`,
5) exports results to `<output-path>` and a short markdown report.
Keep dependencies limited to PGM ecosystem + numpy/pandas/matplotlib/seaborn."

### 2) Conversion and Mapping

"I need to convert `<source-format>` to PGM JSON. Choose the correct PGM-IO converter, show mapping assumptions, and generate a script that logs dropped/altered fields and unit conversions."

"Audit this conversion output `<converted-path>` against source `<source-path>`. Return a mismatch report grouped by criticality (blocking, warning, informational)."

### 3) Validation and Data Quality

"Validate `<dataset-path>` for `<calculation-type>`. Return:
- hard validation failures,
- likely modeling mistakes,
- realism anomalies with confidence labels,
- exact rows/components to fix first."

"Create a validation report function for PGM datasets that outputs JSON + markdown and can be reused in batch pipelines."

### 4) Study Execution (Power Flow / State Estimation / Short Circuit)

"Run `<study-type>` on `<dataset-path>` with justified default options. Then produce a compact KPI table for node voltage, branch loading, and source/generator active-reactive balance."

"Run batch state estimation on `<se-input-path>` + `<se-update-path>` with `<method>` over all scenarios. Return:
1) Step-level convergence summary (solved / non-finite / diverged).
2) KPI table: mean/min/max `u_pu` per step, max branch loading per step.
3) RMSE of estimated `u_pu` vs truth from `<truth-pf-path>` per step.
Use only PGM ecosystem dependencies."

"Generate a parameter sweep for `<option-name>` over `<range>` and show sensitivity of `<metric>` with a chart and short interpretation."

### 5) Result Evaluation and Explanation

"Given `<results-path>`, produce an engineering summary with:
- top 10 overloaded elements,
- top 10 voltage deviations,
- probable root causes,
- mitigation actions ranked by impact and implementation risk."

"Translate these study results into two outputs: a technical appendix and an operator-facing summary with less jargon."

### 6) State Estimation Workflows

"Audit `<se-input-path>` for state estimation sensor coverage. Produce a table with columns: component type, total count, sensors attached, coverage fraction. Flag component types below 50% sensor coverage as observability risks. Add a summary row for the whole network."

"Compare SE output `<se-output-path>` to truth `<truth-pf-path>`. For each node, compute RMSE of `u_pu` across all batch steps. Rank nodes by RMSE, plot a histogram of RMSE values, and for the top 5 worst nodes trace back to sensor placement and sigma configuration to explain likely estimation error sources."

"Evaluate measurement residual quality from `<se-output-path>`. For `sym_voltage_sensor` and `sym_power_sensor` outputs, compute normalized residual distributions. Check whether residuals are approximately unit-normal (i.e., well-calibrated measurement noise). Flag sensors or time windows with systematic bias or heavy tails."

"Debug state estimation non-convergence on `<se-input-path>` + `<se-update-path>`. Identify the batch steps that fail, check for topology changes or extreme load swings in the corresponding update rows, and propose the minimum data corrections to restore solver convergence."

### 7) Debugging and Failure Triage

"This calculation fails with `<error-message>`. Build a triage flow: data issue vs topology issue vs method/options issue, then produce a smallest-first remediation plan."

"I suspect bad topology after conversion. Use PGM-DS graph checks to find disconnected components, invalid orientations, or suspicious feeder splits. Provide reproducible checks in code."

## Ready-to-Use Prompts for This Repository

1. "Validate `data/synthetic_pgm_data_20260531T143646Z/synthetic_input_data.json` for power flow and generate a markdown findings report under `data/synthetic_pgm_data_20260531T143646Z/validation_report.md`."
2. "Use `tests/data/_generate_synthetic_pgm_data.py` as a baseline. Refactor it into reusable functions for generate-input, run-study, and export-results without changing behavior."
3. "Read `data/synthetic_pgm_data_20260531T143646Z/synthetic_power_flow_output_data.json` and produce a concise interpretation of voltage profile, branch loading, losses, and source reactive power behavior."
4. "Assess `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_input_data.json`, `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_update_data.json`, and `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_output_data.json` for state-estimation readiness and result quality over the 192-step batch."
5. "Validate `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_input_data.json` for state estimation. Report sensor coverage by component type, sigma value realism against `validation-rules.yml` thresholds, and any structural errors from PGM's SE validator. Save findings as a markdown report."
6. "Run batch state estimation on `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_input_data.json` + `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_update_data.json` using `iterative_linear`. Return: step-level convergence flags, per-step voltage KPI table, and the worst 5 nodes by mean absolute `u_pu` estimation error vs `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_truth_power_flow_output_data.json`."
7. "Compare SE output `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_state_estimation_output_data.json` to truth `data/synthetic_state_estimation_data_20260531T143924Z/synthetic_truth_power_flow_output_data.json`. Compute per-node RMSE of `u_pu` over 192 steps, plot a time-series of mean absolute voltage error, identify the top 10 worst-estimated nodes, and explain probable causes linked to sensor placement and sigma configuration."

## Prompt Quality Upgrades

Weak prompt:

"Run power flow and explain it."

Stronger prompt:

"Run symmetric power flow on `<dataset-path>` using Newton-Raphson. Return: validation findings, solver settings, top violations, and a short operator summary. Use only PGM ecosystem dependencies."

Weak prompt:

"Fix this grid issue."

Stronger prompt:

"Debug `<error-or-symptom>` on `<dataset-path>`. Distinguish conversion errors, structural validation errors, and solver instability. Provide ranked fixes and a minimal reproduction script."

Weak prompt:

"Run state estimation and check results."

Stronger prompt:

"Run batch state estimation on `<se-input-path>` + `<se-update-path>` using `iterative_linear` over all 192 steps. For each step: flag non-convergence, compute RMSE of `u_pu` against `<truth-pf-path>`, and report worst-10 nodes by absolute voltage error. Summarize sensor coverage and sigma configuration as a plausibility preamble. Use only PGM ecosystem dependencies."

## Checklist for Writing New Prompts

- Name the task type (convert, validate, calculate, explain, debug).
- Include exact input and output locations.
- Specify required deliverable format (code patch, report, table, chart, tests).
- Add constraints (allowed libraries, method choice, performance bounds).
- Ask for assumptions and confidence tags when uncertainty is expected.
---
# SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

name: pgm-assistant
description: "Use when: working on any power-grid-model ecosystem task, including app building, data conversion, validation, grid calculations, result explanation, and debugging. This skill covers the full range of operations across the `power-grid-model` ecosystem, including core calculations (PGM), graph/topology operations and visualizer workflows (PGM-DS), and data format conversions (PGM-IO)."
---

# Power Grid Model Ecosystem Operations

## Package Version Status
Last reviewed: PGM v1.13.122 · PGM-DS v1.10.2 · PGM-IO v1.3.104 (checked 2026-07-20)

This skill is for operations across the full `power-grid-model` ecosystem. The repositories are tools; the user request defines the task.

Prompt starters are available in `PROMPT_LIBRARY.md`.

## Ecosystem Tool Roles
- `power-grid-model` (PGM): core calculations and validation APIs.
- `power-grid-model-ds` (PGM-DS): application-layer grid objects, graph/topology operations, mutations, and visualizer workflows.
- `power-grid-model-io` (PGM-IO): conversion between external formats and PGM-compatible datasets.

## Dependency Rules

| Constraint Category | Rule Details |
| --- | --- |
| **Reference Documents** | Start with `references/README.md`, then route to task guides in `references/tasks` and layer guides in `references/pgm`, `references/pgm-ds`, `references/pgm-io`. `REFERENCES.md` is kept as a backward-compatible landing page. |
| **Allowed Libraries** | You are strictly constrained to `power-grid-model` (PGM), `power-grid-model-ds` (PGM-DS), `power-grid-model-io` (PGM-IO), `numpy`, `pandas`, `matplotlib`, and `seaborn`. |
| **Preference** | Prefer `numpy` over `pandas` where straightforward. |
| **Graph & Visualization** | Strictly utilize any graph and network consistency logic from `power-grid-model-ds` (which exposes a `Grid` dataclass, graph algorithms, and grid visualizer tools). Do not use outside graph dependencies like networkx directly. |
| **Less Popular Libraries** | If you need any library outside the permitted list, ask the user for confirmation first. |
| **Ask Questions** | When requirements are unclear at any step, pause and ask the user for clarification. |

## Python Script Standards
If the user provided other python standards always use these. Otherwise, use the following rules:
When delivering code as a Python script (`.py`):
- Organise all logic into well-named functions (e.g. `load_data()`, `run_power_flow()`, `plot_results()`).
- Include a `main()` function that calls them in order and contains no business logic itself.
- End every script with `if __name__ == "__main__": main()`.

## Plot Standards
When producing time-series plots:
- Always show real dates and times on the x-axis, not bare hours-from-zero.
- Build a `pd.DatetimeIndex` or `np.datetime64` array for the x-axis. If the start datetime cannot be derived from the data, ask the user before proceeding.
- Use `matplotlib.dates` (`AutoDateLocator`, `AutoDateFormatter`, or `mdates.DateFormatter`) so tick labels display as human-readable date/time strings (e.g. `2026-05-26 00:00`).

Use the following task-first workflow.

## Step 0: Clarify Output Format
Before writing any code, ask the user:

> "Should I write this as a Python script (`.py`) or a Jupyter notebook (`.ipynb`)?"

Wait for the answer and apply the appropriate standard (see **Python Script Standards** above for `.py`; use logical cell structure with markdown headings for `.ipynb`).

## Step 1: Classify the Task
Classify the user request into one or more of the following tasks:
- Build or extend an application/workflow on top of PGM.
- Convert/bridge datasets between formats or tools.
- Validate input/update data before calculations.
- Run studies (power flow, state estimation, short circuit).
- Evaluate and explain calculation outputs.
- Debug failures or inconsistent results.

If the request is ambiguous, ask clarifying questions first.

## Step 2: Deserialize and Normalize Data
Ensure the input/update data is in a PGM-compatible form.
- If data is in PGM JSON format, use `power-grid-model-io` converter flows.
- If data is external (Vision, Pandapower, tabular), convert with the correct PGM-IO converter.
- If deserialization or conversion fails, provide precise errors and corrective actions.

Primary references:
- `references/pgm-io/overview-and-converter-selection.md`
- `references/pgm-io/pgm-json-and-data-stores.md`

## Step 3: Execute the Task Playbook
Route to the relevant reference set:

- **Application build/extension**:
	- `references/tasks/application-build-and-automation.md`
	- `references/pgm-ds/pgm-interface-workflow.md`
- **Data validation**:
	- `references/tasks/conversion-validation.md`
	- `references/tasks/data-validation.md`
	- `references/tasks/engineering-plausibility-and-realism.md`
	- `references/tasks/validation-rules.yml`
	- `references/pgm/batch-validation-serialization.md`
- **Calculation run patterns**:
	- `references/pgm/calculation-recipes.md`
	- `references/pgm/overview-and-entrypoints.md`
- **Result evaluation and explanation**:
	- `references/tasks/result-evaluation-and-explanation.md`
	- `references/tasks/engineering-plausibility-and-realism.md`
- **Debugging/troubleshooting**:
	- `references/pgm/errors-and-debugging.md`
	- `references/pgm-ds/graph-and-topology-recipes.md`

When tasks overlap, prioritize references in the order of conversion, validation, calculation, and then debugging.

## Step 4: Return Outputs for the Active Task
Always return task-appropriate outputs:
- Code/script changes for implementation tasks.
- Validation findings and rejected records for validation tasks.
- Calculated datasets and method assumptions for study tasks.
- Clear diagnostics and fix options for debugging tasks.
- Summaries/charts and interpretation for result-explanation tasks.

## Completion Criteria
- [ ] Output format (`.py` or `.ipynb`) was confirmed with the user before writing code.
- [ ] The user request was classified into the correct PGM task(s).
- [ ] Data was deserialized/converted and validated where required.
- [ ] Appropriate ecosystem layers (PGM/PGM-DS/PGM-IO) were used for the task.
- [ ] Deliverables were provided in a task-appropriate form (code, diagnostics, or explanation).
- [ ] Python scripts use functions and a `main()` entry point (if output format is `.py`).
- [ ] Time-series plots show real dates/times on the x-axis (if plots were produced).
- [ ] Verified that no unauthorized external dependencies were used.

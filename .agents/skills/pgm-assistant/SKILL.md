---
# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

name: pgm-assistant
description: "Power grid model (PGM, PGM-DS, PGM-IO) work. Use when the user wants to run power flow, state estimation or short circuit (single, batch, N-1); validate PGM input/update data; convert Vision, pandapower or tabular data; analyse grid topology or feeders; build a PGM script, notebook or pipeline; explain or plot results; or debug PGM errors (IterationDiverge, SparseMatrixError, NotObservableError, IDNotFound, ConflictVoltage). Also when they only mention a network, grid, feeder, overloaded lines, sensors or input_data.json. Suspected bugs in PGM itself go to pgm-issue-analysis."
---

# Power Grid Model Assistant

## Package Version Status
Last reviewed: PGM v1.13.217 · PGM-DS v1.11.0 · PGM-IO v2.0.36 (checked 2026-10-30)

## Route to references
Read only the files the task needs, usually one to three. Paths are relative to `references/`. For multi-row tasks work in the order conversion → validation → calculation → explanation/debugging.

| Task | Read |
| --- | --- |
| Load or convert data (plain PGM JSON needs no converter) | `pgm-io/pgm-json-and-data-stores.md` (PGM JSON); for Vision, pandapower or tabular: `pgm-io/overview-and-converter-selection.md`, then `pgm-io/vision-conversion-guide.md`, `pgm-io/pandapower-conversion-guide.md` or `pgm-io/tabular-mapping-reference.md` |
| Check a conversion | `tasks/conversion-validation.md` |
| Validate input/update data, realism checks | `tasks/data-validation.md`, `tasks/engineering-plausibility-and-realism.md` (thresholds in `tasks/validation-rules.yml`), `pgm/batch-validation-serialization.md` |
| Run power flow / state estimation / short circuit, batch runs | `pgm/overview-and-entrypoints.md`, `pgm/calculation-recipes.md` |
| Component and attribute meaning, dtypes, dataset layout | `pgm/data-model-components-and-datasets.md` |
| Topology, radial/meshed, feeders, paths, mutations, visualizer | `pgm-ds/graph-and-topology-recipes.md`, `pgm-ds/overview-and-core-objects.md`, `pgm-ds/mutations-serialization-visualizer.md` |
| Run calculations from a PGM-DS `Grid` | `pgm-ds/pgm-interface-workflow.md` |
| Explain, summarise or plot results | `tasks/result-evaluation-and-explanation.md`, `tasks/engineering-plausibility-and-realism.md` |
| Debug errors or odd results | `pgm/errors-and-debugging.md`, `pgm-ds/graph-and-topology-recipes.md` |
| Build or extend an application/pipeline | `tasks/application-build-and-automation.md` |

## Rules
- **Validation gate.** Pass input and update data through the PGM validation functions before any calculation, so malformed data fails there instead of as an opaque solver error.
- **Run green.** Done means the code ran clean, convergence and batch errors (`continue_on_batch_error`, `batch_error`) were checked, and assumptions (method, symmetric vs asymmetric, loading limits, sensor sigmas, source `sk`) are stated.
- **Libraries.** PGM, PGM-DS, PGM-IO, `numpy`, `pandas`, `matplotlib`, `seaborn`, with `numpy` preferred over `pandas`; add the library a source format needs (e.g. `pandapower`).
- **Graphs.** Run every graph operation through PGM-DS (`Grid`, graph container), so topology stays consistent with the grid model.
- **Ask.** Ask the user only when the answer changes the result: limits, calculation type, time-series start datetime, a library outside the list, or, for a new code deliverable with no stated or visible preference, `.py` vs `.ipynb`. Otherwise pick a default (`.py`) and state it.

## Deliverable standards
**Scripts (`.py`)**, unless the user gave their own standards: logic in well-named functions (`load_data()`, `run_power_flow()`, `plot_results()`); `main()` calls them in order and holds no logic; end with `if __name__ == "__main__": main()`.

**Notebooks (`.ipynb`)**: logical cells, each section introduced by a markdown heading.

**Time-series plots**: real dates/times on the x-axis. Build a `pd.DatetimeIndex` or `np.datetime64` array and format ticks with `matplotlib.dates` (e.g. `2026-05-26 00:00`).

**By task**: code for implementation; findings and rejected records for validation; datasets plus method assumptions for studies; diagnosis plus fix options for debugging; summary, charts and interpretation for result explanation.

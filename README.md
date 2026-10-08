<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

[![Power Grid Model logo](https://raw.githubusercontent.com/PowerGridModel/.github/main/artwork/svg/color.svg)](#)

# Power Grid Model Skills

A collection of agent skills for working with the [power-grid-model](https://github.com/PowerGridModel/power-grid-model) (PGM) Python ecosystem.

## Skills

### pgm-assistant

A **pair-programming** skill that assists grid operators with the full PGM workflow: loading and converting grid data, running power flow and other studies, validating results, and explaining findings — all using the `power-grid-model`, `power-grid-model-ds`, and `power-grid-model-io` libraries.

Defined in [.agents/skills/pgm-assistant/SKILL.md](.agents/skills/pgm-assistant/SKILL.md). It covers:

- **Data ingestion** — deserializing PGM JSON and converting from external formats (Vision, Pandapower, tabular)
- **Validation** — input data validation and engineering plausibility checks
- **Calculations** — power flow, state estimation, and short-circuit studies
- **Result evaluation** — interpreting and explaining calculation outputs
- **Debugging** — diagnosing failures and inconsistent results

Reference documentation for the skill lives in [.agents/skills/pgm-assistant/references/](.agents/skills/pgm-assistant/references/).

Example prompt to ask the AI with this skill:

```
“Calculate short circuit faults on the network. Find the riskiest nodes and which branches would be affected. Use the PGM-assistant skill."
```

See [PROMPT_LIBRARY.md](.agents/skills/pgm-assistant/PROMPT_LIBRARY.md) for a list of other example prompts.

### pgm-issue-analysis

A **dedicated issue-debugging** skill for investigating errors and unexpected results in PGM. Defined in [.agents/skills/pgm-issues/SKILL.md](.agents/skills/pgm-issues/SKILL.md). You can use the skill to an initial investigation into an issue or error you get when working with PGM. This skill is especially usefull when encountering a **SparseMatrixError** or **IterationDiverge Error**. The skill create a **Minimal Reproducible Case** which helps in understanding what the root cause of the problem is.
It follows a structured five-step investigation workflow:

1. **Reproduce** — run the user's data as-is and confirm the exact error
2. **Understand the data** — build a structural picture of the network (voltage levels, topology, transformer connections)
3. **Validate** — run PGM's built-in validation plus cross-component consistency and physical plausibility checks
4. **Minimal reproducible example** — reduce the dataset to the fewest components that still trigger the failure
5. **Diagnose** — classify the root cause as a user data bug or a potential PGM bug

The skill produces a `report.ipynb` Jupyter notebook with its findings. Each investigation step is also saved as a numbered Python script (`step1_reproduce.py`, etc.) for full traceability.

Example prompt how to use the skill:

```
“I am encountering an error when using PGM. Here is the stack trace and dataset. Can you do an investigation to the root cause.”
```

## Installation

Skills are installed using `npx skills`, a package manager for agent skills. See [skills.sh](https://skills.sh) for more information.
To install the skills into your coding agent run:

```bash
# the skills package will ask you which skill you would like to install (pgm-assistant or pgm-issue-analysis)
npx skills install https://github.com/BrightCubes/power-grid-model-ai
```

<br><br><br>

## Development

To install requirements run:

```bash
uv sync
```

### Installing the skill-creator

The eval loop requires the `skill-creator` skill. How to install it depends on your agent:

**Claude Code** — run `/plugins` and install from the official plugins repository, or install directly with:

```bash
/plugins install https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md
```

**Other agents** — download the [skill-creator directory](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator/skills/skill-creator) and place it in your agent's skills directory (e.g. `.agents/skills/skill-creator`).

### Running skill evaluations

Skill development follows an iterative eval loop managed by the `skill-creator` agent skill. To start, open this repository in an agent that has `skill-creator` available and use a prompt like:

> "Run the evaluations for the pgm-assistant skill at `.agents/skills/pgm-assistant`"

The agent will take it from there:

1. **Run evals** — the agent runs test cases with and without the skill and saves results under `.agents/skills/pgm-assistant-workspace/iteration-N/`.
2. **Review results** — the agent opens a viewer where you leave feedback on each test case.
3. **Iterate** — based on your feedback, the agent improves the skill and reruns the evals.
4. **Optimize triggering** — once the skill content is stable, the agent can optimize the description so the skill triggers reliably.

Test cases are stored in [.agents/skills/pgm-assistant/evals/evals.json](.agents/skills/pgm-assistant/evals/evals.json).

## License

This project is licensed under the Mozilla Public License, version 2.0 - see
[LICENSE](https://github.com/PowerGridModel/pgm-template-repo/blob/main/LICENSE) for details.

## Licenses third-party libraries

This project includes third-party libraries,
which are licensed under their own respective Open-Source licenses.
SPDX-License-Identifier headers are used to show which license is applicable.
The concerning license files can be found in the
[LICENSES](https://github.com/PowerGridModel/pgm-template-repo/tree/main/LICENSES) directory.

## Contributing

Please read [CODE_OF_CONDUCT](https://github.com/PowerGridModel/.github/blob/main/CODE_OF_CONDUCT.md) and [CONTRIBUTING](https://github.com/PowerGridModel/.github/blob/main/CONTRIBUTING.md) for details on the process 
for submitting pull requests to us.

## Historical contributors
Our gratitude goes to the following contributors who have worked (and are still working) on these services before it became open source:

- Camiel Oerlemans (Bright Cubes)
- Nitish Bharambe (Alliander)
- Martijn Govers (Bright Cubes)

## Citations

If you are using Power Grid Model in your research work, please consider citing our library using the following
references.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8054429.svg)](https://zenodo.org/record/8054429)

```bibtex
@software{Xiang_PowerGridModel_power-grid-model,
  author = {Xiang, Yu and Salemink, Peter and van Westering, Werner and Bharambe, Nitish and Govers, Martinus G.H. and van den Bogaard, Jonas and Stoeller, Bram and Wang, Zhen and Guo, Jerry Jinfeng and Figueroa Manrique, Santiago and Jagutis, Laurynas and Wang, Chenguang and van Raalte, Marc and {Contributors to the LF Energy project Power Grid Model}},
  doi = {10.5281/zenodo.8054429},
  license = {MPL-2.0},
  title = {{PowerGridModel/power-grid-model}},
  url = {https://github.com/PowerGridModel/power-grid-model}
}
@inproceedings{Xiang2023,
  author = {Xiang, Yu and Salemink, Peter and Stoeller, Bram and Bharambe, Nitish and van Westering, Werner},
  booktitle={27th International Conference on Electricity Distribution (CIRED 2023)},
  title={Power grid model: a high-performance distribution grid calculation library},
  year={2023},
  volume={2023},
  number={},
  pages={1089-1093},
  keywords={},
  doi={10.1049/icp.2023.0633}
}
```

## Contact

Please read [SUPPORT](https://github.com/PowerGridModel/.github/blob/main/SUPPORT.md) for how to connect and get into
contact with the Power Grid Model project.

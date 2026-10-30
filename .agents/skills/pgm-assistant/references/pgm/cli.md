<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# PGM Command Line Interface

Experimental, added in PGM v1.13.207; the project gives no stability guarantee for its arguments. Check availability first with `power-grid-model --version` (older installs, e.g. 1.13.197, lack it). `pip`/`uv` installs expose the command through a Python shim; inside conda call the executable directly. Verified against v1.13.209.

## When the CLI beats a script

- The user wants results from existing PGM files and no code: one command runs the full calculation, including a 192-scenario batch in about 0.2 s, and output equals the Python API (identical `loading` values on the synthetic data).
- A reproducible one-liner for an issue, CI job or hand-off.
- Testing an on-the-fly hypothesis: filter the output with `--oc`/`--oa`, pipe it through `jq` (see below).
- Writing a result file for a later analysis script.

Use the Python API when the deliverable is code, when you need validation, partial batch results, post-processing in the same run, or anything the flags below do not cover.

## Usage

One command, no subcommands. Required: `-i/--input` and `-o/--output` (the output's parent directory must exist).

```bash
power-grid-model -i input.json -b update.json -o output.json \
  -c power_flow -m newton_raphson --oc line --oa line.id --oa line.loading
```

| Flag | Meaning |
| --- | --- |
| `-c`, `--calculation-type` | `power_flow` (default), `state_estimation`, `short_circuit` (or 0/1/2) |
| `-m`, `--calculation-method` | `default`, `linear`, `newton_raphson`, `iterative_linear`, `iterative_current`, `linear_current`, `iec60909` |
| `-b`, `--batch-update` | Update file; repeat the flag for a cartesian product of batches |
| `--asym` / `--sym` | Asymmetric or symmetric calculation (default symmetric) |
| `--error-tolerance`, `--max-iterations`, `--threading`, `--hertz` | As in the Python calls (`--threading -1` sequential, `0` all threads) |
| `--short-circuit-voltage-scaling`, `--calculation-initialization`, `--tap-changing-strategy` | Enum names or numbers, as in Python |
| `--oc component`, `--oa component.attribute` | Filter output components and attributes (repeatable) |
| `--msgpack` / `--json`, `--indent N`, `--compact` | Output serialization |
| `--verbose` | Echo the resolved options |

## Formats

- Input and update files are in the standard PGM serialization format (`version`/`type`/`data` envelope; JSON or msgpack), i.e. what `json_serialize_to_file` writes. They are not the PGM-IO layout.
- Output is a PGM serialization file. Read it back with `json_deserialize_from_file(Path(...))` or `msgpack_deserialize_from_file(Path(...))` to get numpy data identical in shape to the Python API (`(n_scenarios, n_elements)` for batches).

## Quick hypothesis loop with jq

`--oc`/`--oa` keep the output small and `-o /dev/stdout` streams it, so a question can be answered in one pipeline (needs `jq` installed). Default output is a JSON object per record, so no attribute lookup is needed; with `--compact` records become arrays ordered like `.attributes`.

```bash
set -o pipefail   # otherwise a CLI failure is hidden by the exit code of the last pipe stage

# which lines exceed 100 % loading (single scenario)
power-grid-model -i in.json -o /dev/stdout --oc line --oa line.id --oa line.loading 2>/dev/null \
  | jq -c '.data.line[] | select(.loading > 1)'

# batch: peak loading of line 307 over all scenarios (batch output: .data[] is one object per scenario)
power-grid-model -i in.json -b upd.json -o /dev/stdout --oc line --oa line.id --oa line.loading 2>/dev/null \
  | jq '[.data[].line[] | select(.id == 307) | .loading] | max'

# what-if: edit the input with jq, run on a temp file, count de-energised nodes
jq '(.data.line[] | select(.id == 307) | .to_status) = 0' in.json > /tmp/whatif.json
power-grid-model -i /tmp/whatif.json -o /dev/stdout --oc node --oa node.energized 2>/dev/null \
  | jq '[.data.node[] | select(.energized == 0)] | length'
```

Rules for pipelines (all verified):
- `-i` needs a real file; `<(...)` and `/dev/stdin` fail with `Failed to open file`. Write edited inputs to a temp file.
- Keep `--verbose` out of pipes: it prints to stdout and breaks the JSON.
- Add `2>/dev/null` only after the command is known to work, because error messages go to stderr.
- Each run reloads the model, so a shell loop over elements suits a handful of hypotheses. Hundreds of scenarios (full N-1) belong in one Python batch update.
- Opening one line of a radial grid de-energises everything downstream; the power flow still succeeds and reports `energized == 0` for those nodes.

## Behaviour to plan for

- No validation: run the validation gate in Python beforehand.
- A failing scenario aborts the whole run: error `Error in batch #3: ...`, exit code 2, no output file. There is no `continue_on_batch_error` equivalent; use the Python API when partial results matter.
- Other PGM errors print the message (for example `Conflicting id detected`, `No voltage sensor found!`) and exit with 1. Bad arguments or missing files exit with 105.
- Short circuit still needs `fault` components in the input, and each `source` a finite `sk`; defaults apply silently as in Python.

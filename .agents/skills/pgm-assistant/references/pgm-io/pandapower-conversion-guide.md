<!--
SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Pandapower Conversion Guide (PGM-IO)

## Standard Pandapower Workflow
1. Build/load pandapower `net`.
2. Convert to PGM input:
```python
from power_grid_model_io.converters import PandaPowerConverter

converter = PandaPowerConverter()
input_data, extra_info = converter.load_input_data(pp_net)
```
3. Validate with PGM validation.
4. Run PGM calculation.
5. Convert output back to pandapower result tables:
```python
converted_output = converter.convert(output_data)
for table in converted_output:
    pp_net[table] = converted_output[table]
```

## Cross-Reference Utilities
- `lookup_id(pgm_id)` -> original `(table, index)` mapping
- `get_id(pp_table, pp_idx, name=None)` -> generated PGM ID

## Switch and Transformer Helpers
Converter includes utilities for switch state and winding extraction:
- `get_switch_states(...)`
- `get_trafo_winding_types()`
- `get_trafo3w_winding_types()`

## Typical Roundtrip Pattern
- `pp_net` -> `input_data`
- `PowerGridModel(input_data)` -> `output_data`
- `converter.convert(output_data)` -> `res_*` dataframes

## Important Modeling Differences
Current caveats include:
- Focus is power-flow conversion path.
- `gen` elements are converted (input plus symmetric and three-phase output) as of PGM-IO v1.3.90, sharing the conversion path with `sgen`. Other PV-related features remain unsupported.
- Delta load type unsupported in PGM conversion.
- Some switch-related attributes are unsupported.
- External grid/source impedance treatment differs.
- Transformer and three-winding transformer feature gaps exist for some zero-sequence and phase-shift settings.
- `trafo.mag0_percent` (zero-sequence magnetizing impedance) is interpreted as a percentage for pandapower >= 3.4.0 as of PGM-IO v1.3.44; keep pandapower versions aligned when converting zero-sequence transformer parameters.

## Asymmetric Workflows
Asymmetric examples are supported with converted input and `calculate_power_flow(symmetric=False)`, then conversion back to pandapower result tables.

## Practical Checklist
1. Ensure pandapower net has required electrical parameters loaded.
2. Validate converted `input_data` before calculation.
3. Keep `extra_info` for object reconciliation.
4. Compare a baseline case against pandapower run for confidence.
5. Document any accepted differences due to model mismatch.

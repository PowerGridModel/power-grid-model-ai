<!--
SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>

SPDX-License-Identifier: MPL-2.0
-->

# Pandapower Conversion Guide (PGM-IO)

## Workflow
```python
from power_grid_model import PowerGridModel
from power_grid_model_io.converters import PandaPowerConverter

converter = PandaPowerConverter(system_frequency=50.0, trafo_loading="current")
input_data, extra_info = converter.load_input_data(pp_net)
output_data = PowerGridModel(input_data).calculate_power_flow()   # symmetric=False -> *_3ph result tables
converted_output = converter.convert(output_data)                  # dict: res_* name -> DataFrame
for table, df in converted_output.items():
    pp_net[table] = df
```
- Only `load_input_data(pp_net)` and `convert(output_data)` are supported: no update, short-circuit or file/`save` path. `pp_net` must hold every standard element table (a real `pandapowerNet` does; empty ones are fine).
- `system_frequency` (Hz) is used to derive line `tan1` from `g_us_per_km` and `c_nf_per_km`. `trafo_loading` is `"current"` or `"power"` and selects how `res_trafo.loading_percent` is derived (other values raise `ValueError` in `convert`).
- Symmetric versus asymmetric output is detected from the arrays' dtype; pass an unmodified calculation result of one kind. Asymmetric output yields `res_*_3ph` tables, without `trafo3w` and `switch`.
- `convert` on the same instance that loaded the input: call `convert(output_data)` without `extra_info` (passing it raises `ValueError: pgm_input_data should be empty`).
  In a fresh instance (e.g. a later session) call `convert(output_data, extra_info=extra_info)` with the `extra_info` from `load_input_data`; it carries the table/index reference, node references and trafo derating factor needed for the output. A fresh instance without `extra_info` raises `KeyError: No indexes have been created`.

## ID Cross-Reference
PGM ids are sequential from 0 over all elements. One pandapower element may become several PGM components, distinguished by `name`:
- `get_id(pp_table, pp_idx, name=None)` -> PGM id; `lookup_id(pgm_id)` -> `{"table", "name"?, "index"}`.
- Names: `load` -> `const_power`, `const_impedance`, `const_current` (three `sym_load`s, so `get_id("load", idx)` needs a `name`); `gen` -> `gen` (`sym_gen`) and `regulator` (`voltage_regulator`, `u_ref` = `vm_pu`); `ward` -> `ward_const_power_load`, `ward_const_impedance_load`; `motor` -> `motor_load`; bus-bus switches (`et == "b"`) -> `b2b_switches` (links). All other tables (`bus`, `line`, `trafo`, `trafo3w`, `ext_grid`, `shunt`, `sgen`, `asymmetric_*`) have no name.
- `extra_info[pgm_id]["id_reference"]` holds the same reference.

## Helpers
`get_switch_states(pp_table)` (`"line"` or `"trafo"`, columns `from`/`to`), `get_trafo3w_switch_states(trafo3w)`, `get_trafo_winding_types()`, `get_trafo3w_winding_types()` operate on the loaded `pp_input_data`; they are used internally and rarely needed directly.

## Unsupported and Approximated Features
- Raise `NotImplementedError` when the table is non-empty: `storage`, `impedance`, `xward`, `dcline`; and for `load`/`asymmetric_load` with `type == "delta"` (only wye).
- Raise `RuntimeError`: `tap_dependent_impedance` on `trafo`/`trafo3w`; `tap_at_star_point` on `trafo3w`.
- Ignored with a logged warning: zero-sequence settings of `ext_grid` (`r0x0_max`, `x0x_max`) and of `trafo`/`trafo3w` (`vk0_percent`, `vkr0_percent`, `si0_hv_partial`, ...).
- `gen` is converted (input, symmetric and three-phase output) like `sgen`, plus a voltage regulator (since PGM-IO v1.3.90); `res_gen` only has `p_mw` and `q_mvar`. Other PV-related features are unsupported.
- `trafo.shift_degree` is rounded to a 30-degree clock number.
- `trafo.mag0_percent` is read as a percentage for pandapower >= 3.4.0 (since PGM-IO v1.3.44); for older installed versions the converter multiplies it by 100. The converter reads the installed pandapower version (assuming 3.4.0 when pandapower is absent), so keep it aligned with the net's origin.
- External grid / source impedance treatment differs from pandapower; compare a baseline case against a pandapower run and document accepted differences.

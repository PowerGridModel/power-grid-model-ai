#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

# pyright: reportMissingTypeStubs=false
"""Generate synthetic PGM datasets and optional visualization for skill testing."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from power_grid_model import (
    CalculationMethod,
    CalculationType,
    ComponentType,
    DatasetType,
)
from power_grid_model.data_types import BatchDataset
from power_grid_model.utils import json_serialize_to_file
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data
from power_grid_model_ds import Grid, PowerGridModelInterface

from _synthetic_pgm_common import (
    _find_component_key,
    create_synthetic_input_data,
    create_synthetic_load_update_data,
)


def validate_datasets(input_data: dict, update_data: dict) -> None:
    assert_valid_input_data(
        input_data,
        calculation_type=CalculationType.power_flow,
        symmetric=True,
    )
    assert_valid_batch_data(
        input_data,
        update_data,
        calculation_type=CalculationType.power_flow,
        symmetric=True,
    )


def run_power_flow(
    input_data: dict,
    update_data: dict,
    calculation_method: CalculationMethod,
) -> dict:
    interface = PowerGridModelInterface(input_data=input_data)
    interface.setup_model()
    return interface.calculate_power_flow(
        calculation_method=calculation_method,
        update_data=update_data,
    )


def maybe_visualize_grid(
    grid: Grid,
    update_data: BatchDataset,
    output_data: BatchDataset,
    visualize_enabled: bool,
) -> None:
    if not visualize_enabled:
        return

    try:
        from power_grid_model_ds.visualizer import visualize
    except ImportError as error:
        print("Visualization skipped: optional visualizer dependencies are not installed.")
        print("Install with: pip install 'power-grid-model-ds[visualizer]'")
        print(f"Import error: {error}")
        return

    print("Starting visualizer at default http://127.0.0.1:8050")
    visualize(grid=grid, update_data=update_data, output_data=output_data)


def main() -> None:
    visualize_enabled = True
    nr_nodes = 100
    nr_sources = 1
    nr_nops = 0
    nr_days = 2
    step_minutes = 15
    grid_seed = 20260522
    profile_seed = 20260523
    create_10_3_kv_net = False
    calculation_method = CalculationMethod.newton_raphson
    output_root = Path(__file__).resolve().parent / "generated"
    run_name = f"{datetime.now(timezone.utc).strftime('synthetic_pgm_data_%Y%m%dT%H%M%SZ')}"

    n_steps = nr_days * 24 * (60 // step_minutes)
    run_dir = output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    input_path = run_dir / "synthetic_input_data.json"
    update_path = run_dir / "synthetic_update_data.json"
    output_path = run_dir / "synthetic_power_flow_output_data.json"
    params_path = run_dir / "generation_params.json"

    grid, input_data = create_synthetic_input_data(
        nr_nodes=nr_nodes,
        nr_sources=nr_sources,
        nr_nops=nr_nops,
        seed=grid_seed,
        create_10_3_kv_net=create_10_3_kv_net,
    )
    update_data = create_synthetic_load_update_data(
        input_data=input_data,
        n_steps=n_steps,
        step_minutes=step_minutes,
        seed=profile_seed,
    )
    validate_datasets(input_data=input_data, update_data=update_data)
    output_data = run_power_flow(
        input_data=input_data,
        update_data=update_data,
        calculation_method=calculation_method,
    )

    json_serialize_to_file(
        input_path,
        input_data,
        dataset_type=DatasetType.input,
    )
    json_serialize_to_file(
        update_path,
        update_data,
        dataset_type=DatasetType.update,
        use_compact_list=True,
    )
    json_serialize_to_file(
        output_path,
        output_data,
        dataset_type=DatasetType.sym_output,
        use_compact_list=True,
    )

    params_payload = {
        "nr_nodes": nr_nodes,
        "nr_sources": nr_sources,
        "nr_nops": nr_nops,
        "nr_days": nr_days,
        "step_minutes": step_minutes,
        "n_steps": n_steps,
        "grid_seed": grid_seed,
        "profile_seed": profile_seed,
        "create_10_3_kv_net": create_10_3_kv_net,
        "calculation_method": calculation_method.name,
    }
    params_path.write_text(json.dumps(params_payload, indent=2), encoding="utf-8")

    sym_load_key = _find_component_key(input_data, ComponentType.sym_load)
    print(f"Wrote input_data to: {input_path}")
    print(f"Wrote update_data to: {update_path}")
    print(f"Wrote power_flow output to: {output_path}")
    print(f"Wrote generation params to: {params_path}")
    print(f"Grid nodes: {len(input_data[_find_component_key(input_data, ComponentType.node)])}")
    print(f"Symmetric loads: {len(input_data[sym_load_key])}")
    print(f"Time steps: {n_steps} ({nr_days} days at {step_minutes}-minute resolution)")

    maybe_visualize_grid(
        grid=grid,
        update_data=update_data,
        output_data=output_data,
        visualize_enabled=visualize_enabled,
    )


if __name__ == "__main__":
    main()

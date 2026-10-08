#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

# pyright: reportMissingTypeStubs=false
"""Generate synthetic state-estimation datasets and optional visualization."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from power_grid_model import (
    CalculationMethod,
    CalculationType,
    ComponentType,
    DatasetType,
    MeasuredTerminalType,
    PowerGridModel,
    initialize_array,
)
from power_grid_model.data_types import BatchDataset
from power_grid_model.utils import json_serialize_to_file
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data
from power_grid_model_ds import Grid

from _synthetic_pgm_common import (
    _find_component_key,
    create_synthetic_input_data,
    create_synthetic_load_update_data,
)


def run_power_flow_truth(
    input_data: dict,
    load_update_data: dict,
    calculation_method: CalculationMethod,
) -> dict:
    model = PowerGridModel(input_data)
    return model.calculate_power_flow(
        calculation_method=calculation_method,
        update_data=load_update_data,
    )


def _next_ids(input_data: dict, count: int, start: int = 0) -> np.ndarray:
    max_id = start
    for component_data in input_data.values():
        dtype = getattr(component_data, "dtype", None)
        if dtype is None or dtype.names is None or "id" not in dtype.names or component_data.size == 0:
            continue
        max_id = max(max_id, int(np.max(component_data["id"])))
    return np.arange(max_id + 1, max_id + count + 1, dtype=np.int32)


def _positive_sigma(values: np.ndarray, relative_sigma: float, absolute_floor: float) -> np.ndarray:
    return np.maximum(np.abs(values) * relative_sigma, absolute_floor)


def _apply_measurement_noise(values: np.ndarray, sigma: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return values + rng.normal(loc=0.0, scale=1.0, size=values.shape) * sigma


def create_state_estimation_sensor_input(
    input_data: dict,
    truth_output_data: dict,
    measurement_seed: int,
    voltage_relative_sigma: float,
    voltage_sigma_floor: float,
    power_relative_sigma: float,
    power_sigma_floor: float,
) -> tuple[dict, dict[str, np.ndarray]]:
    node_key = _find_component_key(input_data, ComponentType.node)
    sym_load_key = _find_component_key(input_data, ComponentType.sym_load)
    source_key = _find_component_key(input_data, ComponentType.source)

    node_ids = input_data[node_key]["id"].astype(np.int32, copy=False)
    load_ids = input_data[sym_load_key]["id"].astype(np.int32, copy=False)
    source_ids = input_data[source_key]["id"].astype(np.int32, copy=False)

    truth_nodes = truth_output_data[node_key]
    truth_loads = truth_output_data[sym_load_key]
    truth_sources = truth_output_data[source_key]

    voltage_sensor_ids = _next_ids(input_data, count=len(node_ids))
    power_sensor_ids = _next_ids(
        input_data,
        count=len(load_ids) + len(source_ids),
        start=int(voltage_sensor_ids[-1]) if len(voltage_sensor_ids) else 0,
    )

    voltage_sensors = initialize_array(DatasetType.input, ComponentType.sym_voltage_sensor, len(node_ids))
    voltage_sensors["id"] = voltage_sensor_ids
    voltage_sensors["measured_object"] = node_ids
    voltage_sigma = _positive_sigma(truth_nodes[0]["u"], voltage_relative_sigma, voltage_sigma_floor)
    voltage_sensors["u_sigma"] = voltage_sigma
    voltage_sensors["u_measured"] = _apply_measurement_noise(
        truth_nodes[0]["u"],
        voltage_sigma,
        seed=measurement_seed,
    )

    n_power_sensors = len(load_ids) + len(source_ids)
    power_sensors = initialize_array(DatasetType.input, ComponentType.sym_power_sensor, n_power_sensors)
    power_sensors["id"] = power_sensor_ids
    power_sensors["measured_object"][: len(load_ids)] = load_ids
    power_sensors["measured_object"][len(load_ids) :] = source_ids
    power_sensors["measured_terminal_type"][: len(load_ids)] = MeasuredTerminalType.load
    power_sensors["measured_terminal_type"][len(load_ids) :] = MeasuredTerminalType.source

    base_power_p = np.concatenate([truth_loads[0]["p"], truth_sources[0]["p"]])
    base_power_q = np.concatenate([truth_loads[0]["q"], truth_sources[0]["q"]])
    base_p_sigma = _positive_sigma(base_power_p, power_relative_sigma, power_sigma_floor)
    base_q_sigma = _positive_sigma(base_power_q, power_relative_sigma, power_sigma_floor)
    power_sensors["p_sigma"] = base_p_sigma
    power_sensors["q_sigma"] = base_q_sigma
    power_sensors["p_measured"] = _apply_measurement_noise(
        base_power_p,
        base_p_sigma,
        seed=measurement_seed + 1,
    )
    power_sensors["q_measured"] = _apply_measurement_noise(
        base_power_q,
        base_q_sigma,
        seed=measurement_seed + 2,
    )

    sensor_input_data = dict(input_data)
    sensor_input_data[ComponentType.sym_voltage_sensor] = voltage_sensors
    sensor_input_data[ComponentType.sym_power_sensor] = power_sensors
    sensor_metadata = {
        "voltage_sensor_ids": voltage_sensor_ids,
        "power_sensor_ids": power_sensor_ids,
        "voltage_sigma": voltage_sigma,
        "p_sigma": base_p_sigma,
        "q_sigma": base_q_sigma,
    }
    return sensor_input_data, sensor_metadata


def create_state_estimation_sensor_update_data(
    input_data: dict,
    truth_output_data: dict,
    sensor_metadata: dict[str, np.ndarray],
    measurement_seed: int,
) -> dict:
    node_key = _find_component_key(input_data, ComponentType.node)
    sym_load_key = _find_component_key(input_data, ComponentType.sym_load)
    source_key = _find_component_key(input_data, ComponentType.source)

    truth_nodes = truth_output_data[node_key]
    truth_loads = truth_output_data[sym_load_key]
    truth_sources = truth_output_data[source_key]
    n_steps = truth_nodes.shape[0]

    voltage_sensor_ids = sensor_metadata["voltage_sensor_ids"]
    power_sensor_ids = sensor_metadata["power_sensor_ids"]
    voltage_sigma = np.broadcast_to(sensor_metadata["voltage_sigma"], truth_nodes["u"].shape)
    p_sigma = np.broadcast_to(sensor_metadata["p_sigma"], (n_steps, len(power_sensor_ids)))
    q_sigma = np.broadcast_to(sensor_metadata["q_sigma"], (n_steps, len(power_sensor_ids)))

    voltage_sensor_updates = initialize_array(
        DatasetType.update,
        ComponentType.sym_voltage_sensor,
        shape=(n_steps, len(voltage_sensor_ids)),
    )
    voltage_sensor_updates["id"] = voltage_sensor_ids[np.newaxis, :]
    voltage_sensor_updates["u_measured"] = _apply_measurement_noise(
        truth_nodes["u"],
        voltage_sigma,
        seed=measurement_seed + 3,
    )

    power_sensor_updates = initialize_array(
        DatasetType.update,
        ComponentType.sym_power_sensor,
        shape=(n_steps, len(power_sensor_ids)),
    )
    power_sensor_updates["id"] = power_sensor_ids[np.newaxis, :]
    truth_p = np.concatenate([truth_loads["p"], truth_sources["p"]], axis=1)
    truth_q = np.concatenate([truth_loads["q"], truth_sources["q"]], axis=1)
    power_sensor_updates["p_measured"] = _apply_measurement_noise(
        truth_p,
        p_sigma,
        seed=measurement_seed + 4,
    )
    power_sensor_updates["q_measured"] = _apply_measurement_noise(
        truth_q,
        q_sigma,
        seed=measurement_seed + 5,
    )

    return {
        ComponentType.sym_voltage_sensor: voltage_sensor_updates,
        ComponentType.sym_power_sensor: power_sensor_updates,
    }


def validate_datasets(input_data: dict, update_data: dict) -> None:
    assert_valid_input_data(
        input_data,
        calculation_type=CalculationType.state_estimation,
        symmetric=True,
    )
    assert_valid_batch_data(
        input_data,
        update_data,
        calculation_type=CalculationType.state_estimation,
        symmetric=True,
    )


def run_state_estimation(
    input_data: dict,
    update_data: dict,
    calculation_method: CalculationMethod,
) -> dict:
    model = PowerGridModel(input_data)
    return model.calculate_state_estimation(
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
    measurement_seed = 20260524
    create_10_3_kv_net = False
    truth_calculation_method = CalculationMethod.newton_raphson
    state_estimation_method = CalculationMethod.iterative_linear
    voltage_relative_sigma = 0.005
    voltage_sigma_floor = 5.0
    power_relative_sigma = 0.02
    power_sigma_floor = 50.0
    output_root = Path(__file__).resolve().parent / "generated"
    run_name = f"{datetime.now(timezone.utc).strftime('synthetic_state_estimation_data_%Y%m%dT%H%M%SZ')}"

    n_steps = nr_days * 24 * (60 // step_minutes)
    run_dir = output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    input_path = run_dir / "synthetic_state_estimation_input_data.json"
    update_path = run_dir / "synthetic_state_estimation_update_data.json"
    output_path = run_dir / "synthetic_state_estimation_output_data.json"
    truth_output_path = run_dir / "synthetic_truth_power_flow_output_data.json"
    params_path = run_dir / "generation_params.json"

    grid, base_input_data = create_synthetic_input_data(
        nr_nodes=nr_nodes,
        nr_sources=nr_sources,
        nr_nops=nr_nops,
        seed=grid_seed,
        create_10_3_kv_net=create_10_3_kv_net,
    )
    load_update_data = create_synthetic_load_update_data(
        input_data=base_input_data,
        n_steps=n_steps,
        step_minutes=step_minutes,
        seed=profile_seed,
    )
    truth_output_data = run_power_flow_truth(
        input_data=base_input_data,
        load_update_data=load_update_data,
        calculation_method=truth_calculation_method,
    )
    state_estimation_input_data, sensor_metadata = create_state_estimation_sensor_input(
        input_data=base_input_data,
        truth_output_data=truth_output_data,
        measurement_seed=measurement_seed,
        voltage_relative_sigma=voltage_relative_sigma,
        voltage_sigma_floor=voltage_sigma_floor,
        power_relative_sigma=power_relative_sigma,
        power_sigma_floor=power_sigma_floor,
    )
    sensor_update_data = create_state_estimation_sensor_update_data(
        input_data=state_estimation_input_data,
        truth_output_data=truth_output_data,
        sensor_metadata=sensor_metadata,
        measurement_seed=measurement_seed,
    )
    state_estimation_update_data = dict(load_update_data)
    state_estimation_update_data.update(sensor_update_data)
    validate_datasets(
        input_data=state_estimation_input_data,
        update_data=state_estimation_update_data,
    )
    output_data = run_state_estimation(
        input_data=state_estimation_input_data,
        update_data=state_estimation_update_data,
        calculation_method=state_estimation_method,
    )

    json_serialize_to_file(
        input_path,
        state_estimation_input_data,
        dataset_type=DatasetType.input,
    )
    json_serialize_to_file(
        update_path,
        state_estimation_update_data,
        dataset_type=DatasetType.update,
        use_compact_list=True,
    )
    json_serialize_to_file(
        output_path,
        output_data,
        dataset_type=DatasetType.sym_output,
        use_compact_list=True,
    )
    json_serialize_to_file(
        truth_output_path,
        truth_output_data,
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
        "measurement_seed": measurement_seed,
        "create_10_3_kv_net": create_10_3_kv_net,
        "truth_calculation_method": truth_calculation_method.name,
        "state_estimation_method": state_estimation_method.name,
        "voltage_relative_sigma": voltage_relative_sigma,
        "voltage_sigma_floor": voltage_sigma_floor,
        "power_relative_sigma": power_relative_sigma,
        "power_sigma_floor": power_sigma_floor,
    }
    params_path.write_text(json.dumps(params_payload, indent=2), encoding="utf-8")

    node_key = _find_component_key(state_estimation_input_data, ComponentType.node)
    sym_load_key = _find_component_key(state_estimation_input_data, ComponentType.sym_load)
    voltage_sensor_key = _find_component_key(state_estimation_input_data, ComponentType.sym_voltage_sensor)
    power_sensor_key = _find_component_key(state_estimation_input_data, ComponentType.sym_power_sensor)

    print(f"Wrote state-estimation input_data to: {input_path}")
    print(f"Wrote state-estimation update_data to: {update_path}")
    print(f"Wrote state-estimation output to: {output_path}")
    print(f"Wrote truth power-flow output to: {truth_output_path}")
    print(f"Wrote generation params to: {params_path}")
    print(f"Grid nodes: {len(state_estimation_input_data[node_key])}")
    print(f"Symmetric loads: {len(state_estimation_input_data[sym_load_key])}")
    print(f"Voltage sensors: {len(state_estimation_input_data[voltage_sensor_key])}")
    print(f"Power sensors: {len(state_estimation_input_data[power_sensor_key])}")
    print(f"Time steps: {n_steps} ({nr_days} days at {step_minutes}-minute resolution)")

    maybe_visualize_grid(
        grid=grid,
        update_data=state_estimation_update_data,
        output_data=output_data,
        visualize_enabled=visualize_enabled,
    )


if __name__ == "__main__":
    main()
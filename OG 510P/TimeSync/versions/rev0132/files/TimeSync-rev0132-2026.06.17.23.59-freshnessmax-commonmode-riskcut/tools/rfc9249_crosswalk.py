#!/usr/bin/env python3
"""Validate RFC 9249 / adapter observation crosswalks.

The crosswalks are guardrails against premature generic observation schemas.
Each mapped adapter observation field must declare whether it directly maps,
partially maps, has a standards gap, or is adapter-local, and every such field
remains forbidden for TimeState core promotion until a later adapter proof
justifies it.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
CHRONY_CROSSWALK = ROOT / 'tests/rfc9249-chrony-observation-crosswalk.yaml'
NTPQ_CROSSWALK = ROOT / 'tests/rfc9249-ntpq-observation-crosswalk.yaml'
CHRONY_REQUIRED_PATHS = {
    'tracking.stratum',
    'tracking.reference_id',
    'tracking.system_time_offset_seconds',
    'tracking.root_delay_seconds',
    'tracking.root_dispersion_seconds',
    'tracking.ref_time_utc',
    'tracking.leap_status',
    'tracking.skew_ppm',
    'sources_summary.states[].state',
    'sourcestats_summary.rows[].freq_skew_ppm',
    'sourcestats_summary.rows[].std_dev_seconds',
    'authentication_summary.authdata_rows[].mode',
    'authentication_summary.ntpdata_blocks[].authenticated',
    'capture_context.monotonic_duration_ns',
}
NTPQ_REQUIRED_PATHS = {
    'system.stratum',
    'system.reference_id',
    'system.system_time_offset_seconds',
    'system.root_delay_seconds',
    'system.root_dispersion_seconds',
    'system.ref_time_utc',
    'system.leap',
    'system.clk_wander_ppm',
    'peers_summary.states[].tally',
    'peers_summary.states[].reach',
    'authentication_summary.reported_packet_authentication',
}
VALID_DECISIONS = {'direct_map', 'partial_map', 'gap', 'adapter_local'}
VALID_PROMOTIONS = {'forbidden'}


def load_yaml(path: Path) -> Any:
    import yaml  # type: ignore
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def check_crosswalk(path: Path, *, path_key: str, required_paths: set[str], label: str) -> list[str]:
    errors: list[str] = []
    try:
        rows = load_yaml(path)
    except Exception as exc:  # noqa: BLE001
        return [f'cannot load RFC 9249 {label} crosswalk: {exc}']
    if not isinstance(rows, list) or not rows:
        return [f'RFC 9249 {label} crosswalk must be a non-empty list']
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f'{label} crosswalk row {index} must be an object')
            continue
        obs_path = row.get(path_key)
        if not isinstance(obs_path, str) or not obs_path:
            errors.append(f'{label} crosswalk row {index} requires {path_key}')
            continue
        if obs_path in seen:
            errors.append(f'duplicate {label} crosswalk path: {obs_path}')
        seen.add(obs_path)
        if row.get('decision') not in VALID_DECISIONS:
            errors.append(f'{obs_path}: decision must be one of {sorted(VALID_DECISIONS)}')
        if row.get('core_promotion') not in VALID_PROMOTIONS:
            errors.append(f'{obs_path}: core_promotion must be forbidden')
        ref = row.get('rfc9249_reference')
        if not isinstance(ref, str) or not ref:
            errors.append(f'{obs_path}: rfc9249_reference must be a non-empty string')
        note = row.get('unit_or_semantic_note')
        if not isinstance(note, str) or len(note.strip()) < 20:
            errors.append(f'{obs_path}: unit_or_semantic_note must explain the mapping/gap')
        if row.get('decision') in {'gap', 'adapter_local'} and ref not in {'none'} and '/' not in str(ref):
            errors.append(f'{obs_path}: gap/adapter-local rows must name none or a concrete comparison path')
    missing = sorted(required_paths - seen)
    if missing:
        errors.append(f'RFC 9249 {label} crosswalk missing required paths: {missing}')
    return errors


def check_all(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(check_crosswalk(root / 'tests/rfc9249-chrony-observation-crosswalk.yaml', path_key='chrony_observation_path', required_paths=CHRONY_REQUIRED_PATHS, label='chrony-observation'))
    errors.extend(check_crosswalk(root / 'tests/rfc9249-ntpq-observation-crosswalk.yaml', path_key='ntpq_observation_path', required_paths=NTPQ_REQUIRED_PATHS, label='ntpq-observation'))
    return errors


def self_test(root: Path = ROOT) -> list[str]:
    return check_all(root)


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate RFC 9249 adapter-observation crosswalks.')
    parser.add_argument('--adapter', choices=['all', 'chrony', 'ntpq'], default='all')
    args = parser.parse_args()
    if args.adapter == 'chrony':
        failures = check_crosswalk(CHRONY_CROSSWALK, path_key='chrony_observation_path', required_paths=CHRONY_REQUIRED_PATHS, label='chrony-observation')
    elif args.adapter == 'ntpq':
        failures = check_crosswalk(NTPQ_CROSSWALK, path_key='ntpq_observation_path', required_paths=NTPQ_REQUIRED_PATHS, label='ntpq-observation')
    else:
        failures = check_all(ROOT)
    if failures:
        for failure in failures:
            print(f'ERROR: {failure}')
        return 1
    print('TimeSync RFC 9249 adapter-observation crosswalks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

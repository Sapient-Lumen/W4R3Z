from __future__ import annotations

from pathlib import Path

from vhk.project.runtime_state_cache import (
    compare_runtime_instance_witness,
    summarize_runtime_instance_witness_from_cache,
    write_runtime_state_cache,
)


def test_runtime_state_cache_round_trip_and_compare(tmp_path: Path) -> None:
    root = (tmp_path / 'runtime_state_cache').resolve()
    payload = {
        'pid': 2222,
        'watchers': ['hotkey'],
        'runtime_contract': {'digest': 'abc123'},
        'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
    }
    write_runtime_state_cache(project_root=root, payload=payload, xdg_runtime_dir=None)
    witness = summarize_runtime_instance_witness_from_cache(project_root=root, xdg_runtime_dir=None)
    assert witness['available'] is True
    assert witness['pid'] == 2222
    assert witness['runtime_epoch_id'] == 'epoch-a'
    assert witness['runtime_contract_digest'] == 'abc123'
    status = compare_runtime_instance_witness(witness, dict(witness))
    assert status['status'] == 'in_sync'
    assert status['in_sync'] is True


def test_runtime_state_cache_compare_detects_epoch_drift() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-b',
        'runtime_contract_digest': 'digest-1',
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_epoch_drift'
    assert status['in_sync'] is False
    assert status['epoch_changed'] is True

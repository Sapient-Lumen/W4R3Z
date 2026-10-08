from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone

from vhk.project.desktop_session_contract import summarize_desktop_session_contract
from vhk.project.runtime_state_cache import (
    compare_runtime_instance_witness,
    record_runtime_dispatch_probe_observation,
    summarize_runtime_instance_witness_from_cache,
    write_runtime_state_cache,
)


def test_runtime_state_cache_round_trip_and_compare(tmp_path: Path) -> None:
    root = (tmp_path / 'runtime_state_cache').resolve()
    payload = {
        'pid': 2222,
        'watchers': ['hotkey'],
        'runtime_contract': {'digest': 'abc123'},
        'desktop_session_contract': summarize_desktop_session_contract({
            'DISPLAY': ':1',
            'XAUTHORITY': '/tmp/xauth-a',
            'I3SOCK': '/tmp/i3-a.sock',
            'XDG_SESSION_TYPE': 'x11',
            'XDG_CURRENT_DESKTOP': 'i3',
        }),
        'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
    }
    write_runtime_state_cache(project_root=root, payload=payload, xdg_runtime_dir=None)
    witness = summarize_runtime_instance_witness_from_cache(project_root=root, xdg_runtime_dir=None)
    assert witness['available'] is True
    assert witness['pid'] == 2222
    assert witness['runtime_epoch_id'] == 'epoch-a'
    assert witness['runtime_contract_digest'] == 'abc123'
    assert witness['desktop_session_contract']['display'] == ':1'
    assert witness['desktop_session_contract_digest'] == witness['desktop_session_contract']['digest']
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



def test_runtime_state_cache_compare_detects_desktop_session_drift() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'desktop_session_contract': summarize_desktop_session_contract({
            'DISPLAY': ':1',
            'XAUTHORITY': '/tmp/xauth-new',
            'I3SOCK': '/tmp/i3-new.sock',
            'XDG_SESSION_TYPE': 'x11',
            'XDG_CURRENT_DESKTOP': 'i3',
        }),
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'desktop_session_contract': summarize_desktop_session_contract({
            'DISPLAY': ':0',
            'XAUTHORITY': '/tmp/xauth-old',
            'I3SOCK': '/tmp/i3-old.sock',
            'XDG_SESSION_TYPE': 'x11',
            'XDG_CURRENT_DESKTOP': 'i3',
        }),
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_desktop_session_drift'
    assert status['in_sync'] is False
    assert status['desktop_session_contract_changed'] is True
    assert status['desktop_session_contract']['display_changed'] is True
    assert status['desktop_session_contract']['i3sock_changed'] is True


def test_runtime_state_cache_records_dispatch_probe_observation(tmp_path: Path) -> None:
    root = (tmp_path / 'runtime_state_cache').resolve()
    write_runtime_state_cache(
        project_root=root,
        payload={
            'pid': 2222,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'abc123'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
        },
        xdg_runtime_dir=None,
    )
    record_runtime_dispatch_probe_observation(
        project_root=root,
        probe_summary={
            'status': 'ok',
            'ok': True,
            'observed_at': '2026-03-22T10:58:00Z',
            'roundtrip_latency_ms': 91.4,
            'latency_status': 'over_budget',
            'latency_budget_ms': 60.0,
            'ack_pid': 3333,
            'ack_handled_at': '2026-03-22T10:58:00Z',
            'probe_id': 'probe-123',
        },
        xdg_runtime_dir=None,
    )
    witness = summarize_runtime_instance_witness_from_cache(project_root=root, xdg_runtime_dir=None)
    assert witness['latest_dispatch_probe_status'] == 'ok'
    assert witness['latest_dispatch_probe_latency_status'] == 'over_budget'
    assert witness['latest_dispatch_probe_latency_ms'] == 91.4
    assert witness['latest_dispatch_probe_latency_budget_ms'] == 60.0
    assert witness['latest_dispatch_probe_ack_pid'] == 3333
    assert witness['latest_dispatch_probe_id'] == 'probe-123'


def test_runtime_state_cache_reports_stale_dispatch_probe_freshness(tmp_path: Path) -> None:
    root = (tmp_path / 'runtime_state_cache').resolve()
    observed_at = (datetime.now(timezone.utc) - timedelta(seconds=120)).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    write_runtime_state_cache(
        project_root=root,
        payload={
            'pid': 2222,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'abc123'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': observed_at,
                'roundtrip_latency_ms': 22.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    witness = summarize_runtime_instance_witness_from_cache(project_root=root, xdg_runtime_dir=None)
    assert witness['latest_dispatch_probe_freshness_status'] == 'stale'
    assert witness['latest_dispatch_probe_is_fresh'] is False
    assert witness['latest_dispatch_probe_age_s'] is not None
    assert witness['latest_dispatch_probe_age_s'] >= 120.0
    assert witness['latest_dispatch_probe_freshness_window_s'] == 45.0


def test_runtime_state_cache_compare_detects_probe_freshness_attention_drift() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'stale',
        'latest_dispatch_probe_latency_status': 'within_budget',
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'fresh',
        'latest_dispatch_probe_latency_status': 'within_budget',
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_probe_freshness_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_freshness_attention_changed'] is True
    assert status['current_probe_refresh_attention'] is True
    assert status['observed_probe_refresh_attention'] is False



def test_runtime_state_cache_compare_detects_probe_latency_attention_drift() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'fresh',
        'latest_dispatch_probe_latency_status': 'over_budget',
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'fresh',
        'latest_dispatch_probe_latency_status': 'within_budget',
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_probe_latency_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_latency_attention_changed'] is True
    assert status['current_probe_latency_attention'] is True
    assert status['observed_probe_latency_attention'] is False



def test_runtime_state_cache_compare_detects_probe_result_failure_drift() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ack_timeout',
        'latest_dispatch_probe_freshness_status': 'missing',
        'latest_dispatch_probe_latency_status': 'not_measured',
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'fresh',
        'latest_dispatch_probe_latency_status': 'within_budget',
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_probe_status_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_status_changed'] is True
    assert status['runtime_probe_failure_changed'] is True
    assert status['current_probe_status'] == 'ack_timeout'
    assert status['observed_probe_status'] == 'ok'


def test_runtime_state_cache_compare_detects_probe_result_variant_drift_within_failures() -> None:
    current = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'invalid_ack',
        'latest_dispatch_probe_freshness_status': 'missing',
        'latest_dispatch_probe_latency_status': 'not_measured',
    }
    observed = {
        'available': True,
        'pid': 3000,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-1',
        'latest_dispatch_probe_status': 'ack_timeout',
        'latest_dispatch_probe_freshness_status': 'missing',
        'latest_dispatch_probe_latency_status': 'not_measured',
    }
    status = compare_runtime_instance_witness(current, observed)
    assert status['status'] == 'runtime_probe_status_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_status_changed'] is True
    assert status['runtime_probe_failure_changed'] is False
    assert 'moved from ack_timeout to invalid_ack' in ' ; '.join(status['reasons'])

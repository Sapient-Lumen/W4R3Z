from __future__ import annotations

from pathlib import Path

import pytest

import chatgpt_proof_autopilot as autopilot_module
from chatgpt_proof_autopilot import run_autopilot


@pytest.fixture(autouse=True)
def _isolate_operator_state(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    latest = tmp_path / 'latest'
    monkeypatch.setattr(autopilot_module, 'LATEST', latest)
    monkeypatch.setattr(autopilot_module, 'DEFAULT_OPERATOR_STATE', latest / 'operator-state.json')


def test_autopilot_dry_run_writes_summary_and_does_not_attempt_live_steps(tmp_path: Path) -> None:
    out = tmp_path / 'autopilot.json'

    report = run_autopilot(summary_out=out)

    assert report['tool'] == 'glasstty-chatgpt-proof-autopilot'
    assert report['verdict'] in {'proof-autopilot-awaiting-operator', 'proof-autopilot-complete'}
    assert out.exists()
    attempted = {step['name']: step['attempted'] for step in report['steps']}
    assert attempted['proof-ingest'] is False
    assert attempted['proof-publish-bundle'] is False
    assert 'next_action' in report


def test_autopilot_require_complete_blocks_incomplete_live_pipeline(tmp_path: Path) -> None:
    out = tmp_path / 'autopilot.json'

    report = run_autopilot(summary_out=out, require_complete=True)

    if report['final_stage'] != 'complete':
        assert report['ok'] is False
        assert any('proof pipeline incomplete' in blocker for blocker in report['blockers'])
    else:
        assert report['ok'] is True


def test_autopilot_execute_live_without_input_is_safe_and_does_not_ingest(tmp_path: Path) -> None:
    out = tmp_path / 'autopilot.json'

    report = run_autopilot(summary_out=out, execute_live=True)

    ingest_step = next(step for step in report['steps'] if step['name'] == 'proof-ingest')
    assert ingest_step['attempted'] is False
    assert 'no --input' in ingest_step['skipped_reason'] or 'not in --execute-live' in ingest_step['skipped_reason']

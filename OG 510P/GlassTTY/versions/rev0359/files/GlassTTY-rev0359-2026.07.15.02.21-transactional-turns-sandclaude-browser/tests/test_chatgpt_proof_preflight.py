from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_preflight import build_preflight, run_preflight
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def test_build_preflight_is_ready_but_not_live(tmp_path: Path) -> None:
    surface = _surface()
    contract = build_contract(surface)
    contract_path = tmp_path / 'contract.json'
    fixture_path = tmp_path / 'fixture.json'
    contract_path.write_text(json.dumps(contract), encoding='utf-8')
    fixture_path.write_text(json.dumps(surface), encoding='utf-8')

    report = build_preflight(
        contract_path=contract_path,
        fixture_path=fixture_path,
        rehearsal_out=tmp_path / 'rehearsal.json',
        evaluation_out=tmp_path / 'eval',
    )

    assert report['ok'] is True
    assert report['live_proof'] is False
    assert report['verdict'] == 'ready-for-live-operator-attempt-not-a-live-proof'
    assert report['gates']['fixture_contract_ok'] is True
    assert report['gates']['rehearsal_harness_ok_not_live'] is True


def test_run_preflight_writes_summary(tmp_path: Path) -> None:
    surface = _surface()
    contract = build_contract(surface)
    contract_path = tmp_path / 'contract.json'
    fixture_path = tmp_path / 'fixture.json'
    out = tmp_path / 'preflight.json'
    contract_path.write_text(json.dumps(contract), encoding='utf-8')
    fixture_path.write_text(json.dumps(surface), encoding='utf-8')

    report = run_preflight(
        contract_path=contract_path,
        fixture_path=fixture_path,
        out=out,
        rehearsal_out=tmp_path / 'rehearsal.json',
        evaluation_out=tmp_path / 'eval',
    )

    assert report['ok'] is True
    assert out.exists()
    saved = json.loads(out.read_text())
    assert saved['verdict'] == 'ready-for-live-operator-attempt-not-a-live-proof'

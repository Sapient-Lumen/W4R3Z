from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_rehearsal import build_rehearsal_payload, run_rehearsal
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def test_build_rehearsal_payload_declares_not_live() -> None:
    contract = build_contract(_surface())
    payload = build_rehearsal_payload(contract=contract)

    assert payload['tool'] == 'glasstty-chatgpt-proof-rehearsal'
    assert payload['proof_mode'] == 'offline-rehearsal'
    assert payload['rehearsal_only'] is True
    assert payload['live_proof'] is False
    assert payload['actions'][1]['submit_selector'] == '#composer-submit-button'


def test_run_rehearsal_writes_payload_and_rehearsal_evaluation(tmp_path: Path) -> None:
    contract = build_contract(_surface())
    contract_path = tmp_path / 'contract.json'
    contract_path.write_text(json.dumps(contract), encoding='utf-8')
    out = tmp_path / 'rehearsal.json'
    eval_out = tmp_path / 'evaluation'

    summary = run_rehearsal(contract_path=contract_path, out=out, evaluation_out=eval_out)

    assert summary['ok'] is True
    assert summary['evaluator_verdict'] == 'rehearsal-harness-ok-not-live'
    assert out.exists()
    evaluation = json.loads((eval_out / 'chatgpt-proof-rehearsal-evaluation.json').read_text())
    assert evaluation['ok'] is False
    assert evaluation['harness_ok'] is True
    assert evaluation['rehearsal_only'] is True

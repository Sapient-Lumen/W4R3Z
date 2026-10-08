from __future__ import annotations

import json
from pathlib import Path

from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS
from chatgpt_first_proof_evaluator import evaluate_payload, iter_evidence_records
from chatgpt_proof_pack_exporter import export_pack
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def test_export_pack_materializes_thirty_slots_and_stays_not_live(tmp_path: Path) -> None:
    source = build_rehearsal_payload(contract=build_contract(_surface()))
    source['operator_transfer'] = {'recommended_json_filename': 'GlassTTY-test-capture.json'}
    source_path = tmp_path / 'rehearsal.json'
    pack_dir = tmp_path / 'pack'
    summary_path = tmp_path / 'summary.json'
    source_path.write_text(json.dumps(source), encoding='utf-8')

    summary = export_pack(source_path, pack_dir, summary_path=summary_path, clean=True)

    assert summary['ok'] is True
    assert summary['rehearsal_only'] is True
    assert summary['evaluator_verdict'] == 'rehearsal-harness-ok-not-live'
    assert summary['artifact_count'] == len(ARTIFACT_SLOTS) == 30
    for slot in ARTIFACT_SLOTS:
        assert (pack_dir / slot.filename).exists(), slot.filename
    manifest = json.loads((pack_dir / 'bundle-manifest.json').read_text())
    assert manifest['bundle_schema'] == 'chatgpt-first-proof-bundle/v1'
    assert manifest['operator_transfer']['recommended_json_filename'] == 'GlassTTY-test-capture.json'
    evaluation = json.loads((pack_dir / 'chatgpt-first-proof-evaluation.json').read_text())
    assert evaluation['harness_ok'] is True
    assert evaluation['rehearsal_only'] is True
    assert evaluation['ok'] is False


def test_evaluator_attempt_records_are_not_double_counted() -> None:
    payload = build_rehearsal_payload(contract=build_contract(_surface()))
    result = evaluate_payload(payload)
    implicit = next(attempt for attempt in result['attempts'] if attempt['attempt_id'] == payload['attempt_id'])
    expected = len([record for record in iter_evidence_records(payload) if record.attempt_id == payload['attempt_id']])

    assert implicit['observed']['record_count'] == expected

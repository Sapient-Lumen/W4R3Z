from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from chatgpt_proof_transfer_audit import audit_transfer
from test_chatgpt_proof_attempt_audit import _ordered_capture
from test_chatgpt_proof_ingest import _png_data_url


def _capture() -> dict[str, Any]:
    capture = _ordered_capture()
    rows = capture['actions']
    raw = []
    for row in rows:
        raw.append({
            'version': '0.1',
            'request_id': f'req-{row["sequence_index"]}',
            'type': row['type'],
            'timestamp': '2026-06-13T00:00:00Z',
            'payload': row['payload'],
        })
    for row in rows:
        row['attempt_id'] = 'attempt-1'
        row['payload']['attempt_id'] = 'attempt-1'
    capture.update({
        'attempt_id': 'attempt-1',
        'raw_envelopes': raw,
        'visible_tab_screenshot_data_url': _png_data_url(),
        'operator_transfer': {'recommended_json_filename': 'proof.json'},
    })
    return capture


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_transfer_audit_accepts_downloaded_ready_capture(tmp_path: Path) -> None:
    path = tmp_path / 'proof.json'
    _write(path, _capture())

    report = audit_transfer(
        path,
        summary_out=None,
        require_ready_to_download=True,
        require_full_screenshot=True,
    )

    assert report['ok'] is True
    assert report['verdict'] == 'proof-transfer-audit-ok'
    assert report['observed']['actions_count'] == report['observed']['raw_envelopes_count']
    assert report['observed']['screenshot']['valid_png_data_url'] is True


def test_transfer_audit_blocks_mismatched_envelope_order(tmp_path: Path) -> None:
    capture = _capture()
    capture['raw_envelopes'][4]['type'] = 'transcript.latest'
    path = tmp_path / 'proof.json'
    _write(path, capture)

    report = audit_transfer(path, summary_out=None, require_ready_to_download=True)

    assert report['ok'] is False
    assert any('type order differ' in blocker for blocker in report['blockers'])


def test_transfer_audit_blocks_recovery_preview_when_proof_capture_required(tmp_path: Path) -> None:
    path = tmp_path / 'vault.json'
    _write(path, {
        'schema_version': 1,
        'storage_key': 'glasstty.chatgpt.firstProof.recoveryVault.v1',
        'saved_full_document': False,
        'redacted_preview': {'attempt_id': 'attempt-1'},
    })

    report = audit_transfer(path, summary_out=None)

    assert report['ok'] is False
    assert any('not proof-capture-json' in blocker for blocker in report['blockers'])
    assert report['recommendations']

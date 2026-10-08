from __future__ import annotations

from typing import Any

from chatgpt_proof_attempt_audit import EXPECTED_REPLY, PROBE_TEXT, audit_attempt
from test_chatgpt_proof_ingest import _png_data_url


def _row(kind: str, payload: dict[str, Any], idx: int) -> dict[str, Any]:
    return {
        'type': kind,
        'request_type': kind,
        'response_type': kind,
        'sequence_index': idx,
        'ok': payload.get('ok', True),
        'payload': {'ok': payload.get('ok', True), **payload},
    }


def _ordered_capture() -> dict[str, Any]:
    rows = [
        _row('proof.operator_readiness', {
            'ok': False,
            'verdict': 'proof-attempt-not-ready',
            'next_stage': 'write-checkpoint',
        }, 0),
        _row('prompt.write', {
            'readback': PROBE_TEXT,
        }, 1),
        _row('fixture.capture', {
            'proof_live_gate_ok': True,
            'proof_live_gate_verdict': 'proof-live-gate-ok',
            'proof_live_gate_observed': {
                'submit_selector': '#composer-submit-button',
                'blocked_composer_control_disqualified': True,
            },
        }, 2),
        _row('proof.surface_screenshot', {
            'visible_tab_screenshot_data_url': _png_data_url(),
        }, 3),
        _row('prompt.submit', {
            'composer_readback_before_submit': PROBE_TEXT,
            'proof_live_gate_ok': True,
            'proof_live_gate_verdict': 'proof-live-gate-ok',
        }, 4),
        _row('transcript.latest', {
            'text': EXPECTED_REPLY,
            'latest_user_turn_witness': {'text': PROBE_TEXT},
        }, 5),
        _row('proof.operator_readiness', {
            'ok': True,
            'verdict': 'proof-attempt-ready-to-download',
            'next_stage': 'download-proof-json',
            'checks': {
                'checkpoint_write_readback': True,
                'live_gate_ok': True,
                'visible_screenshot_captured': True,
                'submit_readback_exact_probe': True,
                'latest_reply_exact_checkpoint': True,
                'latest_user_turn_exact_prompt': True,
            },
        }, 6),
    ]
    return {'schema_version': 1, 'surface_key': 'chatgpt', 'actions': rows}


def test_attempt_audit_accepts_ordered_ready_to_download_capture() -> None:
    report = audit_attempt(_ordered_capture(), require_ready_to_download=True)

    assert report['ok'] is True
    assert report['verdict'] == 'proof-attempt-audit-ok'
    assert report['indices']['final_ready_to_download'] == 6
    assert report['blockers'] == []


def test_attempt_audit_blocks_submit_before_screenshot() -> None:
    capture = _ordered_capture()
    rows = capture['actions']
    rows[3], rows[4] = rows[4], rows[3]

    report = audit_attempt(capture, require_ready_to_download=True)

    assert report['ok'] is False
    assert report['verdict'] == 'proof-attempt-audit-blocked'
    assert any('visible screenshot must occur before prompt.submit' in blocker for blocker in report['blockers'])


def test_attempt_audit_requires_final_ready_when_requested() -> None:
    capture = _ordered_capture()
    capture['actions'] = capture['actions'][:-1]

    report = audit_attempt(capture, require_ready_to_download=True)

    assert report['ok'] is False
    assert any('final proof.operator_readiness' in blocker for blocker in report['blockers'])

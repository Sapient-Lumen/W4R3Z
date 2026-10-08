from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sidepanel_proof_submit_is_live_gate_guarded() -> None:
    source = (ROOT / 'extension' / 'src' / 'sidepanel' / 'main.ts').read_text(encoding='utf-8')
    html = (ROOT / 'extension' / 'sidepanel' / 'index.html').read_text(encoding='utf-8')

    assert 'proof-live-gate-check' in html
    assert 'proof-live-gate-status' in html
    assert 'proof-capture-screenshot' in html
    assert 'proof-copy-json' in html
    assert 'proof-download-json' in html
    assert 'proof-download-screenshot' in html
    assert 'proof-transfer-status' in html
    assert 'Submit checkpoint (gated)' in html
    assert 'Generic submit (not proof)' in html
    assert 'PROOF_LIVE_GATE_EXPECTED' in source
    assert "send_selector: '#composer-submit-button'" in source
    assert "send_testid: 'send-button'" in source
    assert "send_aria_label: 'Send prompt'" in source
    assert "blocked_non_send_selector: '#composer-plus-btn'" in source
    assert 'fixturePayloadToLiveGateVerdict' in source
    assert 'runProofLiveGate' in source
    assert 'guardedProofSubmit' in source
    assert 'captureVisibleProofScreenshot' in source
    assert 'chrome.tabs.captureVisibleTab' in source
    assert "type: 'proof.surface_screenshot'" in source
    assert 'visible_tab_screenshot_data_url' in source
    assert 'copyProofCaptureJson' in source
    assert 'downloadProofCaptureJson' in source
    assert 'downloadProofScreenshotPng' in source
    assert 'triggerBlobDownload' in source
    assert 'operator_transfer' in source
    assert 'redactLargeProofValuesForDisplay' in source
    assert "visible_tab_screenshot_data_url: '[embedded in root visible_tab_screenshot_data_url]'" in source
    assert "document.getElementById('proof-submit')?.addEventListener('click', () => void guardedProofSubmit()" in source
    assert "proofWriteReadbackSeen()" in source
    assert 'checkpoint write/readback evidence is missing' in source
    assert "proof_live_gate_verdict: verdict.verdict" in source
    assert "proof_live_gate_ok: verdict.ok" in source
    assert "proof_live_gate_ok_seen" in source
    assert "proof_live_gate_verdicts" in source


def test_evaluator_requires_sidepanel_live_gate_for_reviewable_live_proof() -> None:
    evaluator = (ROOT / 'scripts' / 'chatgpt_first_proof_evaluator.py').read_text(encoding='utf-8')
    rehearsal = (ROOT / 'scripts' / 'chatgpt_proof_rehearsal.py').read_text(encoding='utf-8')

    assert "'proof_live_gate_ok_before_submit'" in evaluator
    assert 'proof_live_gate_ok_submit_records' in evaluator
    assert "first_container_value(record.item, 'proof_live_gate_ok')" in evaluator
    assert "proof_live_gate_verdict'" in evaluator
    assert "'proof_live_gate_verdict': 'proof-live-gate-ok'" in rehearsal
    assert "'proof_live_gate_ok': True" in rehearsal

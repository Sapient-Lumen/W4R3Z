from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sidepanel_has_attempt_readiness_operator_gate() -> None:
    html = (ROOT / 'extension' / 'sidepanel' / 'index.html').read_text(encoding='utf-8')
    source = (ROOT / 'extension' / 'src' / 'sidepanel' / 'main.ts').read_text(encoding='utf-8')
    protocol = (ROOT / 'extension' / 'src' / 'shared' / 'protocol.ts').read_text(encoding='utf-8')

    assert 'proof-attempt-readiness' in html
    assert 'Run attempt readiness' in html
    assert 'proof-attempt-readiness-status' in html
    assert 'Attempt readiness not checked yet.' in html

    assert 'ProofAttemptReadinessReport' in source
    assert 'runProofAttemptReadiness' in source
    assert "makeEnvelope('proof.operator_readiness'" in source
    assert 'proof-attempt-ready-to-download' in source
    assert 'proof-attempt-not-ready' in source
    assert 'active_tab_matches_target' in source
    assert 'checkpoint_write_readback' in source
    assert 'visible_screenshot_captured' in source
    assert 'submit_readback_exact_probe' in source
    assert 'latest_reply_exact_checkpoint' in source
    assert 'latest_user_turn_exact_prompt' in source
    assert 'Download proof JSON' in source
    assert "'proof.operator_readiness'" in protocol

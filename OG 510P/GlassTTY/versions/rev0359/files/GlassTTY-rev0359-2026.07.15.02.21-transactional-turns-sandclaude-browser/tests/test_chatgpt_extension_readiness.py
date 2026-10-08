from __future__ import annotations

from pathlib import Path

from chatgpt_extension_readiness import check_extension_readiness

ROOT = Path(__file__).resolve().parents[1]


def test_extension_readiness_checks_chatgpt_only_manifest_and_sidepanel_markers(tmp_path: Path) -> None:
    summary_path = tmp_path / 'summary.json'
    report = check_extension_readiness(ROOT, require_build=False, summary_path=summary_path)

    assert report['ok'] is True
    assert report['verdict'] == 'extension-readiness-ok'
    assert report['manifest']['host_permissions'] == ['https://chatgpt.com/*']
    assert report['manifest']['content_matches'] == ['https://chatgpt.com/*']
    assert report['sidepanel']['required_buttons']['proof-attempt-readiness'] is True
    assert report['sidepanel']['source_markers']['attempt_readiness_function'] is True
    assert report['sidepanel']['source_markers']['download_proof_json_readiness_gate'] is True
    assert report['sidepanel']['source_markers']['download_proof_json_attempt_audit_handoff'] is True
    assert report['sidepanel']['source_markers']['proof_operator_readiness_message_type'] is True
    assert summary_path.exists()


def test_extension_readiness_blocks_non_chatgpt_host_permissions(tmp_path: Path) -> None:
    root = tmp_path / 'repo'
    (root / 'extension' / 'sidepanel').mkdir(parents=True)
    (root / 'extension' / 'src' / 'sidepanel').mkdir(parents=True)
    (root / 'extension' / 'src' / 'shared').mkdir(parents=True)
    (root / 'extension' / 'manifest.json').write_text('''{
      "manifest_version": 3,
      "name": "bad",
      "version": "1.0.0",
      "permissions": ["storage", "tabs", "sidePanel", "scripting", "webNavigation"],
      "host_permissions": ["https://chatgpt.com/*", "https://example.com/*"],
      "side_panel": {"default_path": "sidepanel/index.html"},
      "content_scripts": [{"matches": ["https://chatgpt.com/*"], "js": ["dist/content/main.js"]}]
    }''', encoding='utf-8')
    (root / 'extension' / 'package.json').write_text('{"version":"1.0.0"}', encoding='utf-8')
    (root / 'extension' / 'sidepanel' / 'index.html').write_text(' '.join([
        'proof-attempt-readiness', 'proof-write-capture', 'proof-live-gate-check',
        'proof-capture-screenshot', 'proof-submit', 'proof-read-latest',
        'proof-download-json', 'proof-save-vault', 'proof-restore-vault', 'proof-download-vault',
    ]), encoding='utf-8')
    (root / 'extension' / 'src' / 'sidepanel' / 'main.ts').write_text(' '.join([
        'PROOF_LIVE_GATE_EXPECTED', 'runProofAttemptReadiness',
        'glasstty.chatgpt.firstProof.recoveryVault.v1', 'downloadProofCaptureJson',
        'captureVisibleProofScreenshot',
        'Proof capture JSON download blocked by attempt readiness.', 'proof-attempt-audit --input',
    ]), encoding='utf-8')
    (root / 'extension' / 'src' / 'shared' / 'protocol.ts').write_text("'proof.operator_readiness'", encoding='utf-8')

    report = check_extension_readiness(root)

    assert report['ok'] is False
    assert report['verdict'] == 'extension-readiness-blocked'
    assert any('host_permissions' in blocker for blocker in report['blockers'])

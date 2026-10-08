from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_refresh_truth_surfaces_rebuilds_current_root_register() -> None:
    payload = json.loads(
        subprocess.check_output(
            [sys.executable, str(ROOT / 'scripts' / 'refresh-truth-surfaces.py')],
            text=True,
        )
    )
    assert payload['project'] == 'GlassTTY'
    assert payload['truth_surface_counts']['families_whose_latest_head_points_at_foreign_root'] == 0
    assert payload['truth_surface_counts']['families_without_current_root_capture'] == 0
    register_path = ROOT / 'validation' / 'latest' / 'truth-surface-register' / 'truth-surface-register.json'
    assert register_path.exists()
    register = json.loads(register_path.read_text(encoding='utf-8'))
    assert register['counts']['families_whose_latest_head_points_at_foreign_root'] == 0
    assert register['counts']['families_without_capture_history'] == 0
    assert (ROOT / 'validation' / 'latest' / 'support-publish-gate' / 'support-publish-gate.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'support-source-baseline' / 'support-source-baseline.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-kit' / 'chatgpt-first-proof-kit.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-posture-matrix' / 'chatgpt-posture-matrix.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-branch-guard' / 'chatgpt-branch-guard.json').exists()
    assert (ROOT / 'CHATGPT-FIRST-PROOF-KIT.json').exists()
    assert (ROOT / 'CHATGPT-POSTURE-MATRIX.json').exists()
    assert (ROOT / 'CHATGPT-BRANCH-GUARD.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-composer-witness-receipt' / 'chatgpt-composer-witness-receipt.json').exists()
    assert (ROOT / 'CHATGPT-COMPOSER-WITNESS-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-submit-witness-receipt' / 'chatgpt-submit-witness-receipt.json').exists()
    assert (ROOT / 'CHATGPT-SUBMIT-WITNESS-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-proof-bundle-receipt' / 'chatgpt-proof-bundle-receipt.json').exists()
    assert (ROOT / 'CHATGPT-PROOF-BUNDLE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-promotion-stability-receipt' / 'chatgpt-promotion-stability-receipt.json').exists()
    assert (ROOT / 'CHATGPT-PROMOTION-STABILITY-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-support-claim-receipt' / 'chatgpt-support-claim-receipt.json').exists()
    assert (ROOT / 'CHATGPT-SUPPORT-CLAIM-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-capability-profile-receipt' / 'chatgpt-capability-profile-receipt.json').exists()
    assert (ROOT / 'CHATGPT-CAPABILITY-PROFILE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-auth-workspace-receipt' / 'chatgpt-auth-workspace-receipt.json').exists()
    assert (ROOT / 'CHATGPT-AUTH-WORKSPACE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-plan-envelope-receipt' / 'chatgpt-plan-envelope-receipt.json').exists()
    assert (ROOT / 'CHATGPT-PLAN-ENVELOPE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-browser-envelope-receipt' / 'chatgpt-browser-envelope-receipt.json').exists()
    assert (ROOT / 'CHATGPT-BROWSER-ENVELOPE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-retention-envelope-receipt' / 'chatgpt-retention-envelope-receipt.json').exists()
    assert (ROOT / 'CHATGPT-RETENTION-ENVELOPE-RECEIPT.json').exists()
    assert (ROOT / 'validation' / 'latest' / 'chatgpt-platform-envelope-receipt' / 'chatgpt-platform-envelope-receipt.json').exists()
    assert (ROOT / 'CHATGPT-PLATFORM-ENVELOPE-RECEIPT.json').exists()
    assert (ROOT / 'docs' / 'support-bundles' / 'candidate' / 'chatgpt-routefirst-chromium-live-candidate.json').exists()
    assert (ROOT / 'SUPPORT-PUBLISH-GATE.json').exists()
    assert (ROOT / 'SUPPORT-SOURCE-BASELINE.json').exists()

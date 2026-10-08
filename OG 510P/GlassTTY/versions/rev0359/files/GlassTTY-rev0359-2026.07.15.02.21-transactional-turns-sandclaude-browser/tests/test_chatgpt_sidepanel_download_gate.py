from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_download_proof_json_is_attempt_readiness_gated() -> None:
    source = (ROOT / 'extension' / 'src' / 'sidepanel' / 'main.ts').read_text(encoding='utf-8')

    assert 'async function downloadProofCaptureJson(): Promise<void>' in source
    assert 'const readiness = await runProofAttemptReadiness();' in source
    assert 'Proof capture JSON download blocked by attempt readiness.' in source
    assert 'proof-attempt-audit --input' in source
    assert 'download_gate' in source

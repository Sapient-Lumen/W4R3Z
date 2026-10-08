from __future__ import annotations

import json
from pathlib import Path

import pytest

import chatgpt_proof_finalize_pack as finalize_module
from chatgpt_proof_finalize_pack import finalize_pack
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


@pytest.fixture(autouse=True)
def _isolate_integrity_summary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(finalize_module, 'ROOT', tmp_path)


def _write_rehearsal(tmp_path: Path) -> Path:
    source = build_rehearsal_payload(contract=build_contract(_surface()))
    source_path = tmp_path / 'rehearsal.json'
    source_path.write_text(json.dumps(source), encoding='utf-8')
    return source_path


def test_finalize_pack_exports_checks_and_writes_handoff(tmp_path: Path) -> None:
    source_path = _write_rehearsal(tmp_path)
    pack_dir = tmp_path / 'pack'

    report = finalize_pack(
        source_path,
        pack_dir,
        final_summary_path=tmp_path / 'final.json',
        export_summary_path=tmp_path / 'export.json',
        check_summary_path=tmp_path / 'check.json',
        clean=True,
    )

    assert report['ok'] is True
    assert report['verdict'] == 'rehearsal-proof-pack-finalized-not-live'
    assert report['check']['verdict'] == 'rehearsal-evidence-pack-check-ok-not-live'
    assert (pack_dir / 'operator-handoff.json').exists()
    assert (pack_dir / 'OPERATOR-HANDOFF.md').exists()
    assert (pack_dir / 'privacy-redaction-review.json').exists()
    assert report['privacy_review']['verdict'] == 'privacy-review-rehearsal-not-live'
    handoff = json.loads((pack_dir / 'operator-handoff.json').read_text())
    assert handoff['verdict'] == report['verdict']


def test_finalize_pack_require_live_blocks_rehearsal_with_actions(tmp_path: Path) -> None:
    source_path = _write_rehearsal(tmp_path)
    pack_dir = tmp_path / 'pack'

    report = finalize_pack(
        source_path,
        pack_dir,
        final_summary_path=tmp_path / 'final.json',
        export_summary_path=tmp_path / 'export.json',
        check_summary_path=tmp_path / 'check.json',
        clean=True,
        require_live=True,
    )

    assert report['ok'] is False
    assert report['verdict'] == 'proof-pack-finalization-blocked'
    assert any('rehearsal_only=true' in blocker for blocker in report['blockers'])
    assert report['blocker_actions']
    assert any('live-sidepanel-proof.json' in action['command_hint'] for action in report['blocker_actions'])


def test_finalize_pack_can_require_privacy_pass_and_block(tmp_path: Path) -> None:
    source_path = _write_rehearsal(tmp_path)
    pack_dir = tmp_path / 'pack'

    report = finalize_pack(
        source_path,
        pack_dir,
        final_summary_path=tmp_path / 'final.json',
        export_summary_path=tmp_path / 'export.json',
        check_summary_path=tmp_path / 'check.json',
        clean=True,
        require_privacy_pass=True,
    )

    assert report['ok'] is False
    assert report['verdict'] == 'proof-pack-finalization-blocked'
    assert any('privacy' in blocker.lower() for blocker in report['blockers'])

from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_pack_check import check_pack
from chatgpt_proof_pack_exporter import export_pack
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def _export_rehearsal_pack(tmp_path: Path) -> Path:
    source = build_rehearsal_payload(contract=build_contract(_surface()))
    source_path = tmp_path / 'rehearsal.json'
    source_path.write_text(json.dumps(source), encoding='utf-8')
    pack_dir = tmp_path / 'pack'
    export_pack(source_path, pack_dir, summary_path=tmp_path / 'export-summary.json', clean=True)
    return pack_dir


def test_check_pack_accepts_complete_rehearsal_but_marks_not_live(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)

    report = check_pack(pack_dir, summary_path=tmp_path / 'check-summary.json')

    assert report['ok'] is True
    assert report['verdict'] == 'rehearsal-evidence-pack-check-ok-not-live'
    assert report['complete_artifact_set'] is True
    assert report['present_artifact_count'] == report['expected_artifact_count'] == 30
    assert report['manifest']['rehearsal_only'] is True
    assert report['screenshot']['placeholder_not_live'] is True
    assert report['evaluation']['verdict'] == 'rehearsal-harness-ok-not-live'
    assert report['privacy_review']['markdown_exists'] is True


def test_check_pack_require_live_blocks_rehearsal_placeholder(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)

    report = check_pack(pack_dir, summary_path=tmp_path / 'check-summary.json', require_live=True)

    assert report['ok'] is False
    assert report['verdict'] == 'evidence-pack-check-blocked'
    assert any('rehearsal_only=true' in blocker for blocker in report['blockers'])
    assert any('placeholder' in blocker for blocker in report['blockers'])


def test_check_pack_blocks_missing_slot(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)
    (pack_dir / 'assistant-output-witness.json').unlink()

    report = check_pack(pack_dir, summary_path=tmp_path / 'check-summary.json')

    assert report['ok'] is False
    assert 'assistant-output-witness.json' in report['missing_artifacts']


def test_check_pack_can_require_privacy_pass(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)

    report = check_pack(pack_dir, summary_path=tmp_path / 'check-summary.json', require_privacy_pass=True)

    assert report['ok'] is False
    assert any('require-privacy-pass' in blocker for blocker in report['blockers'])

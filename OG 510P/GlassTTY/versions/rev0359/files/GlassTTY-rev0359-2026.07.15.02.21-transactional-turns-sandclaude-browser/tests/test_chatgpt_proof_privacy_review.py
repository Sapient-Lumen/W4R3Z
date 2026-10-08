from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_pack_exporter import export_pack
from chatgpt_proof_privacy_review import build_privacy_review
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def _export_rehearsal_pack(tmp_path: Path) -> Path:
    payload = build_rehearsal_payload(contract=build_contract(_surface()))
    source_path = tmp_path / 'rehearsal.json'
    source_path.write_text(json.dumps(payload), encoding='utf-8')
    pack_dir = tmp_path / 'pack'
    export_pack(source_path, pack_dir, summary_path=tmp_path / 'export-summary.json', clean=True)
    return pack_dir


def test_privacy_review_marks_rehearsal_not_live_and_writes_json_and_md(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)
    json_out = tmp_path / 'privacy.json'
    md_out = pack_dir / 'privacy-redaction-review.md'

    report = build_privacy_review(pack_dir, json_out=json_out, markdown_out=md_out)

    assert report['ok'] is True
    assert report['verdict'] == 'privacy-review-rehearsal-not-live'
    assert report['manifest']['rehearsal_only'] is True
    assert json_out.exists()
    assert md_out.exists()
    assert 'privacy-review-rehearsal-not-live' in md_out.read_text(encoding='utf-8')


def test_privacy_review_require_live_blocks_rehearsal(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)

    report = build_privacy_review(pack_dir, json_out=tmp_path / 'privacy.json', require_live=True)

    assert report['ok'] is False
    assert report['verdict'] == 'privacy-review-blocked'
    assert any('rehearsal_only=true' in blocker for blocker in report['blockers'])


def test_privacy_review_require_pass_needs_complete_human_attestation(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)

    report = build_privacy_review(pack_dir, json_out=tmp_path / 'privacy.json', require_pass=True)

    assert report['ok'] is False
    assert any('human privacy attestation is incomplete' in blocker for blocker in report['blockers'])

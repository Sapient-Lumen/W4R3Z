from __future__ import annotations

import json
from pathlib import Path

from chatgpt_proof_pack_exporter import export_pack
from chatgpt_proof_publish_bundle import publish_bundle
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


def test_publish_bundle_blocks_rehearsal_by_default(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)
    out_zip = tmp_path / 'publish.zip'

    report = publish_bundle(pack_dir, out_zip, summary_path=tmp_path / 'publish-summary.json')

    assert report['ok'] is False
    assert report['verdict'] == 'proof-publish-bundle-blocked'
    assert report['zip_created'] is False
    assert not out_zip.exists()
    assert any('require-live' in blocker for blocker in report['blockers'])


def test_publish_bundle_diagnostic_mode_still_blocks_without_privacy_pass(tmp_path: Path) -> None:
    pack_dir = _export_rehearsal_pack(tmp_path)
    out_zip = tmp_path / 'publish.zip'

    report = publish_bundle(
        pack_dir,
        out_zip,
        summary_path=tmp_path / 'publish-summary.json',
        require_live=False,
        require_privacy_pass=True,
    )

    assert report['ok'] is False
    assert report['verdict'] == 'proof-publish-bundle-blocked'
    assert not out_zip.exists()
    assert any('privacy review verdict' in blocker.lower() for blocker in report['blockers'])

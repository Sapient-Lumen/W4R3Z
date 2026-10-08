from __future__ import annotations

import json
import struct
import zipfile
import zlib
from pathlib import Path

from chatgpt_first_proof_evaluator import REVIEWABLE_VERDICT
from chatgpt_proof_pack_exporter import export_pack
from chatgpt_proof_publish_bundle import publish_bundle
from chatgpt_proof_publish_verify import verify_publish_bundle
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def _png(width: int = 2, height: int = 2) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

    raw = b''.join(b'\x00' + (b'\x00\xff\x00\xff' * width) for _ in range(height))
    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw))
        + chunk(b'IEND', b'')
    )


def _export_live_like_pack(tmp_path: Path) -> Path:
    payload = build_rehearsal_payload(contract=build_contract(_surface()))
    source_path = tmp_path / 'capture.json'
    source_path.write_text(json.dumps(payload), encoding='utf-8')
    pack_dir = tmp_path / 'pack'
    export_pack(source_path, pack_dir, summary_path=tmp_path / 'export-summary.json', clean=True)

    manifest_path = pack_dir / 'bundle-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['rehearsal_only'] = False
    manifest['proof_mode'] = 'live'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    evaluation_path = pack_dir / 'chatgpt-first-proof-evaluation.json'
    evaluation = json.loads(evaluation_path.read_text(encoding='utf-8'))
    evaluation['verdict'] = REVIEWABLE_VERDICT
    evaluation['harness_ok'] = True
    evaluation['payload_declares_rehearsal'] = False
    evaluation_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    (pack_dir / 'surface-screenshot.png').write_bytes(_png())
    screenshot_meta_path = pack_dir / 'surface-screenshot.metadata.json'
    screenshot_meta = json.loads(screenshot_meta_path.read_text(encoding='utf-8'))
    screenshot_meta['placeholder_not_live'] = False
    screenshot_meta['source'] = 'sidepanel-visible-tab-capture'
    screenshot_meta_path.write_text(json.dumps(screenshot_meta, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    privacy = {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-proof-privacy-review',
        'ok': True,
        'verdict': 'privacy-review-pass',
        'human_attestation_complete': True,
        'publishable_without_additional_redaction': True,
    }
    (pack_dir / 'privacy-redaction-review.json').write_text(json.dumps(privacy, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (pack_dir / 'privacy-redaction-review.md').write_text('# Privacy redaction review\n\n- verdict: `privacy-review-pass`\n', encoding='utf-8')
    return pack_dir


def test_publish_verify_accepts_ready_publish_zip(tmp_path: Path) -> None:
    pack_dir = _export_live_like_pack(tmp_path)
    out_zip = tmp_path / 'publish.zip'

    publish = publish_bundle(pack_dir, out_zip, summary_path=tmp_path / 'publish-summary.json')
    assert publish['ok'] is True
    assert out_zip.exists()

    report = verify_publish_bundle(out_zip, summary_path=tmp_path / 'verify-summary.json')

    assert report['ok'] is True
    assert report['verdict'] == 'proof-publish-verify-ok'
    assert report['manifest_check']['ok'] is True
    assert report['pack_check']['verdict'] == 'live-evidence-pack-review-ready'


def test_publish_verify_detects_tampered_manifest_file(tmp_path: Path) -> None:
    pack_dir = _export_live_like_pack(tmp_path)
    out_zip = tmp_path / 'publish.zip'
    publish_bundle(pack_dir, out_zip, summary_path=tmp_path / 'publish-summary.json')
    tampered = tmp_path / 'tampered.zip'

    with zipfile.ZipFile(out_zip, 'r') as src, zipfile.ZipFile(tampered, 'w', compression=zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == 'chatgpt-proof-evidence-pack/probe-prompt.txt':
                data = b'NOT THE CHECKPOINT\n'
            dst.writestr(info, data)

    report = verify_publish_bundle(tampered, summary_path=tmp_path / 'verify-summary.json')

    assert report['ok'] is False
    assert report['verdict'] == 'proof-publish-verify-blocked'
    assert any('manifest sha256 mismatch' in blocker for blocker in report['blockers'])


def test_publish_verify_blocks_missing_zip(tmp_path: Path) -> None:
    report = verify_publish_bundle(tmp_path / 'missing.zip', summary_path=tmp_path / 'verify-summary.json')

    assert report['ok'] is False
    assert report['verdict'] == 'proof-publish-verify-blocked'
    assert any('missing' in blocker for blocker in report['blockers'])

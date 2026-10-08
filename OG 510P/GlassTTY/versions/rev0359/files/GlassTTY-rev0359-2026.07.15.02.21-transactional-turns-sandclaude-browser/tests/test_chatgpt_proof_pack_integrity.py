from __future__ import annotations

import json
from pathlib import Path

from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS, build_artifact_ledger
from chatgpt_proof_pack_integrity import INTEGRITY_FILENAME, build_pack_integrity


def _write_slot(path: Path, artifact_type: str, index: int) -> None:
    if artifact_type == 'json':
        path.write_text(json.dumps({'attempt_id': 'attempt-1', 'slot': index}) + '\n', encoding='utf-8')
    elif artifact_type == 'image':
        # Minimal PNG signature plus bytes is enough for integrity hashing; image validity is checked elsewhere.
        path.write_bytes(b'\x89PNG\r\n\x1a\nslot-' + str(index).encode())
    else:
        path.write_text(f'attempt-1 slot {index}\n', encoding='utf-8')


def _pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / 'pack'
    pack_dir.mkdir()
    for slot in ARTIFACT_SLOTS:
        _write_slot(pack_dir / slot.filename, slot.artifact_type, slot.order)
    ledger = build_artifact_ledger(pack_dir, readiness_level='publication-review-ready')
    (pack_dir / 'artifact-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
    return pack_dir


def test_pack_integrity_writes_and_verifies_manifest(tmp_path: Path) -> None:
    pack_dir = _pack(tmp_path)

    report = build_pack_integrity(pack_dir, summary_path=None, write_pack_file=True, refresh_ledger=True)
    assert report['ok'] is True
    assert (pack_dir / INTEGRITY_FILENAME).exists()

    verify = build_pack_integrity(pack_dir, summary_path=None, require_existing_match=True)
    assert verify['ok'] is True
    assert verify['existing_integrity_check']['inventory_matches_current'] is True


def test_pack_integrity_detects_stale_artifact_ledger(tmp_path: Path) -> None:
    pack_dir = _pack(tmp_path)
    (pack_dir / 'privacy-redaction-review.md').write_text('changed after ledger\n', encoding='utf-8')

    report = build_pack_integrity(pack_dir, summary_path=None)
    assert report['ok'] is False
    assert any('artifact-ledger.json is stale' in blocker for blocker in report['blockers'])
    stale_names = {row['filename'] for row in report['artifact_ledger_check']['stale_rows']}
    assert 'privacy-redaction-review.md' in stale_names

    fixed = build_pack_integrity(pack_dir, summary_path=None, write_pack_file=True, refresh_ledger=True)
    assert fixed['ok'] is True


def test_pack_integrity_detects_changed_pack_after_manifest_written(tmp_path: Path) -> None:
    pack_dir = _pack(tmp_path)
    build_pack_integrity(pack_dir, summary_path=None, write_pack_file=True, refresh_ledger=True)
    (pack_dir / 'composer-after.txt').write_text('changed after integrity\n', encoding='utf-8')

    report = build_pack_integrity(pack_dir, summary_path=None, require_existing_match=True)
    assert report['ok'] is False
    assert any(INTEGRITY_FILENAME in blocker for blocker in report['blockers'])

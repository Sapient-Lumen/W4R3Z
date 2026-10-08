from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('archive_audit_script', ROOT / 'scripts' / 'archive-audit.py')
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

build_report = MODULE.build_report


def test_archive_audit_surfaces_redundant_validation_blobs_and_duplicates(tmp_path: Path) -> None:
    (tmp_path / 'validation' / 'rev9999-focused').mkdir(parents=True)
    (tmp_path / 'validation' / 'rev9999-focused' / 'package-check.zip').write_bytes(b'zip-bytes')
    (tmp_path / 'validation' / 'rev9999-focused' / 'diff-vs-prev.patch').write_text('patch\n', encoding='utf-8')
    (tmp_path / 'docs').mkdir()
    blob = b'same-content'
    (tmp_path / 'docs' / 'a.txt').write_bytes(blob)
    (tmp_path / 'docs' / 'b.txt').write_bytes(blob)

    report = build_report(tmp_path)

    redundant_paths = {row['path'] for row in report['redundant_validation_candidates']}
    assert 'validation/rev9999-focused/package-check.zip' in redundant_paths
    assert 'validation/rev9999-focused/diff-vs-prev.patch' in redundant_paths
    assert report['duplicate_groups']
    assert report['duplicate_groups'][0]['duplicate_count'] == 2


def test_archive_audit_flags_manifest_identity_drift(tmp_path: Path) -> None:
    root = tmp_path / 'GlassTTY-rev0072-2026.03.16.23.59-profilepreflight-nativehostledger-browseranchor-curlew'
    root.mkdir()
    (root / 'ARCHIVE_MANIFEST.json').write_text(
        '{"archive_name": "GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing", "archive_revision": 71, "archive_created_at_from_name": "2026.03.16.23.29", "archive_slug": "nativehostaudit-autotarget-browserfit-lapwing"}\n',
        encoding='utf-8',
    )

    report = build_report(root)

    assert report['identity']['ok'] is False
    assert report['identity']['issues']
    assert any('archive_name' in issue for issue in report['identity']['issues'])

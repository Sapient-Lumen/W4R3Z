from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('check_revision_receipt', ROOT / 'scripts' / 'check_revision_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_revision_receipt_conformance = MODULE.build_revision_receipt_conformance
write_root_conformance = MODULE.write_root_conformance


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_build_revision_receipt_conformance_matches_manifest_and_truth_counts(tmp_path: Path) -> None:
    root = tmp_path
    _write_json(root / 'ARCHIVE_MANIFEST.json', {
        'project': 'GlassTTY',
        'archive_name': 'GlassTTY-rev0127-example.zip',
        'archive_revision': 127,
        'codename': 'tern',
        'summary': 'revisionreceipt-warningledger-artifactbuckets',
        'base_archive': 'GlassTTY-rev0126-example.zip',
    })
    _write_json(root / 'validation' / 'opening-surface-captures.json', {'captures': []})
    _write_json(root / 'validation' / 'readiness-report-captures.json', {'entries': []})
    _write_json(root / 'validation' / 'control-plane-report-captures.json', {'captures': []})
    _write_json(root / 'validation' / 'install-receipts.json', {'captures': []})
    _write_json(root / 'validation' / 'support-surface-captures.json', {'captures': []})
    _write_json(root / 'validation' / 'operator-handoff-captures.json', {'entries': []})
    _write_json(root / 'validation' / 'support-source-baseline-captures.json', {'captures': []})
    counts = {
        'families_without_capture_history': 7,
        'families_whose_latest_head_points_at_foreign_root': 0,
        'families_without_current_root_capture': 0,
        'families_without_citation_head': 0,
    }
    _write_json(root / 'REVISION-RECEIPT.json', {
        'project': 'GlassTTY',
        'revision': 127,
        'archive_name': 'GlassTTY-rev0127-example.zip',
        'codename': 'tern',
        'summary_key': 'revisionreceipt-warningledger-artifactbuckets',
        'previous_archive': 'GlassTTY-rev0126-example.zip',
        'truth_surface_counts': counts,
        'top_level_canon_paths': ['README.md'],
        'added_paths': ['README.md'],
        'imported_patterns': ['revision receipt'],
    })
    (root / 'README.md').write_text('# demo\n', encoding='utf-8')
    payload = build_revision_receipt_conformance(root=root)
    assert payload['all_valid'] is True


def test_write_root_conformance_writes_file(tmp_path: Path) -> None:
    root = tmp_path
    _write_json(root / 'ARCHIVE_MANIFEST.json', {
        'project': 'GlassTTY',
        'archive_name': 'GlassTTY-rev0127-example.zip',
        'archive_revision': 127,
        'codename': 'tern',
        'summary': 'revisionreceipt-warningledger-artifactbuckets',
        'base_archive': 'GlassTTY-rev0126-example.zip',
    })
    for rel, payload in {
        'validation/opening-surface-captures.json': {'captures': []},
        'validation/readiness-report-captures.json': {'entries': []},
        'validation/control-plane-report-captures.json': {'captures': []},
        'validation/install-receipts.json': {'captures': []},
        'validation/support-surface-captures.json': {'captures': []},
        'validation/operator-handoff-captures.json': {'entries': []},
        'validation/support-source-baseline-captures.json': {'captures': []},
    }.items():
        _write_json(root / rel, payload)
    counts = {
        'families_without_capture_history': 7,
        'families_whose_latest_head_points_at_foreign_root': 0,
        'families_without_current_root_capture': 0,
        'families_without_citation_head': 0,
    }
    _write_json(root / 'REVISION-RECEIPT.json', {
        'project': 'GlassTTY',
        'revision': 127,
        'archive_name': 'GlassTTY-rev0127-example.zip',
        'codename': 'tern',
        'summary_key': 'revisionreceipt-warningledger-artifactbuckets',
        'previous_archive': 'GlassTTY-rev0126-example.zip',
        'truth_surface_counts': counts,
        'top_level_canon_paths': ['README.md'],
        'added_paths': ['README.md'],
        'imported_patterns': ['revision receipt'],
    })
    (root / 'README.md').write_text('# demo\n', encoding='utf-8')
    payload = write_root_conformance(root=root)
    assert payload['all_valid'] is True
    assert (root / 'REVISION-RECEIPT-CONFORMANCE.json').exists()

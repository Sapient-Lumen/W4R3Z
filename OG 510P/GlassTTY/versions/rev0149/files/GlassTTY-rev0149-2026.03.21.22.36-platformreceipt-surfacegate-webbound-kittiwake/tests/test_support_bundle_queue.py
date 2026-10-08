from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('support_bundle_queue', ROOT / 'scripts' / 'support_bundle_queue.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_support_bundle_queue = MODULE.build_support_bundle_queue
capture_support_bundle_queue = MODULE.capture_support_bundle_queue
validate_bundle_manifest = MODULE.validate_bundle_manifest
summarize_capture_history = MODULE.summarize_capture_history


def _seed_record(root: Path) -> None:
    record = root / 'docs' / 'support-records' / 'claude.md'
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text('# Support record — Claude\n', encoding='utf-8')


def _seed_bundle(root: Path, *, status: str = 'hold', include_artifact: bool = True) -> Path:
    _seed_record(root)
    artifact = root / 'validation' / 'latest' / 'control-plane-report-capture' / 'control-plane-report.json'
    artifact.parent.mkdir(parents=True, exist_ok=True)
    if include_artifact:
        artifact.write_text('{}\n', encoding='utf-8')
    bundle = root / 'docs' / 'support-bundles' / status / 'claude.json'
    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.write_text(json.dumps({
        'bundle_key': 'claude-reference',
        'bundle_status': status,
        'surface_key': 'claude',
        'browser_lane': 'chromium-live',
        'captured_at': '2026-03-20T17:35:00Z',
        'workflows_touched': ['surface-detect', 'support-capture'],
        'support_record': 'docs/support-records/claude.md',
        'artifact_refs': [
            {'path': 'validation/latest/control-plane-report-capture/control-plane-report.json', 'kind': 'control-plane-report', 'role': 'fused snapshot'}
        ],
        'result_summary': {'next_action': 'capture a live support bundle'},
        'publication_decision': {'decision': status, 'why': ['needs live proof']},
    }, indent=2) + '\n', encoding='utf-8')
    return bundle


def test_validate_bundle_manifest_checks_paths_and_status(tmp_path: Path) -> None:
    bundle = _seed_bundle(tmp_path, status='hold', include_artifact=True)
    report = validate_bundle_manifest(bundle, root=tmp_path)
    assert report['ok'] is True
    assert report['existing_artifact_count'] == 1
    assert report['bundle_status'] == 'hold'


def test_validate_bundle_manifest_flags_missing_artifact(tmp_path: Path) -> None:
    bundle = _seed_bundle(tmp_path, status='hold', include_artifact=False)
    report = validate_bundle_manifest(bundle, root=tmp_path)
    assert report['ok'] is False
    assert report['missing_artifact_count'] == 1
    assert any('missing artifact refs' in issue for issue in report['issues'])


def test_build_support_bundle_queue_summarizes_counts_and_review_queue(tmp_path: Path) -> None:
    _seed_bundle(tmp_path, status='hold', include_artifact=True)
    payload = build_support_bundle_queue(root=tmp_path)
    assert payload['counts']['bundle_count'] == 1
    assert payload['counts']['by_status']['hold'] == 1
    assert payload['review_queue'][0]['bundle_key'] == 'claude-reference'
    assert payload['warnings'][0]['severity'] == 'advisory'


def test_capture_support_bundle_queue_writes_bundle_and_history(tmp_path: Path) -> None:
    _seed_bundle(tmp_path, status='hold', include_artifact=True)
    output_dir = tmp_path / 'validation' / 'latest' / 'support-bundle-queue'
    history_path = tmp_path / 'validation' / 'support-bundle-queue-captures.json'
    payload = capture_support_bundle_queue(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'support-bundle-queue.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1

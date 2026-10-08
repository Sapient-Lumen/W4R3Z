from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('published_support_surface', ROOT / 'scripts' / 'published_support_surface.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_published_support_surface = MODULE.build_published_support_surface
capture_published_support_surface = MODULE.capture_published_support_surface
write_root_published_support_surface = MODULE.write_root_published_support_surface


def _seed_support_record(root: Path, *, strongest: str = 'experimental') -> None:
    record = root / 'docs' / 'support-records' / 'claude.md'
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        '\n'.join([
            '# Support record — Claude',
            '',
            '- **Surface key:** `claude`',
            '- **Record status:** `backfilled-from-evidence`',
            '- **Default browser lane:** `chromium-live`',
            '- **Last reviewed:** `2026-03-20`',
            '- **Rollout priority:** `reference adapter`',
            '',
            '## Known blockers and risk notes',
            '- route drift',
            '',
            '## Workflow rows',
            '',
            '| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |',
            '| --- | --- | --- | --- | --- | --- |',
            f'| surface-detect | {strongest} | chromium-live | held bundle exists | route drift | capture live proof |',
            '| receiver-resolve | investigated | chromium-live | note | caveat | need live proof |',
            '| composer-read | investigated | chromium-live | note | caveat | need live proof |',
            '| composer-write | investigated | chromium-live | note | caveat | need live proof |',
            '| turn-submit | investigated | chromium-live | note | caveat | need live proof |',
            '| generation-read | investigated | chromium-live | note | caveat | need live proof |',
            '| latest-turn-read | investigated | chromium-live | note | caveat | need live proof |',
            '| support-capture | investigated | chromium-live | note | caveat | need live proof |',
            '',
            '## Next action',
            '- capture live proof',
            '',
        ]) + '\n',
        encoding='utf-8',
    )


def _seed_bundle(root: Path, *, state: str) -> None:
    bundle = root / 'docs' / 'support-bundles' / state / 'claude.json'
    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.write_text(json.dumps({
        'bundle_key': 'claude-reference',
        'bundle_status': state,
        'surface_key': 'claude',
        'browser_lane': 'chromium-live',
        'captured_at': '2026-03-20T17:35:00Z',
        'workflows_touched': ['surface-detect', 'support-capture'],
        'artifact_refs': [{'path': 'docs/support-records/claude.md', 'kind': 'support-record', 'role': 'record'}],
        'support_record': 'docs/support-records/claude.md',
        'result_summary': {'next_action': 'capture live proof'},
        'publication_decision': {'decision': state, 'why': ['needs live proof']},
    }, indent=2) + '\n', encoding='utf-8')


def test_build_published_support_surface_warns_when_strong_record_lacks_published_bundle(tmp_path: Path) -> None:
    _seed_support_record(tmp_path, strongest='experimental')
    _seed_bundle(tmp_path, state='hold')
    payload = build_published_support_surface(root=tmp_path)
    assert payload['counts']['citable_surface_count'] == 0
    assert payload['surfaces'][0]['publication_posture'] == 'hold'
    assert any('no published support bundle yet' in warning['message'] for warning in payload['warnings'])


def test_build_published_support_surface_marks_published_bundle_as_citable(tmp_path: Path) -> None:
    _seed_support_record(tmp_path, strongest='experimental')
    _seed_bundle(tmp_path, state='published')
    payload = build_published_support_surface(root=tmp_path)
    assert payload['counts']['citable_surface_count'] == 1
    assert payload['surfaces'][0]['citable_now'] is True
    assert payload['surfaces'][0]['published_bundle_keys'] == ['claude-reference']


def test_capture_and_write_root_published_support_surface(tmp_path: Path) -> None:
    _seed_support_record(tmp_path, strongest='investigated')
    _seed_bundle(tmp_path, state='published-ready')
    output_dir = tmp_path / 'validation' / 'latest' / 'published-support-surface'
    history_path = tmp_path / 'validation' / 'published-support-surface-captures.json'
    payload = capture_published_support_surface(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'support-public-surface.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    root_snapshot = write_root_published_support_surface(root=tmp_path)
    assert (tmp_path / 'SUPPORT-PUBLIC-SURFACE.json').exists()
    assert root_snapshot['counts']['published_ready_bundle_count'] == 1

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('support_source_baseline', ROOT / 'scripts' / 'support_source_baseline.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_support_source_baseline = MODULE.build_support_source_baseline
capture_support_source_baseline = MODULE.capture_support_source_baseline
write_root_support_source_baseline = MODULE.write_root_support_source_baseline


def _seed_lock(root: Path) -> None:
    (root / 'SUPPORT-SOURCE-LOCK.json').write_text(json.dumps({
        'project': 'GlassTTY',
        'last_reviewed': '2026-03-20',
        'review_policy': {'max_lock_review_age_days': 30, 'max_source_review_age_days': 30},
        'hierarchy': [{'tier': 'first-party-product-surface', 'rank': 0}, {'tier': 'vendor-runtime-doc', 'rank': 1}],
        'sources': [
            {
                'source_key': 'claude-product-overview',
                'title': 'Claude product overview',
                'url': 'https://claude.com/product/overview',
                'tier': 'first-party-product-surface',
                'surface_keys': ['claude'],
                'required_for_publication': True,
                'reviewed_at': '2026-03-20',
            },
            {
                'source_key': 'chrome-native-messaging',
                'title': 'Native messaging',
                'url': 'https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging',
                'tier': 'vendor-runtime-doc',
                'surface_keys': ['shared-browser-substrate'],
                'required_for_publication': False,
                'reviewed_at': '2026-03-20',
            },
        ],
    }, indent=2) + '\n', encoding='utf-8')


def _seed_support_record(root: Path) -> None:
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
            '| surface-detect | experimental | chromium-live | note | caveat | capture live proof |',
            '| receiver-resolve | investigated | chromium-live | note | caveat | capture live proof |',
            '| composer-read | investigated | chromium-live | note | caveat | capture live proof |',
            '| composer-write | investigated | chromium-live | note | caveat | capture live proof |',
            '| turn-submit | investigated | chromium-live | note | caveat | capture live proof |',
            '| generation-read | investigated | chromium-live | note | caveat | capture live proof |',
            '| latest-turn-read | investigated | chromium-live | note | caveat | capture live proof |',
            '| support-capture | investigated | chromium-live | note | caveat | capture live proof |',
            '',
            '## Next action',
            '- capture live proof',
            '',
        ]) + '\n',
        encoding='utf-8',
    )


def _seed_bundle(root: Path, *, source_refs: list[str] | None = None, state: str = 'hold') -> None:
    bundle = root / 'docs' / 'support-bundles' / state / 'claude.json'
    bundle.parent.mkdir(parents=True, exist_ok=True)
    payload = {
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
    }
    if source_refs is not None:
        payload['source_refs'] = source_refs
    bundle.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def test_support_source_baseline_reports_missing_bundle_source_refs(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    _seed_bundle(tmp_path)
    payload = build_support_source_baseline(root=tmp_path)
    assert payload['counts']['bundles_missing_source_refs'] == 1
    assert any('no source_refs' in warning['message'] for warning in payload['warnings'])


def test_support_source_baseline_tracks_cited_approved_sources(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    _seed_bundle(tmp_path, source_refs=['claude-product-overview', 'chrome-native-messaging'])
    payload = build_support_source_baseline(root=tmp_path)
    surface = payload['surfaces'][0]
    assert surface['approved_source_count'] == 2
    assert surface['cited_bundle_source_keys'] == ['chrome-native-messaging', 'claude-product-overview']
    assert payload['counts']['bundles_missing_source_refs'] == 0


def test_capture_and_write_root_support_source_baseline(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    _seed_bundle(tmp_path, source_refs=['claude-product-overview'])
    output_dir = tmp_path / 'validation' / 'latest' / 'support-source-baseline'
    history_path = tmp_path / 'validation' / 'support-source-baseline-captures.json'
    payload = capture_support_source_baseline(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'support-source-baseline.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    root_snapshot = write_root_support_source_baseline(root=tmp_path)
    assert (tmp_path / 'SUPPORT-SOURCE-BASELINE.json').exists()
    assert root_snapshot['counts']['source_count'] == 2


def test_support_source_baseline_keeps_existing_bundle_action_when_sources_are_cited(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    _seed_bundle(tmp_path, source_refs=['claude-product-overview', 'chrome-native-messaging'])
    payload = build_support_source_baseline(root=tmp_path)
    surface = payload['surfaces'][0]
    assert 'No bundle exists yet' not in surface['next_source_action']
    assert 'Keep the cited approved sources current' in surface['next_source_action']


def test_support_source_baseline_flags_stale_required_source_reviews(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    data = json.loads((tmp_path / 'SUPPORT-SOURCE-LOCK.json').read_text(encoding='utf-8'))
    data['last_reviewed'] = '2020-01-01'
    data['sources'][0]['reviewed_at'] = '2020-01-01'
    (tmp_path / 'SUPPORT-SOURCE-LOCK.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    _seed_support_record(tmp_path)
    _seed_bundle(tmp_path, source_refs=['claude-product-overview'])
    payload = build_support_source_baseline(root=tmp_path)
    assert payload['counts']['stale_lock_review'] is True
    assert payload['counts']['stale_required_source_count'] == 1
    assert any('stale or missing' in warning['message'] for warning in payload['warnings'])

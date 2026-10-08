from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('support_publish_gate', ROOT / 'scripts' / 'support_publish_gate.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_support_publish_gate = MODULE.build_support_publish_gate
evaluate_bundle_gate = MODULE.evaluate_bundle_gate
stamp_publish_guard = MODULE.stamp_publish_guard


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
            }
        ],
    }, indent=2) + '\n', encoding='utf-8')

def _seed_support_record(root: Path, *, status: str = 'backfilled-from-evidence') -> None:
    record = root / 'docs' / 'support-records' / 'claude.md'
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        '\n'.join([
            '# Support record — Claude',
            '',
            '- **Surface key:** `claude`',
            f'- **Record status:** `{status}`',
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
            '| surface-detect | experimental | chromium-live | route bundle exists | route drift | capture live proof |',
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


def _seed_bundle(root: Path, *, state: str = 'hold', blockers: list[str] | None = None, live_artifact: bool = False, source_refs: list[str] | None = None) -> Path:
    bundle = root / 'docs' / 'support-bundles' / state / 'claude.json'
    bundle.parent.mkdir(parents=True, exist_ok=True)
    artifact_refs = [{'path': 'docs/support-records/claude.md', 'kind': 'support-record', 'role': 'record'}]
    if live_artifact:
        live_capture = root / 'validation' / 'latest' / 'claude-live' / 'route-capture.json'
        live_capture.parent.mkdir(parents=True, exist_ok=True)
        live_capture.write_text('{}\n', encoding='utf-8')
        artifact_refs.append({'path': 'validation/latest/claude-live/route-capture.json', 'kind': 'route-capture', 'role': 'live route witness'})
    bundle.write_text(json.dumps({
        'bundle_key': 'claude-reference',
        'bundle_status': state,
        'surface_key': 'claude',
        'browser_lane': 'chromium-live',
        'captured_at': '2026-03-20T17:35:00Z',
        'workflows_touched': ['surface-detect', 'support-capture'],
        'artifact_refs': artifact_refs,
        'support_record': 'docs/support-records/claude.md',
        'result_summary': {'next_action': 'capture live proof'},
        'publication_decision': {'decision': state, 'why': list(blockers or [])},
        'claim_scope': {'publication_blockers': list(blockers or [])},
        'source_refs': list(source_refs or []),
    }, indent=2) + '\n', encoding='utf-8')
    return bundle


def test_publish_gate_blocks_bundle_without_live_publish_evidence(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='hold', blockers=['needs live proof'], live_artifact=False)
    payload = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published-ready')
    assert payload['ok'] is False
    assert any('lacks direct live/route/history/workflow evidence artifacts' in reason for reason in payload['blocking_reasons'])


def test_publish_gate_accepts_clean_bundle_with_live_publish_evidence(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='hold', blockers=[], live_artifact=True, source_refs=['claude-product-overview'])
    payload = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published-ready')
    assert payload['ok'] is True
    assert payload['publish_evidence_artifacts'][0]['kind'] == 'route-capture'


def test_published_gate_requires_current_publish_guard(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='published-ready', blockers=[], live_artifact=True, source_refs=['claude-product-overview'])
    ready = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published-ready')
    assert ready['ok'] is True
    published = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published')
    assert published['ok'] is False
    payload = json.loads(bundle.read_text(encoding='utf-8'))
    stamp_publish_guard(payload, root=tmp_path, target_state='published-ready', gate_summary=ready)
    bundle.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    published = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published')
    assert published['ok'] is True



def test_publish_gate_blocks_bundle_without_required_source_refs(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='hold', blockers=[], live_artifact=True, source_refs=[])
    payload = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published-ready')
    assert payload['ok'] is False
    assert any(check['name'] == 'required_source_refs_present' and check['ok'] is False for check in payload['checks'])

def test_build_support_publish_gate_summarizes_ready_and_publish_counts(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='published-ready', blockers=[], live_artifact=True, source_refs=['claude-product-overview'])
    payload = json.loads(bundle.read_text(encoding='utf-8'))
    stamp_publish_guard(payload, root=tmp_path, target_state='published-ready', gate_summary={'target_state': 'published-ready', 'ok': True, 'blocking_reasons': []})
    bundle.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    report = build_support_publish_gate(root=tmp_path)
    assert report['counts']['published_ready_pass_count'] == 1
    assert report['counts']['published_pass_count'] == 1
    assert report['warnings'] == []


def test_publish_gate_blocks_bundle_when_required_source_review_is_stale(tmp_path: Path) -> None:
    _seed_lock(tmp_path)
    data = json.loads((tmp_path / 'SUPPORT-SOURCE-LOCK.json').read_text(encoding='utf-8'))
    data['last_reviewed'] = '2020-01-01'
    data['sources'][0]['reviewed_at'] = '2020-01-01'
    (tmp_path / 'SUPPORT-SOURCE-LOCK.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    _seed_support_record(tmp_path)
    bundle = _seed_bundle(tmp_path, state='hold', blockers=[], live_artifact=True, source_refs=['claude-product-overview'])
    payload = evaluate_bundle_gate(bundle_path=bundle, root=tmp_path, target_state='published-ready')
    assert payload['ok'] is False
    assert any(check['name'] == 'support_source_lock_review_current' and check['ok'] is False for check in payload['checks'])
    assert any(check['name'] == 'required_source_reviews_current' and check['ok'] is False for check in payload['checks'])

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('support_bundle_transition', ROOT / 'scripts' / 'support_bundle_transition.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

transition_bundle = MODULE.transition_bundle


def _seed_bundle(root: Path, *, state: str = 'hold', name: str = 'claude.json', blockers: list[str] | None = None, live_artifact: bool = False) -> Path:
    bundle = root / 'docs' / 'support-bundles' / state / name
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
        'publication_decision': {'decision': state, 'why': list(blockers) if blockers is not None else ['needs live proof']},
        'claim_scope': {'publication_blockers': list(blockers) if blockers is not None else ['needs live proof']},
    }, indent=2) + '\n', encoding='utf-8')
    record = root / 'docs' / 'support-records' / 'claude.md'
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text('\n'.join([
        '# Support record — Claude',
        '',
        '- **Surface key:** `claude`',
        '- **Record status:** `backfilled-from-evidence`',
        '- **Default browser lane:** `chromium-live`',
        '- **Last reviewed:** `2026-03-20`',
        '- **Rollout priority:** `reference adapter`',
        '',
        '## Workflow rows',
        '',
        '| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |',
        '| --- | --- | --- | --- | --- | --- |',
        '| surface-detect | experimental | chromium-live | route bundle exists | route drift | capture live proof |',
        '| support-capture | investigated | chromium-live | note | caveat | need live proof |',
        '',
        '## Next action',
        '- capture live proof',
        '',
    ]) + '\n', encoding='utf-8')
    return bundle


def test_transition_bundle_moves_file_and_updates_status(tmp_path: Path) -> None:
    source = _seed_bundle(tmp_path, state='hold', blockers=[], live_artifact=True)
    payload = transition_bundle(name_or_key='claude-reference', to_state='published-ready', root=tmp_path)
    dest = tmp_path / 'docs' / 'support-bundles' / 'published-ready' / source.name
    assert payload['from_state'] == 'hold'
    assert payload['to_state'] == 'published-ready'
    assert not source.exists()
    assert dest.exists()
    manifest = json.loads(dest.read_text(encoding='utf-8'))
    assert manifest['bundle_status'] == 'published-ready'
    assert manifest['publication_decision']['decision'] == 'published-ready'


def test_transition_bundle_can_replace_decision_fields(tmp_path: Path) -> None:
    _seed_bundle(tmp_path, state='candidate')
    transition_bundle(
        name_or_key='claude-reference',
        to_state='hold',
        root=tmp_path,
        why=['missing route witness'],
        publish_when=['one current live route bundle exists'],
        next_action='capture route/history witness',
    )
    dest = tmp_path / 'docs' / 'support-bundles' / 'hold' / 'claude.json'
    manifest = json.loads(dest.read_text(encoding='utf-8'))
    assert manifest['publication_decision']['why'] == ['missing route witness']
    assert manifest['publication_decision']['publish_when'] == ['one current live route bundle exists']
    assert manifest['result_summary']['next_action'] == 'capture route/history witness'


def test_transition_bundle_fail_closed_for_publish_gate(tmp_path: Path) -> None:
    _seed_bundle(tmp_path, state='hold', blockers=['needs live proof'], live_artifact=False)
    try:
        transition_bundle(name_or_key='claude-reference', to_state='published-ready', root=tmp_path)
    except ValueError as exc:
        assert 'support publish gate failed' in str(exc)
    else:
        raise AssertionError('expected publish-gate failure')


def test_transition_bundle_stamps_publish_guard_and_receipt(tmp_path: Path) -> None:
    source = _seed_bundle(tmp_path, state='hold', blockers=[], live_artifact=True)
    payload = transition_bundle(name_or_key='claude-reference', to_state='published-ready', root=tmp_path)
    dest = tmp_path / 'docs' / 'support-bundles' / 'published-ready' / source.name
    manifest = json.loads(dest.read_text(encoding='utf-8'))
    assert manifest['publish_guard']['target_state'] == 'published-ready'
    receipt_path = tmp_path / 'validation' / 'latest' / 'support-bundle-transition' / 'transition-receipt.json'
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    assert receipt['gate_ok'] is True
    assert payload['receipt_capture']['capture_count_after_write'] == 1

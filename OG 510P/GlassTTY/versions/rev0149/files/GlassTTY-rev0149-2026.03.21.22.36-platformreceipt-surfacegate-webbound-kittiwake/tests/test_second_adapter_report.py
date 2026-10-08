from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('second_adapter_report', ROOT / 'scripts' / 'second_adapter_report.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_second_adapter_report = MODULE.build_second_adapter_report
capture_second_adapter_report = MODULE.capture_second_adapter_report
write_root_second_adapter_report = MODULE.write_root_second_adapter_report
summarize_capture_history = MODULE.summarize_capture_history


def _seed_matrix(root: Path) -> None:
    (root / 'SECOND-ADAPTER-MATRIX.json').write_text(json.dumps({
        'project': 'GlassTTY',
        'criteria': [
            {'key': 'browser_surface_directness', 'weight': 3},
            {'key': 'workflow_similarity', 'weight': 4},
            {'key': 'evidence_capture_ease', 'weight': 3},
            {'key': 'reusable_lessons', 'weight': 4},
            {'key': 'operator_value', 'weight': 3},
            {'key': 'drift_risk', 'weight': -2},
        ],
        'priority_boost': {
            'reference adapter': 0,
            'recommended second adapter': 5,
            'phase-2': 3,
            'phase-3': 1,
        },
        'source_freshness': {'fresh_first_party_bonus': 4, 'stale_or_missing_first_party_penalty': -6},
        'surfaces': [
            {
                'surface_key': 'claude',
                'browser_surface_directness': 5,
                'workflow_similarity': 5,
                'evidence_capture_ease': 4,
                'reusable_lessons': 5,
                'operator_value': 5,
                'drift_risk': 3,
                'first_lane': 'chromium-live',
                'first_workflow_targets': ['surface-detect'],
                'notes': ['reference'],
            },
            {
                'surface_key': 'chatgpt',
                'browser_surface_directness': 5,
                'workflow_similarity': 5,
                'evidence_capture_ease': 4,
                'reusable_lessons': 5,
                'operator_value': 5,
                'drift_risk': 3,
                'first_lane': 'chromium-live',
                'first_workflow_targets': ['surface-detect', 'composer-read'],
                'notes': ['best fit'],
            },
            {
                'surface_key': 'aistudio',
                'browser_surface_directness': 4,
                'workflow_similarity': 3,
                'evidence_capture_ease': 4,
                'reusable_lessons': 4,
                'operator_value': 4,
                'drift_risk': 3,
                'first_lane': 'chromium-live',
                'first_workflow_targets': ['surface-detect'],
                'notes': ['good phase-2'],
            },
        ],
    }, indent=2) + '\n', encoding='utf-8')


def _seed_lock(root: Path, *, stale_chatgpt: bool = False) -> None:
    reviewed_at = '2020-01-01' if stale_chatgpt else '2026-03-21'
    (root / 'SUPPORT-SOURCE-LOCK.json').write_text(json.dumps({
        'project': 'GlassTTY',
        'last_reviewed': '2026-03-21',
        'hierarchy': [{'tier': 'first-party-product-surface', 'rank': 0}],
        'review_policy': {'max_lock_review_age_days': 30, 'max_source_review_age_days': 30},
        'sources': [
            {
                'source_key': 'claude-product-overview',
                'title': 'Claude',
                'url': 'https://claude.com/product/overview',
                'tier': 'first-party-product-surface',
                'surface_keys': ['claude'],
                'required_for_publication': True,
                'reviewed_at': '2026-03-21',
            },
            {
                'source_key': 'chatgpt-product-overview',
                'title': 'ChatGPT',
                'url': 'https://chatgpt.com/overview',
                'tier': 'first-party-product-surface',
                'surface_keys': ['chatgpt'],
                'required_for_publication': True,
                'reviewed_at': reviewed_at,
            },
            {
                'source_key': 'aistudio-product-home',
                'title': 'AI Studio',
                'url': 'https://ai.google.dev/aistudio',
                'tier': 'first-party-product-surface',
                'surface_keys': ['aistudio'],
                'required_for_publication': True,
                'reviewed_at': '2026-03-21',
            },
        ],
    }, indent=2) + '\n', encoding='utf-8')


def _write_record(path: Path, *, surface_key: str, rollout_priority: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''# Support record — {surface_key.title()}\n\n## Metadata\n- **surface key:** `{surface_key}`\n- **record status:** `seeded`\n- **default browser lane:** `chromium-live`\n- **last reviewed:** `2026-03-21`\n- **rollout priority:** `{rollout_priority}`\n\n## Workflow rows\n\n| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |\n|---|---|---|---|---|---|\n| surface-detect | investigated | chromium-live | pending | caveat | capture bundle |\n| receiver-resolve | investigated | chromium-live | pending | caveat | capture bundle |\n| composer-read | investigated | chromium-live | pending | caveat | capture bundle |\n| composer-write | investigated | chromium-live | pending | caveat | capture bundle |\n| turn-submit | investigated | chromium-live | pending | caveat | capture bundle |\n| generation-read | investigated | chromium-live | pending | caveat | capture bundle |\n| latest-turn-read | investigated | chromium-live | pending | caveat | capture bundle |\n| support-capture | investigated | chromium-live | pending | caveat | capture bundle |\n\n## Known blockers and risk notes\n- blocker\n\n## Next action\n- capture first bundle\n''',
        encoding='utf-8',
    )


def _seed_records(root: Path) -> None:
    _write_record(root / 'docs' / 'support-records' / 'claude.md', surface_key='claude', rollout_priority='reference adapter')
    _write_record(root / 'docs' / 'support-records' / 'chatgpt.md', surface_key='chatgpt', rollout_priority='recommended second adapter')
    _write_record(root / 'docs' / 'support-records' / 'aistudio.md', surface_key='aistudio', rollout_priority='phase-2')


def test_second_adapter_report_recommends_chatgpt_and_excludes_reference_adapter(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    payload = build_second_adapter_report(root=tmp_path)
    assert payload['recommendation']['surface_key'] == 'chatgpt'
    assert payload['candidates'][0]['surface_key'] == 'chatgpt'
    claude = [item for item in payload['candidates'] if item['surface_key'] == 'claude'][0]
    assert claude['excluded_from_second_adapter'] is True


def test_second_adapter_report_penalizes_stale_first_party_source_review(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path, stale_chatgpt=True)
    _seed_records(tmp_path)
    payload = build_second_adapter_report(root=tmp_path)
    chatgpt = [item for item in payload['candidates'] if item['surface_key'] == 'chatgpt'][0]
    aistudio = [item for item in payload['candidates'] if item['surface_key'] == 'aistudio'][0]
    assert chatgpt['source_freshness_score'] < 0
    assert aistudio['source_freshness_score'] > 0
    assert payload['recommendation']['surface_key'] == 'aistudio'


def test_capture_and_write_root_second_adapter_report(tmp_path: Path) -> None:
    _seed_matrix(tmp_path)
    _seed_lock(tmp_path)
    _seed_records(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'second-adapter-report'
    history_path = tmp_path / 'validation' / 'second-adapter-report-captures.json'
    payload = capture_second_adapter_report(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'second-adapter-report.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_snapshot = write_root_second_adapter_report(root=tmp_path)
    assert (tmp_path / 'SECOND-ADAPTER-REPORT.json').exists()
    assert root_snapshot['recommendation']['surface_key'] == 'chatgpt'

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_second_adapter_report import _seed_lock, _seed_matrix, _seed_records

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_branch_guard', ROOT / 'scripts' / 'chatgpt_branch_guard.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_branch_guard = MODULE.build_chatgpt_branch_guard
capture_chatgpt_branch_guard = MODULE.capture_chatgpt_branch_guard
write_root_chatgpt_branch_guard = MODULE.write_root_chatgpt_branch_guard
evaluate_chatgpt_branch_guard = MODULE.evaluate_chatgpt_branch_guard
summarize_capture_history = MODULE.summarize_capture_history


def _augment_lock(root: Path) -> None:
    lock_path = root / 'SUPPORT-SOURCE-LOCK.json'
    payload = json.loads(lock_path.read_text(encoding='utf-8'))
    payload['sources'].extend([
        {'source_key': 'chatgpt-home-page', 'title': 'The ChatGPT home page', 'url': 'https://help.openai.com/en/articles/9125172-the-chatgpt-home-page', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': True, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-capabilities-overview', 'title': 'ChatGPT Capabilities Overview', 'url': 'https://help.openai.com/en/articles/9260256-chatgpt-capabilities-overview', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-projects', 'title': 'Projects in ChatGPT', 'url': 'https://help.openai.com/en/articles/10169521-projects-in-chatgpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-canvas-feature', 'title': 'What is the canvas feature in ChatGPT and how do I use it?', 'url': 'https://help.openai.com/en/articles/9930697-what-is-the-canvas-feature-in-chatgpt-and-how-do-i-use-it', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-search', 'title': 'ChatGPT search', 'url': 'https://help.openai.com/en/articles/9237897-chatgpt-search', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-gpts-builder', 'title': 'Creating and editing GPTs', 'url': 'https://help.openai.com/en/articles/8554397-creating-a-gpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-history-search', 'title': 'How do I search my chat history in ChatGPT?', 'url': 'https://help.openai.com/en/articles/10056348-how-do-i-search-my-chat-history-in-chatgpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-best-practices', 'title': 'Best Practices', 'url': 'https://playwright.dev/docs/best-practices', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-actionability', 'title': 'Auto-waiting', 'url': 'https://playwright.dev/docs/actionability', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
    ])
    lock_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _seed(root: Path) -> None:
    _seed_matrix(root)
    _seed_lock(root)
    _seed_records(root)
    _augment_lock(root)


def test_branch_guard_builds_from_chatgpt_route_first_materials(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_branch_guard(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert 'search-capable-home-lane' in payload['caution_postures']
    assert 'gpts-builder-web-workspace' in payload['stop_postures']
    assert 'playwright-best-practices' in payload['source_keys']
    assert payload['route_guard']['allowed_hosts'] == ['chatgpt.com']


def test_branch_guard_classifies_continue_caution_and_stop(tmp_path: Path) -> None:
    _seed(tmp_path)
    caution = evaluate_chatgpt_branch_guard(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'auth_posture': 'logged-in',
            'title': 'ChatGPT',
            'main_region_text': ['Main conversation', 'Search the web'],
            'sidebar_text': ['Search chats'],
        },
        root=tmp_path,
    )
    assert caution['matched_posture_key'] == 'search-capable-home-lane'
    assert caution['decision'] == 'continue-with-caution'

    stop = evaluate_chatgpt_branch_guard(
        {
            'host': 'chatgpt.com',
            'path': '/gpts/editor',
            'title': 'Create GPT',
            'visible_text': ['Explore GPTs', 'Create GPT'],
        },
        root=tmp_path,
    )
    assert stop['matched_posture_key'] == 'gpts-builder-web-workspace'
    assert stop['decision'] == 'stop'

    baseline = evaluate_chatgpt_branch_guard(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'auth_posture': 'logged-out',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
        },
        root=tmp_path,
    )
    assert baseline['matched_posture_key'] == 'guest-home-single-thread'
    assert baseline['decision'] == 'continue'


def test_branch_guard_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-branch-guard'
    history_path = tmp_path / 'validation' / 'chatgpt-branch-guard-captures.json'
    payload = capture_chatgpt_branch_guard(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-branch-guard.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_branch_guard(root=tmp_path)
    assert (tmp_path / 'CHATGPT-BRANCH-GUARD.json').exists()
    assert root_payload['counts']['stop_posture_count'] == 3

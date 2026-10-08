from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_second_adapter_report import _seed_lock, _seed_matrix, _seed_records

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_composer_witness_receipt', ROOT / 'scripts' / 'chatgpt_composer_witness_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_composer_witness_receipt = MODULE.build_chatgpt_composer_witness_receipt
evaluate_chatgpt_composer_witness_receipt = MODULE.evaluate_chatgpt_composer_witness_receipt
capture_chatgpt_composer_witness_receipt = MODULE.capture_chatgpt_composer_witness_receipt
write_root_chatgpt_composer_witness_receipt = MODULE.write_root_chatgpt_composer_witness_receipt
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
        {'source_key': 'chatgpt-apps-with-sync', 'title': 'ChatGPT apps with sync', 'url': 'https://help.openai.com/en/articles/10847137-chatgpt-apps-with-sync', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-company-knowledge', 'title': 'Company knowledge in ChatGPT (Business, Enterprise, and Edu)', 'url': 'https://help.openai.com/en/articles/12628342-company-knowledge-in-chatgpt-business-enterprise-and-edu', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-tasks', 'title': 'Tasks in ChatGPT', 'url': 'https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-windows-app', 'title': 'Using the ChatGPT Windows app', 'url': 'https://help.openai.com/en/articles/9982051-using-the-chatgpt-windows-app', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-subscription-another-device', 'title': 'Can I access my ChatGPT subscription from another device?', 'url': 'https://help.openai.com/en/articles/8980438-can-i-access-my-chatgpt-subscription-from-another-device', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-temporary-chat-faq', 'title': 'Temporary Chat FAQ', 'url': 'https://help.openai.com/en/articles/8914046-temporary-chat-faq', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-memory-faq', 'title': 'Memory FAQ', 'url': 'https://help.openai.com/en/articles/8590148-memory-faq', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'chatgpt-chat-file-retention', 'title': 'Chat and File Retention Policies in ChatGPT', 'url': 'https://help.openai.com/en/articles/8983778-chat-and-file-retention-policies-in-chatgpt', 'tier': 'first-party-product-surface', 'surface_keys': ['chatgpt'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-authentication', 'title': 'Authentication', 'url': 'https://playwright.dev/docs/auth', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-browsercontext', 'title': 'BrowserContext', 'url': 'https://playwright.dev/docs/api/class-browsercontext', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-best-practices', 'title': 'Best Practices', 'url': 'https://playwright.dev/docs/best-practices', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-actionability', 'title': 'Auto-waiting', 'url': 'https://playwright.dev/docs/actionability', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-input', 'title': 'Actions', 'url': 'https://playwright.dev/docs/input', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-test-assertions', 'title': 'Assertions', 'url': 'https://playwright.dev/docs/test-assertions', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-emulation', 'title': 'Emulation', 'url': 'https://playwright.dev/docs/emulation', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-projects', 'title': 'Projects', 'url': 'https://playwright.dev/docs/test-projects', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
        {'source_key': 'playwright-browsers', 'title': 'Browsers', 'url': 'https://playwright.dev/docs/browsers', 'tier': 'vendor-runtime-doc', 'surface_keys': ['shared-browser-substrate'], 'required_for_publication': False, 'reviewed_at': '2026-03-21'},
    ])
    lock_path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _seed(root: Path) -> None:
    _seed_matrix(root)
    _seed_lock(root)
    _seed_records(root)
    _augment_lock(root)


def test_composer_witness_receipt_builds_quality_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_composer_witness_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['witness_contract']['required_fields'] == ['composer_candidate_family']
    assert [item['quality'] for item in payload['quality_tiers']] == ['strong', 'usable', 'fragile', 'insufficient']


def test_composer_witness_receipt_grades_ready_blocked_and_hold_cases(tmp_path: Path) -> None:
    _seed(tmp_path)
    ready = evaluate_chatgpt_composer_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'auth_posture': 'logged-out',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'accessible-textbox',
            'locator_strategy': 'getByRole(textbox)',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True, 'stable': True, 'receives_events': True},
            'write_method': 'fill',
            'before_text': '',
            'after_text': 'GLASSTTY-CHECKPOINT',
            'expected_probe_text': 'GLASSTTY-CHECKPOINT',
        },
        root=tmp_path,
    )
    assert ready['composer_quality'] == 'strong'
    assert ready['composer_readiness'] == 'ready'

    blocked = evaluate_chatgpt_composer_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'accessible-textbox',
            'actionability': {'visible': True, 'enabled': False, 'editable': True},
            'actionability_failures': ['disabled'],
        },
        root=tmp_path,
    )
    assert blocked['composer_readiness'] == 'blocked'
    assert 'disabled' in blocked['actionability_blockers']

    hold = evaluate_chatgpt_composer_witness_receipt(
        {
            'host': 'chatgpt.com',
            'path': '/',
            'title': 'ChatGPT',
            'visible_text': ['ChatGPT', 'Text box'],
            'main_region_text': ['Main conversation'],
            'composer_candidate_family': 'contenteditable',
            'main_region_scoped': True,
            'actionability': {'visible': True, 'enabled': True, 'editable': True},
            'rejected_higher_priority_candidates': ['textbox hidden'],
        },
        root=tmp_path,
    )
    assert hold['composer_quality'] == 'fragile'
    assert hold['composer_readiness'] == 'hold-for-recapture'
    assert 'after_readback' in hold['missing_field_keys']


def test_composer_witness_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-composer-witness-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-composer-witness-receipt-captures.json'
    payload = capture_chatgpt_composer_witness_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-composer-witness-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_composer_witness_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-COMPOSER-WITNESS-RECEIPT.json').exists()
    assert len(root_payload['composer_readiness_states']) == 7

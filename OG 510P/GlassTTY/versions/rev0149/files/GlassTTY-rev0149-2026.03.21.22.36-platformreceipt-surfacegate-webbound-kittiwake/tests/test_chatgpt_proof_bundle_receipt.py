from __future__ import annotations

import importlib.util
from pathlib import Path

from test_chatgpt_composer_witness_receipt import _seed

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('chatgpt_proof_bundle_receipt', ROOT / 'scripts' / 'chatgpt_proof_bundle_receipt.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_chatgpt_proof_bundle_receipt = MODULE.build_chatgpt_proof_bundle_receipt
evaluate_chatgpt_proof_bundle_receipt = MODULE.evaluate_chatgpt_proof_bundle_receipt
capture_chatgpt_proof_bundle_receipt = MODULE.capture_chatgpt_proof_bundle_receipt
write_root_chatgpt_proof_bundle_receipt = MODULE.write_root_chatgpt_proof_bundle_receipt
summarize_capture_history = MODULE.summarize_capture_history


def _good_bundle() -> dict:
    route = {
        'host': 'chatgpt.com',
        'path': '/',
        'auth_posture': 'logged-out',
        'title': 'ChatGPT',
        'visible_text': ['ChatGPT', 'Text box'],
        'main_region_text': ['Main conversation'],
        'capture_window_id': 'proof-window-1',
    }
    composer = {
        'composer_candidate_family': 'accessible-textbox',
        'locator_strategy': 'getByRole(textbox)',
        'main_region_scoped': True,
        'actionability': {'visible': True, 'enabled': True, 'editable': True, 'stable': True, 'receives_events': True},
        'write_method': 'fill',
        'after_text': 'GLASSTTY-CHECKPOINT',
        'expected_probe_text': 'GLASSTTY-CHECKPOINT',
        'capture_window_id': 'proof-window-1',
    }
    submit = {
        'submit_candidate_family': 'visible-submit-button',
        'submit_method': 'click',
        'submit_actionability': {'visible': True, 'enabled': True, 'stable': True, 'receives_events': True},
        'submit_attempted': True,
        'composer_cleared_after_submit': True,
        'generation_cues': ['streaming-started'],
        'completion_cues': ['response-actions-visible'],
        'latest_turn_scope': 'main conversation region',
        'latest_turn_text': 'GLASSTTY-CHECKPOINT',
        'generation_timeline': ['submit', 'streaming', 'complete'],
        'expected_exact_reply': 'GLASSTTY-CHECKPOINT',
        'capture_window_id': 'proof-window-1',
    }
    return {
        'browser_lane': 'chromium-live',
        'route_witness': route,
        'composer_witness': composer,
        'submit_witness': submit,
        'artifact_refs': [
            {'path': 'surface-screenshot.png', 'kind': 'surface-screenshot'},
            {'path': 'receiver-posture.md', 'kind': 'receiver-posture'},
            {'path': 'composer-candidates.json', 'kind': 'composer-candidates'},
            {'path': 'submit-evidence.json', 'kind': 'submit-evidence'},
            {'path': 'latest-turn.txt', 'kind': 'latest-turn'},
            {'path': 'generation-timeline.json', 'kind': 'generation-timeline'},
            {'path': 'probe-prompt.txt', 'kind': 'probe-prompt'},
        ],
    }


def test_proof_bundle_receipt_builds_contract(tmp_path: Path) -> None:
    _seed(tmp_path)
    payload = build_chatgpt_proof_bundle_receipt(root=tmp_path)
    assert payload['surface_key'] == 'chatgpt'
    assert payload['bundle_contract']['required_witnesses'] == ['route_witness', 'composer_witness', 'submit_witness']
    assert [item['state'] for item in payload['bundle_readiness_states']][0] == 'ready-for-held'


def test_proof_bundle_receipt_grades_ready_planning_and_hold(tmp_path: Path) -> None:
    _seed(tmp_path)
    ready = evaluate_chatgpt_proof_bundle_receipt(_good_bundle(), root=tmp_path)
    assert ready['bundle_readiness'] == 'ready-for-held'
    assert ready['recommended_bundle_status'] == 'hold'

    planning = evaluate_chatgpt_proof_bundle_receipt({}, root=tmp_path)
    assert planning['bundle_readiness'] == 'planning-only'
    assert planning['recommended_bundle_status'] == 'candidate'

    hold = _good_bundle()
    hold['artifact_refs'] = hold['artifact_refs'][:-2]
    hold['submit_witness'].pop('generation_timeline')
    hold['submit_witness']['submit_method'] = 'press Enter'
    hold['submit_witness']['submit_candidate_family'] = 'keyboard-submit'
    hold['submit_witness']['submit_actionability'] = {'composer_focused': True}
    payload = evaluate_chatgpt_proof_bundle_receipt(hold, root=tmp_path)
    assert payload['bundle_readiness'] == 'ready-with-caution'
    assert 'missing-generation-timeline-artifact' in payload['caution_flags']


def test_proof_bundle_receipt_capture_and_write_root(tmp_path: Path) -> None:
    _seed(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-proof-bundle-receipt'
    history_path = tmp_path / 'validation' / 'chatgpt-proof-bundle-receipt-captures.json'
    payload = capture_chatgpt_proof_bundle_receipt(root=tmp_path, output_dir=output_dir, history_path=history_path)
    assert (output_dir / 'chatgpt-proof-bundle-receipt.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['history_update']['capture_count_after_write'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    root_payload = write_root_chatgpt_proof_bundle_receipt(root=tmp_path)
    assert (tmp_path / 'CHATGPT-PROOF-BUNDLE-RECEIPT.json').exists()
    assert len(root_payload['bundle_readiness_states']) == 8

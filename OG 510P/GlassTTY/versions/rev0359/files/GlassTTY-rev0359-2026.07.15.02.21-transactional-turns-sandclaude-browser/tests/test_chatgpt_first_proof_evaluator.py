from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_evaluator', ROOT / 'scripts' / 'chatgpt_first_proof_evaluator.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

evaluate_payload = MODULE.evaluate_payload
evaluate_file = MODULE.evaluate_file
summarize_history = MODULE.summarize_history
required_check_registry_audit = MODULE.required_check_registry_audit
merge_required_checks = MODULE.merge_required_checks

PROBE_TEXT = 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT'
EXPECTED = 'GLASSTTY-CHECKPOINT'
ATTEMPT_ID = 'chatgpt-first-proof-001'
TAB_ID = 314159


def _assistant_latest_witness(text: str = EXPECTED) -> dict:
    return {
        'text': text,
        'selector_hint': 'article[data-message-author-role="assistant"]',
        'selection_policy': 'latest-visible-assistant-like-node-in-dom-order',
        'assistant_like': True,
        'author_role': 'assistant',
        'node_tag': 'article',
        'candidate_score': 0.91,
        'document_order_index': 120,
        'frame_depth': 0,
    }


def _user_turn_witness(text: str = PROBE_TEXT) -> dict:
    return {
        'text': text,
        'selector_hint': 'article[data-message-author-role="user"]',
        'selection_policy': 'latest-visible-user-like-node-in-dom-order',
        'user_like': True,
        'author_role': 'user',
        'node_tag': 'article',
        'candidate_score': 0.88,
        'document_order_index': 90,
        'frame_depth': 0,
    }


def _seed_kit(root: Path) -> None:
    (root / 'CHATGPT-FIRST-PROOF-KIT.json').write_text(json.dumps({
        'probe_prompt': {
            'text': PROBE_TEXT,
            'expected_exact_reply': EXPECTED,
        }
    }, indent=2) + '\n', encoding='utf-8')


def _route_safe_action_policy() -> dict:
    return {
        'submit_method': 'button-click-only',
        'keyboard_submit_enabled': False,
        'route_posture_allows_submit': True,
        'prompt_present_for_submit': True,
        'submit_button_found': True,
        'submit_button_min_score': 0.45,
    }


def _proof_live_gate_fields() -> dict:
    return {
        'proof_live_gate_verdict': 'proof-live-gate-ok',
        'proof_live_gate_ok': True,
        'proof_live_gate_checked_at': '2026-06-13T00:00:00Z',
        'proof_live_gate_expected': {
            'surface_key': 'chatgpt',
            'route_posture': 'plain-chat',
            'prompt_selector': '#prompt-textarea',
            'send_selector': '#composer-submit-button',
        },
        'proof_live_gate_observed': {
            'adapter': 'chatgpt',
            'route_posture': 'plain-chat',
            'prompt_selector': '#prompt-textarea',
            'prompt_text_matches_checkpoint': True,
            'submit_selector': '#composer-submit-button',
            'submit_signal_intent': True,
            'submit_signal_explicit': True,
            'submit_signal_disqualified': False,
        },
    }


def _reviewable_payload() -> dict:
    return {
        'surface_key': 'chatgpt',
        'attempt_id': ATTEMPT_ID,
        'privacy_redaction_review': {
            'review_required_before_publication': True,
            'publishable_without_redaction_review': False,
            'reviewer': 'local-operator',
            'notes': ['local proof evidence only; no public support use without human redaction review'],
        },
        'captures': {
            'after_write': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'tab_id': TAB_ID,
                'prompt': PROBE_TEXT,
                'metadata': {
                    'route_posture': 'plain-chat',
                    'action_policy': _route_safe_action_policy(),
                },
            },
            'after_generation': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/example',
                'tab_id': TAB_ID,
                'latest_output': EXPECTED,
                'latest_output_witness': _assistant_latest_witness(),
                'latest_user_turn_witness': _user_turn_witness(),
                'metadata': {'route_posture': 'plain-chat', 'generation_state': 'settled-or-idle', 'generation_stop_control_present': False},
            },
        },
        'actions': [
            {'sequence_index': 0, 'tab_id': TAB_ID, 'type': 'prompt.write', 'ok': True, 'readback': PROBE_TEXT, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/'},
            {'sequence_index': 1, 'tab_id': TAB_ID, 'type': 'prompt.submit', 'ok': True, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'operator_submit_confirmed': True, 'operator_action': 'sidepanel-chatgpt-first-proof-submit-button', 'submit_method': 'sidepanel-operator-click', **_proof_live_gate_fields(), 'composer_readback_before_submit': PROBE_TEXT, 'prompt_before_submit': PROBE_TEXT, 'submitted_prompt': PROBE_TEXT},
            {'sequence_index': 2, 'tab_id': TAB_ID, 'type': 'transcript.latest', 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'payload': {'text': EXPECTED, 'latest_output_witness': _assistant_latest_witness(), 'latest_user_turn_witness': _user_turn_witness(), 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'tab_id': TAB_ID}},
            {'sequence_index': 3, 'tab_id': TAB_ID, 'type': 'fixture.capture', 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'payload': {'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'tab_id': TAB_ID, 'metadata': {'route_posture': 'plain-chat', 'generation_state': 'settled-or-idle', 'generation_stop_control_present': False}}},
        ],
        'artifacts': {'screenshot_path': 'validation/live-proof-evidence/chatgpt/screenshot.png'},
    }



def test_required_check_registry_partitions_all_required_checks() -> None:
    audit = required_check_registry_audit()

    assert audit['ok'] is True
    assert audit['duplicates'] == []
    assert audit['missing_from_partition'] == []
    assert audit['extra_in_partition'] == []
    assert audit['overlap_between_global_and_attempt_scoped'] == []
    assert audit['required_check_count'] == len(MODULE.REQUIRED_CHECKS)
    assert audit['attempt_scoped_check_count'] + audit['global_only_check_count'] == audit['required_check_count']


def test_merge_required_checks_is_derived_from_required_check_registry() -> None:
    winning_attempt = {'checks': {key: True for key in MODULE.ATTEMPT_SCOPED_CHECKS}}

    checks = merge_required_checks(
        [winning_attempt],
        winning_attempt=winning_attempt,
        global_no_conflicts=True,
        global_privacy_redaction_review_present=True,
    )

    assert list(checks.keys()) == list(MODULE.REQUIRED_CHECKS)
    assert all(checks.values())

def test_evaluator_marks_reviewable_when_one_coherent_attempt_is_present(tmp_path: Path) -> None:
    _seed_kit(tmp_path)

    result = evaluate_payload(_reviewable_payload(), root=tmp_path)

    assert result['schema_version'] == 20
    assert result['ok'] is True
    assert result['verdict'] == 'reviewable-no-claim-widening'
    assert result['winning_attempt_id'] == ATTEMPT_ID
    assert result['missing_required_checks'] == []

    assert result['check_registry_audit']['ok'] is True
    assert set(result['check_registry_audit']['attempt_scoped_checks']).issubset(result['required_checks'])
    assert set(result['check_registry_audit']['global_only_checks']) == {'privacy_redaction_review_present', 'single_coherent_attempt_has_required_evidence', 'no_cross_surface_conflicts'}
    assert result['required_checks']['privacy_redaction_review_present'] is True
    assert result['required_checks']['single_coherent_attempt_has_required_evidence'] is True
    assert result['required_checks']['action_policy_supports_route_safe_submit'] is True
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['explicit_sequence_indices_monotonic'] is True
    assert result['required_checks']['ordered_sequence_has_chatgpt_action_witnesses'] is True
    assert result['required_checks']['post_submit_conversation_route_witness'] is True
    assert result['required_checks']['post_submit_conversation_route_transition'] is True
    assert result['required_checks']['proof_chain_same_tab_context'] is True
    assert result['required_checks']['post_latest_settled_witness_same_conversation_route'] is True
    assert result['required_checks']['operator_submit_attestation_present'] is True
    assert result['required_checks']['proof_live_gate_ok_before_submit'] is True
    assert result['required_checks']['submit_prompt_readback_matches_probe'] is True
    assert result['required_checks']['write_and_submit_readbacks_exact_probe'] is True
    assert result['required_checks']['post_latest_generation_settled_witness'] is True
    assert result['required_checks']['post_latest_settled_witness_sequence_and_surface'] is True
    assert result['required_checks']['transcript_latest_assistant_node_witness'] is True
    assert result['required_checks']['transcript_latest_witness_text_matches_reply'] is True
    assert result['required_checks']['transcript_latest_assistant_witness_not_aggregate_parent'] is True
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is True
    assert result['required_checks']['transcript_latest_user_witness_not_aggregate_parent'] is True
    assert result['required_checks']['transcript_latest_user_before_assistant_witness_order'] is True
    assert result['required_checks']['transcript_latest_turn_pair_explicit_frame_context'] is True
    assert result['support_claim_effect'].startswith('none;')


def test_evaluator_blocks_live_reviewable_without_proof_live_gate(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    for key in list(_proof_live_gate_fields()):
        payload['actions'][1].pop(key, None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['operator_submit_attestation_present'] is True
    assert result['required_checks']['proof_live_gate_ok_before_submit'] is False
    assert 'proof_live_gate_ok_before_submit' in result['missing_required_checks']




def test_evaluator_blocks_missing_privacy_redaction_review_record(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload.pop('privacy_redaction_review')

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['privacy_redaction_review_present'] is False
    assert 'privacy_redaction_review_present' in result['missing_required_checks']
    assert result['observed']['privacy_redaction_review_present'] is False



def test_evaluator_blocks_transcript_latest_without_assistant_node_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload'].pop('latest_output_witness', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['transcript_latest_assistant_node_witness'] is False
    assert 'transcript_latest_assistant_node_witness' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_with_non_assistant_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_output_witness'] = {
        'text': EXPECTED,
        'selector_hint': 'main',
        'selection_policy': 'latest-visible-assistant-like-node-in-dom-order',
        'assistant_like': False,
        'author_role': 'user',
    }

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_assistant_node_witness'] is False
    assert 'transcript_latest_assistant_node_witness' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_when_assistant_witness_text_mismatches_reply(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['text'] = EXPECTED
    payload['actions'][2]['payload']['latest_output_witness'] = _assistant_latest_witness('GLASSTTY-CHECKPOINT drift')

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['transcript_latest_assistant_node_witness'] is True
    assert result['required_checks']['transcript_latest_witness_text_matches_reply'] is False
    assert 'transcript_latest_witness_text_matches_reply' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_without_user_turn_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload'].pop('latest_user_turn_witness', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['transcript_latest_witness_text_matches_reply'] is True
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is False
    assert 'transcript_latest_user_turn_witness_text_matches_prompt' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_when_user_turn_witness_text_mismatches_prompt(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_user_turn_witness'] = _user_turn_witness('Reply with exactly this text and nothing else: WRONG')

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['transcript_latest_witness_text_matches_reply'] is True
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is False
    assert 'transcript_latest_user_turn_witness_text_matches_prompt' in result['missing_required_checks']



def test_evaluator_blocks_transcript_latest_when_turn_witness_order_is_missing(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_user_turn_witness'].pop('document_order_index', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is True
    assert result['required_checks']['transcript_latest_user_before_assistant_witness_order'] is False
    assert 'transcript_latest_user_before_assistant_witness_order' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_when_user_turn_witness_follows_assistant_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_user_turn_witness']['document_order_index'] = 240
    payload['actions'][2]['payload']['latest_output_witness']['document_order_index'] = 120

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is True
    assert result['required_checks']['transcript_latest_user_before_assistant_witness_order'] is False
    assert 'transcript_latest_user_before_assistant_witness_order' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_when_turn_pair_frame_context_is_implicit(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_user_turn_witness'].pop('frame_depth', None)
    payload['actions'][2]['payload']['latest_output_witness'].pop('frame_depth', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_user_before_assistant_witness_order'] is True
    assert result['required_checks']['transcript_latest_turn_pair_explicit_frame_context'] is False
    assert 'transcript_latest_turn_pair_explicit_frame_context' in result['missing_required_checks']


def test_evaluator_blocks_transcript_latest_when_turn_pair_frame_context_differs(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['payload']['latest_user_turn_witness']['frame_depth'] = 1
    payload['actions'][2]['payload']['latest_user_turn_witness']['frame_path'] = 'iframe#composer'
    payload['actions'][2]['payload']['latest_output_witness']['frame_depth'] = 1
    payload['actions'][2]['payload']['latest_output_witness']['frame_path'] = 'iframe#conversation'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_user_before_assistant_witness_order'] is False
    assert result['required_checks']['transcript_latest_turn_pair_explicit_frame_context'] is False
    assert 'transcript_latest_turn_pair_explicit_frame_context' in result['missing_required_checks']

def test_evaluator_blocks_when_latest_exact_reply_is_missing(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['captures']['after_generation']['latest_output'] = 'GLASSTTY-CHECKPOINT.'
    payload['actions'][2]['payload']['text'] = 'GLASSTTY-CHECKPOINT.'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['verdict'] == 'blocked'
    assert 'latest_turn_exact_reply' in result['missing_required_checks']
    assert 'single_coherent_attempt_has_required_evidence' in result['missing_required_checks']


def test_evaluator_blocks_when_required_facts_are_split_across_attempts(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = {
        'surface_key': 'chatgpt',
        'captures': {
            'write': {
                'attempt_id': 'write-attempt',
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'tab_id': TAB_ID,
                'prompt': PROBE_TEXT,
                'metadata': {
                    'route_posture': 'plain-chat',
                    'action_policy': _route_safe_action_policy(),
                },
            },
            'generation': {
                'attempt_id': 'generation-attempt',
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/example',
                'tab_id': TAB_ID,
                'latest_output': EXPECTED,
                'metadata': {'route_posture': 'plain-chat'},
            },
        },
        'actions': [
            {'attempt_id': 'write-attempt', 'sequence_index': 0, 'type': 'prompt.write', 'ok': True, 'readback': PROBE_TEXT, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/'},
            {'attempt_id': 'generation-attempt', 'sequence_index': 1, 'type': 'prompt.submit', 'ok': True, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'operator_submit_confirmed': True, 'operator_action': 'sidepanel-chatgpt-first-proof-submit-button', 'submit_method': 'sidepanel-operator-click', 'composer_readback_before_submit': PROBE_TEXT, 'prompt_before_submit': PROBE_TEXT, 'submitted_prompt': PROBE_TEXT},
            {'attempt_id': 'generation-attempt', 'sequence_index': 2, 'type': 'transcript.latest', 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'payload': {'text': EXPECTED, 'latest_output_witness': _assistant_latest_witness(), 'latest_user_turn_witness': _user_turn_witness(), 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'tab_id': TAB_ID}},
        ],
    }

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['adapter_is_chatgpt'] is True
    assert result['required_checks']['latest_turn_exact_reply'] is True
    assert result['required_checks']['single_coherent_attempt_has_required_evidence'] is False
    assert 'single_coherent_attempt_has_required_evidence' in result['missing_required_checks']
    assert sorted(attempt['attempt_id'] for attempt in result['attempts']) == ['__implicit_attempt__', 'generation-attempt', 'write-attempt']


def test_evaluator_blocks_cross_surface_conflicts_even_when_chatgpt_attempt_passes(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['unrelated_capture'] = {
        'attempt_id': 'other-surface',
        'adapter': 'other-provider',
        'url': 'https://example.invalid/chat/example',
        'surface_key': 'other-provider',
    }

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['single_coherent_attempt_has_required_evidence'] is True
    assert result['required_checks']['no_cross_surface_conflicts'] is False
    assert 'no_cross_surface_conflicts' in result['missing_required_checks']
    assert result['observed']['cross_surface_conflicts']['non_chatgpt_adapters'] == ['other-provider']


def test_evaluator_blocks_missing_route_safe_submit_policy(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    del payload['captures']['after_write']['metadata']['action_policy']

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['action_policy_supports_route_safe_submit'] is False
    assert 'action_policy_supports_route_safe_submit' in result['missing_required_checks']


def test_privacy_review_flags_email_and_raw_html_without_making_it_publishable(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['captures']['after_write']['html_samples'] = {'prompt': '<div data-testid="prompt-textarea">x</div>'}
    payload['captures']['after_write']['account_note'] = 'signed in as reviewer@example.com'

    result = evaluate_payload(payload, root=tmp_path)

    privacy = result['privacy_review']
    assert result['ok'] is True
    assert privacy['scan_completed'] is True
    assert privacy['publishable_without_redaction_review'] is False
    assert privacy['review_required_before_publication'] is True
    assert privacy['flags']['possible_email_address'] == ['reviewer@example.com']
    assert privacy['flags']['raw_html_or_html_sample_present'] is True



def test_evaluator_blocks_fixture_only_prompt_echo_without_write_action(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'] = [action for action in payload['actions'] if action.get('type') != 'prompt.write']

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['composer_write_readback_contains_probe'] is False
    assert 'composer_write_readback_contains_probe' in result['missing_required_checks']


def test_evaluator_blocks_fixture_only_latest_output_without_transcript_latest_action(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'] = [action for action in payload['actions'] if action.get('type') != 'transcript.latest']

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['latest_turn_exact_reply'] is True
    assert result['required_checks']['transcript_latest_action_exact_reply'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is False
    assert 'transcript_latest_action_exact_reply' in result['missing_required_checks']
    assert 'ordered_write_submit_latest_sequence' in result['missing_required_checks']


def test_evaluator_blocks_out_of_order_write_submit_latest_sequence(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'] = [
        {'sequence_index': 0, 'type': 'transcript.latest', 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'payload': {'text': EXPECTED, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'tab_id': TAB_ID}},
        {'sequence_index': 1, 'type': 'prompt.write', 'ok': True, 'readback': PROBE_TEXT, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/'},
        {'sequence_index': 2, 'type': 'prompt.submit', 'ok': True, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/'},
    ]

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is False
    assert 'ordered_write_submit_latest_sequence' in result['missing_required_checks']


def test_evaluator_accepts_sidepanel_manual_capture_shape(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = {
        'schema_version': 1,
        'surface_key': 'chatgpt',
        'capture_kind': 'sidepanel-manual-chatgpt-first-proof',
        'attempt_id': ATTEMPT_ID,
        'privacy_redaction_review': {
            'review_required_before_publication': True,
            'publishable_without_redaction_review': False,
        },
        'actions': [
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 0, 'tab_id': TAB_ID, 'type': 'prompt.write', 'ok': True, 'readback': PROBE_TEXT, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'payload': {'ok': True, 'readback': PROBE_TEXT, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'tab_id': TAB_ID}},
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 1, 'type': 'fixture.capture', 'payload': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/',
                'tab_id': TAB_ID,
                'prompt': PROBE_TEXT,
                'metadata': {
                    'route_posture': 'plain-chat',
                    'route_evidence': ['path:/', 'composer:present', 'plain-chat-path-and-composer'],
                    'action_policy': _route_safe_action_policy(),
                },
            }},
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 2, 'type': 'state.snapshot', 'payload': {'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'prompt': PROBE_TEXT}},
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 3, 'tab_id': TAB_ID, 'type': 'prompt.submit', 'ok': True, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'operator_submit_confirmed': True, 'operator_action': 'sidepanel-chatgpt-first-proof-submit-button', 'submit_method': 'sidepanel-operator-click', **_proof_live_gate_fields(), 'composer_readback_before_submit': PROBE_TEXT, 'prompt_before_submit': PROBE_TEXT, 'submitted_prompt': PROBE_TEXT, 'payload': {'ok': True, 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/', 'tab_id': TAB_ID, 'operator_submit_confirmed': True, 'operator_action': 'sidepanel-chatgpt-first-proof-submit-button', 'submit_method': 'sidepanel-operator-click', **_proof_live_gate_fields(), 'composer_readback_before_submit': PROBE_TEXT, 'prompt_before_submit': PROBE_TEXT, 'submitted_prompt': PROBE_TEXT}},
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 4, 'tab_id': TAB_ID, 'type': 'transcript.latest', 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'payload': {'text': EXPECTED, 'latest_output_witness': _assistant_latest_witness(), 'latest_user_turn_witness': _user_turn_witness(), 'adapter': 'chatgpt', 'url': 'https://chatgpt.com/c/example', 'tab_id': TAB_ID}},
            {'attempt_id': ATTEMPT_ID, 'sequence_index': 5, 'type': 'fixture.capture', 'payload': {
                'adapter': 'chatgpt',
                'url': 'https://chatgpt.com/c/example',
                'tab_id': TAB_ID,
                'latest_output': EXPECTED,
                'latest_output_witness': _assistant_latest_witness(),
                'latest_user_turn_witness': _user_turn_witness(),
                'metadata': {'route_posture': 'plain-chat', 'generation_state': 'settled-or-idle', 'generation_stop_control_present': False},
            }},
        ],
    }

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is True
    assert result['winning_attempt_id'] == ATTEMPT_ID


def test_evaluator_blocks_missing_per_action_url_adapter_witnesses(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    for action in payload['actions']:
        action.pop('adapter', None)
        action.pop('url', None)
        if isinstance(action.get('payload'), dict):
            action['payload'].pop('adapter', None)
            action['payload'].pop('url', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['explicit_sequence_indices_monotonic'] is True
    assert result['required_checks']['ordered_sequence_has_chatgpt_action_witnesses'] is False
    assert 'ordered_sequence_has_chatgpt_action_witnesses' in result['missing_required_checks']


def test_evaluator_blocks_non_monotonic_explicit_sequence_indices(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][0]['sequence_index'] = 2
    payload['actions'][1]['sequence_index'] = 1
    payload['actions'][2]['sequence_index'] = 0

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['ordered_sequence_has_chatgpt_action_witnesses'] is True
    assert result['required_checks']['explicit_sequence_indices_monotonic'] is False
    assert 'explicit_sequence_indices_monotonic' in result['missing_required_checks']


def test_evaluator_blocks_latest_turn_without_post_submit_conversation_route(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['captures']['after_generation']['url'] = 'https://chatgpt.com/'
    payload['actions'][2]['url'] = 'https://chatgpt.com/'
    payload['actions'][2]['payload']['url'] = 'https://chatgpt.com/'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['explicit_sequence_indices_monotonic'] is True
    assert result['required_checks']['ordered_sequence_has_chatgpt_action_witnesses'] is True
    assert result['required_checks']['post_submit_conversation_route_witness'] is False
    assert 'post_submit_conversation_route_witness' in result['missing_required_checks']


def test_evaluator_blocks_write_submit_latest_across_multiple_tabs(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][2]['tab_id'] = TAB_ID + 1
    payload['actions'][2]['payload']['tab_id'] = TAB_ID + 1

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['post_submit_conversation_route_witness'] is True
    assert result['required_checks']['proof_chain_same_tab_context'] is False
    assert 'proof_chain_same_tab_context' in result['missing_required_checks']


def test_evaluator_blocks_missing_explicit_tab_context_on_sequence(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    for action in payload['actions'][:3]:
        action.pop('tab_id', None)
        if isinstance(action.get('payload'), dict):
            action['payload'].pop('tab_id', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['proof_chain_same_tab_context'] is False
    assert 'proof_chain_same_tab_context' in result['missing_required_checks']


def test_evaluator_blocks_settled_witness_from_different_tab(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3]['tab_id'] = TAB_ID + 2
    payload['actions'][3]['payload']['tab_id'] = TAB_ID + 2

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_latest_settled_witness_sequence_and_surface'] is True
    assert result['required_checks']['proof_chain_same_tab_context'] is False
    assert 'proof_chain_same_tab_context' in result['missing_required_checks']


def test_evaluator_blocks_settled_witness_from_different_conversation_route(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3]['url'] = 'https://chatgpt.com/c/different'
    payload['actions'][3]['payload']['url'] = 'https://chatgpt.com/c/different'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_submit_conversation_route_witness'] is True
    assert result['required_checks']['post_submit_conversation_route_transition'] is True
    assert result['required_checks']['proof_chain_same_tab_context'] is True
    assert result['required_checks']['post_latest_settled_witness_same_conversation_route'] is False
    assert 'post_latest_settled_witness_same_conversation_route' in result['missing_required_checks']


def test_evaluator_blocks_missing_operator_submit_attestation(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][1].pop('operator_submit_confirmed', None)
    payload['actions'][1].pop('operator_action', None)
    payload['actions'][1].pop('submit_method', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['operator_submit_attestation_present'] is False
    assert 'operator_submit_attestation_present' in result['missing_required_checks']


def test_evaluator_blocks_missing_submit_prompt_readback(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    for key in ('composer_readback_before_submit', 'prompt_before_submit', 'submitted_prompt'):
        payload['actions'][1].pop(key, None)
        if isinstance(payload['actions'][1].get('payload'), dict):
            payload['actions'][1]['payload'].pop(key, None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['operator_submit_attestation_present'] is True
    assert result['required_checks']['submit_prompt_readback_matches_probe'] is False
    assert 'submit_prompt_readback_matches_probe' in result['missing_required_checks']


def test_evaluator_blocks_mismatched_submit_prompt_readback(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][1]['composer_readback_before_submit'] = 'Reply with exactly this text and nothing else: WRONG'
    payload['actions'][1]['prompt_before_submit'] = 'Reply with exactly this text and nothing else: WRONG'
    payload['actions'][1]['submitted_prompt'] = 'Reply with exactly this text and nothing else: WRONG'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['operator_submit_attestation_present'] is True
    assert result['required_checks']['submit_prompt_readback_matches_probe'] is False
    assert 'submit_prompt_readback_matches_probe' in result['missing_required_checks']


def test_evaluator_blocks_write_readback_that_only_contains_probe(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][0]['readback'] = f'{PROBE_TEXT} trailing draft residue'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['composer_write_readback_contains_probe'] is True
    assert result['required_checks']['write_and_submit_readbacks_exact_probe'] is False
    assert 'write_and_submit_readbacks_exact_probe' in result['missing_required_checks']


def test_evaluator_blocks_submit_readback_that_only_contains_probe(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][1]['composer_readback_before_submit'] = f'{PROBE_TEXT} trailing draft residue'
    payload['actions'][1]['prompt_before_submit'] = f'{PROBE_TEXT} trailing draft residue'
    payload['actions'][1]['submitted_prompt'] = f'{PROBE_TEXT} trailing draft residue'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['submit_prompt_readback_matches_probe'] is True
    assert result['required_checks']['write_and_submit_readbacks_exact_probe'] is False
    assert 'write_and_submit_readbacks_exact_probe' in result['missing_required_checks']


def test_evaluator_blocks_missing_post_latest_settled_generation_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['captures']['after_generation']['metadata']['generation_state'] = 'streaming-or-stoppable'
    payload['captures']['after_generation']['metadata']['generation_stop_control_present'] = True
    payload['actions'][3]['payload']['metadata']['generation_state'] = 'streaming-or-stoppable'
    payload['actions'][3]['payload']['metadata']['generation_stop_control_present'] = True

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_submit_conversation_route_witness'] is True
    assert result['required_checks']['post_latest_generation_settled_witness'] is False
    assert 'post_latest_generation_settled_witness' in result['missing_required_checks']



def test_evaluator_blocks_settled_generation_witness_without_later_sequence_index(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3]['sequence_index'] = 2

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_latest_generation_settled_witness'] is True
    assert result['required_checks']['post_latest_settled_witness_sequence_and_surface'] is False
    assert 'post_latest_settled_witness_sequence_and_surface' in result['missing_required_checks']


def test_evaluator_blocks_settled_generation_witness_without_chatgpt_action_witness(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3].pop('adapter', None)
    payload['actions'][3].pop('url', None)
    payload['actions'][3]['payload'].pop('adapter', None)
    payload['actions'][3]['payload'].pop('url', None)

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_latest_generation_settled_witness'] is True
    assert result['required_checks']['post_latest_settled_witness_sequence_and_surface'] is False
    assert 'post_latest_settled_witness_sequence_and_surface' in result['missing_required_checks']


def test_evaluator_blocks_settled_generation_witness_before_latest_only(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['captures']['after_generation']['metadata'].pop('generation_state', None)
    payload['captures']['after_generation']['metadata'].pop('generation_stop_control_present', None)
    payload['actions'].pop()
    payload['actions'].insert(2, {
        'attempt_id': ATTEMPT_ID,
        'sequence_index': 2,
        'type': 'fixture.capture',
        'adapter': 'chatgpt',
        'url': 'https://chatgpt.com/',
        'metadata': {'route_posture': 'plain-chat', 'generation_state': 'settled-or-idle', 'generation_stop_control_present': False},
    })
    payload['actions'][3]['sequence_index'] = 3

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_latest_generation_settled_witness'] is False
    assert 'post_latest_generation_settled_witness' in result['missing_required_checks']

def test_evaluate_file_writes_report_summary_and_history(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    input_path = tmp_path / 'capture.json'
    input_path.write_text(json.dumps(_reviewable_payload(), indent=2) + '\n', encoding='utf-8')
    output_dir = tmp_path / 'validation' / 'latest' / 'chatgpt-first-proof-evaluation'
    history_path = tmp_path / 'validation' / 'chatgpt-first-proof-evaluation-captures.json'

    result = evaluate_file(input_path, root=tmp_path, output_dir=output_dir, history_path=history_path)
    history = summarize_history(history_path)

    assert result['ok'] is True
    assert (output_dir / 'chatgpt-first-proof-evaluation.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert result['history_update']['capture_count_after_write'] == 1
    assert history['capture_count'] == 1
    assert history['latest_capture']['verdict'] == 'reviewable-no-claim-widening'
    assert history['latest_capture']['winning_attempt_id'] == ATTEMPT_ID
    assert history['latest_capture']['privacy_review_required_before_publication'] is True


def test_evaluator_blocks_submit_that_starts_inside_existing_conversation_without_new_route_transition(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    for index in (0, 1):
        payload['actions'][index]['url'] = 'https://chatgpt.com/c/stale'
        if isinstance(payload['actions'][index].get('payload'), dict):
            payload['actions'][index]['payload']['url'] = 'https://chatgpt.com/c/stale'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_submit_conversation_route_witness'] is True
    assert result['required_checks']['post_submit_conversation_route_transition'] is False
    assert 'post_submit_conversation_route_transition' in result['missing_required_checks']


def test_evaluator_blocks_preexisting_assistant_checkpoint_before_operator_submit(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    preexisting = {
        'sequence_index': 1,
        'tab_id': TAB_ID,
        'type': 'transcript.latest',
        'adapter': 'chatgpt',
        'url': 'https://chatgpt.com/c/preexisting',
        'payload': {
            'text': EXPECTED,
            'latest_output_witness': _assistant_latest_witness(),
            'latest_user_turn_witness': _user_turn_witness(),
            'adapter': 'chatgpt',
            'url': 'https://chatgpt.com/c/preexisting',
            'tab_id': TAB_ID,
        },
    }
    payload['actions'] = [payload['actions'][0], preexisting, payload['actions'][1], payload['actions'][3]]
    payload['actions'][2]['sequence_index'] = 2
    payload['actions'][3]['sequence_index'] = 3

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is False
    assert 'ordered_write_submit_latest_sequence' in result['missing_required_checks']


def test_evaluator_blocks_latest_user_witness_selected_from_wrong_wrapper(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    wrong_wrapper = _user_turn_witness()
    wrong_wrapper['witness_scope'] = 'conversation-wrapper-parent'
    wrong_wrapper['visible_text'] = f'{PROBE_TEXT}\n{EXPECTED}'
    wrong_wrapper['role_mixture_detected'] = True
    payload['actions'][2]['payload']['latest_user_turn_witness'] = wrong_wrapper

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_user_turn_witness_text_matches_prompt'] is True
    assert result['required_checks']['transcript_latest_user_witness_not_aggregate_parent'] is False
    assert 'transcript_latest_user_witness_not_aggregate_parent' in result['missing_required_checks']


def test_evaluator_blocks_assistant_witness_selected_from_parent_turn_pair_wrapper(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    parent_wrapper = _assistant_latest_witness()
    parent_wrapper['witness_scope'] = 'turn-pair-parent-wrapper'
    parent_wrapper['visible_text'] = f'{PROBE_TEXT}\n{EXPECTED}'
    parent_wrapper['contains_user_turn_text'] = True
    payload['actions'][2]['payload']['latest_output_witness'] = parent_wrapper

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_witness_text_matches_reply'] is True
    assert result['required_checks']['transcript_latest_assistant_witness_not_aggregate_parent'] is False
    assert 'transcript_latest_assistant_witness_not_aggregate_parent' in result['missing_required_checks']


def test_evaluator_blocks_exact_latest_reply_when_generation_is_still_streaming(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3]['payload']['metadata']['generation_state'] = 'streaming'
    payload['actions'][3]['payload']['metadata']['generation_stop_control_present'] = True

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['transcript_latest_action_exact_reply'] is True
    assert result['required_checks']['post_latest_generation_settled_witness'] is False
    assert 'post_latest_generation_settled_witness' in result['missing_required_checks']


def test_evaluator_blocks_post_latest_settled_witness_from_root_route(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][3]['url'] = 'https://chatgpt.com/'
    payload['actions'][3]['payload']['url'] = 'https://chatgpt.com/'

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['post_latest_settled_witness_sequence_and_surface'] is True
    assert result['required_checks']['post_latest_settled_witness_same_conversation_route'] is False
    assert 'post_latest_settled_witness_same_conversation_route' in result['missing_required_checks']


def test_evaluator_blocks_equal_sequence_indices_even_when_all_text_matches(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['actions'][0]['sequence_index'] = 7
    payload['actions'][1]['sequence_index'] = 7
    payload['actions'][2]['sequence_index'] = 7

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['required_checks']['ordered_write_submit_latest_sequence'] is True
    assert result['required_checks']['explicit_sequence_indices_monotonic'] is False
    assert 'explicit_sequence_indices_monotonic' in result['missing_required_checks']


def test_evaluator_marks_rehearsal_as_harness_ok_but_not_live_reviewable(tmp_path: Path) -> None:
    _seed_kit(tmp_path)
    payload = _reviewable_payload()
    payload['proof_mode'] = 'offline-rehearsal'
    payload['rehearsal_only'] = True

    result = evaluate_payload(payload, root=tmp_path)

    assert result['ok'] is False
    assert result['harness_ok'] is True
    assert result['verdict'] == 'rehearsal-harness-ok-not-live'
    assert result['proof_mode'] == 'offline-rehearsal'
    assert result['rehearsal_only'] is True
    assert result['missing_required_checks'] == []

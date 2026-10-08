from __future__ import annotations

from chatgpt_surface_contract import build_contract, check_contract


def _surface() -> dict[str, object]:
    return {
        'tool': 'glasstty-chatgpt-surface-oracle-userscript',
        'version': 'rev0333-test',
        'report_kind': 'send-drill-after-write',
        'page': {'host': 'chatgpt.com', 'pathname': '/c/example'},
        'route_posture_guess': {'posture': 'plain-chat', 'pathname': '/c/example'},
        'counts': {
            'buttons': 20,
            'forms': 1,
            'iframes': 1,
            'role_textbox': 1,
            'contenteditable': 1,
            'message_author_role_nodes': 4,
            'assistant_role_nodes': 2,
            'user_role_nodes': 2,
            'conversation_turn_like_nodes': 4,
        },
        'selector_probe': {
            'prompt': [{'selector': '#prompt-textarea', 'count': 1}],
            'send': [{'selector': 'button[data-testid="send-button"]', 'count': 1}],
        },
        'adapter_recommendation': {
            'best_prompt_selector': '#prompt-textarea',
            'best_prompt_score': 1.36,
            'best_send_selector': '#composer-submit-button',
            'best_send_score': 1.45,
            'blocked_send_selector': '#composer-plus-btn',
            'blocked_send_score': -0.85,
            'latest_assistant_selector': '[data-message-author-role="assistant"]',
            'latest_user_selector': '[data-message-author-role="user"]',
            'has_explicit_author_roles': True,
            'plain_chat_submit_allowed_by_route_guess': True,
        },
        'send_state': {
            'strict_send_found': True,
            'blocked_send_control_found': True,
            'best_strict_send': {
                'selector': '#composer-submit-button',
                'id': 'composer-submit-button',
                'data_testid': 'send-button',
                'aria_label': 'Send prompt',
                'score': 1.45,
            },
            'best_blocked_control': {
                'selector': '#composer-plus-btn',
                'id': 'composer-plus-btn',
                'data_testid': 'composer-plus-btn',
                'aria_label': 'Add files and more',
                'score': -0.85,
            },
        },
        'top_candidates': {
            'send': {
                'selector': '#composer-submit-button',
                'id': 'composer-submit-button',
                'data_testid': 'send-button',
                'aria_label': 'Send prompt',
            }
        },
    }


def test_build_contract_captures_chatgpt_live_send_lock() -> None:
    contract = build_contract(_surface(), source_path='report.json')

    assert contract['scope']['surface_key'] == 'chatgpt'
    assert contract['scope']['provider_policy'].startswith('ChatGPT only')
    assert contract['required']['prompt_selector'] == '#prompt-textarea'
    assert contract['required']['strict_send']['selector'] == '#composer-submit-button'
    assert contract['required']['strict_send']['data_testid'] == 'send-button'
    assert contract['known_non_send_controls'][0]['selector'] == '#composer-plus-btn'


def test_contract_check_accepts_matching_surface() -> None:
    surface = _surface()
    contract = build_contract(surface)

    result = check_contract(surface, contract)

    assert result['verdict'] == 'surface-contract-ok'
    assert result['blockers'] == []
    assert result['summary']['strict_send_selector'] == '#composer-submit-button'


def test_contract_check_blocks_when_send_moves_to_plus_button() -> None:
    surface = _surface()
    contract = build_contract(surface)
    drifted = _surface()
    drifted['send_state'] = {
        'best_strict_send': {
            'selector': '#composer-plus-btn',
            'data_testid': 'composer-plus-btn',
            'aria_label': 'Add files and more',
            'score': 0.9,
        }
    }
    drifted['adapter_recommendation'] = {
        **drifted['adapter_recommendation'],
        'best_send_selector': '#composer-plus-btn',
        'best_send_score': 0.9,
    }

    result = check_contract(drifted, contract)

    assert result['verdict'] == 'surface-drift-blocker'
    signals = {item['signal'] for item in result['blockers']}
    assert 'missing_strict_send_selector' in signals
    assert 'strict_send_became_known_non_send_control' in signals


def test_contract_check_warns_on_count_shift_without_breaking_core_selectors() -> None:
    surface = _surface()
    contract = build_contract(surface)
    shifted = _surface()
    shifted['counts'] = {**shifted['counts'], 'buttons': 60}

    result = check_contract(shifted, contract)

    assert result['verdict'] == 'surface-drift-warning'
    assert any(item['signal'] == 'count_shift_large' for item in result['warnings'])


def test_contract_check_returns_operator_recommendations_for_drift() -> None:
    contract = build_contract(_surface())
    drifted = _surface()
    drifted['send_state'] = {
        'best_strict_send': {
            'selector': '#composer-plus-btn',
            'data_testid': 'composer-plus-btn',
            'aria_label': 'Add files and more',
            'score': 0.9,
        }
    }
    drifted['adapter_recommendation'] = {
        **drifted['adapter_recommendation'],
        'best_send_selector': '#composer-plus-btn',
        'best_send_score': 0.9,
    }

    result = check_contract(drifted, contract)

    assert result['recommended_next_action']
    assert any(row['signal'] == 'missing_strict_send_selector' for row in result['recommendations'])
    assert any('safe send-state drill' in row['next_step'] for row in result['recommendations'])

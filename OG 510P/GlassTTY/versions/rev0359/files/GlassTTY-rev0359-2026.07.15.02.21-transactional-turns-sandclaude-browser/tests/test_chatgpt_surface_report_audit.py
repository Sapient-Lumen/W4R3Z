from __future__ import annotations

from chatgpt_surface_report_audit import audit_surface, extract_json_object


def _base_capsule() -> dict[str, object]:
    return {
        'capsule_schema_version': 1,
        'tool': 'glasstty-chatgpt-surface-capsule',
        'version': 'rev0330-test',
        'page': {'host': 'chatgpt.com', 'pathname': '/c/example'},
        'route_posture_guess': {'posture': 'plain-chat'},
        'counts': {'assistant_role_nodes': 2, 'user_role_nodes': 2},
        'adapter_recommendation': {
            'best_prompt_selector': '#prompt-textarea',
            'best_prompt_score': 1.2,
            'best_send_selector': '#composer-submit-button',
            'best_send_score': 0.8,
            'has_explicit_author_roles': True,
            'latest_assistant_selector': '[data-message-author-role="assistant"]',
            'latest_user_selector': '[data-message-author-role="user"]',
        },
        'top_candidates': {
            'send': {
                'selector': '#composer-submit-button',
                'id': 'composer-submit-button',
                'data_testid': 'send-button',
                'aria_label': 'Send prompt',
            },
        },
    }


def test_surface_report_audit_accepts_capsule_line() -> None:
    payload = _base_capsule()
    line = 'GLASSTTY_SURFACE_CAPSULE_JSON=' + __import__('json').dumps(payload)

    parsed = extract_json_object(line)
    audit = audit_surface(parsed)

    assert audit['source_kind'] == 'surface-capsule'
    assert audit['verdict'] == 'adapter-ready-surface'
    assert audit['signals']['chatgpt_host'] is True
    assert audit['signals']['plain_chat_route'] is True
    assert audit['signals']['prompt_ok'] is True
    assert audit['signals']['send_ok'] is True
    assert audit['signals']['strict_send_live_lock'] is True


def test_surface_report_audit_marks_missing_send_as_partial() -> None:
    payload = _base_capsule()
    payload['adapter_recommendation'] = {
        **payload['adapter_recommendation'],
        'best_send_selector': None,
        'best_send_score': 0,
    }

    audit = audit_surface(payload)

    assert audit['verdict'] == 'partial-surface-needs-send-or-turn-witness'
    assert audit['signals']['send_ok'] is False
    assert 're-run after typing harmless text in the composer' in audit['recommendations']


def test_surface_report_audit_rejects_composer_plus_as_send() -> None:
    payload = _base_capsule()
    payload['adapter_recommendation'] = {
        **payload['adapter_recommendation'],
        'best_send_selector': '#composer-plus-btn',
        'best_send_score': 0.46,
    }
    payload['top_candidates'] = {
        'send': {
            'selector': '#composer-plus-btn',
            'id': 'composer-plus-btn',
            'data_testid': 'composer-plus-btn',
            'aria_label': 'Add files and more',
        },
    }

    audit = audit_surface(payload)

    assert audit['verdict'] == 'partial-surface-needs-send-or-turn-witness'
    assert audit['signals']['send_false_positive'] is True
    assert audit['signals']['send_ok'] is False
    assert 'send candidate looks like a non-submit composer control' in audit['issues']


def test_surface_report_audit_marks_empty_composer_missing_send_as_expected() -> None:
    payload = _base_capsule()
    payload['adapter_recommendation'] = {
        **payload['adapter_recommendation'],
        'best_send_selector': None,
        'best_send_score': 0,
    }
    payload['send_readiness'] = {
        'empty_composer_missing_send_is_allowed': True,
        'strict_send_found': False,
    }

    audit = audit_surface(payload)

    assert audit['verdict'] == 'partial-surface-needs-send-or-turn-witness'
    assert audit['signals']['empty_composer_missing_send_is_allowed'] is True
    assert 'send may appear only after composer text exists' in audit['recommendations']


def test_surface_report_audit_accepts_userscript_capsule_prefix() -> None:
    payload = _base_capsule()
    payload['tool'] = 'glasstty-chatgpt-surface-oracle-userscript'
    line = 'GLASSTTY_USER_SURFACE_CAPSULE_JSON=' + __import__('json').dumps(payload)

    parsed = extract_json_object(line)
    audit = audit_surface(parsed)

    assert audit['source_kind'] == 'surface-capsule'
    assert audit['source_tool'] == 'glasstty-chatgpt-surface-oracle-userscript'
    assert audit['verdict'] == 'adapter-ready-surface'


def test_surface_report_audit_uses_userscript_drill_after_capsule() -> None:
    payload = {
        'tool': 'glasstty-chatgpt-surface-oracle-userscript',
        'version': 'rev0331-test',
        'after_capsule': _base_capsule(),
    }
    line = 'GLASSTTY_USER_SURFACE_DRILL_JSON=' + __import__('json').dumps(payload)

    parsed = extract_json_object(line)
    audit = audit_surface(parsed)

    assert audit['source_kind'] == 'surface-oracle-userscript'
    assert audit['audited_nested_source'] == 'after_capsule'
    assert audit['verdict'] == 'adapter-ready-surface'


def test_surface_report_audit_exposes_live_strict_send_witness() -> None:
    payload = _base_capsule()
    payload['tool'] = 'glasstty-chatgpt-surface-oracle-userscript'
    payload['report_kind'] = 'send-drill-after-write'
    payload['send_state'] = {
        'strict_send_found': True,
        'blocked_send_control_found': True,
        'best_strict_send': {
            'selector': '#composer-submit-button',
            'data_testid': 'send-button',
            'aria_label': 'Send prompt',
            'score': 1.45,
        },
        'best_blocked_control': {
            'selector': '#composer-plus-btn',
            'aria_label': 'Add files and more',
            'score': -0.85,
        },
    }

    audit = audit_surface(payload)

    assert audit['verdict'] == 'adapter-ready-surface'
    assert audit['signals']['strict_send_found'] is True
    assert audit['signals']['strict_send_selector'] == '#composer-submit-button'
    assert audit['signals']['strict_send_testid'] == 'send-button'
    assert audit['signals']['strict_send_aria_label'] == 'Send prompt'
    assert audit['signals']['blocked_send_control_found'] is True
    assert audit['signals']['blocked_send_selector'] == '#composer-plus-btn'


def test_surface_report_audit_accepts_generic_send_but_recommends_live_lock() -> None:
    payload = _base_capsule()
    payload['adapter_recommendation'] = {
        **payload['adapter_recommendation'],
        'best_send_selector': 'button[aria-label="Send"]',
    }
    payload['top_candidates'] = {
        'send': {
            'selector': 'button[aria-label="Send"]',
            'id': None,
            'data_testid': None,
            'aria_label': 'Send',
        },
    }

    audit = audit_surface(payload)

    assert audit['verdict'] == 'adapter-ready-surface'
    assert audit['signals']['send_ok'] is True
    assert audit['signals']['strict_send_live_lock'] is False
    assert (
        'send candidate is acceptable but not the observed composer-submit live lock'
        in audit['recommendations']
    )

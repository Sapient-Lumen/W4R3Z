#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PREFIXES = (
    'GLASSTTY_SURFACE_CAPSULE_JSON=',
    'GLASSTTY_SURFACE_REPORT_JSON=',
    'GLASSTTY_USER_SURFACE_CAPSULE_JSON=',
    'GLASSTTY_USER_SURFACE_REPORT_JSON=',
    'GLASSTTY_USER_SURFACE_DRILL_JSON=',
    'GLASSTTY_USER_SURFACE_PROOF_JSON=',
    'GLASSTTY_PAGEWORLD_REST_JSON=',
)


NON_SEND_CONTROL_TERMS = (
    'add files',
    'add file',
    'add photos',
    'add photo',
    'add files and more',
    'composer-plus',
    'plus-btn',
    'attach',
    'attachment',
    'upload',
    'file',
    'files',
    'voice',
    'dictate',
    'microphone',
    'audio',
    'stop',
    'cancel',
    'search',
    'tools',
    'tool',
    'deep research',
    'model',
    'picker',
    'reasoning',
    'library',
    'canvas',
    'email',
    'recipient',
    'image',
    'create image',
)


def _textish(value: Any) -> str:
    return value if isinstance(value, str) else ''


def _looks_like_explicit_send(text: str) -> bool:
    hay = text.lower()
    return (
        'send-button' in hay
        or 'send message' in hay
        or 'send prompt' in hay
        or hay.strip() == 'send'
        or 'aria-label:send' in hay
    )


def _looks_like_non_send_control(payload: dict[str, Any], adapter: dict[str, Any]) -> bool:
    send_candidate = _get(payload, 'top_candidates.send', {}) or {}
    parts = [
        _textish(adapter.get('best_send_selector')),
        _textish(send_candidate.get('selector')),
        _textish(send_candidate.get('id')),
        _textish(send_candidate.get('data_testid')),
        _textish(send_candidate.get('aria_label')),
        _textish(send_candidate.get('placeholder')),
    ]
    combined = ' '.join(part.lower() for part in parts if part)
    if not combined:
        return False
    if _looks_like_explicit_send(combined):
        return False
    return any(term in combined for term in NON_SEND_CONTROL_TERMS)



def _strict_send_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    send_state_candidate = _get(payload, 'send_state.best_strict_send', {}) or {}
    top_candidate = _get(payload, 'top_candidates.send', {}) or {}
    if isinstance(send_state_candidate, dict) and send_state_candidate:
        return send_state_candidate
    return top_candidate if isinstance(top_candidate, dict) else {}


def _strict_send_live_lock(payload: dict[str, Any], adapter: dict[str, Any]) -> bool:
    candidate = _strict_send_candidate(payload)
    parts = [
        _textish(adapter.get('best_send_selector')),
        _textish(candidate.get('selector')),
        _textish(candidate.get('id')),
        _textish(candidate.get('data_testid')),
        _textish(candidate.get('aria_label')),
    ]
    combined = ' '.join(part.lower() for part in parts if part)
    return (
        ('#composer-submit-button' in combined or 'composer-submit-button' in combined)
        and 'send-button' in combined
        and ('send prompt' in combined or 'send message' in combined
             or ' aria-label:send' in combined)
    )

def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        '+00:00',
        'Z',
    )


def _loads_object(payload: str) -> dict[str, Any]:
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError('surface payload must be a JSON object')
    return parsed


def _loads_object_prefix(payload: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    parsed, _end = decoder.raw_decode(payload.strip())
    if not isinstance(parsed, dict):
        raise ValueError('surface payload must be a JSON object')
    return parsed


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    for line in stripped.splitlines():
        line = line.strip()
        for prefix in PREFIXES:
            if line.startswith(prefix):
                return _loads_object_prefix(line[len(prefix):].strip())
    try:
        return _loads_object(stripped)
    except json.JSONDecodeError:
        pass
    start = stripped.find('{')
    end = stripped.rfind('}')
    if start >= 0 and end > start:
        return _loads_object(stripped[start:end + 1])
    raise ValueError('could not find a JSON object or GlassTTY capsule line')


def _get(payload: dict[str, Any], path: str, default: Any = None) -> Any:
    value: Any = payload
    for part in path.split('.'):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def _num(value: Any, default: float = 0.0) -> float:
    return value if isinstance(value, (int, float)) else default


def _source_kind(payload: dict[str, Any]) -> str:
    if payload.get('capsule_schema_version'):
        return 'surface-capsule'
    if payload.get('tool') == 'glasstty-chatgpt-surface-megathing':
        return 'surface-megathing-report'
    if payload.get('tool') == 'glasstty-chatgpt-surface-oracle-userscript':
        return 'surface-oracle-userscript'
    if payload.get('tool') == 'glasstty-chatgpt-pageworld-restprobe':
        return 'pageworld-restprobe'
    return 'unknown-json-object'


def audit_surface(payload: dict[str, Any]) -> dict[str, Any]:
    original_payload = payload
    nested_source = None
    for key in ('after_capsule', 'final_capsule', 'before_capsule'):
        nested = payload.get(key)
        if isinstance(nested, dict):
            payload = nested
            nested_source = key
            break

    adapter = _get(payload, 'adapter_recommendation', {}) or {}
    counts = _get(payload, 'counts', {}) or {}
    route = _get(payload, 'route_posture_guess', {}) or {}
    page = _get(payload, 'page', {}) or {}
    host = page.get('host') or ''
    prompt_score = _num(adapter.get('best_prompt_score'))
    send_score = _num(adapter.get('best_send_score'))
    assistant_count = int(_num(counts.get('assistant_role_nodes')))
    user_count = int(_num(counts.get('user_role_nodes')))
    issues: list[str] = []
    recommendations: list[str] = []

    chatgpt_host = host == 'chatgpt.com' or host.endswith('.chatgpt.com')
    plain_chat_route = route.get('posture') == 'plain-chat'
    prompt_ok = bool(adapter.get('best_prompt_selector')) and prompt_score >= 0.35
    send_present = bool(adapter.get('best_send_selector'))
    send_state = _get(payload, 'send_state', {}) or {}
    strict_send = send_state.get('best_strict_send') or {}
    blocked_send = send_state.get('best_blocked_control') or {}
    strict_send_found = bool(send_state.get('strict_send_found') or strict_send)
    blocked_send_found = bool(
        send_state.get('blocked_send_control_found') or blocked_send
    )
    strict_selector = _textish(strict_send.get('selector'))
    strict_testid = _textish(strict_send.get('data_testid'))
    strict_aria = _textish(strict_send.get('aria_label'))
    strict_score = _num(strict_send.get('score'), send_score)
    if strict_send_found and not send_present:
        adapter = {
            **adapter,
            'best_send_selector': strict_selector,
            'best_send_score': strict_score,
        }
        send_present = bool(strict_selector)
        send_score = strict_score
    send_false_positive = _looks_like_non_send_control(payload, adapter)
    readiness = _get(payload, 'send_readiness', {}) or send_state
    empty_missing_ok = bool(
        readiness.get('empty_composer_missing_send_is_allowed')
    )
    send_ok = (send_present and send_score >= 0.45 and not send_false_positive)
    if strict_send_found:
        send_ok = send_ok or (
            bool(strict_selector)
            and strict_score >= 0.45
            and not _looks_like_non_send_control(
                {'top_candidates': {'send': strict_send}},
                {'best_send_selector': strict_selector},
            )
        )
    strict_send_live_lock = _strict_send_live_lock(payload, adapter)
    roles_present = bool(adapter.get('has_explicit_author_roles'))
    latest_assistant = bool(adapter.get('latest_assistant_selector'))
    latest_user = bool(adapter.get('latest_user_selector'))

    if not chatgpt_host:
        issues.append('capture is not from chatgpt.com')
    if not plain_chat_route:
        issues.append('route posture is not plain-chat')
    if not prompt_ok:
        issues.append('prompt candidate is missing or below score threshold')
    if send_false_positive:
        issues.append('send candidate looks like a non-submit composer control')
        recommendations.append('treat this capture as empty-composer preflight')
    elif not send_ok:
        issues.append('send button is missing or below score threshold')
        if empty_missing_ok:
            recommendations.append('send may appear only after composer text exists')
        else:
            recommendations.append('re-run after typing harmless text in the composer')
    if send_ok and not strict_send_live_lock:
        recommendations.append('send candidate is acceptable but not the observed composer-submit live lock')
    if not roles_present:
        issues.append('explicit data-message-author-role nodes were not found')
    if roles_present and not latest_assistant:
        issues.append('no latest assistant selector was identified')
    if roles_present and not latest_user:
        recommendations.append('capture after a visible user turn is mounted')

    hard_ok = chatgpt_host and plain_chat_route and prompt_ok and roles_present
    if hard_ok and send_ok and latest_assistant:
        verdict = 'adapter-ready-surface'
    elif hard_ok:
        verdict = 'partial-surface-needs-send-or-turn-witness'
    else:
        verdict = 'not-ready-surface'

    return {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-surface-report-audit',
        'audited_at': utcnow(),
        'source_kind': _source_kind(original_payload),
        'audited_nested_source': nested_source,
        'source_tool': original_payload.get('tool') or original_payload.get('source_tool'),
        'source_version': original_payload.get('version') or original_payload.get('source_version'),
        'verdict': verdict,
        'signals': {
            'chatgpt_host': chatgpt_host,
            'host': host,
            'pathname': page.get('pathname') or route.get('pathname'),
            'route_posture': route.get('posture'),
            'plain_chat_route': plain_chat_route,
            'prompt_selector_present': bool(adapter.get('best_prompt_selector')),
            'prompt_score': prompt_score,
            'prompt_ok': prompt_ok,
            'send_selector_present': send_present,
            'send_score': send_score,
            'send_false_positive': send_false_positive,
            'strict_send_found': strict_send_found,
            'strict_send_selector': strict_selector or None,
            'strict_send_testid': strict_testid or None,
            'strict_send_aria_label': strict_aria or None,
            'strict_send_score': strict_score,
            'blocked_send_control_found': blocked_send_found,
            'blocked_send_selector': _textish(blocked_send.get('selector')) or None,
            'blocked_send_aria_label': _textish(blocked_send.get('aria_label')) or None,
            'empty_composer_missing_send_is_allowed': empty_missing_ok,
            'send_ok': send_ok,
            'strict_send_live_lock': strict_send_live_lock,
            'explicit_author_roles_present': roles_present,
            'assistant_role_nodes': assistant_count,
            'user_role_nodes': user_count,
            'latest_assistant_selector_present': latest_assistant,
            'latest_user_selector_present': latest_user,
        },
        'issues': issues,
        'recommendations': recommendations,
        'warnings': payload.get('warnings', []),
    }


def read_input(path: str | None) -> str:
    if path and path != '-':
        return Path(path).read_text(encoding='utf-8')
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Audit a GlassTTY ChatGPT surface megathing/capsule capture.',
    )
    parser.add_argument('input', nargs='?', default='-')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    payload = extract_json_object(read_input(args.input))
    audit = audit_surface(payload)
    indent = 2 if args.pretty else None
    print(json.dumps(audit, indent=indent, sort_keys=bool(indent)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

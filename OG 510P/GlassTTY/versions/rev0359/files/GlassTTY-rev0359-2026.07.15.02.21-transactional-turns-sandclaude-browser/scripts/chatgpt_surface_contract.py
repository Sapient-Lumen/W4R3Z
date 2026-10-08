#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_surface_report_audit import audit_surface, extract_json_object

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _get(value: JsonDict, path: str, default: Any = None) -> Any:
    current: Any = value
    for part in path.split('.'):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _num(value: Any, default: float = 0.0) -> float:
    return value if isinstance(value, (int, float)) else default


def _int(value: Any, default: int = 0) -> int:
    return int(value) if isinstance(value, (int, float)) else default


def _surface_payload(payload: JsonDict) -> JsonDict:
    for key in ('after_capsule', 'final_capsule', 'before_capsule'):
        nested = payload.get(key)
        if isinstance(nested, dict):
            return nested
    return payload


def _unique_text(values: list[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _strict_send(surface: JsonDict) -> JsonDict:
    send_state = _get(surface, 'send_state.best_strict_send', {})
    if isinstance(send_state, dict) and send_state:
        return send_state
    top = _get(surface, 'top_candidates.send', {})
    return top if isinstance(top, dict) else {}


def _blocked_send(surface: JsonDict) -> JsonDict:
    blocked = _get(surface, 'send_state.best_blocked_control', {})
    if isinstance(blocked, dict) and blocked:
        return blocked
    top = _get(surface, 'top_candidates.blocked_send', {})
    return top if isinstance(top, dict) else {}


def _selector_count(surface: JsonDict, bucket: str, selector: str) -> int | None:
    rows = _get(surface, f'selector_probe.{bucket}', [])
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get('selector') == selector:
            count = row.get('count')
            if isinstance(count, (int, float)):
                return int(count)
    return None


def build_contract(payload: JsonDict, *, source_path: str | None = None) -> JsonDict:
    surface = _surface_payload(payload)
    audit = audit_surface(payload)
    adapter = _get(surface, 'adapter_recommendation', {}) or {}
    counts = _get(surface, 'counts', {}) or {}
    route = _get(surface, 'route_posture_guess', {}) or {}
    page = _get(surface, 'page', {}) or {}
    strict = _strict_send(surface)
    blocked = _blocked_send(surface)
    prompt_selector = _text(adapter.get('best_prompt_selector')) or '#prompt-textarea'
    strict_selector = _text(strict.get('selector')) or _text(adapter.get('best_send_selector'))
    blocked_selector = _text(blocked.get('selector')) or _text(adapter.get('blocked_send_selector'))
    contract: JsonDict = {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-surface-contract',
        'contract_version': 'rev0335',
        'created_at': utcnow(),
        'source': {
            'path': source_path,
            'tool': payload.get('tool'),
            'version': payload.get('version'),
            'report_kind': payload.get('report_kind') or surface.get('source_report_kind'),
            'audit_verdict': audit.get('verdict'),
        },
        'scope': {
            'surface_key': 'chatgpt',
            'host': 'chatgpt.com',
            'route_posture': 'plain-chat',
            'provider_policy': 'ChatGPT only; other provider drift is out of scope',
        },
        'required': {
            'page_host': 'chatgpt.com',
            'route_posture': 'plain-chat',
            'prompt_selector': prompt_selector,
            'prompt_min_score': max(0.35, round(_num(adapter.get('best_prompt_score')), 2) - 0.25),
            'explicit_author_roles': True,
            'assistant_role_min': 1,
            'user_role_min': 1,
            'strict_send': {
                'selector': strict_selector,
                'id': _text(strict.get('id')),
                'data_testid': _text(strict.get('data_testid')),
                'aria_label': _text(strict.get('aria_label')),
                'min_score': max(0.45, round(_num(strict.get('score'), _num(adapter.get('best_send_score'))), 2) - 0.35),
            },
        },
        'known_non_send_controls': [
            {
                'selector': blocked_selector,
                'id': _text(blocked.get('id')),
                'data_testid': _text(blocked.get('data_testid')),
                'aria_label': _text(blocked.get('aria_label')),
                'reason': 'composer tool/attachment control, not prompt submit',
            },
            {'aria_label_contains': 'Start dictation', 'reason': 'voice input control'},
            {'text_contains': 'Extra High', 'reason': 'model/reasoning/composer option pill'},
        ],
        'observed_baseline': {
            'pathname_shape': _text(page.get('pathname')),
            'prompt_selector_count': _selector_count(surface, 'prompt', prompt_selector),
            'strict_send_selector_count': _selector_count(surface, 'send', 'button[data-testid="send-button"]'),
            'buttons': _int(counts.get('buttons')),
            'forms': _int(counts.get('forms')),
            'iframes': _int(counts.get('iframes')),
            'role_textbox': _int(counts.get('role_textbox')),
            'contenteditable': _int(counts.get('contenteditable')),
            'message_author_role_nodes': _int(counts.get('message_author_role_nodes')),
            'assistant_role_nodes': _int(counts.get('assistant_role_nodes')),
            'user_role_nodes': _int(counts.get('user_role_nodes')),
            'conversation_turn_like_nodes': _int(counts.get('conversation_turn_like_nodes')),
        },
        'drift_policy': {
            'blockers': [
                'not_chatgpt_host',
                'not_plain_chat_route',
                'missing_prompt_selector',
                'missing_strict_send_selector',
                'strict_send_became_known_non_send_control',
                'missing_explicit_author_roles',
            ],
            'warnings': [
                'count_shift_large',
                'latest_user_missing',
                'latest_assistant_missing',
                'strict_send_label_changed',
                'known_non_send_control_missing',
            ],
        },
        'audit_snapshot': audit,
    }
    return contract


def _matches_host(host: Any, expected: str) -> bool:
    return isinstance(host, str) and (host == expected or host.endswith('.' + expected))


def _candidate_text(candidate: JsonDict) -> str:
    return ' '.join(_unique_text([
        candidate.get('selector'), candidate.get('id'), candidate.get('data_testid'),
        candidate.get('aria_label'), candidate.get('title'), candidate.get('placeholder'),
    ])).lower()


def _known_non_send_hit(candidate: JsonDict, contract: JsonDict) -> str | None:
    hay = _candidate_text(candidate)
    for control in contract.get('known_non_send_controls', []):
        if not isinstance(control, dict):
            continue
        selector = _text(control.get('selector'))
        data_testid = _text(control.get('data_testid'))
        aria = _text(control.get('aria_label'))
        aria_contains = _text(control.get('aria_label_contains'))
        text_contains = _text(control.get('text_contains'))
        if selector and selector.lower() in hay:
            return selector
        if data_testid and data_testid.lower() in hay:
            return data_testid
        if aria and aria.lower() in hay:
            return aria
        if aria_contains and aria_contains.lower() in hay:
            return aria_contains
        if text_contains and text_contains.lower() in hay:
            return text_contains
    return None


def _count_delta(name: str, observed: int, baseline: int) -> JsonDict | None:
    if baseline <= 0:
        return None
    delta = observed - baseline
    ratio = observed / baseline if baseline else 0
    if ratio < 0.5 or ratio > 1.8:
        return {'signal': 'count_shift_large', 'name': name, 'baseline': baseline, 'observed': observed, 'ratio': round(ratio, 3), 'delta': delta}
    return None




def _recommendation_for_signal(signal: str) -> str:
    table = {
        'not_chatgpt_host': 'Open https://chatgpt.com/ before collecting a proof or surface report.',
        'not_plain_chat_route': 'Move to a plain ChatGPT chat route, not Projects, GPT builder, Canvas, agent/task, login, or marketing pages.',
        'missing_prompt_selector': 'Run the Tampermonkey full report and inspect prompt candidates before attempting prompt.write.',
        'prompt_score_below_contract': 'Re-run the surface oracle; if #prompt-textarea still exists, update scorer thresholds with evidence.',
        'missing_strict_send_selector': 'Run the safe send-state drill; do not submit until the strict Send control is rediscovered.',
        'strict_send_became_known_non_send_control': 'Stop: the submit detector has locked onto a known non-send control. Patch adapter blocklists/tests first.',
        'strict_send_testid_changed': 'Treat this as a breaking send-surface change; capture a new drill report and update the contract if valid.',
        'strict_send_score_below_contract': 'Inspect send candidate scoring; require explicit send intent and composer-local scope before proof submission.',
        'missing_explicit_author_roles': 'Do not evaluate transcript.latest yet; capture a full report and repair assistant/user turn witness selection.',
        'assistant_roles_below_contract': 'Open a conversation with at least one assistant turn before running proof capture.',
        'user_roles_below_contract': 'Open a conversation with at least one user turn before running proof capture.',
        'latest_assistant_missing': 'Scroll or wait for the latest assistant turn, then recapture; otherwise update latest-turn selection.',
        'latest_user_missing': 'Scroll or wait for the latest user turn, then recapture; otherwise update user-turn witness selection.',
        'strict_send_label_changed': 'Review the send label change; update the contract only after the drill still proves explicit submit intent.',
        'known_non_send_control_missing': 'This can be benign, but rerun the safe drill to confirm composer tools did not move into the send slot.',
        'count_shift_large': 'Capture a full report and compare selector probes; this may be ordinary page growth or a structural UI change.',
    }
    return table.get(signal, 'Capture a fresh surface report and inspect the changed field before proof submission.')


def _recommendations(blockers: list[JsonDict], warnings: list[JsonDict]) -> list[JsonDict]:
    rows: list[JsonDict] = []
    seen: set[str] = set()
    for severity, items in (('blocker', blockers), ('warning', warnings)):
        for item in items:
            signal = _text(item.get('signal')) or 'unknown'
            key = f'{severity}:{signal}'
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                'severity': severity,
                'signal': signal,
                'next_step': _recommendation_for_signal(signal),
            })
    if not rows:
        rows.append({
            'severity': 'ok',
            'signal': 'surface-contract-ok',
            'next_step': 'Surface contract is satisfied. It is safe to proceed to offline rehearsal or live proof capture when available.',
        })
    return rows

def check_contract(payload: JsonDict, contract: JsonDict) -> JsonDict:
    surface = _surface_payload(payload)
    audit = audit_surface(payload)
    adapter = _get(surface, 'adapter_recommendation', {}) or {}
    counts = _get(surface, 'counts', {}) or {}
    route = _get(surface, 'route_posture_guess', {}) or {}
    page = _get(surface, 'page', {}) or {}
    required = contract.get('required', {}) if isinstance(contract.get('required'), dict) else {}
    strict_req = required.get('strict_send', {}) if isinstance(required.get('strict_send'), dict) else {}
    strict = _strict_send(surface)

    blockers: list[JsonDict] = []
    warnings: list[JsonDict] = []

    host = page.get('host')
    expected_host = _text(required.get('page_host')) or 'chatgpt.com'
    if not _matches_host(host, expected_host):
        blockers.append({'signal': 'not_chatgpt_host', 'expected': expected_host, 'observed': host})

    expected_route = _text(required.get('route_posture')) or 'plain-chat'
    if route.get('posture') != expected_route:
        blockers.append({'signal': 'not_plain_chat_route', 'expected': expected_route, 'observed': route.get('posture')})

    expected_prompt = _text(required.get('prompt_selector'))
    observed_prompt = _text(adapter.get('best_prompt_selector'))
    prompt_score = _num(adapter.get('best_prompt_score'))
    prompt_min = _num(required.get('prompt_min_score'), 0.35)
    if expected_prompt and observed_prompt != expected_prompt:
        blockers.append({'signal': 'missing_prompt_selector', 'expected': expected_prompt, 'observed': observed_prompt})
    elif prompt_score < prompt_min:
        blockers.append({'signal': 'prompt_score_below_contract', 'expected_min': prompt_min, 'observed': prompt_score})

    expected_send = _text(strict_req.get('selector'))
    observed_send = _text(strict.get('selector')) or _text(adapter.get('best_send_selector'))
    if expected_send and observed_send != expected_send:
        blockers.append({'signal': 'missing_strict_send_selector', 'expected': expected_send, 'observed': observed_send})
    send_hit = _known_non_send_hit(strict if strict else {'selector': observed_send}, contract)
    if send_hit:
        blockers.append({'signal': 'strict_send_became_known_non_send_control', 'matched': send_hit, 'observed': observed_send})
    expected_testid = _text(strict_req.get('data_testid'))
    observed_testid = _text(strict.get('data_testid'))
    if expected_testid and observed_testid and observed_testid != expected_testid:
        blockers.append({'signal': 'strict_send_testid_changed', 'expected': expected_testid, 'observed': observed_testid})
    expected_aria = _text(strict_req.get('aria_label'))
    observed_aria = _text(strict.get('aria_label'))
    if expected_aria and observed_aria and observed_aria != expected_aria:
        warnings.append({'signal': 'strict_send_label_changed', 'expected': expected_aria, 'observed': observed_aria})
    min_send_score = _num(strict_req.get('min_score'), 0.45)
    send_score = _num(strict.get('score'), _num(adapter.get('best_send_score')))
    if send_score < min_send_score:
        blockers.append({'signal': 'strict_send_score_below_contract', 'expected_min': min_send_score, 'observed': send_score})

    if required.get('explicit_author_roles', True) and not adapter.get('has_explicit_author_roles'):
        blockers.append({'signal': 'missing_explicit_author_roles'})
    if _int(counts.get('assistant_role_nodes')) < _int(required.get('assistant_role_min'), 1):
        blockers.append({'signal': 'assistant_roles_below_contract', 'expected_min': required.get('assistant_role_min'), 'observed': counts.get('assistant_role_nodes')})
    if _int(counts.get('user_role_nodes')) < _int(required.get('user_role_min'), 1):
        blockers.append({'signal': 'user_roles_below_contract', 'expected_min': required.get('user_role_min'), 'observed': counts.get('user_role_nodes')})
    if not adapter.get('latest_assistant_selector'):
        warnings.append({'signal': 'latest_assistant_missing'})
    if not adapter.get('latest_user_selector'):
        warnings.append({'signal': 'latest_user_missing'})

    baseline = contract.get('observed_baseline', {}) if isinstance(contract.get('observed_baseline'), dict) else {}
    for name in ('buttons', 'forms', 'iframes', 'role_textbox', 'contenteditable', 'message_author_role_nodes'):
        item = _count_delta(name, _int(counts.get(name)), _int(baseline.get(name)))
        if item:
            warnings.append(item)

    known_blocked = _text(_get(surface, 'send_state.best_blocked_control.selector')) or _text(adapter.get('blocked_send_selector'))
    expected_blocked = None
    for control in contract.get('known_non_send_controls', []):
        if isinstance(control, dict) and control.get('selector'):
            expected_blocked = _text(control.get('selector'))
            break
    if expected_blocked and known_blocked != expected_blocked:
        warnings.append({'signal': 'known_non_send_control_missing', 'expected': expected_blocked, 'observed': known_blocked})

    if blockers:
        verdict = 'surface-drift-blocker'
    elif warnings:
        verdict = 'surface-drift-warning'
    else:
        verdict = 'surface-contract-ok'
    recommendations = _recommendations(blockers, warnings)

    return {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-surface-contract-check',
        'checked_at': utcnow(),
        'verdict': verdict,
        'contract_version': contract.get('contract_version'),
        'source_audit_verdict': audit.get('verdict'),
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
        'recommended_next_action': recommendations[0]['next_step'] if recommendations else None,
        'summary': {
            'host': host,
            'pathname': page.get('pathname') or route.get('pathname'),
            'route_posture': route.get('posture'),
            'prompt_selector': observed_prompt,
            'prompt_score': prompt_score,
            'strict_send_selector': observed_send,
            'strict_send_testid': observed_testid,
            'strict_send_aria_label': observed_aria,
            'strict_send_score': send_score,
            'assistant_role_nodes': counts.get('assistant_role_nodes'),
            'user_role_nodes': counts.get('user_role_nodes'),
        },
        'audit': audit,
    }


def read_payload(path: str) -> JsonDict:
    text = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
    return extract_json_object(text)


def read_json(path: str) -> JsonDict:
    text = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError('expected JSON object')
    return parsed


def emit(data: JsonDict, *, pretty: bool) -> None:
    print(json.dumps(data, indent=2 if pretty else None, sort_keys=pretty))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build and check GlassTTY ChatGPT live surface contracts.')
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build', help='Build a surface contract from a report/capsule/drill JSON')
    build.add_argument('report')
    build.add_argument('--out')
    build.add_argument('--pretty', action='store_true')
    check = sub.add_parser('check', help='Check a report/capsule/drill JSON against a surface contract')
    check.add_argument('report')
    check.add_argument('--contract', required=True)
    check.add_argument('--pretty', action='store_true')
    args = parser.parse_args(argv)
    if args.command == 'build':
        payload = read_payload(args.report)
        contract = build_contract(payload, source_path=None if args.report == '-' else args.report)
        if args.out:
            Path(args.out).write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        emit(contract, pretty=args.pretty)
        return 0
    if args.command == 'check':
        payload = read_payload(args.report)
        contract = read_json(args.contract)
        result = check_contract(payload, contract)
        emit(result, pretty=args.pretty)
        return 0 if result['verdict'] == 'surface-contract-ok' else 2
    raise AssertionError(args.command)


if __name__ == '__main__':
    raise SystemExit(main())

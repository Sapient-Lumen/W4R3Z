#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / 'docs/40-verification/corpora/component-lifecycle-activation-corpus-v0.jsonl'

CID_RE = re.compile(r'^[a-z][a-z0-9._-]{0,63}$')
KEY_RE = re.compile(r'^[a-z][a-z0-9._/-]{0,63}$')
ENTRY_RE = re.compile(r'^[a-z][a-z0-9._/-]{0,95}$')
NONCE_RE = re.compile(r'^inc_[a-z0-9]{16}$')
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
TAG_RE = re.compile(r'^[a-z0-9][a-z0-9._-]{0,63}$')

COMP_REQUIRED = {'schema', 'cid', 'image_digest', 'entry', 'critical', 'imports'}
COMP_OPTIONAL = {'restart', 'readiness', 'activation', 'notes_tag'}
COMP_ALLOWED = COMP_REQUIRED | COMP_OPTIONAL
RESTART_ALLOWED = {'policy', 'window_ms', 'max_restarts', 'backoff_ms'}
READINESS_ALLOWED = {'required', 'startup_timeout_ms', 'ready_timeout_ms'}
ACTIVATION_ALLOWED = {'stable_exports', 'escrow'}
ESCROW_ALLOWED = {'enabled', 'key_allowlist', 'max_items'}

ACTSET_REQUIRED = {'schema', 'cid', 'instance_nonce', 'stable', 'escrowed'}
ACTSET_ALLOWED = ACTSET_REQUIRED
ENTRY_ALLOWED = {'key', 'kind', 'rights', 'origin'}
ACTSET_KINDS = {
    'socket', 'env', 'secret', 'trust_bundle', 'config', 'runtime_dir',
    'state_dir', 'lease', 'descriptor', 'continuity_item'
}
RIGHTS = {'read', 'write', 'connect', 'listen', 'renew', 'observe', 'execute'}
FORBIDDEN_HANDLE_KEYS = {'handle', 'value', 'token', 'secret', 'raw', 'path', 'fd', 'descriptor_number'}


def fail(msg: str) -> None:
    raise ValueError(msg)


def no_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            fail(f'duplicate JSON key: {key}')
        out[key] = value
    return out


def parse_json_text(text: str) -> Any:
    return json.loads(text, object_pairs_hook=no_duplicate_object_pairs)


def ensure_no_floats(value: Any, path: str = '$') -> None:
    if isinstance(value, float):
        fail(f'{path}: floats are not allowed in canonical Steward JSON')
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                fail(f'{path}: non-string object key')
            ensure_no_floats(v, f'{path}.{k}')
    elif isinstance(value, list):
        for i, v in enumerate(value):
            ensure_no_floats(v, f'{path}[{i}]')


def canonical_bytes(value: Any) -> bytes:
    ensure_no_floats(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest(value: Any) -> str:
    return 'sha256:' + hashlib.sha256(canonical_bytes(value)).hexdigest()


def require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f'{path}: expected object')
    return value


def require_bool(value: Any, path: str) -> None:
    if type(value) is not bool:
        fail(f'{path}: expected bool')


def require_int(value: Any, path: str, *, minimum: int = 0, maximum: int = 2_147_483_647) -> None:
    if type(value) is not int:
        fail(f'{path}: expected integer')
    if value < minimum or value > maximum:
        fail(f'{path}: integer out of bounds')


def require_pattern(value: Any, regex: re.Pattern[str], path: str) -> None:
    if not isinstance(value, str) or not regex.match(value):
        fail(f'{path}: invalid string')


def require_closed_keys(obj: dict[str, Any], allowed: set[str], required: set[str], path: str) -> None:
    missing = sorted(required - set(obj))
    if missing:
        fail(f'{path}: missing keys {missing}')
    extra = sorted(set(obj) - allowed)
    if extra:
        fail(f'{path}: unknown field(s) {extra}')


def require_string_list(value: Any, path: str, *, regex: re.Pattern[str] = KEY_RE, maximum: int = 16) -> list[str]:
    if not isinstance(value, list):
        fail(f'{path}: expected list')
    if len(value) > maximum:
        fail(f'{path}: too many entries')
    seen: set[str] = set()
    out: list[str] = []
    for idx, item in enumerate(value):
        require_pattern(item, regex, f'{path}[{idx}]')
        if item in seen:
            fail(f'{path}: duplicate entry {item}')
        seen.add(item)
        out.append(item)
    return out


def validate_ch_comp(obj: Any) -> dict[str, Any]:
    obj = require_object(obj, '$')
    require_closed_keys(obj, COMP_ALLOWED, COMP_REQUIRED, '$')
    if obj['schema'] != 'CH-COMP v0':
        fail('$.schema: expected CH-COMP v0')
    require_pattern(obj['cid'], CID_RE, '$.cid')
    require_pattern(obj['image_digest'], DIGEST_RE, '$.image_digest')
    require_pattern(obj['entry'], ENTRY_RE, '$.entry')
    if any(token in obj['entry'] for token in [' ', ';', '|', '&', '$', '`', '\n', '\t']):
        fail('$.entry: shell command text is not a selector')
    require_bool(obj['critical'], '$.critical')
    require_string_list(obj['imports'], '$.imports', maximum=16)
    if 'notes_tag' in obj:
        require_pattern(obj['notes_tag'], TAG_RE, '$.notes_tag')
    if 'restart' in obj:
        r = require_object(obj['restart'], '$.restart')
        require_closed_keys(r, RESTART_ALLOWED, RESTART_ALLOWED, '$.restart')
        if r['policy'] not in {'never', 'on_failure', 'always'}:
            fail('$.restart.policy: invalid policy')
        require_int(r['window_ms'], '$.restart.window_ms', minimum=1, maximum=86_400_000)
        require_int(r['max_restarts'], '$.restart.max_restarts', minimum=0, maximum=1000)
        require_int(r['backoff_ms'], '$.restart.backoff_ms', minimum=0, maximum=86_400_000)
    if 'readiness' in obj:
        rd = require_object(obj['readiness'], '$.readiness')
        require_closed_keys(rd, READINESS_ALLOWED, READINESS_ALLOWED, '$.readiness')
        require_bool(rd['required'], '$.readiness.required')
        require_int(rd['startup_timeout_ms'], '$.readiness.startup_timeout_ms', minimum=1, maximum=86_400_000)
        require_int(rd['ready_timeout_ms'], '$.readiness.ready_timeout_ms', minimum=1, maximum=86_400_000)
    if 'activation' in obj:
        act = require_object(obj['activation'], '$.activation')
        require_closed_keys(act, ACTIVATION_ALLOWED, set(), '$.activation')
        stable_exports = require_string_list(act.get('stable_exports', []), '$.activation.stable_exports', maximum=32)
        if 'escrow' in act:
            esc = require_object(act['escrow'], '$.activation.escrow')
            require_closed_keys(esc, ESCROW_ALLOWED, ESCROW_ALLOWED, '$.activation.escrow')
            require_bool(esc['enabled'], '$.activation.escrow.enabled')
            require_string_list(esc['key_allowlist'], '$.activation.escrow.key_allowlist', maximum=32)
            require_int(esc['max_items'], '$.activation.escrow.max_items', minimum=0, maximum=1024)
        if len(stable_exports) != len(set(stable_exports)):
            fail('$.activation.stable_exports: duplicate key')
    return obj


def validate_act_entry(entry: Any, path: str, expected_origin: str) -> dict[str, Any]:
    e = require_object(entry, path)
    forbidden = sorted(set(e) & FORBIDDEN_HANDLE_KEYS)
    if forbidden:
        fail(f'{path}: bearer/raw material field(s) forbidden {forbidden}')
    require_closed_keys(e, ENTRY_ALLOWED, ENTRY_ALLOWED, path)
    require_pattern(e['key'], KEY_RE, f'{path}.key')
    if e['kind'] not in ACTSET_KINDS:
        fail(f'{path}.kind: invalid kind')
    if e['origin'] != expected_origin:
        fail(f'{path}.origin: expected {expected_origin}')
    rights = require_string_list(e['rights'], f'{path}.rights', regex=KEY_RE, maximum=8)
    bad_rights = [x for x in rights if x not in RIGHTS]
    if bad_rights:
        fail(f'{path}.rights: invalid rights {bad_rights}')
    return e


def validate_ch_actset(obj: Any) -> dict[str, Any]:
    obj = require_object(obj, '$')
    require_closed_keys(obj, ACTSET_ALLOWED, ACTSET_REQUIRED, '$')
    if obj['schema'] != 'CH-ACTSET v0':
        fail('$.schema: expected CH-ACTSET v0')
    require_pattern(obj['cid'], CID_RE, '$.cid')
    require_pattern(obj['instance_nonce'], NONCE_RE, '$.instance_nonce')
    if not isinstance(obj['stable'], list):
        fail('$.stable: expected list')
    if not isinstance(obj['escrowed'], list):
        fail('$.escrowed: expected list')
    if len(obj['stable']) > 64 or len(obj['escrowed']) > 64:
        fail('activation set list too large')
    seen: set[tuple[str, str]] = set()
    for i, entry in enumerate(obj['stable']):
        e = validate_act_entry(entry, f'$.stable[{i}]', 'stable_export')
        pair = (e['origin'], e['key'])
        if pair in seen:
            fail(f'$.stable[{i}]: duplicate origin/key')
        seen.add(pair)
    for i, entry in enumerate(obj['escrowed']):
        e = validate_act_entry(entry, f'$.escrowed[{i}]', 'escrow')
        pair = (e['origin'], e['key'])
        if pair in seen:
            fail(f'$.escrowed[{i}]: duplicate origin/key')
        seen.add(pair)
    return obj


def validate_actset_against_manifest(actset: dict[str, Any], comp: dict[str, Any]) -> None:
    if actset['cid'] != comp['cid']:
        fail('actset cid does not match manifest cid')
    activation = comp.get('activation', {})
    stable_allowed = set(activation.get('stable_exports', []))
    escrow_cfg = activation.get('escrow', {'enabled': False, 'key_allowlist': [], 'max_items': 0})
    escrow_allowed = set(escrow_cfg.get('key_allowlist', [])) if escrow_cfg.get('enabled') else set()
    stable_keys = {entry['key'] for entry in actset['stable']}
    escrow_keys = {entry['key'] for entry in actset['escrowed']}
    if not stable_keys.issubset(stable_allowed):
        fail(f'actset widens stable exports: {sorted(stable_keys - stable_allowed)}')
    if not escrow_keys.issubset(escrow_allowed):
        fail(f'actset widens escrow keys: {sorted(escrow_keys - escrow_allowed)}')
    if len(actset['escrowed']) > int(escrow_cfg.get('max_items', 0)):
        fail('actset exceeds escrow max_items')


def base_component() -> dict[str, Any]:
    return {
        'schema': 'CH-COMP v0',
        'cid': 'demo.web',
        'image_digest': 'sha256:' + 'a' * 64,
        'entry': 'svc/web',
        'critical': True,
        'restart': {'policy': 'on_failure', 'window_ms': 60000, 'max_restarts': 3, 'backoff_ms': 250},
        'readiness': {'required': True, 'startup_timeout_ms': 30000, 'ready_timeout_ms': 5000},
        'activation': {
            'stable_exports': ['listen/http', 'config/app', 'trust/public'],
            'escrow': {'enabled': True, 'key_allowlist': ['cursor/inbox'], 'max_items': 2},
        },
        'imports': ['net/inbound', 'clock/monotonic'],
        'notes_tag': 'proofslice',
    }


def base_actset(nonce: str = 'inc_0000000000000001') -> dict[str, Any]:
    return {
        'schema': 'CH-ACTSET v0',
        'cid': 'demo.web',
        'instance_nonce': nonce,
        'stable': [
            {'key': 'listen/http', 'kind': 'socket', 'rights': ['listen'], 'origin': 'stable_export'},
            {'key': 'config/app', 'kind': 'config', 'rights': ['read'], 'origin': 'stable_export'},
            {'key': 'trust/public', 'kind': 'trust_bundle', 'rights': ['read'], 'origin': 'stable_export'},
        ],
        'escrowed': [
            {'key': 'cursor/inbox', 'kind': 'continuity_item', 'rights': ['read'], 'origin': 'escrow'},
        ],
    }


def widened_actset() -> dict[str, Any]:
    obj = base_actset('inc_0000000000000002')
    obj['stable'] = obj['stable'] + [
        {'key': 'admin/debug', 'kind': 'socket', 'rights': ['listen'], 'origin': 'stable_export'}
    ]
    return obj


def intent(path: str = '/v1/payments', body: str = 'amount=10') -> dict[str, Any]:
    return {'method': 'POST', 'path': path, 'body_digest': digest({'body': body})}


def schema_case(case_id: str, object_kind: str, obj: Any | None, expect: str, why: str, json_text: str | None = None) -> dict[str, Any]:
    case: dict[str, Any] = {
        'case_id': case_id,
        'kind': 'schema',
        'object_kind': object_kind,
        'expect': expect,
        'why': why,
    }
    if json_text is not None:
        case['json_text'] = json_text
    else:
        case['json'] = obj
        if expect == 'accept':
            case['expected_digest'] = digest(obj)
    return case


def lifecycle_case(case_id: str, events: list[dict[str, Any]], expect: str, why: str) -> dict[str, Any]:
    return {
        'case_id': case_id,
        'kind': 'lifecycle',
        'expect': expect,
        'why': why,
        'events': events,
    }


def build_cases() -> list[dict[str, Any]]:
    comp = base_component()
    act = base_actset()
    act2 = base_actset('inc_0000000000000002')
    wide = widened_actset()
    comp_digest = digest(comp)
    act_digest = digest(act)
    act2_digest = digest(act2)
    effect_ref = 'eff_0001'
    base_events = [
        {'event': 'manifest', 'component': comp},
        {'event': 'actset', 'actset': act},
        {'event': 'spawn', 'cid': 'demo.web', 'cycle': 'cycle-1', 'manifest_digest': comp_digest},
        {'event': 'activation_receipt', 'cid': 'demo.web', 'cycle': 'cycle-1', 'actset_digest': act_digest},
    ]

    cases: list[dict[str, Any]] = [
        schema_case('chcomp.accept.minimal', 'CH-COMP', comp, 'accept', 'closed CH-COMP with bounded selectors and activation allowlist'),
        schema_case('chcomp.reject.unknown-host-manager-field', 'CH-COMP', {**comp, 'systemd_unit': 'demo.service'}, 'reject', 'host-manager fields must not become portable manifest truth'),
        schema_case('chcomp.reject.shell-entry-text', 'CH-COMP', {**comp, 'entry': '/bin/sh -c demo'}, 'reject', 'entry is a reviewed selector, not shell command text'),
        schema_case('chcomp.reject.duplicate-imports', 'CH-COMP', {**comp, 'imports': ['net/inbound', 'net/inbound']}, 'reject', 'duplicate imports are not canonical'),
        schema_case('chcomp.reject.bad-digest', 'CH-COMP', {**comp, 'image_digest': 'latest'}, 'reject', 'image identity is exact digest, not tag folklore'),
        schema_case('chactset.accept.base', 'CH-ACTSET', act, 'accept', 'activation set is descriptive, named, bounded, and digestable'),
        schema_case('chactset.reject.bearer-token', 'CH-ACTSET', {**act, 'stable': act['stable'] + [{'key': 'secret/api', 'kind': 'secret', 'rights': ['read'], 'origin': 'stable_export', 'token': 'do-not-log'}]}, 'reject', 'activation sets describe delivery and never export raw bearer material'),
        schema_case('chactset.reject.duplicate-origin-key', 'CH-ACTSET', {**act, 'stable': act['stable'] + [act['stable'][0]]}, 'reject', 'duplicate origin/key pairs are non-canonical'),
        schema_case('chactset.reject.duplicate-json-key', 'CH-ACTSET', None, 'reject', 'duplicate JSON keys reject before semantic validation', json_text='{"schema":"CH-ACTSET v0","schema":"CH-ACTSET v0","cid":"demo.web","instance_nonce":"inc_0000000000000001","stable":[],"escrowed":[]}'),
        schema_case('chactset.reject.raw-fd', 'CH-ACTSET', {**act, 'stable': act['stable'] + [{'key': 'listen/admin', 'kind': 'descriptor', 'rights': ['listen'], 'origin': 'stable_export', 'fd': 3}]}, 'reject', 'descriptor numbers are host facts under the membrane, not export material'),

        lifecycle_case('lifecycle.accept.activation-to-serving', base_events + [
            {'event': 'material_freshness', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'fresh'},
            {'event': 'readiness', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'ready'},
            {'event': 'serve_state', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'serving'},
            {'event': 'traffic_binding', 'cid': 'demo.web', 'surface': 'route/public', 'state': 'active', 'implies_ready': False},
        ], 'accept', 'serving is reachable only through separate activation, freshness, readiness, and serve witnesses'),
        lifecycle_case('lifecycle.reject.spawn-implies-ready', [
            {'event': 'manifest', 'component': comp},
            {'event': 'spawn', 'cid': 'demo.web', 'cycle': 'cycle-1', 'manifest_digest': comp_digest},
            {'event': 'readiness', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'ready'},
        ], 'reject', 'spawn cannot be promoted into ready before activation receipt'),
        lifecycle_case('lifecycle.reject.ready-before-activation', [
            {'event': 'manifest', 'component': comp},
            {'event': 'actset', 'actset': act},
            {'event': 'spawn', 'cid': 'demo.web', 'cycle': 'cycle-1', 'manifest_digest': comp_digest},
            {'event': 'readiness', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'ready'},
        ], 'reject', 'readiness must not outrun activation material delivery'),
        lifecycle_case('lifecycle.accept.restart-replays-same-envelope', base_events + [
            {'event': 'runtime_end', 'cid': 'demo.web', 'cycle': 'cycle-1', 'cause': 'crash'},
            {'event': 'actset', 'actset': act2},
            {'event': 'spawn', 'cid': 'demo.web', 'cycle': 'cycle-2', 'manifest_digest': comp_digest},
            {'event': 'activation_receipt', 'cid': 'demo.web', 'cycle': 'cycle-2', 'actset_digest': act2_digest},
        ], 'accept', 'restart may replay the same reviewed activation envelope under a fresh nonce'),
        lifecycle_case('lifecycle.reject.restart-widens-activation', base_events + [
            {'event': 'runtime_end', 'cid': 'demo.web', 'cycle': 'cycle-1', 'cause': 'crash'},
            {'event': 'actset', 'actset': wide},
        ], 'reject', 'restart cannot smuggle a broader activation set'),
        lifecycle_case('lifecycle.reject.stale-runtime-cycle-action', base_events + [
            {'event': 'runtime_end', 'cid': 'demo.web', 'cycle': 'cycle-1', 'cause': 'crash'},
            {'event': 'actset', 'actset': act2},
            {'event': 'spawn', 'cid': 'demo.web', 'cycle': 'cycle-2', 'manifest_digest': comp_digest},
            {'event': 'control_operation', 'cid': 'demo.web', 'verb': 'stop', 'target_cycle': 'cycle-1'},
        ], 'reject', 'wrong-cycle control operations are stale and must fence'),
        lifecycle_case('lifecycle.reject.stop-request-claims-stopped', base_events + [
            {'event': 'stop_request', 'cid': 'demo.web', 'cycle': 'cycle-1', 'claims_stopped': True},
        ], 'reject', 'stop requested is not stopped'),
        lifecycle_case('lifecycle.accept.stop-boundaries-distinct', base_events + [
            {'event': 'stop_request', 'cid': 'demo.web', 'cycle': 'cycle-1', 'claims_stopped': False},
            {'event': 'stop_progress', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'grace'},
            {'event': 'stop_progress', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'escalation'},
            {'event': 'stop_progress', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'terminated'},
        ], 'accept', 'request, grace, escalation, and terminal cause stay separate'),
        lifecycle_case('lifecycle.reject.quiesce-force-kill', base_events + [
            {'event': 'quiesce', 'cid': 'demo.web', 'cycle': 'cycle-1', 'no_new_work': True, 'claims_force_kill': True},
        ], 'reject', 'quiesce gates new work; it is not force kill'),
        lifecycle_case('lifecycle.accept.quiesce-no-new-work', base_events + [
            {'event': 'quiesce', 'cid': 'demo.web', 'cycle': 'cycle-1', 'no_new_work': True, 'claims_force_kill': False},
        ], 'accept', 'bounded no-new-work fences are allowed without death claims'),
        lifecycle_case('lifecycle.reject.adapter-promotes-host-ready', base_events + [
            {'event': 'adapter_observation', 'cid': 'demo.web', 'source': 'kubernetes', 'fact': 'pod-running', 'promote_to_native': True},
        ], 'reject', 'host-manager observations are weak evidence, not native readiness'),
        lifecycle_case('lifecycle.accept.adapter-observation-weak', base_events + [
            {'event': 'adapter_observation', 'cid': 'demo.web', 'source': 'systemd', 'fact': 'active', 'promote_to_native': False},
        ], 'accept', 'adapter facts may be recorded as weak basis without strengthening truth'),
        lifecycle_case('lifecycle.reject.material-presence-as-fresh', base_events + [
            {'event': 'material_freshness', 'cid': 'demo.web', 'cycle': 'cycle-1', 'state': 'fresh', 'claims_fresh_from_presence': True},
        ], 'reject', 'path/env presence is not freshness'),
        lifecycle_case('lifecycle.reject.traffic-binding-implies-ready', base_events + [
            {'event': 'traffic_binding', 'cid': 'demo.web', 'surface': 'route/public', 'state': 'active', 'implies_ready': True},
        ], 'reject', 'route binding is not readiness truth'),
        lifecycle_case('lifecycle.accept.retry-same-intent-delayed', base_events + [
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-1', 'attempt': 1, 'idempotency_key': 'idem-1', 'canonical_intent': intent(), 'state': 'fresh-attempt'},
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-1', 'attempt': 2, 'idempotency_key': 'idem-1', 'canonical_intent': intent(), 'state': 'pushback-delayed', 'retry_after_ms': 5000, 'reservation_claimed': False},
        ], 'accept', 'same canonical intent may be delayed by advisory retry-after without reserving capacity'),
        lifecycle_case('lifecycle.reject.retry-same-key-mismatch', base_events + [
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-2', 'attempt': 1, 'idempotency_key': 'idem-2', 'canonical_intent': intent(body='amount=10'), 'state': 'fresh-attempt'},
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-2', 'attempt': 2, 'idempotency_key': 'idem-2', 'canonical_intent': intent(body='amount=20'), 'state': 'idempotent-replay'},
        ], 'reject', 'same idempotency key with different canonical intent must not mutate previous intent'),
        lifecycle_case('lifecycle.reject.retry-effect-without-boundary', base_events + [
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-3', 'attempt': 1, 'idempotency_key': 'idem-3', 'canonical_intent': intent(), 'state': 'maybe-applied', 'claims_effect_success': True, 'effect_ref': effect_ref},
        ], 'reject', 'retry behavior alone cannot claim effect success'),
        lifecycle_case('lifecycle.accept.retry-effect-after-boundary', base_events + [
            {'event': 'effect_boundary', 'cid': 'demo.web', 'effect_ref': effect_ref, 'state': 'external-confirmed'},
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-4', 'attempt': 1, 'idempotency_key': 'idem-4', 'canonical_intent': intent(), 'state': 'maybe-applied', 'claims_effect_success': True, 'effect_ref': effect_ref},
        ], 'accept', 'effect claims must point to a named effect-boundary witness'),
        lifecycle_case('lifecycle.reject.retry-after-reservation', base_events + [
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-5', 'attempt': 2, 'idempotency_key': 'idem-5', 'canonical_intent': intent(), 'state': 'pushback-delayed', 'retry_after_ms': 10000, 'reservation_claimed': True},
        ], 'reject', 'retry-after is advice, not capacity reservation'),
        lifecycle_case('lifecycle.reject.hedge-loser-proves-no-effect', base_events + [
            {'event': 'retry_attempt', 'cid': 'demo.web', 'attempt_group': 'rg-6', 'attempt': 1, 'idempotency_key': 'idem-6', 'canonical_intent': intent(), 'state': 'hedged', 'loser_fate': 'no_side_effect_proven_by_cancel'},
        ], 'reject', 'canceling a losing hedge does not prove no side effect'),
    ]
    return cases


def render_cases(cases: list[dict[str, Any]]) -> str:
    return ''.join(json.dumps(case, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n' for case in cases)


def load_corpus(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(parse_json_text(line))
        except Exception as exc:
            raise SystemExit(f'{path}:{lineno}: cannot parse JSONL: {exc}') from exc
    return out


def validate_schema_case(case: dict[str, Any]) -> tuple[bool, str]:
    try:
        if 'json_text' in case:
            obj = parse_json_text(case['json_text'])
        else:
            obj = case['json']
        if case['object_kind'] == 'CH-COMP':
            validate_ch_comp(obj)
        elif case['object_kind'] == 'CH-ACTSET':
            validate_ch_actset(obj)
        else:
            fail('unknown object_kind')
        if case['expect'] == 'accept':
            got = digest(obj)
            if got != case.get('expected_digest'):
                fail(f'digest mismatch: got {got}')
        return True, 'accepted'
    except Exception as exc:
        return False, str(exc)


def validate_lifecycle_case(case: dict[str, Any]) -> tuple[bool, str]:
    try:
        manifests: dict[str, dict[str, Any]] = {}
        manifest_digest_by_cid: dict[str, str] = {}
        actsets_by_digest: dict[str, dict[str, Any]] = {}
        current_cycle: dict[str, str] = {}
        activation_receipts: set[tuple[str, str]] = set()
        material_fresh: set[tuple[str, str]] = set()
        ready: set[tuple[str, str]] = set()
        effect_boundaries: set[str] = set()
        retry_intents: dict[str, str] = {}
        stopped: set[tuple[str, str]] = set()

        for idx, ev in enumerate(case['events']):
            kind = ev.get('event')
            where = f"{case['case_id']} event {idx} ({kind})"
            if kind == 'manifest':
                comp = validate_ch_comp(ev['component'])
                manifests[comp['cid']] = comp
                manifest_digest_by_cid[comp['cid']] = digest(comp)
            elif kind == 'actset':
                actset = validate_ch_actset(ev['actset'])
                comp = manifests.get(actset['cid'])
                if not comp:
                    fail(f'{where}: actset before manifest')
                validate_actset_against_manifest(actset, comp)
                actsets_by_digest[digest(actset)] = actset
            elif kind == 'spawn':
                cid = ev['cid']
                if ev.get('manifest_digest') != manifest_digest_by_cid.get(cid):
                    fail(f'{where}: manifest digest mismatch')
                current_cycle[cid] = ev['cycle']
            elif kind == 'runtime_end':
                cid = ev['cid']
                if current_cycle.get(cid) != ev['cycle']:
                    fail(f'{where}: ending non-current cycle')
            elif kind == 'activation_receipt':
                cid, cycle = ev['cid'], ev['cycle']
                if current_cycle.get(cid) != cycle:
                    fail(f'{where}: activation receipt for non-current cycle')
                if ev['actset_digest'] not in actsets_by_digest:
                    fail(f'{where}: unknown actset digest')
                activation_receipts.add((cid, cycle))
            elif kind == 'material_freshness':
                cid, cycle = ev['cid'], ev['cycle']
                if ev.get('claims_fresh_from_presence'):
                    fail(f'{where}: presence does not prove freshness')
                if (cid, cycle) not in activation_receipts:
                    fail(f'{where}: freshness before activation receipt')
                if ev['state'] == 'fresh':
                    material_fresh.add((cid, cycle))
            elif kind == 'readiness':
                cid, cycle = ev['cid'], ev['cycle']
                if ev['state'] == 'ready' and (cid, cycle) not in activation_receipts:
                    fail(f'{where}: ready before activation receipt')
                ready.add((cid, cycle))
            elif kind == 'serve_state':
                cid, cycle = ev['cid'], ev['cycle']
                if ev['state'] == 'serving' and (cid, cycle) not in ready:
                    fail(f'{where}: serving before ready witness')
            elif kind == 'traffic_binding':
                if ev.get('implies_ready'):
                    fail(f'{where}: traffic binding must not imply readiness')
            elif kind == 'adapter_observation':
                if ev.get('promote_to_native'):
                    fail(f'{where}: adapter observation promoted to native truth')
            elif kind == 'control_operation':
                cid = ev['cid']
                if ev.get('target_cycle') != current_cycle.get(cid):
                    fail(f'{where}: stale runtime-cycle target')
            elif kind == 'stop_request':
                if ev.get('claims_stopped'):
                    fail(f'{where}: stop request claims stopped')
            elif kind == 'stop_progress':
                cid, cycle = ev['cid'], ev['cycle']
                if ev['state'] == 'terminated':
                    stopped.add((cid, cycle))
            elif kind == 'quiesce':
                if ev.get('claims_force_kill'):
                    fail(f'{where}: quiesce claims force kill')
            elif kind == 'effect_boundary':
                effect_boundaries.add(ev['effect_ref'])
            elif kind == 'retry_attempt':
                if ev.get('reservation_claimed'):
                    fail(f'{where}: retry-after/backoff treated as reservation')
                if ev.get('loser_fate') == 'no_side_effect_proven_by_cancel':
                    fail(f'{where}: hedge loser cancel claims no side effect')
                key = ev.get('idempotency_key')
                if key:
                    intent_digest = digest(ev.get('canonical_intent'))
                    if key in retry_intents and retry_intents[key] != intent_digest:
                        fail(f'{where}: same key different canonical intent')
                    retry_intents[key] = intent_digest
                if ev.get('claims_effect_success') and ev.get('effect_ref') not in effect_boundaries:
                    fail(f'{where}: effect success without effect-boundary witness')
            else:
                fail(f'{where}: unknown event kind')
        return True, 'accepted'
    except Exception as exc:
        return False, str(exc)


def check_cases(cases: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    failures: list[str] = []
    for case in cases:
        cid = case.get('case_id')
        if not isinstance(cid, str) or not cid:
            failures.append('case without valid case_id')
            continue
        if cid in seen:
            failures.append(f'{cid}: duplicate case_id')
            continue
        seen.add(cid)
        if case.get('kind') == 'schema':
            accepted, detail = validate_schema_case(case)
        elif case.get('kind') == 'lifecycle':
            accepted, detail = validate_lifecycle_case(case)
        else:
            failures.append(f'{cid}: unknown case kind')
            continue
        expect_accept = case.get('expect') == 'accept'
        if accepted != expect_accept:
            failures.append(f"{cid}: expected {case.get('expect')} but got {'accept' if accepted else 'reject'}: {detail}")
    if failures:
        raise SystemExit('[steward-lifecycle-corpus] FAIL\n' + '\n'.join(failures))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='write deterministic corpus')
    ap.add_argument('--check', action='store_true', help='check corpus and deterministic rendering')
    ap.add_argument('--path', default=str(CORPUS_PATH))
    args = ap.parse_args()
    path = Path(args.path)
    expected = render_cases(build_cases())
    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding='utf-8')
        print(path)
    if args.check:
        if not path.exists():
            raise SystemExit(f'missing corpus: {path}')
        actual = path.read_text(encoding='utf-8')
        if actual != expected:
            raise SystemExit('[steward-lifecycle-corpus] FAIL: corpus is stale; run tools/steward_lifecycle_harness.py --write')
        check_cases(load_corpus(path))
        print('[steward-lifecycle-corpus] OK')
    if not args.write and not args.check:
        ap.error('choose --write and/or --check')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from steward_lifecycle_harness import (
    CID_RE,
    DIGEST_RE,
    fail,
    parse_json_text,
    require_bool,
    require_closed_keys,
    require_int,
    require_object,
    require_pattern,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / 'docs/40-verification/corpora/dependency-gate-corpus-v0.jsonl'

WITNESS_RE = re.compile(r'^wit_[a-z0-9]{16}$')
DEPSPEC_RE = re.compile(r'^depspec_[a-z0-9]{16}$')
DEPCHECK_RE = re.compile(r'^depcheck_[a-z0-9]{16}$')
DEPGATE_RE = re.compile(r'^depgate_[a-z0-9]{16}$')
DEPFALLBACK_RE = re.compile(r'^depfallback_[a-z0-9]{16}$')
ACTOR_RE = re.compile(r'^[a-z][a-z0-9._@/-]{0,95}$')
REF_RE = re.compile(r'^(none|sha256:[0-9a-f]{64}|[a-z][a-z0-9._:/-]{0,95})$')
TEXT_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9 .,;:_/@#()\[\]-]{0,239}$')

ISSUER_REQUIRED = {'kind', 'id'}
ISSUER_OPTIONAL = {'authority_digest'}
ISSUER_ALLOWED = ISSUER_REQUIRED | ISSUER_OPTIONAL
ISSUER_KINDS = {'steward', 'operator', 'adapter', 'policy', 'scheduler', 'auditor'}

COMMON_REQUIRED = {'schema', 'witness_id', 'cid', 'issuer', 'observed_at_ms', 'basis_refs', 'non_implications'}
COMMON_OPTIONAL = {'unknown_reason'}

DEPSPEC_REQUIRED = COMMON_REQUIRED | {
    'dependency_spec_id', 'subject_ref', 'dependency_ref', 'edge_kind', 'strength',
    'direction', 'declared_by', 'applies_to_refs', 'declared_at_ms', 'supersedes_ref',
    'reason',
}
DEPSPEC_ALLOWED = DEPSPEC_REQUIRED | COMMON_OPTIONAL
EDGE_KINDS = {'requires', 'prefers', 'ordered_before', 'ordered_after', 'observes', 'uses', 'optional', 'unknown'}
STRENGTHS = {'hard', 'soft', 'advisory', 'disabled', 'unknown'}
DIRECTIONS = {'outbound', 'inbound', 'bidirectional', 'local', 'unknown'}
DEPSPEC_NON_IMPLICATIONS = {
    'not-topology-authority', 'not-start-order', 'not-readiness', 'not-serving',
    'not-currentness', 'not-failure', 'not-authorization', 'not-admission',
    'not-work-completion', 'not-effect-success',
}

DEPCHECK_REQUIRED = COMMON_REQUIRED | {
    'dependency_check_id', 'dependency_spec_ref', 'dependency_ref', 'check_state',
    'vantage', 'checked_at_ms', 'expires_at_ms', 'stale_policy', 'latency_ms',
    'reason',
}
DEPCHECK_ALLOWED = DEPCHECK_REQUIRED | COMMON_OPTIONAL
CHECK_STATES = {'available', 'degraded', 'unavailable', 'stale', 'unknown'}
VANTAGES = {'local', 'route', 'control_surface', 'adapter', 'operator', 'probe', 'cache', 'unknown'}
STALE_POLICIES = {'block', 'degrade', 'recheck', 'ignore', 'unknown'}
DEPCHECK_NON_IMPLICATIONS = {
    'not-topology-authority', 'not-readiness', 'not-serving', 'not-currentness',
    'not-material-freshness', 'not-admission', 'not-failure', 'not-work-completion',
    'not-effect-success', 'not-authorization',
}

DEPGATE_REQUIRED = COMMON_REQUIRED | {
    'dependency_gate_id', 'request_ref', 'subject_ref', 'decision_state',
    'dependency_spec_refs', 'dependency_check_refs', 'fallback_ref', 'decided_at_ms',
    'expires_at_ms', 'reason',
}
DEPGATE_ALLOWED = DEPGATE_REQUIRED | COMMON_OPTIONAL
GATE_STATES = {'allow', 'block', 'defer', 'degrade', 'unknown'}
DEPGATE_NON_IMPLICATIONS = {
    'not-authority', 'not-authorization', 'not-approval', 'not-started', 'not-executed',
    'not-readiness', 'not-serving', 'not-demand', 'not-custody', 'not-work-completion',
    'not-effect-success', 'not-failure',
}

DEPFALLBACK_REQUIRED = COMMON_REQUIRED | {
    'dependency_fallback_id', 'dependency_spec_refs', 'mode', 'activation_state',
    'activation_refs', 'decided_at_ms', 'expires_at_ms', 'degradation_class', 'reason',
}
DEPFALLBACK_ALLOWED = DEPFALLBACK_REQUIRED | COMMON_OPTIONAL
FALLBACK_MODES = {'none', 'degraded_mode', 'cached', 'alternate', 'queue_only', 'read_only', 'disabled', 'unknown'}
FALLBACK_STATES = {'planned', 'armed', 'active', 'revoked', 'expired', 'unknown'}
DEGRADATION_CLASSES = {'none', 'capacity', 'freshness', 'feature', 'safety', 'availability', 'unknown'}
DEPFALLBACK_NON_IMPLICATIONS = {
    'not-authority', 'not-authorization', 'not-readiness', 'not-serving',
    'not-currentness', 'not-failure', 'not-repair', 'not-rollback',
    'not-work-completion', 'not-effect-success',
}

FORBIDDEN_ANYWHERE = {
    'claims_topology_authority', 'claims_dependency_ready', 'claims_dependency_satisfied',
    'claims_start_order', 'claims_started', 'claims_executed', 'claims_authority',
    'claims_authorized', 'claims_authorization', 'claims_approval', 'claims_current',
    'claims_current_state', 'claims_fresh', 'claims_material_freshness', 'claims_ready',
    'claims_readiness', 'claims_serving', 'claims_failure', 'claims_failed', 'claims_admitted',
    'claims_admission', 'claims_demand', 'claims_custody', 'claims_work_complete',
    'claims_effect_success', 'claims_repair', 'claims_rollback', 'claims_success',
    'topology_authority', 'dependency_ready', 'dependency_satisfied', 'start_order',
    'started', 'executed', 'authority', 'authorized', 'approved', 'current_state',
    'current', 'fresh', 'material_freshness', 'ready', 'readiness', 'serving',
    'failure', 'failed', 'admitted', 'admission', 'demand', 'custody', 'work_complete',
    'effect_success', 'repair_action', 'rollback_success', 'success', 'raw', 'raw_value',
    'raw_body', 'raw_log', 'raw_handle', 'raw_text', 'token', 'secret', 'bearer',
    'credential', 'password', 'cookie', 'authorization', 'value', 'path', 'raw_path',
    'host_path', 'endpoint', 'raw_endpoint', 'url', 'uri', 'fd', 'descriptor_number',
    'pid', 'ppid', 'pgid', 'cgroup', 'cgroup_path', 'systemd_unit', 'host_unit',
    'pod_name', 'container_id', 'node_name', 'process_name', 'pty_name', 'shell_job',
    'pane_text', 'command_text', 'k8s_resource_name',
}
AMBIENT_REFS = {'ambient', 'current', 'dependency:current', 'component:current', 'runtime:current', 'topology:current'}


def scan_forbidden_keys(value: Any, path: str = '$') -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_ANYWHERE:
                fail(f'{path}: forbidden field {key}')
            scan_forbidden_keys(child, f'{path}.{key}')
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            scan_forbidden_keys(child, f'{path}[{idx}]')


def require_text(value: Any, path: str) -> None:
    require_pattern(value, TEXT_RE, path)
    lowered = value.lower()
    banned = [
        'token=', 'secret=', 'bearer ', 'password=', 'cookie=', 'http:', 'https:',
        '/var/', '/proc/', '/tmp/', 'dependency proves ready', 'upstream proves ready',
        'check proves serving', 'dependency failure proves component failure',
        'topology authority', 'start order granted', 'effect success', 'rollback success',
    ]
    if any(item in lowered for item in banned):
        fail(f'{path}: raw secret, endpoint, host-path-looking material, or semantic flattery is not allowed')


def require_refs(value: Any, path: str, *, maximum: int = 16, allow_empty: bool = False, regex: re.Pattern[str] = REF_RE, allow_none: bool = False) -> list[str]:
    if not isinstance(value, list):
        fail(f'{path}: expected list')
    if len(value) > maximum:
        fail(f'{path}: too many entries')
    if not allow_empty and not value:
        fail(f'{path}: must not be empty')
    seen: set[str] = set()
    out: list[str] = []
    for idx, item in enumerate(value):
        require_pattern(item, regex, f'{path}[{idx}]')
        if item in AMBIENT_REFS:
            fail(f'{path}[{idx}]: must be exact ref, not ambient/current context')
        if item == 'none' and not allow_none:
            fail(f'{path}[{idx}]: none is not allowed here')
        if item in seen:
            fail(f'{path}: duplicate entry {item}')
        seen.add(item)
        out.append(item)
    return out


def require_ref(value: Any, path: str, *, allow_none: bool = False, regex: re.Pattern[str] = REF_RE) -> None:
    require_pattern(value, regex, path)
    if value in AMBIENT_REFS:
        fail(f'{path}: must be exact ref, not ambient/current context')
    if value == 'none' and not allow_none:
        fail(f'{path}: none is not allowed here')


def require_non_implications(value: Any, required: set[str], path: str) -> set[str]:
    items = set(require_refs(value, path, maximum=40))
    missing = sorted(required - items)
    if missing:
        fail(f'{path}: missing non-implications {missing}')
    return items


def validate_issuer(value: Any, path: str) -> dict[str, Any]:
    issuer = require_object(value, path)
    require_closed_keys(issuer, ISSUER_ALLOWED, ISSUER_REQUIRED, path)
    if issuer['kind'] not in ISSUER_KINDS:
        fail(f'{path}.kind: invalid issuer kind')
    require_pattern(issuer['id'], ACTOR_RE, f'{path}.id')
    if 'authority_digest' in issuer:
        require_pattern(issuer['authority_digest'], DIGEST_RE, f'{path}.authority_digest')
    return issuer


def validate_common(obj: Any, allowed: set[str], required: set[str], schema: str) -> dict[str, Any]:
    obj = require_object(obj, '$')
    scan_forbidden_keys(obj)
    require_closed_keys(obj, allowed, required, '$')
    if obj['schema'] != schema:
        fail(f'$.schema: expected {schema}')
    require_pattern(obj['witness_id'], WITNESS_RE, '$.witness_id')
    require_pattern(obj['cid'], CID_RE, '$.cid')
    validate_issuer(obj['issuer'], '$.issuer')
    require_int(obj['observed_at_ms'], '$.observed_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_refs(obj['basis_refs'], '$.basis_refs', maximum=32)
    if 'unknown_reason' in obj:
        require_text(obj['unknown_reason'], '$.unknown_reason')
    return obj


def validate_depspec(obj: Any) -> dict[str, Any]:
    obj = validate_common(obj, DEPSPEC_ALLOWED, DEPSPEC_REQUIRED, 'ST-DEPSPEC v0')
    require_pattern(obj['dependency_spec_id'], DEPSPEC_RE, '$.dependency_spec_id')
    require_ref(obj['subject_ref'], '$.subject_ref')
    require_ref(obj['dependency_ref'], '$.dependency_ref')
    if obj['edge_kind'] not in EDGE_KINDS:
        fail('$.edge_kind: invalid')
    if obj['strength'] not in STRENGTHS:
        fail('$.strength: invalid')
    if obj['direction'] not in DIRECTIONS:
        fail('$.direction: invalid')
    require_pattern(obj['declared_by'], ACTOR_RE, '$.declared_by')
    require_refs(obj['applies_to_refs'], '$.applies_to_refs', maximum=16)
    require_int(obj['declared_at_ms'], '$.declared_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_ref(obj['supersedes_ref'], '$.supersedes_ref', allow_none=True)
    require_text(obj['reason'], '$.reason')
    require_non_implications(obj['non_implications'], DEPSPEC_NON_IMPLICATIONS, '$.non_implications')
    if obj['strength'] == 'disabled' and obj['edge_kind'] not in {'optional', 'unknown'}:
        fail('$.strength: disabled dependency cannot remain a hard/ordering edge')
    return obj


def validate_depcheck(obj: Any) -> dict[str, Any]:
    obj = validate_common(obj, DEPCHECK_ALLOWED, DEPCHECK_REQUIRED, 'ST-DEPCHECK v0')
    require_pattern(obj['dependency_check_id'], DEPCHECK_RE, '$.dependency_check_id')
    require_ref(obj['dependency_spec_ref'], '$.dependency_spec_ref')
    require_ref(obj['dependency_ref'], '$.dependency_ref')
    if obj['check_state'] not in CHECK_STATES:
        fail('$.check_state: invalid')
    if obj['vantage'] not in VANTAGES:
        fail('$.vantage: invalid')
    require_int(obj['checked_at_ms'], '$.checked_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_int(obj['expires_at_ms'], '$.expires_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    if obj['stale_policy'] not in STALE_POLICIES:
        fail('$.stale_policy: invalid')
    require_int(obj['latency_ms'], '$.latency_ms', minimum=0, maximum=3_600_000)
    require_text(obj['reason'], '$.reason')
    require_non_implications(obj['non_implications'], DEPCHECK_NON_IMPLICATIONS, '$.non_implications')
    if obj['check_state'] in {'available', 'degraded', 'unavailable'} and obj['expires_at_ms'] <= obj['checked_at_ms']:
        fail('$.expires_at_ms: known dependency check is already stale')
    if obj['check_state'] == 'stale' and obj['stale_policy'] == 'ignore':
        fail('$.stale_policy: stale checks cannot be silently ignored')
    return obj


def validate_depgate(obj: Any) -> dict[str, Any]:
    obj = validate_common(obj, DEPGATE_ALLOWED, DEPGATE_REQUIRED, 'ST-DEPGATE v0')
    require_pattern(obj['dependency_gate_id'], DEPGATE_RE, '$.dependency_gate_id')
    require_ref(obj['request_ref'], '$.request_ref')
    require_ref(obj['subject_ref'], '$.subject_ref')
    if obj['decision_state'] not in GATE_STATES:
        fail('$.decision_state: invalid')
    require_refs(obj['dependency_spec_refs'], '$.dependency_spec_refs', maximum=16)
    require_refs(obj['dependency_check_refs'], '$.dependency_check_refs', maximum=16)
    require_ref(obj['fallback_ref'], '$.fallback_ref', allow_none=True)
    require_int(obj['decided_at_ms'], '$.decided_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_int(obj['expires_at_ms'], '$.expires_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_text(obj['reason'], '$.reason')
    require_non_implications(obj['non_implications'], DEPGATE_NON_IMPLICATIONS, '$.non_implications')
    if obj['expires_at_ms'] <= obj['decided_at_ms'] and obj['decision_state'] != 'unknown':
        fail('$.expires_at_ms: known dependency gate is already stale')
    if obj['decision_state'] == 'degrade' and obj['fallback_ref'] == 'none':
        fail('$.fallback_ref: degrade requires a fallback witness')
    if obj['decision_state'] == 'allow' and obj['fallback_ref'] != 'none':
        fail('$.fallback_ref: allow must not rely on fallback activation')
    return obj


def validate_depfallback(obj: Any) -> dict[str, Any]:
    obj = validate_common(obj, DEPFALLBACK_ALLOWED, DEPFALLBACK_REQUIRED, 'ST-DEPFALLBACK v0')
    require_pattern(obj['dependency_fallback_id'], DEPFALLBACK_RE, '$.dependency_fallback_id')
    require_refs(obj['dependency_spec_refs'], '$.dependency_spec_refs', maximum=16)
    if obj['mode'] not in FALLBACK_MODES:
        fail('$.mode: invalid')
    if obj['activation_state'] not in FALLBACK_STATES:
        fail('$.activation_state: invalid')
    require_refs(obj['activation_refs'], '$.activation_refs', maximum=16, allow_empty=True)
    require_int(obj['decided_at_ms'], '$.decided_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    require_int(obj['expires_at_ms'], '$.expires_at_ms', minimum=0, maximum=9_223_372_036_854_775_807)
    if obj['degradation_class'] not in DEGRADATION_CLASSES:
        fail('$.degradation_class: invalid')
    require_text(obj['reason'], '$.reason')
    require_non_implications(obj['non_implications'], DEPFALLBACK_NON_IMPLICATIONS, '$.non_implications')
    if obj['mode'] == 'none' and obj['activation_state'] in {'armed', 'active'}:
        fail('$.mode: none cannot be armed or active')
    if obj['activation_state'] == 'active' and not obj['activation_refs']:
        fail('$.activation_refs: active fallback needs exact activation basis')
    if obj['expires_at_ms'] <= obj['decided_at_ms'] and obj['activation_state'] not in {'expired', 'unknown'}:
        fail('$.expires_at_ms: fallback witness is already stale')
    return obj


VALIDATORS = {
    'ST-DEPSPEC': validate_depspec,
    'ST-DEPCHECK': validate_depcheck,
    'ST-DEPGATE': validate_depgate,
    'ST-DEPFALLBACK': validate_depfallback,
}


def validate_packet(obj: dict[str, Any]) -> dict[str, Any]:
    schema = obj.get('schema')
    if not isinstance(schema, str) or not schema.endswith(' v0'):
        fail('packet missing schema')
    key = schema.removesuffix(' v0')
    validator = VALIDATORS.get(key)
    if validator is None:
        fail(f'unknown packet schema {schema}')
    return validator(obj)


def base_common(schema: str, witness_id: str) -> dict[str, Any]:
    return {
        'schema': schema,
        'witness_id': witness_id,
        'cid': 'demo.web',
        'issuer': {'kind': 'steward', 'id': 'steward.core'},
        'observed_at_ms': 5000,
        'basis_refs': ['sha256:' + '5' * 64],
    }


def schema_case(case_id: str, object_kind: str, obj: dict[str, Any] | None, expect: str, note: str, *, json_text: str | None = None) -> dict[str, Any]:
    out = {'id': case_id, 'kind': 'schema', 'object_kind': object_kind, 'expect': expect, 'note': note}
    if json_text is not None:
        out['json_text'] = json_text
    else:
        out['object'] = obj
    return out


def flow_case(case_id: str, packets: list[dict[str, Any]], expect: str, note: str) -> dict[str, Any]:
    return {'id': case_id, 'kind': 'flow', 'packets': packets, 'expect': expect, 'note': note}


def build_cases() -> list[dict[str, Any]]:
    depspec_hard = {
        **base_common('ST-DEPSPEC v0', 'wit_a200000000000001'),
        'dependency_spec_id': 'depspec_2000000000000001',
        'subject_ref': 'cid/demo.web',
        'dependency_ref': 'cid/demo.db',
        'edge_kind': 'requires',
        'strength': 'hard',
        'direction': 'outbound',
        'declared_by': 'policy.deps',
        'applies_to_refs': ['op/start/demo.web'],
        'declared_at_ms': 4900,
        'supersedes_ref': 'none',
        'reason': 'web start needs database dependency check',
        'non_implications': sorted(DEPSPEC_NON_IMPLICATIONS),
    }
    depspec_soft = {
        **depspec_hard,
        'witness_id': 'wit_a200000000000002',
        'dependency_spec_id': 'depspec_2000000000000002',
        'dependency_ref': 'route/cache.cluster',
        'edge_kind': 'prefers',
        'strength': 'soft',
        'reason': 'cache is useful but not mandatory',
    }
    depspec_disabled_bad = {**depspec_hard, 'witness_id': 'wit_a200000000000003', 'dependency_spec_id': 'depspec_2000000000000003', 'strength': 'disabled'}

    depcheck_available = {
        **base_common('ST-DEPCHECK v0', 'wit_b200000000000001'),
        'dependency_check_id': 'depcheck_2000000000000001',
        'dependency_spec_ref': 'depspec_2000000000000001',
        'dependency_ref': 'cid/demo.db',
        'check_state': 'available',
        'vantage': 'probe',
        'checked_at_ms': 5010,
        'expires_at_ms': 5600,
        'stale_policy': 'block',
        'latency_ms': 42,
        'reason': 'dependency probe was available from declared vantage',
        'non_implications': sorted(DEPCHECK_NON_IMPLICATIONS),
    }
    depcheck_degraded = {
        **depcheck_available,
        'witness_id': 'wit_b200000000000002',
        'dependency_check_id': 'depcheck_2000000000000002',
        'check_state': 'degraded',
        'expires_at_ms': 5550,
        'latency_ms': 900,
        'reason': 'dependency available only in degraded condition',
    }
    depcheck_unavailable = {
        **depcheck_available,
        'witness_id': 'wit_b200000000000003',
        'dependency_check_id': 'depcheck_2000000000000003',
        'check_state': 'unavailable',
        'expires_at_ms': 5550,
        'latency_ms': 0,
        'reason': 'dependency not available from exact check vantage',
    }
    depcheck_expired = {**depcheck_available, 'witness_id': 'wit_b200000000000004', 'dependency_check_id': 'depcheck_2000000000000004', 'expires_at_ms': 5010}

    fallback_active = {
        **base_common('ST-DEPFALLBACK v0', 'wit_c200000000000001'),
        'dependency_fallback_id': 'depfallback_2000000000000001',
        'dependency_spec_refs': ['depspec_2000000000000001'],
        'mode': 'read_only',
        'activation_state': 'active',
        'activation_refs': ['genready/demo.web/ro'],
        'decided_at_ms': 5020,
        'expires_at_ms': 5400,
        'degradation_class': 'feature',
        'reason': 'dependency fallback serves read only mode',
        'non_implications': sorted(DEPFALLBACK_NON_IMPLICATIONS),
    }
    fallback_none = {
        **fallback_active,
        'witness_id': 'wit_c200000000000002',
        'dependency_fallback_id': 'depfallback_2000000000000002',
        'mode': 'none',
        'activation_state': 'planned',
        'activation_refs': [],
        'degradation_class': 'none',
        'reason': 'no fallback activation chosen',
    }

    gate_allow = {
        **base_common('ST-DEPGATE v0', 'wit_d200000000000001'),
        'dependency_gate_id': 'depgate_2000000000000001',
        'request_ref': 'opreq/demo.web/start/0001',
        'subject_ref': 'cid/demo.web',
        'decision_state': 'allow',
        'dependency_spec_refs': ['depspec_2000000000000001'],
        'dependency_check_refs': ['depcheck_2000000000000001'],
        'fallback_ref': 'none',
        'decided_at_ms': 5030,
        'expires_at_ms': 5300,
        'reason': 'hard dependency check is available for this request',
        'non_implications': sorted(DEPGATE_NON_IMPLICATIONS),
    }
    gate_block = {
        **gate_allow,
        'witness_id': 'wit_d200000000000002',
        'dependency_gate_id': 'depgate_2000000000000002',
        'decision_state': 'block',
        'dependency_check_refs': ['depcheck_2000000000000003'],
        'reason': 'hard dependency unavailable so request is blocked',
    }
    gate_degrade = {
        **gate_allow,
        'witness_id': 'wit_d200000000000003',
        'dependency_gate_id': 'depgate_2000000000000003',
        'decision_state': 'degrade',
        'dependency_check_refs': ['depcheck_2000000000000002'],
        'fallback_ref': 'depfallback_2000000000000001',
        'reason': 'dependency degraded so read only fallback is selected',
    }
    gate_stale_allow = {**gate_allow, 'witness_id': 'wit_d200000000000004', 'dependency_gate_id': 'depgate_2000000000000004', 'dependency_check_refs': ['depcheck_2000000000000004']}

    return [
        schema_case('depspec.accept.hard-requires', 'ST-DEPSPEC', depspec_hard, 'accept', 'dependency declarations can be hard and exact without becoming topology authority or readiness'),
        schema_case('depspec.accept.soft-preference', 'ST-DEPSPEC', depspec_soft, 'accept', 'soft dependency preferences are descriptive and do not create start order'),
        schema_case('depspec.reject.topology-authority-flattery', 'ST-DEPSPEC', {**depspec_hard, 'claims_topology_authority': True}, 'reject', 'dependency declarations do not create topology authority'),
        schema_case('depspec.reject.disabled-hard-edge', 'ST-DEPSPEC', depspec_disabled_bad, 'reject', 'disabled dependencies cannot remain hard required edges'),
        schema_case('depcheck.accept.available', 'ST-DEPCHECK', depcheck_available, 'accept', 'dependency availability is only a check from a bounded vantage'),
        schema_case('depcheck.accept.degraded', 'ST-DEPCHECK', depcheck_degraded, 'accept', 'degraded dependency checks explain a weaker condition without component failure claims'),
        schema_case('depcheck.reject.readiness-flattery', 'ST-DEPCHECK', {**depcheck_available, 'claims_readiness': True}, 'reject', 'available dependency does not prove subject readiness or serving'),
        schema_case('depcheck.reject.stale-known-check', 'ST-DEPCHECK', depcheck_expired, 'reject', 'known dependency checks need a future freshness bound'),
        schema_case('depfallback.accept.read-only-active', 'ST-DEPFALLBACK', fallback_active, 'accept', 'fallback activation can name a degraded mode without repair, rollback, readiness, or effect claims'),
        schema_case('depfallback.accept.none', 'ST-DEPFALLBACK', fallback_none, 'accept', 'no fallback is still an explicit weak witness'),
        schema_case('depfallback.reject.active-without-basis', 'ST-DEPFALLBACK', {**fallback_active, 'activation_refs': []}, 'reject', 'active fallback needs exact activation basis'),
        schema_case('depfallback.reject.repair-flattery', 'ST-DEPFALLBACK', {**fallback_active, 'claims_repair': True}, 'reject', 'fallback is not repair or rollback success'),
        schema_case('depgate.accept.allow', 'ST-DEPGATE', gate_allow, 'accept', 'dependency gate allow is not execution or readiness'),
        schema_case('depgate.accept.block', 'ST-DEPGATE', gate_block, 'accept', 'dependency gate block explains a request gate without component failure'),
        schema_case('depgate.reject.execution-flattery', 'ST-DEPGATE', {**gate_allow, 'claims_executed': True}, 'reject', 'dependency gate decisions are not operation execution'),
        schema_case('depgate.reject.degrade-without-fallback', 'ST-DEPGATE', {**gate_degrade, 'fallback_ref': 'none'}, 'reject', 'degraded gate decisions need fallback witness basis'),
        schema_case('depgate.reject.duplicate-json-key', 'ST-DEPGATE', None, 'reject', 'duplicate JSON keys reject before semantic validation', json_text='{"schema":"ST-DEPGATE v0","schema":"ST-DEPGATE v0","witness_id":"wit_d200000000000005","cid":"demo.web","issuer":{"kind":"steward","id":"steward.core"},"observed_at_ms":5000,"basis_refs":["sha256:5555555555555555555555555555555555555555555555555555555555555555"],"non_implications":[],"dependency_gate_id":"depgate_2000000000000005","request_ref":"opreq/demo.web/start/0005","subject_ref":"cid/demo.web","decision_state":"allow","dependency_spec_refs":[],"dependency_check_refs":[],"fallback_ref":"none","decided_at_ms":5030,"expires_at_ms":5300,"reason":"duplicate"}'),

        flow_case('dependency-gate.accept.allow-available-hard-dependency', [depspec_hard, depcheck_available, gate_allow], 'accept', 'hard dependency checks can support an allow gate without making the subject ready'),
        flow_case('dependency-gate.accept.block-unavailable-hard-dependency', [depspec_hard, depcheck_unavailable, gate_block], 'accept', 'unavailable hard dependency can block the request without proving subject failure'),
        flow_case('dependency-gate.accept.degrade-with-active-fallback', [depspec_hard, depcheck_degraded, fallback_active, gate_degrade], 'accept', 'degraded dependency plus explicit fallback can produce a degrade gate without rollout or effect claims'),
        flow_case('dependency-gate.reject.allow-with-unavailable-hard-dependency', [depspec_hard, depcheck_unavailable, {**gate_allow, 'dependency_check_refs': ['depcheck_2000000000000003']}], 'reject', 'allow cannot cite unavailable hard dependency checks'),
        flow_case('dependency-gate.reject.allow-with-stale-check', [depspec_hard, depcheck_expired, gate_stale_allow], 'reject', 'allow cannot cite a stale dependency check'),
        flow_case('dependency-gate.reject.degrade-missing-fallback', [depspec_hard, depcheck_degraded, gate_degrade], 'reject', 'degrade gate must point to a known fallback witness'),
        flow_case('dependency-gate.reject.gate-before-spec', [depcheck_available, gate_allow], 'reject', 'dependency gates cannot rely on checks whose spec is missing'),
        flow_case('dependency-gate.reject.check-spec-mismatch', [depspec_soft, depcheck_available, {**gate_allow, 'dependency_spec_refs': ['depspec_2000000000000002']}], 'reject', 'gate spec refs and check spec refs must agree'),
        flow_case('dependency-gate.reject.duplicate-gate-id-drift', [gate_allow, {**gate_allow, 'witness_id': 'wit_d200000000000006', 'reason': 'same gate id with different bytes'}], 'reject', 'dependency gate ids cannot be reused with different canonical bytes'),
    ]


def validate_flow(packets: list[dict[str, Any]]) -> None:
    by_schema: dict[str, list[dict[str, Any]]] = {}
    canonical_by_domain_id: dict[tuple[str, str], str] = {}
    for idx, packet in enumerate(packets):
        obj = validate_packet(packet)
        schema = obj['schema'].removesuffix(' v0')
        by_schema.setdefault(schema, []).append(obj)
        if schema == 'ST-DEPSPEC':
            domain_id = obj['dependency_spec_id']
        elif schema == 'ST-DEPCHECK':
            domain_id = obj['dependency_check_id']
        elif schema == 'ST-DEPGATE':
            domain_id = obj['dependency_gate_id']
        elif schema == 'ST-DEPFALLBACK':
            domain_id = obj['dependency_fallback_id']
        else:
            domain_id = obj['witness_id']
        key = (schema, domain_id)
        raw = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        prior = canonical_by_domain_id.get(key)
        if prior is not None and prior != raw:
            fail(f'packet {idx}: duplicate {schema} domain id with different canonical bytes')
        canonical_by_domain_id[key] = raw

    specs = {p['dependency_spec_id']: p for p in by_schema.get('ST-DEPSPEC', [])}
    checks = {c['dependency_check_id']: c for c in by_schema.get('ST-DEPCHECK', [])}
    fallbacks = {f['dependency_fallback_id']: f for f in by_schema.get('ST-DEPFALLBACK', [])}

    for check in by_schema.get('ST-DEPCHECK', []):
        spec = specs.get(check['dependency_spec_ref'])
        if spec is None:
            fail(f'dependency check {check["dependency_check_id"]}: missing dependency spec {check["dependency_spec_ref"]}')
        if spec['dependency_ref'] != check['dependency_ref']:
            fail(f'dependency check {check["dependency_check_id"]}: dependency ref mismatch')

    for fallback in by_schema.get('ST-DEPFALLBACK', []):
        for ref in fallback['dependency_spec_refs']:
            if ref not in specs:
                fail(f'fallback {fallback["dependency_fallback_id"]}: missing dependency spec {ref}')

    for gate in by_schema.get('ST-DEPGATE', []):
        gate_specs = {ref: specs.get(ref) for ref in gate['dependency_spec_refs']}
        if any(spec is None for spec in gate_specs.values()):
            fail(f'dependency gate {gate["dependency_gate_id"]}: missing dependency spec')
        gate_checks = []
        for ref in gate['dependency_check_refs']:
            check = checks.get(ref)
            if check is None:
                fail(f'dependency gate {gate["dependency_gate_id"]}: missing dependency check {ref}')
            gate_checks.append(check)
            if check['dependency_spec_ref'] not in gate_specs:
                fail(f'dependency gate {gate["dependency_gate_id"]}: check {ref} points outside gate spec set')
            if check['expires_at_ms'] <= gate['decided_at_ms']:
                fail(f'dependency gate {gate["dependency_gate_id"]}: check {ref} is stale at decision time')
        if gate['fallback_ref'] != 'none' and gate['fallback_ref'] not in fallbacks:
            fail(f'dependency gate {gate["dependency_gate_id"]}: missing fallback {gate["fallback_ref"]}')
        hard_checks = [c for c in gate_checks if specs[c['dependency_spec_ref']]['strength'] == 'hard']
        if gate['decision_state'] == 'allow':
            for check in hard_checks:
                if check['check_state'] != 'available':
                    fail(f'dependency gate {gate["dependency_gate_id"]}: allow cites non-available hard dependency {check["dependency_check_id"]}')
        if gate['decision_state'] == 'degrade':
            if gate['fallback_ref'] == 'none':
                fail(f'dependency gate {gate["dependency_gate_id"]}: degrade without fallback')
            fallback = fallbacks[gate['fallback_ref']]
            if fallback['activation_state'] != 'active':
                fail(f'dependency gate {gate["dependency_gate_id"]}: degrade fallback is not active')
            for ref in fallback['dependency_spec_refs']:
                if ref not in gate_specs:
                    fail(f'dependency gate {gate["dependency_gate_id"]}: fallback spec outside gate spec set')


def run_schema_case(case: dict[str, Any]) -> None:
    try:
        if case.get('json_text') is not None:
            obj = parse_json_text(case['json_text'])
        else:
            obj = case['object']
        object_kind = case['object_kind']
        validator = VALIDATORS.get(object_kind)
        if validator is None:
            fail(f'unknown object_kind {object_kind}')
        validator(obj)
        actual = 'accept'
    except Exception:
        actual = 'reject'
    if actual != case['expect']:
        fail(f"{case['id']}: expected {case['expect']} got {actual}")


def run_flow_case(case: dict[str, Any]) -> None:
    try:
        validate_flow(case['packets'])
        actual = 'accept'
    except Exception:
        actual = 'reject'
    if actual != case['expect']:
        fail(f"{case['id']}: expected {case['expect']} got {actual}")


def render_cases(cases: list[dict[str, Any]]) -> str:
    return ''.join(json.dumps(case, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n' for case in cases)


def load_corpus(path: Path = CORPUS_PATH) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def check_cases(cases: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for case in cases:
        if case['id'] in seen:
            fail(f"duplicate case id {case['id']}")
        seen.add(case['id'])
        if case['kind'] == 'schema':
            run_schema_case(case)
        elif case['kind'] == 'flow':
            run_flow_case(case)
        else:
            fail(f"{case['id']}: unknown kind")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if not args.write and not args.check:
        ap.error('choose --write and/or --check')
    if args.write:
        CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        CORPUS_PATH.write_text(render_cases(build_cases()), encoding='utf-8')
        print(CORPUS_PATH)
    if args.check:
        check_cases(load_corpus())
        print('[steward_dependency_gate_harness] OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

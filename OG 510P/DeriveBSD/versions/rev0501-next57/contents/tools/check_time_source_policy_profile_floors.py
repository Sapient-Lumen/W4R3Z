#!/usr/bin/env python3
"""Guardrail for profile-mapped trustworthy-time source-policy floors."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def count_protocol(policy: dict, protocol: str) -> int:
    return sum(1 for src in policy.get('sources', []) if src.get('protocol') == protocol)


errors: list[str] = []

FLOORS = {
    'spec/examples/time.source.policy.fleet_host.json': {
        'min_total_sources': 3,
        'min_nts': 1,
        'min_roughtime': 1,
        'min_sources_floor': 2,
        'max_skew_ceiling': 50,
        'require_vendor_diversity': True,
        'bootstrap': {
            'allow_rtc': True,
            'max_rtc_age_sec': 300,
            'max_forward_jump_ms': 1000,
            'max_backward_jump_ms': 0,
        },
    },
    'spec/examples/time.source.policy.workstation.json': {
        'min_total_sources': 2,
        'min_nts': 1,
        'min_roughtime': 0,
        'min_sources_floor': 1,
        'max_skew_ceiling': 200,
        'require_vendor_diversity': False,
        'bootstrap': {
            'allow_rtc': True,
            'max_rtc_age_sec': 86400,
            'max_forward_jump_ms': 60000,
            'max_backward_jump_ms': 1000,
        },
    },
    'spec/examples/time.source.policy.general_os.json': {
        'min_total_sources': 1,
        'min_nts': 1,
        'min_roughtime': 0,
        'min_sources_floor': 1,
        'max_skew_ceiling': 1000,
        'require_vendor_diversity': False,
        'bootstrap': {
            'allow_rtc': True,
            'max_rtc_age_sec': 604800,
            'max_forward_jump_ms': 300000,
            'max_backward_jump_ms': 5000,
        },
    },
    'spec/examples/time.source.policy.appliance_factory.json': {
        'min_total_sources': 3,
        'min_nts': 1,
        'min_roughtime': 1,
        'min_sources_floor': 2,
        'max_skew_ceiling': 50,
        'require_vendor_diversity': True,
        'bootstrap': {
            'allow_rtc': False,
        },
    },
}

for rel, floor in FLOORS.items():
    policy = load_json(rel)
    if len(policy.get('sources', [])) < floor['min_total_sources']:
        errors.append(f'{rel}: must configure at least {floor["min_total_sources"]} authenticated sources')
    if count_protocol(policy, 'nts') < floor['min_nts']:
        errors.append(f'{rel}: must include at least {floor["min_nts"]} NTS source(s)')
    if count_protocol(policy, 'roughtime') < floor['min_roughtime']:
        errors.append(f'{rel}: must include at least {floor["min_roughtime"]} Roughtime source(s)')

    quorum = policy.get('quorum') or {}
    if quorum.get('min_sources', -1) < floor['min_sources_floor']:
        errors.append(f'{rel}: quorum.min_sources floor mismatch')
    if quorum.get('max_skew_ms', 10**18) > floor['max_skew_ceiling']:
        errors.append(f'{rel}: quorum.max_skew_ms ceiling mismatch')
    if quorum.get('require_vendor_diversity') is not floor['require_vendor_diversity']:
        errors.append(f'{rel}: quorum.require_vendor_diversity mismatch')

    bootstrap = policy.get('bootstrap') or {}
    for key, expected in floor['bootstrap'].items():
        if bootstrap.get(key) != expected:
            errors.append(f'{rel}: bootstrap.{key} must be {expected!r}')

DOC_TOKENS = {
    'adrs/ADR-0312-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md': [
        '`time-source-policy` floors are now profile-mapped and finite.',
        'at least **one `nts` source and one `roughtime` source** present',
        'signed offline-time/bootstrap story remains a separate lane',
    ],
    'docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md': [
        'what concrete `time-source-policy` floor does each product shape compile to?',
        "This is the archive's concrete answer to \"when does Roughtime stop being optional?\"",
        'steady-state production policy keeps `allow_rtc = false`',
    ],
    'docs/468-trustworthy-time-posture-by-profile.md': [
        'The archive now also fixes the next smaller implementation floor in `docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`:',
    ],
    'docs/307-time-sources-in-practice-chrony-nts-and-roughtime.md': [
        'The profile-mapped `time-source-policy` floor is no longer vague either:',
        'A/D now require mixed authenticated source sets (NTS plus Roughtime) and 2-of-N quorum',
    ],
    'docs/283-trustworthy-time-nts-roughtime-and-lkgt.md': [
        'Concrete profile floors now live in `docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md`.',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        'signed offline-time token envelope, approval semantics, and replay/retention behavior',
        'monitor/escalation behavior when authenticated sources disagree or disappear for long periods',
    ],
    'docs/98-archive-hygiene.md': [
        'check_time_source_policy_profile_floors.py',
        'profile-mapped trustworthy-time floor',
    ],
    'docs/99-llm-runbook.md': [
        'check_time_source_policy_profile_floors.py',
        'mixed authenticated source sets (NTS + Roughtime)',
    ],
    'docs/00-index.md': [
        'docs/722-time-source-policy-profile-floors-stay-finite-and-profile-mapped.md',
        'check_time_source_policy_profile_floors.py',
    ],
}
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f'{rel}: missing token {token!r}')

if errors:
    print('time source-policy profile-floor check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('time source-policy profile-floor check passed')

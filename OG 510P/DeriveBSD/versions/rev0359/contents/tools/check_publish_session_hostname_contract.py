#!/usr/bin/env python3
"""Guardrail for publish-session published-endpoint hostname posture."""
from __future__ import annotations

import ipaddress
import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def hostname_errors(doc: dict) -> list[str]:
    endpoint = doc.get('published_endpoint') or {}
    hostname = endpoint.get('hostname')
    if not hostname:
        return []
    errs: list[str] = []
    lower = hostname.lower().rstrip('.')
    if lower == 'localhost' or lower.endswith('.localhost'):
        errs.append('published_endpoint.hostname must stay non-local and not use localhost/.localhost')
    try:
        if ipaddress.ip_address(hostname).is_loopback:
            errs.append('published_endpoint.hostname must not be a loopback IP literal')
    except ValueError:
        pass
    return errs


def main() -> int:
    errors: list[str] = []
    schema = load_json('spec/net.publish.session.schema.json')
    example = load_json('spec/examples/net.publish.session.json')
    validator = Draft202012Validator(schema)

    errs = validate(validator, example)
    for msg in errs[:20]:
        errors.append(f'spec/examples/net.publish.session.json invalid: {msg}')
    if len(errs) > 20:
        errors.append(f'spec/examples/net.publish.session.json invalid with {len(errs) - 20} additional errors')
    errors.extend(hostname_errors(example))

    scheme_bad = deepcopy(example)
    scheme_bad['published_endpoint']['hostname'] = 'https://preview-7c3f.relay.example.invalid'
    if not validate(validator, scheme_bad):
        errors.append('publish-session example with scheme-bearing published_endpoint.hostname must fail validation')

    port_bad = deepcopy(example)
    port_bad['published_endpoint']['hostname'] = 'preview-7c3f.relay.example.invalid:443'
    if not validate(validator, port_bad):
        errors.append('publish-session example with host:port published_endpoint.hostname must fail validation')

    path_bad = deepcopy(example)
    path_bad['published_endpoint']['hostname'] = 'preview-7c3f.relay.example.invalid/hooks/demo'
    if not validate(validator, path_bad):
        errors.append('publish-session example with path-bearing published_endpoint.hostname must fail validation')

    upper_bad = deepcopy(example)
    upper_bad['published_endpoint']['hostname'] = 'Preview-7c3f.relay.example.invalid'
    if not validate(validator, upper_bad):
        errors.append('publish-session example with uppercase published_endpoint.hostname must fail validation')

    localhost_bad = deepcopy(example)
    localhost_bad['published_endpoint']['hostname'] = 'localhost'
    if not hostname_errors(localhost_bad):
        errors.append('publish-session published_endpoint.hostname must fail when it is localhost')

    dotlocalhost_bad = deepcopy(example)
    dotlocalhost_bad['published_endpoint']['hostname'] = 'preview.localhost'
    if not hostname_errors(dotlocalhost_bad):
        errors.append('publish-session published_endpoint.hostname must fail when it is under .localhost')

    loopback_bad = deepcopy(example)
    loopback_bad['published_endpoint']['hostname'] = '127.0.0.1'
    if not hostname_errors(loopback_bad):
        errors.append('publish-session published_endpoint.hostname must fail when it is a loopback IP literal')

    reverse_ok = deepcopy(example)
    reverse_ok['published_endpoint']['exposure_scope'] = 'tailnet'
    reverse_ok['published_endpoint']['access_model'] = 'reverse-forward'
    reverse_ok['published_endpoint']['locator_posture'] = 'tailnet-device-name'
    reverse_ok['published_endpoint']['hostname'] = 'preview-dev-17.tailnet.example.invalid'
    reverse_ok['published_endpoint']['port'] = 8443
    reverse_ok['published_endpoint'].pop('url_hint', None)
    reverse_ok['published_endpoint'].pop('path_prefix', None)
    reverse_ok['published_endpoint']['audience']['class'] = 'tailnet-users'
    reverse_ok['published_endpoint']['audience']['authn_mode'] = 'tailnet-identity'
    reverse_ok['published_endpoint']['audience'].pop('validation_hint', None)
    reverse_ok['published_endpoint'].pop('secret_handoff', None)
    reverse_ok['authority']['trigger'] = 'operator-session'
    reverse_ok['authority'].pop('consent_receipt_digest', None)
    reverse_ok['authority']['operator_session_digest'] = 'sha256:' + 'ab' * 32
    reverse_ok['lifecycle']['end_conditions'] = [
        'lease-expiry',
        'manual-revoke',
        'local-service-unavailable',
        'operator-session-end',
        'host-reboot',
    ]
    reverse_ok['relay']['destination_hint'] = 'tailnet preview-dev-17:8443'
    reverse_ok['relay']['remote_locator']['kind'] = 'object-path'
    reverse_ok['relay']['remote_locator']['value'] = 'tailnet/devices/preview-dev-17/services/8443'
    if validate(validator, reverse_ok) or hostname_errors(reverse_ok):
        errors.append('publish-session reverse-forward example with lowercase DNS-host-shaped hostname should validate')

    doc_checks = {
        'docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md': ['published_endpoint.hostname', 'host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md': ['published_endpoint.hostname', 'host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/575-publish-session-endpoint-hints-follow-access-model.md': ['published_endpoint.hostname', 'host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md': ['published_endpoint.hostname', 'localhost', 'example.invalid'],
        'docs/286-inbound-listen-broker-and-firewall-leases.md': ['published_endpoint.hostname', 'host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/460-inbound-listen-posture-by-profile.md': ['published_endpoint.hostname', 'host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/98-archive-hygiene.md': ['tools/check_publish_session_hostname_contract.py', 'published_endpoint.hostname'],
        'docs/99-llm-runbook.md': ['docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md', 'tools/check_publish_session_hostname_contract.py'],
        'docs/110-juicy-os-lessons.md': ['Temporary sharing published-endpoint hostnames should stay host-shaped', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0171', 'published_endpoint.hostname'],
        'docs/32-curated-references.md': ['RFC 2606: Reserved Top Level DNS Names', 'RFC 6761: Special-Use Domain Names', 'RFC 3986: URI Generic Syntax'],
        'README.md': ['docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md', 'published_endpoint.hostname'],
        'docs/00-index.md': ['docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md', 'published_endpoint.hostname'],
        'CHANGELOG.md': ['ADR-0171', 'docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f'{rel} missing required publish-session hostname token: {needle}')

    if errors:
        print('Publish-session hostname posture contract check FAILED:')
        for err in errors:
            print(f'- {err}')
        return 1
    print('Publish-session hostname posture contract check OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guardrail for publish-session local-service URI-hint posture."""
from __future__ import annotations

import ipaddress
from copy import deepcopy
from pathlib import Path

from cube_digest_lib import load_json as strict_load_json
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    return strict_load_json(ROOT, rel)


def validate(validator: Draft202012Validator, doc: dict) -> list[str]:
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))]


def is_loopback_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    host = hostname.rstrip('.').lower()
    if host == 'localhost' or host.endswith('.localhost'):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def hint_errors(doc: dict) -> list[str]:
    local = doc.get('local_service') or {}
    hint = local.get('service_uri_hint')
    if not hint:
        return []
    parsed = urlsplit(hint)
    errs: list[str] = []
    if not parsed.scheme or not parsed.netloc:
        errs.append('local_service.service_uri_hint must stay an absolute URI with authority')
        return errs
    if parsed.username is not None or parsed.password is not None:
        errs.append('local_service.service_uri_hint must not carry userinfo')
    if parsed.query:
        errs.append('local_service.service_uri_hint must not carry a query')
    if parsed.fragment:
        errs.append('local_service.service_uri_hint must not carry a fragment')
    if not is_loopback_host(parsed.hostname):
        errs.append('local_service.service_uri_hint host must stay loopback-shaped (localhost/.localhost or loopback IP)')
    proto = local.get('protocol')
    if proto in {'http', 'https', 'ssh'} and parsed.scheme != proto:
        errs.append(f'local_service.service_uri_hint scheme must match local_service.protocol={proto}')
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
    errors.extend(hint_errors(example))

    lan_bad = deepcopy(example)
    lan_bad['local_service']['service_uri_hint'] = 'http://preview-box.lan:4040'
    if not validate(validator, lan_bad):
        errors.append('publish-session example with non-loopback local_service.service_uri_hint must fail validation')
    if not hint_errors(lan_bad):
        errors.append('publish-session local_service.service_uri_hint must fail when the host drifts off loopback')

    query_bad = deepcopy(example)
    query_bad['local_service']['service_uri_hint'] = 'http://127.0.0.1:4040/?token=secret'
    if not validate(validator, query_bad):
        errors.append('publish-session example with query-bearing local_service.service_uri_hint must fail validation')
    if not hint_errors(query_bad):
        errors.append('publish-session local_service.service_uri_hint must fail when it carries a query token')

    userinfo_bad = deepcopy(example)
    userinfo_bad['local_service']['service_uri_hint'] = 'http://user:pass@localhost:4040/'
    if not validate(validator, userinfo_bad):
        errors.append('publish-session example with userinfo-bearing local_service.service_uri_hint must fail validation')
    if not hint_errors(userinfo_bad):
        errors.append('publish-session local_service.service_uri_hint must fail when it carries userinfo')

    scheme_bad = deepcopy(example)
    scheme_bad['local_service']['protocol'] = 'http'
    scheme_bad['local_service']['service_uri_hint'] = 'ssh://localhost:4040/'
    if not validate(validator, scheme_bad):
        errors.append('publish-session example with mismatched local_service.protocol/service_uri_hint scheme must fail validation')
    if not hint_errors(scheme_bad):
        errors.append('publish-session local_service.service_uri_hint must fail when scheme contradicts local_service.protocol')

    localhost_sub_ok = deepcopy(example)
    localhost_sub_ok['local_service']['service_uri_hint'] = 'http://preview.localhost:4040/'
    if validate(validator, localhost_sub_ok) or hint_errors(localhost_sub_ok):
        errors.append('publish-session example using a .localhost local_service.service_uri_hint should validate')

    doc_checks = {
        'docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md': ['local_service.service_uri_hint', 'loopback-shaped', 'docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md'],
        'docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md': ['local_service.service_uri_hint', '.localhost', 'userinfo'],
        'docs/286-inbound-listen-broker-and-firewall-leases.md': ['local_service.service_uri_hint', 'loopback-shaped'],
        'docs/460-inbound-listen-posture-by-profile.md': ['local_service.service_uri_hint', 'loopback-shaped'],
        'docs/98-archive-hygiene.md': ['tools/check_publish_session_local_service_hint_contract.py', 'local_service.service_uri_hint'],
        'docs/99-llm-runbook.md': ['docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md', 'tools/check_publish_session_local_service_hint_contract.py'],
        'docs/110-juicy-os-lessons.md': ['Temporary sharing local-service URI hints should stay loopback-shaped', 'docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md'],
        'docs/266-open-questions-and-risk-register.md': ['ADR-0170', 'local_service.service_uri_hint'],
        'docs/32-curated-references.md': ['RFC 6761: Special-Use Domain Names', 'RFC 3986: URI Generic Syntax'],
        'README.md': ['docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md', 'local_service.service_uri_hint'],
        'docs/00-index.md': ['docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md', 'local_service.service_uri_hint'],
        'CHANGELOG.md': ['ADR-0170', 'docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md'],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                errors.append(f'{rel} missing required publish-session local-service-hint token: {needle}')

    if errors:
        print('Publish-session local-service URI-hint contract check FAILED:')
        for err in errors:
            print(f'- {err}')
        return 1
    print('Publish-session local-service URI-hint contract check OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

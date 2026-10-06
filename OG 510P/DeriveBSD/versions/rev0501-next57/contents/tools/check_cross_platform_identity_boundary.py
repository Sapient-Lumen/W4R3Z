#!/usr/bin/env python3
"""Guardrail for the cross-compilation platform-identity boundary."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    'adrs/ADR-0291-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md': [
        'platform identity is explicit typed metadata, not store-path syntax',
        'canonical platform-role model is `build_platform`, `host_platform`, and optional `target_platform`',
        'Store paths stay content-addressed and digest-first',
    ],
    'docs/701-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md': [
        'Store paths stay digest-only',
        'Platform roles are explicit typed data',
        'Runtime closure and activation bind `host_platform`',
        'target triples are aliases, not authority',
    ],
    'docs/03-store.md': [
        'platform identity is carried in typed metadata rather than encoded into store paths',
        '`build_platform` / `host_platform` / optional `target_platform`',
    ],
    'docs/90-closure-proof.md': [
        '`host_platform` (not `build_platform`)',
        'build-only tools do not become runtime closure authority',
    ],
    'docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md': [
        'platform-role helpers from `spec/platform.identity.schema.json` and `spec/platform.roles.schema.json`',
        '`build_platform` / `host_platform` model',
    ],
    'docs/266-open-questions-and-risk-register.md': [
        '## 2) Cross compilation and multi-arch closures [DECIDED]',
        'store paths stay content-addressed and digest-first',
        'runtime closure and activation bind `host_platform`',
    ],
    'docs/98-archive-hygiene.md': [
        'check_cross_platform_identity_boundary.py',
        'store paths are not a target-triple namespace',
    ],
    'docs/99-llm-runbook.md': [
        'check_cross_platform_identity_boundary.py',
        'cross-compilation identity is explicit `build_platform` / `host_platform` / optional `target_platform` metadata',
    ],
    'docs/00-index.md': [
        'docs/701-cross-compilation-platform-identity-stays-build-host-target-shaped-and-not-store-path-encoded.md',
        'check_cross_platform_identity_boundary.py',
    ],
    'spec/platform.roles.schema.json': [
        '"build_platform"',
        '"host_platform"',
        '"target_platform"',
    ],
    'spec/base.set.schema.json': [
        '"build_platform"',
        '"host_platform"',
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print('cross-platform identity boundary check failed:', file=sys.stderr)
    for err in errors:
        print(f'- {err}', file=sys.stderr)
    raise SystemExit(1)

print('cross-platform identity boundary check passed')

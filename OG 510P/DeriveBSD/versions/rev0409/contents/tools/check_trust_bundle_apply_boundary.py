#!/usr/bin/env python3
"""Guardrail for trust-bundle apply receipts staying authoritative and distinct from diff review."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "spec/pki.trust.bundle.apply.receipt.schema.json": [
        'pki.trust.bundle.apply.receipt',
        'bundle_digest',
        'renderings',
        'applied',
    ],
    "spec/examples/pki.trust.bundle.apply.receipt.json": [
        'pki.trust.bundle.apply.receipt',
        'bundle_digest',
        'renderings',
        '"status": "applied"',
    ],
    "spec/pki.event.schema.json": [
        'pki_trust_bundle_apply_receipt_digest',
    ],
    "docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md": [
        'pki.trust.bundle.apply.receipt',
        'pki-trust-bundle remains authoritative',
        'not a new product-profile key',
        'what exact trust view did this host/unit really serve?',
    ],
    "adrs/ADR-0212-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md": [
        'pki.trust.bundle.apply.receipt',
        'One receipt = one canonical bundle→one target view.',
        'No new `product.profiles.defaults` key is introduced.',
    ],
    "docs/228-pki-and-identity-lifecycle-as-evidence.md": [
        'pki.trust.bundle.apply.receipt',
        'pki.trust-bundle.updated',
    ],
    "docs/304-trust-bundles-and-ca-injection-as-artifacts.md": [
        'pki.trust.bundle.apply.receipt',
        'joined `pki.trust-bundle.updated` event',
    ],
    "docs/327-shadow-trust-and-system-ca-governance.md": [
        'canonical `pki-trust-bundle` plus the joined `pki.trust.bundle.apply.receipt`',
    ],
    "docs/434-pki-trust-bundle-diff-as-review-surface.md": [
        'pki.trust.bundle.apply.receipt',
        'what exact trust view was served',
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
    ],
    "docs/480-trust-bundle-posture-by-profile.md": [
        'trust-bundle apply proof',
        'pki.trust.bundle.apply.receipt',
    ],
    "docs/229-evidence-spine-overview.md": [
        'trust-bundle apply receipts',
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
    ],
    "docs/266-open-questions-and-risk-register.md": [
        'ADR-0212',
        'pki.trust.bundle.apply.receipt',
    ],
    "docs/98-archive-hygiene.md": [
        'check_trust_bundle_apply_boundary.py',
        'keep `pki-trust-bundle` authoritative',
    ],
    "docs/99-llm-runbook.md": [
        'check_trust_bundle_apply_boundary.py',
        'typed proof of the exact served runtime trust view',
    ],
    "docs/110-juicy-os-lessons.md": [
        'typed `pki.trust.bundle.apply.receipt` proof',
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
    ],
    "docs/32-curated-references.md": [
        'trust-manager ClusterBundle transition announcement',
    ],
    "README.md": [
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
        'spec/pki.trust.bundle.apply.receipt.schema.json',
    ],
    "docs/00-index.md": [
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
        '2026-03-21r352',
    ],
    "CHANGELOG.md": [
        '2026-03-21r352',
        'tools/check_trust_bundle_apply_boundary.py',
        'docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md',
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("Trust-bundle apply boundary check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

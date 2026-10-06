#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_TOKENS = {
    "docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "top-level basename collisions fail closed",
    ],
    "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md": [
        "first implementation of the reviewed finite collection handoff does not support trusted-UI top-level aliasing",
        "basename collisions simply fail closed",
        "later explicit RFC/ADR cut",
    ],
    "adrs/ADR-0278-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md": [
        "trusted-UI top-level aliasing is **not supported**",
        "handoff creation must **fail closed**",
        "later RFC/ADR cut",
    ],
    "rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md": [
        "Keep the first implementation fail-closed on top-level collisions",
        "should **not** support trusted-UI top-level aliasing",
        "later explicit RFC/ADR cut",
    ],
    "docs/205-data-transfer-portals-clipboard-and-dnd.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "top-level basename collisions now fail closed",
    ],
    "docs/538-workstation-cross-domain-datatransfer-floor.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "keeps top-level alias/disambiguation UX out of scope",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "keep top-level alias/disambiguation UX out of the first implementation",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "fail closed and ask for revised selection",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "does not mint reviewed alias state",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0278",
        "trusted-UI top-level aliasing out",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_datatransfer_collection_first_impl_aliasing.py",
        "collection-first-impl-aliasing",
    ],
    "docs/99-llm-runbook.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "check_workstation_datatransfer_collection_first_impl_aliasing.py",
    ],
    "docs/110-juicy-os-lessons.md": [
        "## 90zd) The first implementation should fail closed on top-level collisions",
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
    ],
    "docs/00-index.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "top-level basename collisions",
    ],
    "README.md": [
        "docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md",
        "fails closed on top-level basename collisions",
    ],
}

errors: list[str] = []
for rel, tokens in DOC_TOKENS.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{rel}: missing token {token!r}")

if errors:
    print("workstation data-transfer collection first-impl-aliasing check failed:", file=sys.stderr)
    for err in errors:
        print(f"- {err}", file=sys.stderr)
    raise SystemExit(1)

print("workstation data-transfer collection first-impl-aliasing check passed")

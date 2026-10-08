#!/usr/bin/env python3
"""scripts/check_doc_envelope_kind_references.py

Drift firewall: envelope kind references in documentation must be registered.

Scope:
- Markdown files under docs/ and top-level *.md
- Only references that explicitly use a 'kind:' or 'Envelope kind:' label.

Rationale:
Registry drift is easy to catch in example packets (scripts/check_envelope_kinds.py),
but documentation can silently accumulate typos or stale kind names.
This check keeps the verifier-facing surface coherent without policing casual prose.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"

# Match patterns like:
#   - kind: `hfv.public.notice`
#   Envelope kind: `hfv.publication.contract`
# Backticks are optional.
KIND_RE = re.compile(r"(?im)\b(?:envelope\s+kind|kind)\s*:\s*`?(hfv\.[a-z0-9_.]+)`?")


def load_registered_kinds() -> set[str]:
    if not REGISTRY.exists():
        raise SystemExit(f"Missing registry: {REGISTRY}")
    with REGISTRY.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"kind", "track", "payload_schema", "stability", "description"}
        if set(r.fieldnames or []) != required:
            raise SystemExit(
                f"Registry columns must be exactly {sorted(required)}; got {r.fieldnames}"
            )
        out: set[str] = set()
        for row in r:
            k = (row.get("kind") or "").strip()
            if k:
                out.add(k)
        return out


def iter_md_files() -> list[Path]:
    md: list[Path] = []
    if (ROOT / "docs").exists():
        md.extend((ROOT / "docs").rglob("*.md"))
    md.extend([p for p in ROOT.glob("*.md") if p.is_file()])
    return sorted(set(md))


def main() -> int:
    kinds = load_registered_kinds()
    errors: list[str] = []

    for p in iter_md_files():
        rel = p.relative_to(ROOT)
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            errors.append(f"failed to read {rel}: {e}")
            continue

        for m in KIND_RE.finditer(txt):
            k = m.group(1)
            if k not in kinds:
                # Provide a small excerpt pointer (line number) for fast fixes.
                line = txt.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: unregistered envelope kind reference: {k}")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

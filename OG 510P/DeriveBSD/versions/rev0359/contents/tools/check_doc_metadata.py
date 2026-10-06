#!/usr/bin/env python3
"""Check that newer high-leverage docs carry a tiny metadata block (and that values are sane).

Rationale:
- Helps humans and LLMs avoid amnesia about tiers/profiles/pillars.
- Keeps A–D + tier discipline mechanically visible at the doc surface.

Rule (intentionally narrow):
- Docs with numeric prefix >= 397 MUST include, near the top:
  - **Tier:**
  - **Profiles:**
  - **Pillars:**

Additionally (lightweight validation):
- Tier must start with one of {A,B,C,D,E} (feature-tier discipline).
- Profiles must be a comma-separated subset of {A,B,C,D}.
- Pillars must be a comma-separated subset of:
    reproducibility, isolation, supply-chain, operability

This only applies to the meta-engineering / late-doc range so we don't
retrofit hundreds of older notes.

Usage:
  python3 tools/check_doc_metadata.py

Exit codes:
  0: OK
  1: At least one doc missing required metadata or has invalid values
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

PROFILE_ALIASES = ROOT / "spec" / "product.profile_aliases.json"
PRODUCT_PROFILES = ROOT / "spec" / "examples" / "product.profiles.json"

DOC_RE = re.compile(r"^(?P<num>\d+)-.+\.md$")

TIER_RE = re.compile(r"^\*\*Tier:\*\*\s*(?P<val>.+?)\s*$")
PROFILES_RE = re.compile(r"^\*\*Profiles:\*\*\s*(?P<val>.+?)\s*$")
PILLARS_RE = re.compile(r"^\*\*Pillars:\*\*\s*(?P<val>.+?)\s*$")

ALLOWED_TIERS = {"A", "B", "C", "D", "E"}
ALLOWED_PROFILES = {"A", "B", "C", "D"}  # legacy letter aliases
ALLOWED_PILLARS = {"reproducibility", "isolation", "supply-chain", "operability"}


def _load_profile_ids() -> tuple[dict[str, str], set[str]]:
    aliases: dict[str, str] = {}
    try:
        obj = json.loads(PROFILE_ALIASES.read_text(encoding="utf-8"))
        aliases = {k.strip(): v.strip() for k, v in (obj.get("aliases") or {}).items() if k and v}
    except Exception:
        aliases = {"A": "fleet_host", "B": "workstation", "C": "general_os", "D": "appliance_factory"}

    ids: set[str] = set()
    try:
        pobj = json.loads(PRODUCT_PROFILES.read_text(encoding="utf-8"))
        for pid in (pobj.get("profiles") or {}).keys():
            if isinstance(pid, str) and pid.strip():
                ids.add(pid.strip())
    except Exception:
        ids = {"fleet_host", "workstation", "general_os", "appliance_factory"}

    return aliases, ids


def _top_lines(txt: str, max_lines: int = 40) -> list[str]:
    return [ln.rstrip() for ln in txt.splitlines()[:max_lines]]


def _split_csv(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def _parse(top: list[str]) -> tuple[str, list[str], list[str]]:
    tier = ""
    profiles: list[str] = []
    pillars: list[str] = []

    for ln in top:
        if not tier:
            m = TIER_RE.match(ln)
            if m:
                tier = m.group("val").strip()
                continue
        if not profiles:
            m = PROFILES_RE.match(ln)
            if m:
                profiles = _split_csv(m.group("val").strip())
                continue
        if not pillars:
            m = PILLARS_RE.match(ln)
            if m:
                pillars = [x.strip().lower() for x in _split_csv(m.group("val").strip())]
                continue

    return tier, profiles, pillars


def _tier_letter(tier: str) -> str:
    tier = tier.strip()
    return tier[:1].upper() if tier else ""


def main() -> int:
    problems: list[str] = []

    alias_map, canonical_ids = _load_profile_ids()


    for p in sorted(DOCS.glob("*.md")):
        m = DOC_RE.match(p.name)
        if not m:
            continue
        n = int(m.group("num"))
        if n < 397:
            continue

        top = _top_lines(p.read_text(encoding="utf-8", errors="replace"))
        tier, profiles, pillars = _parse(top)

        missing = []
        if not tier:
            missing.append("**Tier:**")
        if not profiles:
            missing.append("**Profiles:**")
        if not pillars:
            missing.append("**Pillars:**")

        if missing:
            problems.append(f"{p.name}: missing {', '.join(missing)}")
            continue

        t = _tier_letter(tier)
        if t not in ALLOWED_TIERS:
            problems.append(f"{p.name}: invalid Tier value '{tier}' (must start with one of {sorted(ALLOWED_TIERS)})")

        # Accept either legacy A–D letters or canonical profile ids; normalize to canonical ids for duplicate detection.
        normalized: list[str] = []
        bad_profiles: list[str] = []
        for x in profiles:
            if x in alias_map:
                normalized.append(alias_map[x])
            elif x in canonical_ids:
                normalized.append(x)
            else:
                bad_profiles.append(x)

        if bad_profiles:
            allowed = sorted(set(alias_map.keys()) | canonical_ids)
            problems.append(f"{p.name}: invalid Profiles entries {bad_profiles} (allowed: {allowed})")

        # Duplicate after normalization (e.g. 'A' + 'fleet_host') is a smell.
        if len(set(normalized)) != len(normalized):
            problems.append(f"{p.name}: duplicate Profiles after normalization {normalized}")

        bad_pillars = [x for x in pillars if x not in ALLOWED_PILLARS]
        if bad_pillars:
            problems.append(
                f"{p.name}: invalid Pillars entries {bad_pillars} (allowed: {sorted(ALLOWED_PILLARS)})"
            )

    if problems:
        print("Doc metadata check FAILED. Fix the metadata block near the top:\n")
        for pr in problems:
            print(f"- {pr}")
        print("\nTemplate:\n")
        print("  **Tier:** B (Base)\n  **Profiles:** A, B, C, D\n  **Pillars:** reproducibility, isolation, supply-chain, operability\n")
        return 1

    print("Doc metadata check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

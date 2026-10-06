#!/usr/bin/env python3
"""Keep risk flag reason codes stable and discoverable.

Risk flags are small, reviewer-facing reason codes typically emitted in diff summaries
(e.g. `*.diff` -> summary.risk_flags). Without a registry, they drift into ad-hoc strings.

This check enforces:
  1) A canonical registry exists as a typed artifact example:
       spec/examples/risk.flag.registry.json
  2) Registry ids are kebab-case and unique.
  3) Any `risk_flags` values appearing in spec/examples/*.json must use canonical ids.
  4) Docs that mention concrete `risk_flags` ids (heuristic: lines containing `risk_flags`)
     must use canonical ids.

Usage:
  python3 tools/check_risk_flag_registry.py

Exit codes:
  0: ok
  1: registry missing or violations found
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_EXAMPLE = ROOT / "spec" / "examples" / "risk.flag.registry.json"
EXAMPLES_DIR = ROOT / "spec" / "examples"
DOCS_DIR = ROOT / "docs"

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BACKTICK_RE = re.compile(r"`(?P<tok>[a-z0-9_-]+)`")


def _walk_collect_risk_flags(x, out: set[str]) -> None:
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "risk_flags" and isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        out.add(item)
            _walk_collect_risk_flags(v, out)
    elif isinstance(x, list):
        for v in x:
            _walk_collect_risk_flags(v, out)


def _load_registry() -> tuple[set[str], set[str], dict[str, list[str]]]:
    if not REG_EXAMPLE.exists():
        raise FileNotFoundError("Missing spec/examples/risk.flag.registry.json")

    data = json.loads(REG_EXAMPLE.read_text(encoding="utf-8"))
    if data.get("kind") != "risk.flag.registry":
        raise ValueError("risk.flag.registry example has wrong kind")

    ids: set[str] = set()
    aliases: set[str] = set()
    alias_map: dict[str, list[str]] = {}

    for f in data.get("flags", []):
        fid = f.get("id")
        if not isinstance(fid, str):
            continue
        if fid in ids:
            raise ValueError(f"Duplicate risk flag id in registry: {fid}")
        if not KEBAB_RE.match(fid):
            raise ValueError(f"Risk flag id is not kebab-case: {fid}")
        ids.add(fid)
        als = [a for a in (f.get("aliases") or []) if isinstance(a, str)]
        alias_map[fid] = als
        for a in als:
            aliases.add(a)

    overlap = ids.intersection(aliases)
    if overlap:
        raise ValueError(f"Registry ids overlap with aliases: {sorted(overlap)}")

    return ids, aliases, alias_map


def _risk_flags_in_examples() -> set[str]:
    flags: set[str] = set()
    for p in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        _walk_collect_risk_flags(obj, flags)
    return flags


def _risk_flags_in_docs() -> dict[str, set[str]]:
    """Heuristic: scan lines containing 'risk_flags' for backticked tokens."""
    found: dict[str, set[str]] = {}
    for p in sorted(DOCS_DIR.glob("*.md")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        toks: set[str] = set()
        for ln in txt.splitlines():
            if "risk_flags" not in ln:
                continue
            for m in BACKTICK_RE.finditer(ln):
                tok = m.group("tok")
                # Only consider plausible risk flag tokens.
                if tok == "risk_flags":
                    continue
                if "-" in tok or "_" in tok:
                    toks.add(tok)
        if toks:
            found[str(p.relative_to(ROOT))] = toks
    return found


def main() -> int:
    try:
        ids, aliases, _alias_map = _load_registry()
    except Exception as e:
        print("Risk flag registry check FAILED:")
        print(str(e))
        return 1

    # Spec examples must use canonical ids.
    used = _risk_flags_in_examples()
    bad = sorted([f for f in used if f not in ids])

    # Docs must also use canonical ids (heuristic scan).
    docs = _risk_flags_in_docs()
    bad_docs: list[str] = []
    for doc, toks in docs.items():
        for t in sorted(toks):
            if t not in ids:
                bad_docs.append(f"{doc}: {t}")

    # Ensure registry covers canonical usage.
    missing_from_registry = sorted([f for f in used if f not in ids and f not in aliases])

    if bad or bad_docs or missing_from_registry:
        print("Risk flag registry check FAILED.\n")
        if missing_from_registry:
            print("Risk flags used in spec/examples but missing from registry (id or alias):")
            for f in missing_from_registry:
                print("-", f)
            print("")
        if bad:
            print("Spec examples must use canonical registry ids (not aliases):")
            for f in bad:
                print("-", f)
            print("")
        if bad_docs:
            print("Docs mention non-canonical risk flag ids (lines containing 'risk_flags'):")
            for ln in bad_docs:
                print("-", ln)
            print("")
        print("Fix: update risk flags to canonical kebab-case ids and/or extend the registry.")
        return 1

    print("Risk flag registry check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

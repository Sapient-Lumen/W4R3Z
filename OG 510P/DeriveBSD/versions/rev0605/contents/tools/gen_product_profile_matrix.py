#!/usr/bin/env python3
"""Generate docs/412-product-profile-matrix.md from spec/examples/product.profiles.json.

This is intentionally lightweight and deterministic.

Usage:
  python3 tools/gen_product_profile_matrix.py          # print to stdout
  python3 tools/gen_product_profile_matrix.py --write  # update docs file
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "spec" / "examples" / "product.profiles.json"
DST = ROOT / "docs" / "412-product-profile-matrix.md"
ALIASES = ROOT / "spec" / "product.profile_aliases.json"
CHANGELOG = ROOT / "CHANGELOG.md"

ORDER = ["fleet_host", "workstation", "general_os", "appliance_factory"]


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def _top_version() -> str:
    txt = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"^##\s+(\S+)\s*$", txt, re.MULTILINE)
    return m.group(1) if m else "<generated>"

def _load_aliases() -> dict[str, str]:
    # Returns canonical_id -> letter alias (A–D)
    try:
        obj = _read_json(ALIASES)
        amap = obj.get("aliases") or {}
        out = {}
        for letter, cid in amap.items():
            if isinstance(letter, str) and isinstance(cid, str):
                out[cid.strip()] = letter.strip()
        return out
    except Exception:
        return {"fleet_host":"A","workstation":"B","general_os":"C","appliance_factory":"D"}



def _md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def render() -> str:
    obj = _read_json(SRC)
    profiles = obj.get("profiles", {})
    alias_by_id = _load_aliases()

    out: list[str] = []
    out.append("# Product profile matrix (A–D)\n")
    out.append("> Generated from `spec/examples/product.profiles.json`. Do not hand-edit; run `python3 tools/gen_product_profile_matrix.py --write`.\n")
    out.append("**Tier:** A (Core meta-doc)  ")
    out.append("**Profiles:** A, B, C, D  ")
    out.append("**Pillars:** reproducibility, isolation, supply-chain, operability\n")

    out.append("## Defaults snapshot\n")
    out.append("| Profile | Default posture (selected knobs) |\n|---|---|")
    for k in ORDER:
        p = profiles.get(k, {})
        label = p.get("label", k)
        defaults = p.get("defaults") or {}
        items = ", ".join([f"`{kk}={defaults[kk]}`" for kk in sorted(defaults.keys())])
        letter = alias_by_id.get(k, "")
        prof_name = f"{letter} — {label} (`{k}`)" if letter else f"{label} (`{k}`)"
        out.append(f"| {_md_escape(prof_name)} | {items} |")

    out.append("\n## Required invariants\n")
    for k in ORDER:
        p = profiles.get(k, {})
        label = p.get("label", k)
        letter = alias_by_id.get(k, "")
        hdr = f"{letter} — {label} (`{k}`)" if letter else f"{label} (`{k}`)"
        out.append(f"### {hdr}")
        for inv in (p.get("required_invariants") or []):
            out.append(f"- {inv}")
        out.append("")

    out.append("## Forbidden by default\n")
    for k in ORDER:
        p = profiles.get(k, {})
        label = p.get("label", k)
        letter = alias_by_id.get(k, "")
        hdr = f"{letter} — {label} (`{k}`)" if letter else f"{label} (`{k}`)"
        out.append(f"### {hdr}")
        fbd = p.get("forbidden_by_default") or []
        if not fbd:
            out.append("- (none listed)")
        else:
            for x in fbd:
                out.append(f"- {x}")
        out.append("")

    out.append("## Notes\n")
    out.append("- Profiles are compilation targets for defaults and gates; they are not forks.")
    out.append("- Letter aliases A–D are defined in `spec/product.profile_aliases.json` (tools normalize to canonical ids).")
    out.append("- Features should declare **Tier** and applicable **Profiles** in their doc metadata.")
    out.append("")
    out.append(f"Last updated: {_top_version()}")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write to docs/412-product-profile-matrix.md")
    args = ap.parse_args()

    txt = render()
    if args.write:
        DST.write_text(txt, encoding="utf-8")
    else:
        print(txt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

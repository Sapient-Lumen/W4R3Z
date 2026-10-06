#!/usr/bin/env python3
"""Generate a compact, deterministic 'context pack' for humans and LLMs.

This is a memory prosthetic: it surfaces the current archive version, must-read docs,
A–D product profile summary, and top open questions with their risks.

Outputs:
  - Markdown (stdout): docs/420-context-pack.md content
  - JSON (stdout with --json): docs/_generated/context_pack.json content

Write outputs to the repo:
  python3 tools/gen_context_pack.py --write

Notes:
  - deterministic output (no timestamps)
  - repo-relative paths only
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHANGELOG = ROOT / "CHANGELOG.md"
RUNBOOK = ROOT / "docs" / "99-llm-runbook.md"
RISK = ROOT / "docs" / "266-open-questions-and-risk-register.md"
PROFILES_EX = ROOT / "spec" / "examples" / "product.profiles.json"
PROFILE_ALIASES = ROOT / "spec" / "product.profile_aliases.json"

OUT_MD = ROOT / "docs" / "420-context-pack.md"
OUT_JSON = ROOT / "docs" / "_generated" / "context_pack.json"

CHANGELOG_TOP_RE = re.compile(r"^##\s+(\S+)\s*$", re.MULTILINE)
PATH_RE = re.compile(r"`([^`]+)`")
NUM_RE = re.compile(r"^(?P<num>\d+)\)\s*(?P<title>.+)$")
DECIDED_TAG_RE = re.compile(r"\[DECIDED\]", re.IGNORECASE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _top_version() -> str:
    m = CHANGELOG_TOP_RE.search(_read(CHANGELOG))
    if not m:
        return "<unknown>"
    return m.group(1)


def _recent_changes(max_versions: int = 3, max_bullets: int = 4) -> list[dict[str, object]]:
    """Return the newest CHANGELOG entries as compact bullet lists.

    This is a small amnesia-resistor surface: it keeps the context pack self-contained
    without duplicating the full changelog.
    """

    txt = _read(CHANGELOG)
    matches = list(CHANGELOG_TOP_RE.finditer(txt))
    out: list[dict[str, object]] = []

    for i, m in enumerate(matches[:max_versions]):
        v = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(txt)
        block = txt[start:end]

        bullets: list[str] = []
        for line in block.splitlines():
            line = line.rstrip()
            if line.startswith("- "):
                bullets.append(line.removeprefix("- ").strip())
            if len(bullets) >= max_bullets:
                break

        out.append({"version": v, "bullets": bullets})

    return out


def _extract_must_read(runbook_txt: str) -> list[str]:
    out: list[str] = []
    in_list = False
    for line in runbook_txt.splitlines():
        if line.strip() == "## Mandatory refresh before editing":
            in_list = True
            continue
        if in_list:
            if line.startswith("## "):
                break
            if line.strip().startswith("-"):
                # Allow multiple repo paths in one bullet (common in older docs).
                hits = PATH_RE.findall(line)
                if hits:
                    out.extend(hits)
                else:
                    out.append(line.strip("- ").strip())

    # De-dupe while preserving order.
    seen: set[str] = set()
    dedup: list[str] = []
    for x in out:
        if not x:
            continue
        if x in seen:
            continue
        seen.add(x)
        dedup.append(x)
    return dedup


def _profiles_summary() -> list[dict[str, str]]:
    try:
        obj = json.loads(PROFILES_EX.read_text(encoding="utf-8"))
        ps = obj.get("profiles", {})

        # canonical_id -> alias letter (A-D)
        alias_by_id: dict[str, str] = {}
        try:
            aobj = json.loads(PROFILE_ALIASES.read_text(encoding="utf-8"))
            for letter, cid in (aobj.get("aliases") or {}).items():
                if isinstance(letter, str) and isinstance(cid, str):
                    alias_by_id[cid] = letter
        except Exception:
            alias_by_id = {
                "fleet_host": "A",
                "workstation": "B",
                "general_os": "C",
                "appliance_factory": "D",
            }

        rows: list[dict[str, str]] = []
        for k in ["fleet_host", "workstation", "general_os", "appliance_factory"]:
            p = ps.get(k, {})
            defaults = p.get("defaults") or {}
            dstr = ", ".join([f"{kk}={vv}" for kk, vv in sorted(defaults.items())][:6])
            rows.append(
                {
                    "id": str(p.get("id", k)),
                    "alias": alias_by_id.get(k, ""),
                    "label": str(p.get("label", "")),
                    "defaults": dstr,
                }
            )
        return rows
    except Exception:
        return []


def _risk_summaries(max_items: int = 12) -> list[dict[str, str]]:
    """Return compact summaries of *open* questions.

    Conventions:
      - numeric headings in docs/266 are items
      - items tagged with [DECIDED] are historical context and are excluded
    """

    txt = _read(RISK)
    lines = txt.splitlines()
    summaries: list[dict[str, str]] = []

    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        heading = line.removeprefix("## ").strip()
        if DECIDED_TAG_RE.search(heading):
            continue
        if not NUM_RE.match(heading):
            continue

        risk = ""
        for j in range(i + 1, min(i + 220, len(lines))):
            if lines[j].startswith("## "):
                break
            if lines[j].startswith("Risk:"):
                risk = lines[j].strip()
                break

        summaries.append({"topic": heading, "risk": risk})
        if len(summaries) >= max_items:
            break

    return summaries


def render_json(
    archive_version: str,
    recent_changes: list[dict[str, object]],
    must_read: list[str],
    profiles: list[dict[str, str]],
    risks: list[dict[str, str]],
) -> str:
    payload = {
        "version": 1,
        "archive": {"version": archive_version},
        "recent_changes": recent_changes,
        "must_read": must_read,
        "profiles": profiles,
        "top_open_questions": risks,
        "commands": [
            "python3 tools/hygiene.py",
            "python3 tools/gen_context_pack.py --write  # refresh docs/420 + docs/_generated/context_pack.json",
            "python3 tools/gen_product_profile_matrix.py --write  # refresh docs/412",
            "python3 tools/gen_doc_catalog.py --write  # refresh docs/414 + docs/_generated/doc_catalog.json",
            "python3 tools/gen_risk_register_index.py --write  # refresh docs/415 + docs/_generated/risk_register.json",
            "python3 tools/gen_artifact_index.py --write  # refresh docs/418 + docs/_generated/artifact_index.json",
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_markdown(
    archive_version: str,
    recent_changes: list[dict[str, object]],
    must_read: list[str],
    profiles: list[dict[str, str]],
    risks: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Context pack (generated)")
    lines.append("")
    lines.append("**Tier:** A")
    lines.append("**Profiles:** A, B, C, D")
    lines.append("**Pillars:** operability, reproducibility")
    lines.append("")
    lines.append("This page is generated by `tools/gen_context_pack.py`. It is an amnesia resistor:")
    lines.append("a compact refresh of the current archive state, must-read set, product profiles, top risks, and recent changes.")
    lines.append("")
    lines.append(f"Archive version: **{archive_version}**")
    lines.append("")

    lines.append("## Recent changes (from CHANGELOG)")
    for entry in recent_changes:
        v = str(entry.get("version") or "")
        bullets = entry.get("bullets") or []
        lines.append(f"- **{v}**")
        if isinstance(bullets, list):
            for b in bullets:
                b = str(b).strip()
                if b:
                    lines.append(f"  - {b}")
    lines.append("")

    lines.append("## Must-read (refresh before editing)")
    for p in must_read:
        lines.append(f"- `{p}`")
    lines.append("")
    lines.append("## Product profiles (A–D) summary")
    for r in profiles:
        label = (r.get("label") or r.get("id") or "").strip()
        alias = (r.get("alias") or "").strip()
        defaults = (r.get("defaults") or "").strip()
        suffix = f" — {defaults}" if defaults else ""
        prefix = f"{alias}: " if alias else ""
        lines.append(f"- {prefix}{label}{suffix}")
    lines.append("")
    lines.append("## Top open questions (with risk lines)")
    for r in risks:
        topic = (r.get("topic") or "").strip()
        risk = (r.get("risk") or "").strip()
        if not topic:
            continue
        lines.append(f"- {topic} — {risk}" if risk else f"- {topic}")
    lines.append("")
    lines.append("## Commands")
    lines.append("- `python3 tools/hygiene.py`")
    lines.append("- `python3 tools/gen_context_pack.py --write`  # refresh docs/420 + docs/_generated/context_pack.json")
    lines.append("- `python3 tools/gen_product_profile_matrix.py --write`  # refresh docs/412")
    lines.append("- `python3 tools/gen_doc_catalog.py --write`  # refresh docs/414 + docs/_generated/doc_catalog.json")
    lines.append("- `python3 tools/gen_risk_register_index.py --write`  # refresh docs/415 + docs/_generated/risk_register.json")
    lines.append("- `python3 tools/gen_artifact_index.py --write`  # refresh docs/418 + docs/_generated/artifact_index.json")
    lines.append("")
    lines.append("Full machine-readable pack: `docs/_generated/context_pack.json`.")
    lines.append("")
    lines.append(f"Last updated: {archive_version}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--write", action="store_true", help="write outputs to repo")
    args = ap.parse_args()

    version = _top_version()
    recent = _recent_changes()
    must_read = _extract_must_read(_read(RUNBOOK))
    profiles = _profiles_summary()
    risks = _risk_summaries()

    if args.json:
        out = render_json(version, recent, must_read, profiles, risks)
        if args.write:
            OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
            OUT_JSON.write_text(out, encoding="utf-8")
        print(out, end="")
        return 0

    out = render_markdown(version, recent, must_read, profiles, risks)
    if args.write:
        OUT_MD.write_text(out, encoding="utf-8")
        # Keep the machine-readable pack in sync: `--write` refreshes both outputs.
        jout = render_json(version, recent, must_read, profiles, risks)
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(jout, encoding="utf-8")
    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

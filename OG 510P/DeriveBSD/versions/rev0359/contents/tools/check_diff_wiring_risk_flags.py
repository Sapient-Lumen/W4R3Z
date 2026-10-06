#!/usr/bin/env python3
"""Ensure diff wiring docs declare Risk flags (incremental baseline).

Rationale:
- Diff surfaces that emit `risk_flags` are only gateable if humans/tools
  can find the intended reason-code vocabulary quickly.
- We already have a canonical diff surface registry (docs/430) and a
  canonical risk flag registry (risk.flag.registry).
- This check ties them together by requiring each diff wiring doc to
  declare a "## Risk flags" section (or be explicitly allowlisted).

Incremental rollout:
- Existing wiring docs are allowlisted under tools/baselines/ to avoid
  retroactive churn.
- New wiring docs should include a Risk flags section (even if it is "None").

Validation (conservative):
- For non-allowlisted wiring docs, a top-level heading "## Risk flags" must exist.
- If the section contains ids, they must be canonical ids in
  spec/examples/risk.flag.registry.json.

Usage:
  python3 tools/check_diff_wiring_risk_flags.py

Exit codes:
  0: OK
  1: Missing sections or unknown ids
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DIFF_REGISTRY = ROOT / "docs" / "430-diff-surface-registry.md"
BASELINE = ROOT / "tools" / "baselines" / "diff_wiring_missing_risk_flags.txt"
RISK_EXAMPLE = ROOT / "spec" / "examples" / "risk.flag.registry.json"

ROW_RE = re.compile(r"\|\s*`[^`]+`\s*\|[^|]*\|[^|]*\|\s*`(?P<doc>docs/[^`]+)`\s*\|")
H_RISK = re.compile(r"^##\s+Risk flags\b", re.MULTILINE)
H2 = re.compile(r"^##\s+", re.MULTILINE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _load_baseline() -> set[str]:
    if not BASELINE.exists():
        return set()
    out: set[str] = set()
    for ln in _read(BASELINE).splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        out.add(ln)
    return out


def _canonical_risk_ids() -> set[str]:
    data = json.loads(_read(RISK_EXAMPLE))
    flags = data.get("flags", [])
    return {f.get("id") for f in flags if isinstance(f, dict) and f.get("id")}


def _extract_wiring_docs() -> list[str]:
    txt = _read(DIFF_REGISTRY)
    return [m.group("doc") for m in ROW_RE.finditer(txt)]


def _section(txt: str) -> str:
    m = H_RISK.search(txt)
    if not m:
        return ""
    start = m.end()
    m2 = H2.search(txt, start)
    end = m2.start() if m2 else len(txt)
    return txt[start:end]


def _extract_ids(section: str) -> set[str]:
    ids: set[str] = set(re.findall(r"`([a-z0-9-]+)`", section))
    # Also accept bare ids in bullet lists.
    for ln in section.splitlines():
        ln = ln.strip()
        if not ln.startswith("-"):
            continue
        m = re.match(r"^-\s*([a-z0-9-]+)\b", ln)
        if m:
            ids.add(m.group(1))
    return ids


def main() -> int:
    baseline = _load_baseline()
    canonical = _canonical_risk_ids()
    wiring = _extract_wiring_docs()

    problems: list[str] = []

    for rel in wiring:
        p = ROOT / rel
        if not p.exists():
            # existence enforced elsewhere
            continue

        txt = _read(p)
        has = bool(H_RISK.search(txt))
        if not has:
            if rel not in baseline:
                problems.append(f"{rel}: missing '## Risk flags' section (add it or baseline it)")
            continue

        sec = _section(txt)
        if not sec.strip():
            problems.append(f"{rel}: empty Risk flags section (use 'None' or list ids)")
            continue

        # Accept explicit None.
        if re.search(r"\bnone\b", sec, re.IGNORECASE) and not _extract_ids(sec):
            continue

        ids = _extract_ids(sec)
        if not ids:
            problems.append(f"{rel}: Risk flags section has no ids (use 'None' or list canonical ids)")
            continue

        unknown = sorted(i for i in ids if i not in canonical)
        if unknown:
            problems.append(
                f"{rel}: unknown risk flag ids {unknown} (must be canonical ids in risk.flag.registry)"
            )

    if problems:
        print("Diff wiring Risk flags check FAILED.\n")
        for pr in problems:
            print("-", pr)
        print("\nFix:\n- Add a '## Risk flags' section to the wiring doc (list canonical ids or 'None').")
        print("- If retrofitting is out of scope, add the doc path to tools/baselines/diff_wiring_missing_risk_flags.txt")
        return 1

    print("Diff wiring Risk flags check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

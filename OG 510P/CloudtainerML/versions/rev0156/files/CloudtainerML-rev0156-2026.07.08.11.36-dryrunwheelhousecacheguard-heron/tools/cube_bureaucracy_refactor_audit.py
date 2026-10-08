#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0093"))
REVUP = REV.upper()
OUT_AUDIT = ROOT / "artifacts" / "audit"
OUT_AUDIT.mkdir(parents=True, exist_ok=True)

CURRENT_SURFACES = [
    "START_HERE.md",
    "START_HERE_SLIM.md",
    "README.md",
    "PRIORITY-LIST.md",
    "NEXT-TURN-PROMPT.md",
    "MISSION-KERNEL.md",
    "EVIDENCE-STATUS.json",
    "REENTRY-CONTRACT.json",
]


def file_info(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {"path": rel, "exists": False}
    text = p.read_text(encoding="utf-8", errors="replace") if p.suffix in {".md", ".json", ".html"} else ""
    return {
        "path": rel,
        "exists": True,
        "bytes": p.stat().st_size,
        "mentions_current_rev_near_top": REV in text[:4000],
        "first_heading": next((line.strip() for line in text.splitlines() if line.strip().startswith("#")), ""),
    }


def build_audit() -> dict[str, Any]:
    capture_scripts = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "artifacts" / "capture-kit").glob("REV*_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh"))
    mission_audits = sorted(p.name for p in ROOT.glob("MISSION-AUDIT-REV*.md"))
    current_artifacts = list(META.get("current_revision_artifacts", []))
    surface_infos = [file_info(rel) for rel in CURRENT_SURFACES]
    stale_current_surfaces = [s["path"] for s in surface_infos if s.get("exists") and not s.get("mentions_current_rev_near_top")]
    debt = []
    if len(capture_scripts) > 4:
        debt.append("historical_capture_kit_script_accumulation")
    if len(mission_audits) > 8:
        debt.append("mission_audit_accumulation")
    if stale_current_surfaces:
        debt.append("top_level_surface_not_current_near_top")
    return {
        "revision": REV,
        "revision_number": int(str(REV).replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_debt" if debt else "pass",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Refactor audit of cube surfaces and trace-lane launch clutter. It distinguishes current entrypoints from retained historical provenance.",
        "surface_infos": surface_infos,
        "current_revision_artifact_count": len(current_artifacts),
        "current_revision_artifacts": current_artifacts,
        "capture_kit_run_script_count": len(capture_scripts),
        "historical_capture_kit_run_scripts": capture_scripts,
        "current_capture_entrypoint": f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
        "mission_audit_count": len(mission_audits),
        "mission_audits_retained": mission_audits[-20:],
        "debt": debt,
        "actions_taken_rev0093": [
            "rewrote START_HERE.md and START_HERE_SLIM.md around the current launch script",
            "rewrote PRIORITY-LIST.md into three execution priorities and one anti-priority",
            "rewrote NEXT-TURN-PROMPT.md to prevent registry-only continuation",
            "added a single current one-shot public trace capture entrypoint",
            "left historical scripts and mission audits intact as immutable provenance rather than deleting them",
        ],
        "next_refactor_only_if_needed": [
            "content-address historical capture-kit revisions into an archive index only after the real trace path has run or been stopped",
            "collapse top-level JSON status mirrors after package readers no longer depend on them",
        ],
    }


def write_md(audit: dict[str, Any], path: Path) -> None:
    debt = "\n".join(f"- `{d}`" for d in audit.get("debt", [])) or "- none"
    actions = "\n".join(f"- {a}" for a in audit.get("actions_taken_rev0093", []))
    txt = f"""# Cube bureaucracy/refactor audit — {REVUP}

Status: `{audit.get('status')}`  
Promotion allowed: `false`

## What was audited

- Top-level current surfaces: `{len(audit.get('surface_infos', []))}`
- Historical capture-kit run scripts retained: `{audit.get('capture_kit_run_script_count')}`
- Mission audit files retained: `{audit.get('mission_audit_count')}`
- Current capture entrypoint: `{audit.get('current_capture_entrypoint')}`

## Debt still present

{debt}

## Actions taken in rev0093

{actions}

## Interpretation

The cube still contains historical bulk, but the live working surface now points at execution instead of asking the next turn to re-read a registry. This audit intentionally avoids deletion because provenance is valuable and the decisive trace has not yet run.
"""
    path.write_text(txt, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT_AUDIT / f"{REVUP}_CUBE_BUREAUCRACY_REFACTOR_AUDIT.json")
    parser.add_argument("--md-out", type=Path, default=OUT_AUDIT / f"{REVUP}_CUBE_BUREAUCRACY_REFACTOR_AUDIT.md")
    args = parser.parse_args()
    audit = build_audit()
    args.out.write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    write_md(audit, args.md_out)
    print(json.dumps({"status": audit["status"], "debt": audit["debt"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Traceability/audit report for source -> idea -> cell -> probe links.

This is a cube-maintenance refactor. It does not judge scientific quality; it
checks whether the scouting ledgers are connected enough to re-enter later.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "audit"


def revision() -> str:
    try:
        return json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0011")
    except Exception:
        return "rev0011"


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    src = load("RESEARCH-SOURCE-REGISTRY.json")["sources"]
    ideas = load("IDEA-LEDGER.json")["ideas"]
    cells = load("EXPERIMENT-MATRIX.json")["cells"]
    source_ids = {s["id"] for s in src}
    idea_ids = {i["id"] for i in ideas}
    idea_by_source: Dict[str, List[str]] = {s["id"]: [] for s in src}
    cell_by_idea: Dict[str, List[str]] = {i["id"]: [] for i in ideas}
    cell_by_source: Dict[str, List[str]] = {s["id"]: [] for s in src}
    for idea in ideas:
        for sid in idea.get("source_ids", []):
            idea_by_source.setdefault(sid, []).append(idea["id"])
    for cell in cells:
        iid = cell.get("idea_id", "")
        cell_by_idea.setdefault(iid, []).append(cell["cell_id"])
        for sid in cell.get("source_ids", []):
            cell_by_source.setdefault(sid, []).append(cell["cell_id"])

    probe_files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "experiments").glob("*/*.py"))
    probe_outputs = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "artifacts" / "probe-results").glob("REV*_*.json"))
    note_paths = {p.stem: str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "02-experiment-cells").glob("cell-*.md")}

    source_records = []
    for s in src:
        sid = s["id"]
        source_records.append({
            "source_id": sid,
            "priority": s.get("priority", ""),
            "family": s.get("family", ""),
            "arxiv": s.get("arxiv", ""),
            "title": s.get("title", ""),
            "idea_count": len(idea_by_source.get(sid, [])),
            "cell_count": len(cell_by_source.get(sid, [])),
        })
    idea_records = []
    for i in ideas:
        iid = i["id"]
        idea_records.append({
            "idea_id": iid,
            "priority": i.get("priority", ""),
            "name": i.get("name", ""),
            "source_count": len([sid for sid in i.get("source_ids", []) if sid in source_ids]),
            "cell_count": len(cell_by_idea.get(iid, [])),
            "status": i.get("status", ""),
        })
    cell_records = []
    for c in cells:
        cid = c["cell_id"]
        num = cid.split("-")[-1].lower()
        note_hit = any(p.name.lower().startswith(f"cell-{num}") for p in (ROOT / "docs" / "02-experiment-cells").glob("cell-*.md"))
        cell_records.append({
            "cell_id": cid,
            "priority": c.get("priority", ""),
            "name": c.get("name", ""),
            "idea_id": c.get("idea_id", ""),
            "idea_exists": c.get("idea_id", "") in idea_ids,
            "source_count": len([sid for sid in c.get("source_ids", []) if sid in source_ids]),
            "has_note": bool(note_hit),
            "status": c.get("status", ""),
        })
    orphan_p0_sources = [r for r in source_records if r["priority"] == "P0" and (r["idea_count"] == 0 or r["cell_count"] == 0)]
    orphan_p0_ideas = [r for r in idea_records if r["priority"] == "P0" and r["cell_count"] == 0]
    note_missing = [r for r in cell_records if not r["has_note"]]
    return {
        "project": "CloudtainerML",
        "revision": revision(),
        "report": "traceability_report",
        "summary": {
            "source_count": len(src),
            "idea_count": len(ideas),
            "cell_count": len(cells),
            "probe_file_count": len(probe_files),
            "probe_output_count": len(probe_outputs),
            "orphan_p0_source_count": len(orphan_p0_sources),
            "orphan_p0_idea_count": len(orphan_p0_ideas),
            "cell_note_missing_count": len(note_missing),
        },
        "orphan_p0_sources": orphan_p0_sources[:50],
        "orphan_p0_ideas": orphan_p0_ideas[:50],
        "cell_note_missing": note_missing[:50],
        "source_records": source_records,
        "idea_records": idea_records,
        "cell_records": cell_records,
    }


def write(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = OUT / f"{revision().upper()}_TRACEABILITY_REPORT"
    prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        rows = payload["cell_records"]
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    md = [
        f"# Traceability report — {payload['revision']}",
        "",
        "## Summary",
        "",
    ]
    for k, v in payload["summary"].items():
        md.append(f"- {k}: {v}")
    md.extend(["", "## P0 gaps", ""])
    md.append(f"- P0 sources missing idea/cell links: {payload['summary']['orphan_p0_source_count']}")
    md.append(f"- P0 ideas missing cells: {payload['summary']['orphan_p0_idea_count']}")
    md.append(f"- cells missing cell notes: {payload['summary']['cell_note_missing_count']}")
    md.extend(["", "## Refactor rule", "", "Every P0 source should bind to at least one idea and cell; every runnable probe should have a cell note and primary metric output."])
    prefix.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    write(payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

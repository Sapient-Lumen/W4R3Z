#!/usr/bin/env python3
"""Build a cross-probe metric index.

CloudtainerML probes intentionally start heterogeneous. This tool is the next
refactor step after the dashboard: it extracts declared primary_metric blocks
where present, falls back to known summary conventions, and writes a small index
that says which probes are ready for plotted comparison and which still need a
schema patch.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "artifacts" / "probe-results"
DASH_DIR = ROOT / "artifacts" / "dashboard"


def revision(root: Path = ROOT) -> str:
    try:
        return json.loads((root / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0008")
    except Exception:
        return "rev0008"


def load(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def rows_count(obj: dict[str, Any]) -> int:
    rows = obj.get("rows")
    if isinstance(rows, list):
        return len(rows)
    if isinstance(rows, int):
        return rows
    summary = obj.get("summary")
    if isinstance(summary, dict) and isinstance(summary.get("row_count"), int):
        return int(summary["row_count"])
    return 0


def detect_primary(obj: dict[str, Any]) -> tuple[str, str, str, str]:
    summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
    pm = summary.get("primary_metric") if isinstance(summary, dict) else None
    if isinstance(pm, dict):
        return str(pm.get("name", "declared")), str(pm.get("direction", "unknown")), "declared", str(pm.get("winner_field", ""))
    for key in ["winners", "winners_excluding_full_attention", "winners_excluding_full_cache", "winners_excluding_oracle", "practical_winners_excluding_pre_sft"]:
        if isinstance(summary.get(key), dict):
            return key, "higher_is_better_proxy", "winner-map", key
    for key in ["best_policy_by_regime_budget", "best_compressed_policy_by_regime_budget"]:
        if isinstance(summary.get(key), dict):
            return key, "lower_error_proxy", "best-policy-map", key
    return "missing", "unknown", "needs_schema_patch", ""


def winner_compact(obj: dict[str, Any]) -> str:
    summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
    for key in ["winners", "winners_excluding_full_attention", "winners_excluding_full_cache", "winners_excluding_oracle", "practical_winners_excluding_pre_sft"]:
        val = summary.get(key)
        if isinstance(val, dict):
            parts = [f"{k}:{v}" for k, v in list(val.items())[:5]]
            more = "…" if len(val) > 5 else ""
            return "; ".join(parts) + more
    best = summary.get("best_policy_by_regime_budget")
    if isinstance(best, dict):
        counts: Dict[str, int] = {}
        for item in best.values():
            if isinstance(item, dict) and isinstance(item.get("best_policy"), str):
                counts[item["best_policy"]] = counts.get(item["best_policy"], 0) + 1
        return "; ".join(f"{k}:{v}" for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:5])
    return ""


def build(root: Path) -> dict[str, Any]:
    records: List[dict[str, Any]] = []
    for path in sorted((root / "artifacts" / "probe-results").glob("REV*_*.json")):
        if any(skip in path.name for skip in ["PROBE_SUITE_DASHBOARD", "METRIC_INDEX"]):
            continue
        obj = load(path)
        if not obj:
            records.append({"artifact": str(path.relative_to(root)), "probe": path.stem, "parse_status": "fail"})
            continue
        metric, direction, status, winner_field = detect_primary(obj)
        records.append({
            "artifact": str(path.relative_to(root)),
            "probe": str(obj.get("probe", path.stem)),
            "rows": rows_count(obj),
            "parse_status": "ok",
            "metric_status": status,
            "primary_metric": metric,
            "direction": direction,
            "winner_field": winner_field,
            "winner_compact": winner_compact(obj),
            "has_config": isinstance(obj.get("config"), dict),
            "has_summary": isinstance(obj.get("summary"), dict),
            "has_rows": isinstance(obj.get("rows"), list),
        })
    summary = {
        "artifact_count": len(records),
        "ready_metric_count": sum(1 for r in records if r.get("metric_status") in {"declared", "winner-map", "best-policy-map"}),
        "needs_schema_patch_count": sum(1 for r in records if r.get("metric_status") == "needs_schema_patch"),
        "row_total": sum(int(r.get("rows") or 0) for r in records),
    }
    return {"project": "CloudtainerML", "revision": revision(root), "probe": "probe_metric_index", "summary": summary, "records": records}


def write_outputs(root: Path, payload: dict[str, Any]) -> None:
    out_prefix = root / "artifacts" / "dashboard" / f"{revision(root).upper()}_PROBE_METRIC_INDEX"
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    (out_prefix.with_suffix(".json")).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    records = payload["records"]
    if records:
        with out_prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
            fields = list(records[0].keys())
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader(); writer.writerows(records)
    md = [f"# Probe metric index — {payload['revision']}", "", f"Artifacts: **{payload['summary']['artifact_count']}**", f"Metric-ready: **{payload['summary']['ready_metric_count']}**", f"Needs schema patch: **{payload['summary']['needs_schema_patch_count']}**", "", "| probe | rows | status | metric | winners / compact result |", "|---|---:|---|---|---|"]
    for r in records:
        md.append(f"| {r.get('probe')} | {r.get('rows','')} | {r.get('metric_status','')} | {r.get('primary_metric','')} | {str(r.get('winner_compact','')).replace('|','/')} |")
    md.extend(["", "## Refactor rule", "", "New probes should emit `summary.primary_metric`, a winner map where applicable, and row-level fields with stable metric names. Older probes can be patched gradually rather than rewritten."])
    out_prefix.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    rows = []
    for r in records:
        rows.append("<tr>" + "".join([
            f"<td>{html.escape(str(r.get('probe','')))}</td>",
            f"<td>{html.escape(str(r.get('rows','')))}</td>",
            f"<td>{html.escape(str(r.get('metric_status','')))}</td>",
            f"<td>{html.escape(str(r.get('primary_metric','')))}</td>",
            f"<td>{html.escape(str(r.get('winner_compact','')))}</td>",
        ]) + "</tr>")
    html_doc = f"""<!doctype html><html><head><meta charset='utf-8'><title>CloudtainerML {payload['revision']} metric index</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto;line-height:1.4}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:.35rem;vertical-align:top}}</style></head><body><h1>CloudtainerML {payload['revision']} metric index</h1><p>Metric-ready: <b>{payload['summary']['ready_metric_count']}</b> / {payload['summary']['artifact_count']}</p><table><thead><tr><th>Probe</th><th>Rows</th><th>Status</th><th>Primary metric</th><th>Compact result</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""
    out_prefix.with_suffix(".html").write_text(html_doc, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    root = args.root.resolve()
    payload = build(root)
    write_outputs(root, payload)
    print(json.dumps(payload["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

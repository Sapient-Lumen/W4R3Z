#!/usr/bin/env python3
"""Emit lightweight graph specs for probe families.

The cube has many heterogeneous probe outputs. This tool produces a chart-plan
index rather than plotting every artifact: what metric, grouping fields, and
chart type should be used first for each probe. It is meant to reduce dashboard
sprawl and guide future plotting work.
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "artifacts" / "probe-results"
OUT = ROOT / "artifacts" / "dashboard"

FAMILY_RULES = [
    ("quantization", ["KV_WIND", "TOKEN_PRECISION", "KVarN", "KVCAT"]),
    ("retention", ["REGION", "DORMANT", "VALUE_OUTLIER", "MOMENT", "INTENT", "OBSERVABILITY"]),
    ("routing", ["FORECAST", "SHARED_ROUTING", "PCAF", "SPARDA", "EVIDENCE_ALIGNED", "BRANCH_CACHE", "ENTROPY_GUIDED", "REASONING_CACHE", "QUERY_MOVE"]),
    ("agentic-search", ["AGENTIC_DFS", "DFS_SEARCH"]),
    ("agentic-budget", ["TRACE_PREFIX", "ROLLOUT"]),
    ("streaming-coreset", ["EXPRESS_STREAMING", "CORESET"]),
    ("meta-optimization", ["CENTAUR_HPO", "HPO"]),
    ("decoding-acceleration", ["CLP_MULTITOKEN", "K_FORCING"]),
    ("compaction", ["STILL", "LATENT_CONTEXT", "TENSOR_CACHE", "BLURRY", "FADEMEM"]),
    ("projection", ["QKV", "QK_RESTORE", "DEPTH_VALUE", "ENTMAX", "BANK_OF_VALUES", "HIST_WINDOW", "LRKV"]),
    ("state-memory", ["SMT", "DYNAMIC_STATE", "SPECTRAL", "PARAMETRIC", "RESIDUAL_KV", "RESIDUAL_STREAM"]),
    ("latent-compute", ["LATENT_REASONING", "REASONING_WAVE", "ART_RUNTIME"]),
]

GROUP_HINTS = {
    "quantization": ["scenario", "budget", "policy"],
    "retention": ["regime", "budget", "policy"],
    "routing": ["regime", "budget", "policy"],
    "compaction": ["regime", "slots", "method"],
    "projection": ["regime", "variant", "method"],
    "state-memory": ["regime", "buffer", "policy"],
    "latent-compute": ["regime", "budget", "policy"],
    "agentic-search": ["regime", "depth", "policy"],
    "agentic-budget": ["regime", "budget", "policy"],
    "streaming-coreset": ["regime", "budget", "policy"],
    "meta-optimization": ["landscape", "method"],
    "decoding-acceleration": ["regime", "policy"],
    "misc": ["regime", "policy"],
}


def revision() -> str:
    try:
        return json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0010")
    except Exception:
        return "rev0010"


def family_for(name: str) -> str:
    u = name.upper()
    for fam, parts in FAMILY_RULES:
        if any(part in u for part in parts):
            return fam
    return "misc"


def load(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def infer_fields(obj: dict[str, Any]) -> list[str]:
    rows = obj.get("rows")
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        return sorted(rows[0].keys())
    return []


def build() -> dict[str, Any]:
    records: List[dict[str, Any]] = []
    for path in sorted(PROBE_DIR.glob("REV*_*.json")):
        if any(skip in path.name for skip in ["DASHBOARD", "METRIC_INDEX", "CACHE_PROBE_REPORT"]):
            continue
        obj = load(path)
        if not obj:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        pm = summary.get("primary_metric") if isinstance(summary, dict) else None
        fields = infer_fields(obj)
        fam = family_for(path.name)
        hints = [h for h in GROUP_HINTS.get(fam, []) if h in fields]
        metric = pm.get("name") if isinstance(pm, dict) else "undeclared"
        direction = pm.get("direction") if isinstance(pm, dict) else "unknown"
        chart = "line_or_heatmap" if any(x in fields for x in ["budget", "slots", "steps", "retention"]) else "bar_by_method"
        records.append({
            "artifact": str(path.relative_to(ROOT)),
            "probe": obj.get("probe", path.stem),
            "family": fam,
            "primary_metric": metric,
            "direction": direction,
            "suggested_chart": chart,
            "facet_fields": ",".join(hints[:3]),
            "row_fields_seen": len(fields),
            "schema_ready": isinstance(pm, dict),
        })
    by_family: Dict[str, int] = {}
    for r in records:
        by_family[r["family"]] = by_family.get(r["family"], 0) + 1
    return {"project": "CloudtainerML", "revision": revision(), "tool": "probe_graph_specs", "summary": {"artifact_count": len(records), "family_counts": by_family, "schema_ready": sum(1 for r in records if r["schema_ready"])}, "records": records}


def write(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = OUT / f"{revision().upper()}_PROBE_GRAPH_SPECS"
    prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(payload["records"][0].keys()) if payload["records"] else ["artifact"])
        w.writeheader(); w.writerows(payload["records"])
    md = [f"# Probe graph specs — {revision()}", "", "This is a plotting plan, not a leaderboard.", "", "| family | probe | metric | chart | facets |", "|---|---|---|---|---|"]
    for r in payload["records"]:
        md.append(f"| {r['family']} | {r['probe']} | {r['primary_metric']} | {r['suggested_chart']} | {r['facet_fields']} |")
    prefix.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    table = "".join("<tr>" + "".join(f"<td>{html.escape(str(r[k]))}</td>" for k in ["family", "probe", "primary_metric", "suggested_chart", "facet_fields"]) + "</tr>" for r in payload["records"])
    doc = f"<!doctype html><html><head><meta charset='utf-8'><title>CloudtainerML {revision()} graph specs</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:.35rem}}</style></head><body><h1>Probe graph specs — {revision()}</h1><p>Schema-ready: <b>{payload['summary']['schema_ready']}</b> / {payload['summary']['artifact_count']}</p><table><thead><tr><th>Family</th><th>Probe</th><th>Metric</th><th>Chart</th><th>Facets</th></tr></thead><tbody>{table}</tbody></table></body></html>"
    prefix.with_suffix(".html").write_text(doc, encoding="utf-8")


def main() -> int:
    payload = build(); write(payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

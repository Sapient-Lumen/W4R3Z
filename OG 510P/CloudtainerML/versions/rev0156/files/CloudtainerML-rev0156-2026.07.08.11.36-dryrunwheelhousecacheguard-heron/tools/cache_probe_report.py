#!/usr/bin/env python3
"""Build a cache/memory probe comparison report.

This refactor layer does not force all probes into one numeric metric. It groups
probe artifacts by family, extracts primary-metric declarations where available,
and produces a readable "what is winning where" report plus a schema TODO list.
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "dashboard"
PROBE_DIR = ROOT / "artifacts" / "probe-results"

FAMILY_RULES = [
    ("quantization", ["KV_WIND", "TOKEN_PRECISION", "KVAR", "QUANT", "KVCAT"]),
    ("retention/eviction", ["REGION_WIPEOUT", "DORMANT", "VALUE_OUTLIER", "MOMENT", "INTENT", "OBSERVABILITY", "KVCAT"]),
    ("routing/indexing", ["SHARED_ROUTING", "FORECAST", "PCAF", "REASONING_WAVE", "EVIDENCE_ALIGNED", "BRANCH_CACHE", "ENTROPY_GUIDED", "REASONING_CACHE", "QUERY_MOVE", "STOCHASTIC_SPARSE"]),
    ("agentic search", ["AGENTIC_DFS", "DFS_SEARCH"]),
    ("agentic budget", ["TRACE_PREFIX", "ROLLOUT"]),
    ("streaming coreset", ["EXPRESS_STREAMING", "CORESET"]),
    ("meta optimization", ["CENTAUR_HPO", "HPO"]),
    ("decoding acceleration", ["CLP_MULTITOKEN", "K_FORCING"]),
    ("bounded memory", ["TENSOR_CACHE", "FADEMEM", "BLURRY", "DYNAMIC_STATE", "SPECTRAL", "LATENT_CONTEXT", "STILL_COMPACTOR", "SMT_TRANSITION", "PARAMETRIC_KV", "RESIDUAL_KV", "RESIDUAL_STREAM"]),
    ("attention architecture", ["QKV", "QK_RESTORE", "BANK_OF_VALUES", "DEPTH_VALUE", "HIST_WINDOW", "ENTMAX", "LRKV"]),
    ("runtime/depth", ["ART_RUNTIME", "LATENT_REASONING"]),
]


def revision() -> str:
    try:
        return json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0009")
    except Exception:
        return "rev0009"


def family_for(name: str) -> str:
    up = name.upper()
    for fam, terms in FAMILY_RULES:
        if any(t in up for t in terms):
            return fam
    return "other"


def load(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def compact_winners(summary: dict[str, Any]) -> str:
    for key in ["winners_excluding_oracle", "winners_excluding_full_attention", "winners_excluding_full_cache", "practical_winners_excluding_pre_sft", "winners"]:
        val = summary.get(key)
        if isinstance(val, dict):
            counts: Dict[str, int] = {}
            for w in val.values():
                if isinstance(w, dict):
                    w = w.get("best_policy") or w.get("winner") or str(w)
                counts[str(w)] = counts.get(str(w), 0) + 1
            return "; ".join(f"{k}:{v}" for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:6])
    for key in ["winner_counts_excluding_oracle", "winner_counts"]:
        val = summary.get(key)
        if isinstance(val, dict):
            return "; ".join(f"{k}:{v}" for k, v in sorted(val.items(), key=lambda x: (-x[1], x[0]))[:6])
    return ""


def build() -> dict[str, Any]:
    records: List[dict[str, Any]] = []
    for path in sorted(PROBE_DIR.glob("REV*_*.json")):
        if "PROBE_SUITE_DASHBOARD" in path.name:
            continue
        obj = load(path)
        if not obj:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        pm = summary.get("primary_metric") if isinstance(summary, dict) else None
        metric = pm.get("name") if isinstance(pm, dict) else "undeclared"
        direction = pm.get("direction") if isinstance(pm, dict) else "unknown"
        row_count = len(obj.get("rows", [])) if isinstance(obj.get("rows"), list) else summary.get("row_count", 0)
        rec = {
            "artifact": str(path.relative_to(ROOT)),
            "probe": str(obj.get("probe", path.stem)),
            "family": family_for(path.name),
            "revision_source": path.name.split("_")[0],
            "rows": int(row_count or 0),
            "metric": str(metric),
            "direction": str(direction),
            "winner_compact": compact_winners(summary),
            "schema_ready": isinstance(pm, dict),
        }
        records.append(rec)
    fam_counts: Dict[str, int] = {}
    schema_ready_by_family: Dict[str, int] = {}
    for r in records:
        fam_counts[r["family"]] = fam_counts.get(r["family"], 0) + 1
        if r["schema_ready"]:
            schema_ready_by_family[r["family"]] = schema_ready_by_family.get(r["family"], 0) + 1
    return {
        "project": "CloudtainerML",
        "revision": revision(),
        "report": "cache_probe_report",
        "summary": {
            "artifact_count": len(records),
            "family_counts": fam_counts,
            "schema_ready_count": sum(1 for r in records if r["schema_ready"]),
            "schema_ready_by_family": schema_ready_by_family,
        },
        "records": records,
    }


def write(payload: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prefix = OUT / f"{revision().upper()}_CACHE_PROBE_REPORT"
    prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    records = payload["records"]
    if records:
        with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            w.writeheader(); w.writerows(records)
    md = [f"# Cache/memory probe report — {payload['revision']}", "", f"Artifacts: **{payload['summary']['artifact_count']}**", f"Schema-ready: **{payload['summary']['schema_ready_count']}**", "", "## Family counts", ""]
    for fam, count in sorted(payload["summary"]["family_counts"].items()):
        ready = payload["summary"]["schema_ready_by_family"].get(fam, 0)
        md.append(f"- **{fam}**: {count} artifacts; {ready} schema-ready")
    md.extend(["", "## Compact winners", "", "| family | probe | rows | metric | compact result |", "|---|---|---:|---|---|"])
    for r in records:
        md.append(f"| {r['family']} | {r['probe']} | {r['rows']} | {r['metric']} | {str(r['winner_compact']).replace('|','/')} |")
    md.extend(["", "## Audit note", "", "This report is deliberately a comparison surface, not a unified leaderboard. The next refactor should add per-family comparable metrics and graph specs."])
    prefix.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    rows = "".join("<tr>" + "".join(f"<td>{html.escape(str(r[k]))}</td>" for k in ["family","probe","rows","metric","winner_compact"]) + "</tr>" for r in records)
    doc = f"""<!doctype html><html><head><meta charset='utf-8'><title>CloudtainerML {payload['revision']} cache report</title><style>body{{font-family:system-ui,sans-serif;max-width:1200px;margin:2rem auto;line-height:1.4}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:.35rem;vertical-align:top}}</style></head><body><h1>CloudtainerML {payload['revision']} cache/memory probe report</h1><p>Artifacts: <b>{payload['summary']['artifact_count']}</b>; schema-ready: <b>{payload['summary']['schema_ready_count']}</b>.</p><table><thead><tr><th>Family</th><th>Probe</th><th>Rows</th><th>Metric</th><th>Compact result</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    prefix.with_suffix(".html").write_text(doc, encoding="utf-8")


def main() -> int:
    payload = build()
    write(payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

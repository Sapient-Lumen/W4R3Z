#!/usr/bin/env python3
"""Build a lightweight dashboard over CloudtainerML probe outputs.

The probes do not share a perfect metric schema yet. This tool is an audit/refactor
bridge: it scans artifact JSON files, extracts common metadata, records schema
coverage, and creates a human-readable table of the strongest claim/failure axis
for each probe where we know how to read it.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "probe-results"

def revision(root: Path = ROOT) -> str:
    try:
        return json.loads((root / 'CUBE-META.json').read_text(encoding='utf-8')).get('revision', 'rev0007')
    except Exception:
        return 'rev0007'

REVISION = revision()
REVUP = REVISION.upper()


def load_json(path: Path) -> Dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def mean_rows(rows: Iterable[Dict[str, Any]], field: str) -> float | None:
    vals = []
    for r in rows:
        v = r.get(field)
        if isinstance(v, (int, float)):
            vals.append(float(v))
    return sum(vals) / len(vals) if vals else None


def extract_known_highlight(obj: Dict[str, Any]) -> Tuple[str, float | None, str]:
    probe = str(obj.get("probe", "unknown"))
    summary = obj.get("summary", {}) if isinstance(obj.get("summary"), dict) else {}
    rows = obj.get("rows", []) if isinstance(obj.get("rows"), list) else []


    # Known schemas from rev0006 probes.
    if probe == "bank_of_values" and isinstance(obj.get("methods"), dict):
        return f"identity:{obj.get('identity_winner')} / context:{obj.get('context_winner')}", None, "declared winners"

    if probe == "attention_runtime_termination" and isinstance(obj.get("scenarios"), dict):
        candidates = []
        for scenario, methods in obj["scenarios"].items():
            if not isinstance(methods, dict):
                continue
            for method, m in methods.items():
                if isinstance(m, dict):
                    cos = m.get("cosine_mean")
                    frac = m.get("read_fraction_mean")
                    if isinstance(cos, (int, float)) and isinstance(frac, (int, float)) and cos >= 0.99:
                        candidates.append((float(frac), f"{scenario}/{method}"))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1], candidates[0][0], "lowest read fraction with cosine>=0.99"

    if probe == "branch_cache_sharing":
        by = summary.get("by_scenario_policy")
        if isinstance(by, dict):
            candidates = []
            for name, m in by.items():
                if not isinstance(m, dict):
                    continue
                err = m.get("mean_unacceptable_error_rate")
                frac = m.get("mean_cache_compute_fraction")
                speed = m.get("mean_implied_speedup")
                if isinstance(err, (int, float)) and isinstance(frac, (int, float)) and err <= 0.05:
                    candidates.append((float(frac), str(name), float(speed) if isinstance(speed, (int, float)) else None))
            if candidates:
                candidates.sort(key=lambda x: x[0])
                return candidates[0][1], candidates[0][0], "lowest cache fraction with unacceptable_error<=0.05"

    # Generic by_* summary: choose lowest mean output rel error if present.
    for key in ["best_compressed_policy_by_regime_budget", "by_task_method", "by_scenario_policy", "by_regime_policy", "by_regime_variant", "by_policy", "by_method", "by_regime_method"]:
        by = summary.get(key)
        if isinstance(by, dict):
            candidates = []
            for name, metrics in by.items():
                if isinstance(metrics, dict):
                    display_name = str(name)
                    if isinstance(metrics.get("best_policy"), str):
                        display_name = f"{name}->{metrics['best_policy']}"
                    for metric_name in ["mean_output_rel_error", "mean_output_l2_error_vs_full", "mean_rel_error", "mean_mse", "mean_error", "output_rel_error", "mean_unacceptable_error_rate"]:
                        if isinstance(metrics.get(metric_name), (int, float)):
                            name_s = display_name
                            if name_s.endswith("/full_cache") or name_s == "full_cache" or "teacher_full" in name_s or name_s.endswith("/full_attention") or name_s == "full_attention":
                                continue
                            candidates.append((float(metrics[metric_name]), name_s, metric_name))
                            break
            if candidates:
                candidates.sort(key=lambda x: x[0])
                return candidates[0][1], candidates[0][0], f"best by {candidates[0][2]}"

    # If best_policy_by_regime_budget exists, report the most frequent winner.
    best = summary.get("best_policy_by_regime_budget")
    if isinstance(best, dict):
        counts: Dict[str, int] = {}
        for item in best.values():
            if isinstance(item, dict) and isinstance(item.get("best_policy"), str):
                counts[item["best_policy"]] = counts.get(item["best_policy"], 0) + 1
        if counts:
            winner = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0]
            return winner[0], float(winner[1]), "most frequent best policy across regimes/budgets"

    # Row-only fallback: group by obvious candidate names.
    for group_field in ["policy", "variant", "method", "cache_policy"]:
        if rows and isinstance(rows[0], dict) and group_field in rows[0]:
            groups: Dict[str, List[Dict[str, Any]]] = {}
            for r in rows:
                if isinstance(r, dict):
                    groups.setdefault(str(r.get(group_field)), []).append(r)
            metric = "output_rel_error" if any("output_rel_error" in r for r in rows if isinstance(r, dict)) else "output_mse"
            candidates = []
            for name, rs in groups.items():
                m = mean_rows(rs, metric)
                if m is not None:
                    candidates.append((m, name))
            if candidates:
                candidates.sort(key=lambda x: x[0])
                return candidates[0][1], candidates[0][0], f"fallback row mean {metric}"

    return "unread", None, "no shared metric extracted"


def build_dashboard(root: Path, out_prefix: Path) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for path in sorted((root / "artifacts" / "probe-results").glob("REV*_*.json")):
        if "PROBE_SUITE_DASHBOARD" in path.name:
            continue
        obj = load_json(path)
        if not obj:
            continue
        raw_rows = obj.get("rows", [])
        rows = raw_rows if isinstance(raw_rows, list) else []
        row_count = len(rows) if rows else (raw_rows if isinstance(raw_rows, int) else "")
        summary = obj.get("summary", {}) if isinstance(obj.get("summary"), dict) else {}
        highlight_name, highlight_value, highlight_note = extract_known_highlight(obj)
        records.append({
            "artifact": str(path.relative_to(root)),
            "probe": obj.get("probe", path.stem),
            "row_count": row_count if row_count != "" else summary.get("row_count", ""),
            "has_config": isinstance(obj.get("config"), dict),
            "has_summary": isinstance(obj.get("summary"), dict),
            "has_rows": bool(rows),
            "highlight_name": highlight_name,
            "highlight_value": highlight_value if highlight_value is not None else "",
            "highlight_note": highlight_note,
        })
    result = {
        "probe": "probe_suite_dashboard",
        "purpose": "Audit/refactor surface over heterogeneous CloudtainerML probe outputs.",
        "summary": {
            "artifact_count": len(records),
            "with_rows": sum(1 for r in records if r["has_rows"]),
            "with_summary": sum(1 for r in records if r["has_summary"]),
            "schema_warning": "Probe outputs are intentionally heterogeneous; this dashboard records what can be compared before forcing a common schema.",
        },
        "records": records,
    }
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_prefix.with_suffix(".json")
    csv_path = out_prefix.with_suffix(".csv")
    md_path = out_prefix.with_suffix(".md")
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if records:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
    md_lines = [
        f"# Probe suite dashboard — {revision(root)}",
        "",
        f"Artifacts scanned: **{len(records)}**",
        "",
        "| probe | rows | highlight | value | note |",
        "|---|---:|---|---:|---|",
    ]
    for r in records:
        val = r["highlight_value"]
        if isinstance(val, float):
            val_s = f"{val:.6g}"
        else:
            val_s = str(val)
        md_lines.append(f"| {r['probe']} | {r['row_count']} | {r['highlight_name']} | {val_s} | {r['highlight_note']} |")
    md_lines.append("")
    md_lines.append("## Refactor note")
    md_lines.append("")
    md_lines.append("Next schema target: every probe should emit `probe`, `config`, `summary.row_count`, `rows`, and one declared `primary_metric` block so cross-probe ranking does not require heuristics.")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out-prefix", type=Path, default=ROOT / "artifacts" / "probe-results" / f"{REVUP}_PROBE_SUITE_DASHBOARD")
    args = ap.parse_args()
    result = build_dashboard(args.root.resolve(), args.out_prefix)
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

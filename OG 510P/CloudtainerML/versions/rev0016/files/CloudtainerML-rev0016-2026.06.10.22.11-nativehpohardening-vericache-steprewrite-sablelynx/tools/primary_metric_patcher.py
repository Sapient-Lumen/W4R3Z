#!/usr/bin/env python3
"""Patch older probe JSON summaries with explicit primary metrics.

Rev0009's metric index showed many early probes had useful rows but no declared
`summary.primary_metric`. This refactor does not alter row data or winners; it
adds a small schema annotation so dashboards know how to compare/facet them.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "artifacts" / "probe-results"
AUDIT_DIR = ROOT / "artifacts" / "audit"

METRICS: Dict[str, Dict[str, str]] = {
    "kv_wind_tunnel": {"name": "relative_error", "direction": "lower_is_better", "winner_field": "none_rows_only"},
    "spectral_assoc_recall": {"name": "accuracy", "direction": "higher_is_better", "winner_field": "none_rows_only"},
    "dormant_sponsorship": {"name": "target_value_retention", "direction": "higher_is_better", "winner_field": "none_rows_only"},
    "region_wipeout_cache": {"name": "coverage_success", "direction": "higher_is_better", "winner_field": "none_rows_only"},
    "value_outlier_eviction": {"name": "critical_value_retention", "direction": "higher_is_better", "winner_field": "none_rows_only"},
    "depth_value_mixing": {"name": "mean_error", "direction": "lower_is_better", "winner_field": "by_scenario_method"},
    "dynamic_state_merging": {"name": "transition_preservation", "direction": "higher_is_better", "winner_field": "by_budget_policy"},
    "entmax_support_recovery": {"name": "output_error", "direction": "lower_is_better", "winner_field": "none_rows_only"},
    "moment_directional_gap": {"name": "reconstruction_error", "direction": "lower_is_better", "winner_field": "none_rows_only"},
    "qkv_projection_sharing": {"name": "relative_error", "direction": "lower_is_better", "winner_field": "by_regime_variant"},
    "tensor_cache_l1_l2": {"name": "retrieval_error", "direction": "lower_is_better", "winner_field": "none_rows_only"},
    "attention_runtime_termination": {"name": "relative_error", "direction": "lower_is_better", "winner_field": "none_rows_only"},
    "bank_of_values": {"name": "prediction_accuracy", "direction": "higher_is_better", "winner_field": "none_rows_only"},
    "blurry_window_attention": {"name": "reconstruction_error", "direction": "lower_is_better", "winner_field": "by_task_method"},
    "branch_cache_sharing": {"name": "state_match", "direction": "higher_is_better", "winner_field": "by_scenario_policy"},
    "hierarchical_fademem_cache": {"name": "reconstruction_error", "direction": "lower_is_better", "winner_field": "best_compressed_policy_by_regime_budget"},
    "reasoning_wave_budget": {"name": "retained_mass", "direction": "higher_is_better", "winner_field": "practical_winners_excluding_oracle"},
    "token_precision_frontier": {"name": "quality_score", "direction": "higher_is_better", "winner_field": "winner_counts"},
    "qk_restore_amnesia": {"name": "recall_accuracy", "direction": "higher_is_better", "winner_field": "practical_winners_excluding_pre_sft"},
}

SKIP_NAME_PARTS = ["DASHBOARD", "METRIC_INDEX", "CACHE_PROBE_REPORT"]


def revision() -> str:
    try:
        return json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")).get("revision", "rev0010")
    except Exception:
        return "rev0010"


def load(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def patch_file(path: Path, dry_run: bool = False) -> dict[str, Any]:
    obj = load(path)
    if not obj:
        return {"artifact": str(path.relative_to(ROOT)), "status": "parse_fail"}
    probe = str(obj.get("probe", path.stem))
    summary = obj.setdefault("summary", {})
    if not isinstance(summary, dict):
        obj["summary"] = summary = {}
    if isinstance(summary.get("primary_metric"), dict):
        return {"artifact": str(path.relative_to(ROOT)), "probe": probe, "status": "already_declared"}
    metric = METRICS.get(probe)
    if not metric:
        return {"artifact": str(path.relative_to(ROOT)), "probe": probe, "status": "no_mapping"}
    summary["primary_metric"] = metric
    summary["schema_patch"] = {
        "revision": revision(),
        "tool": "tools/primary_metric_patcher.py",
        "note": "Added dashboard-facing metric annotation only; row data unchanged.",
    }
    if not dry_run:
        path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    return {"artifact": str(path.relative_to(ROOT)), "probe": probe, "status": "patched", "metric": metric["name"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    records = []
    for path in sorted(PROBE_DIR.glob("REV*_*.json")):
        if any(part in path.name for part in SKIP_NAME_PARTS):
            continue
        records.append(patch_file(path, dry_run=args.dry_run))
    summary = {
        "patched": sum(1 for r in records if r.get("status") == "patched"),
        "already_declared": sum(1 for r in records if r.get("status") == "already_declared"),
        "no_mapping": sum(1 for r in records if r.get("status") == "no_mapping"),
        "parse_fail": sum(1 for r in records if r.get("status") == "parse_fail"),
    }
    payload = {"project": "CloudtainerML", "revision": revision(), "tool": "primary_metric_patcher", "summary": summary, "records": records}
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    prefix = AUDIT_DIR / f"{revision().upper()}_PRIMARY_METRIC_PATCH"
    prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = [f"# Primary metric patch — {revision()}", "", f"Patched: **{summary['patched']}**", f"Already declared: **{summary['already_declared']}**", f"No mapping: **{summary['no_mapping']}**", "", "| status | probe | artifact | metric |", "|---|---|---|---|"]
    for r in records:
        md.append(f"| {r.get('status')} | {r.get('probe','')} | {r.get('artifact','')} | {r.get('metric','')} |")
    prefix.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["parse_fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

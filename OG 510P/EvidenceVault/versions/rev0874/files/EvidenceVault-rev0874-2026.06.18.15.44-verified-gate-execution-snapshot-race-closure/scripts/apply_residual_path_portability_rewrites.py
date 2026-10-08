#!/usr/bin/env python3
"""Apply the rev0831 residual path portability rewrites.

rev0830 removed the large majority of cloud/container absolute paths.  This
script handles the remaining small set by using explicit replacements rather
than heuristic suffix matching.  Each replacement either points to a shipped
archive-relative target, preserves a known negative/missing-artifact condition
with a relative path, or replaces a build-host root with an explicit
unretained-upstream label.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.json"
MD_OUT = ROOT / "AUDIT" / "RESIDUAL_PATH_PORTABILITY_REWRITE_REV0831.md"

REPLACEMENTS: list[dict[str, str]] = [
    {
        "path": "artifacts/curated/zkrtp_v2/policy_report.json",
        "old": "/mnt/data/zk_rtp_paper_v0.27",
        "new": "unretained-upstream:zk_rtp_paper_v0.27",
        "classification": "historical_unretained_build_root_label",
        "rationale": "The curated zk-RTP representation does not retain the full upstream root referenced by the historical report; keep the upstream root token without a cloud/container coordinate.",
    },
    {
        "path": "sources/ocf_llm/examples/mer_demo/receipt_cache_index.json",
        "old": "/mnt/data/ocf_llm_paper_v196_work/ocf_llm_paper_evolving_v196/examples/mer_demo/receipt_cache",
        "new": "sources/ocf_llm/examples/mer_demo/receipt_cache",
        "classification": "rewrite_to_existing_shipped_directory",
        "rationale": "The receipt cache directory is shipped at this archive-relative path.",
    },
    {
        "path": "sources/ocf_llm/examples/nuc_demo/receipt_cache_ok_index.json",
        "old": "/mnt/data/ocf_llm_paper_v197_work/ocf_llm_paper_evolving_v197/examples/nuc_demo/receipt_cache_ok",
        "new": "sources/ocf_llm/examples/nuc_demo/receipt_cache_ok",
        "classification": "rewrite_to_existing_shipped_directory",
        "rationale": "The receipt cache directory is shipped at this archive-relative path.",
    },
    {
        "path": "sources/ocf_llm/examples/pip_gate_decision_annexiv_tampered_v1.json",
        "old": "ocf/paper/=/mnt/data/ocf_llm_paper_v97/",
        "new": "ocf/paper/=sources/ocf_llm/",
        "classification": "rewrite_prefix_map_to_shipped_source_root",
        "rationale": "The resolver prefix maps into the retained OCF LLM source tree.",
    },
    {
        "path": "sources/ocf_llm/examples/pip_gate_decision_annexiv_v1.json",
        "old": "ocf/paper/=/mnt/data/ocf_llm_paper_v97/",
        "new": "ocf/paper/=sources/ocf_llm/",
        "classification": "rewrite_prefix_map_to_shipped_source_root",
        "rationale": "The resolver prefix maps into the retained OCF LLM source tree.",
    },
    {
        "path": "sources/ocf_llm/examples/prc_put_demo_v203/prc.json",
        "old": "file:///mnt/data/ocf_llm_paper_evolving_current_v203/examples/prc_put_demo_v203",
        "new": "archive-relative:sources/ocf_llm/examples/prc_put_demo_v203",
        "classification": "rewrite_file_uri_to_archive_relative_locator",
        "rationale": "A file:// URI would require a host-specific absolute path; this archive-relative locator names the shipped demo directory without pretending to be a local host path.",
    },
    {
        "path": "sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_rec.yaml",
        "old": "/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl",
        "new": "sources/ocf_llm/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl",
        "classification": "rewrite_missing_artifact_reference_to_relative_expected_path",
        "rationale": "The trace records a missing-file condition.  Keep it missing, but express the expected file as an archive-relative path instead of a build-host path.",
    },
    {
        "path": "sources/ocf_llm/examples/publication_or_refusal_demo_v123/trace_pub_scitt.yaml",
        "old": "/mnt/data/ocf_llm_paper_evolving_current_v123/ocf_llm_paper_evolving/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl",
        "new": "sources/ocf_llm/examples/publication_or_refusal_demo_v123/mcp_episode_attempt_log_v1.jsonl",
        "classification": "rewrite_missing_artifact_reference_to_relative_expected_path",
        "rationale": "The trace records a missing-file condition.  Keep it missing, but express the expected file as an archive-relative path instead of a build-host path.",
    },
    {
        "path": "sources/ocf_llm/examples/release_train_overlap_demo_v211/summary.json",
        "old": "/mnt/data/ocf_llm_paper_evolving_current_v211/examples/release_train_overlap_demo_v211",
        "new": "sources/ocf_llm/examples/release_train_overlap_demo_v211",
        "classification": "rewrite_to_existing_shipped_directory",
        "rationale": "The demo output directory is shipped at this archive-relative path.",
    },
    {
        "path": "sources/ocf_llm/examples/resolver_bench_v1.json",
        "old": "/mnt/data/ocf_llm_paper_v87",
        "new": "sources/ocf_llm",
        "classification": "rewrite_benchmark_base_to_shipped_source_root",
        "rationale": "The commands in this benchmark use tools/ and examples/ relative to the OCF LLM source root.",
    },
    {
        "path": "sources/ocf_llm/examples/resolver_bench_v2.json",
        "old": "/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90",
        "new": ".",
        "classification": "rewrite_benchmark_base_to_archive_root",
        "rationale": "The commands in this benchmark already use sources/ocf_llm/... paths relative to the archive root.",
    },
    {
        "path": "sources/ocf_llm/examples/resolver_bench_v3.json",
        "old": "/mnt/data/ocf_llm_paper_workspace_v91/ocf_llm_paper_v90",
        "new": ".",
        "classification": "rewrite_benchmark_base_to_archive_root",
        "rationale": "The commands in this benchmark already use sources/ocf_llm/... paths relative to the archive root.",
    },
    {
        "path": "sources/ocf_llm/examples/resolver_trace_sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm.yaml",
        "old": "/mnt/data/ocf_llm_v81_work/ocf_llm_paper/examples/{'kind': 'file', 'path': 'examples/scitt_receipt_refusal_map_root_v1.json'}",
        "new": "sources/ocf_llm/examples/{'kind': 'file', 'path': 'examples/scitt_receipt_refusal_map_root_v1.json'}",
        "classification": "preserve_serialized_path_object_bug_without_cloud_root",
        "rationale": "The trace appears to contain a serialized object inside a path field.  Do not silently turn the historical fail-closed trace into an ok trace; remove the build-host prefix and let the shape-anomaly audit carry the remaining bug.",
    },
    {
        "path": "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
        "old": "/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_eval_log_v1.jsonl",
        "new": "sources/ocf_llm/examples/eic_qic_latency_eval_log_v1.jsonl",
        "classification": "rewrite_to_existing_shipped_file_inside_captured_output",
        "rationale": "The evidence file is shipped at this archive-relative path; the captured output remains otherwise unchanged.",
    },
    {
        "path": "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
        "old": "/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_suite_v1.jsonl",
        "new": "sources/ocf_llm/examples/eic_qic_latency_suite_v1.jsonl",
        "classification": "rewrite_to_existing_shipped_file_inside_captured_output",
        "rationale": "The evidence file is shipped at this archive-relative path; the captured output remains otherwise unchanged.",
    },
    {
        "path": "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
        "old": "/mnt/data/ocf_llm_paper_v96/examples/eic_qic_latency_summary_v1.json",
        "new": "sources/ocf_llm/examples/eic_qic_latency_summary_v1.json",
        "classification": "rewrite_to_existing_shipped_file_inside_captured_output",
        "rationale": "The evidence file is shipped at this archive-relative path; the captured output remains otherwise unchanged.",
    },
    {
        "path": "sources/ocf_llm/examples/runtime_gate_bench_v1.json",
        "old": "/mnt/data/ocf_llm_paper_v96",
        "new": "sources/ocf_llm",
        "classification": "rewrite_benchmark_base_to_shipped_source_root",
        "rationale": "The commands in this benchmark use tools/ and examples/ relative to the OCF LLM source root.",
    },
    {
        "path": "sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_pinned.yaml",
        "old": "/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json",
        "new": "sources/ocf_llm/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json",
        "classification": "rewrite_missing_artifact_reference_to_relative_expected_path",
        "rationale": "The trace records a missing-artifact condition.  Keep it missing, but express the expected file as an archive-relative path.",
    },
    {
        "path": "sources/ocf_llm/examples/scitt_log_substitution_v124/resolver_trace_base_unpinned.yaml",
        "old": "/mnt/data/ocf_llm_paper_evolving_current_v125/ocf_llm_paper_evolving/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json",
        "new": "sources/ocf_llm/examples/scitt_log_substitution_v124/scitt_receipt_placeholder.json",
        "classification": "rewrite_missing_artifact_reference_to_relative_expected_path",
        "rationale": "The trace records a missing-artifact condition.  Keep it missing, but express the expected file as an archive-relative path.",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(root: Path = ROOT) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    touched: dict[str, dict[str, Any]] = {}
    for repl in REPLACEMENTS:
        rel = repl["path"]
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(rel)
        before_text = path.read_text(encoding="utf-8")
        count = before_text.count(repl["old"])
        if count == 0:
            raise RuntimeError(f"old value not found in {rel}: {repl['old']!r}")
        after_text = before_text.replace(repl["old"], repl["new"])
        path.write_text(after_text, encoding="utf-8")
        touched.setdefault(rel, {"before_sha256": None, "after_sha256": None})
        rows.append({
            "path": rel,
            "old": repl["old"],
            "new": repl["new"],
            "occurrences_rewritten": count,
            "classification": repl["classification"],
            "rationale": repl["rationale"],
            "new_target_exists": (root / repl["new"]).exists() if not repl["new"].startswith(("unretained-upstream:", "archive-relative:")) and repl["new"] != "." and "{" not in repl["new"] else None,
        })
    for rel in touched:
        touched[rel]["after_sha256"] = sha256(root / rel)
    return {
        "version": 1,
        "revision_context": "rev0831-session-patch-over-rev0830-over-rev0826",
        "status": "residual_cloud_paths_rewritten_or_relabelled",
        "purpose": "Remove the residual build-host path coordinates left after rev0830 while preserving historical missing-artifact and fail-closed semantics.",
        "summary": {
            "replacement_rules": len(REPLACEMENTS),
            "files_touched": len({row["path"] for row in rows}),
            "occurrences_rewritten": sum(row["occurrences_rewritten"] for row in rows),
            "classifications": sorted(set(row["classification"] for row in rows)),
        },
        "rows": rows,
        "builder": "scripts/apply_residual_path_portability_rewrites.py",
        "validator": "scripts/validate_residual_path_portability_rewrite.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    s = data["summary"]
    lines = [
        "# Residual path portability rewrite — rev0831",
        "",
        "This ledger records the explicit, non-heuristic rewrites used to remove the remaining cloud/container path coordinates after rev0830.",
        "",
        f"- Status: `{data['status']}`",
        f"- Replacement rules: **{s['replacement_rules']}**",
        f"- Files touched: **{s['files_touched']}**",
        f"- Occurrences rewritten: **{s['occurrences_rewritten']}**",
        "",
        "## Classifications",
        "",
    ]
    for cls in s["classifications"]:
        lines.append(f"- `{cls}`")
    lines.extend([
        "",
        "## Rewrite rows",
        "",
        "| Path | Count | Classification | Old | New |",
        "| --- | ---: | --- | --- | --- |",
    ])
    for row in data["rows"]:
        old = row["old"].replace("|", "\\|")
        new = row["new"].replace("|", "\\|")
        lines.append(f"| `{row['path']}` | {row['occurrences_rewritten']} | `{row['classification']}` | `{old}` | `{new}` |")
    lines.extend([
        "",
        "## Notes",
        "",
        "- Rewrites with `rewrite_missing_artifact_reference_to_relative_expected_path` intentionally keep the referenced target absent; the point is portability of the expected path, not conversion of a negative test into a passing test.",
        "- The serialized-object path anomaly is intentionally not normalized into an existing receipt path because that would silently change a historical fail-closed trace. It is surfaced separately by `AUDIT/PATH_REFERENCE_SHAPE_AUDIT.*`.",
        "- The zk-RTP build root is relabelled as `unretained-upstream:*` because the full upstream root is not retained in this archive.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = apply(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "residual-path-portability-rewrite: OK "
        f"({data['summary']['files_touched']} files, {data['summary']['occurrences_rewritten']} occurrences)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

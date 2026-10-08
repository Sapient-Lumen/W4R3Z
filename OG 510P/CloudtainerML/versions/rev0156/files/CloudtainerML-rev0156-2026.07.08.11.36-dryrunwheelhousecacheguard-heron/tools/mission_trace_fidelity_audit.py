#!/usr/bin/env python3
"""Mission, waste, surface-coherence, and trace-fidelity audit for current revision."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from revision_lineage_static_audit import scan_revision_lineage

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0076")
REVUP = REV.upper()
STAMP = META.get("generated_at") or META.get("created_at") or "unknown"
OUT_JSON = ROOT / "artifacts" / "audit" / f"{REVUP}_MISSION_WASTE_TRACE_FIDELITY_AUDIT.json"
OUT_MD = ROOT / "artifacts" / "audit" / f"{REVUP}_MISSION_WASTE_TRACE_FIDELITY_AUDIT.md"
ROOT_MD = ROOT / f"MISSION-AUDIT-{REVUP}.md"
PREFLIGHT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
POST_CONTRACT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT.json"

CRITICAL_JSON_SURFACES = [
    "CUBE-META.json",
    "EVIDENCE-STATUS.json",
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "REENTRY-CONTRACT.json",
]
CRITICAL_TEXT_SURFACES = [
    "README.md", "START_HERE.md", "START_HERE_SLIM.md", "NEXT-TURN-PROMPT.md",
    "MISSION-KERNEL.md", "PROJECT-CHARTER.md", "PROJECT-SALIENCE.md", "PRIORITY-LIST.md",
    "CONTEXT-PACK.md", "OPEN-QUESTIONS.md", "HUNT-QUESTIONS.md",
]


def load_json(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def top_counts(values: list[str], n: int = 12) -> list[dict[str, Any]]:
    return [{"value": key, "count": count} for key, count in Counter(values).most_common(n)]


def tree_metrics() -> dict[str, Any]:
    files = [p for p in ROOT.rglob("*") if p.is_file()]
    top_bytes: Counter[str] = Counter()
    artifact_bytes: Counter[str] = Counter()
    extension_counts: Counter[str] = Counter()
    revision_counts: Counter[str] = Counter()
    revision_bytes: Counter[str] = Counter()
    largest: list[tuple[int, str]] = []
    hash_groups: dict[str, list[tuple[str, int]]] = defaultdict(list)
    binary_paths: list[dict[str, Any]] = []
    pyc = []
    revision_content_mismatches: list[dict[str, Any]] = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        size = path.stat().st_size
        top = rel.split("/", 1)[0]
        top_bytes[top] += size
        if rel.startswith("artifacts/"):
            parts = rel.split("/")
            artifact_bytes[parts[1] if len(parts) > 1 else "(root)"] += size
        suffix = path.suffix.lower() or "(none)"
        extension_counts[suffix] += 1
        match = re.search(r"REV(\d{4})", path.name.upper())
        if match:
            key = f"rev{match.group(1)}"
            revision_counts[key] += 1
            revision_bytes[key] += size
            if path.suffix.lower() == ".json" and size < 4_000_000:
                try:
                    obj = json.loads(path.read_text(encoding="utf-8"))
                    content_revision = str(obj.get("revision", "")) if isinstance(obj, dict) else ""
                    if re.fullmatch(r"rev\d{4}", content_revision) and content_revision != key:
                        revision_content_mismatches.append({
                            "path": rel,
                            "filename_revision": key,
                            "content_revision": content_revision,
                        })
                except (UnicodeDecodeError, json.JSONDecodeError, OSError):
                    pass
        largest.append((size, rel))
        if suffix == ".pyc":
            pyc.append(rel)
        if rel.startswith("artifacts/bin/") or rel.startswith("artifacts/native-build/"):
            binary_paths.append({"path": rel, "bytes": size})
        # Hash every file; the cube is small enough and exact duplicates are useful waste evidence.
        hash_groups[sha256_file(path)].append((rel, size))
    duplicate_groups = []
    recoverable = 0
    for digest, group in hash_groups.items():
        if len(group) > 1:
            size = group[0][1]
            recoverable += size * (len(group) - 1)
            duplicate_groups.append({"sha256": digest, "bytes_each": size, "paths": [p for p, _ in group]})
    duplicate_groups.sort(key=lambda x: x["bytes_each"] * (len(x["paths"]) - 1), reverse=True)
    return {
        "file_count": len(files),
        "tracked_bytes_current_tree": sum(p.stat().st_size for p in files),
        "top_level_bytes": dict(top_bytes.most_common()),
        "artifact_subtree_bytes": dict(artifact_bytes.most_common()),
        "extension_counts": dict(extension_counts.most_common()),
        "largest_files": [{"path": rel, "bytes": size} for size, rel in sorted(largest, reverse=True)[:15]],
        "exact_duplicate_group_count": len(duplicate_groups),
        "exact_duplicate_recoverable_bytes": recoverable,
        "largest_exact_duplicate_groups": duplicate_groups[:12],
        "compiled_binary_count": len(binary_paths),
        "compiled_binary_bytes": sum(x["bytes"] for x in binary_paths),
        "compiled_binaries": binary_paths,
        "pyc_count": len(pyc),
        "pyc_paths": pyc,
        "revision_labels_in_filenames": len(revision_counts),
        "revision_file_counts": dict(sorted(revision_counts.items())),
        "revision_bytes": dict(sorted(revision_bytes.items())),
        "revision_content_mismatch_count": len(revision_content_mismatches),
        "revision_content_mismatches": revision_content_mismatches,
    }


def ledger_metrics() -> dict[str, Any]:
    ideas_doc = load_json("IDEA-LEDGER.json")
    cells_doc = load_json("EXPERIMENT-MATRIX.json")
    questions_doc = load_json("QUESTION-LEDGER.json")
    sources_doc = load_json("RESEARCH-SOURCE-REGISTRY.json")
    native_doc = load_json("NATIVE-PROBE-MANIFEST.json")
    ideas = ideas_doc.get("ideas", [])
    cells = cells_doc.get("cells", [])
    questions = questions_doc.get("questions", [])
    sources = sources_doc.get("sources", [])

    arxiv_groups: dict[str, list[str]] = defaultdict(list)
    title_groups: dict[str, list[str]] = defaultdict(list)
    for source in sources:
        arxiv = str(source.get("arxiv", "")).strip()
        if arxiv:
            arxiv_groups[arxiv].append(str(source.get("id")))
        title = normalized_title(str(source.get("title", "")))
        if title:
            title_groups[title].append(str(source.get("id")))
    duplicate_arxiv = {key: value for key, value in arxiv_groups.items() if len(value) > 1}
    duplicate_titles = {key: value for key, value in title_groups.items() if len(value) > 1}

    bind_prefixes: Counter[str] = Counter()
    for question in questions:
        for ref in question.get("binds_to", []) or []:
            text = str(ref)
            if text.startswith("IDEA-"):
                bind_prefixes["IDEA"] += 1
            elif text.startswith("CELL-"):
                bind_prefixes["CELL"] += 1
            elif text.startswith("SRC-"):
                bind_prefixes["SRC"] += 1
            elif text.startswith("CUBE"):
                bind_prefixes["CUBE"] += 1
            else:
                bind_prefixes["OTHER"] += 1

    q_status = Counter(str(x.get("status", "")) for x in questions)
    open_count = q_status.get("open", 0)
    return {
        "ideas": {
            "count": len(ideas),
            "declared_count": ideas_doc.get("count"),
            "ledger_revision": ideas_doc.get("revision"),
            "distinct_statuses": len({str(x.get("status", "")) for x in ideas}),
            "status_top": top_counts([str(x.get("status", "")) for x in ideas]),
        },
        "cells": {
            "count": len(cells),
            "declared_count": cells_doc.get("count"),
            "ledger_revision": cells_doc.get("revision"),
            "distinct_statuses": len({str(x.get("status", "")) for x in cells}),
            "status_top": top_counts([str(x.get("status", "")) for x in cells]),
        },
        "questions": {
            "count": len(questions),
            "declared_count": questions_doc.get("count"),
            "ledger_revision": questions_doc.get("revision"),
            "status_counts": dict(q_status),
            "open_ratio": open_count / len(questions) if questions else None,
            "distinct_topics": len({str(x.get("topic", "")) for x in questions}),
            "binding_reference_types": dict(bind_prefixes),
        },
        "sources": {
            "count": len(sources),
            "declared_count": sources_doc.get("count"),
            "ledger_revision": sources_doc.get("revision"),
            "distinct_families": len({str(x.get("family", "")) for x in sources}),
            "family_to_source_ratio": len({str(x.get("family", "")) for x in sources}) / len(sources) if sources else None,
            "duplicate_arxiv_id_count": len(duplicate_arxiv),
            "duplicate_arxiv_entries_beyond_first": sum(len(v) - 1 for v in duplicate_arxiv.values()),
            "duplicate_arxiv_groups": duplicate_arxiv,
            "duplicate_normalized_title_count": len(duplicate_titles),
            "year_counts": dict(Counter(str(x.get("year", "unknown")) for x in sources)),
        },
        "native_probe_manifest": {
            "declared_count": native_doc.get("count"),
            "ledger_revision": native_doc.get("revision"),
            "actual_cpp_file_count": len(list((ROOT / "experiments").rglob("*.cpp"))),
        },
    }


def surface_metrics() -> dict[str, Any]:
    errors = []
    details: dict[str, Any] = {}
    package_name = META.get("package_name")
    archive_name = META.get("archive_name")
    for rel in CRITICAL_JSON_SURFACES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        data = load_json(rel)
        revisions = {key: data.get(key) for key in ["revision", "current_revision", "evidence_revision"] if key in data}
        details[rel] = revisions
        if "revision" in data and data.get("revision") != REV:
            errors.append(f"{rel} revision={data.get('revision')} expected {REV}")
        if "revision_number" in data and int(data.get("revision_number")) != int(META.get("revision_number")):
            errors.append(f"{rel} revision_number mismatch")
        if "package_name" in data and data.get("package_name") != package_name:
            errors.append(f"{rel} package_name mismatch")
        if "archive_name" in data and data.get("archive_name") != archive_name:
            errors.append(f"{rel} archive_name mismatch")
    for rel in CRITICAL_TEXT_SURFACES:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        details[rel] = {"mentions_current_revision": REV in text[:2000]}
        if REV not in text[:2000]:
            errors.append(f"{rel} does not mention {REV} near entry surface")
    return {"status": "pass" if not errors else "fail", "errors": errors, "details": details}


def trace_fidelity_metrics() -> dict[str, Any]:
    gate_text = (ROOT / "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py").read_text(encoding="utf-8")
    capture_text = (ROOT / "experiments/public_trace_capture/hf_attention_trace_capture.py").read_text(encoding="utf-8")
    contract_text = (ROOT / "experiments/post_transform_trace_contract/post_transform_trace_contract.py").read_text(encoding="utf-8") if (ROOT / "experiments/post_transform_trace_contract/post_transform_trace_contract.py").exists() else ""
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8")) if PREFLIGHT.exists() else {}
    pre_summary = preflight.get("summary", {})
    contract = json.loads(POST_CONTRACT.read_text(encoding="utf-8")) if POST_CONTRACT.exists() else {}
    contract_summary = contract.get("summary", {})
    checks = {
        "actual_d_head_reaches_compiler": "d_head=row.d_head" in gate_text,
        "qkv_aliases_supported": '("queries", "keys", "values")' in gate_text,
        "score_only_requires_d_head": "score/value schema requires positive integer d_head metadata" in gate_text,
        "public_requires_post_transform_stage": "PUBLIC_SCORE_INPUT_STAGE" in gate_text and "post_model_qk_transforms" in gate_text,
        "public_requires_explicit_score_semantics": all(x in gate_text for x in ["PUBLIC_SCORE_TRANSFORM", "attention_scale", "score_bias"]),
        "public_recomputes_dense_reference": "verify_qkv_score_contract" in gate_text and "computed_dense_reference_max_abs_error" in gate_text,
        "public_requires_immutable_revisions": "_is_immutable_revision" in gate_text and "tokenizer_revision must be an immutable" in gate_text,
        "public_schema_v3_v2": "public_trace_claim_v3" in gate_text and "qkv_npz_v2" in gate_text,
        "raw_projection_capture_marked_unverified": "raw_projection_pre_attention_transforms" in capture_text and '"attention_score_inputs_verified": False' in capture_text,
        "capture_score_semantics_marked_unverified": '"attention_scale_verified": False' in capture_text and '"score_bias_verified": False' in capture_text,
        "bf16_safe_capture_cast": "to(dtype=torch.float32).cpu().numpy()" in capture_text,
        "immutable_revision_capture_guard": "_is_immutable_revision" in capture_text and "resolved_tokenizer_revision" in capture_text,
        "preflight_all_cases_passed": pre_summary.get("all_cases_passed") is True and int(pre_summary.get("case_count", 0)) >= 16,
        "raw_projection_public_claim_rejected": pre_summary.get("raw_projection_public_claim_rejected") is True,
        "score_semantics_required": pre_summary.get("score_semantics_required") is True,
        "dense_reference_recomputed": pre_summary.get("dense_reference_recomputed") is True,
        "forged_dense_reference_rejected": pre_summary.get("forged_dense_reference_rejected") is True,
        "immutable_model_tokenizer_code_enforced": all(pre_summary.get(k) is True for k in ["immutable_model_revision_enforced", "immutable_tokenizer_revision_enforced", "immutable_trusted_code_revision_enforced"]),
        "actual_q_head_dimension_propagated": pre_summary.get("actual_q_head_dimension_propagated") is True,
        "post_transform_contract_runner_present": "apply_rope" in contract_text and "dense_attention" in contract_text and "NEGATIVE_MASK_BIAS" in contract_text,
        "post_transform_contract_exact": contract_summary.get("post_transform_contract_within_tolerance") is True and float(contract_summary.get("post_transform_dense_reference_max_abs_error", 1.0)) <= 1e-12,
        "raw_projection_negative_control_exceeds_tolerance": contract_summary.get("raw_projection_contract_rejected_or_out_of_tolerance") is True and float(contract_summary.get("raw_projection_against_post_reference_max_abs_error", 0.0)) > 1e-5,
        "post_transform_multi_axis_coverage": int(contract_summary.get("prompt_count", 0)) >= 3 and int(contract_summary.get("position_count", 0)) >= 6 and int(contract_summary.get("layer_count", 0)) >= 3 and int(contract_summary.get("head_count", 0)) >= 2,
        "post_transform_gate_nonpublic_replay": contract_summary.get("gate_external_nonpublic_loaded") is True and contract_summary.get("gate_actual_d_head_propagated") is True,
        "synthetic_public_claim_rejected": contract_summary.get("synthetic_public_claim_rejected") is True,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "preflight_summary": pre_summary,
        "post_transform_contract_summary": contract_summary,
    }


def build_report() -> dict[str, Any]:
    tree = tree_metrics()
    ledgers = ledger_metrics()
    surfaces = surface_metrics()
    fidelity = trace_fidelity_metrics()
    lineage = scan_revision_lineage()
    lineage_summary = lineage.get("summary", {})

    severe = [
        {
            "id": "semantic-trace-capture-stage",
            "severity": "critical-corrected",
            "finding": "The inherited Llama/Mistral/Gemma projection-hook adapter captured q_proj/k_proj outputs before rotary/architecture-specific Q/K transforms, while the evaluator treated them as the vectors actually scored by attention.",
            "correction": "Public claims now require post_model_qk_transforms, verified score inputs, and dense-reference parity. Raw projection captures remain diagnostic and are rejected by the preflight.",
        },
        {
            "id": "score-semantics-and-self-attested-parity",
            "severity": "critical-corrected",
            "finding": "Even post-transform Q/K is insufficient unless replay also knows the model's exact score rule. The inherited contract omitted attention scaling and score bias/mask, and accepted dense-reference parity as a boolean plus claimed error instead of recomputing it.",
            "correction": "Public qkv_npz_v2 bundles must carry explicit attention_scale, score_bias, a supported score_transform, and dense_reference_output. The gate recomputes softmax attention and rejects missing, unsupported, or forged references.",
        },
        {
            "id": "mutable-provenance-accepted-as-immutable",
            "severity": "high-corrected",
            "finding": "The prior provenance gate required nonempty revision labels but could accept mutable branches or tags; tokenizer identity and trusted remote code were not enforced as immutable inputs.",
            "correction": "Public claims now require immutable full model and tokenizer commit/content hashes, plus an immutable code revision when trusted remote code is enabled. The preflight exercises all three vetoes.",
        },
        {
            "id": "head-dimension-cost-substitution",
            "severity": "high-corrected",
            "finding": "Imported Q/K/V traces were evaluated with a global D_HEAD=32 even when q.shape[-1] differed; the rev0075 fixture is D=12. This corrupted QK byte estimates at the exact cost-truth boundary the mission treats as decisive.",
            "correction": "TraceRow carries d_head; Q/K/V derives it from q.shape[-1]; score-only bundles must supply it; the preflight proves D=12 is propagated.",
        },
        {
            "id": "green-check-semantic-gap",
            "severity": "high-corrected-partially",
            "finding": "The inherited validators proved labels, hashes, shapes, and fail-closed claims, but not whether captured tensors and replay equations meant what the scientific claim said they meant.",
            "correction": "rev0076 added tensor-stage, score-rule, recomputed-parity, and immutable-revision checks; rev0077 adds an executable synthetic post-transform contract harness proving exact post-transform replay and raw-projection failure. A real public model bundle and real HF architecture adapter remain missing.",
        },
        {
            "id": "live-surface-multiple-truths",
            "severity": "high-corrected",
            "finding": "The source rev0075 package exposed rev0074 in README/START_HERE/reentry surfaces and mixed rev0071/rev0072/rev0074 fields in SURFACE-STATUS.json.",
            "correction": "Critical entry surfaces are rewritten around one current revision contract and checked by this audit.",
        },
        {
            "id": "historical-runners-can-launder-current-revisions",
            "severity": "high-partially-corrected",
            "finding": (
                f"The static scan found {lineage_summary.get('historical_dynamic_artifact_minting_hazards', 0)} legacy Python runners/reports that can inherit the live cube revision and write revision-derived artifact paths; "
                f"{lineage_summary.get('dynamic_revision_hardcoded_timestamp_hazards', 0)} also pair that dynamic revision with a hard-coded historical timestamp. A rerun can therefore look current while carrying historical code and time semantics."
            ),
            "correction": (
                f"The three public-trace historical experiments and their three paired audits are pinned to their original revisions and marked frozen history ({lineage_summary.get('protected_public_trace_surfaces_safe', 0)}/{lineage_summary.get('protected_public_trace_surfaces', 0)} protected surfaces safe). "
                "The remaining legacy runners are enumerated by the current revision-lineage static audit and require staged migration rather than silent relabeling."
            ),
        },
    ]

    waste = [
        {
            "id": "governance-loop-around-absent-data",
            "severity": "high-ongoing",
            "evidence": "rev0072–rev0075 repeatedly hardened claim/capture ingress while actual public post-transform Q/K/V and named-hardware fused timing remained absent.",
            "recommended_stop_rule": "No further provenance/gate-only revision unless it closes a newly demonstrated acceptance defect. The next trace-lane revision must contain either a verified real model capture, a verified adapter parity test, or a named-hardware kernel result.",
        },
        {
            "id": "ledger-taxonomy-fragmentation",
            "severity": "medium-ongoing",
            "evidence": {
                "idea_status_count": ledgers["ideas"]["distinct_statuses"],
                "cell_status_count": ledgers["cells"]["distinct_statuses"],
                "source_family_count": ledgers["sources"]["distinct_families"],
                "source_count": ledgers["sources"]["count"],
                "question_topic_count": ledgers["questions"]["distinct_topics"],
                "question_count": ledgers["questions"]["count"],
            },
            "recommended_change": "Introduce small controlled enums plus aliases: evidence_stage, lane_state, decision, and mechanism_family. Preserve original labels as history, but stop minting one-off statuses/families.",
        },
        {
            "id": "question-registry-overhang",
            "severity": "medium-ongoing",
            "evidence": {
                "open_questions": ledgers["questions"]["status_counts"].get("open", 0),
                "question_count": ledgers["questions"]["count"],
                "open_ratio": ledgers["questions"]["open_ratio"],
            },
            "recommended_change": "Questions should be retired, merged, or bound to a funded experiment. Cap active questions per lane and require a next falsifier or archive them.",
        },
        {
            "id": "historical-revision-label-mismatches",
            "severity": "low-integrity-debt-ongoing",
            "evidence": {
                "count": tree["revision_content_mismatch_count"],
                "items": tree["revision_content_mismatches"],
            },
            "recommended_change": "Preserve historical artifacts immutably, but add an explicit correction index rather than silently rewriting old evidence. New packaging audits should reject fresh filename/content revision mismatches.",
        },
        {
            "id": "historical-binary-and-input-carry-cost",
            "severity": "low-to-medium-ongoing",
            "evidence": {
                "compiled_binary_count": tree["compiled_binary_count"],
                "compiled_binary_bytes": tree["compiled_binary_bytes"],
                "artifact_subtree_bytes": tree["artifact_subtree_bytes"],
            },
            "recommended_change": "Keep source and run manifests in the working cube; move reproducible executables and repeated native input blobs to a cold-history archive unless they are current replay dependencies.",
        },
    ]

    status = "pass_with_blockers" if surfaces["status"] == "pass" and fidelity["status"] == "pass" and lineage.get("status") != "fail" else "fail"
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "mission_waste_trace_fidelity_audit",
        "generated_at": STAMP,
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "heart_of_mission": "Convert architecture claims into cheap adversarial falsifiers, enforce exactness/cost/provenance vetoes, and promote only mechanisms that survive measured deployment—not accumulate ideas, probes, or green checks.",
        "source_revision_assessed": "rev0075",
        "severe_findings": severe,
        "waste_findings": waste,
        "missing": [
            "real HF architecture-aware post-transform Q/K/V capture on an actual public pretrained model",
            "immutable public model/tokenizer/code/config provenance on an actual trace bundle",
            "multi-prompt, multi-position, multi-length real-model trace coverage rather than synthetic contract coverage",
            "GPU/fused sparse-kernel implementation and named-hardware end-to-end timing",
            "end-to-end task quality under the same model, prompts, and serving constraints",
            "controlled status/family taxonomy and typed ledger references",
            "revision budget/stop rule that prevents governance work from becoming the product",
            "explicit run-lineage contracts for legacy runners so historical code cannot inherit the current revision or overwrite retained evidence",
        ],
        "recommended_operating_change": {
            "center": "claim compiler / falsification wind tunnel",
            "next_mandatory_lane": "real public-model capture or named-hardware implementation, not another synthetic/gate revision",
            "three_budget_rule": {
                "science_or_kernel": "at least 70% of revision effort",
                "audit_and_provenance": "at most 20% unless a concrete defect is demonstrated",
                "registry_and_docs": "at most 10%",
            },
            "promotion_vector": [
                "semantic fidelity",
                "exactness/task quality",
                "measured latency/throughput and memory on named hardware",
                "reproducible immutable provenance",
                "coverage across hostile regimes",
            ],
        },
        "surface_coherence": surfaces,
        "trace_fidelity": fidelity,
        "revision_lineage": lineage,
        "ledgers": ledgers,
        "tree": tree,
        "remaining_blockers": [
            "actual_public_pretrained_post_transform_qkv_bundle_missing",
            "verified_capture_adapter_with_exact_score_semantics_and_dense_reference_parity_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "named_hardware_end_to_end_replay_missing",
            "legacy_dynamic_revision_inheritance_migration_incomplete",
        ],
        "interpretation": "rev0077 adds executable post-transform adapter semantics on top of rev0076 trace-ingress hardening. It deliberately does not promote the sparse-attention lane. The next valuable revision must contain real public-model capture or named-hardware evidence, or should pivot to another mechanism with a cheaper decisive falsifier.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    ledgers = report["ledgers"]
    tree = report["tree"]
    lines = [
        f"# CloudtainerML mission audit — {REV}",
        "",
        f"**Status:** {report['status']}  ",
        "**Promotion:** blocked  ",
        "**Claim boundary:** mission/surface/trace-ingress audit only; no public-model or GPU result.",
        "",
        "## Heart of the mission",
        "",
        report["heart_of_mission"],
        "",
        "The cube is best understood as a **claim compiler**: it should turn a proposed mechanism into the cheapest decisive experiment, force the experiment through exactness and cost vetoes, and either stop the lane or escalate it to measured implementation. Its product is a trustworthy decision, not a growing registry.",
        "",
        "## What had gone severely wrong",
        "",
    ]
    for item in report["severe_findings"]:
        lines.extend([f"### {item['severity']}: {item['id']}", "", item["finding"], "", f"**Correction:** {item['correction']}", ""])
    lines.extend([
        "## What is missing",
        "",
    ])
    lines.extend([f"- {item}" for item in report["missing"]])
    lines.extend([
        "",
        "## Waste and drift",
        "",
        f"- {ledgers['questions']['status_counts'].get('open', 0)} of {ledgers['questions']['count']} questions remain open ({ledgers['questions']['open_ratio']:.1%}).",
        f"- {ledgers['sources']['distinct_families']} source families classify {ledgers['sources']['count']} sources; the taxonomy is nearly one family per source.",
        f"- Idea and experiment-cell ledgers use {ledgers['ideas']['distinct_statuses']} and {ledgers['cells']['distinct_statuses']} distinct status strings.",
        f"- The research registry contains {ledgers['sources']['duplicate_arxiv_id_count']} duplicated arXiv-ID groups.",
        f"- {tree['revision_content_mismatch_count']} historical JSON summaries disagree between the revision in their filename and the revision in their content; they are preserved as history and should be indexed as corrections rather than silently mutated.",
        f"- Compiled artifacts occupy {tree['compiled_binary_bytes']:,} bytes across {tree['compiled_binary_count']} files; exact duplicate recovery is only {tree['exact_duplicate_recoverable_bytes']:,} bytes, so the larger footprint is mostly historical inputs/results rather than accidental copies.",
        f"- The lineage scan still finds {report['revision_lineage']['summary']['historical_dynamic_artifact_minting_hazards']} legacy artifact-minting hazards, including {report['revision_lineage']['summary']['dynamic_revision_hardcoded_timestamp_hazards']} dynamic-revision/hard-coded-time contradictions; six public-trace surfaces are now pinned.",
        "- The dominant process waste is not storage; it is revision attention spent perfecting ingress governance around real public-model and hardware evidence that still does not exist.",
        "",
        "## What should change",
        "",
        "1. **Stop gate-only churn.** No more trace-governance revision without a demonstrated new defect. Require a real verified trace, verified adapter parity, or named-hardware result.",
        "2. **Make semantic fidelity a first-class veto.** Capture post-transform Q/K/V, record exact scale/bias/transform semantics, recompute dense parity, pin model/tokenizer/code commits, and record config hashes.",
        "3. **Measure systems, not proxies.** Keep the CPU/NumPy wind tunnel for falsification, but treat promotion as a named-hardware kernel and end-to-end task-quality decision.",
        "4. **Compress the registries.** Normalize statuses/families, type references, merge duplicate questions/sources, and keep only a small funded frontier active.",
        "5. **Adopt revision budgets.** Target 70% mechanism/kernel work, at most 20% audit/provenance, and at most 10% registry/docs unless a concrete integrity defect is found.",
        "6. **Separate history from reruns.** Freeze historical runners to their original revisions. A genuine rerun must declare a new run revision, generate its execution time at runtime, hash code/dependencies, and write to a separate namespace.",
        "",
        "## Current corrective result",
        "",
        f"The {REV} post-transform contract covers {report['trace_fidelity']['post_transform_contract_summary'].get('row_count')} synthetic rows across {report['trace_fidelity']['post_transform_contract_summary'].get('prompt_count')} prompts, {report['trace_fidelity']['post_transform_contract_summary'].get('position_count')} positions, {report['trace_fidelity']['post_transform_contract_summary'].get('layer_count')} layers, and {report['trace_fidelity']['post_transform_contract_summary'].get('head_count')} heads. Post-transform replay error is {report['trace_fidelity']['post_transform_contract_summary'].get('post_transform_dense_reference_max_abs_error')}; raw projection Q/K fails against the same reference with max error {report['trace_fidelity']['post_transform_contract_summary'].get('raw_projection_against_post_reference_max_abs_error')}. The inherited preflight still passes {report['trace_fidelity']['preflight_summary'].get('passed_cases')} of {report['trace_fidelity']['preflight_summary'].get('case_count')} adversarial cases.",
        "",
        "## Next hard stop",
        "",
        "The next revision should not add another synthetic contract or policy layer. It should either (a) capture a real immutable public trace with an architecture-aware adapter, (b) run a sparse kernel on named hardware with end-to-end quality, or (c) explicitly stop this lane and redeploy the claim-compiler machinery to a different mechanism.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(report)
    OUT_MD.write_text(md, encoding="utf-8")
    ROOT_MD.write_text(md, encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "surface_status": report["surface_coherence"]["status"],
        "trace_fidelity_status": report["trace_fidelity"]["status"],
        "revision_lineage_status": report["revision_lineage"]["status"],
        "lineage_migration_debt": report["revision_lineage"]["summary"]["remaining_migration_debt"],
        "open_questions": report["ledgers"]["questions"]["status_counts"].get("open", 0),
        "source_families": report["ledgers"]["sources"]["distinct_families"],
        "compiled_binary_bytes": report["tree"]["compiled_binary_bytes"],
    }, indent=2))
    return 0 if report["status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())

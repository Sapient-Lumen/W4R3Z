import json
import pathlib
import re
from collections import Counter, defaultdict
from typing import Any

from release_hygiene_lib import iter_release_paths
from release_integrity_lib import INTEGRITY_SURFACES
from generated_surface_lib import GENERATOR_SCRIPTS
from ledger_debt_policy_lib import (
    LEDGER_DEBT_POLICIES,
    live_debt_snapshot,
    live_retrospectives_with_nonlive_obligations,
    state_mirror_mismatches,
)
from validation_toolchain_lib import build_validation_toolchain

AUDIT_SURFACES = {"ARCHIVE-ECONOMY-AUDIT.json", "docs/00-meta/archive-economy-audit.md"}
ECONOMY_EXCLUDED_SURFACES = AUDIT_SURFACES | INTEGRITY_SURFACES
WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def load_canary_runs(root: pathlib.Path) -> dict[str, Any]:
    path = root / "CANARY-RUNS.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rows_from_canary_runs(root: pathlib.Path, key: str) -> list[dict[str, Any]]:
    data = load_canary_runs(root)
    rows = data.get(key, [])
    return rows if isinstance(rows, list) else []


def canary_failure_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if isinstance(row, dict) and row.get("status") != "pass")


def package_artifact_rows_from_canary_runs(root: pathlib.Path) -> list[dict[str, Any]]:
    rows = rows_from_canary_runs(root, "negative_mutation_runs")
    return [
        row for row in rows
        if isinstance(row, dict)
        and (str(row.get("id", "")).startswith("zip-") or str(row.get("id", "")).startswith("safe-extract-"))
    ]


def release_economy_paths(root: pathlib.Path) -> list[pathlib.Path]:
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    bundle_name = manifest.get("bundle")
    paths = []
    for path in iter_release_paths(root, bundle_name):
        rel = path.relative_to(root).as_posix()
        if rel in ECONOMY_EXCLUDED_SURFACES:
            continue
        paths.append(path)
    return paths


def sha256ish_surface(path: pathlib.Path) -> bool:
    return path.name in {"CHECKSUMS.sha256"} or path.name.endswith(".sha256")


def count_words(path: pathlib.Path) -> int:
    try:
        return len(WORD_RE.findall(path.read_text(encoding="utf-8")))
    except UnicodeDecodeError:
        return 0


def top_counter(counter: Counter, limit: int = 12) -> list[dict[str, Any]]:
    return [{"key": key, "count": count} for key, count in counter.most_common(limit)]


def file_record(root: pathlib.Path, path: pathlib.Path, *, include_words: bool = False) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    row: dict[str, Any] = {"path": rel, "bytes": path.stat().st_size}
    if include_words:
        row["words"] = count_words(path)
    return row


def ledger_counts(root: pathlib.Path) -> dict[str, Any]:
    specs = {
        "FOLLOWTHROUGH-QUEUE.json": "state",
        "ASSUMPTION-LEDGER.json": "state",
        "OBLIGATION-LEDGER.json": "state",
        "RETROSPECTIVE-QUEUE.json": "state",
        "RESOLUTION-LEDGER.json": "state",
        "APPLICABILITY-LEDGER.json": "state",
        "FIREBREAK-LEDGER.json": "state",
        "FOREIGN-PRESSURE-LEDGER.json": "state",
    }
    rows: dict[str, Any] = {}
    for rel, key in specs.items():
        data = load_json(root, rel)
        items = data.get("items", [])
        by_state = Counter(str(item.get(key)) for item in items)
        rows[rel] = {
            "items": len(items),
            "state_counts": dict(sorted(by_state.items())),
            "latest_id": items[-1].get("id") if items else None,
        }
    return rows


def short_contract_checkers(root: pathlib.Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / "tools").glob("check_*_contract.py")):
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "nonblank_noncomment_lines": len(lines),
        })
    return sorted(rows, key=lambda row: (row["nonblank_noncomment_lines"], row["bytes"], row["path"]))[:25]


def declarative_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    batch = root / "tools" / "check_declarative_witness_contract_batch.py"
    if not batch.exists():
        return {"state": "absent", "checker": "tools/check_declarative_witness_contract_batch.py", "contract_count": 0}
    text = batch.read_text(encoding="utf-8")
    contracts = re.findall(r'^    "([a-z0-9_]+_contract)",$', text, re.M)
    return {
        "state": "present",
        "checker": "tools/check_declarative_witness_contract_batch.py",
        "contract_count": len(contracts),
        "preserved_contracts": contracts,
        "removed_wrapper_policy": "one tiny wrapper per declarative witness contract was replaced by this batch checker; packet specs remain in tools/packet_contract_common.py",
    }


def shadow_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    batch = root / "tools" / "check_shadow_batch_contract.py"
    common = root / "tools" / "shadow_contract_common.py"
    if not batch.exists() or not common.exists():
        return {"state": "absent", "checker": "tools/check_shadow_batch_contract.py", "contract_count": 0}
    text = common.read_text(encoding="utf-8")
    kinds = re.findall(r"'kind': '([^']+)'", text)
    return {
        "state": "present",
        "checker": "tools/check_shadow_batch_contract.py",
        "support_module": "tools/shadow_contract_common.py",
        "contract_count": len(kinds),
        "preserved_contracts": kinds,
        "removed_wrapper_policy": "bespoke-looking shadow wrapper files were converted into explicit data specs plus one batch checker; each failing shadow kind remains named by require_shadow_contract",
    }


def hot_surface_compaction(root: pathlib.Path) -> dict[str, Any]:
    receipt = root / "HOT-SURFACE-COMPACTION.json"
    if not receipt.exists():
        return {"state": "absent", "surface": "HOT-SURFACE-COMPACTION.json", "target_count": 0}
    data = json.loads(receipt.read_text(encoding="utf-8"))
    totals = data.get("totals", {})
    return {
        "state": data.get("state", "present"),
        "surface": "HOT-SURFACE-COMPACTION.json",
        "checker": "tools/check_hot_surface_compaction_contract.py",
        "source_bundle": data.get("source_bundle"),
        "target_count": len(data.get("targets", [])),
        "original_markdown_words": totals.get("original_markdown_words"),
        "compacted_markdown_words": totals.get("compacted_markdown_words"),
        "word_delta": totals.get("word_delta"),
        "policy": "hot markdown surfaces are compacted only with lossless full-source retention and an explicit non-authority boundary",
    }



def gpustorming_late_search_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_gpustorming_late_search_family_batch_contract.py"
    helper = root / "tools" / "gpustorming_contract_lib.py"
    if not checker.exists() or not helper.exists():
        return {"state": "absent", "checker": "tools/check_gpustorming_late_search_family_batch_contract.py", "contract_count": 0}
    from gpustorming_contract_lib import late_search_surface_families
    families = late_search_surface_families()
    return {
        "state": "present",
        "checker": "tools/check_gpustorming_late_search_family_batch_contract.py",
        "support_module": "tools/gpustorming_contract_lib.py",
        "contract_count": len(families),
        "preserved_contracts": families,
        "removed_wrapper_policy": "late-search GPustorming family wrappers are checked through one batch checker while per-family diagnostics remain named",
    }

def hot_surface_source_roundtrip(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_hot_surface_source_roundtrip_contract.py"
    helper = root / "tools" / "hot_surface_compaction_lib.py"
    if not checker.exists() or not helper.exists():
        return {"state": "absent", "checker": "tools/check_hot_surface_source_roundtrip_contract.py"}
    receipt = root / "HOT-SURFACE-COMPACTION.json"
    source = root / "HOT-SURFACE-COMPACTION-ORIGINALS.json"
    return {
        "state": "present",
        "checker": "tools/check_hot_surface_source_roundtrip_contract.py",
        "helper": "tools/hot_surface_compaction_lib.py",
        "receipt": "HOT-SURFACE-COMPACTION.json",
        "source_bundle": "HOT-SURFACE-COMPACTION-ORIGINALS.json",
        "target_count": len(json.loads(receipt.read_text(encoding="utf-8")).get("targets", [])) if receipt.exists() else 0,
        "policy": "source-bundle retention must restore exact pre-compaction markdown texts in a temporary tree; compacted surfaces are not semantic substitutes",
    }


def ledger_debt_guard(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_ledger_debt_guard.py"
    if not checker.exists():
        return {"state": "absent", "checker": "tools/check_ledger_debt_guard.py"}
    ledger_items = {
        rel: load_json(root, rel).get("items", []) for rel in LEDGER_DEBT_POLICIES
    }
    current_revision = load_json(root, "REVISION-RECEIPT.json")["revision"]
    rows = []
    all_admissible = True
    mirror_mismatches: dict[str, list[dict[str, str]]] = {}
    for rel, policy in LEDGER_DEBT_POLICIES.items():
        items = ledger_items[rel]
        snapshot = live_debt_snapshot(items, policy, current_revision)
        rows.append({
            "surface": rel,
            "live_state": policy["live_state"],
            "live_count": snapshot["live_count"],
            "budget": policy["budget"],
            "minimum_headroom": snapshot["minimum_headroom"],
            "admission_limit": snapshot["admission_limit"],
            "headroom": snapshot["headroom"],
            "within_budget": snapshot["live_count"] <= policy["budget"],
            "reserve_satisfied": not snapshot["reserve_breached"],
        })
        all_admissible = all_admissible and not snapshot["reserve_breached"]
        mirror_mismatches[rel] = state_mirror_mismatches(items, policy)
    orphaned_retrospectives = live_retrospectives_with_nonlive_obligations(
        ledger_items["RETROSPECTIVE-QUEUE.json"],
        ledger_items["OBLIGATION-LEDGER.json"],
    )
    consistency_clean = not any(mirror_mismatches.values()) and not orphaned_retrospectives
    return {
        "state": (
            "present-budget-and-consistency-enforced"
            if all_admissible and consistency_clean
            else "present-needs-ledger-repair"
        ),
        "checker": "tools/check_ledger_debt_guard.py",
        "rows": rows,
        "state_mirror_mismatch_count": sum(len(rows) for rows in mirror_mismatches.values()),
        "live_retrospective_nonlive_obligation_count": len(orphaned_retrospectives),
        "policy_source": "tools/ledger_debt_policy_lib.py",
        "policy": "each live ledger must preserve its configured admission reserve before a new tail is added; old non-latest rows may be transitioned only with revision-named reasons; present compatibility state mirrors must agree with canonical state, and a cooling retrospective cannot outlive its paired same-origin obligation",
    }



def ledger_coldstore_roundtrip(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_ledger_coldstore_roundtrip_contract.py"
    canary_checker = root / "tools" / "check_ledger_coldstore_mutation_canaries.py"
    helper = root / "tools" / "ledger_coldstore_contract_lib.py"
    coldstore = root / "LEDGER-COLDSTORE.json"
    if not checker.exists() or not coldstore.exists():
        return {"state": "absent", "checker": "tools/check_ledger_coldstore_roundtrip_contract.py"}
    data = json.loads(coldstore.read_text(encoding="utf-8"))
    cold_rows = int(data.get("cold_row_count", 0) or 0)
    saved = int(data.get("net_plaintext_saved_bytes", 0) or 0)
    mutation_guarded = canary_checker.exists() and helper.exists()
    return {
        "state": "present-roundtrip-and-mutation-guarded" if cold_rows >= 1000 and saved > 0 and mutation_guarded else "present-needs-review",
        "checker": "tools/check_ledger_coldstore_roundtrip_contract.py",
        "mutation_checker": "tools/check_ledger_coldstore_mutation_canaries.py" if canary_checker.exists() else None,
        "support_module": "tools/ledger_coldstore_contract_lib.py" if helper.exists() else None,
        "surface": "LEDGER-COLDSTORE.json",
        "cold_row_count": cold_rows,
        "governed_ledger_count": len(data.get("stats", []) or []),
        "hot_ledger_before_bytes": data.get("hot_ledger_before_bytes"),
        "hot_ledger_after_bytes": data.get("hot_ledger_after_bytes"),
        "coldstore_bytes": data.get("coldstore_bytes"),
        "net_plaintext_saved_bytes": saved,
        "compaction_revision": data.get("compaction_revision"),
        "policy": "historical rows may leave the hot path only when the coldstore restores exact canonical rows, mutation canaries fail locally, and current tails stay hot",
    }



def receipt_coldstore_roundtrip(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_receipt_coldstore_roundtrip_contract.py"
    canary_checker = root / "tools" / "check_receipt_coldstore_mutation_canaries.py"
    helper = root / "tools" / "receipt_coldstore_contract_lib.py"
    coldstore = root / "RECEIPT-COLDSTORE.json"
    if not checker.exists() or not coldstore.exists():
        return {"state": "absent", "checker": "tools/check_receipt_coldstore_roundtrip_contract.py"}
    data = json.loads(coldstore.read_text(encoding="utf-8"))
    cold_keys = int(data.get("cold_key_count", 0) or 0)
    saved = int(data.get("net_plaintext_saved_bytes", 0) or 0)
    mutation_guarded = canary_checker.exists() and helper.exists()
    return {
        "state": "present-roundtrip-and-mutation-guarded" if cold_keys >= 100 and saved > 0 and mutation_guarded else "present-needs-review",
        "checker": "tools/check_receipt_coldstore_roundtrip_contract.py",
        "mutation_checker": "tools/check_receipt_coldstore_mutation_canaries.py" if canary_checker.exists() else None,
        "support_module": "tools/receipt_coldstore_contract_lib.py" if helper.exists() else None,
        "surface": "RECEIPT-COLDSTORE.json",
        "cold_key_count": cold_keys,
        "hot_receipt_before_bytes": data.get("hot_receipt_before_bytes"),
        "hot_receipt_after_bytes": data.get("hot_receipt_after_bytes"),
        "coldstore_bytes": data.get("coldstore_bytes"),
        "net_plaintext_saved_bytes": saved,
        "compaction_revision": data.get("compaction_revision"),
        "policy": "historical receipt witness fields may leave REVISION-RECEIPT only when exact restoration, mutation canaries, and current-key exclusion are checked",
    }




def spec_part_metrics(root: pathlib.Path, part_paths: list[str]) -> dict[str, Any]:
    rows = []
    for rel in part_paths:
        path = root / rel
        rows.append({
            "path": rel,
            "bytes": path.stat().st_size if path.exists() else 0,
            "exists": path.exists(),
        })
    return {
        "part_count": len(part_paths),
        "max_part_bytes": max((row["bytes"] for row in rows), default=0),
        "parts": rows,
    }


def gpu_witness_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_gpu_witness_batch_contract.py"
    specs = root / "tools" / "gpu_witness_contract_specs.py"
    if not checker.exists() or not specs.exists():
        return {"state": "absent", "checker": "tools/check_gpu_witness_batch_contract.py", "contract_count": 0}
    from gpu_witness_contract_specs import GPU_WITNESS_CONTRACT_SPEC_PARTS, GPU_WITNESS_CONTRACT_SPECS
    sources = [row.get("source_checker") for row in GPU_WITNESS_CONTRACT_SPECS]
    missing_sources = [source for source in sources if (root / "tools" / str(source)).exists()]
    part_metrics = spec_part_metrics(root, GPU_WITNESS_CONTRACT_SPEC_PARTS)
    return {
        "state": "present-segmented",
        "checker": "tools/check_gpu_witness_batch_contract.py",
        "spec_module": "tools/gpu_witness_contract_specs.py",
        "spec_parts": GPU_WITNESS_CONTRACT_SPEC_PARTS,
        "spec_part_metrics": part_metrics,
        "contract_count": len(GPU_WITNESS_CONTRACT_SPECS),
        "former_wrapper_count": len(sources),
        "former_wrappers_still_present": missing_sources,
        "removed_wrapper_policy": "GPU replay / reopened-residue / post-arbitration witness wrappers are checked through one batch checker with exact per-contract specs, locality-sized spec segments, and historical source-checker needles retained as audit data",
    }


def gpustorming_standard_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_gpustorming_standard_family_batch_contract.py"
    specs = root / "tools" / "gpustorming_standard_contract_specs.py"
    if not checker.exists() or not specs.exists():
        return {"state": "absent", "checker": "tools/check_gpustorming_standard_family_batch_contract.py", "contract_count": 0}
    from gpustorming_standard_contract_specs import GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS, GPUSTORMING_STANDARD_CONTRACT_SPECS
    sources = [row.get("source_checker") for row in GPUSTORMING_STANDARD_CONTRACT_SPECS]
    still_present = [source for source in sources if (root / "tools" / str(source)).exists()]
    source_payload_rows = [row.get("source_checker") for row in GPUSTORMING_STANDARD_CONTRACT_SPECS if "source" in row]
    modes = Counter(str(row.get("mode")) for row in GPUSTORMING_STANDARD_CONTRACT_SPECS)
    part_metrics = spec_part_metrics(root, GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS)
    return {
        "state": "present-segmented-no-exec",
        "checker": "tools/check_gpustorming_standard_family_batch_contract.py",
        "spec_module": "tools/gpustorming_standard_contract_specs.py",
        "spec_parts": GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS,
        "spec_part_metrics": part_metrics,
        "contract_count": len(GPUSTORMING_STANDARD_CONTRACT_SPECS),
        "former_wrapper_count": len(sources),
        "former_wrappers_still_present": still_present,
        "source_payload_rows": source_payload_rows,
        "mode_counts": dict(sorted(modes.items())),
        "removed_wrapper_policy": "standard GPustorming family wrappers are checked through one batch checker with declarative needle/spec maps, locality-sized spec segments, no stored source payloads, and named diagnostics",
    }



def method_doc_ratchet_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_method_doc_ratchet_batch_contract.py"
    specs = root / "tools" / "method_doc_ratchet_contract_specs.py"
    if not checker.exists() or not specs.exists():
        return {"state": "absent", "checker": "tools/check_method_doc_ratchet_batch_contract.py", "contract_count": 0}
    from method_doc_ratchet_contract_specs import METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS, METHOD_DOC_RATCHET_CONTRACT_SPECS
    sources = [row.get("source_checker") for row in METHOD_DOC_RATCHET_CONTRACT_SPECS]
    still_present = [source for source in sources if (root / "tools" / str(source)).exists()]
    part_metrics = spec_part_metrics(root, METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS)
    return {
        "state": "present-segmented",
        "checker": "tools/check_method_doc_ratchet_batch_contract.py",
        "spec_module": "tools/method_doc_ratchet_contract_specs.py",
        "spec_parts": METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS,
        "spec_part_metrics": part_metrics,
        "contract_count": len(METHOD_DOC_RATCHET_CONTRACT_SPECS),
        "former_wrapper_count": len(sources),
        "former_wrappers_still_present": still_present,
        "removed_wrapper_policy": "homogeneous method-doc prompt/runbook ratchet wrappers are checked through one segmented batch checker; each former source checker still has segment-local diagnostics and no wrapper-regrowth-by-alias",
    }

def core_method_batch_refactor(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_core_method_batch_contract.py"
    specs = root / "tools" / "core_method_contract_specs.py"
    if not checker.exists() or not specs.exists():
        return {"state": "absent", "checker": "tools/check_core_method_batch_contract.py", "contract_count": 0}
    from core_method_contract_specs import CORE_METHOD_CONTRACT_SPEC_PARTS, CORE_METHOD_CONTRACT_SPECS
    sources = [row.get("source_checker") for row in CORE_METHOD_CONTRACT_SPECS]
    still_present = [source for source in sources if (root / "tools" / str(source)).exists()]
    part_metrics = spec_part_metrics(root, CORE_METHOD_CONTRACT_SPEC_PARTS)
    return {
        "state": "present-segmented-semantic-guarded",
        "checker": "tools/check_core_method_batch_contract.py",
        "spec_module": "tools/core_method_contract_specs.py",
        "spec_parts": CORE_METHOD_CONTRACT_SPEC_PARTS,
        "spec_part_metrics": part_metrics,
        "contract_count": len(CORE_METHOD_CONTRACT_SPECS),
        "former_wrapper_count": len(sources),
        "former_wrappers_still_present": still_present,
        "removed_wrapper_policy": "simple core method/state wrappers are checked through one segmented batch checker with exact source-checker diagnostics, bounded needle rows, auxiliary-surface checks, and source documents retained as semantic surfaces",
    }



def priority_zero_burden_gate(root: pathlib.Path) -> dict[str, Any]:
    fixture = root / "assays/priority-zero-burden-gate-2026-06-15.json"
    checker = root / "tools/check_priority_zero_burden_gate_contract.py"
    if not fixture.exists() or not checker.exists():
        return {"state": "absent", "surface": "assays/priority-zero-burden-gate-2026-06-15.json", "checker": "tools/check_priority_zero_burden_gate_contract.py"}
    data = json.loads(fixture.read_text(encoding="utf-8"))
    hot = data.get("hot_cue_gate", {})
    decisions = data.get("decisions", [])
    return {
        "state": "present-hot-cue-gated",
        "surface": "assays/priority-zero-burden-gate-2026-06-15.json",
        "checker": "tools/check_priority_zero_burden_gate_contract.py",
        "method_surface": "docs/40-session/priority-zero-burden-gate-audit-2026-06-15.md",
        "based_on_assay": data.get("based_on_assay"),
        "before_current_additions_count": hot.get("before_current_additions_count"),
        "after_current_additions_count": hot.get("after_current_additions_count"),
        "decision_count": len(decisions),
        "queued_successor": data.get("next_open_question"),
        "policy": "first smoke-slice evidence may gate default hot cues and trigger a rotated follow-up, but it is not deletion authority or a review court",
    }


def generated_surface_drift_gate(root: pathlib.Path) -> dict[str, Any]:
    checker = root / "tools" / "check_generated_surface_drift.py"
    orchestrator = root / "tools" / "gen_all_generated_surfaces.py"
    helper = root / "tools" / "generated_surface_lib.py"
    if not checker.exists() or not orchestrator.exists() or not helper.exists():
        return {"state": "absent", "checker": "tools/check_generated_surface_drift.py", "generator_tools_in_lint": None}
    tools = build_validation_toolchain(root)
    gen_tools = [name for name in tools if name.startswith("gen_")]
    return {
        "state": "present-temporary-copy-read-only-target",
        "checker": "tools/check_generated_surface_drift.py",
        "orchestrator": "tools/gen_all_generated_surfaces.py",
        "helper": "tools/generated_surface_lib.py",
        "generator_tools_in_lint": gen_tools,
        "lint_tool_count": len(tools),
        "policy": "make lint snapshots target generated surfaces, regenerates only in a temporary release-tree copy, compares bytes, and removes the copy; stale generated evidence fails without repairing the judged tree",
    }



def release_integrity_refactor(root: pathlib.Path) -> dict[str, Any]:
    helper = root / "tools" / "release_integrity_contract_lib.py"
    checker = root / "tools" / "check_release_integrity_contract.py"
    canary = root / "tools" / "check_release_integrity_negative_canaries.py"
    source = root / "tools" / "release_integrity_lib.py"
    if not helper.exists() or not checker.exists() or not canary.exists():
        return {"state": "absent", "helper": "tools/release_integrity_contract_lib.py", "checker": "tools/check_release_integrity_contract.py", "negative_canary_checker": "tools/check_release_integrity_negative_canaries.py"}
    rows = rows_from_canary_runs(root, "release_integrity_rows")
    failures = canary_failure_count(rows)
    helper_text = helper.read_text(encoding="utf-8")
    return {
        "state": "present-manifest-checksum-provenance-mutation-gated" if failures == 0 else "present-needs-repair",
        "helper": "tools/release_integrity_contract_lib.py",
        "source_helper": "tools/release_integrity_lib.py",
        "checker": "tools/check_release_integrity_contract.py",
        "negative_canary_checker": "tools/check_release_integrity_negative_canaries.py",
        "canary_count": len(rows),
        "canary_failures": failures,
        "validated_surfaces": ["FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json", "RELEASE-MANIFEST.json"],
        "strict_checks": [
            "file content hashes",
            "checksum text format and path order",
            "manifest path_count",
            "provenance command",
            "provenance self-reference policy",
        ],
        "independent_parser_present": "validate_checksums_text" in helper_text and "validate_release_provenance" in helper_text,
        "policy": "release integrity validation is helper-local and mutation-tested; archive economy reuses CANARY-RUNS rows instead of re-running mutation canaries during generated-surface drift checks, so the audit stays low-cost and non-authoritative",
    }


def package_release_preflight(root: pathlib.Path) -> dict[str, Any]:
    package = root / "tools" / "package_release.py"
    helper = root / "tools" / "package_preflight_lib.py"
    checker = root / "tools" / "check_package_release_preflight_contract.py"
    if not package.exists() or not helper.exists() or not checker.exists():
        return {"state": "absent", "package_release": "tools/package_release.py", "helper": "tools/package_preflight_lib.py", "checker": "tools/check_package_release_preflight_contract.py"}
    package_text = package.read_text(encoding="utf-8")
    helper_text = helper.read_text(encoding="utf-8")
    try:
        refresh_at = package_text.rindex("refresh_generated_surfaces(ROOT, include_release_integrity=True)")
        preflight_at = package_text.index("run_lint_preflight(ROOT)")
        zip_at = package_text.index("write_deterministic_zip(ROOT, bundle_path, bundle_name)")
        smoke_at = package_text.index("run_artifact_smoke(ROOT, bundle_path, bundle_name)")
        sidecar_at = package_text.index("write_verified_sha256_sidecar(bundle_path, sidecar, bundle_name)")
        order = "refresh-preflight-zip-artifact-smoke-verified-sidecar" if refresh_at < preflight_at < zip_at < smoke_at < sidecar_at else "misordered"
    except ValueError:
        order = "missing-call"
    smoke_helper = all(needle in helper_text for needle in ["validate_zip_member_set", "extract_zip_safely", "run_lint_preflight(extract_root)"])
    mutation_helper = "package_artifact_negative_canary_results" in helper_text and (root / "tools" / "check_package_artifact_smoke_negative_canaries.py").exists()
    determinism_helper = "package_determinism_canary_results" in helper_text and (root / "tools" / "check_package_deterministic_zip_canaries.py").exists()
    sidecar_helper = "package_sidecar_canary_results" in helper_text and "write_verified_sha256_sidecar" in helper_text and (root / "tools" / "check_package_sidecar_canaries.py").exists()
    identity_helper = "release_identity_canary_results" in (root / "tools" / "release_hygiene_lib.py").read_text(encoding="utf-8") and (root / "tools" / "check_release_identity_canaries.py").exists()
    artifact_rows = package_artifact_rows_from_canary_runs(root) if mutation_helper else []
    determinism_rows = rows_from_canary_runs(root, "deterministic_writer_rows") if determinism_helper else []
    sidecar_rows = rows_from_canary_runs(root, "sidecar_rows") if sidecar_helper else []
    mutation_count = len(artifact_rows)
    mutation_failures = canary_failure_count(artifact_rows) if mutation_helper else None
    determinism_count = len(determinism_rows)
    determinism_failures = canary_failure_count(determinism_rows) if determinism_helper else None
    sidecar_count = len(sidecar_rows)
    sidecar_failures = canary_failure_count(sidecar_rows) if sidecar_helper else None
    return {
        "state": "present-admission-artifact-mutation-determinism-sidecar-and-name-gated" if order == "refresh-preflight-zip-artifact-smoke-verified-sidecar" and smoke_helper and mutation_helper and mutation_failures == 0 and determinism_helper and determinism_failures == 0 and sidecar_helper and sidecar_failures == 0 and identity_helper else "present-needs-repair",
        "package_release": "tools/package_release.py",
        "helper": "tools/package_preflight_lib.py",
        "checker": "tools/check_package_release_preflight_contract.py",
        "negative_canary_checker": "tools/check_package_artifact_smoke_negative_canaries.py",
        "determinism_canary_checker": "tools/check_package_deterministic_zip_canaries.py",
        "sidecar_canary_checker": "tools/check_package_sidecar_canaries.py",
        "release_identity_canary_checker": "tools/check_release_identity_canaries.py",
        "release_identity_helper": "tools/release_hygiene_lib.py#validate_release_identity",
        "order": order,
        "artifact_smoke_helper": smoke_helper,
        "mutation_canary_count": mutation_count,
        "mutation_canary_failures": mutation_failures,
        "determinism_canary_count": determinism_count,
        "determinism_canary_failures": determinism_failures,
        "sidecar_canary_count": sidecar_count,
        "sidecar_canary_failures": sidecar_failures,
        "release_identity_canaries_present": identity_helper,
        "safe_extract_independent": "safe_zip_member_target" in helper_text and "extract_zip_safely" in helper_text,
        "writer_helper": "write_deterministic_zip" in helper_text and "FIXED_ZIP_DT" in helper_text and "FIXED_EXTERNAL_ATTR" in helper_text,
        "sidecar_helper": "write_verified_sha256_sidecar" in helper_text and "verify_sha256_sidecar" in helper_text,
        "policy": "direct make package-release must refresh generated surfaces, pass non-mutating lint, emit the zip, prove the zip member set and a clean-extraction lint, then write and verify the SHA256 sidecar; archive economy reads CANARY-RUNS rows for mutation counts instead of re-running those canaries while generated-drift checks are copying temporary trees",
    }

def path_alias_batch_groups(root: pathlib.Path) -> dict[str, Any]:
    path = root / "PATH-ALIAS-LEDGER.json"
    if not path.exists():
        return {"state": "absent", "checker": "tools/check_path_alias_ledger_contract.py", "group_count": 0, "source_count": 0}
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = data.get("batch_alias_groups", [])
    source_count = sum(int(group.get("source_count", 0)) for group in groups if isinstance(group, dict))
    return {
        "state": "present" if groups else "absent",
        "surface": "PATH-ALIAS-LEDGER.json",
        "checker": "tools/check_path_alias_ledger_contract.py",
        "group_count": len(groups),
        "source_count": source_count,
        "policy": "batch alias groups retain retired checker-path provenance without wrapper-regrowth-by-alias or redirect authority",
    }

def build_archive_economy_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_json(root, "REVISION-RECEIPT.json")
    paths = release_economy_paths(root)
    suffix_counts: Counter[str] = Counter()
    suffix_bytes: defaultdict[str, int] = defaultdict(int)
    top_dirs: Counter[str] = Counter()
    path_lengths: list[int] = []
    markdown_records: list[dict[str, Any]] = []
    py_records: list[dict[str, Any]] = []

    for path in paths:
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower() or "[no suffix]"
        suffix_counts[suffix] += 1
        suffix_bytes[suffix] += path.stat().st_size
        top_dirs[rel.split("/", 1)[0] if "/" in rel else "."] += 1
        path_lengths.append(len(rel))
        if suffix == ".md":
            markdown_records.append(file_record(root, path, include_words=True))
        if suffix == ".py":
            py_records.append(file_record(root, path))

    total_bytes = sum(path.stat().st_size for path in paths)
    markdown_words = sum(row.get("words", 0) for row in markdown_records)
    tools = build_validation_toolchain(root)
    check_tools = [name for name in tools if name.startswith("check_")]
    generator_tools = sorted(pathlib.Path(script).name for script in GENERATOR_SCRIPTS)
    support_modules = sorted(path.name for path in (root / "tools").glob("*_lib.py"))
    checker_files = sorted(path.name for path in (root / "tools").glob("check_*.py"))
    contract_checkers = sorted(path.name for path in (root / "tools").glob("check_*_contract.py"))

    largest_files = sorted((file_record(root, path) for path in paths), key=lambda row: row["bytes"], reverse=True)[:25]
    largest_markdown = sorted(markdown_records, key=lambda row: row.get("words", 0), reverse=True)[:20]
    largest_python = sorted(py_records, key=lambda row: row["bytes"], reverse=True)[:20]
    long_paths = sorted((file_record(root, path) | {"path_length": len(path.relative_to(root).as_posix())} for path in paths), key=lambda row: row["path_length"], reverse=True)[:20]

    risk_flags = []
    if len(paths) > 700:
        risk_flags.append({"id": "AE-RISK-0001", "trigger": "release_file_count_gt_700", "value": len(paths), "repair": "compact or consolidate low-signal witness/checker surfaces before adding new families"})
    if markdown_words > 500_000:
        risk_flags.append({"id": "AE-RISK-0002", "trigger": "markdown_words_gt_500k", "value": markdown_words, "repair": "prefer deltas, generated indexes, and retired-history summaries over new long prose"})
    live_debt = {}
    for rel, policy in LEDGER_DEBT_POLICIES.items():
        items = load_json(root, rel).get("items", [])
        snapshot = live_debt_snapshot(items if isinstance(items, list) else [], policy, receipt["revision"])
        live_debt[rel] = snapshot
        if snapshot["reserve_breached"]:
            risk_flags.append({
                "id": policy["risk_id"],
                "trigger": policy["risk_label"],
                "value": snapshot["live_count"],
                "budget": snapshot["budget"],
                "minimum_headroom": snapshot["minimum_headroom"],
                "admission_limit": snapshot["admission_limit"],
                "headroom": snapshot["headroom"],
                "oldest_live_id": snapshot["oldest_live_id"],
                "oldest_live_revision": snapshot["oldest_live_revision"],
                "oldest_live_age_revisions": snapshot["oldest_live_age_revisions"],
                "repair": policy["repair"],
            })
    if len(checker_files) > 350:
        risk_flags.append({"id": "AE-RISK-0004", "trigger": "checker_files_gt_350", "value": len(checker_files), "repair": "move near-declarative contract checks into registry data plus shared generic checkers"})
    if max(path_lengths or [0]) > 180:
        risk_flags.append({"id": "AE-RISK-0005", "trigger": "path_length_gt_180", "value": max(path_lengths), "repair": "cap new surface slugs and retire path-expansion patterns"})

    return {
        "project": "DelayBasin",
        "revision": receipt["revision"],
        "surface": "ARCHIVE-ECONOMY-AUDIT.json",
        "guide_surface": "docs/00-meta/archive-economy-audit.md",
        "state": "generated-archive-economy-audit",
        "generated_from": [
            "REVISION-RECEIPT.json",
            "RELEASE-MANIFEST.json",
            "tools/archive_economy_audit_lib.py",
            "tools/ledger_debt_policy_lib.py",
            "tools/release_hygiene_lib.py",
            "tools/validation_toolchain_lib.py",
            "release paths excluding frozen bundles and self-reference surfaces",
        ],
        "scope": {
            "included": "release-hygiene paths in the current checkout",
            "excluded": sorted(ECONOMY_EXCLUDED_SURFACES),
            "reason": "self-referential audit and release-integrity files are excluded so the economy audit is stable across generator/release-integrity order",
        },
        "counts": {
            "release_economy_files": len(paths),
            "release_economy_bytes": total_bytes,
            "markdown_files": len(markdown_records),
            "markdown_words": markdown_words,
            "python_files": len(py_records),
            "validation_tool_count": len(tools),
            "checker_file_count": len(checker_files),
            "contract_checker_file_count": len(contract_checkers),
            "generator_tool_count": len(generator_tools),
            "support_module_count": len(support_modules),
            "max_path_length": max(path_lengths or [0]),
        },
        "live_debt": live_debt,
        "suffix_counts": top_counter(suffix_counts, 16),
        "suffix_bytes": [{"key": key, "bytes": value} for key, value in sorted(suffix_bytes.items(), key=lambda kv: kv[1], reverse=True)[:16]],
        "top_level_file_counts": top_counter(top_dirs, 12),
        "largest_files": largest_files,
        "largest_markdown_by_words": largest_markdown,
        "largest_python_by_bytes": largest_python,
        "longest_paths": long_paths,
        "ledger_counts": ledger_counts(root),
        "checker_consolidation_candidates": short_contract_checkers(root),
        "completed_refactors": {
            "declarative_witness_contract_batch": declarative_batch_refactor(root),
            "shadow_contract_batch": shadow_batch_refactor(root),
            "hot_surface_compaction": hot_surface_compaction(root),
            "hot_surface_source_roundtrip": hot_surface_source_roundtrip(root),
            "ledger_debt_guard": ledger_debt_guard(root),
            "ledger_coldstore_roundtrip": ledger_coldstore_roundtrip(root),
            "receipt_coldstore_roundtrip": receipt_coldstore_roundtrip(root),
            "gpustorming_late_search_batch": gpustorming_late_search_batch_refactor(root),
            "gpustorming_standard_batch": gpustorming_standard_batch_refactor(root),
            "gpu_witness_batch": gpu_witness_batch_refactor(root),
            "method_doc_ratchet_batch": method_doc_ratchet_batch_refactor(root),
            "core_method_batch": core_method_batch_refactor(root),
            "path_alias_batch_groups": path_alias_batch_groups(root),
            "generated_surface_drift_gate": generated_surface_drift_gate(root),
            "release_integrity_refactor": release_integrity_refactor(root),
            "package_release_preflight": package_release_preflight(root),
            "priority_zero_burden_gate": priority_zero_burden_gate(root),
        },
        "release_hygiene_root_relative_regression": {
            "checker": "tools/check_release_hygiene_relative_root.py",
            "patched_helper": "tools/release_hygiene_lib.py#release_relative_parts",
            "failure_prevented": "absolute parent directory named like DelayBasin-rev#### no longer causes every release file to be skipped",
        },
        "risk_flags": risk_flags,
        "next_actions": [
            "keep release-hygiene root-relative regression in the admission suite",
            "keep declarative, shadow, GPU, and GPustorming batch checkers diagnostic enough to name the failing contract kind",
            "keep batch-spec segments locality-sized, index-derived only from part rows, and standard GPustorming specs free of stored executable source payloads",
            "keep method-doc and core-method batch specs as bounded validation needles only, never semantic substitutes for source method documents",
            "keep generated-surface drift checks before the validation suite so make lint cannot repair stale generated evidence while passing",
            "keep package release admission- and artifact-gated so direct package-release calls cannot emit or hash a zip that fails clean extraction",
            "keep release-integrity canaries cheap and manifest/checksum/provenance-local so they catch hash drift without becoming a bundle-notary layer",
            "keep artifact-smoke mutation canaries cheap and synthetic so the smoke gate does not become clean-extraction ceremony",
            "keep hot-surface source-bundle round-trip checks in the admission suite before treating compact markdown as reentry evidence",
            "burn down active-assumption/open-obligation/cooling-retrospective sediment before adding new continuity debt",
            "keep ledger-debt budgets executable so sediment repair cannot regress into report-only doctrine",
            "keep ledger coldstores round-trip checked, current-tail-hot, and non-authoritative before further hot ledger trimming",
            "keep receipt coldstore restoration and current-key exclusion checked before trimming more receipt witness mass",
            "burn down or compress long prose before adding new doctrine surfaces",
        ],
        "explicit_non_claim": "Archive economy metrics are triage evidence only: not a deletion court, quality score, completeness proof, semantic authority, or permission to remove governing surfaces without ordinary review.",
    }


def render_archive_economy_markdown(audit: dict[str, Any]) -> str:
    c = audit["counts"]
    lines = [
        "# Archive economy audit",
        "",
        "This generated audit measures release-path mass, checker sprawl, large prose surfaces, path-length pressure, and queue sediment.",
        "It exists to make the next deletion/refactor move concrete instead of adding another abstract governance layer.",
        "",
        "## Counts",
        "",
        f"- Release-economy files: `{c['release_economy_files']}`",
        f"- Release-economy bytes: `{c['release_economy_bytes']}`",
        f"- Markdown files / words: `{c['markdown_files']}` / `{c['markdown_words']}`",
        f"- Python files: `{c['python_files']}`",
        f"- Validation tools: `{c['validation_tool_count']}`",
        f"- Checker files / contract checkers: `{c['checker_file_count']}` / `{c['contract_checker_file_count']}`",
        f"- Generator tools: `{c['generator_tool_count']}`",
        f"- Max path length: `{c['max_path_length']}`",
        "",
        "## Risk flags",
    ]
    if audit["risk_flags"]:
        for row in audit["risk_flags"]:
            lines.append(f"- `{row['id']}` — `{row['trigger']}` = `{row['value']}`; repair: {row['repair']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Largest files"])
    for row in audit["largest_files"][:12]:
        lines.append(f"- `{row['path']}` — `{row['bytes']}` bytes")
    lines.extend(["", "## Largest markdown by words"])
    for row in audit["largest_markdown_by_words"][:12]:
        lines.append(f"- `{row['path']}` — `{row['words']}` words")
    refactors = audit.get("completed_refactors", {})
    lines.extend(["", "## Completed refactors"])
    dec = refactors.get("declarative_witness_contract_batch", {})
    if dec.get("state") == "present":
        lines.append(f"- `{dec['checker']}` batches `{dec['contract_count']}` formerly one-file declarative witness contracts.")
    shadow = refactors.get("shadow_contract_batch", {})
    if shadow.get("state") == "present":
        lines.append(f"- `{shadow['checker']}` batches `{shadow['contract_count']}` formerly one-file shadow contract wrappers.")
    hot = refactors.get("hot_surface_compaction", {})
    if hot.get("state") != "absent":
        lines.append(f"- `{hot['surface']}` compacts `{hot['target_count']}` hot markdown surfaces with word delta `{hot['word_delta']}` and source bundle `{hot['source_bundle']}`.")
    roundtrip = refactors.get("hot_surface_source_roundtrip", {})
    if roundtrip.get("state") == "present":
        lines.append(f"- `{roundtrip['checker']}` restores `{roundtrip['target_count']}` pre-compaction targets from `{roundtrip['source_bundle']}` in a temporary tree.")
    debt_guard = refactors.get("ledger_debt_guard", {})
    if str(debt_guard.get("state", "")).startswith("present"):
        summary = ", ".join(
            f"{row['surface']} {row['live_state']}={row['live_count']}/{row['budget']} (headroom {row.get('headroom')})"
            for row in debt_guard.get("rows", [])
        )
        lines.append(
            f"- `{debt_guard['checker']}` enforces live-ledger budgets and cross-field/cohort consistency: "
            f"{summary}; mirror mismatches `{debt_guard.get('state_mirror_mismatch_count')}`, "
            f"orphaned cooling retrospectives `{debt_guard.get('live_retrospective_nonlive_obligation_count')}`."
        )
    coldstore = refactors.get("ledger_coldstore_roundtrip", {})
    if str(coldstore.get("state", "")).startswith("present"):
        lines.append(f"- `{coldstore['checker']}` verifies `{coldstore['cold_row_count']}` cold-stored historical ledger rows in `{coldstore['surface']}` with net plaintext savings `{coldstore['net_plaintext_saved_bytes']}` bytes.")
    receipt_coldstore = refactors.get("receipt_coldstore_roundtrip", {})
    if str(receipt_coldstore.get("state", "")).startswith("present"):
        lines.append(f"- `{receipt_coldstore['checker']}` verifies `{receipt_coldstore['cold_key_count']}` cold-stored historical receipt keys in `{receipt_coldstore['surface']}` with net plaintext savings `{receipt_coldstore['net_plaintext_saved_bytes']}` bytes.")
    gpustorming_batch = refactors.get("gpustorming_late_search_batch", {})
    if gpustorming_batch.get("state") == "present":
        lines.append(f"- `{gpustorming_batch['checker']}` batches `{gpustorming_batch['contract_count']}` late-search GPustorming family contracts.")
    standard_batch = refactors.get("gpustorming_standard_batch", {})
    if str(standard_batch.get("state", "")).startswith("present"):
        part_metrics = standard_batch.get("spec_part_metrics", {})
        lines.append(f"- `{standard_batch['checker']}` batches `{standard_batch['contract_count']}` standard GPustorming family contracts with no stored source payloads and `{part_metrics.get('part_count')}` spec parts; max part bytes `{part_metrics.get('max_part_bytes')}`.")
    gpu_batch = refactors.get("gpu_witness_batch", {})
    if str(gpu_batch.get("state", "")).startswith("present"):
        part_metrics = gpu_batch.get("spec_part_metrics", {})
        lines.append(f"- `{gpu_batch['checker']}` batches `{gpu_batch['contract_count']}` GPU witness contracts with `{part_metrics.get('part_count')}` spec parts; max part bytes `{part_metrics.get('max_part_bytes')}`.")
    method_batch = refactors.get("method_doc_ratchet_batch", {})
    if str(method_batch.get("state", "")).startswith("present"):
        part_metrics = method_batch.get("spec_part_metrics", {})
        lines.append(f"- `{method_batch['checker']}` batches `{method_batch['contract_count']}` method-doc prompt/runbook ratchet contracts with `{part_metrics.get('part_count')}` spec parts; max part bytes `{part_metrics.get('max_part_bytes')}`.")
    core_method_batch = refactors.get("core_method_batch", {})
    if str(core_method_batch.get("state", "")).startswith("present"):
        part_metrics = core_method_batch.get("spec_part_metrics", {})
        lines.append(f"- `{core_method_batch['checker']}` batches `{core_method_batch['contract_count']}` core method/state contracts with `{part_metrics.get('part_count')}` spec parts; max part bytes `{part_metrics.get('max_part_bytes')}`; source documents remain semantic surfaces.")
    alias_groups = refactors.get("path_alias_batch_groups", {})
    if alias_groups.get("state") == "present":
        lines.append(f"- `{alias_groups['surface']}` records `{alias_groups['group_count']}` batch alias groups covering `{alias_groups['source_count']}` former checker paths without wrapper regrowth.")
    release_integrity = refactors.get("release_integrity_refactor", {})
    if str(release_integrity.get("state", "")).startswith("present"):
        lines.append(f"- `{release_integrity['checker']}` now delegates to `{release_integrity['helper']}` and `{release_integrity['negative_canary_checker']}` covers `{release_integrity.get('canary_count')}` manifest/checksum/provenance mutations with failures `{release_integrity.get('canary_failures')}`.")
    package_preflight = refactors.get("package_release_preflight", {})
    if str(package_preflight.get("state", "")).startswith("present"):
        lines.append(f"- `{package_preflight['package_release']}` now runs `{package_preflight['helper']}` before deterministic zip emission and again on a clean extracted artifact before verified sidecar writing; order `{package_preflight.get('order')}`; mutation canaries `{package_preflight.get('mutation_canary_count')}` with failures `{package_preflight.get('mutation_canary_failures')}`; deterministic writer canaries `{package_preflight.get('determinism_canary_count')}` with failures `{package_preflight.get('determinism_canary_failures')}`; sidecar canaries `{package_preflight.get('sidecar_canary_count')}` with failures `{package_preflight.get('sidecar_canary_failures')}`.")
    burden_gate = refactors.get("priority_zero_burden_gate", {})
    if str(burden_gate.get("state", "")).startswith("present"):
        lines.append(f"- `{burden_gate['checker']}` checks `{burden_gate['surface']}`: hot Current additions `{burden_gate.get('before_current_additions_count')}` → `{burden_gate.get('after_current_additions_count')}`, decisions `{burden_gate.get('decision_count')}`, successor `{burden_gate.get('queued_successor')}`.")
    if not any(row.get("state") == "present" or row.get("state") not in {None, "absent"} for row in refactors.values()):
        lines.append("- none")
    lines.extend(["", "## Checker consolidation candidates"])
    for row in audit["checker_consolidation_candidates"][:12]:
        lines.append(f"- `{row['path']}` — `{row['nonblank_noncomment_lines']}` nonblank noncomment lines")
    lines.extend(["", "## Non-claim", "", audit["explicit_non_claim"]])
    return "\n".join(lines).rstrip() + "\n"


def write_archive_economy_audit(root: pathlib.Path) -> dict[str, Any]:
    audit = build_archive_economy_audit(root)
    (root / "ARCHIVE-ECONOMY-AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "docs/00-meta/archive-economy-audit.md").write_text(render_archive_economy_markdown(audit), encoding="utf-8")
    return audit

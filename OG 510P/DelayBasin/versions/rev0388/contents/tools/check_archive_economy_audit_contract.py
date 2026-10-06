import json
import pathlib

from archive_economy_audit_lib import build_archive_economy_audit
from ledger_debt_policy_lib import LEDGER_DEBT_POLICIES, live_debt_snapshot

ROOT = pathlib.Path(__file__).resolve().parents[1]
JSON = ROOT / "ARCHIVE-ECONOMY-AUDIT.json"
DOC = ROOT / "docs/00-meta/archive-economy-audit.md"
for path in (JSON, DOC, ROOT / "tools/archive_economy_audit_lib.py", ROOT / "tools/gen_archive_economy_audit.py"):
    if not path.exists():
        raise SystemExit(f"missing archive economy audit surface: {path.relative_to(ROOT)}")

payload = json.loads(JSON.read_text(encoding="utf-8"))
expected = build_archive_economy_audit(ROOT)
if payload != expected:
    raise SystemExit("ARCHIVE-ECONOMY-AUDIT.json drifted from generated archive-economy audit; run tools/gen_archive_economy_audit.py")
if payload.get("surface") != "ARCHIVE-ECONOMY-AUDIT.json":
    raise SystemExit("archive economy audit surface self-id drifted")
counts = payload.get("counts", {})
for key in ["release_economy_files", "release_economy_bytes", "markdown_words", "validation_tool_count", "checker_file_count", "max_path_length"]:
    if not isinstance(counts.get(key), int) or counts[key] <= 0:
        raise SystemExit(f"archive economy count missing or non-positive: {key}")
if payload.get("release_hygiene_root_relative_regression", {}).get("checker") != "tools/check_release_hygiene_relative_root.py":
    raise SystemExit("archive economy audit must name the release-hygiene root-relative regression")
refactors = payload.get("completed_refactors", {})
refactor = refactors.get("declarative_witness_contract_batch", {})
if refactor.get("checker") != "tools/check_declarative_witness_contract_batch.py" or refactor.get("contract_count", 0) < 30:
    raise SystemExit("archive economy audit must preserve the declarative witness batch refactor evidence")
shadow = refactors.get("shadow_contract_batch", {})
if shadow.get("checker") != "tools/check_shadow_batch_contract.py" or shadow.get("contract_count", 0) < 20:
    raise SystemExit("archive economy audit must preserve the shadow batch refactor evidence")
hot = refactors.get("hot_surface_compaction", {})
if hot.get("surface") != "HOT-SURFACE-COMPACTION.json" or hot.get("word_delta", 0) >= 0:
    raise SystemExit("archive economy audit must preserve hot-surface compaction evidence")
roundtrip = refactors.get("hot_surface_source_roundtrip", {})
if roundtrip.get("checker") != "tools/check_hot_surface_source_roundtrip_contract.py" or roundtrip.get("target_count") != hot.get("target_count"):
    raise SystemExit("archive economy audit must preserve hot-surface source-roundtrip evidence")
gpu_batch = refactors.get("gpustorming_late_search_batch", {})
if gpu_batch.get("checker") != "tools/check_gpustorming_late_search_family_batch_contract.py" or gpu_batch.get("contract_count", 0) < 10:
    raise SystemExit("archive economy audit must preserve GPustorming late-search batch evidence")
standard_batch = refactors.get("gpustorming_standard_batch", {})
if standard_batch.get("checker") != "tools/check_gpustorming_standard_family_batch_contract.py" or standard_batch.get("contract_count", 0) < 40:
    raise SystemExit("archive economy audit must preserve standard GPustorming batch evidence")
if standard_batch.get("former_wrappers_still_present"):
    raise SystemExit("standard GPustorming batch refactor must not leave former one-file wrappers in place")
if standard_batch.get("source_payload_rows"):
    raise SystemExit("standard GPustorming batch specs must not retain executable source payloads")
if standard_batch.get("spec_part_metrics", {}).get("part_count", 0) < 4 or standard_batch.get("spec_part_metrics", {}).get("max_part_bytes", 10**9) > 100000:
    raise SystemExit("standard GPustorming batch specs must be segmented into locality-sized parts")
gpu_witness_batch = refactors.get("gpu_witness_batch", {})
if gpu_witness_batch.get("checker") != "tools/check_gpu_witness_batch_contract.py" or gpu_witness_batch.get("contract_count", 0) < 50:
    raise SystemExit("archive economy audit must preserve GPU witness batch evidence")
if gpu_witness_batch.get("former_wrappers_still_present"):
    raise SystemExit("GPU witness batch refactor must not leave former one-file wrappers in place")
if gpu_witness_batch.get("spec_part_metrics", {}).get("part_count", 0) < 4 or gpu_witness_batch.get("spec_part_metrics", {}).get("max_part_bytes", 10**9) > 100000:
    raise SystemExit("GPU witness batch specs must be segmented into locality-sized parts")
method_batch = refactors.get("method_doc_ratchet_batch", {})
if method_batch.get("checker") != "tools/check_method_doc_ratchet_batch_contract.py" or method_batch.get("contract_count", 0) < 18:
    raise SystemExit("archive economy audit must preserve method-doc ratchet batch evidence")
if method_batch.get("former_wrappers_still_present"):
    raise SystemExit("method-doc ratchet batch refactor must not leave former one-file wrappers in place")
if method_batch.get("spec_part_metrics", {}).get("part_count", 0) < 2 or method_batch.get("spec_part_metrics", {}).get("max_part_bytes", 10**9) > 100000:
    raise SystemExit("method-doc ratchet batch specs must be segmented into locality-sized parts")
core_method_batch = refactors.get("core_method_batch", {})
if core_method_batch.get("checker") != "tools/check_core_method_batch_contract.py" or core_method_batch.get("contract_count", 0) < 20:
    raise SystemExit("archive economy audit must preserve core method batch evidence")
if core_method_batch.get("former_wrappers_still_present"):
    raise SystemExit("core method batch refactor must not leave former one-file wrappers in place")
if core_method_batch.get("spec_part_metrics", {}).get("part_count", 0) < 2 or core_method_batch.get("spec_part_metrics", {}).get("max_part_bytes", 10**9) > 100000:
    raise SystemExit("core method batch specs must be segmented into locality-sized parts")
alias_groups = refactors.get("path_alias_batch_groups", {})
if alias_groups.get("checker") != "tools/check_path_alias_ledger_contract.py" or alias_groups.get("source_count", 0) < 130:
    raise SystemExit("archive economy audit must preserve batch alias group evidence")
drift_gate = refactors.get("generated_surface_drift_gate", {})
if drift_gate.get("checker") != "tools/check_generated_surface_drift.py" or drift_gate.get("orchestrator") != "tools/gen_all_generated_surfaces.py" or drift_gate.get("helper") != "tools/generated_surface_lib.py":
    raise SystemExit("archive economy audit must preserve generated-surface drift gate evidence")
if drift_gate.get("generator_tools_in_lint") != [] or drift_gate.get("state") != "present-temporary-copy-read-only-target":
    raise SystemExit("generated-surface drift gate must prove lint regenerates only in a temporary copy and never repairs the judged tree")
if "temporary" not in drift_gate.get("policy", "") or "stale generated evidence fails" not in drift_gate.get("policy", ""):
    raise SystemExit("generated-surface drift gate policy must state the non-mutating failure contract")
if not (ROOT / "tools/check_generated_surface_nonmutation_canary.py").exists():
    raise SystemExit("archive economy audit requires the generated-surface nonmutation canary")

live_debt = payload.get("live_debt", {})
risk_by_id = {row.get("id"): row for row in payload.get("risk_flags", [])}
for surface, policy in LEDGER_DEBT_POLICIES.items():
    items = json.loads((ROOT / surface).read_text(encoding="utf-8")).get("items", [])
    expected_snapshot = live_debt_snapshot(items, policy, payload["revision"])
    snapshot = live_debt.get(surface)
    if snapshot != expected_snapshot:
        raise SystemExit(f"archive economy audit live-debt snapshot drifted for {surface}")
    risk = risk_by_id.get(policy["risk_id"])
    if snapshot["reserve_breached"]:
        if (
            not isinstance(risk, dict)
            or risk.get("budget") != policy["budget"]
            or risk.get("minimum_headroom") != policy["minimum_headroom"]
            or risk.get("headroom") != snapshot["headroom"]
        ):
            raise SystemExit(f"archive economy audit must emit reachable reserve-breach risk {policy['risk_id']}")
    elif risk is not None:
        raise SystemExit(f"archive economy audit must clear stale at-budget risk {policy['risk_id']}")
if "deletion court" not in payload.get("explicit_non_claim", ""):
    raise SystemExit("archive economy audit missing deletion-court non-claim")
text = DOC.read_text(encoding="utf-8")
for needle in ["# Archive economy audit", "## Counts", "## Risk flags", "Completed refactors", "Checker consolidation candidates", "not a deletion court"]:
    if needle not in text:
        raise SystemExit(f"archive economy guide missing {needle}")
print("check_archive_economy_audit_contract: OK")

#!/usr/bin/env python3
"""Read-only DelayBasin cloudtainer mission preflight.

This working-overlay diagnostic checks the concrete repairs made after rev0376.
It is not a canonical DelayBasin admission or an external replay result.

Usage:
    python -S cloudtainer/tools/check_cloudtainer_mission_preflight.py
    python -S cloudtainer/tools/check_cloudtainer_mission_preflight.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "cloudtainer/tools"))

from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    CommitmentContractError,
    responder_packet_projection_sha256,
    validate_assignment_commitment,
)
from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    RESPONSE_SET_CONTRACT_VERSION,
)
from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    RUN_BUNDLE_CONTRACT_VERSION,
)
from oq0266_isolated_scoring_policy_lib import (  # type: ignore  # noqa: E402
    POLICY_VERIFICATION_CONTRACT_VERSION,
    SCORING_POLICY_CONTRACT_VERSION,
)
from priority_zero_causal_artifact_lib import (  # noqa: E402
    CURRENT_CUSTODY_CONTRACT,
    CURRENT_SCORING_CONTRACT,
)
LANDING_TARGETS = ["README.md", "START_HERE.md", "AGENTS.md", "docs/README.md"]
SELF_EXCLUDED_MANIFEST_PATHS = {"FILE-MANIFEST.json", "CHECKSUMS.sha256", "RELEASE-PROVENANCE.json"}
RESPONDER_KIT = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-bundle-2026-06-16.zip"
CUSTODY_KIT = "handoffs/priority-zero-preanswer-clamped-external-replay-postfreeze-custody-kit-2026-06-16.zip"
SCORER_KIT = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-kit-2026-06-16.zip"
SCORER_INTAKE = "assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json"
RESPONDER_PACKET = "assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json"
RESPONSE_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
EVIDENCE_TEMPLATE = "assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json"
SCORE_SHEET_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json"
HANDOFF_MANIFEST = "handoffs/priority-zero-preanswer-clamped-external-replay-handoff-manifest-2026-06-16.json"
RESPONDER_README = "handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md"
CUSTODY_README = "handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md"
SCORER_README = "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md"
RESPONSE_PREP_TOOL = "tools/prepare_priority_zero_external_replay_response.py"
CUSTODY_PREP_TOOL = "tools/prepare_priority_zero_clean_response_custody_record.py"
SCORE_SHEET_PREP_TOOL = "tools/prepare_priority_zero_external_replay_score_sheet.py"
ARTIFACT_LIB = "tools/priority_zero_external_run_artifact_lib.py"
RESPONSE_LIB = "tools/priority_zero_external_replay_response_lib.py"
TIMELINE_LIB = "tools/priority_zero_custody_timeline_lib.py"
CUSTODY_LIB = "tools/priority_zero_external_replay_custody_lib.py"
CAUSAL_LIB = "tools/priority_zero_causal_artifact_lib.py"
ISOLATED_PILOT = "cloudtainer/oq0266-isolated-semantic-pilot"
EXPECTED_RESPONDER_INPUTS = {
    RESPONDER_PACKET, RESPONSE_TEMPLATE, RESPONDER_README, RESPONSE_PREP_TOOL, ARTIFACT_LIB, RESPONSE_LIB,
}
EXPECTED_CUSTODY_INPUTS = {
    EVIDENCE_TEMPLATE, RESPONSE_TEMPLATE, CUSTODY_README, CUSTODY_PREP_TOOL,
    CAUSAL_LIB, ARTIFACT_LIB, RESPONSE_LIB, TIMELINE_LIB, CUSTODY_LIB,
}
EXPECTED_SCORER_INPUTS = {
    SCORER_INTAKE, SCORE_SHEET_TEMPLATE, EVIDENCE_TEMPLATE, RESPONDER_PACKET, RESPONSE_TEMPLATE,
    "tools/score_priority_zero_external_replay_response.py", SCORE_SHEET_PREP_TOOL,
    ARTIFACT_LIB, RESPONSE_LIB, "tools/priority_zero_assay_lib.py",
    "tools/priority_zero_external_replay_decision_lib.py",
    CAUSAL_LIB, TIMELINE_LIB, CUSTODY_LIB, SCORER_README,
}



@dataclass
class Finding:
    severity: str
    id: str
    summary: str
    detail: str


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def extract_current_additions(text: str) -> list[str]:
    match = re.search(r"Current additions: (?P<additions>.*?)(?:\n|$)", text)
    if not match:
        return []
    return [item.strip() for item in match.group("additions").split(";") if item.strip()]


def manifest_paths() -> set[str]:
    rows = load_json("FILE-MANIFEST.json").get("files", [])
    return {
        row["path"]
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }


def actual_paths() -> set[str]:
    paths: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if "__pycache__" in rel or rel.endswith((".pyc", ".pyo")):
            continue
        paths.add(rel)
    return paths


def generated_drift_is_read_only() -> tuple[bool, str]:
    helper = (ROOT / "tools/generated_surface_lib.py").read_text(encoding="utf-8")
    toolchain = (ROOT / "tools/validation_toolchain_lib.py").read_text(encoding="utf-8")
    checks = {
        "declared_mode": 'DRIFT_VALIDATION_MODE = "temporary-copy-read-only-target"' in helper,
        "copies_tree": "copy_release_tree_for_generation(root)" in helper,
        "regenerates_copy": "refresh_generated_surfaces(generated_root" in helper,
        "does_not_regenerate_target": "refresh_generated_surfaces(root" not in re.search(
            r"def generated_surface_drift\(.*?(?=\ndef |\Z)", helper, flags=re.S
        ).group(0),
        "canary_exists": (ROOT / "tools/check_generated_surface_nonmutation_canary.py").exists(),
        "canary_in_toolchain": '"check_generated_surface_nonmutation_canary.py"' in toolchain,
    }
    failed = [name for name, ok in checks.items() if not ok]
    return not failed, ", ".join(failed) if failed else "temporary-copy mode plus mutation canary are present"


def scorer_lane_status() -> tuple[bool, str]:
    intake = load_json(SCORER_INTAKE)
    response_template = load_json(RESPONSE_TEMPLATE)
    evidence_template = load_json(EVIDENCE_TEMPLATE)
    score_template = load_json(SCORE_SHEET_TEMPLATE)
    manifest = load_json(HANDOFF_MANIFEST)
    required = "\n".join(str(item) for item in intake.get("required_response_checks", []))
    criteria = "\n".join(
        str(item.get("criterion", "")) for item in intake.get("metrics", []) if isinstance(item, dict)
    )
    stale = "routes OQ-0264 to OQ-0265" in criteria or "OQ-0264 must import a response" in required
    current = "OQ-0266 must import a response/custody/score-sheet triplet" in required and "routes OQ-0266" in criteria

    score_tool = (ROOT / "tools/score_priority_zero_external_replay_response.py").read_text(encoding="utf-8")
    response_tool = (ROOT / RESPONSE_PREP_TOOL).read_text(encoding="utf-8")
    custody_tool = (ROOT / CUSTODY_PREP_TOOL).read_text(encoding="utf-8")
    score_sheet_tool = (ROOT / SCORE_SHEET_PREP_TOOL).read_text(encoding="utf-8")
    response_lib = (ROOT / RESPONSE_LIB).read_text(encoding="utf-8")
    artifact_lib = (ROOT / ARTIFACT_LIB).read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    responder_readme = (ROOT / RESPONDER_README).read_text(encoding="utf-8")
    custody_readme = (ROOT / CUSTODY_README).read_text(encoding="utf-8")
    scorer_readme = (ROOT / SCORER_README).read_text(encoding="utf-8")
    evidence_att = evidence_template.get("custodian_attestation", {})
    score_att = score_template.get("scorer_attestation", {})
    expected_sequence = [
        "finalize completed responder output with bundled response helper",
        "open custody kit and revalidate the exact response bytes",
        "freeze custody record with producer-local response observation",
        "open scorer kit and initialize score draft after exact custody validation",
        "complete and freeze score sheet with scorer-local custody observation",
        "run scorer on the exact response/custody/score-sheet hash chain",
    ]
    manual_time_flags = {
        "--response-frozen-at", "--custody-kit-opened-at", "--custody-record-frozen-at",
        "--scorer-kit-opened-at", "--scored-at",
    }
    current_command_text = "\n".join([makefile, custody_readme, scorer_readme])
    protections = {
        "bound_custody": intake.get("requires_bound_custody_record_file") is True,
        "bound_score_sheet": intake.get("requires_bound_score_sheet_file") is True,
        "distinct_scorer": intake.get("requires_distinct_scorer_from_responder") is True,
        "metric_rationales": intake.get("requires_metric_rationales") is True,
        "packet_cost": intake.get("requires_per_packet_operator_cost") is True,
        "cost_sum": intake.get("requires_operator_cost_sum_match") is True,
        "bounded_scope": intake.get("allows_global_compact_gate_confirmation") is False,
        "trace_excerpt_honesty": "trace excerpt rather than a measured full-archive load" in str(intake.get("full_archive_control_state")),
        "response_contract_intake": intake.get("response_preparation_contract_version") == "responder-finalize-v1" and intake.get("requires_tool_finalized_response") is True,
        "response_contract_templates": response_template.get("response_preparation_contract_version") == "responder-finalize-v1" and evidence_template.get("response_preparation_contract_version") == "responder-finalize-v1" and score_template.get("response_preparation_contract_version") == "responder-finalize-v1",
        "responder_helper_runnable": all(token in response_tool for token in ["command_init", "command_finalize", "validate_draft_binding", "write_new_json"]),
        "responder_readme_runnable": all(token in responder_readme for token in ["prepare_priority_zero_external_replay_response.py init", "prepare_priority_zero_external_replay_response.py finalize", "fails before custody is spent"]),
        "shared_response_validator": all("validate_finalized_response" in text for text in [custody_tool, score_sheet_tool, score_tool]),
        "shared_custody_validator": all("validate_current_custody_record" in text for text in [custody_tool, score_sheet_tool, score_tool]),
        "shared_artifact_primitives": all(token in artifact_lib for token in ["strict_json", "parse_timestamp", "write_new_json", "refusing to overwrite"]),
        "atomic_no_clobber_publish": all(token in artifact_lib for token in ["tempfile.mkstemp", "os.fsync", "os.link"]),
        "readonly_final_artifacts": (
            "write_new_json(out, final, readonly=True)" in response_tool
            and "write_new_json(out, record, readonly=True)" in custody_tool
            and "write_new_json(out, final, readonly=True)" in score_sheet_tool
        ),
        "strict_json": (
            "strict_json_bytes(raw" in score_tool
            and "reject_duplicate_keys" in artifact_lib
            and "parse_constant=reject_constant" in artifact_lib
            and "parse_float=finite_float" in artifact_lib
            and "outside the finite runtime range" in artifact_lib
        ),
        "single_read_response_hash": "response bytes validated by this run" in score_tool and "response_file_sha256=response_sha256" in score_tool,
        "complete_make_triplet": all(token in makefile for token in ["EVIDENCE required", "SCORE_SHEET required", "SUMMARY_OUT"]),
        "custody_make_target": all(token in makefile for token in ["prepare-external-custody", "ATTEST_CLEAN_PREANSWER=yes required"]),
        "no_manual_stage_time_flags": not any(flag in current_command_text for flag in manual_time_flags),
        "causal_stage_intake": intake.get("custody_contract_version") == CURRENT_CUSTODY_CONTRACT and intake.get("scoring_contract_version") == CURRENT_SCORING_CONTRACT,
        "causal_stage_templates": evidence_template.get("custody_contract_version") == CURRENT_CUSTODY_CONTRACT and score_template.get("scoring_contract_version") == CURRENT_SCORING_CONTRACT,
        "custody_does_not_forecast_scorer": "scorer_opened_at" not in evidence_att and "scorer_intake_surface" not in evidence_template and "scorer_intake_sha256" not in evidence_template,
        "score_sheet_records_helper_sources": score_att.get("scorer_kit_opened_at_source") == "" and score_att.get("custody_record_observed_at_source") == "" and score_att.get("scored_at_source") == "",
        "custody_helper_current": all(token in custody_tool for token in ["validate_finalized_response", "validate_current_custody_record", "--prerequisite", "local-process-clock-at-custody-helper-start"]),
        "score_sheet_helper_current": all(token in score_sheet_tool for token in ["command_init", "command_finalize", "local-process-clock-at-score-sheet-init", "local-process-clock-at-score-sheet-finalize"]),
        "manifest_sequence": manifest.get("postfreeze_sequence") == expected_sequence,
        "manifest_causal_ordering": manifest.get("cross_operator_ordering_basis") == "exact-artifact-hash-chain; independent wall clocks are descriptive only",
        "manifest_response_contract": manifest.get("response_preparation_contract_version") == "responder-finalize-v1",
        "two_operator_minimum": manifest.get("minimum_distinct_operators") == 2,
        "clock_nonclaim": "not trusted" in str(manifest.get("timestamp_non_claim", "")),
        "response_lib_has_no_key": all(token not in response_lib for token in ["answer_key", "true_variant", "expected_score"]),
    }

    topologies: dict[str, tuple[set[str], set[str]]] = {}
    for name, rel, expected in [
        ("responder", RESPONDER_KIT, EXPECTED_RESPONDER_INPUTS),
        ("custody", CUSTODY_KIT, EXPECTED_CUSTODY_INPUTS),
        ("scorer", SCORER_KIT, EXPECTED_SCORER_INPUTS),
    ]:
        with zipfile.ZipFile(ROOT / rel) as archive:
            members = set(archive.namelist())
        topologies[name] = (expected - members, members - expected)

    sha_by_name = {
        "responder": hashlib.sha256((ROOT / RESPONDER_KIT).read_bytes()).hexdigest(),
        "custody": hashlib.sha256((ROOT / CUSTODY_KIT).read_bytes()).hexdigest(),
        "scorer": hashlib.sha256((ROOT / SCORER_KIT).read_bytes()).hexdigest(),
    }
    hashes_current = (
        manifest.get("responder_bundle_sha256") == sha_by_name["responder"]
        and manifest.get("custody_kit_sha256") == sha_by_name["custody"]
        and manifest.get("scorer_kit_sha256") == sha_by_name["scorer"]
    )
    manifest_topology_current = (
        manifest.get("responder_bundle_members") == [
            RESPONDER_PACKET, RESPONSE_TEMPLATE, RESPONDER_README, RESPONSE_PREP_TOOL, ARTIFACT_LIB, RESPONSE_LIB
        ]
        and manifest.get("custody_kit_members") == [
            EVIDENCE_TEMPLATE, RESPONSE_TEMPLATE, CUSTODY_README, CUSTODY_PREP_TOOL,
            CAUSAL_LIB, ARTIFACT_LIB, RESPONSE_LIB, TIMELINE_LIB, CUSTODY_LIB
        ]
        and set(manifest.get("scorer_kit_members", [])) == EXPECTED_SCORER_INPUTS
    )
    failed_protections = sorted(name for name, ok in protections.items() if not ok)
    topology_clean = all(not missing and not extra for missing, extra in topologies.values())
    ok = current and not stale and topology_clean and manifest_topology_current and not failed_protections and hashes_current
    topology_detail = {
        name: {"missing": sorted(missing), "extra": sorted(extra)}
        for name, (missing, extra) in topologies.items()
    }
    detail = (
        f"current_routing={current}; stale_routing={stale}; topology={topology_detail}; "
        f"manifest_topology_current={manifest_topology_current}; "
        f"failed_protections={failed_protections}; kit_hashes_current={hashes_current}"
    )
    return ok, detail


def isolated_pilot_status() -> tuple[bool, str]:
    pilot = ROOT / ISOLATED_PILOT
    required = [
        "assignment-plan.json",
        "assignment-commitment.json",
        "scoring-policy.json",
        "dispatch-manifest.json",
        "batch-manifest.json",
        "build-receipt.json",
        "PREFREEZE-README.md",
        "prefreeze-dispatch-kit.zip",
        "postfreeze-batch-kit.zip",
        "run-manifest-template.json",
    ]
    missing = [name for name in required if not (pilot / name).exists()]
    tool_required = [
        ROOT / "cloudtainer/tools/lock_oq0266_isolated_response_set.py",
        ROOT / "cloudtainer/tools/oq0266_isolated_response_set_lib.py",
        ROOT / "cloudtainer/tools/check_oq0266_isolated_semantic_pilot.py",
        ROOT / "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py",
        ROOT / "cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py",
        ROOT / "cloudtainer/tools/oq0266_isolated_scoring_policy_lib.py",
        ROOT / "cloudtainer/tools/oq0266_isolated_commitment_lib.py",
        ROOT / "cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py",
        ROOT / "cloudtainer/tools/oq0266_isolated_run_bundle_lib.py",
        ROOT / CAUSAL_LIB,
    ]
    missing_tools = [path.relative_to(ROOT).as_posix() for path in tool_required if not path.exists()]
    if missing or missing_tools:
        return False, f"missing={missing}; missing_tools={missing_tools}"
    try:
        plan_path = pilot / "assignment-plan.json"
        commitment_path = pilot / "assignment-commitment.json"
        policy_path = pilot / "scoring-policy.json"
        dispatch_path = pilot / "dispatch-manifest.json"
        prefreeze_path = pilot / "prefreeze-dispatch-kit.zip"
        postfreeze_path = pilot / "postfreeze-batch-kit.zip"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        commitment = json.loads(commitment_path.read_text(encoding="utf-8"))
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        dispatch = json.loads(dispatch_path.read_text(encoding="utf-8"))
        manifest = json.loads((pilot / "batch-manifest.json").read_text(encoding="utf-8"))
        receipt = json.loads((pilot / "build-receipt.json").read_text(encoding="utf-8"))
        plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        commitment_sha = hashlib.sha256(commitment_path.read_bytes()).hexdigest()
        policy_sha = hashlib.sha256(policy_path.read_bytes()).hexdigest()
        dispatch_sha = hashlib.sha256(dispatch_path.read_bytes()).hexdigest()
        prefreeze_sha = hashlib.sha256(prefreeze_path.read_bytes()).hexdigest()
        postfreeze_sha = hashlib.sha256(postfreeze_path.read_bytes()).hexdigest()

        arms = plan.get("arms", [])
        manifest_arms = manifest.get("arms", [])
        dispatch_arms = dispatch.get("arms", [])
        arm_codes = [row.get("arm_code") for row in arms if isinstance(row, dict)]
        manifest_codes = [row.get("arm_code") for row in manifest_arms if isinstance(row, dict)]
        dispatch_codes = [row.get("arm_code") for row in dispatch_arms if isinstance(row, dict)]
        variants = [row.get("analysis_variant") for row in arms if isinstance(row, dict)]
        topology_ok = (
            len(arms) == 4
            and len(manifest_arms) == 4
            and len(dispatch_arms) == 4
            and len(set(arm_codes)) == 4
            and set(arm_codes) == set(manifest_codes) == set(dispatch_codes)
        )
        variant_ok = set(variants) == {"compact", "sham", "baseline", "trace"}
        try:
            commitment_summary = validate_assignment_commitment(
                commitment,
                assignment_plan_sha256=plan_sha,
                scoring_policy_sha256=policy_sha,
                scoring_policy_contract_version=SCORING_POLICY_CONTRACT_VERSION,
                expected_arm_codes=set(arm_codes),
            )
            committed_packet_projections = (
                commitment_summary.responder_packet_projection_sha256_by_arm
            )
            commitment_contract_valid = commitment_summary.batch_id == plan.get("batch_id")
        except CommitmentContractError:
            committed_packet_projections = {}
            commitment_contract_valid = False
        commitment_ok = (
            commitment_contract_valid
            and policy.get("assignment_plan_sha256") == plan_sha
            and policy.get("scoring_policy_contract_version")
            == SCORING_POLICY_CONTRACT_VERSION
            and policy.get("batch_id") == plan.get("batch_id")
        )
        contract_ok = (
            dispatch.get("response_set_contract_version") == RESPONSE_SET_CONTRACT_VERSION
            and manifest.get("response_set_contract_version") == RESPONSE_SET_CONTRACT_VERSION
            and receipt.get("response_set_contract_version") == RESPONSE_SET_CONTRACT_VERSION
            and manifest.get("run_bundle_contract_version") == RUN_BUNDLE_CONTRACT_VERSION
            and receipt.get("run_bundle_contract_version") == RUN_BUNDLE_CONTRACT_VERSION
            and dispatch.get("assignment_commitment_sha256") == commitment_sha
            and dispatch.get("arm_count") == 4
            and dispatch.get("minimum_distinct_responders") == 4
        )
        receipt_ok = (
            receipt.get("assignment_plan_sha256") == plan_sha
            and receipt.get("assignment_commitment_sha256") == commitment_sha
            and receipt.get("dispatch_manifest_sha256") == dispatch_sha
            and receipt.get("prefreeze_dispatch_kit_sha256") == prefreeze_sha
            and receipt.get("postfreeze_batch_kit_sha256") == postfreeze_sha
            and receipt.get("scoring_policy_sha256") == policy_sha
            and receipt.get("scoring_policy_contract_version") == SCORING_POLICY_CONTRACT_VERSION
            and receipt.get("policy_verification_contract_version")
            == POLICY_VERIFICATION_CONTRACT_VERSION
            and receipt.get("arm_count") == 4
            and receipt.get("commitment_binding_state")
            == "assignment-plan-scoring-policy-and-responder-visible-packet-projections-bound-before-response"
            and receipt.get("batch_barrier_state")
            == "all-arm-response-lock-policy-receipts-source-kits-and-final-triplets-content-bundled"
            and receipt.get("burden_inference_state") == "not-identifiable-between-subjects-n1-per-arm"
        )
        manifest_ok = (
            manifest.get("assignment_plan_sha256") == plan_sha
            and manifest.get("run_bundle_contract_version") == RUN_BUNDLE_CONTRACT_VERSION
            and manifest.get("scoring_policy_sha256") == policy_sha
            and manifest.get("scoring_policy_contract_version") == SCORING_POLICY_CONTRACT_VERSION
            and manifest.get("policy_verification_contract_version")
            == POLICY_VERIFICATION_CONTRACT_VERSION
            and manifest.get("assignment_commitment_sha256") == commitment_sha
            and manifest.get("dispatch_manifest_sha256") == dispatch_sha
            and manifest.get("prefreeze_dispatch_kit_sha256") == prefreeze_sha
            and "all four exact" in str(manifest.get("required_batch_barrier", ""))
            and RUN_BUNDLE_CONTRACT_VERSION in str(manifest.get("required_batch_barrier", ""))
            and "scoring-policy bytes" in str(manifest.get("commitment_binding", ""))
            and "responder-visible packet projection" in str(
                manifest.get("commitment_binding", "")
            )
        )

        manifest_by_arm = {
            row.get("arm_code"): row for row in manifest_arms if isinstance(row, dict)
        }
        dispatch_by_arm = {
            row.get("arm_code"): row for row in dispatch_arms if isinstance(row, dict)
        }
        bundle_hashes_ok = True
        packet_commitment_bindings_ok = True
        policy_rows = policy.get("arms", [])
        policy_by_arm = {
            row.get("arm_code"): row.get("scorer_policy")
            for row in policy_rows
            if isinstance(row, dict)
        }
        policy_bindings_ok = (
            len(policy_by_arm) == 4
            and set(policy_by_arm) == set(arm_codes)
            and policy.get("global_requirements", {}).get("scorer_distinct_from_responder") is True
            and policy.get("global_requirements", {}).get("self_contained_source_kit_evidence_capsule_required") is True
            and policy.get("global_requirements", {}).get("separately_preserved_outer_digest_required") is True
            and policy.get("global_requirements", {}).get("bounded_safe_nested_zip_parsing_required") is True
            and policy.get("global_requirements", {}).get("postassembly_dynamic_or_source_artifact_replacement_rejected") is True
            and all(
                isinstance(surface, str)
                and isinstance(digest, str)
                and (ROOT / surface).is_file()
                and hashlib.sha256((ROOT / surface).read_bytes()).hexdigest() == digest
                for surface, digest in policy.get("tool_sha256_by_surface", {}).items()
            )
        )
        nested_bundle_bytes_ok = True
        for arm in arm_codes:
            row = manifest_by_arm.get(arm, {})
            dispatch_row = dispatch_by_arm.get(arm, {})
            bundle_rel = row.get("responder_bundle_surface")
            if not isinstance(bundle_rel, str) or not (ROOT / bundle_rel).exists():
                bundle_hashes_ok = False
                continue
            digest = hashlib.sha256((ROOT / bundle_rel).read_bytes()).hexdigest()
            if (
                digest != row.get("responder_bundle_sha256")
                or digest != dispatch_row.get("responder_bundle_sha256")
                or digest != receipt.get("responder_bundle_sha256_by_arm", {}).get(arm)
            ):
                bundle_hashes_ok = False
            packet_rel = row.get("responder_packet_surface")
            try:
                packet = load_json(str(packet_rel)) if isinstance(packet_rel, str) else {}
            except (OSError, json.JSONDecodeError):
                packet = {}
            if packet.get("assignment_commitment_sha256") != commitment_sha:
                packet_commitment_bindings_ok = False
            try:
                packet_projection_sha = responder_packet_projection_sha256(packet)
            except CommitmentContractError:
                packet_projection_sha = ""
            if (
                packet_projection_sha != committed_packet_projections.get(arm)
                or packet_projection_sha
                != row.get("responder_packet_projection_sha256")
                or packet_projection_sha
                != dispatch_row.get("responder_packet_projection_sha256")
            ):
                packet_commitment_bindings_ok = False
            scorer_rel = row.get("scorer_intake_surface")
            if not isinstance(scorer_rel, str) or not (ROOT / scorer_rel).is_file():
                policy_bindings_ok = False
            else:
                scorer = load_json(scorer_rel)
                policy_row = policy_by_arm.get(arm)
                if (
                    hashlib.sha256((ROOT / scorer_rel).read_bytes()).hexdigest()
                    != row.get("scorer_intake_sha256")
                    or scorer.get("scoring_policy_sha256") != policy_sha
                    or scorer.get("scoring_policy_surface") != f"{ISOLATED_PILOT}/scoring-policy.json"
                    or scorer.get("requires_distinct_scorer_from_responder") is not True
                    or not isinstance(policy_row, dict)
                    or policy_row.get("requires_distinct_scorer_from_responder") is not True
                    or scorer.get("answer_key") != policy_row.get("answer_key")
                ):
                    policy_bindings_ok = False

        expected_prefreeze = [
            f"{ISOLATED_PILOT}/dispatch-manifest.json",
            f"{ISOLATED_PILOT}/assignment-commitment.json",
            f"{ISOLATED_PILOT}/PREFREEZE-README.md",
            "cloudtainer/tools/lock_oq0266_isolated_response_set.py",
            "cloudtainer/tools/oq0266_isolated_response_set_lib.py",
            "cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py",
            "cloudtainer/tools/oq0266_isolated_scoring_policy_lib.py",
            "cloudtainer/tools/oq0266_isolated_commitment_lib.py",
            CAUSAL_LIB,
            "tools/priority_zero_external_run_artifact_lib.py",
            "tools/priority_zero_external_replay_response_lib.py",
            *[dispatch_by_arm[arm].get("responder_bundle_surface") for arm in arm_codes],
        ]
        with zipfile.ZipFile(prefreeze_path) as archive:
            prefreeze_integrity_ok = archive.testzip() is None
            prefreeze_names = archive.namelist()
            prefreeze_topology_ok = prefreeze_names == expected_prefreeze
            for arm in arm_codes:
                bundle_rel = dispatch_by_arm[arm].get("responder_bundle_surface")
                if not isinstance(bundle_rel, str) or archive.read(bundle_rel) != (ROOT / bundle_rel).read_bytes():
                    nested_bundle_bytes_ok = False
            prefreeze_text = "\n".join(
                archive.read(name).decode("utf-8")
                for name in prefreeze_names
                if not name.endswith(".zip")
            )
        dispatch_text = dispatch_path.read_text(encoding="utf-8")
        prefreeze_leak_free = all(
            fragment not in dispatch_text
            for fragment in [
                '"analysis_variant"',
                '"source_packet_label"',
                '"reference_expected_score"',
                '"scorer_intake_surface"',
                '"custody_template_surface"',
                '"score_sheet_template_surface"',
                "packet-alpha",
                "packet-bravo",
                "packet-charlie",
                "packet-delta",
            ]
        ) and all(
            label not in prefreeze_text
            for label in ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]
        )
        # Validator source names forbidden keys/paths in order to reject them;
        # the executable boundary is instead checked by exact ZIP topology and
        # the absence of concrete assignment labels or postfreeze tools.
        prefreeze_boundary_ok = (
            prefreeze_integrity_ok
            and prefreeze_topology_ok
            and nested_bundle_bytes_ok
            and prefreeze_leak_free
            and f"{ISOLATED_PILOT}/assignment-plan.json" not in prefreeze_names
            and f"{ISOLATED_PILOT}/scoring-policy.json" not in prefreeze_names
            and f"{ISOLATED_PILOT}/postfreeze-batch-kit.zip" not in prefreeze_names
            and "tools/prepare_priority_zero_clean_response_custody_record.py" not in prefreeze_names
            and "tools/prepare_priority_zero_external_replay_score_sheet.py" not in prefreeze_names
            and "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py" not in prefreeze_names
        )

        with zipfile.ZipFile(postfreeze_path) as archive:
            postfreeze_integrity_ok = archive.testzip() is None
            postfreeze_names = set(archive.namelist())
        postfreeze_required = {
            f"{ISOLATED_PILOT}/assignment-plan.json",
            f"{ISOLATED_PILOT}/scoring-policy.json",
            f"{ISOLATED_PILOT}/assignment-commitment.json",
            f"{ISOLATED_PILOT}/dispatch-manifest.json",
            f"{ISOLATED_PILOT}/batch-manifest.json",
            f"{ISOLATED_PILOT}/run-manifest-template.json",
            "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py",
            "cloudtainer/tools/oq0266_isolated_response_set_lib.py",
            "cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py",
            "cloudtainer/tools/oq0266_isolated_scoring_policy_lib.py",
            "cloudtainer/tools/oq0266_isolated_commitment_lib.py",
            "cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py",
            "cloudtainer/tools/oq0266_isolated_run_bundle_lib.py",
            CAUSAL_LIB,
            "tools/prepare_priority_zero_clean_response_custody_record.py",
            "tools/prepare_priority_zero_external_replay_score_sheet.py",
        }
        postfreeze_topology_ok = postfreeze_integrity_ok and postfreeze_required.issubset(postfreeze_names)

        checker_path = ROOT / "cloudtainer/tools/check_oq0266_isolated_semantic_pilot.py"
        scorer_path = ROOT / "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py"
        lock_path = ROOT / "cloudtainer/tools/lock_oq0266_isolated_response_set.py"
        checker_text = checker_path.read_text(encoding="utf-8")
        scorer_text = scorer_path.read_text(encoding="utf-8")
        lock_text = lock_path.read_text(encoding="utf-8")
        canaries_ok = all(
            token in checker_text
            for token in [
                "cross-machine-clock-skew-accepted",
                "self-contained-capsule-replay-without-ambient-pilot-files",
                "postassembly-source-score-mutation-isolated",
                "separately-pinned-outer-digest-accepted",
                "prefreeze-dispatch-postfreeze-leak",
                "incomplete-response-set-lock",
                "missing-custody-prerequisite-receipt",
                "substituted-custody-prerequisite-receipt",
                "response-set-lock-substitution",
                "postresponse-plan-commitment-substitution",
                "postresponse-scorer-policy-substitution-self-score",
                "responder-stimulus-and-runtime-hash-substitution",
                "duplicate-responder-batch",
                "strict-json-exponent-overflow",
                "postassembly-score-member-replacement",
            "whole-capsule-replacement-against-preserved-digest",
            "unsafe-nested-zip-member",
                "whole-capsule-replacement-against-preserved-digest",
                "unsafe-nested-zip-member",
            ]
        )
        scorer_barrier_ok = (
            "expected_responses_by_arm=expected_lock_rows" in scorer_text
            and "custody prerequisite set drifted" in scorer_text
            and "custody prerequisite {prerequisite_label} does not bind the supplied exact artifact bytes" in scorer_text
            and "responder self-scoring is forbidden by the preanswer batch policy" in scorer_text
            and "validate_policy_verification_receipt" in scorer_text
            and "validate_scorer_against_policy" in scorer_text
            and "load_run_bundle" in scorer_text
            and "expected_run_bundle_sha256" in scorer_text
            and "read_safe_zip_members" in scorer_text
            and "source_kit_replay_state" in scorer_text
            and "run_bundle_member_binding_state" in scorer_text
            and "content-bundled" in scorer_text
        )
        lock_boundary_ok = (
            "exactly {EXPECTED_ARM_COUNT} --response" in lock_text
            and "--attest-clean-batch-barrier" in lock_text
            and "assignment-plan.json" not in lock_text
            and "prepare_priority_zero_clean_response_custody_record" not in lock_text
            and "score_oq0266_isolated_semantic_pilot" not in lock_text
        )
        expected_positive = {
            "cross-machine-clock-skew-accepted",
            "self-contained-capsule-replay-without-ambient-pilot-files",
            "postassembly-source-score-mutation-isolated",
            "separately-pinned-outer-digest-accepted",
        }
        expected_negative = {
            "responder-bundle-mapping-leak",
            "prefreeze-dispatch-postfreeze-leak",
            "incomplete-response-set-lock",
            "missing-custody-prerequisite-receipt",
            "substituted-custody-prerequisite-receipt",
            "response-set-lock-substitution",
            "postresponse-plan-commitment-substitution",
            "postresponse-scorer-policy-substitution-self-score",
            "responder-stimulus-and-runtime-hash-substitution",
            "duplicate-responder-batch",
            "strict-json-exponent-overflow",
            "postassembly-score-member-replacement",
            "whole-capsule-replacement-against-preserved-digest",
            "unsafe-nested-zip-member",
        }
        receipt_canaries_ok = (
            expected_positive.issubset(set(receipt.get("positive_canaries", [])))
            and expected_negative.issubset(set(receipt.get("negative_canaries", [])))
        )

        ok = all([
            topology_ok,
            variant_ok,
            commitment_ok,
            contract_ok,
            receipt_ok,
            manifest_ok,
            bundle_hashes_ok,
            packet_commitment_bindings_ok,
            policy_bindings_ok,
            prefreeze_boundary_ok,
            postfreeze_topology_ok,
            canaries_ok,
            scorer_barrier_ok,
            lock_boundary_ok,
            receipt_canaries_ok,
        ])
        detail = (
            f"arms={len(arms)}; variants={sorted(str(v) for v in variants)}; "
            f"commitment_current={commitment_ok}; response_set_contract={contract_ok}; "
            f"receipt_current={receipt_ok}; manifest_current={manifest_ok}; "
            f"bundle_hashes_current={bundle_hashes_ok}; "
            f"packet_commitment_bindings={packet_commitment_bindings_ok}; "
            f"policy_bindings={policy_bindings_ok}; "
            f"prefreeze_boundary={prefreeze_boundary_ok}; "
            f"postfreeze_topology={postfreeze_topology_ok}; "
            f"barrier_canaries={canaries_ok}; scorer_barrier={scorer_barrier_ok}; "
            f"lock_boundary={lock_boundary_ok}; receipt_canaries={receipt_canaries_ok}; "
            "burden_inference=descriptive-only-between-subjects-n1"
        )
        return ok, detail
    except (
        OSError,
        KeyError,
        CommitmentContractError,
        json.JSONDecodeError,
        zipfile.BadZipFile,
    ) as exc:
        return False, str(exc)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=18, help="maximum landing hot-cue item count")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    receipt = load_json("REVISION-RECEIPT.json")
    release = load_json("RELEASE-MANIFEST.json")
    status = load_json("SURFACE-STATUS.json")
    context = load_json("context-pack.json")
    archive_audit = load_json("ARCHIVE-ECONOMY-AUDIT.json")
    cloud_note_path = ROOT / "cloudtainer/CLOUDTAINER-REVISION-NOTE.json"
    cloud_note = json.loads(cloud_note_path.read_text(encoding="utf-8")) if cloud_note_path.exists() else {}

    findings: list[Finding] = []
    canonical_revs = {
        "REVISION-RECEIPT.json": receipt.get("revision"),
        "RELEASE-MANIFEST.json": release.get("revision"),
        "SURFACE-STATUS.json": status.get("revision"),
    }
    working_rev = cloud_note.get("working_revision")
    if working_rev and set(canonical_revs.values()) != {working_rev}:
        findings.append(Finding(
            "info",
            "overlay-not-canonical",
            f"cloudtainer working revision {working_rev} differs from canonical root {sorted(set(canonical_revs.values()))}",
            "Expected for this named working overlay; no full receipt/ledger/status/provenance promotion was attempted.",
        ))

    hot = receipt.get("hot_current_supports")
    if not isinstance(hot, list) or not hot or len(hot) > args.threshold or len(hot) != len(set(hot)):
        findings.append(Finding("fail", "hot-support-contract", "receipt hot_current_supports is invalid", f"observed={hot!r}; threshold={args.threshold}"))
        hot = hot if isinstance(hot, list) else []

    hot_counts: dict[str, int] = {}
    for rel in LANDING_TARGETS:
        path = ROOT / rel
        if not path.exists():
            findings.append(Finding("fail", "missing-landing-surface", rel, "expected landing surface is absent"))
            continue
        items = extract_current_additions(path.read_text(encoding="utf-8"))
        hot_counts[rel] = len(items)
        if items != hot:
            findings.append(Finding("fail", "landing-hot-support-drift", rel, "Current additions must equal receipt hot_current_supports exactly and in order"))
    if hot and not any(f.id.startswith("landing-hot") or f.id == "hot-support-contract" for f in findings):
        findings.append(Finding("info", "hot-supports-bounded", f"four landing cues share the same {len(hot)}-item hot support set", "full canon/touched trace remains separate"))

    read_only, drift_detail = generated_drift_is_read_only()
    findings.append(Finding(
        "info" if read_only else "fail",
        "lint-drift-read-only" if read_only else "lint-drift-mutates",
        "generated-surface drift validation is read-only" if read_only else "generated-surface drift validation is not proven read-only",
        drift_detail,
    ))

    scorer_ok, scorer_detail = scorer_lane_status()
    findings.append(Finding(
        "info" if scorer_ok else "fail",
        "scorer-kit-runnable" if scorer_ok else "scorer-kit-incomplete",
        "OQ-0266 responder/custody/scorer lane is fail-fast, file-bound, cost-reconciled, scope-clamped, and standalone-current" if scorer_ok else "OQ-0266 custody/scorer lane remains stale or incomplete",
        scorer_detail,
    ))

    pilot_ok, pilot_detail = isolated_pilot_status()
    findings.append(Finding(
        "info" if pilot_ok else "fail",
        "isolated-pilot-runnable" if pilot_ok else "isolated-pilot-incomplete",
        "four-responder blinded isolated-arm semantic pilot is packaged and hash-committed" if pilot_ok else "isolated-arm pilot is missing or internally inconsistent",
        pilot_detail,
    ))

    mpaths = manifest_paths()
    apaths = actual_paths()
    unmanifested = sorted(apaths - mpaths - SELF_EXCLUDED_MANIFEST_PATHS)
    if unmanifested:
        findings.append(Finding("warn", "unmanifested-files", f"{len(unmanifested)} files sit outside FILE-MANIFEST", "; ".join(unmanifested[:20])))

    live_debt = archive_audit.get("live_debt", {})
    reserve_breaches = []
    for surface, snapshot in live_debt.items():
        if isinstance(snapshot, dict) and snapshot.get("reserve_breached"):
            reserve_breaches.append(surface)
            findings.append(Finding(
                "warn",
                "live-debt-reserve-breached",
                f"{surface} headroom {snapshot.get('headroom')} is below reserve {snapshot.get('minimum_headroom')}",
                f"live {snapshot.get('live_count')}/{snapshot.get('budget')}; oldest {snapshot.get('oldest_live_id')} from {snapshot.get('oldest_live_revision')}",
            ))
    if live_debt and not reserve_breaches:
        detail = "; ".join(
            f"{surface}={snapshot.get('live_count')}/{snapshot.get('budget')} headroom={snapshot.get('headroom')}"
            for surface, snapshot in live_debt.items()
            if isinstance(snapshot, dict)
        )
        findings.append(Finding("info", "live-debt-reserve-restored", "all four live ledgers preserve their admission reserve", detail))
    decay = context.get("decay_watch_overdue", [])
    if decay:
        findings.append(Finding("warn", "decay-watch-overdue", f"{len(decay)} overdue decay-watch rows", ", ".join(str(row.get("id", "?")) for row in decay if isinstance(row, dict))))
    else:
        findings.append(Finding("info", "decay-watch-reviewed", "no decay-watch row is overdue at the canonical receipt date", "DW-0001 through DW-0003 were reviewed and renewed with bounded horizons"))

    oq_ids = [row.get("id") for row in context.get("open_questions", []) if isinstance(row, dict)]
    if "OQ-0266" not in oq_ids:
        findings.append(Finding("fail", "oq-0266-not-selected", "context-pack does not select OQ-0266", "clean response/custody/score triplet must remain the frontier"))
    else:
        findings.append(Finding("info", "oq-0266-selected", "OQ-0266 remains the selected frontier", "the actual clean response + custody record + separate score sheet are still absent; the legacy four-packet lane remains co-visible, while the new isolated-arm pilot removes carryover but still needs four real distinct responders and cannot identify burden at n=1 per arm"))

    result = {
        "project": "DelayBasin",
        "preflight": "cloudtainer mission preflight",
        "root": str(ROOT),
        "canonical_revisions": canonical_revs,
        "working_revision": working_rev,
        "hot_current_supports_count": len(hot),
        "hot_current_additions_counts": hot_counts,
        "canon_additions_count": len(receipt.get("canon_additions", [])),
        "touched_surfaces_count": len(receipt.get("touched_surfaces", [])),
        "context_pack_bytes": (ROOT / "context-pack.json").stat().st_size,
        "manifest_path_count": len(mpaths),
        "actual_file_count": len(apaths),
        "unmanifested_path_count": len(unmanifested),
        "live_debt": archive_audit.get("live_debt", {}),
        "decay_watch_overdue": decay,
        "findings": [asdict(f) for f in findings],
        "summary_counts": {
            "fail": sum(1 for f in findings if f.severity == "fail"),
            "warn": sum(1 for f in findings if f.severity == "warn"),
            "info": sum(1 for f in findings if f.severity == "info"),
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        counts = result["summary_counts"]
        print(f"DelayBasin cloudtainer mission preflight: {counts['fail']} fail / {counts['warn']} warn / {counts['info']} info")
        for finding in findings:
            print(f"- {finding.severity.upper()} {finding.id}: {finding.summary}")
            if finding.detail:
                print(f"  {finding.detail}")
    return 1 if any(f.severity == "fail" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

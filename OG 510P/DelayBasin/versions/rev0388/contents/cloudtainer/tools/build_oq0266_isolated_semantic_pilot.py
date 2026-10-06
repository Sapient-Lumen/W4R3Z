#!/usr/bin/env python3
"""Build the runnable blinded, isolated-arm OQ-0266 semantic pilot.

Each responder ZIP contains exactly one opaque arm and no assignment mapping,
answer key, custody material, scorer material, or other arm.  A prefreeze
collector kit distributes those ZIPs and freezes one exact all-response lock;
the committed assignment plan and scorer material live in a separate
postfreeze kit that is opened only after that lock exists.

This pilot removes co-visibility, fixed packet order, and within-responder
carryover from the existing four-packet assay.  With one responder per arm it
still cannot identify causal burden differences; costs remain descriptive.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
from typing import Any

_IMPORT_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_IMPORT_ROOT / "tools"))
sys.path.insert(0, str(_IMPORT_ROOT / "cloudtainer/tools"))
from priority_zero_causal_artifact_lib import (  # type: ignore  # noqa: E402
    CURRENT_CUSTODY_CONTRACT,
    CURRENT_POLICY_VERIFICATION_CONTRACT,
    CURRENT_RESPONSE_SET_CONTRACT,
    CURRENT_SCORING_CONTRACT,
)
from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    ASSIGNMENT_COMMITMENT_CONTRACT_VERSION,
    ASSIGNMENT_COMMITMENT_RECORD_TYPE,
    RESPONDER_PACKET_PROJECTION_SCHEME,
    responder_packet_projection_sha256,
)
from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    LOCK_MEMBER,
    POLICY_RECEIPT_MEMBER,
    POSTFREEZE_KIT_MEMBER,
    PREFREEZE_KIT_MEMBER,
    RUN_BUNDLE_CONTRACT_VERSION,
    RUN_BUNDLE_RECORD_TYPE,
    RUN_BUNDLE_STATE,
    evidence_record_member,
    response_member,
    score_sheet_member,
)

ROOT = _IMPORT_ROOT
PILOT = "cloudtainer/oq0266-isolated-semantic-pilot"
BATCH_ID = "oq0266-isolated-semantic-pilot-2026-06-18"
CREATED_AT = "2026-06-18T17:31:00-04:00"
REVISION = "rev0388-working-overlay"

SOURCE_PACKET = "assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json"
SOURCE_RESPONSE_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
SOURCE_CUSTODY_TEMPLATE = "assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json"
SOURCE_SCORE_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json"
SOURCE_SCORER = "assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json"

RESPONSE_TOOL = "tools/prepare_priority_zero_external_replay_response.py"
CUSTODY_TOOL = "tools/prepare_priority_zero_clean_response_custody_record.py"
SCORE_SHEET_TOOL = "tools/prepare_priority_zero_external_replay_score_sheet.py"
SCORER_TOOL = "tools/score_priority_zero_external_replay_response.py"
ARTIFACT_LIB = "tools/priority_zero_external_run_artifact_lib.py"
RESPONSE_LIB = "tools/priority_zero_external_replay_response_lib.py"
CUSTODY_LIB = "tools/priority_zero_external_replay_custody_lib.py"
TIMELINE_LIB = "tools/priority_zero_custody_timeline_lib.py"
ASSAY_LIB = "tools/priority_zero_assay_lib.py"
DECISION_LIB = "tools/priority_zero_external_replay_decision_lib.py"
BATCH_SCORER = "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py"
RESPONSE_SET_LOCK_TOOL = "cloudtainer/tools/lock_oq0266_isolated_response_set.py"
RESPONSE_SET_LIB = "cloudtainer/tools/oq0266_isolated_response_set_lib.py"
POLICY_VERIFY_TOOL = "cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py"
SCORING_POLICY_LIB = "cloudtainer/tools/oq0266_isolated_scoring_policy_lib.py"
COMMITMENT_LIB = "cloudtainer/tools/oq0266_isolated_commitment_lib.py"
RUN_MANIFEST_TOOL = "cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py"
RUN_BUNDLE_LIB = "cloudtainer/tools/oq0266_isolated_run_bundle_lib.py"
CAUSAL_LIB = "tools/priority_zero_causal_artifact_lib.py"
RESPONSE_SET_CONTRACT_VERSION = CURRENT_RESPONSE_SET_CONTRACT
SCORING_POLICY_CONTRACT_VERSION = "preanswer-scoring-policy-v1"
POLICY_VERIFICATION_CONTRACT_VERSION = CURRENT_POLICY_VERIFICATION_CONTRACT

POLICY_TOOL_SURFACES = [
    POLICY_VERIFY_TOOL,
    SCORING_POLICY_LIB,
    COMMITMENT_LIB,
    RUN_MANIFEST_TOOL,
    RUN_BUNDLE_LIB,
    CAUSAL_LIB,
    BATCH_SCORER,
    RESPONSE_SET_LIB,
    CUSTODY_TOOL,
    SCORE_SHEET_TOOL,
    SCORER_TOOL,
    ARTIFACT_LIB,
    RESPONSE_LIB,
    CUSTODY_LIB,
    TIMELINE_LIB,
    ASSAY_LIB,
    DECISION_LIB,
]

# Opaque arm codes deliberately do not preserve canonical packet order.
ARM_ASSIGNMENTS = [
    ("arm-7f2c", "packet-bravo", "compact"),
    ("arm-b91e", "packet-alpha", "sham"),
    ("arm-d4a7", "packet-delta", "trace"),
    ("arm-e263", "packet-charlie", "baseline"),
]

FORBIDDEN_RESPONDER_TOKENS = [
    "answer_key",
    "true_variant",
    "expected_score",
    "packet-alpha",
    "packet-bravo",
    "packet-charlie",
    "packet-delta",
    "assignment-plan.json",
    "scorer-intake.json",
    "custody-template.json",
    "score_oq0266_isolated_semantic_pilot.py",
    "analysis_variant",
    "source_packet_label",
    "reference_expected_score",
]


def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write(rel: str, data: dict[str, Any]) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_text(rel: str, text: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def build_zip(
    rel: str,
    members: list[str],
    *,
    scan_forbidden: bool = False,
    forbidden_scan_members: list[str] | None = None,
    scan_self_hash: bool = False,
) -> str:
    # Import only at execution time so this file remains easy to audit.
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from priority_zero_handoff_bundle_lib import (  # type: ignore
        assert_no_embedded_bundle_hash_claims,
        build_zip_bundle,
    )

    scan_members = forbidden_scan_members if forbidden_scan_members is not None else members
    digest = build_zip_bundle(
        root=ROOT,
        bundle_rel=rel,
        members=members,
        forbidden_tokens=FORBIDDEN_RESPONDER_TOKENS if scan_forbidden else (),
        forbidden_token_members=scan_members if scan_forbidden else None,
    )
    if scan_self_hash:
        assert_no_embedded_bundle_hash_claims(ROOT, scan_members, actual_bundle_sha256=digest)
    return digest


def arm_dir(arm: str) -> str:
    return f"{PILOT}/arms/{arm}"


def arm_paths(arm: str) -> dict[str, str]:
    base = arm_dir(arm)
    return {
        "packet": f"{base}/responder-packet.json",
        "response_template": f"{base}/response-template.json",
        "responder_readme": f"{base}/RESPONDER-README.md",
        "responder_bundle": f"{base}/responder-bundle.zip",
        "custody_template": f"{base}/custody-template.json",
        "score_template": f"{base}/score-sheet-template.json",
        "scorer": f"{base}/scorer-intake.json",
    }


def make_assignment_plan(source_scorer: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for arm, source_label, variant in ARM_ASSIGNMENTS:
        source_key = source_scorer["answer_key"][source_label]
        rows.append(
            {
                "arm_code": arm,
                "source_packet_label": source_label,
                "analysis_variant": variant,
                "expected_posture": source_key["expected_posture"],
                "reference_expected_score": source_key["expected_score"],
                "responder_bundle_surface": arm_paths(arm)["responder_bundle"],
                "scorer_intake_surface": arm_paths(arm)["scorer"],
            }
        )
    return {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-assignment-plan",
        "batch_id": BATCH_ID,
        "revision": REVISION,
        "created_at": CREATED_AT,
        "assignment_state": "plan-policy-and-responder-visible-stimulus-frozen-before-responder-bundles-built-and-hidden-until-all-responses-freeze",
        "arms": rows,
        "decision_thresholds": {
            "compact_min_score": 15,
            "sham_max_score": 6,
            "baseline_max_score": 5,
            "trace_override_margin": 3,
            "support_if_trace_minus_compact_at_most": 1,
        },
        "design": {
            "responder_allocation": "one distinct responder per opaque arm",
            "arm_visibility": "one arm only; no other cue arm is present",
            "assignment_visibility": "commitment digest pre-response; mapping post-freeze only",
            "commitment_binding": "the exact commitment-file SHA-256 is embedded in every responder packet; the commitment fixes assignment-plan bytes, scoring-policy bytes, and a cycle-free digest of every responder-visible packet field except that self-referential hash",
            "batch_barrier": "a prefreeze-safe collector must lock all four exact finalized responses before the assignment mapping, custody templates, scorer intakes, or score sheets open",
            "semantic_inference": "isolated-arm bounded semantic recovery pilot",
            "burden_inference": "not identifiable from one different responder per arm; timing is descriptive only",
            "global_compact_gate_confirmation": False,
        },
        "non_claim": "not a causal burden experiment, not a global compact-default confirmation, not deletion authority, not benchmark authority, and not independent certification merely because the batch is runnable",
    }


def response_row(label: str) -> dict[str, Any]:
    return {
        "label": label,
        "operator_cost_minutes": None,
        "mission_heart": "",
        "oq_routing": "",
        "compact_gate_posture": "",
        "waste_or_refactor_implicated": "",
        "next_safe_action": "",
        "abstentions": "",
        "uncertainty_or_conflicts": "",
    }


def score_row(label: str, source_score_template: dict[str, Any]) -> dict[str, Any]:
    prototype = copy.deepcopy(source_score_template["manual_metric_scores"][0])
    prototype["label"] = label
    return prototype


def make_responder_packet(
    arm: str,
    source_row: dict[str, Any],
    paths: dict[str, str],
    commitment_rel: str,
    commitment_sha: str,
) -> dict[str, Any]:
    return {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-{arm}-responder-packet",
        "revision": REVISION,
        "surface": paths["packet"],
        "created_at": CREATED_AT,
        "batch_id": BATCH_ID,
        "arm_code": arm,
        "assignment_commitment_surface": commitment_rel,
        "assignment_commitment_sha256": commitment_sha,
        "response_template_surface": paths["response_template"],
        "instructions": "Use only this extracted responder bundle. Answer the single opaque arm from its visible cues, record positive operator time, and finalize before seeing any custody, scorer, assignment mapping, other arm, archive, or prior-conversation material.",
        "non_claim": "single blinded responder arm; not scorer material, not the assignment mapping, not custody evidence, not burden identification, not compact-gate confirmation, and not deletion authority",
        "packets": [
            {
                "label": arm,
                "packet_surfaces": copy.deepcopy(source_row["packet_surfaces"]),
                "visible_task_cues": copy.deepcopy(source_row["visible_task_cues"]),
                "response_instruction": source_row["response_instruction"],
            }
        ],
        "packet_family": BATCH_ID,
        "frontier_question": "OQ-0266",
        "responder_instruction": "Treat this as the only available cue set. Do not infer other arms or assignment. Complete every answer field; abstain explicitly where unsupported.",
        "evidence_scope": "one opaque cue arm shown to one responder with no co-visible comparison arm",
        "preanswer_material_boundary": "Exactly this responder ZIP is allowed. The assignment mapping, post-freeze batch kit, all other arms, custody/scorer material, full archive, and prior conversation remain unavailable until response freeze.",
    }


def make_response_template(
    arm: str,
    paths: dict[str, str],
    packet_sha: str,
    source_template: dict[str, Any],
) -> dict[str, Any]:
    template = copy.deepcopy(source_template)
    template.update(
        {
            "id": f"{BATCH_ID}-{arm}-response-template",
            "revision": REVISION,
            "surface": paths["response_template"],
            "created_at": CREATED_AT,
            "responder_packet_surface": paths["packet"],
            "responder_only_surface": paths["packet"],
            "responder_packet_sha256": packet_sha,
            "responder_bundle_surface": paths["responder_bundle"],
            "non_claim": "blank isolated-arm response template; not a completed response, not assignment disclosure, not custody evidence, and not a score sheet",
            "instructions": "Run the bundled init helper, fill only the one arm answer row and matching total cost, then run finalize with explicit clean-preanswer attestation before any post-freeze material opens.",
            "evidence_scope_boundary": "This artifact can support only its single opaque arm. Cross-arm interpretation occurs after all responses freeze.",
        }
    )
    template["responder_stage"]["packet_answers"] = [response_row(arm)]
    template["responder_stage"]["operator_cost_rule"] = "Set one positive finite arm cost and the same positive finite run total; finalization rejects disagreement beyond 0.05 minutes."
    if isinstance(template.get("post_response_scoring_boundary"), dict):
        template["post_response_scoring_boundary"]["score_sheet_template_surface"] = paths["score_template"]
    return template


def make_custody_template(
    arm: str,
    paths: dict[str, str],
    bundle_sha: str,
    packet_sha: str,
    response_template_sha: str,
    source_template: dict[str, Any],
) -> dict[str, Any]:
    template = copy.deepcopy(source_template)
    template.update(
        {
            "id": f"{BATCH_ID}-{arm}-custody-template",
            "revision": REVISION,
            "surface": paths["custody_template"],
            "created_at": CREATED_AT,
            "responder_bundle_surface": paths["responder_bundle"],
            "responder_bundle_sha256": bundle_sha,
            "responder_only_surface": paths["packet"],
            "responder_only_sha256": packet_sha,
            "response_template_surface": paths["response_template"],
            "response_template_sha256": response_template_sha,
            "non_claim": "isolated-arm custody template only; not a completed custody record, not assignment disclosure, not scoring, and not independent certification",
        }
    )
    template["custodian_attestation"]["pre_response_materials_given"] = paths["responder_bundle"]
    template["required_prerequisite_labels"] = [
        "response-set-lock",
        "postfreeze-policy-verification",
    ]
    template["prerequisite_artifacts"] = []
    template["preanswer_material_boundary"] = "Clean arm evidence is admissible only when the named one-arm responder bundle was the sole pre-response material."
    template["causal_chain_boundary"] = "Custody must bind the exact all-response lock and exact postfreeze-policy verification receipt by SHA-256. Independent operator clocks remain descriptive and are never compared across machines."
    return template


def make_score_template(
    arm: str,
    paths: dict[str, str],
    source_template: dict[str, Any],
) -> dict[str, Any]:
    template = copy.deepcopy(source_template)
    template.update(
        {
            "id": f"{BATCH_ID}-{arm}-score-sheet-template",
            "revision": REVISION,
            "surface": paths["score_template"],
            "created_at": CREATED_AT,
            "scorer_intake_surface": paths["scorer"],
            "non_claim": "isolated-arm score-sheet template only; not a completed score, not cross-arm inference, and not compact-gate confirmation",
            "rationale_boundary": "Every metric for the one opaque arm requires a concise evidence-grounded rationale, including zero scores.",
        }
    )
    template["manual_metric_scores"] = [score_row(arm, source_template)]
    return template


def make_scorer_policy(
    arm: str,
    source_label: str,
    variant: str,
    source_scorer: dict[str, Any],
) -> dict[str, Any]:
    key = copy.deepcopy(source_scorer["answer_key"][source_label])
    key["source_packet_label"] = source_label
    key["analysis_variant"] = variant
    return {
        "project": "DelayBasin",
        "batch_id": BATCH_ID,
        "arm_code": arm,
        "required_answer_fields": copy.deepcopy(source_scorer["required_answer_fields"]),
        "required_response_checks": [
            "The response is a responder-finalize-v1 artifact for exactly this opaque arm.",
            "The response, custody record, and score sheet are byte-bound to current templates and one-arm bundle identity.",
            "The exact response, all-response lock, postfreeze-policy receipt, custody record, and score sheet form a complete causal hash chain; wall clocks are ordered only within their producing process.",
            "Every metric has an evidence rationale and the arm has a packet note.",
        ],
        "required_attestations": copy.deepcopy(source_scorer["required_attestations"]),
        "requires_custody_evidence_record": True,
        "requires_bound_custody_record_file": True,
        "requires_bound_score_sheet_file": True,
        "requires_separate_score_sheet": True,
        "requires_distinct_scorer_from_responder": True,
        "requires_distinct_custodian": True,
        "requires_responder_id_match": True,
        "requires_custody_timeline_order": True,
        "requires_pre_response_material_exact_match": True,
        "requires_score_sheet_chronology": True,
        "requires_metric_rationales": True,
        "requires_packet_score_notes": True,
        "requires_per_packet_operator_cost": True,
        "requires_operator_cost_sum_match": True,
        "operator_cost_sum_tolerance_minutes": 0.05,
        "allowed_pre_response_materials": [arm_paths(arm)["responder_bundle"]],
        "forbidden_pre_response_material_tokens": copy.deepcopy(source_scorer["forbidden_pre_response_material_tokens"]),
        "metrics": copy.deepcopy(source_scorer["metrics"]),
        "answer_key": {arm: key},
        "scoring_order": [
            "Verify the exact one-arm response/custody/score-sheet hash chain and producer-local chronology.",
            "Apply every metric to the opaque arm with an evidence rationale.",
            "Record the arm score; do not issue cross-arm or burden conclusions here.",
        ],
        "scoring_rule": "Score this arm only. The batch aggregator reveals the committed mapping after all four arms freeze. Per-arm scoring cannot confirm a compact default or compare burden.",
        "decision_evidence_scope": {
            "design": "one-responder one-arm blinded isolated semantic pilot",
            "supports": ["bounded semantic score for this arm", "descriptive arm completion time"],
            "does_not_support": ["cross-arm burden causality", "global compact-default confirmation", "deletion authority"],
        },
        "full_archive_control_state": "No within-responder full-archive control exists in this isolated arm; the trace arm is a bounded excerpt and uses a different responder.",
        "allows_global_compact_gate_confirmation": False,
        "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
        "required_custody_evidence_state": "completed-response-and-causal-custody-record-frozen-before-scorer-kit",
        "scoring_contract_version": CURRENT_SCORING_CONTRACT,
        "required_custody_attestations": copy.deepcopy(source_scorer["required_custody_attestations"]),
        "required_score_sheet_attestations": copy.deepcopy(source_scorer["required_score_sheet_attestations"]),
        "response_preparation_contract_version": "responder-finalize-v1",
        "requires_tool_finalized_response": True,
        "non_claim": "post-freeze one-arm scorer intake; not a clean response itself, not burden identification, not global compact-gate confirmation, not deletion authority, and not benchmark authority",
    }


def make_scorer(
    arm: str,
    paths: dict[str, str],
    bundle_sha: str,
    packet_sha: str,
    response_template_sha: str,
    custody_template_sha: str,
    score_template_sha: str,
    scorer_policy: dict[str, Any],
    postfreeze_kit_rel: str,
    scoring_policy_rel: str,
    scoring_policy_sha: str,
) -> dict[str, Any]:
    """Merge precommitted policy with post-build artifact bindings."""
    return {
        "id": f"{BATCH_ID}-{arm}-scorer-intake",
        "revision": REVISION,
        "surface": paths["scorer"],
        "created_at": CREATED_AT,
        "responder_only_surface": paths["packet"],
        "responder_only_sha256": packet_sha,
        "response_template_surface": paths["response_template"],
        "response_template_sha256": response_template_sha,
        "responder_bundle_surface": paths["responder_bundle"],
        "responder_bundle_sha256": bundle_sha,
        "evidence_record_template_surface": paths["custody_template"],
        "evidence_record_template_sha256": custody_template_sha,
        "score_sheet_template_surface": paths["score_template"],
        "score_sheet_template_sha256": score_template_sha,
        "scorer_kit_surface": postfreeze_kit_rel,
        "custody_kit_surface": postfreeze_kit_rel,
        "scoring_policy_surface": scoring_policy_rel,
        "scoring_policy_sha256": scoring_policy_sha,
        **copy.deepcopy(scorer_policy),
    }


def responder_readme(arm: str, paths: dict[str, str]) -> str:
    return f"""# OQ-0266 isolated responder arm `{arm}`

You have exactly one opaque cue arm. Do not seek another arm or open any post-freeze material.

From the extracted bundle root, preserve the original ZIP and run:

```sh
python -S {RESPONSE_TOOL} init \\
  --bundle-file /path/to/original-{arm}-responder-bundle.zip \\
  --responder-id YOUR-STABLE-ID \\
  --template {paths['response_template']} \\
  --packet {paths['packet']} \\
  --out {arm}-response-draft.json
```

Fill only the single packet answer row, its positive `operator_cost_minutes`, and the equal run total. Then, before seeing custody, scorer, assignment, other-arm, archive, manifest, or prior-conversation material:

```sh
python -S {RESPONSE_TOOL} finalize \\
  --draft {arm}-response-draft.json \\
  --bundle-file /path/to/original-{arm}-responder-bundle.zip \\
  --template {paths['response_template']} \\
  --packet {paths['packet']} \\
  --exposure-notes 'only the one-arm responder bundle was visible' \\
  --attest-clean-preanswer \\
  --out {arm}-response-final.json
```

Give the exact final file to a distinct custodian. Do not edit it. Timing is descriptive only because each arm uses a different responder.
"""


def _shell_command(lines: list[str]) -> str:
    return (" " + chr(92) + "\n").join(lines)


def dispatch_readme(
    prefreeze_kit_rel: str,
    dispatch_manifest_rel: str,
    commitment_rel: str,
) -> str:
    lock_command = _shell_command([
        f"python -S {RESPONSE_SET_LOCK_TOOL}",
        *[
            f"  --response {arm}=/path/to/{arm}-response-final.json"
            for arm, _, _ in ARM_ASSIGNMENTS
        ],
        "  --collector-id YOUR-STABLE-COLLECTOR-ID",
        "  --exposure-notes 'only the prefreeze dispatch kit and four finalized responses were visible'",
        "  --attest-clean-batch-barrier",
        f"  --dispatch-manifest {dispatch_manifest_rel}",
        f"  --commitment {commitment_rel}",
        "  --out /path/to/oq0266-response-set-lock.json",
    ])
    policy_verify_command = _shell_command([
        f"python -S {POLICY_VERIFY_TOOL}",
        "  --response-set-lock /path/to/oq0266-response-set-lock.json",
        "  --postfreeze-root /path/to/extracted-postfreeze-kit",
        "  --verifier-id YOUR-STABLE-VERIFIER-ID",
        "  --attest-postfreeze-opened-after-lock",
        "  --out /path/to/oq0266-postfreeze-policy-verification.json",
    ])
    return f"""# OQ-0266 isolated semantic pilot — prefreeze dispatch kit

This is the only pilot-wide kit that may be opened before all four responses freeze. Do not open the full DelayBasin cube, the postfreeze kit, the assignment plan, custody templates, scorer intakes, or score sheets during collection.

Distribute exactly one nested responder ZIP to each genuinely separate responder. Never give a responder this whole dispatch kit or another arm. Preserve every original nested ZIP.

After all four finalized response JSON files return, but before opening any postfreeze material, run from this extracted kit root:

```sh
{lock_command}
```

The command revalidates each exact response from the nested one-arm bundle, verifies that every responder-visible packet projection still matches the preanswer commitment, requires four distinct responder IDs plus a distinct collector, and freezes all response hashes plus collector-local receipt times in one read-only lock. Responder-reported times remain descriptive and are not compared to the collector clock. Only after that command succeeds may the postfreeze kit open.

After opening the postfreeze kit, but before custody or scoring begins, verify that its hidden assignment, scoring rules, exact responder-visible packet projections, scorer intakes, and executable validators match the commitment fixed before response:

```sh
{policy_verify_command}
```

Do not begin custody or scoring unless this no-clobber verifier succeeds. The final batch scorer revalidates the receipt against the current files, so later policy or tool substitution remains detectable.

Kit surface: `{prefreeze_kit_rel}`. Exact artifact hashes carry cross-operator ordering; local clocks and string identities are recorded observations, not trusted timestamping or proof of real-world independence.
"""


def batch_readme(
    postfreeze_kit_rel: str,
    prefreeze_kit_rel: str,
) -> str:
    custody_example = _shell_command([
        f"python -S {CUSTODY_TOOL}",
        "  /path/to/ARM-response-final.json",
        "  --custodian-id DISTINCT-CUSTODIAN-ID",
        "  --pre-response-exposure-notes 'only the named one-arm responder bundle was visible before response'",
        "  --prerequisite response-set-lock=/path/to/oq0266-response-set-lock.json",
        "  --prerequisite postfreeze-policy-verification=/path/to/oq0266-postfreeze-policy-verification.json",
        "  --attest-clean-preanswer",
        f"  --template {PILOT}/arms/ARM/custody-template.json",
        f"  --response-template {PILOT}/arms/ARM/response-template.json",
        "  --out /path/to/ARM-custody-final.json",
    ])
    score_init_example = _shell_command([
        f"python -S {SCORE_SHEET_TOOL} init",
        "  /path/to/ARM-response-final.json",
        "  /path/to/ARM-custody-final.json",
        "  --scorer-id DISTINCT-SCORER-ID",
        f"  --scorer-intake {PILOT}/arms/ARM/scorer-intake.json",
        f"  --template {PILOT}/arms/ARM/score-sheet-template.json",
        f"  --response-template {PILOT}/arms/ARM/response-template.json",
        "  --out /path/to/ARM-score-draft.json",
    ])
    score_finalize_example = _shell_command([
        f"python -S {SCORE_SHEET_TOOL} finalize",
        "  /path/to/ARM-response-final.json",
        "  /path/to/ARM-custody-final.json",
        "  --draft /path/to/ARM-score-draft.json",
        "  --scorer-id DISTINCT-SCORER-ID",
        f"  --scorer-intake {PILOT}/arms/ARM/scorer-intake.json",
        f"  --template {PILOT}/arms/ARM/score-sheet-template.json",
        f"  --response-template {PILOT}/arms/ARM/response-template.json",
        "  --scorer-notes 'evidence-grounded one-arm scoring completed after custody validation'",
        "  --attest-separated-scoring",
        "  --out /path/to/ARM-score-final.json",
    ])
    assembly_command = _shell_command([
        f"python -S {RUN_MANIFEST_TOOL}",
        "  --prefreeze-dispatch-kit /path/to/original-prefreeze-dispatch-kit.zip",
        "  --postfreeze-batch-kit /path/to/original-postfreeze-batch-kit.zip",
        "  --response-set-lock /path/to/oq0266-response-set-lock.json",
        "  --policy-verification /path/to/oq0266-postfreeze-policy-verification.json",
        *[f"  --response {arm}=/path/to/{arm}-response-final.json" for arm, _, _ in ARM_ASSIGNMENTS],
        *[f"  --evidence-record {arm}=/path/to/{arm}-custody-final.json" for arm, _, _ in ARM_ASSIGNMENTS],
        *[f"  --score-sheet {arm}=/path/to/{arm}-score-final.json" for arm, _, _ in ARM_ASSIGNMENTS],
        f"  --template {PILOT}/run-manifest-template.json",
        "  --out /path/to/oq0266-isolated-run-bundle.zip",
    ])
    scoring_command = _shell_command([
        f"python -S {BATCH_SCORER}",
        "  --run-bundle /path/to/oq0266-isolated-run-bundle.zip",
        "  --expected-run-bundle-sha256 PASTE-SEPARATELY-PRESERVED-SHA256",
        "  --summary-out /path/to/isolated-batch-summary.json",
    ])
    return f"""# OQ-0266 isolated semantic pilot — postfreeze batch kit

Open this kit only after the prefreeze collector has produced the exact four-response lock. Verify the newly opened policy kit before custody or scoring, and preserve both read-only receipts. Cross-operator order is carried by exact artifact hashes; each tool checks clock order only inside its own process.

For each arm, replace `ARM` with its opaque arm code and run custody with both prerequisite receipts:

```sh
{custody_example}
```

Then initialize the score sheet, fill every metric score/rationale plus the packet note, and finalize it:

```sh
{score_init_example}
# edit only the draft's scoring fields
{score_finalize_example}
```

After all four exact triplets exist, do **not** hand-edit hashes into the template. Preserve the original prefreeze and postfreeze ZIPs, then assemble one self-contained evidence capsule in one command:

```sh
{assembly_command}
```

Copy the SHA-256 printed by the assembler into a separate custody note or digest file. Only then run the final aggregator against the capsule and that separately preserved digest:

```sh
{scoring_command}
```

The assembler fails before publication when either source kit is malformed or differs from the executing postfreeze root, an arm is missing, a response differs from the all-response lock, custody omits or substitutes either prerequisite receipt, or a score sheet does not bind the exact response and custody bytes. It copies both exact source kits and every dynamic artifact into one deterministic evidence capsule with an internal checksum manifest. The aggregator requires the separately preserved outer SHA-256, parses every nested ZIP with path and size bounds, replays only captured source-kit bytes, and refuses causal burden or global compact-default claims. Ambient pilot files may be deleted or mutated without changing replay.

Kit surface: `{postfreeze_kit_rel}`. Local wall clocks and string identities remain descriptive observations, not trusted timestamping or proof of real-world independence.
"""

def main() -> None:
    source_packet = load(SOURCE_PACKET)
    source_response_template = load(SOURCE_RESPONSE_TEMPLATE)
    source_custody_template = load(SOURCE_CUSTODY_TEMPLATE)
    source_score_template = load(SOURCE_SCORE_TEMPLATE)
    source_scorer = load(SOURCE_SCORER)
    source_rows = {row["label"]: row for row in source_packet["packets"]}

    assignment_rel = f"{PILOT}/assignment-plan.json"
    commitment_rel = f"{PILOT}/assignment-commitment.json"
    scoring_policy_rel = f"{PILOT}/scoring-policy.json"
    run_manifest_rel = f"{PILOT}/run-manifest-template.json"
    dispatch_manifest_rel = f"{PILOT}/dispatch-manifest.json"
    batch_manifest_rel = f"{PILOT}/batch-manifest.json"
    dispatch_readme_rel = f"{PILOT}/PREFREEZE-README.md"
    batch_readme_rel = f"{PILOT}/POSTFREEZE-README.md"
    prefreeze_kit_rel = f"{PILOT}/prefreeze-dispatch-kit.zip"
    postfreeze_kit_rel = f"{PILOT}/postfreeze-batch-kit.zip"

    assignment = make_assignment_plan(source_scorer)
    write(assignment_rel, assignment)
    assignment_sha = sha(assignment_rel)
    scorer_policies = {
        arm: make_scorer_policy(arm, source_label, variant, source_scorer)
        for arm, source_label, variant in ARM_ASSIGNMENTS
    }
    scoring_policy = {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-scoring-policy",
        "record_type": "isolated-scoring-policy",
        "scoring_policy_contract_version": SCORING_POLICY_CONTRACT_VERSION,
        "batch_id": BATCH_ID,
        "revision": REVISION,
        "created_at": CREATED_AT,
        "assignment_plan_sha256": assignment_sha,
        "required_variants": ["baseline", "compact", "sham", "trace"],
        "decision_thresholds": copy.deepcopy(assignment["decision_thresholds"]),
        "global_requirements": {
            "all_responses_before_postfreeze": True,
            "distinct_responder_per_arm": True,
            "collector_distinct_from_responders": True,
            "custodian_distinct_from_responder": True,
            "scorer_distinct_from_responder": True,
            "custody_before_scoring": True,
            "metric_rationales_required": True,
            "packet_notes_required": True,
            "positive_per_packet_cost_required": True,
            "cost_sum_match_required": True,
            "strict_json_required": True,
            "current_tool_hashes_required": True,
            "cross_operator_order_carried_by_exact_artifact_receipts": True,
            "manual_run_manifest_hash_transcription_forbidden": True,
            "self_contained_source_kit_evidence_capsule_required": True,
            "separately_preserved_outer_digest_required": True,
            "bounded_safe_nested_zip_parsing_required": True,
            "postassembly_dynamic_or_source_artifact_replacement_rejected": True,
        },
        "tool_sha256_by_surface": {surface: sha(surface) for surface in POLICY_TOOL_SURFACES},
        "arms": [
            {
                "arm_code": arm,
                "scorer_policy": scorer_policies[arm],
            }
            for arm, _, _ in ARM_ASSIGNMENTS
        ],
        "non_claim": "preanswer digest-bound scoring and admissibility policy; hidden until all responses freeze and not itself a completed score, trusted timestamp, identity proof, or external result",
    }
    write(scoring_policy_rel, scoring_policy)
    scoring_policy_sha = sha(scoring_policy_rel)

    # Construct every responder-visible packet before the commitment.  The
    # projection excludes only assignment_commitment_sha256, avoiding a hash
    # cycle while fixing every cue, instruction, path, and boundary.
    packet_drafts: dict[str, dict[str, Any]] = {}
    packet_projection_sha_by_arm: dict[str, str] = {}
    for arm, source_label, _variant in ARM_ASSIGNMENTS:
        paths = arm_paths(arm)
        packet_draft = make_responder_packet(
            arm,
            source_rows[source_label],
            paths,
            commitment_rel,
            "PENDING-COMMITMENT-SHA256",
        )
        packet_drafts[arm] = packet_draft
        packet_projection_sha_by_arm[arm] = responder_packet_projection_sha256(
            packet_draft
        )

    commitment = {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-assignment-commitment",
        "record_type": ASSIGNMENT_COMMITMENT_RECORD_TYPE,
        "commitment_contract_version": ASSIGNMENT_COMMITMENT_CONTRACT_VERSION,
        "batch_id": BATCH_ID,
        "revision": REVISION,
        "created_at": CREATED_AT,
        "commitment_scheme": "sha256-of-exact-assignment-plan-and-scoring-policy-file-bytes-plus-cycle-free-responder-packet-projections",
        "assignment_plan_sha256": assignment_sha,
        "scoring_policy_contract_version": SCORING_POLICY_CONTRACT_VERSION,
        "scoring_policy_sha256": scoring_policy_sha,
        "responder_packet_projection_scheme": RESPONDER_PACKET_PROJECTION_SCHEME,
        "responder_packet_projection_sha256_by_arm": packet_projection_sha_by_arm,
        "opaque_arm_codes": sorted(arm for arm, _, _ in ARM_ASSIGNMENTS),
        "mapping_visibility": "assignment mapping and scoring policy content remain hidden until the all-response lock; opaque per-arm digests fix the complete responder-visible packet projection without revealing the mapping",
        "non_claim": "digest commitment only; it fixes assignment, scoring policy, and exact responder-visible packet projections before response, but does not prove trusted publication time, real-world identity separation, or clean execution",
    }
    write(commitment_rel, commitment)
    commitment_sha = sha(commitment_rel)

    arm_manifest_rows: list[dict[str, Any]] = []
    for arm, source_label, variant in ARM_ASSIGNMENTS:
        paths = arm_paths(arm)
        packet = copy.deepcopy(packet_drafts[arm])
        packet["assignment_commitment_sha256"] = commitment_sha
        if responder_packet_projection_sha256(packet) != packet_projection_sha_by_arm[arm]:
            raise RuntimeError(f"{arm} responder-packet projection changed while binding commitment")
        write(paths["packet"], packet)
        response_template = make_response_template(
            arm,
            paths,
            sha(paths["packet"]),
            source_response_template,
        )
        write(paths["response_template"], response_template)
        write_text(paths["responder_readme"], responder_readme(arm, paths))
        responder_members = [
            paths["packet"],
            paths["response_template"],
            paths["responder_readme"],
            commitment_rel,
            RESPONSE_TOOL,
            ARTIFACT_LIB,
            RESPONSE_LIB,
        ]
        bundle_sha = build_zip(
            paths["responder_bundle"],
            responder_members,
            scan_forbidden=True,
            scan_self_hash=True,
        )

        custody_template = make_custody_template(
            arm,
            paths,
            bundle_sha,
            sha(paths["packet"]),
            sha(paths["response_template"]),
            source_custody_template,
        )
        write(paths["custody_template"], custody_template)
        score_template = make_score_template(arm, paths, source_score_template)
        write(paths["score_template"], score_template)
        scorer = make_scorer(
            arm,
            paths,
            bundle_sha,
            sha(paths["packet"]),
            sha(paths["response_template"]),
            sha(paths["custody_template"]),
            sha(paths["score_template"]),
            scorer_policies[arm],
            postfreeze_kit_rel,
            scoring_policy_rel,
            scoring_policy_sha,
        )
        write(paths["scorer"], scorer)
        arm_manifest_rows.append(
            {
                "arm_code": arm,
                "responder_bundle_surface": paths["responder_bundle"],
                "responder_bundle_sha256": bundle_sha,
                "responder_bundle_members": responder_members,
                "responder_packet_surface": paths["packet"],
                "responder_packet_sha256": sha(paths["packet"]),
                "responder_packet_projection_sha256": packet_projection_sha_by_arm[arm],
                "response_template_surface": paths["response_template"],
                "response_template_sha256": sha(paths["response_template"]),
                "custody_template_surface": paths["custody_template"],
                "custody_template_sha256": sha(paths["custody_template"]),
                "score_sheet_template_surface": paths["score_template"],
                "score_sheet_template_sha256": sha(paths["score_template"]),
                "scorer_intake_surface": paths["scorer"],
                "scorer_intake_sha256": sha(paths["scorer"]),
            }
        )

    dispatch_manifest = {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-prefreeze-dispatch-manifest",
        "batch_id": BATCH_ID,
        "revision": REVISION,
        "created_at": CREATED_AT,
        "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
        "assignment_commitment_surface": commitment_rel,
        "assignment_commitment_sha256": commitment_sha,
        "arm_count": len(arm_manifest_rows),
        "minimum_distinct_responders": 4,
        "arms": [
            {
                "arm_code": row["arm_code"],
                "responder_bundle_surface": row["responder_bundle_surface"],
                "responder_bundle_sha256": row["responder_bundle_sha256"],
                "responder_bundle_members": row["responder_bundle_members"],
                "responder_packet_surface": row["responder_packet_surface"],
                "responder_packet_sha256": row["responder_packet_sha256"],
                "responder_packet_projection_sha256": row["responder_packet_projection_sha256"],
                "response_template_surface": row["response_template_surface"],
                "response_template_sha256": row["response_template_sha256"],
            }
            for row in arm_manifest_rows
        ],
        "prefreeze_visibility_boundary": "Only this dispatch manifest, the assignment commitment, the collector lock tool/library, and four nested one-arm responder ZIPs may be visible before the response-set lock.",
        "postfreeze_visibility_boundary": "Assignment mapping, custody templates, scorer intakes, score sheets, batch thresholds, and aggregation remain unavailable until the response-set lock exists.",
        "non_claim": "opaque dispatch metadata only; not an assignment mapping, scorer key, custody record, trusted timestamp, identity proof, or completed pilot",
    }
    write(dispatch_manifest_rel, dispatch_manifest)
    write_text(
        dispatch_readme_rel,
        dispatch_readme(prefreeze_kit_rel, dispatch_manifest_rel, commitment_rel),
    )
    prefreeze_text_members = [
        dispatch_manifest_rel,
        commitment_rel,
        dispatch_readme_rel,
        RESPONSE_SET_LOCK_TOOL,
        RESPONSE_SET_LIB,
        POLICY_VERIFY_TOOL,
        SCORING_POLICY_LIB,
        COMMITMENT_LIB,
        CAUSAL_LIB,
        ARTIFACT_LIB,
        RESPONSE_LIB,
    ]
    # Source validators necessarily name the keys they reject, so the raw-token
    # leak scan is limited to declarative prefreeze metadata/readme surfaces.
    # Executable source is audited structurally by the extracted-kit canary.
    prefreeze_forbidden_scan_members = [
        dispatch_manifest_rel,
        commitment_rel,
        dispatch_readme_rel,
    ]
    prefreeze_members = [
        *prefreeze_text_members,
        *[row["responder_bundle_surface"] for row in arm_manifest_rows],
    ]
    prefreeze_sha = build_zip(
        prefreeze_kit_rel,
        prefreeze_members,
        scan_forbidden=True,
        forbidden_scan_members=prefreeze_forbidden_scan_members,
    )

    run_manifest = {
        "project": "DelayBasin",
        "record_type": RUN_BUNDLE_RECORD_TYPE,
        "run_bundle_contract_version": RUN_BUNDLE_CONTRACT_VERSION,
        "run_bundle_state": RUN_BUNDLE_STATE,
        "batch_id": BATCH_ID,
        "assignment_plan_sha256": assignment_sha,
        "prefreeze_dispatch_kit_member": PREFREEZE_KIT_MEMBER,
        "prefreeze_dispatch_kit_sha256": "FILL-WITH-EXACT-PREFREEZE-DISPATCH-KIT-SHA256",
        "postfreeze_batch_kit_member": POSTFREEZE_KIT_MEMBER,
        "postfreeze_batch_kit_sha256": "FILL-WITH-EXACT-POSTFREEZE-BATCH-KIT-SHA256",
        "response_set_lock_member": LOCK_MEMBER,
        "response_set_lock_sha256": "FILL-WITH-EXACT-RESPONSE-SET-LOCK-SHA256",
        "postfreeze_policy_verification_member": POLICY_RECEIPT_MEMBER,
        "postfreeze_policy_verification_sha256": "FILL-WITH-EXACT-POLICY-VERIFICATION-RECEIPT-SHA256",
        "arms": [
            {
                "arm_code": arm,
                "response_member": response_member(arm),
                "response_file_sha256": "FILL-WITH-FROZEN-RESPONSE-SHA256",
                "evidence_record_member": evidence_record_member(arm),
                "evidence_record_file_sha256": "FILL-WITH-FROZEN-CUSTODY-SHA256",
                "score_sheet_member": score_sheet_member(arm),
                "score_sheet_file_sha256": "FILL-WITH-FROZEN-SCORE-SHEET-SHA256",
            }
            for arm, _, _ in ARM_ASSIGNMENTS
        ],
        "non_claim": "self-contained exact-byte evidence-capsule template only; preserve the published outer SHA-256 separately and determine evidence state by strict aggregation",
    }
    write(run_manifest_rel, run_manifest)
    write_text(batch_readme_rel, batch_readme(postfreeze_kit_rel, prefreeze_kit_rel))

    batch_manifest = {
        "project": "DelayBasin",
        "id": f"{BATCH_ID}-batch-manifest",
        "batch_id": BATCH_ID,
        "revision": REVISION,
        "created_at": CREATED_AT,
        "assignment_plan_surface": assignment_rel,
        "assignment_plan_sha256": assignment_sha,
        "scoring_policy_surface": scoring_policy_rel,
        "scoring_policy_sha256": scoring_policy_sha,
        "scoring_policy_contract_version": SCORING_POLICY_CONTRACT_VERSION,
        "policy_verification_contract_version": POLICY_VERIFICATION_CONTRACT_VERSION,
        "assignment_commitment_surface": commitment_rel,
        "assignment_commitment_sha256": commitment_sha,
        "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
        "run_bundle_contract_version": RUN_BUNDLE_CONTRACT_VERSION,
        "dispatch_manifest_surface": dispatch_manifest_rel,
        "dispatch_manifest_sha256": sha(dispatch_manifest_rel),
        "prefreeze_dispatch_kit_surface": prefreeze_kit_rel,
        "prefreeze_dispatch_kit_sha256": prefreeze_sha,
        "arms": arm_manifest_rows,
        "postfreeze_kit_surface": postfreeze_kit_rel,
        "postfreeze_kit_sha256_note": "Recorded outside this self-containing manifest after build; do not embed a self-hash claim.",
        "minimum_distinct_responders": 4,
        "minimum_distinct_operators_per_arm": 2,
        "required_batch_barrier": f"all four exact responder-tool-finalized responses must be frozen into one {RESPONSE_SET_CONTRACT_VERSION} lock, hidden postfreeze policy and responder-visible packet projections must verify against the preanswer commitment before custody/scoring, and both exact source kits plus every final dynamic artifact must be frozen into one outer-digest-pinned {RUN_BUNDLE_CONTRACT_VERSION} evidence capsule before aggregation",
        "commitment_binding": "assignment commitment file hash embedded in every responder packet binds exact assignment-plan bytes, exact scoring-policy bytes, and each complete responder-visible packet projection excluding only the self-referential commitment hash",
        "inference_boundary": "Semantic thresholding only. One different responder per arm removes carryover but confounds timing with responder identity.",
    }
    write(batch_manifest_rel, batch_manifest)

    postfreeze_members = [
        assignment_rel,
        scoring_policy_rel,
        commitment_rel,
        dispatch_manifest_rel,
        batch_manifest_rel,
        run_manifest_rel,
        batch_readme_rel,
        BATCH_SCORER,
        RUN_MANIFEST_TOOL,
        RUN_BUNDLE_LIB,
        RESPONSE_SET_LIB,
        POLICY_VERIFY_TOOL,
        SCORING_POLICY_LIB,
        COMMITMENT_LIB,
        CAUSAL_LIB,
        CUSTODY_TOOL,
        SCORE_SHEET_TOOL,
        SCORER_TOOL,
        ARTIFACT_LIB,
        RESPONSE_LIB,
        CUSTODY_LIB,
        TIMELINE_LIB,
        ASSAY_LIB,
        DECISION_LIB,
    ]
    for row in arm_manifest_rows:
        postfreeze_members.extend(
            [
                row["responder_packet_surface"],
                row["response_template_surface"],
                row["custody_template_surface"],
                row["score_sheet_template_surface"],
                row["scorer_intake_surface"],
            ]
        )
    postfreeze_sha = build_zip(postfreeze_kit_rel, postfreeze_members)

    root_readme = f"""# OQ-0266 isolated semantic pilot

This runnable pilot replaces co-visible fixed-order packets with four opaque one-arm responder bundles, a hard all-response batch barrier, and a preanswer commitment that fixes the hidden assignment, scoring/admissibility policy, and exact responder-visible packet projections before any responder answers. The execution surfaces are intentionally split:

- Prefreeze dispatch kit: `{prefreeze_kit_rel}` (`{prefreeze_sha}`). This is the only pilot-wide kit allowed before all responses freeze.
- Postfreeze batch kit: `{postfreeze_kit_rel}` (`{postfreeze_sha}`). Open only after the dispatch tool emits the exact response-set lock.

The full DelayBasin cube, this builder source, and the postfreeze kit reveal mapping/scoring material and are **not prefreeze-safe**. A collector should open only the prefreeze dispatch kit, distribute one nested responder ZIP per distinct responder, lock all four returned response bytes, then verify the newly opened postfreeze kit against the preanswer policy commitment before handing control to custody/scoring.

Responder bundles:
""" + "\n".join(
        f"- `{row['arm_code']}`: `{row['responder_bundle_surface']}` (`{row['responder_bundle_sha256']}`)"
        for row in arm_manifest_rows
    ) + f"""

The final evidence capsule binds both source kits and every dynamic artifact, and its outer SHA-256 must be preserved separately before scoring. Replay no longer depends on mutable ambient pilot files. The pilot can supply cleaner isolated semantic evidence. It cannot identify causal burden from one different responder per arm, cannot prove real-world identity separation or trusted time, cannot confirm a global compact default, and cannot replace the still-missing conventional external OQ-0266 triplet.
"""
    write_text(f"{PILOT}/README.md", root_readme)

    receipt = {
        "project": "DelayBasin",
        "batch_id": BATCH_ID,
        "assignment_plan_sha256": assignment_sha,
        "scoring_policy_sha256": scoring_policy_sha,
        "assignment_commitment_sha256": commitment_sha,
        "dispatch_manifest_sha256": sha(dispatch_manifest_rel),
        "prefreeze_dispatch_kit_sha256": prefreeze_sha,
        "postfreeze_batch_kit_sha256": postfreeze_sha,
        "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
        "run_bundle_contract_version": RUN_BUNDLE_CONTRACT_VERSION,
        "arm_count": len(arm_manifest_rows),
        "responder_bundle_sha256_by_arm": {
            row["arm_code"]: row["responder_bundle_sha256"] for row in arm_manifest_rows
        },
        "scoring_policy_contract_version": SCORING_POLICY_CONTRACT_VERSION,
        "policy_verification_contract_version": POLICY_VERIFICATION_CONTRACT_VERSION,
        "design_state": "runnable-isolated-semantic-pilot-with-self-contained-outer-digest-pinned-evidence-capsule-not-yet-externally-executed",
        "commitment_binding_state": "assignment-plan-scoring-policy-and-responder-visible-packet-projections-bound-before-response",
        "batch_barrier_state": "all-arm-response-lock-policy-receipts-source-kits-and-final-triplets-content-bundled",
        "positive_canaries": [
            "cross-machine-clock-skew-accepted",
            "self-contained-capsule-replay-without-ambient-pilot-files",
            "postassembly-source-score-mutation-isolated",
            "separately-pinned-outer-digest-accepted",
        ],
        "negative_canaries": [
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
        ],
        "burden_inference_state": "not-identifiable-between-subjects-n1-per-arm",
    }
    write(f"{PILOT}/build-receipt.json", receipt)

    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

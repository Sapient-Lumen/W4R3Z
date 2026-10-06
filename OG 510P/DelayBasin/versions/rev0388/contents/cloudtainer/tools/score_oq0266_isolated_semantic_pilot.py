#!/usr/bin/env python3
"""Validate and aggregate the blinded four-arm OQ-0266 semantic pilot.

The command revalidates each exact response/custody/score-sheet triplet under
its one-arm scorer intake, verifies the pre-response assignment commitment,
requires a distinct responder for every arm, and enforces a batch-level lock
showing all four responses froze before any custody/scorer stage opened.  It
applies only bounded semantic thresholds.  Per-arm costs are reported but never
used as causal burden evidence because responder identity differs by arm and
n=1 per arm.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import shutil
import sys
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from priority_zero_external_run_artifact_lib import (  # type: ignore  # noqa: E402
    ExternalRunArtifactError,
    non_placeholder_text,
    strict_json,
    write_new_json,
)
from score_priority_zero_external_replay_response import (  # type: ignore  # noqa: E402
    ResponseIntakeError,
    validate_response_file,
)

from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    CommitmentContractError,
    responder_packet_projection_sha256,
)
from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    RunBundleContractError,
    load_run_bundle,
    read_safe_zip_members,
)
from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    ResponseSetContractError,
    validate_dispatch_manifest,
    validate_response_set_lock,
)
from oq0266_isolated_scoring_policy_lib import (  # type: ignore  # noqa: E402
    ScoringPolicyContractError,
    validate_policy_commitment,
    validate_policy_verification_receipt,
    validate_scorer_against_policy,
    validate_scoring_policy,
)

DEFAULT_PLAN = "cloudtainer/oq0266-isolated-semantic-pilot/assignment-plan.json"
DEFAULT_COMMITMENT = "cloudtainer/oq0266-isolated-semantic-pilot/assignment-commitment.json"
DEFAULT_DISPATCH = "cloudtainer/oq0266-isolated-semantic-pilot/dispatch-manifest.json"
DEFAULT_POLICY = "cloudtainer/oq0266-isolated-semantic-pilot/scoring-policy.json"
DEFAULT_BATCH_MANIFEST = "cloudtainer/oq0266-isolated-semantic-pilot/batch-manifest.json"
EXPECTED_VARIANTS = {"compact", "sham", "baseline", "trace"}


class IsolatedBatchError(ValueError):
    pass


def _resolve(path: str | pathlib.Path, *, root: pathlib.Path = ROOT) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _load(
    path: str | pathlib.Path,
    label: str,
    *,
    root: pathlib.Path = ROOT,
) -> tuple[dict[str, Any], bytes]:
    try:
        return strict_json(_resolve(path, root=root), label)
    except ExternalRunArtifactError as exc:
        raise IsolatedBatchError(str(exc)) from exc


def _non_placeholder(value: Any, label: str) -> str:
    try:
        return non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise IsolatedBatchError(str(exc)) from exc


def _numeric(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise IsolatedBatchError(f"{label} must be numeric and not boolean")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise IsolatedBatchError(f"{label} must be finite")
    return numeric


def _validate_plan(plan: dict[str, Any], commitment: dict[str, Any], plan_raw: bytes) -> list[dict[str, Any]]:
    if plan.get("project") != "DelayBasin" or commitment.get("project") != "DelayBasin":
        raise IsolatedBatchError("assignment plan and commitment must identify DelayBasin")
    batch_id = _non_placeholder(plan.get("batch_id"), "assignment plan batch_id")
    if commitment.get("batch_id") != batch_id:
        raise IsolatedBatchError("assignment commitment batch_id disagrees with plan")
    observed = hashlib.sha256(plan_raw).hexdigest()
    if commitment.get("assignment_plan_sha256") != observed:
        raise IsolatedBatchError("assignment plan bytes do not match the pre-response commitment")
    rows = plan.get("arms")
    if not isinstance(rows, list) or len(rows) != 4:
        raise IsolatedBatchError("assignment plan must contain exactly four arms")
    arm_codes: list[str] = []
    variants: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise IsolatedBatchError(f"assignment plan arms[{index}] must be an object")
        arm_codes.append(_non_placeholder(row.get("arm_code"), f"assignment plan arms[{index}].arm_code"))
        variants.append(_non_placeholder(row.get("analysis_variant"), f"assignment plan arms[{index}].analysis_variant"))
        _non_placeholder(row.get("scorer_intake_surface"), f"assignment plan arms[{index}].scorer_intake_surface")
    if len(set(arm_codes)) != 4:
        raise IsolatedBatchError("assignment plan arm codes must be unique")
    if set(variants) != EXPECTED_VARIANTS or len(set(variants)) != 4:
        raise IsolatedBatchError(
            f"assignment plan must map exactly one arm to each variant {sorted(EXPECTED_VARIANTS)}"
        )
    committed_codes = commitment.get("opaque_arm_codes")
    if committed_codes != sorted(arm_codes):
        raise IsolatedBatchError("assignment commitment opaque arm list disagrees with plan")
    return rows


def _validate_arm_commitment_binding(
    plan_row: dict[str, Any],
    scorer: dict[str, Any],
    *,
    batch_id: str,
    commitment_file_sha256: str,
    expected_packet_projection_sha256: str,
    root: pathlib.Path = ROOT,
) -> tuple[dict[str, Any], str, str]:
    """Bind the supplied committed plan to the packet frozen in this arm.

    Checking only ``plan -> commitment`` is insufficient: after responses
    freeze, a replacement plan and replacement commitment could agree with one
    another while disagreeing with what responders actually saw.  The exact
    commitment file hash is therefore required to match the hash embedded in
    each responder packet, whose bytes are independently bound by the response
    and scorer contracts.
    """
    arm = _non_placeholder(plan_row.get("arm_code"), "assignment plan arm_code")
    if scorer.get("project") != "DelayBasin":
        raise IsolatedBatchError(f"arm {arm} scorer intake project must be DelayBasin")
    if scorer.get("batch_id") != batch_id or scorer.get("arm_code") != arm:
        raise IsolatedBatchError(f"arm {arm} scorer intake identity disagrees with assignment plan")

    packet_rel = _non_placeholder(
        scorer.get("responder_only_surface"),
        f"arm {arm} scorer responder_only_surface",
    )
    packet, packet_raw = _load(packet_rel, f"{arm} responder packet", root=root)
    packet_sha = hashlib.sha256(packet_raw).hexdigest()
    if scorer.get("responder_only_sha256") != packet_sha:
        raise IsolatedBatchError(f"arm {arm} responder packet hash drifted from scorer intake")
    if packet.get("project") != "DelayBasin":
        raise IsolatedBatchError(f"arm {arm} responder packet project must be DelayBasin")
    if packet.get("batch_id") != batch_id or packet.get("arm_code") != arm:
        raise IsolatedBatchError(f"arm {arm} responder packet identity disagrees with assignment plan")
    if packet.get("assignment_commitment_sha256") != commitment_file_sha256:
        raise IsolatedBatchError(
            f"arm {arm} frozen responder packet does not bind the supplied assignment commitment; "
            "rejecting post-response plan/commitment substitution"
        )
    packet_projection_sha = responder_packet_projection_sha256(packet)
    if packet_projection_sha != expected_packet_projection_sha256:
        raise IsolatedBatchError(
            f"arm {arm} responder-visible packet projection disagrees with the preanswer commitment"
        )

    if plan_row.get("responder_bundle_surface") != scorer.get("responder_bundle_surface"):
        raise IsolatedBatchError(f"arm {arm} responder bundle surface disagrees across plan and scorer")
    answer_key = scorer.get("answer_key")
    if not isinstance(answer_key, dict) or set(answer_key) != {arm}:
        raise IsolatedBatchError(f"arm {arm} scorer must contain exactly one opaque answer-key row")
    key_row = answer_key[arm]
    if not isinstance(key_row, dict):
        raise IsolatedBatchError(f"arm {arm} answer-key row must be an object")
    for plan_field, key_field in [
        ("source_packet_label", "source_packet_label"),
        ("analysis_variant", "analysis_variant"),
        ("expected_posture", "expected_posture"),
        ("reference_expected_score", "expected_score"),
    ]:
        if plan_row.get(plan_field) != key_row.get(key_field):
            raise IsolatedBatchError(
                f"arm {arm} committed assignment field {plan_field} disagrees with its scorer key"
            )
    return scorer, packet_sha, packet_projection_sha


def ensure_distinct_responder_ids(validated_rows: list[dict[str, Any]]) -> None:
    """Require one distinct responder per isolated arm."""
    ids = [_non_placeholder(row.get("responder_id"), "validated arm responder_id") for row in validated_rows]
    if len(ids) != len(set(ids)):
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        raise IsolatedBatchError(
            "isolated-arm pilot requires one distinct responder per arm; duplicate responder IDs: "
            + ", ".join(duplicates)
        )


def _decide(
    by_variant: dict[str, dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    compact = _numeric(by_variant["compact"]["score"], "compact score")
    sham = _numeric(by_variant["sham"]["score"], "sham score")
    baseline = _numeric(by_variant["baseline"]["score"], "baseline score")
    trace = _numeric(by_variant["trace"]["score"], "trace score")

    compact_min = _numeric(thresholds.get("compact_min_score"), "compact_min_score")
    sham_max = _numeric(thresholds.get("sham_max_score"), "sham_max_score")
    baseline_max = _numeric(thresholds.get("baseline_max_score"), "baseline_max_score")
    override_margin = _numeric(thresholds.get("trace_override_margin"), "trace_override_margin")
    support_margin = _numeric(
        thresholds.get("support_if_trace_minus_compact_at_most"),
        "support_if_trace_minus_compact_at_most",
    )
    scores = {variant: by_variant[variant]["score"] for variant in sorted(by_variant)}
    costs = {variant: by_variant[variant]["operator_cost_minutes"] for variant in sorted(by_variant)}

    blocking: list[str] = []
    if compact < compact_min:
        blocking.append(f"compact score {compact:g} below minimum {compact_min:g}")
    if sham > sham_max:
        blocking.append(f"sham score {sham:g} above maximum {sham_max:g}")
    if baseline > baseline_max:
        blocking.append(f"baseline score {baseline:g} above maximum {baseline_max:g}")
    if blocking:
        state = "reverse-isolated-semantic-support"
        posture = "remain-narrowed-and-redesign-or-retest"
        reason = "; ".join(blocking)
    elif trace - compact >= override_margin:
        state = "narrow-isolated-semantic-support"
        posture = "trace-escalation-remains-material-for-this-bounded-slice"
        reason = (
            f"trace exceeded compact by {trace - compact:g}, meeting the bounded override margin "
            f"{override_margin:g}"
        )
    elif trace - compact <= support_margin:
        state = "support-isolated-semantic-recovery-pilot"
        posture = "remain-narrowed-with-cleaner-isolated-semantic-support"
        reason = (
            "compact met its semantic threshold, sham and baseline controls behaved, and the trace arm "
            f"led compact by at most {support_margin:g}; responder-separated n=1 arms still do not identify burden"
        )
    else:
        state = "narrow-isolated-semantic-support"
        posture = "remain-narrowed-pending-replication"
        reason = (
            f"compact passed controls but trace led by {trace - compact:g}, above support allowance "
            f"{support_margin:g} and below override margin {override_margin:g}"
        )
    return {
        "decision_state": state,
        "compact_gate_state": posture,
        "reason": reason,
        "scores_by_variant": scores,
        "operator_cost_minutes_by_variant": costs,
        "operator_cost_inference_state": "descriptive-only-not-identifiable-between-subjects-n1-per-arm",
        "bounded_semantic_support": state == "support-isolated-semantic-recovery-pilot",
        "global_compact_gate_confirmed": False,
        "supports_deletion": False,
        "benchmark_authority": False,
    }



def _write_materialized_members(
    root: pathlib.Path,
    members: dict[str, bytes],
) -> None:
    """Materialize already-safe ZIP members without following archive paths."""
    for name, raw in members.items():
        path = root / pathlib.PurePosixPath(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o444)


def _validate_and_materialize_source_kits(
    run_bundle: Any,
    materialized_root: pathlib.Path,
) -> tuple[dict[str, bytes], dict[str, bytes], dict[str, Any]]:
    """Validate both source kits and create the static replay tree.

    The trusted verifier parses the capsule.  It does not import or execute code
    from the capsule; source-kit tools are retained as hashed evidence and are
    checked against the preanswer policy by the trusted verifier implementation.
    """
    try:
        prefreeze_members = read_safe_zip_members(
            run_bundle.prefreeze_dispatch_kit_raw,
            "run-capsule prefreeze dispatch kit",
        )
        postfreeze_members = read_safe_zip_members(
            run_bundle.postfreeze_batch_kit_raw,
            "run-capsule postfreeze batch kit",
        )
    except RunBundleContractError as exc:
        raise IsolatedBatchError(str(exc)) from exc

    _write_materialized_members(materialized_root, postfreeze_members)
    batch_manifest, _ = _load(
        DEFAULT_BATCH_MANIFEST,
        "postfreeze batch manifest",
        root=materialized_root,
    )
    prefreeze_sha = hashlib.sha256(run_bundle.prefreeze_dispatch_kit_raw).hexdigest()
    if batch_manifest.get("prefreeze_dispatch_kit_sha256") != prefreeze_sha:
        raise IsolatedBatchError(
            "postfreeze batch manifest does not bind the prefreeze dispatch kit captured in the run capsule"
        )
    if (
        batch_manifest.get("run_bundle_contract_version")
        != run_bundle.manifest.get("run_bundle_contract_version")
    ):
        raise IsolatedBatchError(
            "postfreeze batch manifest does not require the run-capsule contract presented for replay"
        )

    for surface in [DEFAULT_DISPATCH, DEFAULT_COMMITMENT]:
        post_raw = postfreeze_members.get(surface)
        pre_raw = prefreeze_members.get(surface)
        if post_raw is None or pre_raw is None:
            raise IsolatedBatchError(
                f"source kits are missing shared preanswer surface: {surface}"
            )
        if pre_raw != post_raw:
            raise IsolatedBatchError(
                f"prefreeze and postfreeze source kits disagree on exact bytes for {surface}"
            )

    dispatch, dispatch_raw = _load(
        DEFAULT_DISPATCH,
        "prefreeze dispatch manifest",
        root=materialized_root,
    )
    rows = dispatch.get("arms")
    if not isinstance(rows, list) or len(rows) != 4:
        raise IsolatedBatchError("dispatch manifest must contain exactly four arms")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise IsolatedBatchError(f"dispatch manifest arms[{index}] must be an object")
        arm = _non_placeholder(row.get("arm_code"), f"dispatch arms[{index}].arm_code")
        bundle_surface = _non_placeholder(
            row.get("responder_bundle_surface"),
            f"dispatch {arm}.responder_bundle_surface",
        )
        bundle_raw = prefreeze_members.get(bundle_surface)
        if bundle_raw is None:
            raise IsolatedBatchError(
                f"prefreeze dispatch kit is missing responder bundle for {arm}: {bundle_surface}"
            )
        bundle_sha = hashlib.sha256(bundle_raw).hexdigest()
        if bundle_sha != row.get("responder_bundle_sha256"):
            raise IsolatedBatchError(
                f"prefreeze responder bundle hash disagrees with dispatch manifest for {arm}"
            )
        try:
            nested = read_safe_zip_members(
                bundle_raw,
                f"prefreeze responder bundle {arm}",
            )
        except RunBundleContractError as exc:
            raise IsolatedBatchError(str(exc)) from exc
        expected_names = row.get("responder_bundle_members")
        if not isinstance(expected_names, list) or list(nested) != expected_names:
            raise IsolatedBatchError(
                f"prefreeze responder bundle topology disagrees with dispatch manifest for {arm}"
            )
        for shared_surface in [
            DEFAULT_COMMITMENT,
            row.get("responder_packet_surface"),
            row.get("response_template_surface"),
        ]:
            if not isinstance(shared_surface, str):
                raise IsolatedBatchError(
                    f"dispatch manifest has invalid shared responder surface for {arm}"
                )
            if nested.get(shared_surface) != postfreeze_members.get(shared_surface):
                raise IsolatedBatchError(
                    f"prefreeze responder bundle and postfreeze kit disagree on {shared_surface} for {arm}"
                )
        bundle_path = materialized_root / pathlib.PurePosixPath(bundle_surface)
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        bundle_path.write_bytes(bundle_raw)
        bundle_path.chmod(0o444)

    # Exact source-kit digests have already been bound by the capsule manifest;
    # record the dispatch bytes here so callers need not reopen any source ZIP.
    if hashlib.sha256(dispatch_raw).hexdigest() != batch_manifest.get("dispatch_manifest_sha256"):
        raise IsolatedBatchError(
            "postfreeze batch manifest dispatch hash disagrees with the shared source-kit dispatch bytes"
        )
    return prefreeze_members, postfreeze_members, batch_manifest


def validate_batch(
    run_bundle_path: str | pathlib.Path,
    expected_run_bundle_sha256: str,
) -> dict[str, Any]:
    try:
        run_bundle = load_run_bundle(
            _resolve(run_bundle_path),
            expected_bundle_sha256=expected_run_bundle_sha256,
        )
    except RunBundleContractError as exc:
        raise IsolatedBatchError(f"isolated run evidence capsule failed validation: {exc}") from exc

    materialized_root = pathlib.Path(
        tempfile.mkdtemp(prefix="delaybasin-oq0266-evidence-capsule-")
    )
    try:
        prefreeze_members, postfreeze_members, batch_manifest = (
            _validate_and_materialize_source_kits(run_bundle, materialized_root)
        )
        plan, plan_raw = _load(
            DEFAULT_PLAN,
            "assignment plan",
            root=materialized_root,
        )
        commitment, commitment_raw = _load(
            DEFAULT_COMMITMENT,
            "assignment commitment",
            root=materialized_root,
        )
        policy, policy_raw = _load(
            DEFAULT_POLICY,
            "preanswer-bound scoring policy",
            root=materialized_root,
        )
        dispatch, dispatch_raw = _load(
            DEFAULT_DISPATCH,
            "prefreeze dispatch manifest",
            root=materialized_root,
        )
        plan_rows = _validate_plan(plan, commitment, plan_raw)
        plan_sha = hashlib.sha256(plan_raw).hexdigest()
        commitment_file_sha256 = hashlib.sha256(commitment_raw).hexdigest()
        policy_sha = hashlib.sha256(policy_raw).hexdigest()
        dispatch_sha = hashlib.sha256(dispatch_raw).hexdigest()
        batch_id = _non_placeholder(plan.get("batch_id"), "assignment plan batch_id")
        expected_arm_codes = {str(row["arm_code"]) for row in plan_rows}

        manifest_plan_sha = run_bundle.manifest.get("assignment_plan_sha256")
        if manifest_plan_sha != plan_sha:
            raise IsolatedBatchError(
                "run-capsule assignment-plan hash disagrees with the plan captured in its postfreeze source kit"
            )
        if run_bundle.manifest.get("batch_id") != batch_id:
            raise IsolatedBatchError(
                "run-capsule batch_id disagrees with the plan captured in its postfreeze source kit"
            )
        if set(run_bundle.arm_order) != expected_arm_codes:
            raise IsolatedBatchError(
                "run-capsule arm set disagrees with the plan captured in its postfreeze source kit"
            )
        expected_batch_hashes = {
            "assignment_plan_sha256": plan_sha,
            "scoring_policy_sha256": policy_sha,
            "assignment_commitment_sha256": commitment_file_sha256,
            "dispatch_manifest_sha256": dispatch_sha,
        }
        for field, expected in expected_batch_hashes.items():
            if batch_manifest.get(field) != expected:
                raise IsolatedBatchError(
                    f"postfreeze batch manifest {field} disagrees with captured source-kit bytes"
                )

        try:
            committed_packet_projections = validate_policy_commitment(
                commitment,
                assignment_plan_sha256=plan_sha,
                scoring_policy_sha256=policy_sha,
            )
            policy_by_arm, observed_tool_hashes = validate_scoring_policy(
                policy,
                plan,
                assignment_plan_sha256=plan_sha,
                root=materialized_root,
            )
        except ScoringPolicyContractError as exc:
            raise IsolatedBatchError(
                f"preanswer scoring policy failed validation: {exc}"
            ) from exc

        try:
            dispatch_by_arm = validate_dispatch_manifest(
                dispatch,
                assignment_commitment_sha256=commitment_file_sha256,
                responder_packet_projection_sha256_by_arm=committed_packet_projections,
            )
        except ResponseSetContractError as exc:
            raise IsolatedBatchError(
                f"prefreeze dispatch manifest failed validation: {exc}"
            ) from exc
        if dispatch.get("batch_id") != batch_id:
            raise IsolatedBatchError(
                "dispatch manifest batch_id disagrees with assignment plan"
            )
        if set(dispatch_by_arm) != expected_arm_codes:
            raise IsolatedBatchError(
                "dispatch manifest arm set disagrees with assignment plan"
            )
        if set(policy_by_arm) != expected_arm_codes:
            raise IsolatedBatchError(
                "preanswer scoring-policy arm set disagrees with assignment plan"
            )

        lock = run_bundle.response_set_lock
        lock_raw = run_bundle.response_set_lock_raw
        lock_sha = hashlib.sha256(lock_raw).hexdigest()
        try:
            preliminary_lock_summary = validate_response_set_lock(
                lock,
                dispatch,
                dispatch_manifest_sha256=dispatch_sha,
                assignment_commitment_sha256=commitment_file_sha256,
                responder_packet_projection_sha256_by_arm=committed_packet_projections,
            )
        except ResponseSetContractError as exc:
            raise IsolatedBatchError(
                f"response-set lock failed validation: {exc}"
            ) from exc

        scorers_by_arm: dict[str, dict[str, Any]] = {}
        scorer_hashes: dict[str, str] = {}
        scorer_paths: dict[str, pathlib.Path] = {}
        for plan_row in plan_rows:
            arm = str(plan_row["arm_code"])
            scorer_rel = _non_placeholder(
                plan_row.get("scorer_intake_surface"),
                f"assignment plan {arm}.scorer_intake_surface",
            )
            scorer, scorer_raw = _load(
                scorer_rel,
                f"{arm} scorer intake",
                root=materialized_root,
            )
            try:
                validate_scorer_against_policy(
                    scorer,
                    expected_policy=policy_by_arm[arm],
                    arm=arm,
                    scoring_policy_surface=DEFAULT_POLICY,
                    scoring_policy_sha256=policy_sha,
                )
            except ScoringPolicyContractError as exc:
                raise IsolatedBatchError(
                    f"arm {arm} scorer policy binding failed: {exc}"
                ) from exc
            scorers_by_arm[arm] = scorer
            scorer_hashes[arm] = hashlib.sha256(scorer_raw).hexdigest()
            scorer_paths[arm] = _resolve(scorer_rel, root=materialized_root)

        policy_receipt = run_bundle.postfreeze_policy_verification
        policy_receipt_raw = run_bundle.postfreeze_policy_verification_raw
        policy_receipt_sha = hashlib.sha256(policy_receipt_raw).hexdigest()
        try:
            verifier_id, _policy_verified_at = validate_policy_verification_receipt(
                policy_receipt,
                batch_id=batch_id,
                assignment_commitment_sha256=commitment_file_sha256,
                assignment_plan_sha256=plan_sha,
                scoring_policy_sha256=policy_sha,
                dispatch_manifest_sha256=dispatch_sha,
                response_set_lock_sha256=lock_sha,
                response_set_locked_at=preliminary_lock_summary.response_set_locked_at,
                scorer_intake_sha256_by_arm=scorer_hashes,
                responder_packet_projection_sha256_by_arm=committed_packet_projections,
                tool_sha256_by_surface=observed_tool_hashes,
            )
        except ScoringPolicyContractError as exc:
            raise IsolatedBatchError(
                f"postfreeze policy verification receipt failed: {exc}"
            ) from exc

        run_by_arm = {
            str(row["arm_code"]): row for row in run_bundle.manifest["arms"]
        }
        dynamic_root = materialized_root / ".run-artifacts"
        materialized_paths: dict[str, dict[str, pathlib.Path]] = {}
        for arm in run_bundle.arm_order:
            arm_root = dynamic_root / arm
            arm_root.mkdir(parents=True)
            payloads = run_bundle.artifacts_by_arm[arm]
            row_paths = {
                "response": arm_root / "response.json",
                "custody": arm_root / "custody.json",
                "score_sheet": arm_root / "score-sheet.json",
            }
            for label, path in row_paths.items():
                path.write_bytes(payloads[label])
                path.chmod(0o444)
            materialized_paths[arm] = row_paths

        validated: list[dict[str, Any]] = []
        expected_lock_rows: dict[str, dict[str, Any]] = {}
        for plan_row in plan_rows:
            arm = str(plan_row["arm_code"])
            run_row = run_by_arm[arm]
            paths = materialized_paths[arm]
            scorer = scorers_by_arm[arm]
            scorer_hash_before = scorer_hashes[arm]
            scorer, responder_packet_sha256, responder_packet_projection_sha = (
                _validate_arm_commitment_binding(
                    plan_row,
                    scorer,
                    batch_id=batch_id,
                    commitment_file_sha256=commitment_file_sha256,
                    expected_packet_projection_sha256=committed_packet_projections[arm],
                    root=materialized_root,
                )
            )
            scorer_rel = _non_placeholder(
                plan_row.get("scorer_intake_surface"),
                f"assignment plan {arm}.scorer_intake_surface",
            )
            try:
                summary = validate_response_file(
                    paths["response"],
                    scorer_intake=scorer_rel,
                    evidence_record_file=paths["custody"],
                    score_sheet_file=paths["score_sheet"],
                    root=materialized_root,
                )
            except ResponseIntakeError as exc:
                raise IsolatedBatchError(
                    f"arm {arm} triplet failed strict validation: {exc}"
                ) from exc
            if hashlib.sha256(scorer_paths[arm].read_bytes()).hexdigest() != scorer_hash_before:
                raise IsolatedBatchError(
                    f"arm {arm} scorer intake changed during validation; refusing a split-time policy read"
                )
            expected_member_hashes = {
                "response_file_sha256": run_row["response_file_sha256"],
                "custody_evidence_record_sha256": run_row[
                    "evidence_record_file_sha256"
                ],
                "score_sheet_sha256": run_row["score_sheet_file_sha256"],
            }
            for summary_field, expected_sha in expected_member_hashes.items():
                if summary.get(summary_field) != expected_sha:
                    raise IsolatedBatchError(
                        f"arm {arm} validated {summary_field} disagrees with the frozen run-capsule manifest"
                    )
            if summary.get("external_response_evidence") is not True:
                raise IsolatedBatchError(
                    f"arm {arm} is not admitted as strict external evidence"
                )
            if summary.get("responder_packet_sha256") != responder_packet_sha256:
                raise IsolatedBatchError(
                    f"arm {arm} validated response packet hash disagrees with committed packet"
                )
            if summary.get("responder_bundle_sha256") != scorer.get(
                "responder_bundle_sha256"
            ):
                raise IsolatedBatchError(
                    f"arm {arm} validated response bundle hash disagrees with scorer intake"
                )
            if summary.get("manual_score_status") != "complete":
                raise IsolatedBatchError(
                    f"arm {arm} has no complete separated manual score"
                )
            label_rows = summary.get("manual_scores_by_label")
            if not isinstance(label_rows, dict) or set(label_rows) != {arm}:
                raise IsolatedBatchError(
                    f"arm {arm} score summary does not contain exactly its opaque arm row"
                )
            score_row = label_rows[arm]
            if not isinstance(score_row, dict):
                raise IsolatedBatchError(
                    f"arm {arm} score summary row is invalid"
                )
            cost_by_label = summary.get("operator_cost_minutes_by_label")
            if not isinstance(cost_by_label, dict) or set(cost_by_label) != {arm}:
                raise IsolatedBatchError(
                    f"arm {arm} cost summary does not contain exactly its opaque arm row"
                )
            response_file_sha256 = _non_placeholder(
                summary.get("response_file_sha256"),
                f"arm {arm} response_file_sha256",
            )
            responder_id = _non_placeholder(
                summary.get("responder_id"), f"arm {arm} responder_id"
            )
            custodian_id = _non_placeholder(
                summary.get("custodian_id"), f"arm {arm} custodian_id"
            )
            scorer_id = _non_placeholder(
                summary.get("scorer_id"), f"arm {arm} scorer_id"
            )
            if scorer_id == responder_id:
                raise IsolatedBatchError(
                    f"arm {arm} responder self-scoring is forbidden by the preanswer batch policy"
                )
            if custodian_id == responder_id:
                raise IsolatedBatchError(
                    f"arm {arm} responder self-custody is forbidden by the preanswer batch policy"
                )
            response_finalized_at = _non_placeholder(
                summary.get("response_finalized_at"),
                f"arm {arm} response_finalized_at",
            )
            custody_kit_opened_at = _non_placeholder(
                summary.get("custody_kit_opened_at"),
                f"arm {arm} custody_kit_opened_at",
            )
            scorer_kit_opened_at = _non_placeholder(
                summary.get("scorer_kit_opened_at"),
                f"arm {arm} scorer_kit_opened_at",
            )
            prerequisite_artifacts = summary.get("prerequisite_artifacts")
            expected_prerequisite_hashes = {
                "response-set-lock": lock_sha,
                "postfreeze-policy-verification": policy_receipt_sha,
            }
            if (
                not isinstance(prerequisite_artifacts, dict)
                or set(prerequisite_artifacts) != set(expected_prerequisite_hashes)
            ):
                observed = (
                    sorted(prerequisite_artifacts)
                    if isinstance(prerequisite_artifacts, dict)
                    else type(prerequisite_artifacts).__name__
                )
                raise IsolatedBatchError(
                    f"arm {arm} custody prerequisite set drifted: observed={observed} "
                    f"expected={sorted(expected_prerequisite_hashes)}"
                )
            for prerequisite_label, expected_sha in expected_prerequisite_hashes.items():
                prerequisite = prerequisite_artifacts.get(prerequisite_label)
                if (
                    not isinstance(prerequisite, dict)
                    or prerequisite.get("artifact_sha256") != expected_sha
                ):
                    raise IsolatedBatchError(
                        f"arm {arm} custody prerequisite {prerequisite_label} does not bind the supplied exact artifact bytes"
                    )
            expected_lock_rows[arm] = {
                **preliminary_lock_summary.responses_by_arm[arm],
                "arm_code": arm,
                "response_file_sha256": response_file_sha256,
                "responder_id": responder_id,
                "response_finalized_at": response_finalized_at,
                "responder_bundle_sha256": summary.get("responder_bundle_sha256"),
                "responder_packet_sha256": summary.get("responder_packet_sha256"),
                "responder_packet_projection_sha256": responder_packet_projection_sha,
            }
            validated.append(
                {
                    "arm_code": arm,
                    "analysis_variant": plan_row["analysis_variant"],
                    "source_packet_label": plan_row["source_packet_label"],
                    "responder_id": responder_id,
                    "custodian_id": custodian_id,
                    "scorer_id": scorer_id,
                    "response_file_sha256": response_file_sha256,
                    "response_finalized_at": response_finalized_at,
                    "custody_evidence_record_sha256": summary.get(
                        "custody_evidence_record_sha256"
                    ),
                    "custody_kit_opened_at": custody_kit_opened_at,
                    "custody_record_frozen_at": summary.get(
                        "custody_record_frozen_at"
                    ),
                    "score_sheet_sha256": summary.get("score_sheet_sha256"),
                    "scorer_kit_opened_at": scorer_kit_opened_at,
                    "scored_at": summary.get("scored_at"),
                    "score": score_row.get("score"),
                    "score_max": score_row.get("max"),
                    "operator_cost_minutes": cost_by_label[arm],
                    "responder_packet_projection_sha256": responder_packet_projection_sha,
                    "responder_commitment_binding_state": (
                        "plan-policy-and-visible-stimulus-verified"
                    ),
                    "scoring_policy_binding_state": (
                        "verified-against-preanswer-policy"
                    ),
                    "custody_prerequisite_binding_state": (
                        "exact-response-lock-and-policy-receipt-hashes-verified"
                    ),
                    "run_bundle_member_binding_state": (
                        "source-kits-response-custody-and-score-member-hashes-verified"
                    ),
                    "triplet_validation_state": "valid",
                }
            )

        ensure_distinct_responder_ids(validated)
        try:
            lock_summary = validate_response_set_lock(
                lock,
                dispatch,
                dispatch_manifest_sha256=dispatch_sha,
                assignment_commitment_sha256=commitment_file_sha256,
                responder_packet_projection_sha256_by_arm=committed_packet_projections,
                expected_responses_by_arm=expected_lock_rows,
            )
        except ResponseSetContractError as exc:
            raise IsolatedBatchError(
                f"all-response batch barrier failed: {exc}"
            ) from exc

        by_variant = {str(row["analysis_variant"]): row for row in validated}
        if set(by_variant) != EXPECTED_VARIANTS:
            raise IsolatedBatchError(
                "validated arm set does not resolve exactly one row per analysis variant"
            )
        thresholds = policy.get("decision_thresholds")
        if not isinstance(thresholds, dict):
            raise IsolatedBatchError(
                "preanswer scoring policy missing decision_thresholds"
            )
        decision = _decide(by_variant, thresholds)
        return {
            "project": "DelayBasin",
            "batch_id": batch_id,
            "assignment_plan_sha256": plan_sha,
            "scoring_policy_sha256": policy_sha,
            "assignment_commitment_file_sha256": commitment_file_sha256,
            "assignment_commitment_state": (
                "plan-policy-and-exact-responder-visible-packet-projections-verified"
            ),
            "dispatch_manifest_sha256": dispatch_sha,
            "run_bundle_sha256": run_bundle.bundle_sha256,
            "expected_run_bundle_sha256": expected_run_bundle_sha256,
            "outer_digest_binding_state": (
                "matched-separately-supplied-sha256-before-capsule-interpretation"
            ),
            "run_bundle_manifest_sha256": run_bundle.manifest_sha256,
            "run_bundle_contract_version": run_bundle.manifest[
                "run_bundle_contract_version"
            ],
            "run_bundle_state": run_bundle.manifest["run_bundle_state"],
            "prefreeze_dispatch_kit_sha256": hashlib.sha256(
                run_bundle.prefreeze_dispatch_kit_raw
            ).hexdigest(),
            "postfreeze_batch_kit_sha256": hashlib.sha256(
                run_bundle.postfreeze_batch_kit_raw
            ).hexdigest(),
            "source_kit_replay_state": (
                "exact-prefreeze-and-postfreeze-kits-validated-from-capsule"
            ),
            "source_kit_member_counts": {
                "prefreeze": len(prefreeze_members),
                "postfreeze": len(postfreeze_members),
            },
            "response_set_lock_sha256": lock_sha,
            "response_set_lock": lock_summary.as_dict(),
            "postfreeze_policy_verification_sha256": policy_receipt_sha,
            "postfreeze_policy_verification": {
                "verifier_id": verifier_id,
                "verified_at": policy_receipt.get("verified_at"),
                "verification_state": policy_receipt.get("verification_state"),
                "scorer_intake_count": len(scorer_hashes),
                "committed_tool_count": len(observed_tool_hashes),
            },
            "batch_barrier_state": (
                "all-four-responses-hash-locked-policy-receipt-bound-source-kits-and-final-triplets-content-bundled"
            ),
            "arm_count": len(validated),
            "distinct_responder_count": len(
                {row["responder_id"] for row in validated}
            ),
            "arms": validated,
            "decision": decision,
            "evidence_scope": {
                "supports": (
                    "bounded isolated-arm semantic recovery evidence replayed from one outer-digest-pinned, "
                    "self-contained source-kit and dynamic-artifact capsule"
                ),
                "does_not_support": [
                    "causal compact-versus-trace burden comparison",
                    "global compact-default confirmation",
                    "deletion or benchmark authority",
                    "trusted timestamping, signed provenance, or proof of real-world operator independence beyond recorded identities",
                    "verification by executing code from inside the capsule; verifier trust remains external",
                ],
            },
        }
    finally:
        shutil.rmtree(materialized_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-bundle", required=True)
    parser.add_argument(
        "--expected-run-bundle-sha256",
        required=True,
        help="lowercase SHA-256 preserved separately from the run capsule",
    )
    parser.add_argument("--summary-out")
    args = parser.parse_args()
    try:
        summary = validate_batch(
            args.run_bundle,
            args.expected_run_bundle_sha256,
        )
        if args.summary_out:
            write_new_json(pathlib.Path(args.summary_out), summary, readonly=True)
    except (
        CommitmentContractError,
        ExternalRunArtifactError,
        IsolatedBatchError,
        RunBundleContractError,
        ResponseSetContractError,
        ScoringPolicyContractError,
    ) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

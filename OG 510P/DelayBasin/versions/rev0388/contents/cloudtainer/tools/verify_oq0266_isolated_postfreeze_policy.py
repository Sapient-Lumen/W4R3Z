#!/usr/bin/env python3
"""Verify hidden OQ-0266 postfreeze policy against its preanswer commitment.

Run this from the extracted prefreeze dispatch kit only after the all-response
lock succeeds and after opening the postfreeze kit.  The verifier contains no
assignment mapping or answer key.  It checks that the newly visible assignment,
scoring policy, scorer intakes, and executable validation surfaces match the
exact digests committed before any responder answered, then emits one immutable
receipt that the final batch scorer revalidates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "cloudtainer/tools"))

from priority_zero_external_run_artifact_lib import (  # type: ignore  # noqa: E402
    ExternalRunArtifactError,
    non_placeholder_text,
    now_timestamp,
    sha256_bytes,
    strict_json,
    write_new_json,
)
from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    CommitmentContractError,
    responder_packet_projection_sha256,
    validate_assignment_commitment,
)
from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    ResponseSetContractError,
    validate_dispatch_manifest,
    validate_response_set_lock,
)
from oq0266_isolated_scoring_policy_lib import (  # type: ignore  # noqa: E402
    POLICY_VERIFICATION_CONTRACT_VERSION,
    POLICY_VERIFICATION_RECORD_TYPE,
    POLICY_VERIFICATION_STATE,
    POLICY_VERIFICATION_STARTED_AT_SOURCE,
    POLICY_LOCK_OBSERVED_AT_SOURCE,
    POLICY_VERIFIED_AT_SOURCE,
    ScoringPolicyContractError,
    file_sha256,
    validate_policy_commitment,
    validate_scorer_against_policy,
    validate_scoring_policy,
)

PILOT = "cloudtainer/oq0266-isolated-semantic-pilot"
DEFAULT_DISPATCH = f"{PILOT}/dispatch-manifest.json"
DEFAULT_COMMITMENT = f"{PILOT}/assignment-commitment.json"
DEFAULT_PLAN = f"{PILOT}/assignment-plan.json"
DEFAULT_POLICY = f"{PILOT}/scoring-policy.json"


class PolicyVerificationError(ValueError):
    """Raised when the postfreeze disclosure does not match preanswer policy."""


def _prefreeze(path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def _postfreeze(root: pathlib.Path, path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _load(path: pathlib.Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        return strict_json(path, label)
    except ExternalRunArtifactError as exc:
        raise PolicyVerificationError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dispatch-manifest", default=DEFAULT_DISPATCH)
    parser.add_argument("--commitment", default=DEFAULT_COMMITMENT)
    parser.add_argument("--response-set-lock", required=True)
    parser.add_argument("--postfreeze-root", required=True)
    parser.add_argument("--assignment-plan", default=DEFAULT_PLAN)
    parser.add_argument("--scoring-policy", default=DEFAULT_POLICY)
    parser.add_argument("--verifier-id", required=True)
    parser.add_argument(
        "--attest-postfreeze-opened-after-lock",
        action="store_true",
        help="attest that the assignment/policy/postfreeze kit opened only after the response-set lock succeeded",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not args.attest_postfreeze_opened_after_lock:
        raise SystemExit(
            "--attest-postfreeze-opened-after-lock is required; the verifier will not manufacture disclosure chronology"
        )

    verification_started_text, _ = now_timestamp()
    post_root = pathlib.Path(args.postfreeze_root).resolve()
    try:
        verifier_id = non_placeholder_text(args.verifier_id, "postfreeze policy verifier_id")
        dispatch, dispatch_raw = _load(_prefreeze(args.dispatch_manifest), "prefreeze dispatch manifest")
        commitment, commitment_raw = _load(_prefreeze(args.commitment), "assignment commitment")
        lock, lock_raw = _load(_prefreeze(args.response_set_lock), "response-set lock")
        plan, plan_raw = _load(
            _postfreeze(post_root, args.assignment_plan),
            "postfreeze assignment plan",
        )
        policy_path = _postfreeze(post_root, args.scoring_policy)
        policy, policy_raw = _load(policy_path, "postfreeze scoring policy")

        commitment_sha = sha256_bytes(commitment_raw)
        dispatch_sha = sha256_bytes(dispatch_raw)
        lock_sha = sha256_bytes(lock_raw)
        plan_sha = sha256_bytes(plan_raw)
        policy_sha = sha256_bytes(policy_raw)

        commitment_summary = validate_assignment_commitment(commitment)
        committed_packet_projections = (
            commitment_summary.responder_packet_projection_sha256_by_arm
        )
        dispatch_by_arm = validate_dispatch_manifest(
            dispatch,
            assignment_commitment_sha256=commitment_sha,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
        )
        lock_summary = validate_response_set_lock(
            lock,
            dispatch,
            dispatch_manifest_sha256=dispatch_sha,
            assignment_commitment_sha256=commitment_sha,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
        )
        lock_observed_text, _ = now_timestamp()
        policy_packet_projections = validate_policy_commitment(
            commitment,
            assignment_plan_sha256=plan_sha,
            scoring_policy_sha256=policy_sha,
        )
        if policy_packet_projections != committed_packet_projections:
            raise PolicyVerificationError(
                "assignment commitment packet projections changed across validation stages"
            )
        policy_by_arm, observed_tools = validate_scoring_policy(
            policy,
            plan,
            assignment_plan_sha256=plan_sha,
            root=post_root,
        )
        batch_id = non_placeholder_text(plan.get("batch_id"), "assignment plan batch_id")
        if dispatch.get("batch_id") != batch_id or lock.get("batch_id") != batch_id:
            raise PolicyVerificationError(
                "assignment, dispatch, and response-set lock batch identities disagree"
            )

        rows = plan.get("arms")
        if not isinstance(rows, list) or len(rows) != 4:
            raise PolicyVerificationError("assignment plan must contain exactly four arms")
        scorer_hashes: dict[str, str] = {}
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise PolicyVerificationError(f"assignment plan arms[{index}] must be an object")
            arm = non_placeholder_text(row.get("arm_code"), f"assignment plan arms[{index}].arm_code")
            if arm not in dispatch_by_arm or arm not in policy_by_arm:
                raise PolicyVerificationError(f"assignment arm {arm} is absent from dispatch or policy")
            scorer_surface = non_placeholder_text(
                row.get("scorer_intake_surface"),
                f"assignment plan {arm}.scorer_intake_surface",
            )
            scorer_path = _postfreeze(post_root, scorer_surface)
            scorer, scorer_raw = _load(scorer_path, f"postfreeze scorer intake {arm}")
            validate_scorer_against_policy(
                scorer,
                expected_policy=policy_by_arm[arm],
                arm=arm,
                scoring_policy_surface=DEFAULT_POLICY,
                scoring_policy_sha256=policy_sha,
            )
            packet_surface = non_placeholder_text(
                scorer.get("responder_only_surface"),
                f"postfreeze scorer {arm}.responder_only_surface",
            )
            packet, packet_raw = _load(
                _postfreeze(post_root, packet_surface),
                f"postfreeze responder packet {arm}",
            )
            packet_sha = hashlib.sha256(packet_raw).hexdigest()
            if scorer.get("responder_only_sha256") != packet_sha:
                raise PolicyVerificationError(
                    f"postfreeze scorer {arm} responder-packet hash drifted"
                )
            if dispatch_by_arm[arm].get("responder_packet_sha256") != packet_sha:
                raise PolicyVerificationError(
                    f"postfreeze responder packet {arm} disagrees with prefreeze dispatch"
                )
            packet_projection_sha = responder_packet_projection_sha256(packet)
            if packet_projection_sha != committed_packet_projections[arm]:
                raise PolicyVerificationError(
                    f"postfreeze responder packet {arm} projection disagrees with the preanswer commitment"
                )
            scorer_hashes[arm] = hashlib.sha256(scorer_raw).hexdigest()

        verified_text, _ = now_timestamp()
        receipt = {
            "project": "DelayBasin",
            "id": f"{batch_id}-postfreeze-policy-verification",
            "record_type": POLICY_VERIFICATION_RECORD_TYPE,
            "policy_verification_contract_version": POLICY_VERIFICATION_CONTRACT_VERSION,
            "batch_id": batch_id,
            "assignment_commitment_sha256": commitment_sha,
            "assignment_plan_sha256": plan_sha,
            "scoring_policy_sha256": policy_sha,
            "dispatch_manifest_sha256": dispatch_sha,
            "response_set_lock_sha256": lock_sha,
            "verifier_id": verifier_id,
            "response_set_locked_at": lock_summary.response_set_locked_at,
            "verification_started_at": verification_started_text,
            "verification_started_at_source": POLICY_VERIFICATION_STARTED_AT_SOURCE,
            "response_set_lock_observed_at": lock_observed_text,
            "response_set_lock_observed_at_source": POLICY_LOCK_OBSERVED_AT_SOURCE,
            "verified_at": verified_text,
            "verified_at_source": POLICY_VERIFIED_AT_SOURCE,
            "postfreeze_material_opened_only_after_response_set_lock": True,
            "scorer_intake_sha256_by_arm": scorer_hashes,
            "responder_packet_projection_sha256_by_arm": committed_packet_projections,
            "tool_sha256_by_surface": observed_tools,
            "verification_state": POLICY_VERIFICATION_STATE,
            "non_claim": "digest-bound postfreeze commitment verification with verifier-local artifact observations; collector and verifier clocks are not compared; not trusted timestamping, identity proof, scorer independence, completed external evidence, or causal burden identification",
        }
        # Validate our own shape before publication so producer and consumer use
        # one contract. The final scorer repeats this check against current bytes.
        from oq0266_isolated_scoring_policy_lib import validate_policy_verification_receipt

        validate_policy_verification_receipt(
            receipt,
            batch_id=batch_id,
            assignment_commitment_sha256=commitment_sha,
            assignment_plan_sha256=plan_sha,
            scoring_policy_sha256=policy_sha,
            dispatch_manifest_sha256=dispatch_sha,
            response_set_lock_sha256=lock_sha,
            response_set_locked_at=lock_summary.response_set_locked_at,
            scorer_intake_sha256_by_arm=scorer_hashes,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
            tool_sha256_by_surface=observed_tools,
        )
        write_new_json(_prefreeze(args.out), receipt, readonly=True)
    except (
        CommitmentContractError,
        ExternalRunArtifactError,
        PolicyVerificationError,
        ResponseSetContractError,
        ScoringPolicyContractError,
    ) as exc:
        raise SystemExit(str(exc)) from exc

    print(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Assemble one self-contained OQ-0266 isolated-run evidence capsule.

The helper validates the exact source kits, response-set lock, postfreeze-policy
receipt, and all four response/custody/score-sheet chains.  It then snapshots
both source kits and every dynamic artifact into one deterministic no-clobber
ZIP.  Final aggregation can replay the evidence from this capsule without
consulting mutable plan, policy, packet, template, or scorer files outside it.
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

from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    LOCK_MEMBER,
    POLICY_RECEIPT_MEMBER,
    POSTFREEZE_KIT_MEMBER,
    PREFREEZE_KIT_MEMBER,
    RUN_BUNDLE_CONTRACT_VERSION,
    RUN_BUNDLE_RECORD_TYPE,
    RUN_BUNDLE_STATE,
    RUN_MANIFEST_FIELDS,
    RUN_MANIFEST_MEMBER,
    evidence_record_member,
    load_run_bundle,
    read_safe_zip_members,
    response_member,
    score_sheet_member,
)
from priority_zero_external_run_artifact_lib import (  # type: ignore  # noqa: E402
    ExternalRunArtifactError,
    non_placeholder_text,
    resolve_input,
    sha256_bytes,
    strict_json,
    write_new_zip,
)

PILOT = "cloudtainer/oq0266-isolated-semantic-pilot"
DEFAULT_TEMPLATE = f"{PILOT}/run-manifest-template.json"
DEFAULT_BATCH_MANIFEST = f"{PILOT}/batch-manifest.json"
DISPATCH_SURFACE = f"{PILOT}/dispatch-manifest.json"
COMMITMENT_SURFACE = f"{PILOT}/assignment-commitment.json"
LOCK_LABEL = "response-set-lock"
POLICY_LABEL = "postfreeze-policy-verification"


class RunManifestPreparationError(ValueError):
    pass


def _resolve(path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else pathlib.Path.cwd() / candidate


def _root_path(surface: str) -> pathlib.Path:
    return ROOT / pathlib.PurePosixPath(surface)


def _parse_arm_paths(values: list[str], option: str) -> dict[str, pathlib.Path]:
    result: dict[str, pathlib.Path] = {}
    for index, value in enumerate(values):
        if "=" not in value:
            raise RunManifestPreparationError(
                f"{option} value {index + 1} must use ARM_CODE=PATH"
            )
        arm, raw_path = value.split("=", 1)
        try:
            arm = non_placeholder_text(arm, f"{option} arm")
            raw_path = non_placeholder_text(raw_path, f"{option} {arm} path")
        except ExternalRunArtifactError as exc:
            raise RunManifestPreparationError(str(exc)) from exc
        if arm in result:
            raise RunManifestPreparationError(f"duplicate {option} arm: {arm}")
        result[arm] = _resolve(raw_path)
    return result


def _load(path: pathlib.Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        return strict_json(path, label)
    except ExternalRunArtifactError as exc:
        raise RunManifestPreparationError(str(exc)) from exc


def _prerequisite_hashes(custody: dict[str, Any], arm: str) -> dict[str, str]:
    rows = custody.get("prerequisite_artifacts")
    if not isinstance(rows, list):
        raise RunManifestPreparationError(
            f"{arm} custody record has no prerequisite_artifacts list"
        )
    result: dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise RunManifestPreparationError(
                f"{arm} custody prerequisite_artifacts[{index}] must be an object"
            )
        try:
            label = non_placeholder_text(
                row.get("label"), f"{arm} custody prerequisite label"
            )
            digest = non_placeholder_text(
                row.get("artifact_sha256"),
                f"{arm} custody prerequisite {label} artifact_sha256",
            )
        except ExternalRunArtifactError as exc:
            raise RunManifestPreparationError(str(exc)) from exc
        if label in result:
            raise RunManifestPreparationError(
                f"{arm} custody record duplicates prerequisite label {label}"
            )
        result[label] = digest
    return result


def _template_arm_order(template: dict[str, Any]) -> list[str]:
    if set(template) != RUN_MANIFEST_FIELDS:
        raise RunManifestPreparationError(
            "run-capsule manifest template fields drifted: "
            f"observed={sorted(template)} expected={sorted(RUN_MANIFEST_FIELDS)}"
        )
    if template.get("project") != "DelayBasin":
        raise RunManifestPreparationError("run-capsule template project must be DelayBasin")
    if template.get("record_type") != RUN_BUNDLE_RECORD_TYPE:
        raise RunManifestPreparationError(
            f"run-capsule template record_type must be {RUN_BUNDLE_RECORD_TYPE}"
        )
    if template.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
        raise RunManifestPreparationError(
            f"run-capsule template contract must be {RUN_BUNDLE_CONTRACT_VERSION}"
        )
    if template.get("run_bundle_state") != RUN_BUNDLE_STATE:
        raise RunManifestPreparationError(
            f"run-capsule template state must be {RUN_BUNDLE_STATE}"
        )
    expected_members = {
        "prefreeze_dispatch_kit_member": PREFREEZE_KIT_MEMBER,
        "postfreeze_batch_kit_member": POSTFREEZE_KIT_MEMBER,
        "response_set_lock_member": LOCK_MEMBER,
        "postfreeze_policy_verification_member": POLICY_RECEIPT_MEMBER,
    }
    for field, expected in expected_members.items():
        if template.get(field) != expected:
            raise RunManifestPreparationError(
                f"run-capsule template {field} must be {expected}"
            )
    rows = template.get("arms")
    if not isinstance(rows, list):
        raise RunManifestPreparationError("run-capsule template arms must be a list")
    arm_order: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise RunManifestPreparationError(
                f"run-capsule template arms[{index}] must be an object"
            )
        arm_order.append(
            non_placeholder_text(
                row.get("arm_code"),
                f"run-capsule template arms[{index}].arm_code",
            )
        )
    if len(arm_order) != 4 or len(set(arm_order)) != 4:
        raise RunManifestPreparationError(
            "run-capsule template must contain exactly four unique arm rows"
        )
    return arm_order


def _verify_postfreeze_kit_matches_root(members: dict[str, bytes]) -> None:
    for surface, raw in members.items():
        path = _root_path(surface)
        if not path.exists() or not path.is_file():
            raise RunManifestPreparationError(
                f"postfreeze kit member is absent from the executing kit root: {surface}"
            )
        if path.read_bytes() != raw:
            raise RunManifestPreparationError(
                f"postfreeze kit member differs from the executing kit root: {surface}"
            )


def _verify_prefreeze_kit(
    raw: bytes,
    members: dict[str, bytes],
    *,
    batch_manifest: dict[str, Any],
) -> None:
    observed_sha = sha256_bytes(raw)
    if batch_manifest.get("prefreeze_dispatch_kit_sha256") != observed_sha:
        raise RunManifestPreparationError(
            "prefreeze dispatch kit SHA-256 disagrees with the postfreeze batch manifest"
        )
    for surface in [DISPATCH_SURFACE, COMMITMENT_SURFACE]:
        if surface not in members:
            raise RunManifestPreparationError(
                f"prefreeze dispatch kit is missing required member: {surface}"
            )
        if members[surface] != _root_path(surface).read_bytes():
            raise RunManifestPreparationError(
                f"prefreeze and postfreeze kits disagree on exact bytes for {surface}"
            )
    dispatch, _ = _load(_root_path(DISPATCH_SURFACE), "dispatch manifest")
    rows = dispatch.get("arms")
    if not isinstance(rows, list) or len(rows) != 4:
        raise RunManifestPreparationError("dispatch manifest must contain exactly four arms")
    for row in rows:
        if not isinstance(row, dict):
            raise RunManifestPreparationError("dispatch manifest arm rows must be objects")
        arm = non_placeholder_text(row.get("arm_code"), "dispatch arm_code")
        surface = non_placeholder_text(
            row.get("responder_bundle_surface"), f"dispatch {arm}.responder_bundle_surface"
        )
        if surface not in members:
            raise RunManifestPreparationError(
                f"prefreeze dispatch kit is missing responder bundle for {arm}: {surface}"
            )
        bundle_raw = members[surface]
        if sha256_bytes(bundle_raw) != row.get("responder_bundle_sha256"):
            raise RunManifestPreparationError(
                f"prefreeze responder bundle hash disagrees with dispatch manifest for {arm}"
            )
        nested = read_safe_zip_members(bundle_raw, f"prefreeze responder bundle {arm}")
        expected_names = row.get("responder_bundle_members")
        if not isinstance(expected_names, list) or list(nested) != expected_names:
            raise RunManifestPreparationError(
                f"prefreeze responder bundle topology disagrees with dispatch manifest for {arm}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefreeze-dispatch-kit", required=True)
    parser.add_argument("--postfreeze-batch-kit", required=True)
    parser.add_argument("--response-set-lock", required=True)
    parser.add_argument("--policy-verification", required=True)
    parser.add_argument("--response", action="append", required=True, metavar="ARM=PATH")
    parser.add_argument("--evidence-record", action="append", required=True, metavar="ARM=PATH")
    parser.add_argument("--score-sheet", action="append", required=True, metavar="ARM=PATH")
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--batch-manifest", default=DEFAULT_BATCH_MANIFEST)
    parser.add_argument("--out", required=True, help="new self-contained run-capsule ZIP path")
    args = parser.parse_args()

    try:
        template_path = pathlib.Path(args.template)
        if not template_path.is_absolute():
            template_path = ROOT / template_path
        template, _ = _load(template_path, "run-capsule manifest template")
        arm_order = _template_arm_order(template)

        batch_manifest_path = pathlib.Path(args.batch_manifest)
        if not batch_manifest_path.is_absolute():
            batch_manifest_path = ROOT / batch_manifest_path
        batch_manifest, _ = _load(batch_manifest_path, "postfreeze batch manifest")

        prefreeze_path = _resolve(args.prefreeze_dispatch_kit)
        postfreeze_path = _resolve(args.postfreeze_batch_kit)
        if not prefreeze_path.exists() or not prefreeze_path.is_file():
            raise RunManifestPreparationError(
                f"missing original prefreeze dispatch kit: {prefreeze_path}"
            )
        if not postfreeze_path.exists() or not postfreeze_path.is_file():
            raise RunManifestPreparationError(
                f"missing original postfreeze batch kit: {postfreeze_path}"
            )
        prefreeze_raw = prefreeze_path.read_bytes()
        postfreeze_raw = postfreeze_path.read_bytes()
        prefreeze_members = read_safe_zip_members(
            prefreeze_raw, "source prefreeze dispatch kit"
        )
        postfreeze_members = read_safe_zip_members(
            postfreeze_raw, "source postfreeze batch kit"
        )
        _verify_postfreeze_kit_matches_root(postfreeze_members)
        _verify_prefreeze_kit(
            prefreeze_raw,
            prefreeze_members,
            batch_manifest=batch_manifest,
        )
        if batch_manifest.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
            raise RunManifestPreparationError(
                "postfreeze batch manifest does not require the current evidence-capsule contract"
            )

        lock_path = _resolve(args.response_set_lock)
        policy_path = _resolve(args.policy_verification)
        lock, lock_raw = _load(lock_path, "response-set lock")
        policy, policy_raw = _load(policy_path, "postfreeze policy verification")
        lock_sha = sha256_bytes(lock_raw)
        policy_sha = sha256_bytes(policy_raw)
        if policy.get("response_set_lock_sha256") != lock_sha:
            raise RunManifestPreparationError(
                "postfreeze policy verification does not bind the supplied response-set lock bytes"
            )
        if (
            template.get("batch_id") != lock.get("batch_id")
            or template.get("batch_id") != policy.get("batch_id")
            or template.get("batch_id") != batch_manifest.get("batch_id")
        ):
            raise RunManifestPreparationError(
                "run-capsule template, batch manifest, response-set lock, and policy receipt batch IDs disagree"
            )

        response_paths = _parse_arm_paths(args.response, "--response")
        custody_paths = _parse_arm_paths(args.evidence_record, "--evidence-record")
        score_paths = _parse_arm_paths(args.score_sheet, "--score-sheet")
        expected = set(arm_order)
        for label, mapping in [
            ("responses", response_paths),
            ("custody records", custody_paths),
            ("score sheets", score_paths),
        ]:
            if set(mapping) != expected:
                raise RunManifestPreparationError(
                    f"{label} arm set drifted: observed={sorted(mapping)} expected={sorted(expected)}"
                )

        lock_rows = lock.get("responses")
        if not isinstance(lock_rows, list):
            raise RunManifestPreparationError("response-set lock responses must be a list")
        lock_by_arm = {
            row.get("arm_code"): row for row in lock_rows if isinstance(row, dict)
        }
        if set(lock_by_arm) != expected:
            raise RunManifestPreparationError(
                "response-set lock arm set disagrees with run-capsule template"
            )

        completed_rows: list[dict[str, str]] = []
        member_payloads: list[tuple[str, bytes]] = []
        for arm in arm_order:
            response, response_raw = _load(response_paths[arm], f"{arm} response")
            custody, custody_raw = _load(custody_paths[arm], f"{arm} custody record")
            score, score_raw = _load(score_paths[arm], f"{arm} score sheet")
            response_sha = sha256_bytes(response_raw)
            custody_sha = sha256_bytes(custody_raw)
            score_sha = sha256_bytes(score_raw)
            if lock_by_arm[arm].get("response_file_sha256") != response_sha:
                raise RunManifestPreparationError(
                    f"{arm} response bytes disagree with the response-set lock"
                )
            if custody.get("response_file_sha256") != response_sha:
                raise RunManifestPreparationError(
                    f"{arm} custody record does not bind the supplied response bytes"
                )
            prerequisites = _prerequisite_hashes(custody, arm)
            expected_prerequisites = {
                LOCK_LABEL: lock_sha,
                POLICY_LABEL: policy_sha,
            }
            if prerequisites != expected_prerequisites:
                raise RunManifestPreparationError(
                    f"{arm} custody prerequisites drifted: observed={prerequisites} "
                    f"expected={expected_prerequisites}"
                )
            if score.get("response_file_sha256") != response_sha:
                raise RunManifestPreparationError(
                    f"{arm} score sheet does not bind the supplied response bytes"
                )
            if score.get("custody_evidence_record_sha256") != custody_sha:
                raise RunManifestPreparationError(
                    f"{arm} score sheet does not bind the supplied custody bytes"
                )
            completed_rows.append(
                {
                    "arm_code": arm,
                    "response_member": response_member(arm),
                    "response_file_sha256": response_sha,
                    "evidence_record_member": evidence_record_member(arm),
                    "evidence_record_file_sha256": custody_sha,
                    "score_sheet_member": score_sheet_member(arm),
                    "score_sheet_file_sha256": score_sha,
                }
            )
            member_payloads.extend(
                [
                    (response_member(arm), response_raw),
                    (evidence_record_member(arm), custody_raw),
                    (score_sheet_member(arm), score_raw),
                ]
            )

        manifest = {
            "project": "DelayBasin",
            "record_type": RUN_BUNDLE_RECORD_TYPE,
            "run_bundle_contract_version": RUN_BUNDLE_CONTRACT_VERSION,
            "run_bundle_state": RUN_BUNDLE_STATE,
            "batch_id": template["batch_id"],
            "assignment_plan_sha256": template["assignment_plan_sha256"],
            "prefreeze_dispatch_kit_member": PREFREEZE_KIT_MEMBER,
            "prefreeze_dispatch_kit_sha256": sha256_bytes(prefreeze_raw),
            "postfreeze_batch_kit_member": POSTFREEZE_KIT_MEMBER,
            "postfreeze_batch_kit_sha256": sha256_bytes(postfreeze_raw),
            "response_set_lock_member": LOCK_MEMBER,
            "response_set_lock_sha256": lock_sha,
            "postfreeze_policy_verification_member": POLICY_RECEIPT_MEMBER,
            "postfreeze_policy_verification_sha256": policy_sha,
            "arms": completed_rows,
            "non_claim": (
                "self-contained exact-byte evidence handoff only; final evidence state is determined "
                "by a separately trusted verifier and the capsule does not prove signer identity, "
                "trusted time, real-world independence, or non-collusion"
            ),
        }
        manifest_raw = (
            json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        ).encode("utf-8")
        members = [
            (RUN_MANIFEST_MEMBER, manifest_raw),
            (PREFREEZE_KIT_MEMBER, prefreeze_raw),
            (POSTFREEZE_KIT_MEMBER, postfreeze_raw),
            (LOCK_MEMBER, lock_raw),
            (POLICY_RECEIPT_MEMBER, policy_raw),
            *member_payloads,
        ]
        out = resolve_input(args.out)
        write_new_zip(out, members, readonly=True)
        loaded = load_run_bundle(
            out,
            expected_batch_id=template["batch_id"],
            expected_assignment_plan_sha256=template["assignment_plan_sha256"],
            expected_arm_codes=expected,
        )
    except (
        ExternalRunArtifactError,
        RunManifestPreparationError,
        ValueError,
    ) as exc:
        raise SystemExit(str(exc)) from exc

    print(
        json.dumps(
            {
                "run_bundle": str(out),
                "run_bundle_sha256": loaded.bundle_sha256,
                "preserve_this_digest_outside_the_assembly_directory": loaded.bundle_sha256,
                "run_manifest_member": RUN_MANIFEST_MEMBER,
                "run_manifest_sha256": loaded.manifest_sha256,
                "prefreeze_dispatch_kit_sha256": manifest["prefreeze_dispatch_kit_sha256"],
                "postfreeze_batch_kit_sha256": manifest["postfreeze_batch_kit_sha256"],
                "response_set_lock_sha256": lock_sha,
                "postfreeze_policy_verification_sha256": policy_sha,
                "arm_count": len(completed_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

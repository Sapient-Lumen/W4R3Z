#!/usr/bin/env python3
"""Freeze the four-response barrier before any OQ-0266 postfreeze material opens.

Run this only from the prefreeze dispatch kit after receiving all four
responder-tool-finalized response JSON files.  The command validates every
response against its exact one-arm bundle without opening the assignment plan,
custody templates, scorer intakes, or score sheets.  It then publishes one
read-only lock binding all response bytes, responder-reported finalization times, and collector-local observations of those exact artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile
from typing import Any

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    CommitmentContractError,
    responder_packet_projection_sha256,
    validate_assignment_commitment,
)
from priority_zero_external_run_artifact_lib import (  # type: ignore  # noqa: E402
    ExternalRunArtifactError,
    non_placeholder_text,
    now_timestamp,
    resolve_input,
    sha256_bytes,
    strict_json,
    strict_json_bytes,
    write_new_json,
)
from priority_zero_external_replay_response_lib import (  # type: ignore  # noqa: E402
    ResponseContractError,
    validate_finalized_response,
)
from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    EXPECTED_ARM_COUNT,
    LOCK_CLOCK_SOURCE,
    RESPONSE_OBSERVED_CLOCK_SOURCE,
    RESPONSE_SET_CONTRACT_VERSION,
    RESPONSE_SET_RECORD_TYPE,
    RESPONSE_SET_STATE,
    ResponseSetContractError,
    validate_dispatch_manifest,
    validate_response_set_lock,
)

DEFAULT_DISPATCH = "cloudtainer/oq0266-isolated-semantic-pilot/dispatch-manifest.json"
DEFAULT_COMMITMENT = "cloudtainer/oq0266-isolated-semantic-pilot/assignment-commitment.json"


def _resolve(path: str | pathlib.Path) -> pathlib.Path:
    candidate = pathlib.Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def _response_args(values: list[str]) -> dict[str, pathlib.Path]:
    by_arm: dict[str, pathlib.Path] = {}
    for index, value in enumerate(values):
        if "=" not in value:
            raise ResponseSetContractError(
                f"--response value {index + 1} must use ARM_CODE=/path/to/final-response.json"
            )
        arm, raw_path = value.split("=", 1)
        arm = arm.strip()
        raw_path = raw_path.strip()
        if not arm or not raw_path:
            raise ResponseSetContractError(
                f"--response value {index + 1} must contain a non-empty arm and path"
            )
        if arm in by_arm:
            raise ResponseSetContractError(f"duplicate --response arm: {arm}")
        by_arm[arm] = resolve_input(raw_path)
    if len(by_arm) != EXPECTED_ARM_COUNT:
        raise ResponseSetContractError(
            f"exactly {EXPECTED_ARM_COUNT} --response ARM=PATH values are required"
        )
    return by_arm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--response",
        action="append",
        required=True,
        metavar="ARM=PATH",
        help="repeat exactly four times, once for each finalized opaque-arm response",
    )
    parser.add_argument("--collector-id", required=True)
    parser.add_argument("--exposure-notes", required=True)
    parser.add_argument(
        "--attest-clean-batch-barrier",
        action="store_true",
        help="attest that neither the postfreeze kit nor assignment mapping was opened before all four responses were frozen",
    )
    parser.add_argument("--dispatch-manifest", default=DEFAULT_DISPATCH)
    parser.add_argument("--commitment", default=DEFAULT_COMMITMENT)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    collection_started_text, _ = now_timestamp()
    if not args.attest_clean_batch_barrier:
        raise SystemExit(
            "--attest-clean-batch-barrier is required; the helper will not manufacture the all-response barrier attestation"
        )

    try:
        response_paths = _response_args(args.response)
        dispatch_path = _resolve(args.dispatch_manifest)
        commitment_path = _resolve(args.commitment)
        dispatch, dispatch_raw = strict_json(dispatch_path, "dispatch manifest")
        commitment, commitment_raw = strict_json(commitment_path, "assignment commitment")
        commitment_sha = sha256_bytes(commitment_raw)
        commitment_summary = validate_assignment_commitment(commitment)
        commitment_batch_id = commitment_summary.batch_id
        committed_arm_codes = set(commitment_summary.arm_codes)
        committed_packet_projections = (
            commitment_summary.responder_packet_projection_sha256_by_arm
        )
        dispatch_by_arm = validate_dispatch_manifest(
            dispatch,
            assignment_commitment_sha256=commitment_sha,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
        )
        if dispatch.get("batch_id") != commitment_batch_id:
            raise ResponseSetContractError(
                "dispatch manifest batch_id disagrees with assignment commitment"
            )
        if set(dispatch_by_arm) != committed_arm_codes:
            raise ResponseSetContractError(
                "dispatch manifest arm set disagrees with assignment commitment"
            )
        if set(response_paths) != set(dispatch_by_arm):
            raise ResponseSetContractError(
                f"--response arm set drifted: observed={sorted(response_paths)} expected={sorted(dispatch_by_arm)}"
            )

        lock_rows: list[dict[str, Any]] = []
        for arm in sorted(dispatch_by_arm):
            dispatch_row = dispatch_by_arm[arm]
            bundle_path = _resolve(dispatch_row["responder_bundle_surface"])
            bundle_raw = bundle_path.read_bytes()
            bundle_sha = sha256_bytes(bundle_raw)
            if bundle_sha != dispatch_row.get("responder_bundle_sha256"):
                raise ResponseSetContractError(
                    f"{arm} responder bundle hash disagrees with dispatch manifest"
                )
            with zipfile.ZipFile(bundle_path) as archive:
                bad = archive.testzip()
                if bad is not None:
                    raise ResponseSetContractError(
                        f"{arm} responder bundle failed ZIP integrity at member {bad}"
                    )
                members = archive.namelist()
                if members != dispatch_row.get("responder_bundle_members"):
                    raise ResponseSetContractError(
                        f"{arm} responder bundle member order/topology drifted"
                    )
                packet_surface = dispatch_row["responder_packet_surface"]
                template_surface = dispatch_row["response_template_surface"]
                packet_raw = archive.read(packet_surface)
                template_raw = archive.read(template_surface)
            packet = strict_json_bytes(packet_raw, f"{arm} responder packet in bundle")
            template = strict_json_bytes(template_raw, f"{arm} response template in bundle")
            packet_sha = sha256_bytes(packet_raw)
            template_sha = sha256_bytes(template_raw)
            if packet_sha != dispatch_row.get("responder_packet_sha256"):
                raise ResponseSetContractError(
                    f"{arm} responder packet hash disagrees with dispatch manifest"
                )
            if template_sha != dispatch_row.get("response_template_sha256"):
                raise ResponseSetContractError(
                    f"{arm} response template hash disagrees with dispatch manifest"
                )
            if packet.get("project") != "DelayBasin" or packet.get("batch_id") != dispatch.get("batch_id"):
                raise ResponseSetContractError(f"{arm} responder packet identity drifted")
            if packet.get("arm_code") != arm:
                raise ResponseSetContractError(f"{arm} responder packet arm_code drifted")
            if packet.get("assignment_commitment_sha256") != commitment_sha:
                raise ResponseSetContractError(
                    f"{arm} responder packet does not bind the supplied assignment commitment"
                )
            packet_projection_sha = responder_packet_projection_sha256(packet)
            if packet_projection_sha != committed_packet_projections[arm]:
                raise ResponseSetContractError(
                    f"{arm} responder packet projection disagrees with the preanswer commitment"
                )
            if (
                dispatch_row.get("responder_packet_projection_sha256")
                != packet_projection_sha
            ):
                raise ResponseSetContractError(
                    f"{arm} dispatch responder-packet projection hash drifted"
                )

            response, response_raw = strict_json(response_paths[arm], f"{arm} finalized response")
            response_summary = validate_finalized_response(
                response,
                template,
                expected_bundle_sha256=bundle_sha,
                expected_packet_sha256=packet_sha,
            )
            if response_summary.get("packet_labels") != [arm]:
                raise ResponseSetContractError(
                    f"{arm} response does not contain exactly its opaque arm row"
                )
            response_observed_text, _ = now_timestamp()
            lock_rows.append(
                {
                    "arm_code": arm,
                    "response_file_sha256": sha256_bytes(response_raw),
                    "responder_id": response_summary["responder_id"],
                    "response_finalized_at": response_summary["response_finalized_at"],
                    "response_observed_at": response_observed_text,
                    "response_observed_at_source": RESPONSE_OBSERVED_CLOCK_SOURCE,
                    "responder_bundle_sha256": bundle_sha,
                    "responder_packet_sha256": packet_sha,
                    "responder_packet_projection_sha256": packet_projection_sha,
                }
            )

        collector_id = non_placeholder_text(args.collector_id, "collector_id")
        exposure_notes = non_placeholder_text(args.exposure_notes, "exposure_notes")
        responder_ids = [row["responder_id"] for row in lock_rows]
        if len(responder_ids) != len(set(responder_ids)):
            duplicates = sorted({value for value in responder_ids if responder_ids.count(value) > 1})
            raise ResponseSetContractError(
                "one distinct responder is required per arm; duplicate responder IDs: "
                + ", ".join(duplicates)
            )
        if collector_id in set(responder_ids):
            raise ResponseSetContractError(
                "collector_id must differ from every responder_id"
            )

        locked_text, _ = now_timestamp()
        lock = {
            "project": "DelayBasin",
            "id": f"{dispatch['batch_id']}-response-set-lock",
            "record_type": RESPONSE_SET_RECORD_TYPE,
            "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
            "batch_id": dispatch["batch_id"],
            "dispatch_manifest_sha256": sha256_bytes(dispatch_raw),
            "assignment_commitment_sha256": commitment_sha,
            "response_count": len(lock_rows),
            "distinct_responder_count": len(set(responder_ids)),
            "response_set_state": RESPONSE_SET_STATE,
            "responses": lock_rows,
            "collector_attestation": {
                "collector_id": collector_id,
                "collection_started_at": collection_started_text,
                "response_set_locked_at": locked_text,
                "response_set_locked_at_source": LOCK_CLOCK_SOURCE,
                "postfreeze_kit_not_opened_before_response_set_lock": True,
                "assignment_mapping_not_opened_before_response_set_lock": True,
                "all_responses_received_as_tool_finalized_artifacts": True,
                "collector_is_distinct_from_all_responders": True,
                "exposure_notes": exposure_notes,
            },
            "non_claim": "digest-bound batch barrier with collector-local artifact observations; responder clocks are descriptive and not compared across machines; not a signature, trusted timestamp, identity proof, causal burden result, compact-gate confirmation, or independent certification",
        }
        validate_response_set_lock(
            lock,
            dispatch,
            dispatch_manifest_sha256=sha256_bytes(dispatch_raw),
            assignment_commitment_sha256=commitment_sha,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
            expected_responses_by_arm={row["arm_code"]: row for row in lock_rows},
        )
        out = resolve_input(args.out)
        write_new_json(out, lock, readonly=True)
    except (
        OSError,
        zipfile.BadZipFile,
        CommitmentContractError,
        ExternalRunArtifactError,
        ResponseContractError,
        ResponseSetContractError,
    ) as exc:
        raise SystemExit(str(exc)) from exc

    print(
        json.dumps(
            {
                "response_set_lock": str(out),
                "response_set_lock_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                "response_count": len(lock_rows),
                "distinct_responder_count": len(set(responder_ids)),
                "collector_id": collector_id,
                "response_set_locked_at": locked_text,
                "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

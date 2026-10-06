"""Initialize and finalize the responder artifact without scorer material.

Run ``init`` from the extracted responder bundle before answering.  Fill only
packet answers and per-packet/total operator cost.  Run ``finalize`` before any
custody, manifest, score-sheet, archive, or answer-key material is opened.  The
finalizer validates the complete response, records hashes and local process
clock timestamps, writes a new immutable candidate, and refuses overwrite.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib

from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    LOCAL_PROCESS_CLOCK,
    non_placeholder_text,
    now_timestamp,
    resolve_input,
    resolve_local,
    sha256_file,
    strict_json,
    write_new_json,
)
from priority_zero_external_replay_response_lib import (
    CURRENT_RESPONSE_PREPARATION_CONTRACT,
    FINALIZER_TOOL,
    FINAL_RESPONSE_STATE,
    ResponseContractError,
    TIMESTAMP_SOURCE,
    validate_draft_binding,
    validate_finalized_response,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
DEFAULT_PACKET = "assays/priority-zero-preanswer-clamped-external-replay-responder-only-2026-06-16.json"


def _load_local_contract(template_rel: str, packet_rel: str) -> tuple[dict, dict, str]:
    template, _ = strict_json(resolve_local(ROOT, template_rel), "response template")
    packet_path = resolve_local(ROOT, packet_rel)
    packet, _ = strict_json(packet_path, "responder packet")
    packet_sha = sha256_file(packet_path)
    if template.get("responder_packet_surface") != packet_rel:
        raise ExternalRunArtifactError("response template does not point to the selected responder packet")
    if template.get("responder_packet_sha256") != packet_sha:
        raise ExternalRunArtifactError("response template responder-packet hash drifted")
    if packet.get("surface") != packet_rel:
        raise ExternalRunArtifactError("responder packet does not identify its selected surface")
    if template.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
        raise ExternalRunArtifactError("response template is not the current responder-finalize-v1 contract")
    return template, packet, packet_sha


def command_init(args: argparse.Namespace) -> None:
    template, _, packet_sha = _load_local_contract(args.template, args.packet)
    responder_id = non_placeholder_text(args.responder_id, "responder_id")
    bundle_path = resolve_input(args.bundle_file)
    bundle_sha = sha256_file(bundle_path)
    started_text, _ = now_timestamp()

    draft = copy.deepcopy(template)
    draft["response_state"] = "pre-response-draft"
    draft["response_preparation_contract_version"] = CURRENT_RESPONSE_PREPARATION_CONTRACT
    stage = draft.get("responder_stage")
    if not isinstance(stage, dict):
        raise ExternalRunArtifactError("response template missing responder_stage")
    stage.update(
        {
            "responder_id": responder_id,
            "run_started_at": started_text,
            "run_completed_at": "",
            "saw_responder_bundle_sha256": bundle_sha,
            "saw_responder_packet_sha256": packet_sha,
            "no_scorer_key_before_response": None,
            "no_full_archive_before_response": None,
            "no_conversation_context_before_response": None,
            "accidental_exposure_notes": "",
        }
    )
    draft["response_artifact"] = {
        "draft_created_at": started_text,
        "finalized_at": "",
        "timestamp_source": TIMESTAMP_SOURCE,
        "finalizer_tool": FINALIZER_TOOL,
        "finalization_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
        "immutable_after_finalize": None,
    }
    out = resolve_input(args.out)
    write_new_json(out, draft)
    print(
        json.dumps(
            {
                "response_draft": str(out),
                "responder_id": responder_id,
                "run_started_at": started_text,
                "observed_responder_bundle_sha256": bundle_sha,
                "observed_responder_packet_sha256": packet_sha,
                "timestamp_source": LOCAL_PROCESS_CLOCK,
                "next": "fill every packet answer and packet cost, set the total cost, then run finalize before opening post-response material",
            },
            indent=2,
        )
    )


def command_finalize(args: argparse.Namespace) -> None:
    if not args.attest_clean_preanswer:
        raise ExternalRunArtifactError(
            "--attest-clean-preanswer is required; clean separation booleans are never inferred"
        )
    exposure_notes = non_placeholder_text(args.exposure_notes, "exposure_notes")
    template, _, packet_sha = _load_local_contract(args.template, args.packet)
    draft, _ = strict_json(resolve_input(args.draft), "response draft")
    bundle_sha = sha256_file(resolve_input(args.bundle_file))
    summary = validate_draft_binding(
        draft,
        template,
        expected_bundle_sha256=bundle_sha,
        expected_packet_sha256=packet_sha,
    )
    completed_text, completed_at = now_timestamp()
    if completed_at < summary["run_started"]:
        raise ExternalRunArtifactError("local clock moved backward before response finalization")

    final = copy.deepcopy(draft)
    final["response_state"] = FINAL_RESPONSE_STATE
    final["response_preparation_contract_version"] = CURRENT_RESPONSE_PREPARATION_CONTRACT
    stage = final["responder_stage"]
    stage.update(
        {
            "run_completed_at": completed_text,
            "no_scorer_key_before_response": True,
            "no_full_archive_before_response": True,
            "no_conversation_context_before_response": True,
            "accidental_exposure_notes": exposure_notes,
        }
    )
    final["response_artifact"] = {
        "draft_created_at": final.get("response_artifact", {}).get("draft_created_at", summary["run_started_at"]),
        "finalized_at": completed_text,
        "timestamp_source": TIMESTAMP_SOURCE,
        "finalizer_tool": FINALIZER_TOOL,
        "finalization_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
        "immutable_after_finalize": True,
    }
    validate_finalized_response(
        final,
        template,
        expected_bundle_sha256=bundle_sha,
        expected_packet_sha256=packet_sha,
    )
    out = resolve_input(args.out)
    write_new_json(out, final, readonly=True)
    print(
        json.dumps(
            {
                "frozen_response": str(out),
                "response_file_sha256": sha256_file(out),
                "responder_id": summary["responder_id"],
                "run_started_at": summary["run_started_at"],
                "response_finalized_at": completed_text,
                "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
                "next": "hand this exact file to a distinct custodian; do not edit it",
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a hash-bound response draft and record run start")
    init_parser.add_argument("--bundle-file", required=True, help="the original responder bundle ZIP handed to this responder")
    init_parser.add_argument("--responder-id", required=True)
    init_parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    init_parser.add_argument("--packet", default=DEFAULT_PACKET)
    init_parser.add_argument("--out", required=True)
    init_parser.set_defaults(func=command_init)

    finalize_parser = subparsers.add_parser("finalize", help="validate answers and write a new frozen response candidate")
    finalize_parser.add_argument("--draft", required=True)
    finalize_parser.add_argument("--bundle-file", required=True, help="the same original responder bundle ZIP used at init")
    finalize_parser.add_argument("--exposure-notes", required=True)
    finalize_parser.add_argument("--attest-clean-preanswer", action="store_true")
    finalize_parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    finalize_parser.add_argument("--packet", default=DEFAULT_PACKET)
    finalize_parser.add_argument("--out", required=True)
    finalize_parser.set_defaults(func=command_finalize)

    args = parser.parse_args()
    try:
        args.func(args)
    except (ExternalRunArtifactError, ResponseContractError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()

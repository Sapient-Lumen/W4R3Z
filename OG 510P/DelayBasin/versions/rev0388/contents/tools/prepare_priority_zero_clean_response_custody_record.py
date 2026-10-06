"""Prepare the current causal custody record for a finalized response.

The helper reruns the complete finalized-response contract, records a local
observation of those exact bytes, binds any template-required prerequisite
artifacts by hash, and atomically freezes custody before scorer material opens.
Cross-operator wall clocks are retained as descriptive observations only.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
from typing import Any

from priority_zero_causal_artifact_lib import CURRENT_CUSTODY_CONTRACT
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    now_timestamp,
    resolve_input,
    resolve_local,
    sha256_bytes,
    sha256_file,
    strict_json,
    write_new_json,
)
from priority_zero_external_replay_custody_lib import (
    CurrentCustodyContractError,
    validate_current_custody_record,
)
from priority_zero_external_replay_response_lib import (
    CURRENT_RESPONSE_PREPARATION_CONTRACT,
    ResponseContractError,
    validate_finalized_response,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = "assays/priority-zero-preanswer-clamped-clean-external-response-evidence-record-template-2026-06-16.json"
DEFAULT_RESPONSE_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
CUSTODY_OPEN_CLOCK_SOURCE = "local-process-clock-at-custody-helper-start"
RESPONSE_OBSERVED_CLOCK_SOURCE = "local-process-clock-after-finalized-response-validation"
PREREQUISITE_OBSERVED_CLOCK_SOURCE = "local-process-clock-after-prerequisite-read"
CUSTODY_FREEZE_CLOCK_SOURCE = "local-process-clock-before-custody-write"


def _parse_prerequisites(values: list[str]) -> dict[str, pathlib.Path]:
    result: dict[str, pathlib.Path] = {}
    for value in values:
        if "=" not in value:
            raise ExternalRunArtifactError(
                "--prerequisite must be LABEL=PATH (repeat once per required prerequisite)"
            )
        label, raw_path = value.split("=", 1)
        label = non_placeholder_text(label, "prerequisite label")
        raw_path = non_placeholder_text(raw_path, f"prerequisite {label} path")
        if label in result:
            raise ExternalRunArtifactError(f"duplicate --prerequisite label: {label}")
        result[label] = resolve_input(raw_path)
    return result


def _required_labels(template: dict[str, Any]) -> list[str]:
    value = template.get("required_prerequisite_labels")
    if not isinstance(value, list):
        raise ExternalRunArtifactError(
            "custody template required_prerequisite_labels must be a list"
        )
    labels: list[str] = []
    for index, item in enumerate(value):
        label = non_placeholder_text(item, f"required_prerequisite_labels[{index}]")
        if label in labels:
            raise ExternalRunArtifactError(
                f"custody template contains duplicate prerequisite label: {label}"
            )
        labels.append(label)
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_file", help="tool-finalized response JSON; it must already be immutable")
    parser.add_argument("--custodian-id", required=True)
    parser.add_argument("--pre-response-exposure-notes", required=True)
    parser.add_argument(
        "--prerequisite",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="bind a template-required prior-stage artifact; repeat for every required label",
    )
    parser.add_argument(
        "--attest-clean-preanswer",
        action="store_true",
        help="explicitly attest that only the responder bundle was shown before response and no post-response material leaked",
    )
    parser.add_argument("--out", required=True)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--response-template", default=DEFAULT_RESPONSE_TEMPLATE)
    args = parser.parse_args()

    custody_opened_text, custody_opened = now_timestamp()
    if not args.attest_clean_preanswer:
        raise SystemExit(
            "--attest-clean-preanswer is required; the helper will not manufacture clean custody booleans implicitly"
        )

    response_path = resolve_input(args.response_file)
    template_path = resolve_local(ROOT, args.template)
    response_template_path = resolve_local(ROOT, args.response_template)
    out = resolve_input(args.out)

    try:
        response, response_raw = strict_json(response_path, "response file")
        template, _ = strict_json(template_path, "custody template")
        response_template, _ = strict_json(response_template_path, "response template")
        if template.get("custody_contract_version") != CURRENT_CUSTODY_CONTRACT:
            raise ExternalRunArtifactError(
                f"custody template is not the current {CURRENT_CUSTODY_CONTRACT} contract"
            )
        if template.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
            raise ExternalRunArtifactError("custody template does not require the current responder-finalize-v1 response")

        response_summary = validate_finalized_response(
            response,
            response_template,
            expected_bundle_sha256=non_placeholder_text(
                template.get("responder_bundle_sha256"), "custody template responder_bundle_sha256"
            ),
            expected_packet_sha256=non_placeholder_text(
                template.get("responder_only_sha256"), "custody template responder_only_sha256"
            ),
        )
        response_observed_text, response_observed = now_timestamp()
        if response_observed < custody_opened:
            raise ExternalRunArtifactError("local clock moved backward while validating the response")

        responder_id = response_summary["responder_id"]
        custodian_id = non_placeholder_text(args.custodian_id, "custodian_id")
        if custodian_id == responder_id:
            raise ExternalRunArtifactError("custodian_id must differ from responder_id for clean evidence")
        exposure_notes = non_placeholder_text(
            args.pre_response_exposure_notes, "pre_response_exposure_notes"
        )

        required_labels = _required_labels(template)
        supplied = _parse_prerequisites(args.prerequisite)
        if list(supplied) != required_labels:
            raise ExternalRunArtifactError(
                "required prerequisite labels/order drifted: "
                f"observed={list(supplied)} expected={required_labels}"
            )
        prerequisite_rows: list[dict[str, str]] = []
        for label in required_labels:
            path = supplied[label]
            if not path.exists() or not path.is_file():
                raise ExternalRunArtifactError(f"missing prerequisite artifact {label}: {path}")
            raw = path.read_bytes()
            observed_text, observed = now_timestamp()
            if observed < custody_opened:
                raise ExternalRunArtifactError(
                    f"local clock moved backward while reading prerequisite {label}"
                )
            prerequisite_rows.append(
                {
                    "label": label,
                    "artifact_sha256": sha256_bytes(raw),
                    "observed_at": observed_text,
                    "observed_at_source": PREREQUISITE_OBSERVED_CLOCK_SOURCE,
                }
            )

        response_frozen_text = response_summary["response_finalized_at"]
        custody_frozen_text, custody_frozen = now_timestamp()
        if custody_frozen < response_observed:
            raise ExternalRunArtifactError("local clock moved backward during custody preparation")

        record = copy.deepcopy(template)
        record.update(
            {
                "id": "priority-zero-preanswer-clamped-clean-external-response-custody-record",
                "record_type": "custody-evidence-record",
                "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
                "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
                "evidence_state": "completed-response-and-causal-custody-record-frozen-before-scorer-kit",
                "response_file_sha256": sha256_bytes(response_raw),
                "response_finalized_at": response_frozen_text,
                "prerequisite_artifacts": prerequisite_rows,
            }
        )
        record.pop("scorer_intake_surface", None)
        record.pop("scorer_intake_sha256", None)
        record["custodian_attestation"] = {
            "custodian_id": custodian_id,
            "responder_id": responder_id,
            "response_frozen_at": response_frozen_text,
            "response_frozen_at_source": "response.response_artifact.finalized_at",
            "custody_kit_opened_at": custody_opened_text,
            "custody_kit_opened_at_source": CUSTODY_OPEN_CLOCK_SOURCE,
            "response_observed_at": response_observed_text,
            "response_observed_at_source": RESPONSE_OBSERVED_CLOCK_SOURCE,
            "custody_record_frozen_at": custody_frozen_text,
            "custody_record_frozen_at_source": CUSTODY_FREEZE_CLOCK_SOURCE,
            "pre_response_materials_given": template["responder_bundle_surface"],
            "pre_response_exposure_notes": exposure_notes,
            "responder_was_given_only_responder_bundle_before_response": True,
            "full_archive_not_given_before_response": True,
            "conversation_not_shown_before_response": True,
            "answer_key_not_shown_before_response": True,
            "response_hash_recorded_before_custody_record_frozen": True,
            "custodian_is_distinct_from_responder": True,
            "custody_helper_observed_exact_response_before_record_freeze": True,
            "required_prerequisites_observed_before_custody_record_frozen": True,
            "scorer_kit_not_opened_before_custody_record_frozen": True,
            "score_sheet_template_not_opened_before_custody_record_frozen": True,
            "handoff_manifest_not_opened_before_custody_record_frozen": True,
        }
        validate_current_custody_record(
            record,
            template,
            response=response,
            response_summary=response_summary,
            response_file_sha256=sha256_bytes(response_raw),
        )
        write_new_json(out, record, readonly=True)
    except (
        ExternalRunArtifactError,
        ResponseContractError,
        CurrentCustodyContractError,
    ) as exc:
        raise SystemExit(str(exc)) from exc

    print(
        json.dumps(
            {
                "custody_record": str(out),
                "custody_record_sha256": sha256_file(out),
                "response_file_sha256": record["response_file_sha256"],
                "responder_id": responder_id,
                "custodian_id": custodian_id,
                "run_started_at": response_summary["run_started_at"],
                "run_completed_at": response_summary["run_completed_at"],
                "responder_reported_finalized_at": response_frozen_text,
                "custody_kit_opened_at": custody_opened_text,
                "response_observed_at": response_observed_text,
                "custody_record_frozen_at": custody_frozen_text,
                "prerequisite_artifact_count": len(prerequisite_rows),
                "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
                "custody_contract_version": CURRENT_CUSTODY_CONTRACT,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

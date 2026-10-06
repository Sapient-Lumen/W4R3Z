"""Bind and finalize a causal Priority-0 external replay score sheet.

The score-sheet draft records when this local scorer process opened and when it
finished validating the exact custody bytes.  Cross-operator order is carried
by response/custody hashes, not by comparing unrelated wall clocks.  Finalize
rebinds every input, validates manual scoring, records local completion, and
atomically publishes a new read-only artifact.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import pathlib

from priority_zero_causal_artifact_lib import (
    CURRENT_SCORING_CONTRACT,
    CausalArtifactError,
    validate_local_order,
)
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    now_timestamp,
    parse_timestamp,
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
DEFAULT_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-score-sheet-template-2026-06-16.json"
DEFAULT_SCORER = "assays/priority-zero-preanswer-clamped-external-replay-scorer-intake-2026-06-16.json"
DEFAULT_RESPONSE_TEMPLATE = "assays/priority-zero-preanswer-clamped-external-replay-response-template-2026-06-16.json"
SCORER_OPEN_CLOCK_SOURCE = "local-process-clock-at-score-sheet-init"
CUSTODY_OBSERVED_CLOCK_SOURCE = "local-process-clock-after-custody-validation"
SCORED_CLOCK_SOURCE = "local-process-clock-at-score-sheet-finalize"


class ScoreSheetPreparationError(ValueError):
    pass


def _load_bound_inputs(
    args: argparse.Namespace,
) -> tuple[dict, bytes, dict, bytes, dict, bytes, dict]:
    response, response_raw = strict_json(resolve_input(args.response_file), "response file")
    evidence, evidence_raw = strict_json(resolve_input(args.evidence_record), "custody evidence record")
    scorer, scorer_raw = strict_json(resolve_local(ROOT, args.scorer_intake), "scorer intake")
    response_template, _ = strict_json(
        resolve_local(ROOT, args.response_template), "response template"
    )
    if response.get("project") != "DelayBasin":
        raise ScoreSheetPreparationError("response project must be DelayBasin")
    if evidence.get("project") != "DelayBasin" or evidence.get("record_type") != "custody-evidence-record":
        raise ScoreSheetPreparationError("custody evidence record identity is invalid")
    if evidence.get("custody_contract_version") != CURRENT_SCORING_CONTRACT:
        raise ScoreSheetPreparationError(
            f"custody evidence is not the current {CURRENT_SCORING_CONTRACT} contract"
        )
    if evidence.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
        raise ScoreSheetPreparationError("custody evidence is not bound to a responder-finalize-v1 response")
    if evidence.get("response_file_sha256") != sha256_bytes(response_raw):
        raise ScoreSheetPreparationError("custody evidence response hash does not match exact response bytes")
    if scorer.get("surface") != args.scorer_intake:
        raise ScoreSheetPreparationError("selected scorer intake surface does not identify itself")
    if scorer.get("response_preparation_contract_version") != CURRENT_RESPONSE_PREPARATION_CONTRACT:
        raise ScoreSheetPreparationError("selected scorer intake does not require responder-finalize-v1")

    response_summary = validate_finalized_response(
        response,
        response_template,
        expected_bundle_sha256=non_placeholder_text(
            scorer.get("responder_bundle_sha256"), "scorer responder_bundle_sha256"
        ),
        expected_packet_sha256=non_placeholder_text(
            scorer.get("responder_only_sha256"), "scorer responder_only_sha256"
        ),
    )

    custody_template_rel = non_placeholder_text(
        scorer.get("evidence_record_template_surface"),
        "scorer evidence_record_template_surface",
    )
    custody_template, custody_template_raw = strict_json(
        resolve_local(ROOT, custody_template_rel), "custody template"
    )
    if scorer.get("evidence_record_template_sha256") != sha256_bytes(custody_template_raw):
        raise ScoreSheetPreparationError("scorer custody-template hash drifted")
    for scorer_key, template_key, label in [
        ("responder_bundle_sha256", "responder_bundle_sha256", "responder bundle"),
        ("responder_only_sha256", "responder_only_sha256", "responder packet"),
        ("response_template_sha256", "response_template_sha256", "response template"),
    ]:
        if scorer.get(scorer_key) != custody_template.get(template_key):
            raise ScoreSheetPreparationError(
                f"scorer and custody template disagree on {label} identity"
            )
    validate_current_custody_record(
        evidence,
        custody_template,
        response=response,
        response_summary=response_summary,
        response_file_sha256=sha256_bytes(response_raw),
    )
    return response, response_raw, evidence, evidence_raw, scorer, scorer_raw, response_summary


def _base_bound_sheet(
    args: argparse.Namespace,
    *,
    scorer_opened_text: str,
    custody_observed_text: str | None = None,
) -> tuple[dict, dict, dict, dict, str]:
    response, response_raw, evidence, evidence_raw, scorer, scorer_raw, response_summary = _load_bound_inputs(args)
    if custody_observed_text is None:
        custody_observed_text, _ = now_timestamp()
    template, _ = strict_json(resolve_local(ROOT, args.template), "score sheet template")
    if template.get("scoring_contract_version") != CURRENT_SCORING_CONTRACT:
        raise ScoreSheetPreparationError(
            f"score sheet template is not the current {CURRENT_SCORING_CONTRACT} contract"
        )
    scorer_id = non_placeholder_text(args.scorer_id, "scorer_id")
    if scorer_id == response_summary["responder_id"]:
        raise ScoreSheetPreparationError("scorer_id must differ from responder_id")
    try:
        local_texts, _ = validate_local_order(
            [
                ("scorer_attestation.scorer_kit_opened_at", scorer_opened_text),
                ("scorer_attestation.custody_record_observed_at", custody_observed_text),
            ],
            boundary="scorer-local initialization",
        )
    except CausalArtifactError as exc:
        raise ScoreSheetPreparationError(str(exc)) from exc

    sheet = copy.deepcopy(template)
    sheet.update(
        {
            "id": "priority-zero-preanswer-clamped-external-replay-score-sheet",
            "scoring_contract_version": CURRENT_SCORING_CONTRACT,
            "response_preparation_contract_version": CURRENT_RESPONSE_PREPARATION_CONTRACT,
            "response_file_sha256": sha256_bytes(response_raw),
            "custody_evidence_record_sha256": sha256_bytes(evidence_raw),
            "scorer_intake_surface": args.scorer_intake,
            "scorer_intake_sha256": sha256_bytes(scorer_raw),
        }
    )
    score_att = dict(sheet.get("scorer_attestation") or {})
    score_att.update(
        {
            "scorer_id": scorer_id,
            "scorer_kit_opened_at": local_texts[0],
            "scorer_kit_opened_at_source": SCORER_OPEN_CLOCK_SOURCE,
            "custody_record_observed_at": local_texts[1],
            "custody_record_observed_at_source": CUSTODY_OBSERVED_CLOCK_SOURCE,
        }
    )
    sheet["scorer_attestation"] = score_att
    return sheet, response, scorer, response_summary, local_texts[1]


def _validate_manual_rows(sheet: dict, scorer: dict) -> None:
    metrics = scorer.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ScoreSheetPreparationError("scorer intake has no metrics")
    metric_max: dict[str, float] = {}
    for metric in metrics:
        if not isinstance(metric, dict):
            raise ScoreSheetPreparationError("scorer metric row must be an object")
        metric_id = non_placeholder_text(metric.get("id"), "metric.id")
        maximum = metric.get("max")
        if isinstance(maximum, bool) or not isinstance(maximum, (int, float)):
            raise ScoreSheetPreparationError(f"metric {metric_id} has invalid maximum")
        metric_max[metric_id] = float(maximum)
    answer_key = scorer.get("answer_key")
    expected_labels = sorted(answer_key) if isinstance(answer_key, dict) else []
    rows = sheet.get("manual_metric_scores")
    if not isinstance(rows, list) or not rows:
        raise ScoreSheetPreparationError("manual_metric_scores must be a non-empty list")
    labels: list[str] = []
    expected_row_fields = {"label", "metric_scores", "notes", "metric_rationales"}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ScoreSheetPreparationError(f"manual_metric_scores[{index}] must be an object")
        if set(row) != expected_row_fields:
            raise ScoreSheetPreparationError(
                f"manual_metric_scores[{index}] contains undeclared or missing fields"
            )
        label = non_placeholder_text(row.get("label"), f"manual_metric_scores[{index}].label")
        labels.append(label)
        scores = row.get("metric_scores")
        rationales = row.get("metric_rationales")
        if not isinstance(scores, dict) or set(scores) != set(metric_max):
            raise ScoreSheetPreparationError(f"{label} metric_scores must cover every metric exactly")
        if not isinstance(rationales, dict) or set(rationales) != set(metric_max):
            raise ScoreSheetPreparationError(f"{label} metric_rationales must cover every metric exactly")
        for metric_id, value in scores.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ScoreSheetPreparationError(f"{label}.{metric_id} must be a finite numeric score")
            if value < 0 or value > metric_max[metric_id]:
                raise ScoreSheetPreparationError(f"{label}.{metric_id} score is out of range")
            non_placeholder_text(rationales.get(metric_id), f"{label}.{metric_id} rationale")
        non_placeholder_text(row.get("notes"), f"{label}.notes")
    if labels != expected_labels or len(labels) != len(set(labels)):
        raise ScoreSheetPreparationError(f"manual score labels/order drifted: {labels} != {expected_labels}")


def command_init(args: argparse.Namespace) -> None:
    scorer_opened_text, _ = now_timestamp()
    sheet, _, _, _, custody_observed_text = _base_bound_sheet(
        args, scorer_opened_text=scorer_opened_text
    )
    sheet["score_sheet_state"] = "post-response-manual-score-draft"
    att = sheet["scorer_attestation"]
    att["scored_at"] = ""
    att["scored_at_source"] = ""
    for key in [
        "response_was_tool_finalized_before_scoring",
        "custody_record_hash_bound_before_score_draft_published",
        "custody_record_observed_before_scoring",
        "scorer_used_only_frozen_response_custody_and_current_scorer_kit",
        "no_response_mutation_after_freeze",
    ]:
        att[key] = None
    out = resolve_input(args.out)
    write_new_json(out, sheet)
    print(
        json.dumps(
            {
                "score_sheet_draft": str(out),
                "response_file_sha256": sheet["response_file_sha256"],
                "custody_evidence_record_sha256": sheet["custody_evidence_record_sha256"],
                "scorer_intake_sha256": sheet["scorer_intake_sha256"],
                "scorer_kit_opened_at": scorer_opened_text,
                "custody_record_observed_at": custody_observed_text,
                "next": "fill every metric score, rationale, and packet note; then run finalize",
            },
            indent=2,
        )
    )


def command_finalize(args: argparse.Namespace) -> None:
    draft, _ = strict_json(resolve_input(args.draft), "score sheet draft")
    draft_att = draft.get("scorer_attestation")
    if not isinstance(draft_att, dict):
        raise ScoreSheetPreparationError("draft missing scorer_attestation")
    scorer_opened_text = non_placeholder_text(
        draft_att.get("scorer_kit_opened_at"), "scorer_attestation.scorer_kit_opened_at"
    )
    custody_observed_text = non_placeholder_text(
        draft_att.get("custody_record_observed_at"),
        "scorer_attestation.custody_record_observed_at",
    )
    base, response, scorer, response_summary, _ = _base_bound_sheet(
        args,
        scorer_opened_text=scorer_opened_text,
        custody_observed_text=custody_observed_text,
    )
    if set(draft) != set(base):
        raise ScoreSheetPreparationError(
            f"draft top-level fields drifted: observed={sorted(draft)} expected={sorted(base)}"
        )
    if draft.get("score_sheet_state") != "post-response-manual-score-draft":
        raise ScoreSheetPreparationError("draft score_sheet_state must be post-response-manual-score-draft")
    for key, expected in base.items():
        if key not in {"score_sheet_state", "manual_metric_scores", "scorer_attestation"} and draft.get(key) != expected:
            raise ScoreSheetPreparationError(f"draft protected template field drifted: {key}")
    if set(draft_att) != set(base["scorer_attestation"]):
        raise ScoreSheetPreparationError("draft scorer_attestation fields drifted")
    if draft_att != base["scorer_attestation"]:
        raise ScoreSheetPreparationError("draft scorer_attestation values drifted; fill score rows only")
    for protected in [
        "project",
        "record_type",
        "scoring_contract_version",
        "response_preparation_contract_version",
        "response_file_sha256",
        "custody_evidence_record_sha256",
        "scorer_intake_surface",
        "scorer_intake_sha256",
    ]:
        if draft.get(protected) != base.get(protected):
            raise ScoreSheetPreparationError(f"draft binding field drifted: {protected}")
    for protected in [
        "scorer_id",
        "scorer_kit_opened_at",
        "scorer_kit_opened_at_source",
        "custody_record_observed_at",
        "custody_record_observed_at_source",
    ]:
        if draft_att.get(protected) != base["scorer_attestation"].get(protected):
            raise ScoreSheetPreparationError(f"draft scorer binding field drifted: {protected}")
    _validate_manual_rows(draft, scorer)
    notes = non_placeholder_text(args.scorer_notes, "scorer_notes")
    if not args.attest_separated_scoring:
        raise ScoreSheetPreparationError(
            "--attest-separated-scoring is required; final attestations are never inferred"
        )
    scored_text, _ = now_timestamp()
    try:
        validate_local_order(
            [
                ("scorer_attestation.scorer_kit_opened_at", draft_att.get("scorer_kit_opened_at")),
                ("scorer_attestation.custody_record_observed_at", draft_att.get("custody_record_observed_at")),
                ("scorer_attestation.scored_at", scored_text),
            ],
            boundary="scorer-local scoring timeline",
        )
    except CausalArtifactError as exc:
        raise ScoreSheetPreparationError(str(exc)) from exc
    opened_text = scorer_opened_text

    final = copy.deepcopy(draft)
    final["id"] = "priority-zero-preanswer-clamped-external-replay-score-sheet"
    final["score_sheet_state"] = "post-response-manual-score-record"
    final_att = dict(draft_att)
    final_att.update(
        {
            "scored_at": scored_text,
            "scored_at_source": SCORED_CLOCK_SOURCE,
            "response_was_tool_finalized_before_scoring": True,
            "custody_record_hash_bound_before_score_draft_published": True,
            "custody_record_observed_before_scoring": True,
            "scorer_used_only_frozen_response_custody_and_current_scorer_kit": True,
            "no_response_mutation_after_freeze": True,
            "notes": notes,
        }
    )
    final["scorer_attestation"] = final_att
    out = resolve_input(args.out)
    write_new_json(out, final, readonly=True)
    print(
        json.dumps(
            {
                "score_sheet": str(out),
                "score_sheet_sha256": sha256_file(out),
                "scorer_id": final_att["scorer_id"],
                "responder_id": response_summary["responder_id"],
                "scorer_kit_opened_at": opened_text,
                "custody_record_observed_at": custody_observed_text,
                "scored_at": scored_text,
                "scoring_contract_version": CURRENT_SCORING_CONTRACT,
            },
            indent=2,
        )
    )


def common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("response_file")
    parser.add_argument("evidence_record")
    parser.add_argument("--scorer-id", required=True)
    parser.add_argument("--scorer-intake", default=DEFAULT_SCORER)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--response-template", default=DEFAULT_RESPONSE_TEMPLATE)
    parser.add_argument("--out", required=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a byte-bound blank score-sheet draft")
    common_arguments(init_parser)
    init_parser.set_defaults(func=command_init)

    finalize_parser = subparsers.add_parser("finalize", help="validate and freeze a filled score-sheet draft")
    common_arguments(finalize_parser)
    finalize_parser.add_argument("--draft", required=True)
    finalize_parser.add_argument("--scorer-notes", required=True)
    finalize_parser.add_argument("--attest-separated-scoring", action="store_true")
    finalize_parser.set_defaults(func=command_finalize)

    args = parser.parse_args()
    try:
        args.func(args)
    except (
        ExternalRunArtifactError,
        ResponseContractError,
        CurrentCustodyContractError,
        ScoreSheetPreparationError,
    ) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()

"""Validate and summarize a completed Priority-0 external replay response.

Usage:
  python tools/score_priority_zero_external_replay_response.py completed-response.json
  python tools/score_priority_zero_external_replay_response.py --scorer-intake assays/...json completed-response.json
  python tools/score_priority_zero_external_replay_response.py --evidence-record assays/...json completed-response.json
  python tools/score_priority_zero_external_replay_response.py --score-sheet assays/...json --evidence-record assays/...json completed-response.json
  python tools/score_priority_zero_external_replay_response.py --allow-contaminated-dryrun completed-response.json

The strict default resolves the live scorer intake from FRONTIER-BACKLOG instead
of a frozen historical fixture.  Current scorer intakes may require a separate
custody evidence record; in that mode a self-attested response is not clean
external evidence merely because its own booleans say so.  Current score-
separated intakes also require manual metric scores to live in a separate
post-response score sheet, never inside the frozen response file, and that
score sheet must name custody_evidence_record_sha256 for the completed custody
record, open only after that custody record is frozen, and obey pre-answer
material clamps.  Contaminated
dry-run mode exists only to exercise the intake/scoring path inside a non-
independent session; it never converts the response into external evidence.

Current strict scoring also byte-binds the custody record and score sheet to
the exact files supplied on the command line, emits their actual hashes,
requires a scorer distinct from the responder, requires evidence-grounded
rationales for every metric score, and records positive per-packet operator
cost whose sum matches the run total.  The custodian may also be the scorer, so
the current lane still needs only two distinct operators.  Because the four
synthetic packets are co-visible and the nominal full control is a trace
excerpt rather than a measured full-archive trial, current decisions are
bounded semantic support or narrowing evidence—not global compact-default
confirmation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
from datetime import datetime
from typing import Any

from priority_zero_assay_lib import load_json, file_sha256
from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    strict_json_bytes,
)
from priority_zero_external_replay_decision_lib import decide_compact_gate
from priority_zero_causal_artifact_lib import (
    CausalArtifactError,
    validate_local_order,
)
from priority_zero_custody_timeline_lib import (
    CURRENT_CUSTODY_CONTRACT,
    CustodyTimelineError,
    validate_custody_timeline,
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
DEFAULT_SCORER_INTAKE = "auto:frontier"
REQUIRED_ANSWER_FIELDS = [
    "mission_heart",
    "oq_routing",
    "compact_gate_posture",
    "waste_or_refactor_implicated",
    "next_safe_action",
    "abstentions",
    "uncertainty_or_conflicts",
]
_PLACEHOLDER_VALUES = {"", "n/a", "na", "tbd", "todo", "placeholder", "none", "null"}


class ResponseIntakeError(ValueError):
    pass


def _fail(msg: str) -> None:
    raise ResponseIntakeError(msg)


def _non_empty_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be a non-empty string")
    if value.strip().lower() in _PLACEHOLDER_VALUES:
        _fail(f"{label} must not be a placeholder")
    return value.strip()


def _load_json_rel(root: pathlib.Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        _fail(f"default scorer candidate missing: {rel}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"default scorer candidate is not JSON: {rel}: {exc}")


def _candidate_is_scorer_intake(root: pathlib.Path, rel: Any) -> bool:
    if not isinstance(rel, str):
        return False
    if not rel.startswith("assays/priority-zero-") or not rel.endswith(".json"):
        return False
    if "scorer-intake" not in pathlib.PurePosixPath(rel).name:
        return False
    path = root / rel
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return all(key in data for key in ["answer_key", "metrics", "responder_only_surface"])


def resolve_default_scorer_intake(root: pathlib.Path = ROOT) -> str:
    """Return the live external replay scorer intake named by FRONTIER-BACKLOG."""
    frontier_path = root / "FRONTIER-BACKLOG.json"
    if not frontier_path.exists():
        _fail("cannot resolve default scorer intake without FRONTIER-BACKLOG.json")
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    items = frontier.get("items")
    if not isinstance(items, list) or not items:
        _fail("FRONTIER-BACKLOG has no items for default scorer resolution")
    top = items[0]
    candidates = [rel for rel in top.get("fanout", []) if _candidate_is_scorer_intake(root, rel)]
    if len(candidates) != 1:
        _fail(f"expected exactly one scorer-intake in live frontier fanout, found {candidates}")
    return candidates[0]


def resolve_scorer_intake(selector: str | None = None, *, root: pathlib.Path = ROOT) -> str:
    """Resolve an explicit scorer intake or the live auto:frontier default."""
    selector = selector or DEFAULT_SCORER_INTAKE
    if selector == DEFAULT_SCORER_INTAKE:
        return resolve_default_scorer_intake(root)
    return selector


def load_scorer_intake(selector: str | None = None, *, root: pathlib.Path = ROOT) -> tuple[dict[str, Any], str]:
    selector = selector or DEFAULT_SCORER_INTAKE
    rel = resolve_scorer_intake(selector, root=root)
    if selector == DEFAULT_SCORER_INTAKE:
        return _load_json_rel(root, rel), rel
    return load_json(rel, root=root), rel


def _path_sha256(path: str | pathlib.Path, *, root: pathlib.Path = ROOT) -> str:
    p = _resolve_path(path, root=root)
    if not p.exists():
        _fail(f"missing file for sha256: {path}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _resolve_path(path: str | pathlib.Path, *, root: pathlib.Path = ROOT) -> pathlib.Path:
    p = pathlib.Path(path)
    return p if p.is_absolute() else root / p


def _read_json_file(
    path: str | pathlib.Path,
    *,
    label: str,
    root: pathlib.Path = ROOT,
) -> tuple[dict[str, Any], str, pathlib.Path]:
    resolved = _resolve_path(path, root=root)
    if not resolved.exists():
        _fail(f"missing {label} file: {path}")
    raw = resolved.read_bytes()

    try:
        data = strict_json_bytes(raw, f"{label} file")
    except ExternalRunArtifactError as exc:
        _fail(str(exc))
    return data, hashlib.sha256(raw).hexdigest(), resolved


def _canonical_json_identity(value: dict[str, Any]) -> str:
    """Preserve JSON types while ignoring harmless key order/whitespace."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _bind_json_object_to_file(
    provided: dict[str, Any] | None,
    file_path: str | pathlib.Path | None,
    *,
    label: str,
    require_file: bool,
    root: pathlib.Path = ROOT,
) -> tuple[dict[str, Any] | None, str | None, pathlib.Path | None]:
    """Return one object/byte identity or fail on split-brain inputs.

    Library callers previously could validate custody from one in-memory object
    while binding the score sheet to a different file.  Current strict scoring
    requires the object and the named file to be the same artifact.
    """
    if file_path is None:
        if require_file:
            _fail(f"{label} must be supplied as a bound file for strict scoring")
        return provided, None, None
    loaded, digest, resolved = _read_json_file(file_path, label=label, root=root)
    if provided is not None:
        try:
            same_identity = _canonical_json_identity(provided) == _canonical_json_identity(loaded)
        except (TypeError, ValueError) as exc:
            _fail(f"{label} object cannot be represented as strict JSON: {exc}")
        if not same_identity:
            _fail(f"{label} object does not match bound file contents")
    return loaded, digest, resolved


def _parse_iso_timestamp(value: Any, *, label: str) -> datetime:
    s = _non_empty_string(value, label=label)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        _fail(f"{label} must be ISO-8601 with timezone offset")
    if dt.tzinfo is None or dt.utcoffset() is None:
        _fail(f"{label} must include timezone offset")
    return dt


def _material_entries(value: Any) -> list[str]:
    if isinstance(value, str):
        entries = [value.strip()] if value.strip() else []
    elif isinstance(value, list):
        entries = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                _fail("custodian_attestation.pre_response_materials_given entries must be non-empty strings")
            entries.append(item.strip())
    else:
        _fail("custodian_attestation.pre_response_materials_given must be a string or list of strings")
    if not entries:
        _fail("custodian_attestation.pre_response_materials_given must not be empty")
    return entries


def _validate_pre_response_materials(materials: Any, scorer: dict[str, Any]) -> list[str]:
    entries = _material_entries(materials)
    allowed = scorer.get("allowed_pre_response_materials")
    if scorer.get("requires_pre_response_material_exact_match") is True:
        if not isinstance(allowed, list) or not all(isinstance(row, str) and row for row in allowed):
            _fail("scorer exact pre-response clamp requires allowed_pre_response_materials")
        if sorted(entries) != sorted(allowed):
            _fail("custody evidence pre-response material must exactly match allowed responder-only bundle list")
    elif scorer.get("responder_bundle_surface") not in "\n".join(entries):
        _fail("custody evidence must name the responder bundle as the pre-response material")
    default_forbidden = [
        "scorer-intake",
        "answer_key",
        "full archive",
        "REVISION-RECEIPT",
        "RESOLUTION-LEDGER",
        "score-sheet",
        "score sheet",
        "scorer kit",
        "scorer-kit",
        "custody kit",
        "custody-kit",
        "custody evidence",
        "evidence-record",
        "handoff manifest",
        "expected bundle digest",
        "expected digest",
        "submission-kit",
        "submission kit",
    ]
    configured = scorer.get("forbidden_pre_response_material_tokens")
    if configured is not None:
        if not isinstance(configured, list) or not all(isinstance(row, str) and row for row in configured):
            _fail("forbidden_pre_response_material_tokens must be a list of non-empty strings")
        forbidden = list(dict.fromkeys(default_forbidden + configured))
    else:
        forbidden = default_forbidden
    lowered = "\n".join(entries).lower()
    for token in forbidden:
        if token.lower() in lowered:
            _fail(f"custody evidence pre-response material leaks forbidden token: {token}")
    return entries


def _manual_rows_from_response(response: dict[str, Any]) -> list[Any]:
    stage = response.get("scorer_stage")
    if not isinstance(stage, dict):
        return []
    manual = stage.get("manual_metric_scores", [])
    if manual in (None, []):
        return []
    if not isinstance(manual, list):
        _fail("scorer_stage.manual_metric_scores must be a list when present")
    return manual


def _score_manual_rows(manual: list[Any], scorer: dict[str, Any], expected_labels: list[str]) -> dict[str, Any]:
    if not manual:
        return {
            "manual_score_total": None,
            "manual_score_max": None,
            "manual_scores_by_label": {},
            "manual_score_status": "not-provided",
        }
    metric_ids = {m["id"]: m["max"] for m in scorer.get("metrics", [])}
    if not metric_ids:
        _fail("scorer intake must define at least one metric")
    if any(not isinstance(row, dict) for row in manual):
        _fail("each manual score row must be an object")
    labels = [row.get("label") for row in manual]
    if any(not isinstance(label, str) or not label for label in labels):
        _fail("each manual score row must have a non-empty string label")
    if sorted(labels) != expected_labels or len(labels) != len(set(labels)):
        _fail(f"manual score labels drifted: {sorted(labels)} != {expected_labels}")
    require_rationales = scorer.get("requires_metric_rationales") is True
    require_notes = scorer.get("requires_packet_score_notes") is True
    total = 0
    max_total = 0
    by_label: dict[str, dict[str, Any]] = {}
    for row in manual:
        label = row.get("label")
        scores = row.get("metric_scores", {})
        if not isinstance(scores, dict):
            _fail(f"manual score for {label} must provide metric_scores as an object")
        if set(scores) != set(metric_ids):
            _fail(f"manual score for {label} must cover all metrics")
        for metric_id, value in scores.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                _fail(f"manual score for {label}.{metric_id} must be numeric, not boolean or another type")
            if not math.isfinite(float(value)):
                _fail(f"manual score for {label}.{metric_id} must be finite")
            if value < 0 or value > metric_ids[metric_id]:
                _fail(f"manual score out of range for {label}.{metric_id}")
        rationales = row.get("metric_rationales")
        if require_rationales:
            if not isinstance(rationales, dict) or set(rationales) != set(metric_ids):
                _fail(f"manual score for {label} must provide metric_rationales for every metric")
            for metric_id, rationale in rationales.items():
                _non_empty_string(rationale, label=f"manual score rationale {label}.{metric_id}")
        notes = row.get("notes")
        if require_notes:
            _non_empty_string(notes, label=f"manual score notes {label}")
        label_total = sum(scores.values())
        label_max = sum(metric_ids.values())
        total += label_total
        max_total += label_max
        scored_row: dict[str, Any] = {
            "score": label_total,
            "max": label_max,
            "metric_scores": scores,
        }
        if require_rationales:
            scored_row["metric_rationales"] = rationales
        if require_notes:
            scored_row["notes"] = notes
        by_label[str(label)] = scored_row
    return {
        "manual_score_total": total,
        "manual_score_max": max_total,
        "manual_scores_by_label": by_label,
        "manual_score_status": "complete",
    }


def _dryrun_authorized(response: dict[str, Any]) -> bool:
    mode = response.get("dryrun_mode", {})
    if not isinstance(mode, dict):
        return False
    return (
        mode.get("contaminated_same_session") is True
        and mode.get("external_response_evidence") is False
        and isinstance(mode.get("contamination_notes"), str)
        and "not independent" in mode.get("contamination_notes", "")
    )


def _validate_custody_evidence_record(
    evidence_record: dict[str, Any] | None,
    scorer: dict[str, Any],
    *,
    response: dict[str, Any],
    response_summary: dict[str, Any],
    response_file: str | pathlib.Path | None,
    response_file_sha256: str | None,
    root: pathlib.Path = ROOT,
) -> dict[str, Any]:
    """Validate one custody artifact under the live or historical contract.

    The live causal contract has one implementation in
    ``priority_zero_external_replay_custody_lib``.  Everything after that
    branch is intentionally historical-only; keeping the paths disjoint avoids
    a second, silently diverging interpretation of current custody evidence.
    """
    if evidence_record is None:
        _fail("strict external scoring requires a separate custody evidence record")
    if response_file_sha256 is None:
        if response_file is None:
            _fail("custody evidence validation requires the response file identity")
        response_file_sha256 = _path_sha256(response_file, root=root)

    expected_contract = scorer.get("custody_contract_version")
    if expected_contract == CURRENT_CUSTODY_CONTRACT:
        template_rel = scorer.get("evidence_record_template_surface")
        if not isinstance(template_rel, str) or not template_rel:
            _fail("current scorer intake must name evidence_record_template_surface")
        if scorer.get("evidence_record_template_sha256") != file_sha256(template_rel, root=root):
            _fail("current scorer intake custody-template hash drifted")
        custody_template = load_json(template_rel, root=root)
        for scorer_key, template_key, label in [
            ("responder_bundle_sha256", "responder_bundle_sha256", "responder bundle"),
            ("responder_only_sha256", "responder_only_sha256", "responder packet"),
            ("response_template_sha256", "response_template_sha256", "response template"),
        ]:
            if scorer.get(scorer_key) != custody_template.get(template_key):
                _fail(f"scorer and custody template disagree on {label} identity")
        try:
            return validate_current_custody_record(
                evidence_record,
                custody_template,
                response=response,
                response_summary=response_summary,
                response_file_sha256=response_file_sha256,
            )
        except CurrentCustodyContractError as exc:
            _fail(str(exc))

    # Historical compatibility only. Current causal evidence has already
    # returned through the shared validator above, so no live-contract branch
    # is duplicated below.
    if evidence_record.get("project") != "DelayBasin":
        _fail("custody evidence record project must be DelayBasin")
    if evidence_record.get("record_type") != "custody-evidence-record":
        _fail("custody evidence record_type must be custody-evidence-record")
    if expected_contract is not None and evidence_record.get("custody_contract_version") != expected_contract:
        _fail(f"custody evidence contract mismatch: expected {expected_contract}")
    expected_response_contract = scorer.get("response_preparation_contract_version")
    if expected_response_contract is not None and evidence_record.get("response_preparation_contract_version") != expected_response_contract:
        _fail(f"custody evidence response preparation contract mismatch: expected {expected_response_contract}")
    expected_state = scorer.get("required_custody_evidence_state") or "completed-response-frozen-before-scoring"
    if evidence_record.get("evidence_state") != expected_state:
        _fail(f"custody evidence state must be {expected_state}")
    if evidence_record.get("response_file_sha256") != response_file_sha256:
        _fail("custody evidence response_file_sha256 does not match the response bytes validated by this run")
    if evidence_record.get("responder_bundle_sha256") != scorer.get("responder_bundle_sha256"):
        _fail("custody evidence responder bundle hash drifted")
    if evidence_record.get("responder_only_sha256") != file_sha256(scorer.get("responder_only_surface"), root=root):
        _fail("custody evidence responder packet hash drifted")
    if scorer.get("response_template_surface") and evidence_record.get("response_template_sha256") != file_sha256(scorer.get("response_template_surface"), root=root):
        _fail("custody evidence response template hash drifted")
    if evidence_record.get("scorer_intake_surface") != scorer.get("surface"):
        _fail("custody evidence scorer intake surface mismatch")
    if evidence_record.get("scorer_intake_sha256") != file_sha256(scorer.get("surface"), root=root):
        _fail("custody evidence scorer intake hash drifted")

    att = evidence_record.get("custodian_attestation")
    if not isinstance(att, dict):
        _fail("custody evidence record missing custodian_attestation object")
    for key in [
        "custodian_id",
        "responder_id",
        "response_frozen_at",
        "pre_response_exposure_notes",
        "scorer_opened_at",
    ]:
        _non_empty_string(att.get(key), label=f"custodian_attestation.{key}")
    required_custody_attestations = scorer.get("required_custody_attestations")
    if required_custody_attestations is None:
        required_custody_attestations = [
            "responder_was_given_only_responder_bundle_before_response",
            "scorer_intake_opened_only_after_response_frozen",
            "full_archive_not_given_before_response",
            "conversation_not_shown_before_response",
            "answer_key_not_shown_before_response",
            "response_hash_recorded_before_scoring",
        ]
    if not isinstance(required_custody_attestations, list) or not all(
        isinstance(key, str) and key for key in required_custody_attestations
    ):
        _fail("required_custody_attestations must be a list of non-empty strings")
    for key in required_custody_attestations:
        if att.get(key) is not True:
            _fail(f"custodian_attestation.{key} must be true for clean external evidence")
    pre_response_entries = _validate_pre_response_materials(
        att.get("pre_response_materials_given"), scorer
    )
    return {
        "custody_evidence_record_id": evidence_record.get("id"),
        "custody_evidence_state": evidence_record.get("evidence_state"),
        "custody_contract_version": evidence_record.get("custody_contract_version") or "legacy",
        "response_file_sha256": evidence_record.get("response_file_sha256"),
        "custodian_id": att.get("custodian_id"),
        "pre_response_materials_given": pre_response_entries,
        "response_frozen_at": att.get("response_frozen_at"),
        "scorer_opened_at": att.get("scorer_opened_at"),
    }

def _validate_score_sheet(
    score_sheet: dict[str, Any] | None,
    scorer: dict[str, Any],
    expected_labels: list[str],
    *,
    response: dict[str, Any],
    response_file: str | pathlib.Path | None,
    response_file_sha256: str | None,
    evidence_record: dict[str, Any] | None,
    evidence_record_sha256: str | None,
    score_sheet_sha256: str | None,
    root: pathlib.Path = ROOT,
) -> dict[str, Any]:
    if score_sheet is None:
        return {
            "manual_score_total": None,
            "manual_score_max": None,
            "manual_scores_by_label": {},
            "manual_score_status": "separate-score-sheet-required",
            "manual_score_source": "absent",
        }
    if response_file_sha256 is None:
        if response_file is None:
            _fail("score sheet validation requires the response file identity")
        response_file_sha256 = _path_sha256(response_file, root=root)
    if score_sheet.get("project") != "DelayBasin":
        _fail("score sheet project must be DelayBasin")
    if score_sheet.get("record_type") != "external-replay-score-sheet":
        _fail("score sheet record_type must be external-replay-score-sheet")
    expected_scoring_contract = scorer.get("scoring_contract_version")
    current_causal_stage = expected_scoring_contract == CURRENT_CUSTODY_CONTRACT
    if expected_scoring_contract is not None and score_sheet.get("scoring_contract_version") != expected_scoring_contract:
        _fail(f"score sheet contract mismatch: expected {expected_scoring_contract}")
    expected_response_contract = scorer.get("response_preparation_contract_version")
    if expected_response_contract is not None and score_sheet.get("response_preparation_contract_version") != expected_response_contract:
        _fail(f"score sheet response preparation contract mismatch: expected {expected_response_contract}")
    score_template: dict[str, Any] | None = None
    if current_causal_stage:
        template_rel = scorer.get("score_sheet_template_surface")
        if not isinstance(template_rel, str) or not template_rel:
            _fail("current scorer intake must name score_sheet_template_surface")
        score_template = load_json(template_rel, root=root)
        if set(score_sheet) != set(score_template):
            _fail(
                "current score sheet top-level fields drifted from template: "
                f"observed={sorted(score_sheet)} expected={sorted(score_template)}"
            )
        dynamic_top = {
            "id", "score_sheet_state", "response_file_sha256",
            "custody_evidence_record_sha256", "scorer_intake_surface",
            "scorer_intake_sha256", "manual_metric_scores", "scorer_attestation",
        }
        for key, expected in score_template.items():
            if key not in dynamic_top and score_sheet.get(key) != expected:
                _fail(f"current score sheet protected template field drifted: {key}")
    if score_sheet.get("score_sheet_state") != "post-response-manual-score-record":
        _fail("score sheet must be a post-response manual score record")
    if score_sheet.get("response_file_sha256") != response_file_sha256:
        _fail("score sheet response_file_sha256 does not match the response bytes validated by this run")
    if score_sheet.get("scorer_intake_surface") != scorer.get("surface"):
        _fail("score sheet scorer intake surface mismatch")
    if score_sheet.get("scorer_intake_sha256") != file_sha256(scorer.get("surface"), root=root):
        _fail("score sheet scorer intake hash drifted")
    expected_evidence_hash = score_sheet.get("custody_evidence_record_sha256")
    if not isinstance(expected_evidence_hash, str) or not expected_evidence_hash.strip():
        _fail("score sheet must name custody_evidence_record_sha256 for the completed custody record")
    if evidence_record_sha256 is None:
        _fail("score sheet names custody_evidence_record_sha256 but no bound evidence record file was provided")
    if expected_evidence_hash != evidence_record_sha256:
        _fail("score sheet custody_evidence_record_sha256 does not match evidence record file")
    if not isinstance(evidence_record, dict):
        _fail("score sheet validation requires the same bound custody evidence record used for custody admission")
    att = score_sheet.get("scorer_attestation")
    if not isinstance(att, dict):
        _fail("score sheet missing scorer_attestation object")
    if current_causal_stage:
        template_att = score_template.get("scorer_attestation") if isinstance(score_template, dict) else None
        if not isinstance(template_att, dict) or set(att) != set(template_att):
            _fail("current score sheet scorer_attestation fields drifted from template")
    for key in ["scorer_id", "scored_at"]:
        _non_empty_string(att.get(key), label=f"scorer_attestation.{key}")
    if current_causal_stage:
        expected_sources = {
            "scorer_kit_opened_at_source": "local-process-clock-at-score-sheet-init",
            "custody_record_observed_at_source": "local-process-clock-after-custody-validation",
            "scored_at_source": "local-process-clock-at-score-sheet-finalize",
        }
        for key, expected in expected_sources.items():
            if att.get(key) != expected:
                _fail(f"scorer_attestation.{key} must be {expected}")
    scorer_kit_opened_at_text: str | None = None
    custody_record_observed_at_text: str | None = None
    if scorer.get("requires_score_sheet_chronology") is True:
        custody_att = evidence_record.get("custodian_attestation")
        if not isinstance(custody_att, dict):
            _fail("score sheet chronology requires custodian_attestation in evidence record")
        if current_causal_stage:
            scorer_kit_opened_at_text = _non_empty_string(
                att.get("scorer_kit_opened_at"),
                label="scorer_attestation.scorer_kit_opened_at",
            )
            custody_record_observed_at_text = _non_empty_string(
                att.get("custody_record_observed_at"),
                label="scorer_attestation.custody_record_observed_at",
            )
            try:
                validate_local_order(
                    [
                        ("scorer_attestation.scorer_kit_opened_at", scorer_kit_opened_at_text),
                        ("scorer_attestation.custody_record_observed_at", custody_record_observed_at_text),
                        ("scorer_attestation.scored_at", att.get("scored_at")),
                    ],
                    boundary="scorer-local scoring timeline",
                )
            except CausalArtifactError as exc:
                _fail(str(exc))
        else:
            scored_at = _parse_iso_timestamp(att.get("scored_at"), label="scorer_attestation.scored_at")
            response_frozen_at = _parse_iso_timestamp(custody_att.get("response_frozen_at"), label="custodian_attestation.response_frozen_at")
            if scored_at < response_frozen_at:
                _fail("score sheet chronology impossible: scored_at precedes response_frozen_at")
            scorer_opened_at = _parse_iso_timestamp(
                custody_att.get("scorer_opened_at"),
                label="custodian_attestation.scorer_opened_at",
            )
            if scored_at < scorer_opened_at:
                _fail("score sheet chronology impossible: scored_at precedes scorer_opened_at")
    required_score_attestations = scorer.get("required_score_sheet_attestations") or [
        "response_was_frozen_before_scoring",
        "scorer_intake_opened_after_response_frozen",
        "scorer_used_only_frozen_response_and_custody_record",
        "no_response_mutation_after_freeze",
    ]
    if not isinstance(required_score_attestations, list) or not all(isinstance(key, str) and key for key in required_score_attestations):
        _fail("required_score_sheet_attestations must be a list of non-empty strings")
    for key in required_score_attestations:
        if att.get(key) is not True:
            _fail(f"scorer_attestation.{key} must be true for clean separated scoring")
    response_stage = response.get("responder_stage")
    custody_att = evidence_record.get("custodian_attestation")
    if not isinstance(response_stage, dict) or not isinstance(custody_att, dict):
        _fail("scorer identity separation requires responder_stage and custodian_attestation")
    responder_id = _non_empty_string(response_stage.get("responder_id"), label="responder_stage.responder_id")
    custodian_id = _non_empty_string(custody_att.get("custodian_id"), label="custodian_attestation.custodian_id")
    scorer_id = _non_empty_string(att.get("scorer_id"), label="scorer_attestation.scorer_id")
    if scorer.get("requires_distinct_scorer_from_responder") is True and scorer_id == responder_id:
        _fail("scorer_id must differ from response responder_id; responder self-scoring is not admissible")
    manual = score_sheet.get("manual_metric_scores", [])
    if not isinstance(manual, list) or not manual:
        _fail("score sheet manual_metric_scores must be a non-empty list")
    if current_causal_stage:
        expected_row_fields = {"label", "metric_scores", "notes", "metric_rationales"}
        observed_order: list[str] = []
        for index, row in enumerate(manual):
            if not isinstance(row, dict) or set(row) != expected_row_fields:
                _fail(f"current score sheet manual_metric_scores[{index}] fields drifted from template")
            observed_order.append(str(row.get("label")))
        if observed_order != expected_labels:
            _fail(f"current score sheet packet row order drifted: {observed_order} != {expected_labels}")
    summary = _score_manual_rows(manual, scorer, expected_labels)
    summary["manual_score_source"] = "separate-score-sheet"
    summary["score_sheet_id"] = score_sheet.get("id")
    summary["score_sheet_sha256"] = score_sheet_sha256
    summary["scorer_id"] = scorer_id
    summary["distinct_scorer_from_responder"] = scorer_id != responder_id
    summary["scorer_is_custodian"] = scorer_id == custodian_id
    summary["scored_at"] = att.get("scored_at")
    if scorer.get("requires_score_sheet_chronology") is True:
        summary["score_sheet_chronology_state"] = "valid"
        if scorer_kit_opened_at_text is not None:
            summary["scorer_kit_opened_at"] = scorer_kit_opened_at_text
        if custody_record_observed_at_text is not None:
            summary["custody_record_observed_at"] = custody_record_observed_at_text
        if current_causal_stage:
            summary["cross_operator_time_ordering"] = "exact-artifact-hash-chain-not-wall-clock"
    return summary


def validate_response(
    response: dict[str, Any],
    scorer: dict[str, Any],
    *,
    allow_contaminated_dryrun: bool = False,
    evidence_record: dict[str, Any] | None = None,
    response_file: str | pathlib.Path | None = None,
    response_file_sha256: str | None = None,
    score_sheet: dict[str, Any] | None = None,
    evidence_record_sha256: str | None = None,
    score_sheet_sha256: str | None = None,
    root: pathlib.Path = ROOT,
) -> dict[str, Any]:
    if response.get("project") != "DelayBasin":
        _fail("response project must be DelayBasin")
    response_contract_summary: dict[str, Any] = {}
    if scorer.get("response_preparation_contract_version") == CURRENT_RESPONSE_PREPARATION_CONTRACT:
        template_rel = scorer.get("response_template_surface")
        if not isinstance(template_rel, str) or not template_rel:
            _fail("current scorer intake must name response_template_surface")
        try:
            response_contract_summary = validate_finalized_response(
                response,
                load_json(template_rel, root=root),
                expected_bundle_sha256=_non_empty_string(
                    scorer.get("responder_bundle_sha256"),
                    label="scorer.responder_bundle_sha256",
                ),
                expected_packet_sha256=file_sha256(scorer.get("responder_only_surface"), root=root),
            )
        except ResponseContractError as exc:
            _fail(f"current finalized response contract failed: {exc}")
    stage = response.get("responder_stage")
    if not isinstance(stage, dict):
        _fail("response must contain responder_stage object")
    for key in ["responder_id", "run_started_at", "run_completed_at"]:
        _non_empty_string(stage.get(key), label=f"responder_stage.{key}")
    responder_rel = scorer.get("responder_only_surface")
    expected_hash = file_sha256(responder_rel, root=root)
    if stage.get("saw_responder_packet_sha256") != expected_hash:
        _fail("response did not record the expected responder-only packet hash")
    bundle_rel = scorer.get("responder_bundle_surface")
    if bundle_rel and stage.get("saw_responder_bundle_sha256") != scorer.get("responder_bundle_sha256"):
        _fail("response did not record the expected responder bundle hash")
    dryrun = allow_contaminated_dryrun and _dryrun_authorized(response)
    embedded_manual_scores = _manual_rows_from_response(response)
    if not dryrun and embedded_manual_scores:
        _fail("strict clean scoring requires a separate score sheet; frozen response must not carry manual_metric_scores")
    required_attestations = scorer.get("required_attestations") or [
        "no_scorer_key_before_response",
        "no_full_archive_before_response",
    ]
    diagnostic_by_attestation = {
        "no_scorer_key_before_response": "response does not attest to scorer-key separation; record exposure notes before scoring",
        "no_full_archive_before_response": "response does not attest to no-full-archive-before-response; record exposure notes before scoring",
        "no_conversation_context_before_response": "response does not attest to no-conversation-context-before-response; record exposure notes before scoring",
    }
    for attestation in required_attestations:
        if stage.get(attestation) is not True and not dryrun:
            _fail(diagnostic_by_attestation.get(attestation, f"response does not attest to required separation: {attestation}"))
    if dryrun and not isinstance(stage.get("accidental_exposure_notes"), str):
        _fail("contaminated dry-run must record accidental_exposure_notes")
    operator_cost = stage.get("operator_cost_minutes")
    if (
        isinstance(operator_cost, bool)
        or not isinstance(operator_cost, (int, float))
        or not math.isfinite(float(operator_cost))
        or operator_cost <= 0
    ):
        _fail("response must record positive operator_cost_minutes")
    answers = stage.get("packet_answers")
    if not isinstance(answers, list):
        _fail("response responder_stage.packet_answers must be a list")
    expected_labels = sorted(scorer.get("answer_key", {}))
    observed_labels = sorted(row.get("label") for row in answers if isinstance(row, dict))
    if observed_labels != expected_labels:
        _fail(f"response labels drifted: {observed_labels} != {expected_labels}")
    required_fields = scorer.get("required_answer_fields") or REQUIRED_ANSWER_FIELDS
    operator_cost_minutes_by_label: dict[str, int | float] = {}
    for row in answers:
        if not isinstance(row, dict):
            _fail("each packet answer must be an object")
        label = row.get("label", "<missing-label>")
        for field in required_fields:
            _non_empty_string(row.get(field), label=f"packet_answers[{label}].{field}")
        if scorer.get("requires_per_packet_operator_cost") is True:
            packet_cost = row.get("operator_cost_minutes")
            if (
                isinstance(packet_cost, bool)
                or not isinstance(packet_cost, (int, float))
                or not math.isfinite(float(packet_cost))
                or packet_cost <= 0
            ):
                _fail(f"packet_answers[{label}].operator_cost_minutes must be a positive finite number")
            operator_cost_minutes_by_label[str(label)] = packet_cost
    if scorer.get("requires_operator_cost_sum_match") is True:
        if len(operator_cost_minutes_by_label) != len(expected_labels):
            _fail("operator cost sum check requires one per-packet cost for every response label")
        packet_cost_total = sum(operator_cost_minutes_by_label.values())
        tolerance = scorer.get("operator_cost_sum_tolerance_minutes", 0.05)
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or tolerance < 0:
            _fail("operator_cost_sum_tolerance_minutes must be a non-negative number")
        if not math.isclose(float(packet_cost_total), float(operator_cost), rel_tol=0.0, abs_tol=float(tolerance)):
            _fail(
                "responder_stage.operator_cost_minutes must equal the sum of packet operator costs "
                f"within tolerance {tolerance}: total={operator_cost}, packets={packet_cost_total}"
            )
    custody_summary: dict[str, Any] = {}
    if not dryrun and scorer.get("requires_custody_evidence_record") is True:
        custody_summary = _validate_custody_evidence_record(
            evidence_record,
            scorer,
            response=response,
            response_summary=response_contract_summary,
            response_file=response_file,
            response_file_sha256=response_file_sha256,
            root=root,
        )
        if response_contract_summary:
            if evidence_record is None or evidence_record.get("response_finalized_at") != response_contract_summary.get("response_finalized_at"):
                _fail("custody response_finalized_at does not match response.response_artifact.finalized_at")
            custody_att = evidence_record.get("custodian_attestation")
            if not isinstance(custody_att, dict) or custody_att.get("response_frozen_at") != response_contract_summary.get("response_finalized_at"):
                _fail("custody response_frozen_at does not equal finalized response time")
        if scorer.get("requires_custody_timeline_order") is True or scorer.get("requires_responder_id_match") is True or scorer.get("requires_distinct_custodian") is True:
            try:
                timeline_summary = validate_custody_timeline(
                    response,
                    evidence_record or {},
                    require_distinct_custodian=bool(scorer.get("requires_distinct_custodian")),
                )
            except CustodyTimelineError as exc:
                _fail(str(exc))
            custody_summary.update(timeline_summary.as_dict())
    if dryrun:
        manual_summary = _score_manual_rows(embedded_manual_scores, scorer, expected_labels)
        manual_summary["manual_score_source"] = "embedded-contaminated-dryrun" if embedded_manual_scores else "absent"
    elif scorer.get("requires_separate_score_sheet") is True:
        manual_summary = _validate_score_sheet(
            score_sheet,
            scorer,
            expected_labels,
            response=response,
            response_file=response_file,
            response_file_sha256=response_file_sha256,
            evidence_record=evidence_record,
            evidence_record_sha256=evidence_record_sha256,
            score_sheet_sha256=score_sheet_sha256,
            root=root,
        )
    else:
        manual_summary = _score_manual_rows(embedded_manual_scores, scorer, expected_labels)
        manual_summary["manual_score_source"] = "embedded-historical" if embedded_manual_scores else "absent"
    summary = {
        "responder_packet_sha256": expected_hash,
        "responder_bundle_sha256": scorer.get("responder_bundle_sha256"),
        "response_file_sha256": response_file_sha256,
        "custody_evidence_record_sha256": evidence_record_sha256,
        "labels": expected_labels,
        "operator_cost_minutes": stage.get("operator_cost_minutes"),
        "operator_cost_minutes_by_label": operator_cost_minutes_by_label,
        "response_preparation_contract_version": response_contract_summary.get("response_preparation_contract_version"),
        "response_finalized_at": response_contract_summary.get("response_finalized_at"),
        "response_contract_state": "valid" if response_contract_summary else "historical-or-not-required",
        "decision_evidence_scope": scorer.get("decision_evidence_scope"),
        "full_archive_control_state": scorer.get("full_archive_control_state"),
        **manual_summary,
        **custody_summary,
        "answer_key_available_after_response": True,
        "validation_mode": "contaminated-dryrun" if dryrun else "strict-external",
        "requires_custody_evidence_record": bool(scorer.get("requires_custody_evidence_record")),
        "requires_separate_score_sheet": bool(scorer.get("requires_separate_score_sheet")),
        "external_response_evidence": False if dryrun else True,
        "non_claim": "tool validates custody/shape/completeness and totals manual scores; contaminated dry-run mode, self-attestation without required custody evidence, and manual scores embedded in a frozen response do not certify semantic correctness, independence, compact-cue confirmation, external replay success, deletion authority, or impossible/self-custodied custody chronology, pre-answer material leakage, or score-sheet chronology drift",
    }
    summary["compact_gate_decision"] = decide_compact_gate(summary, scorer)
    return summary


def validate_response_file(
    path: str | pathlib.Path,
    scorer: dict[str, Any] | None = None,
    *,
    allow_contaminated_dryrun: bool = False,
    scorer_intake: str | None = None,
    evidence_record: dict[str, Any] | None = None,
    score_sheet: dict[str, Any] | None = None,
    evidence_record_file: str | pathlib.Path | None = None,
    score_sheet_file: str | pathlib.Path | None = None,
    root: pathlib.Path = ROOT,
) -> dict[str, Any]:
    response, response_sha256, response_path = _read_json_file(path, label="response", root=root)
    resolved_scorer = scorer
    resolved_rel = scorer_intake
    if resolved_scorer is None:
        resolved_scorer, resolved_rel = load_scorer_intake(scorer_intake, root=root)
    if resolved_rel and resolved_rel != DEFAULT_SCORER_INTAKE:
        scorer_from_file, _, _ = _read_json_file(resolved_rel, label="scorer intake", root=root)
        if resolved_scorer != scorer_from_file:
            _fail("scorer intake object does not match selected scorer intake file")
    authorized_dryrun = allow_contaminated_dryrun and _dryrun_authorized(response)
    require_evidence_file = bool(resolved_scorer.get("requires_bound_custody_record_file")) and not authorized_dryrun
    require_score_file = bool(resolved_scorer.get("requires_bound_score_sheet_file")) and not authorized_dryrun
    bound_evidence, evidence_sha256, _ = _bind_json_object_to_file(
        evidence_record,
        evidence_record_file,
        label="custody evidence record",
        require_file=require_evidence_file,
        root=root,
    )
    bound_score_sheet, score_sheet_sha256, _ = _bind_json_object_to_file(
        score_sheet,
        score_sheet_file,
        label="score sheet",
        require_file=require_score_file,
        root=root,
    )
    summary = validate_response(
        response,
        resolved_scorer,
        allow_contaminated_dryrun=allow_contaminated_dryrun,
        evidence_record=bound_evidence,
        response_file=response_path,
        response_file_sha256=response_sha256,
        score_sheet=bound_score_sheet,
        evidence_record_sha256=evidence_sha256,
        score_sheet_sha256=score_sheet_sha256,
        root=root,
    )
    summary["response_file"] = str(response_path)
    summary["response_file_sha256"] = response_sha256
    if evidence_record_file is not None:
        summary["custody_evidence_record_file"] = str(_resolve_path(evidence_record_file, root=root))
    if score_sheet_file is not None:
        summary["score_sheet_file"] = str(_resolve_path(score_sheet_file, root=root))
    if resolved_rel:
        summary["scorer_intake"] = resolved_rel
    summary["scorer_selector"] = scorer_intake or DEFAULT_SCORER_INTAKE
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("response_file")
    parser.add_argument("--scorer-intake", default=DEFAULT_SCORER_INTAKE, help="scorer intake path, or auto:frontier to use the live FRONTIER-BACKLOG scorer")
    parser.add_argument("--evidence-record", help="custody evidence record for strict external scoring")
    parser.add_argument("--score-sheet", help="separate post-response manual score sheet for score-separated strict scoring")
    parser.add_argument("--allow-contaminated-dryrun", action="store_true")
    parser.add_argument("--summary-out", help="write validation summary JSON to this path as well as stdout")
    args = parser.parse_args()
    try:
        scorer, scorer_rel = load_scorer_intake(args.scorer_intake)
        evidence = load_json(args.evidence_record) if args.evidence_record else None
        score_sheet = load_json(args.score_sheet) if args.score_sheet else None
        summary = validate_response_file(
            args.response_file,
            scorer,
            allow_contaminated_dryrun=args.allow_contaminated_dryrun,
            scorer_intake=scorer_rel,
            evidence_record=evidence,
            evidence_record_file=args.evidence_record,
            score_sheet=score_sheet,
            score_sheet_file=args.score_sheet,
        )
    except ResponseIntakeError as exc:
        raise SystemExit(str(exc)) from exc
    output = json.dumps(summary, indent=2)
    if args.summary_out:
        out = pathlib.Path(args.summary_out)
        out.parent.mkdir(parents=True, exist_ok=True) if out.parent != pathlib.Path(".") else None
        out.write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

from __future__ import annotations

import copy
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any, ContextManager

from . import __version__
from .contamination import (
    CONTAMINATION_PLAN_FILE,
    CONTAMINATION_SCAN_FILE,
    FILESYSTEM_CANARY_FILE,
    SCENARIO_CONTAMINATION_PLAN_SCHEMA,
    SCENARIO_CONTAMINATION_SCAN_SCHEMA,
    authenticate_scenario_contamination_scan,
    build_scenario_contamination_plan,
    build_scenario_contamination_scan,
    contamination_controls_for_cell,
    contamination_scan_markdown as render_contamination_scan_markdown,
    filesystem_canary_text,
    validate_scenario_contamination_plan,
)
from .cube_copies import clone_cube_exact
from .errors import LacunaError
from .providers import PROVIDERS
from .sidecars import (
    canonical_json_digest,
    ensure_sidecar_lock,
    publish_private_directory,
    make_private_directory,
    read_sidecar_json_object,
    read_sidecar_text,
    resolve_sidecar_directory,
    resolve_sidecar_member_directory,
    shell_command,
    sidecar_lock,
)
from .store import CUBE_CONFIG, DATABASE_NAME, Cube
from .util import (
    SHA256_RE,
    atomic_write_json,
    atomic_write_text,
    canonical_json,
    new_id,
    pretty_json,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

SCENARIO_CAPSULE_SCHEMA = "lacuna.scenario-capsule.v1"
SCENARIO_RUN_SCHEMA = "lacuna.scenario-run.v3"
SCENARIO_ASSIGNMENT_SCHEMA = "lacuna.scenario-assignment.v1"
SCENARIO_DRIVER_SCHEMA = "lacuna.scenario-cell-driver.v2"
SCENARIO_CELL_RETURN_SCHEMA = "lacuna.scenario-cell-return.v1"
SCENARIO_CELL_RECEIPT_SCHEMA = "lacuna.scenario-cell-receipt.v1"
SCENARIO_BLIND_PACKET_SCHEMA = "lacuna.scenario-blind-rating-packet.v1"
SCENARIO_RATING_SCHEMA = "lacuna.scenario-rating.v1"
SCENARIO_MASKING_SCHEMA = "lacuna.scenario-masking-assessment.v1"
SCENARIO_REPORT_SCHEMA = "lacuna.scenario-report.v3"

SCENARIO_RUN_EVENT = "lacuna.scenario.run"
RUN_MANIFEST_FILE = "run.json"
NEXT_FILE = "NEXT.md"
RUN_LOCK_FILE = ".run.lock"
CAPSULE_FILE = "10-capsule.json"
ASSIGNMENT_FILE = "20-PRIVATE-assignment.json"
BLIND_PACKET_FILE = "70-blind-rating-packet.json"
REPORT_FILE = "90-unblinded-report.json"
MASKING_DIR = "ratings"

SCENARIO_CONDITIONS = (
    "forward-only",
    "prompt-only-retcon",
    "lacuna-serial",
    "lacuna-role-separated",
)
RETCON_ROLES = (
    "lacuna-retcon-generator",
    "lacuna-retcon-judge",
    "lacuna-retcon-compressor",
    "lacuna-retcon-verifier",
)
HUMAN_RATING_DIMENSIONS = (
    "coherence",
    "agency",
    "character_believability",
    "genre_fit",
    "payoff",
    "novelty",
    "coincidence_restraint",
    "mystery_fairness",
    "seam_invisibility",
)
SCENARIO_ASSIGNMENT_METHODS = {
    "host-random-seed-sha256-sort-v1",
    "bundle-precommitted-seed-sha256-sort-v1",
}
SCENARIO_FAILURE_CLASSES = {
    "provider-error",
    "timeout",
    "transport-error",
    "invalid-output",
    "worker-refusal",
    "kernel-refusal",
    "budget-exhausted",
    "interrupted",
    "other",
}
CELL_STATUSES = ("pending", "active", "recorded")
RUN_STATUSES = (
    "collecting-results",
    "awaiting-ratings",
    "awaiting-masking",
    "ready-to-unblind",
    "unblinded",
)
MASKING_GUESSES = SCENARIO_CONDITIONS + ("unknown",)
MASKING_FAMILIARITY = ("none", "low", "medium", "high")
SCENARIO_SCRIPT_TEMPLATE_PLACEHOLDERS = {
    "Replace this sentence with one exact scripted off-plan player action.",
    "Replace this sentence with one exact action that tests the post-checkpoint continuation.",
}
SCENARIO_MODEL_POLICY_TEMPLATE_VALUES = {
    ("model_family", "declare-one-model-family"),
    ("model", "unknown"),
    (
        "sampling_policy",
        "Use the same declared sampling policy and budget in every cell.",
    ),
}

CAPSULE_FIELDS = {
    "schema",
    "capsule_id",
    "title",
    "research_question",
    "seed",
    "actors",
    "script",
    "conditions",
    "model_policy",
    "budget",
    "rating",
    "notes",
}
SEED_FIELDS = {"cube_id", "head"}
ACTOR_FIELDS = {"audience_id", "actor_id"}
STEP_FIELDS = {
    "step_id",
    "player_input",
    "checkpoint_after",
    "checkpoint_trigger",
    "tags",
}
MODEL_POLICY_FIELDS = {
    "provider",
    "model_family",
    "model",
    "model_version",
    "sampling_policy",
    "sampling_seed",
    "same_model_required",
}
BUDGET_FIELDS = {
    "max_invocations_per_cell",
    "max_duration_ms_per_cell",
    "max_input_tokens_per_cell",
    "max_output_tokens_per_cell",
    "max_cost_microusd_per_cell",
}
RATING_POLICY_FIELDS = {
    "rater_count",
    "scale_min",
    "scale_max",
    "dimension_prompts",
    "comments_prompt",
}
MANIFEST_FIELDS = {
    "event",
    "schema",
    "project_version",
    "run_id",
    "run_path",
    "created_at",
    "updated_at",
    "reference",
    "resolved_seed_cube_path",
    "seed",
    "status",
    "capsule",
    "assignment",
    "contamination_plan",
    "contamination_scan",
    "cells",
    "ratings",
    "masking_assessments",
    "unblind_gate",
    "blind_packet",
    "report",
    "unblinded_at",
    "next_action",
    "nonclaims",
}
MANIFEST_SEED_FIELDS = {
    "cube_id",
    "head",
    "event_count",
    "snapshot_sha256",
}
ARTIFACT_REF_FIELDS = {"path", "sha256", "schema", "role"}
CELL_FIELDS = {"ordinal", "label", "status", "cube_path", "driver", "result"}
RATING_REF_FIELDS = ARTIFACT_REF_FIELDS | {"rating_id", "rater_id"}
MASKING_REF_FIELDS = ARTIFACT_REF_FIELDS | {"masking_id", "assessor_id"}
NEXT_ACTION_FIELDS = {
    "owner",
    "action",
    "input_path",
    "expected_schema",
    "command",
    "blind",
}
UNBLIND_GATE_FIELDS = {
    "kind",
    "bundle_id",
    "block_id",
    "status",
    "opened_at",
    "opening_sha256",
    "nonclaims",
}
ASSIGNMENT_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "method",
    "randomization_seed",
    "assignments",
    "created_at",
    "nonclaims",
}
ASSIGNMENT_ITEM_FIELDS = {"ordinal", "cell_label", "condition"}
DRIVER_FIELDS = {
    "event",
    "schema",
    "project_version",
    "run_id",
    "capsule_id",
    "cell_label",
    "ordinal",
    "condition",
    "seed",
    "resolved_cube_path",
    "turn_run_root",
    "checkpoint_run_root",
    "script",
    "model_policy",
    "budget",
    "condition_contract",
    "contamination_controls",
    "instructions",
    "return_contract",
    "nonclaims",
}
CONDITION_CONTRACT_FIELDS = {
    "checkpoint_mode",
    "required_roles",
    "context_rule",
    "continuation_mode",
    "checkpoint_step_ids",
}
RETURN_CONTRACT_FIELDS = {"schema", "template", "record_command"}
CELL_RETURN_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "cell_label",
    "status",
    "transcript",
    "invocations",
    "failure",
    "completed_at",
    "operator_notes",
    "declaration",
    "nonclaims",
}
TRANSCRIPT_ITEM_FIELDS = {"step_id", "narration"}
INVOCATION_FIELDS = {
    "sequence",
    "phase",
    "role",
    "script_step_id",
    "checkpoint_step_id",
    "managed_checkpoint_id",
    "continuation_checkpoint_id",
    "continuation_capsule_sha256",
    "provider",
    "model",
    "model_version",
    "context_id",
    "invocation_id",
    "input_sha256",
    "output_sha256",
    "started_at",
    "completed_at",
    "duration_ms",
    "input_tokens",
    "output_tokens",
    "cost_microusd",
    "outcome",
    "failure_class",
    "failure_message",
}
FAILURE_FIELDS = {"class", "message"}
RECEIPT_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "cell_label",
    "assignment_sha256",
    "driver_sha256",
    "return_artifact",
    "return_sha256",
    "transcript_sha256",
    "observed_cube",
    "execution_totals",
    "accepted_at",
    "nonclaims",
}
OBSERVED_CUBE_FIELDS = {
    "cube_id",
    "seed_head",
    "final_head",
    "seed_event_count",
    "final_event_count",
    "event_count_delta",
    "verification_sha256",
    "overall_status",
}
EXECUTION_TOTAL_FIELDS = {
    "invocation_count",
    "accepted_invocations",
    "failed_invocations",
    "duration_ms",
    "duration_complete",
    "input_tokens",
    "input_tokens_complete",
    "output_tokens",
    "output_tokens_complete",
    "cost_microusd",
    "cost_complete",
}
BLIND_PACKET_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "title",
    "research_question",
    "created_at",
    "rubric",
    "cells",
    "instructions",
    "nonclaims",
}
BLIND_CELL_FIELDS = {"cell_label", "status", "transcript", "transcript_sha256"}
RATING_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "rating_id",
    "rater_id",
    "blind_packet_sha256",
    "ratings",
    "declared_at",
    "declaration",
    "nonclaims",
}
RATING_ITEM_FIELDS = {"cell_label", "scores", "preference_rank", "comments"}
MASKING_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "masking_id",
    "assessor_id",
    "blind_packet_sha256",
    "primary_rating_sha256s",
    "assessments",
    "declared_at",
    "declaration",
    "nonclaims",
}
MASKING_ITEM_FIELDS = {
    "cell_label",
    "guessed_condition",
    "confidence",
    "cues",
    "familiarity",
    "recognized_method",
    "notes",
}
REPORT_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "title",
    "research_question",
    "assignment_sha256",
    "blind_packet_sha256",
    "contamination_scan_sha256",
    "contamination_summary",
    "rating_artifact_sha256s",
    "masking_artifact_sha256s",
    "cell_records",
    "mechanical_outcomes",
    "human_rating_summary",
    "method_identifiability_summary",
    "unblinded_at",
    "separation",
    "nonclaims",
}
REPORT_CELL_FIELDS = {
    "condition",
    "cell_label",
    "status",
    "transcript_sha256",
    "return_sha256",
    "receipt_sha256",
    "contamination_status",
    "contamination_unexpected_match_count",
}
CONTAMINATION_SUMMARY_FIELDS = {
    "overall_status",
    "unexpected_match_count",
    "cells",
}
CONTAMINATION_CELL_SUMMARY_FIELDS = {
    "condition",
    "cell_label",
    "status",
    "own_canary_leaks",
    "foreign_canary_leaks",
    "unexpected_match_count",
}
MECHANICAL_OUTCOME_FIELDS = {
    "condition",
    "cell_label",
    "final_head",
    "event_count_delta",
    "execution_totals",
}
SUMMARY_FIELDS = {"dimensions", "preference_rank"}
SUMMARY_VALUE_FIELDS = {"score_sum", "score_count"}
METHOD_IDENTIFIABILITY_FIELDS = {
    "assessor_count",
    "cell_count",
    "correct_guess_count",
    "nonunknown_guess_count",
    "confidence_sum",
    "confusion",
}
CONFUSION_VALUE_FIELDS = {
    "guess_count",
    "correct_guess_count",
    "confidence_sum",
    "recognized_method_count",
}

SCENARIO_RUN_NONCLAIMS = [
    "The scenario run is a private experiment sidecar, not a ledger event, provider invocation, randomization oracle, or proof of model independence.",
    "All four cell cubes are exact local clones of one verified seed boundary and intentionally retain the same cube identity; cell labels and paths provide experimental separation, not ontological forks.",
    "Condition assignment is committed before results are accepted, but a same-host experiment owner can still rerun or discard unpublished experiments unless an external witness retains the commitment.",
    "Invocation identity, context separation, token counts, cost, latency, and failure metadata are host declarations unless independently attested by a provider.",
    "Blind rating packets omit structural condition labels and private canary findings, but Lacuna cannot prove semantic blinding or prevent a transcript from revealing its method.",
    "Preregistered exact canaries can falsify some claimed context or filesystem boundaries; a clean scan cannot prove isolation, forgetting, or semantic noninterference.",
    "Mechanical cube outcomes, host-declared execution measures, and authored human ratings remain separate evidence classes; none is automatically truth or causal proof.",
    "The .run.lock file coordinates cooperative same-host callers only and is not a distributed lock or hostile-user boundary.",
]
ASSIGNMENT_NONCLAIMS = [
    "This private assignment document reveals condition identity and must not be given to blind raters before unblinding.",
    "The SHA-256 sort is deterministic from the recorded seed, but the host-generated seed is not externally witnessed randomness.",
    "A retained commitment detects later edits to this published run; it does not prove that discarded unpublished assignments never existed.",
]
DRIVER_NONCLAIMS = [
    "This driver describes one experimental condition; it does not invoke a model, enforce provider memory boundaries, or grant kernel authority.",
    "The cell cube is an experimental clone. Its mutations do not change the seed cube or any other cell.",
    "Only player-visible transcript text enters the blind rating packet; hidden prompts, canary tokens, scan findings, and role artifacts remain private experiment custody until unblinding.",
    "The operator-only canary is intentionally present in this private cell-coordinator driver; do not forward the complete driver to delegated role workers or blind raters.",
]
CELL_RETURN_NONCLAIMS = [
    "Invocation metadata, context IDs, managed checkpoint IDs, and continuation capsule digests are host declarations, not provider-signed attestations.",
    "A digest binds the retained value the host chose to identify; it does not prove the provider received or produced that value.",
    "Transcript narration is player-visible experiment output and does not become seed-cube canon by appearing here.",
]
CELL_RECEIPT_NONCLAIMS = [
    "The observed cube metrics are derived by Lacuna from the cell clone at acceptance time.",
    "Execution totals summarize host-declared invocation records and are not independently metered.",
    "Acceptance freezes the cell head for later audit but does not establish narrative quality or causal effect.",
]
RATING_NONCLAIMS = [
    "This rating is an authored judgment, not an objective truth metric.",
    "The rater declares that the blind packet, not the private assignment, was used; Lacuna cannot inspect the rater's prior knowledge.",
    "Condition identity is intentionally absent from the structured rating contract until unblinding.",
]
MASKING_NONCLAIMS = [
    "This masking assessment is collected only after the primary blind rating for the run has been frozen.",
    "The assessment may expose method names to the assessor and therefore must not be available before primary rating artifacts are accepted.",
    "Condition guesses, cue reports, recognition claims, and confidence values are authored judgments, not proof of semantic anonymity or leakage.",
    "Correctness is intentionally absent from this artifact and is joined only by the unblinded descriptive report.",
]
UNBLIND_GATE_NONCLAIMS = [
    "This child run was staged inside a preregistered scenario bundle and cannot be unblinded by the standalone scenario command until the bundle opens this gate.",
    "The gate prevents accidental direct-child unblinding; it is not a hostile-host security boundary or provider attestation.",
    "The opening digest is supplied by the bundle after the blinded block seal exists and every scheduled block is sealed.",
]
BLIND_PACKET_NONCLAIMS = [
    "The packet omits structured condition identity and assignment order.",
    "Lacuna cannot guarantee that prose style, failures, or leaked method names do not reveal a condition semantically.",
    "Ratings should be completed and recorded before the experiment owner runs unblind.",
    "The packet intentionally omits the private contamination plan and scan result so exact findings cannot bias blind ratings.",
]
REPORT_NONCLAIMS = [
    "The report is a descriptive join of committed assignment, accepted cell receipts, and authored blind ratings.",
    "Score sums and counts are not calibrated utilities, statistical significance, or causal estimates.",
    "Host-declared invocation measures must not be conflated with Lacuna-derived cube verification and event-count measures.",
    "Exact canary findings are falsification evidence only; clean status is not provider attestation or proof of semantic isolation.",
]


def _fail(code: str, message: str, details: dict[str, Any] | None = None) -> None:
    raise LacunaError(code, message, details)


def _strict(value: Any, *, label: str, fields: set[str], code: str) -> dict[str, Any]:
    try:
        document = require_mapping(value, label)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    unexpected = sorted(set(document) - fields)
    missing = sorted(fields - set(document))
    if unexpected or missing:
        _fail(
            code,
            f"{label} has an invalid field set",
            {"unexpected": unexpected, "missing": missing},
        )
    return document


def _digest(value: Any, *, label: str = "scenario artifact") -> str:
    return canonical_json_digest(
        value,
        error_code="bad-scenario-artifact",
        label=label,
    )


def _optional_string(
    value: Any,
    field: str,
    *,
    max_len: int = 4096,
    allow_empty: bool = True,
) -> str | None:
    if value is None:
        return None
    try:
        return require_string(value, field, allow_empty=allow_empty, max_len=max_len)
    except ValueError as exc:
        raise LacunaError("bad-scenario-artifact", str(exc)) from exc


def _require_bool(value: Any, field: str, *, code: str) -> bool:
    if not isinstance(value, bool):
        _fail(code, f"{field} must be boolean")
    return value


def _bounded_int(
    value: Any,
    field: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
    nullable: bool = False,
    code: str,
) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(code, f"{field} must be an integer" + (" or null" if nullable else ""))
    assert isinstance(value, int)
    if value < minimum or (maximum is not None and value > maximum):
        suffix = f" between {minimum} and {maximum}" if maximum is not None else f" at least {minimum}"
        _fail(code, f"{field} must be{suffix}")
    return value


def _require_sha256(value: Any, field: str, *, code: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(code, f"{field} must be a lowercase SHA-256 digest")
    return value


def _artifact_ref(*, path: str, value: dict[str, Any], schema: str, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": _digest(value, label=path),
        "schema": schema,
        "role": role,
    }


def _write_json_ref(
    run_path: Path,
    *,
    relative_path: str,
    value: dict[str, Any],
    schema: str,
    role: str,
) -> dict[str, Any]:
    target = run_path / PurePosixPath(relative_path)
    atomic_write_json(target, value)
    return _artifact_ref(path=relative_path, value=value, schema=schema, role=role)


def _validate_ref(
    run_path: Path,
    value: Any,
    *,
    expected_path: str,
    expected_schema: str,
    expected_role: str,
    label: str,
    fields: set[str] = ARTIFACT_REF_FIELDS,
) -> dict[str, Any]:
    document = _strict(value, label=label, fields=fields, code="bad-scenario-run")
    if document.get("path") != expected_path:
        _fail(
            "scenario-run-path-mismatch",
            f"{label}.path must be {expected_path!r}",
            {"actual": document.get("path")},
        )
    _require_sha256(document.get("sha256"), f"{label}.sha256", code="bad-scenario-run")
    if document.get("schema") != expected_schema or document.get("role") != expected_role:
        _fail(
            "scenario-run-artifact-metadata-mismatch",
            f"{label} metadata does not match its fixed contract",
            {
                "expected_schema": expected_schema,
                "actual_schema": document.get("schema"),
                "expected_role": expected_role,
                "actual_role": document.get("role"),
            },
        )
    return document


def _read_ref_json(
    run_path: Path,
    ref: dict[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    document = read_sidecar_json_object(
        run_path / PurePosixPath(ref["path"]),
        label=label,
        error_prefix="scenario-run",
        root_error_code="bad-scenario-artifact",
    )
    if _digest(document, label=label) != ref["sha256"]:
        _fail(
            "scenario-run-artifact-digest-mismatch",
            f"{label} no longer matches its retained digest",
            {"path": ref["path"]},
        )
    return document


def _private_mkdir(path: Path) -> None:
    make_private_directory(path)


def _scenario_assignment(seed: str) -> list[dict[str, Any]]:
    ordered_conditions = sorted(
        SCENARIO_CONDITIONS,
        key=lambda condition: (sha256_text(f"{seed}:condition:{condition}"), condition),
    )
    assignments: list[dict[str, Any]] = []
    for ordinal, condition in enumerate(ordered_conditions, start=1):
        label = "cell_" + sha256_text(f"{seed}:label:{ordinal}")[:12]
        assignments.append(
            {"ordinal": ordinal, "cell_label": label, "condition": condition}
        )
    return assignments


def _default_dimension_prompts() -> dict[str, str]:
    return {
        "coherence": "How internally coherent is the continuation with the story so far?",
        "agency": "How well does the continuation preserve meaningful player choice?",
        "character_believability": "How believable and stable are character motives and behavior?",
        "genre_fit": "How well does the continuation fit the established genre and tone?",
        "payoff": "How effectively does the continuation create or deliver meaningful payoff?",
        "novelty": "How interesting and non-generic is the continuation?",
        "coincidence_restraint": "How well does it avoid implausibly making every incidental detail important?",
        "mystery_fairness": "How fairly does it preserve evidence and avoid moving the answer after clues?",
        "seam_invisibility": "How little does the continuation expose replanning, contradiction, or railroading seams?",
    }


def build_scenario_capsule_template(
    cube: Cube,
    *,
    title: str = "Retcon planning comparison",
    research_question: str = "Does source-bound retcon planning improve an off-script continuation without producing rubber reality?",
) -> dict[str, Any]:
    try:
        title = require_string(title, "title", max_len=512)
        research_question = require_string(
            research_question, "research_question", max_len=4000
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        _fail(
            "cube-verification-failed",
            "refusing to bind a scenario capsule template to an unverified cube",
            verification,
        )
    return {
        "schema": SCENARIO_CAPSULE_SCHEMA,
        "capsule_id": new_id("capsule"),
        "title": title,
        "research_question": research_question,
        "seed": {"cube_id": cube.meta("cube_id"), "head": cube.head()},
        "actors": {"audience_id": "player", "actor_id": "narrator"},
        "script": [
            {
                "step_id": "step.off-script-1",
                "player_input": "Replace this sentence with one exact scripted off-plan player action.",
                "checkpoint_after": True,
                "checkpoint_trigger": "Reconsider the latent story only after preserving every observed fact and exposed consequence.",
                "tags": ["off-script-departure"],
            },
            {
                "step_id": "step.post-checkpoint-1",
                "player_input": "Replace this sentence with one exact action that tests the post-checkpoint continuation.",
                "checkpoint_after": False,
                "checkpoint_trigger": None,
                "tags": ["post-checkpoint-continuation"],
            },
        ],
        "conditions": list(SCENARIO_CONDITIONS),
        "model_policy": {
            "provider": "portable",
            "model_family": "declare-one-model-family",
            "model": "unknown",
            "model_version": None,
            "sampling_policy": "Use the same declared sampling policy and budget in every cell.",
            "sampling_seed": None,
            "same_model_required": True,
        },
        "budget": {
            "max_invocations_per_cell": 64,
            "max_duration_ms_per_cell": None,
            "max_input_tokens_per_cell": None,
            "max_output_tokens_per_cell": None,
            "max_cost_microusd_per_cell": None,
        },
        "rating": {
            "rater_count": 1,
            "scale_min": 1,
            "scale_max": 7,
            "dimension_prompts": _default_dimension_prompts(),
            "comments_prompt": "Record concrete seams, contradictions, agency losses, unfair clue movement, and notable strengths.",
        },
        "notes": None,
    }


def validate_scenario_capsule(value: Any) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario capsule",
        fields=CAPSULE_FIELDS,
        code="bad-scenario-capsule",
    )
    if document.get("schema") != SCENARIO_CAPSULE_SCHEMA:
        _fail("bad-scenario-capsule", "unsupported scenario capsule schema")
    try:
        require_id(document.get("capsule_id"), "capsule_id")
        require_string(document.get("title"), "title", max_len=512)
        require_string(
            document.get("research_question"),
            "research_question",
            max_len=4000,
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc

    seed = _strict(
        document.get("seed"),
        label="seed",
        fields=SEED_FIELDS,
        code="bad-scenario-capsule",
    )
    try:
        require_id(seed.get("cube_id"), "seed.cube_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    _require_sha256(seed.get("head"), "seed.head", code="bad-scenario-capsule")

    actors = _strict(
        document.get("actors"),
        label="actors",
        fields=ACTOR_FIELDS,
        code="bad-scenario-capsule",
    )
    try:
        require_id(actors.get("audience_id"), "actors.audience_id")
        require_id(actors.get("actor_id"), "actors.actor_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc

    try:
        script_values = require_list(document.get("script"), "script")
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    if not 2 <= len(script_values) <= 100:
        _fail("bad-scenario-capsule", "script must contain between 2 and 100 steps")
    step_ids: list[str] = []
    checkpoint_count = 0
    normalized_script: list[dict[str, Any]] = []
    for index, value_item in enumerate(script_values):
        item = _strict(
            value_item,
            label=f"script[{index}]",
            fields=STEP_FIELDS,
            code="bad-scenario-capsule",
        )
        try:
            step_id = require_id(item.get("step_id"), f"script[{index}].step_id")
            player_input = require_string(
                item.get("player_input"),
                f"script[{index}].player_input",
                max_len=50000,
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-capsule", str(exc)) from exc
        if step_id in step_ids:
            _fail("bad-scenario-capsule", f"duplicate script step_id {step_id!r}")
        if player_input in SCENARIO_SCRIPT_TEMPLATE_PLACEHOLDERS:
            _fail(
                "scenario-capsule-template-not-edited",
                "scenario capsule still contains generated player-input template text",
                {"step_id": step_id, "script_index": index},
            )
        step_ids.append(step_id)
        checkpoint_after = _require_bool(
            item.get("checkpoint_after"),
            f"script[{index}].checkpoint_after",
            code="bad-scenario-capsule",
        )
        trigger = item.get("checkpoint_trigger")
        if checkpoint_after:
            if index == len(script_values) - 1:
                _fail(
                    "bad-scenario-capsule",
                    "a checkpoint cannot follow the final script step because no post-checkpoint continuation would be observed",
                    {"step_id": step_id, "index": index},
                )
            checkpoint_count += 1
            try:
                trigger = require_string(
                    trigger,
                    f"script[{index}].checkpoint_trigger",
                    max_len=50000,
                )
            except ValueError as exc:
                raise LacunaError("bad-scenario-capsule", str(exc)) from exc
        elif trigger is not None:
            _fail(
                "bad-scenario-capsule",
                f"script[{index}].checkpoint_trigger must be null when checkpoint_after is false",
            )
        try:
            tag_values = require_list(item.get("tags"), f"script[{index}].tags")
            tags = [
                require_id(tag, f"script[{index}].tags[{tag_index}]")
                for tag_index, tag in enumerate(tag_values)
            ]
        except ValueError as exc:
            raise LacunaError("bad-scenario-capsule", str(exc)) from exc
        if len(tags) != len(set(tags)) or len(tags) > 32:
            _fail(
                "bad-scenario-capsule",
                f"script[{index}].tags must contain at most 32 unique IDs",
            )
        normalized_script.append(
            {
                "step_id": step_id,
                "player_input": player_input,
                "checkpoint_after": checkpoint_after,
                "checkpoint_trigger": trigger,
                "tags": tags,
            }
        )
    if checkpoint_count == 0:
        _fail(
            "bad-scenario-capsule",
            "at least one script step must designate a checkpoint for the retcon conditions",
        )

    try:
        conditions = require_list(document.get("conditions"), "conditions")
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    if conditions != list(SCENARIO_CONDITIONS):
        _fail(
            "bad-scenario-capsule",
            "conditions must contain the four canonical comparison conditions in fixed order",
            {"expected": list(SCENARIO_CONDITIONS), "actual": conditions},
        )

    policy = _strict(
        document.get("model_policy"),
        label="model_policy",
        fields=MODEL_POLICY_FIELDS,
        code="bad-scenario-capsule",
    )
    if policy.get("provider") not in PROVIDERS:
        _fail(
            "bad-scenario-capsule",
            f"model_policy.provider must be one of {list(PROVIDERS)}",
        )
    for field, placeholder in SCENARIO_MODEL_POLICY_TEMPLATE_VALUES:
        if policy.get(field) == placeholder:
            _fail(
                "scenario-capsule-template-not-edited",
                "scenario capsule still contains generated model-policy template text",
                {"field": f"model_policy.{field}"},
            )
    try:
        require_string(policy.get("model_family"), "model_policy.model_family", max_len=512)
        require_string(policy.get("model"), "model_policy.model", max_len=512)
        _optional_string(policy.get("model_version"), "model_policy.model_version", max_len=512)
        require_string(
            policy.get("sampling_policy"),
            "model_policy.sampling_policy",
            max_len=4000,
        )
        _optional_string(
            policy.get("sampling_seed"),
            "model_policy.sampling_seed",
            max_len=512,
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    _require_bool(
        policy.get("same_model_required"),
        "model_policy.same_model_required",
        code="bad-scenario-capsule",
    )

    budget = _strict(
        document.get("budget"),
        label="budget",
        fields=BUDGET_FIELDS,
        code="bad-scenario-capsule",
    )
    _bounded_int(
        budget.get("max_invocations_per_cell"),
        "budget.max_invocations_per_cell",
        minimum=1,
        maximum=1000,
        code="bad-scenario-capsule",
    )
    for field in sorted(BUDGET_FIELDS - {"max_invocations_per_cell"}):
        _bounded_int(
            budget.get(field),
            f"budget.{field}",
            minimum=0,
            nullable=True,
            code="bad-scenario-capsule",
        )

    rating = _strict(
        document.get("rating"),
        label="rating",
        fields=RATING_POLICY_FIELDS,
        code="bad-scenario-capsule",
    )
    rater_count = _bounded_int(
        rating.get("rater_count"),
        "rating.rater_count",
        minimum=1,
        maximum=100,
        code="bad-scenario-capsule",
    )
    scale_min = _bounded_int(
        rating.get("scale_min"),
        "rating.scale_min",
        minimum=0,
        maximum=100,
        code="bad-scenario-capsule",
    )
    scale_max = _bounded_int(
        rating.get("scale_max"),
        "rating.scale_max",
        minimum=1,
        maximum=100,
        code="bad-scenario-capsule",
    )
    assert isinstance(scale_min, int) and isinstance(scale_max, int)
    if scale_min >= scale_max:
        _fail("bad-scenario-capsule", "rating.scale_min must be below scale_max")
    prompts = _strict(
        rating.get("dimension_prompts"),
        label="rating.dimension_prompts",
        fields=set(HUMAN_RATING_DIMENSIONS),
        code="bad-scenario-capsule",
    )
    try:
        normalized_prompts = {
            dimension: require_string(
                prompts[dimension],
                f"rating.dimension_prompts.{dimension}",
                max_len=2000,
            )
            for dimension in HUMAN_RATING_DIMENSIONS
        }
        comments_prompt = require_string(
            rating.get("comments_prompt"),
            "rating.comments_prompt",
            max_len=4000,
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-capsule", str(exc)) from exc
    assert isinstance(rater_count, int)

    notes = _optional_string(document.get("notes"), "notes", max_len=20000)
    normalized = copy.deepcopy(document)
    normalized["seed"] = {"cube_id": seed["cube_id"], "head": seed["head"]}
    normalized["actors"] = {
        "audience_id": actors["audience_id"],
        "actor_id": actors["actor_id"],
    }
    normalized["script"] = normalized_script
    normalized["conditions"] = list(SCENARIO_CONDITIONS)
    normalized["model_policy"] = {
        "provider": policy["provider"],
        "model_family": policy["model_family"],
        "model": policy["model"],
        "model_version": policy["model_version"],
        "sampling_policy": policy["sampling_policy"],
        "sampling_seed": policy["sampling_seed"],
        "same_model_required": policy["same_model_required"],
    }
    normalized["budget"] = {
        field: budget[field]
        for field in (
            "max_invocations_per_cell",
            "max_duration_ms_per_cell",
            "max_input_tokens_per_cell",
            "max_output_tokens_per_cell",
            "max_cost_microusd_per_cell",
        )
    }
    normalized["rating"] = {
        "rater_count": rater_count,
        "scale_min": scale_min,
        "scale_max": scale_max,
        "dimension_prompts": normalized_prompts,
        "comments_prompt": comments_prompt,
    }
    normalized["notes"] = notes
    return normalized


def _checkpoint_step_ids(capsule: dict[str, Any]) -> list[str]:
    return [
        step["step_id"]
        for step in capsule["script"]
        if step["checkpoint_after"]
    ]


def _condition_contract(condition: str, capsule: dict[str, Any]) -> dict[str, Any]:
    checkpoint_steps = _checkpoint_step_ids(capsule)
    if condition == "forward-only":
        return {
            "checkpoint_mode": "none",
            "required_roles": [],
            "context_rule": "All ordinary turns use one persistent declared narrator context; no checkpoint invocation is permitted.",
            "continuation_mode": "persistent-context",
            "checkpoint_step_ids": checkpoint_steps,
        }
    if condition == "prompt-only-retcon":
        return {
            "checkpoint_mode": "monolithic",
            "required_roles": ["monolithic-retcon"],
            "context_rule": "Ordinary narration and every monolithic retcon checkpoint use one persistent declared context for the cell.",
            "continuation_mode": "persistent-context",
            "checkpoint_step_ids": checkpoint_steps,
        }
    if condition == "lacuna-serial":
        return {
            "checkpoint_mode": "managed-serial",
            "required_roles": list(RETCON_ROLES),
            "context_rule": "Ordinary narration and all four managed checkpoint roles use one persistent declared context for the cell.",
            "continuation_mode": "persistent-context",
            "checkpoint_step_ids": checkpoint_steps,
        }
    if condition == "lacuna-role-separated":
        return {
            "checkpoint_mode": "managed-role-separated",
            "required_roles": list(RETCON_ROLES),
            "context_rule": "Every checkpoint role uses a fresh pairwise-distinct declared context, and the first narrator after each checkpoint uses another fresh context.",
            "continuation_mode": "fresh-narrator-capsule",
            "checkpoint_step_ids": checkpoint_steps,
        }
    _fail("bad-scenario-condition", f"unsupported scenario condition {condition!r}")


def _condition_instructions(condition: str) -> list[str]:
    common = [
        "Start from the supplied cell cube only; do not read another cell, the private assignment file, or a completed transcript.",
        "Process scripted player inputs in order and retain the exact player-visible narration for every completed step.",
        "Use the capsule's declared provider/model/sampling policy and stay within every declared cell budget.",
        "Record every model attempt in sequence, including failed attempts, with honest script-step, context, digest, timing, token, and cost declarations when available.",
        "Use a fresh provider conversation or execution session for this cell and do not reuse a declared context_id from another condition.",
        "Do not edit the seed cube or another cell. Only this cell clone may change.",
    ]
    if condition == "forward-only":
        specific = [
            "Use one persistent narrator context for the complete cell.",
            "Do not run a retcon checkpoint, revise hidden state because of later events, or reinterpret earlier details teleologically.",
            "Continue from whatever forward plan or latent state existed at the seed boundary; record contradiction, drift, refusal, or railroading rather than silently switching methods.",
        ]
    elif condition == "prompt-only-retcon":
        specific = [
            "Use one persistent narrator context for the complete cell, including every monolithic retcon checkpoint.",
            "At every designated checkpoint, use one monolithic retcon invocation that may generate, select, and compress in that same context.",
            "Do not use Lacuna's generator/judge/compressor/verifier cards or claim role separation.",
            "After the monolithic checkpoint, continue forward in the same context from its compact hidden-state result while preserving observed canon.",
        ]
    elif condition == "lacuna-serial":
        specific = [
            "Use one persistent narrator context for the complete cell.",
            "At every designated checkpoint, use the managed checkpoint runner and execute generator, judge, compressor, and verifier sequentially in that same context.",
            "Continue narration in the same context after commit; this condition intentionally retains rejected futures and parent discussion as a context-window confound.",
            "Only the parent coordinator may accept outputs, review, commit/recover, and present narration.",
        ]
    elif condition == "lacuna-role-separated":
        specific = [
            "At every designated checkpoint, use the managed checkpoint runner and its exact four role cards.",
            "Give generator, judge, compressor, and verifier fresh pairwise-distinct declared contexts or subagents, with only each manufactured least-context card.",
            "After commit, run `checkpoint run next-turn` with the next exact player input; give that complete continuation dispatch to another fresh narrator context and record its checkpoint ID and embedded capsule digest.",
            "Do not continue narration in the parent or any checkpoint worker context.",
            "Only the parent coordinator may accept outputs, review, commit/recover, and present narration.",
        ]
    else:
        _fail("bad-scenario-condition", f"unsupported scenario condition {condition!r}")
    return common + specific


def _invocation_template(capsule: dict[str, Any]) -> dict[str, Any]:
    policy = capsule["model_policy"]
    return {
        "sequence": 1,
        "phase": "ordinary-turn",
        "role": "lacuna-narrator",
        "script_step_id": capsule["script"][0]["step_id"],
        "checkpoint_step_id": None,
        "managed_checkpoint_id": None,
        "continuation_checkpoint_id": None,
        "continuation_capsule_sha256": None,
        "provider": policy["provider"],
        "model": policy["model"],
        "model_version": policy["model_version"],
        "context_id": "context.replace-me",
        "invocation_id": None,
        "input_sha256": "0" * 64,
        "output_sha256": "0" * 64,
        "started_at": None,
        "completed_at": None,
        "duration_ms": None,
        "input_tokens": None,
        "output_tokens": None,
        "cost_microusd": None,
        "outcome": "accepted",
        "failure_class": None,
        "failure_message": None,
    }


def _cell_return_template(
    *,
    run_id: str,
    capsule: dict[str, Any],
    cell_label: str,
) -> dict[str, Any]:
    return {
        "event": "lacuna.scenario.cell-return",
        "schema": SCENARIO_CELL_RETURN_SCHEMA,
        "run_id": run_id,
        "capsule_id": capsule["capsule_id"],
        "cell_label": cell_label,
        "status": "completed",
        "transcript": [
            {
                "step_id": step["step_id"],
                "narration": "Replace with the exact player-visible narration for this step.",
            }
            for step in capsule["script"]
        ],
        "invocations": [_invocation_template(capsule)],
        "failure": None,
        "completed_at": None,
        "operator_notes": None,
        "declaration": "host-declared",
        "nonclaims": list(CELL_RETURN_NONCLAIMS),
    }


def _build_driver(
    *,
    run_id: str,
    run_path: Path,
    capsule: dict[str, Any],
    assignment: dict[str, Any],
    contamination_plan: dict[str, Any],
) -> dict[str, Any]:
    label = assignment["cell_label"]
    cell_root = run_path / "cells" / label
    cube_path = cell_root / "cube"
    return {
        "event": "lacuna.scenario.cell-driver",
        "schema": SCENARIO_DRIVER_SCHEMA,
        "project_version": __version__,
        "run_id": run_id,
        "capsule_id": capsule["capsule_id"],
        "cell_label": label,
        "ordinal": assignment["ordinal"],
        "condition": assignment["condition"],
        "seed": copy.deepcopy(capsule["seed"]),
        "resolved_cube_path": str(cube_path),
        "turn_run_root": str(cell_root / "turn-runs"),
        "checkpoint_run_root": str(cell_root / "checkpoint-runs"),
        "script": copy.deepcopy(capsule["script"]),
        "model_policy": copy.deepcopy(capsule["model_policy"]),
        "budget": copy.deepcopy(capsule["budget"]),
        "condition_contract": _condition_contract(assignment["condition"], capsule),
        "contamination_controls": contamination_controls_for_cell(
            contamination_plan, cell_label=label
        ),
        "instructions": _condition_instructions(assignment["condition"]),
        "return_contract": {
            "schema": SCENARIO_CELL_RETURN_SCHEMA,
            "template": _cell_return_template(
                run_id=run_id,
                capsule=capsule,
                cell_label=label,
            ),
            "record_command": shell_command(
                [
                    "./lacuna",
                    "scenario",
                    "record",
                    str(run_path),
                    "CELL_RETURN.json",
                ]
            ),
        },
        "nonclaims": list(DRIVER_NONCLAIMS),
    }


def _validate_assignment(
    value: Any,
    *,
    run_id: str,
    capsule: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario assignment",
        fields=ASSIGNMENT_FIELDS,
        code="bad-scenario-assignment",
    )
    if document.get("event") != "lacuna.scenario.assignment" or document.get("schema") != SCENARIO_ASSIGNMENT_SCHEMA:
        _fail("bad-scenario-assignment", "unsupported scenario assignment contract")
    if document.get("run_id") != run_id or document.get("capsule_id") != capsule["capsule_id"]:
        _fail("bad-scenario-assignment", "assignment identity does not match the scenario run")
    if document.get("method") not in SCENARIO_ASSIGNMENT_METHODS:
        _fail("bad-scenario-assignment", "unsupported assignment randomization method")
    seed = document.get("randomization_seed")
    if not isinstance(seed, str) or len(seed) != 64 or not SHA256_RE.fullmatch(seed):
        _fail("bad-scenario-assignment", "randomization_seed must be 32 bytes of lowercase hex")
    try:
        assignments = require_list(document.get("assignments"), "assignments")
    except ValueError as exc:
        raise LacunaError("bad-scenario-assignment", str(exc)) from exc
    normalized: list[dict[str, Any]] = []
    for index, value_item in enumerate(assignments):
        item = _strict(
            value_item,
            label=f"assignments[{index}]",
            fields=ASSIGNMENT_ITEM_FIELDS,
            code="bad-scenario-assignment",
        )
        ordinal = _bounded_int(
            item.get("ordinal"),
            f"assignments[{index}].ordinal",
            minimum=1,
            maximum=len(SCENARIO_CONDITIONS),
            code="bad-scenario-assignment",
        )
        try:
            label = require_id(item.get("cell_label"), f"assignments[{index}].cell_label")
        except ValueError as exc:
            raise LacunaError("bad-scenario-assignment", str(exc)) from exc
        condition = item.get("condition")
        if condition not in SCENARIO_CONDITIONS:
            _fail("bad-scenario-assignment", f"unsupported condition {condition!r}")
        normalized.append(
            {"ordinal": ordinal, "cell_label": label, "condition": condition}
        )
    expected = _scenario_assignment(seed)
    if normalized != expected:
        _fail(
            "scenario-assignment-mismatch",
            "condition assignment is not the deterministic permutation committed by its seed",
        )
    try:
        require_string(document.get("created_at"), "created_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-assignment", str(exc)) from exc
    if document.get("nonclaims") != ASSIGNMENT_NONCLAIMS:
        _fail("bad-scenario-assignment", "assignment nonclaims were changed")
    return copy.deepcopy(document)


def _validate_driver(
    value: Any,
    *,
    expected: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario cell driver",
        fields=DRIVER_FIELDS,
        code="bad-scenario-driver",
    )
    contract = _strict(
        document.get("condition_contract"),
        label="condition_contract",
        fields=CONDITION_CONTRACT_FIELDS,
        code="bad-scenario-driver",
    )
    _strict(
        document.get("return_contract"),
        label="return_contract",
        fields=RETURN_CONTRACT_FIELDS,
        code="bad-scenario-driver",
    )
    if contract != expected["condition_contract"] or document != expected:
        _fail(
            "scenario-driver-mismatch",
            "cell driver is not the deterministic condition handoff for this run",
            {"cell_label": expected["cell_label"]},
        )
    return copy.deepcopy(document)


def _render_next(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    lines = [
        "# Lacuna comparative scenario — exact next action",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Status: **{manifest['status']}**",
        f"- Owner: **{action['owner']}**",
        f"- Blind: **{str(action['blind']).lower()}**",
        "",
        action["action"],
    ]
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["expected_schema"] is not None:
        lines.append(f"Expected artifact: `{action['expected_schema']}`")
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.extend(
        [
            "",
            "`run.json` is authoritative. This file is a deterministic pointer only.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(directory: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(directory / RUN_MANIFEST_FILE, manifest)
    atomic_write_text(directory / NEXT_FILE, _render_next(manifest))


def _next_action(run_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    status = manifest["status"]
    cells = manifest["cells"]
    if status == "collecting-results":
        active = [cell for cell in cells if cell["status"] == "active"]
        if active:
            cell = active[0]
            return {
                "owner": "cell-operator",
                "action": f"Execute the active opaque cell {cell['label']} using its private condition driver, then return one exact cell result.",
                "input_path": str(run_path / cell["driver"]["path"]),
                "expected_schema": SCENARIO_CELL_RETURN_SCHEMA,
                "command": shell_command(
                    [
                        "./lacuna",
                        "scenario",
                        "record",
                        str(run_path),
                        "CELL_RETURN.json",
                    ]
                ),
                "blind": False,
            }
        pending = [cell for cell in cells if cell["status"] == "pending"]
        if not pending:
            _fail("bad-scenario-run", "collecting-results has no pending or active cell")
        return {
            "owner": "experiment-owner",
            "action": f"Activate and render the next opaque cell {pending[0]['label']}. Do not share its private driver with blind raters.",
            "input_path": None,
            "expected_schema": SCENARIO_DRIVER_SCHEMA,
            "command": shell_command(
                [
                    "./lacuna",
                    "scenario",
                    "dispatch",
                    str(run_path),
                    "--format",
                    "markdown",
                ]
            ),
            "blind": False,
        }
    if status == "awaiting-ratings":
        return {
            "owner": "blind-rater",
            "action": "Rate every opaque transcript in the blind packet without reading private drivers or the assignment file.",
            "input_path": str(run_path / BLIND_PACKET_FILE),
            "expected_schema": SCENARIO_RATING_SCHEMA,
            "command": shell_command(
                [
                    "./lacuna",
                    "scenario",
                    "rate",
                    str(run_path),
                    "RATING.json",
                ]
            ),
            "blind": True,
        }
    if status == "awaiting-masking":
        return {
            "owner": "blind-rater",
            "action": "Primary ratings are frozen. Now complete the separate method-identifiability/masking assessment without reading private drivers or the assignment file.",
            "input_path": str(run_path / BLIND_PACKET_FILE),
            "expected_schema": SCENARIO_MASKING_SCHEMA,
            "command": shell_command(
                [
                    "./lacuna",
                    "scenario",
                    "mask",
                    str(run_path),
                    "MASKING.json",
                ]
            ),
            "blind": True,
        }
    if status == "ready-to-unblind":
        return {
            "owner": "experiment-owner",
            "action": "All required blind ratings and post-rating masking assessments are frozen. Join them to the committed condition assignment now.",
            "input_path": str(run_path / ASSIGNMENT_FILE),
            "expected_schema": SCENARIO_REPORT_SCHEMA,
            "command": shell_command(
                ["./lacuna", "scenario", "unblind", str(run_path)]
            ),
            "blind": False,
        }
    if status == "unblinded":
        return {
            "owner": "experiment-owner",
            "action": "The descriptive unblinded report is complete. Preserve the run directory and interpret ratings separately from mechanical custody measures.",
            "input_path": str(run_path / REPORT_FILE),
            "expected_schema": None,
            "command": None,
            "blind": False,
        }
    _fail("bad-scenario-run", f"unsupported scenario run status {status!r}")


def _run_directory(value: str | Path) -> Path:
    return resolve_sidecar_directory(
        value,
        manifest_file=RUN_MANIFEST_FILE,
        unknown_code="unknown-scenario-run",
        kind_label="scenario run",
    )


def _run_lock(run_path: Path) -> ContextManager[None]:
    return sidecar_lock(
        run_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="scenario-run",
        kind_label="scenario run",
        busy_message="another process is already advancing this scenario run",
    )


def stage_scenario_run(
    cube: Cube,
    capsule: dict[str, Any],
    *,
    reference: str,
    resolved_seed_cube_path: Path,
    storage_path: Path,
    authority_path: Path,
    run_id: str,
    created_at: str,
    randomization_seed: str,
    assignment_method: str,
    snapshot_sha256: str,
    seed_event_count: int,
    unblind_gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one complete scenario run tree at ``storage_path``.

    ``authority_path`` is the path embedded in manifests, drivers, commands, and
    receipts after publication.  Keeping storage and authority separate lets a
    caller preflight the entire run while it is still inside an unpublished
    parent staging directory.  The caller owns publication and cleanup.
    """
    if not storage_path.is_dir():
        _fail(
            "scenario-run-create-failed",
            f"scenario run staging path is not a directory: {storage_path}",
        )
    if not isinstance(randomization_seed, str) or not SHA256_RE.fullmatch(
        randomization_seed
    ):
        _fail(
            "scenario-run-create-failed",
            "scenario assignment seed must be 32 bytes of lowercase hex",
        )
    if assignment_method not in SCENARIO_ASSIGNMENT_METHODS:
        _fail(
            "scenario-run-create-failed",
            "scenario assignment method is unsupported",
            {"assignment_method": assignment_method},
        )
    assignment_items = _scenario_assignment(randomization_seed)
    assignment = {
        "event": "lacuna.scenario.assignment",
        "schema": SCENARIO_ASSIGNMENT_SCHEMA,
        "run_id": run_id,
        "capsule_id": capsule["capsule_id"],
        "method": assignment_method,
        "randomization_seed": randomization_seed,
        "assignments": assignment_items,
        "created_at": created_at,
        "nonclaims": list(ASSIGNMENT_NONCLAIMS),
    }
    _validate_assignment(assignment, run_id=run_id, capsule=capsule)

    ensure_sidecar_lock(
        storage_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="scenario-run",
        kind_label="scenario run",
    )
    capsule_ref = _write_json_ref(
        storage_path,
        relative_path=CAPSULE_FILE,
        value=capsule,
        schema=SCENARIO_CAPSULE_SCHEMA,
        role="experiment-owner",
    )
    assignment_ref = _write_json_ref(
        storage_path,
        relative_path=ASSIGNMENT_FILE,
        value=assignment,
        schema=SCENARIO_ASSIGNMENT_SCHEMA,
        role="experiment-owner-private",
    )
    contamination_plan = build_scenario_contamination_plan(
        run_id=run_id,
        capsule_id=capsule["capsule_id"],
        assignment=assignment,
        assignment_sha256=assignment_ref["sha256"],
        created_at=created_at,
    )
    contamination_plan_ref = _write_json_ref(
        storage_path,
        relative_path=CONTAMINATION_PLAN_FILE,
        value=contamination_plan,
        schema=SCENARIO_CONTAMINATION_PLAN_SCHEMA,
        role="experiment-owner-private",
    )
    cells_root = storage_path / "cells"
    _private_mkdir(cells_root)
    cells: list[dict[str, Any]] = []
    for assignment_item in assignment_items:
        label = assignment_item["cell_label"]
        cell_root = cells_root / label
        _private_mkdir(cell_root)
        clone_cube_exact(
            cube,
            cell_root / "cube",
            expected_snapshot_sha256=snapshot_sha256,
            error_prefix="scenario",
            kind_label="scenario cell clone",
        )
        _private_mkdir(cell_root / "turn-runs")
        _private_mkdir(cell_root / "checkpoint-runs")
        atomic_write_text(
            cell_root / FILESYSTEM_CANARY_FILE,
            filesystem_canary_text(contamination_plan, cell_label=label),
        )
        driver = _build_driver(
            run_id=run_id,
            run_path=authority_path,
            capsule=capsule,
            assignment=assignment_item,
            contamination_plan=contamination_plan,
        )
        driver_path = f"cells/{label}/30-driver.json"
        driver_ref = _write_json_ref(
            storage_path,
            relative_path=driver_path,
            value=driver,
            schema=SCENARIO_DRIVER_SCHEMA,
            role="experiment-owner-private",
        )
        atomic_write_text(
            cell_root / "DRIVER.md",
            scenario_driver_markdown(driver),
        )
        cells.append(
            {
                "ordinal": assignment_item["ordinal"],
                "label": label,
                "status": "pending",
                "cube_path": f"cells/{label}/cube",
                "driver": driver_ref,
                "result": None,
            }
        )
    manifest: dict[str, Any] = {
        "event": SCENARIO_RUN_EVENT,
        "schema": SCENARIO_RUN_SCHEMA,
        "project_version": __version__,
        "run_id": run_id,
        "run_path": str(authority_path),
        "created_at": created_at,
        "updated_at": created_at,
        "reference": reference,
        "resolved_seed_cube_path": str(resolved_seed_cube_path),
        "seed": {
            "cube_id": cube.meta("cube_id"),
            "head": cube.head(),
            "event_count": seed_event_count,
            "snapshot_sha256": snapshot_sha256,
        },
        "status": "collecting-results",
        "capsule": capsule_ref,
        "assignment": assignment_ref,
        "contamination_plan": contamination_plan_ref,
        "contamination_scan": None,
        "cells": cells,
        "ratings": [],
        "masking_assessments": [],
        "unblind_gate": copy.deepcopy(unblind_gate),
        "blind_packet": None,
        "report": None,
        "unblinded_at": None,
        "next_action": {},
        "nonclaims": list(SCENARIO_RUN_NONCLAIMS),
    }
    manifest["next_action"] = _next_action(authority_path, manifest)
    _write_manifest(storage_path, manifest)
    # Preflight the complete unpublished tree.  This catches construction drift
    # before a standalone run—or an outer replicated experiment—becomes visible.
    return _audit_scenario_run_unlocked(
        storage_path,
        authority_path=authority_path,
    )


def begin_scenario_run(
    cube: Cube,
    capsule_value: dict[str, Any],
    *,
    reference: str,
    resolved_seed_cube_path: str,
    root: str | Path,
    run_id: str | None = None,
    randomization_seed: str | None = None,
) -> dict[str, Any]:
    capsule = validate_scenario_capsule(capsule_value)
    try:
        reference = require_string(reference, "reference", max_len=4096)
        resolved_seed_cube_path = require_string(
            resolved_seed_cube_path, "resolved_seed_cube_path", max_len=4096
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-run-input", str(exc)) from exc
    try:
        bound = cube.root.resolve(strict=True)
        supplied = Path(resolved_seed_cube_path).expanduser().resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            "bad-scenario-run-input",
            f"cannot resolve the scenario seed cube path: {exc}",
        ) from exc
    if bound != supplied:
        _fail(
            "scenario-run-cube-path-mismatch",
            "resolved_seed_cube_path must name the exact Cube used to clone cells",
            {"expected": str(bound), "actual": str(supplied)},
        )
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        _fail(
            "cube-verification-failed",
            "refusing to begin a scenario from a cube that fails verification",
            verification,
        )
    if capsule["seed"] != {"cube_id": cube.meta("cube_id"), "head": cube.head()}:
        _fail(
            "scenario-seed-mismatch",
            "capsule seed identity does not match the open cube boundary",
            {
                "capsule": capsule["seed"],
                "actual": {"cube_id": cube.meta("cube_id"), "head": cube.head()},
            },
        )
    snapshot_sha256 = _digest(cube.snapshot(), label="scenario seed snapshot")
    seed_event_count = cube.event_count()

    root_path = Path(root).expanduser().resolve()
    try:
        root_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise LacunaError(
            "scenario-run-create-failed",
            f"cannot create scenario run root {root_path}: {exc}",
        ) from exc
    if not root_path.is_dir():
        _fail("scenario-run-create-failed", f"scenario run root is not a directory: {root_path}")

    if run_id is None:
        run_id = new_id("scr")
    else:
        try:
            run_id = require_id(run_id, "run_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-run-input", str(exc)) from exc
    if randomization_seed is None:
        randomization_seed = os.urandom(32).hex()
        assignment_method = "host-random-seed-sha256-sort-v1"
    else:
        if not isinstance(randomization_seed, str) or not SHA256_RE.fullmatch(randomization_seed):
            _fail(
                "bad-scenario-run-input",
                "randomization_seed must be 32 bytes of lowercase hex when supplied",
            )
        assignment_method = "bundle-precommitted-seed-sha256-sort-v1"
    run_path = root_path / run_id
    created_at = utc_now()

    with publish_private_directory(
        run_path,
        error_code="scenario-run-create-failed",
        kind_label="scenario run",
    ) as staging_path:
        stage_scenario_run(
            cube,
            capsule,
            reference=reference,
            resolved_seed_cube_path=bound,
            storage_path=staging_path,
            authority_path=run_path,
            run_id=run_id,
            created_at=created_at,
            randomization_seed=randomization_seed,
            assignment_method=assignment_method,
            snapshot_sha256=snapshot_sha256,
            seed_event_count=seed_event_count,
            unblind_gate=None,
        )
    return audit_scenario_run(run_path)


def _validate_invocation(
    value: Any,
    *,
    index: int,
    capsule: dict[str, Any],
    checkpoint_steps: set[str],
) -> dict[str, Any]:
    item = _strict(
        value,
        label=f"invocations[{index}]",
        fields=INVOCATION_FIELDS,
        code="bad-scenario-cell-return",
    )
    sequence = _bounded_int(
        item.get("sequence"),
        f"invocations[{index}].sequence",
        minimum=1,
        maximum=1000,
        code="bad-scenario-cell-return",
    )
    if sequence != index + 1:
        _fail(
            "bad-scenario-cell-return",
            "invocation sequence numbers must be contiguous and one-based",
        )
    if item.get("phase") not in {"ordinary-turn", "checkpoint"}:
        _fail(
            "bad-scenario-cell-return",
            f"invocations[{index}].phase must be ordinary-turn or checkpoint",
        )
    try:
        role = require_id(item.get("role"), f"invocations[{index}].role")
        context_id = require_id(
            item.get("context_id"), f"invocations[{index}].context_id"
        )
        model = require_string(
            item.get("model"), f"invocations[{index}].model", max_len=512
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
    try:
        script_step_id = require_id(
            item.get("script_step_id"), f"invocations[{index}].script_step_id"
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
    script_steps = {step["step_id"] for step in capsule["script"]}
    if script_step_id not in script_steps:
        _fail(
            "bad-scenario-cell-return",
            f"invocations[{index}].script_step_id names an unknown script step",
            {"script_step_id": script_step_id},
        )
    checkpoint_step_id = item.get("checkpoint_step_id")
    if item["phase"] == "checkpoint":
        try:
            checkpoint_step_id = require_id(
                checkpoint_step_id,
                f"invocations[{index}].checkpoint_step_id",
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
        if checkpoint_step_id not in checkpoint_steps:
            _fail(
                "bad-scenario-cell-return",
                f"checkpoint invocation names unknown or non-checkpoint step {checkpoint_step_id!r}",
            )
        if checkpoint_step_id != script_step_id:
            _fail(
                "bad-scenario-cell-return",
                "checkpoint_step_id must equal script_step_id for checkpoint invocations",
            )
    elif checkpoint_step_id is not None:
        _fail(
            "bad-scenario-cell-return",
            f"invocations[{index}].checkpoint_step_id must be null for ordinary-turn",
        )
    elif role != "lacuna-narrator":
        _fail(
            "scenario-condition-topology-mismatch",
            "ordinary-turn invocations must use role lacuna-narrator",
            {"sequence": sequence, "role": role},
        )
    managed_checkpoint_id = item.get("managed_checkpoint_id")
    continuation_checkpoint_id = item.get("continuation_checkpoint_id")
    try:
        if managed_checkpoint_id is not None:
            managed_checkpoint_id = require_id(
                managed_checkpoint_id, f"invocations[{index}].managed_checkpoint_id"
            )
        if continuation_checkpoint_id is not None:
            continuation_checkpoint_id = require_id(
                continuation_checkpoint_id, f"invocations[{index}].continuation_checkpoint_id"
            )
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
    continuation_capsule_sha256 = item.get("continuation_capsule_sha256")
    if continuation_capsule_sha256 is not None:
        continuation_capsule_sha256 = _require_sha256(
            continuation_capsule_sha256,
            f"invocations[{index}].continuation_capsule_sha256",
            code="bad-scenario-cell-return",
        )
    if (continuation_checkpoint_id is None) != (continuation_capsule_sha256 is None):
        _fail(
            "bad-scenario-cell-return",
            "continuation_checkpoint_id and continuation_capsule_sha256 must both be present or both be null",
        )
    if item["phase"] == "checkpoint":
        if continuation_checkpoint_id is not None:
            _fail(
                "bad-scenario-cell-return",
                "checkpoint invocations cannot consume a post-checkpoint narrator capsule",
            )
    elif managed_checkpoint_id is not None:
        _fail(
            "bad-scenario-cell-return",
            "ordinary-turn invocations must use continuation_checkpoint_id rather than managed_checkpoint_id",
        )

    provider = item.get("provider")
    if provider not in PROVIDERS:
        _fail(
            "bad-scenario-cell-return",
            f"invocations[{index}].provider must be one of {list(PROVIDERS)}",
        )
    model_version = _optional_string(
        item.get("model_version"),
        f"invocations[{index}].model_version",
        max_len=512,
    )
    invocation_id = _optional_string(
        item.get("invocation_id"),
        f"invocations[{index}].invocation_id",
        max_len=512,
    )
    input_sha256 = _require_sha256(
        item.get("input_sha256"),
        f"invocations[{index}].input_sha256",
        code="bad-scenario-cell-return",
    )
    output_sha256 = item.get("output_sha256")
    if output_sha256 is not None:
        output_sha256 = _require_sha256(
            output_sha256,
            f"invocations[{index}].output_sha256",
            code="bad-scenario-cell-return",
        )
    started_at = _optional_string(
        item.get("started_at"), f"invocations[{index}].started_at", max_len=128
    )
    completed_at = _optional_string(
        item.get("completed_at"), f"invocations[{index}].completed_at", max_len=128
    )
    if (started_at is None) != (completed_at is None):
        _fail(
            "bad-scenario-cell-return",
            "started_at and completed_at must both be present or both be null",
        )
    duration_ms = _bounded_int(
        item.get("duration_ms"),
        f"invocations[{index}].duration_ms",
        minimum=0,
        nullable=True,
        code="bad-scenario-cell-return",
    )
    input_tokens = _bounded_int(
        item.get("input_tokens"),
        f"invocations[{index}].input_tokens",
        minimum=0,
        nullable=True,
        code="bad-scenario-cell-return",
    )
    output_tokens = _bounded_int(
        item.get("output_tokens"),
        f"invocations[{index}].output_tokens",
        minimum=0,
        nullable=True,
        code="bad-scenario-cell-return",
    )
    cost = _bounded_int(
        item.get("cost_microusd"),
        f"invocations[{index}].cost_microusd",
        minimum=0,
        nullable=True,
        code="bad-scenario-cell-return",
    )
    outcome = item.get("outcome")
    if outcome not in {"accepted", "failed"}:
        _fail(
            "bad-scenario-cell-return",
            f"invocations[{index}].outcome must be accepted or failed",
        )
    failure_class = item.get("failure_class")
    failure_message = _optional_string(
        item.get("failure_message"),
        f"invocations[{index}].failure_message",
        max_len=10000,
    )
    if outcome == "accepted":
        if output_sha256 is None or failure_class is not None or failure_message is not None:
            _fail(
                "bad-scenario-cell-return",
                "accepted invocations require output_sha256 and no failure fields",
            )
    else:
        if output_sha256 is not None or failure_class not in SCENARIO_FAILURE_CLASSES:
            _fail(
                "bad-scenario-cell-return",
                "failed invocations require a supported failure_class and null output_sha256",
            )
    policy = capsule["model_policy"]
    if policy["same_model_required"]:
        expected = (policy["provider"], policy["model"], policy["model_version"])
        actual = (provider, model, model_version)
        if actual != expected:
            _fail(
                "scenario-model-policy-mismatch",
                "same_model_required forbids provider/model/version drift across cells",
                {"expected": expected, "actual": actual, "sequence": sequence},
            )
    return {
        "sequence": sequence,
        "phase": item["phase"],
        "role": role,
        "script_step_id": script_step_id,
        "checkpoint_step_id": checkpoint_step_id,
        "managed_checkpoint_id": managed_checkpoint_id,
        "continuation_checkpoint_id": continuation_checkpoint_id,
        "continuation_capsule_sha256": continuation_capsule_sha256,
        "provider": provider,
        "model": model,
        "model_version": model_version,
        "context_id": context_id,
        "invocation_id": invocation_id,
        "input_sha256": input_sha256,
        "output_sha256": output_sha256,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_microusd": cost,
        "outcome": outcome,
        "failure_class": failure_class,
        "failure_message": failure_message,
    }


def _validate_condition_topology(
    *,
    condition: str,
    capsule: dict[str, Any],
    invocations: list[dict[str, Any]],
    transcript_step_ids: list[str],
    completed: bool,
) -> None:
    script_step_ids = [step["step_id"] for step in capsule["script"]]
    checkpoint_step_ids = _checkpoint_step_ids(capsule)
    checkpoint_step_set = set(checkpoint_step_ids)
    step_positions = {step_id: index for index, step_id in enumerate(script_step_ids)}

    ordinary_calls = [item for item in invocations if item["phase"] == "ordinary-turn"]
    ordinary_accepted = [item for item in ordinary_calls if item["outcome"] == "accepted"]
    accepted_step_ids = [item["script_step_id"] for item in ordinary_accepted]
    expected_steps = script_step_ids if completed else transcript_step_ids
    if accepted_step_ids != expected_steps:
        _fail(
            "scenario-condition-topology-mismatch",
            "accepted ordinary-turn calls must match the retained transcript exactly, once per step and in script order",
            {"expected": expected_steps, "actual": accepted_step_ids},
        )
    accepted_ordinary_by_step = {
        item["script_step_id"]: item for item in ordinary_accepted
    }
    ordinary_calls_by_step: dict[str, list[dict[str, Any]]] = {
        step_id: [] for step_id in script_step_ids
    }
    for item in ordinary_calls:
        ordinary_calls_by_step[item["script_step_id"]].append(item)

    phase_ranks = [
        2 * step_positions[item["script_step_id"]]
        + (1 if item["phase"] == "checkpoint" else 0)
        for item in invocations
    ]
    if phase_ranks != sorted(phase_ranks):
        _fail(
            "scenario-condition-topology-mismatch",
            "invocations must walk each ordinary turn and its checkpoint before advancing to the next script step",
        )
    for step_id, calls in ordinary_calls_by_step.items():
        accepted_seen = False
        for call in sorted(calls, key=lambda item: item["sequence"]):
            if accepted_seen:
                _fail(
                    "scenario-condition-topology-mismatch",
                    "no ordinary-turn retry may follow an accepted output for the same script step",
                    {"step_id": step_id},
                )
            accepted_seen = call["outcome"] == "accepted"

    checkpoint_calls = [item for item in invocations if item["phase"] == "checkpoint"]
    for call in checkpoint_calls:
        ordinary = accepted_ordinary_by_step.get(call["script_step_id"])
        if ordinary is None or call["sequence"] <= ordinary["sequence"]:
            _fail(
                "scenario-condition-topology-mismatch",
                "checkpoint attempts must follow an accepted ordinary turn for the same script step",
                {"sequence": call["sequence"], "script_step_id": call["script_step_id"]},
            )
        step_index = step_positions[call["script_step_id"]]
        if step_index + 1 < len(script_step_ids):
            next_ordinary = accepted_ordinary_by_step.get(script_step_ids[step_index + 1])
            if next_ordinary is not None and call["sequence"] >= next_ordinary["sequence"]:
                _fail(
                    "scenario-condition-topology-mismatch",
                    "checkpoint attempts must finish before the next scripted ordinary turn",
                    {"sequence": call["sequence"], "script_step_id": call["script_step_id"]},
                )

    continuation_records = [
        item for item in ordinary_calls
        if item["continuation_checkpoint_id"] is not None
    ]
    if condition == "forward-only":
        if checkpoint_calls:
            _fail(
                "scenario-condition-topology-mismatch",
                "forward-only cells must not contain checkpoint invocations",
            )
        if any(item["managed_checkpoint_id"] is not None for item in invocations) or continuation_records:
            _fail(
                "scenario-condition-topology-mismatch",
                "forward-only cells cannot claim managed checkpoints or fresh-narrator capsules",
            )
        if len({item["context_id"] for item in invocations}) > 1:
            _fail(
                "scenario-condition-topology-mismatch",
                "forward-only requires one persistent declared context for the complete cell",
            )
        return

    grouped: dict[str, list[dict[str, Any]]] = {
        step_id: [] for step_id in checkpoint_step_ids
    }
    for item in checkpoint_calls:
        assert item["checkpoint_step_id"] is not None
        grouped[item["checkpoint_step_id"]].append(item)
    if completed and any(not grouped[step_id] for step_id in checkpoint_step_ids):
        _fail(
            "scenario-condition-topology-mismatch",
            "a completed retcon cell requires one invocation group for every designated checkpoint",
            {"missing": [step_id for step_id in checkpoint_step_ids if not grouped[step_id]]},
        )

    if condition in {"prompt-only-retcon", "lacuna-serial"}:
        if continuation_records:
            _fail(
                "scenario-condition-topology-mismatch",
                f"{condition} must continue in its persistent context rather than claiming a fresh-narrator capsule",
            )
        if len({item["context_id"] for item in invocations}) > 1:
            _fail(
                "scenario-condition-topology-mismatch",
                f"{condition} requires one persistent declared context for the complete cell",
            )

    managed_checkpoint_ids: dict[str, str] = {}
    completed_checkpoint_ids: dict[str, str] = {}
    for step_id, calls in grouped.items():
        if not calls:
            continue
        calls = sorted(calls, key=lambda item: item["sequence"])
        accepted = [item for item in calls if item["outcome"] == "accepted"]
        if condition == "prompt-only-retcon":
            if any(item["role"] != "monolithic-retcon" for item in calls):
                _fail(
                    "scenario-condition-topology-mismatch",
                    "prompt-only-retcon checkpoint calls must use only role monolithic-retcon",
                    {"step_id": step_id},
                )
            if any(item["managed_checkpoint_id"] is not None for item in calls):
                _fail(
                    "scenario-condition-topology-mismatch",
                    "prompt-only-retcon calls cannot claim a managed Lacuna checkpoint ID",
                    {"step_id": step_id},
                )
            if completed and len(accepted) != 1:
                _fail(
                    "scenario-condition-topology-mismatch",
                    "each completed prompt-only checkpoint requires exactly one accepted monolithic-retcon call",
                    {"step_id": step_id, "accepted": len(accepted)},
                )
            accepted_seen = False
            for call in calls:
                if accepted_seen:
                    _fail(
                        "scenario-condition-topology-mismatch",
                        "no monolithic checkpoint retry may follow its accepted output",
                        {"step_id": step_id},
                    )
                accepted_seen = call["outcome"] == "accepted"
            continue

        checkpoint_ids = {item["managed_checkpoint_id"] for item in calls}
        if None in checkpoint_ids or len(checkpoint_ids) != 1:
            _fail(
                "scenario-condition-topology-mismatch",
                "every attempt in one managed checkpoint group must name the same non-null managed_checkpoint_id",
                {
                    "step_id": step_id,
                    "checkpoint_ids": sorted(str(item) for item in checkpoint_ids),
                },
            )
        checkpoint_id = next(iter(checkpoint_ids))
        assert isinstance(checkpoint_id, str)
        managed_checkpoint_ids[step_id] = checkpoint_id

        if any(item["role"] not in RETCON_ROLES for item in calls):
            _fail(
                "scenario-condition-topology-mismatch",
                "managed checkpoint groups may contain only the four fixed retcon roles",
                {"step_id": step_id},
            )
        stage_index = 0
        for call in calls:
            role_index = RETCON_ROLES.index(call["role"])
            if stage_index >= len(RETCON_ROLES) or role_index != stage_index:
                _fail(
                    "scenario-condition-topology-mismatch",
                    "managed checkpoint attempts must stay on one role until acceptance, then advance exactly once",
                    {
                        "step_id": step_id,
                        "expected_role": (
                            RETCON_ROLES[stage_index]
                            if stage_index < len(RETCON_ROLES)
                            else None
                        ),
                        "actual_role": call["role"],
                    },
                )
            if call["outcome"] == "accepted":
                stage_index += 1

        role_to_accepted: dict[str, list[dict[str, Any]]] = {
            role: [item for item in accepted if item["role"] == role]
            for role in RETCON_ROLES
        }
        if completed and any(len(role_to_accepted[role]) != 1 for role in RETCON_ROLES):
            _fail(
                "scenario-condition-topology-mismatch",
                "each completed managed checkpoint requires exactly one accepted output per role",
                {
                    "step_id": step_id,
                    "accepted_counts": {
                        role: len(role_to_accepted[role]) for role in RETCON_ROLES
                    },
                },
            )
        accepted_complete = [
            role_to_accepted[role][0]
            for role in RETCON_ROLES
            if role_to_accepted[role]
        ]
        sequence_roles = [
            item["role"]
            for item in sorted(accepted_complete, key=lambda item: item["sequence"])
        ]
        expected_prefix = list(RETCON_ROLES[: len(sequence_roles)])
        if sequence_roles != expected_prefix:
            _fail(
                "scenario-condition-topology-mismatch",
                "accepted managed checkpoint roles must appear in generator/judge/compressor/verifier order",
                {"step_id": step_id, "actual": sequence_roles},
            )
        if len(accepted_complete) == len(RETCON_ROLES):
            completed_checkpoint_ids[step_id] = checkpoint_id

        if condition == "lacuna-role-separated":
            contexts_by_role = {
                role: {item["context_id"] for item in calls if item["role"] == role}
                for role in RETCON_ROLES
                if any(item["role"] == role for item in calls)
            }
            if any(len(contexts) != 1 for contexts in contexts_by_role.values()):
                _fail(
                    "scenario-condition-topology-mismatch",
                    "retries for one role must remain in that role's declared context",
                    {
                        "step_id": step_id,
                        "contexts_by_role": {
                            role: sorted(contexts)
                            for role, contexts in contexts_by_role.items()
                        },
                    },
                )
            role_contexts = [next(iter(contexts_by_role[role])) for role in contexts_by_role]
            if len(set(role_contexts)) != len(role_contexts):
                _fail(
                    "scenario-condition-topology-mismatch",
                    "lacuna-role-separated requires pairwise-distinct role context_id values",
                    {"step_id": step_id, "contexts": role_contexts},
                )
            first_sequence = calls[0]["sequence"]
            earlier_contexts = {
                item["context_id"]
                for item in invocations
                if item["sequence"] < first_sequence
            }
            if any(context in earlier_contexts for context in role_contexts):
                _fail(
                    "scenario-condition-topology-mismatch",
                    "role-separated checkpoint contexts must be fresh and cannot reuse the narrator or an earlier role context",
                    {"step_id": step_id, "contexts": role_contexts},
                )

    if len(set(managed_checkpoint_ids.values())) != len(managed_checkpoint_ids):
        _fail(
            "scenario-condition-topology-mismatch",
            "distinct managed checkpoint steps must retain distinct managed_checkpoint_id values",
            {"managed_checkpoint_ids": managed_checkpoint_ids},
        )

    if condition != "lacuna-role-separated":
        return

    current_narrator_context: str | None = None
    pending_checkpoint_id: str | None = None
    for step_id in script_step_ids:
        calls = sorted(ordinary_calls_by_step[step_id], key=lambda item: item["sequence"])
        if calls:
            contexts = {item["context_id"] for item in calls}
            if len(contexts) != 1:
                _fail(
                    "scenario-condition-topology-mismatch",
                    "all attempts for one ordinary turn must remain in one declared narrator context",
                    {"step_id": step_id, "contexts": sorted(contexts)},
                )
            context_id = next(iter(contexts))
            continuation_pairs = {
                (item["continuation_checkpoint_id"], item["continuation_capsule_sha256"])
                for item in calls
            }
            if pending_checkpoint_id is None:
                if continuation_pairs != {(None, None)}:
                    _fail(
                        "scenario-condition-topology-mismatch",
                        "a narrator may claim a continuation capsule only on the first turn after a completed managed checkpoint",
                        {"step_id": step_id},
                    )
                if current_narrator_context is None:
                    current_narrator_context = context_id
                elif context_id != current_narrator_context:
                    _fail(
                        "scenario-condition-topology-mismatch",
                        "ordinary turns between checkpoints must stay in one narrator context",
                        {
                            "step_id": step_id,
                            "expected_context": current_narrator_context,
                            "actual_context": context_id,
                        },
                    )
            else:
                checkpoint_ids = {pair[0] for pair in continuation_pairs}
                capsule_digests = {pair[1] for pair in continuation_pairs}
                if checkpoint_ids != {pending_checkpoint_id} or None in capsule_digests or len(capsule_digests) != 1:
                    _fail(
                        "scenario-condition-topology-mismatch",
                        "the first narrator after a role-separated checkpoint must receive one exact capsule bound to that checkpoint on every attempt",
                        {
                            "step_id": step_id,
                            "expected_checkpoint_id": pending_checkpoint_id,
                            "actual_pairs": sorted(str(pair) for pair in continuation_pairs),
                        },
                    )
                first_sequence = calls[0]["sequence"]
                prior_contexts = {
                    item["context_id"]
                    for item in invocations
                    if item["sequence"] < first_sequence
                }
                if context_id in prior_contexts:
                    _fail(
                        "scenario-condition-topology-mismatch",
                        "the first narrator after a role-separated checkpoint must use a fresh declared context",
                        {"step_id": step_id, "context_id": context_id},
                    )
                current_narrator_context = context_id
                pending_checkpoint_id = None

        if step_id in checkpoint_step_set and step_id in completed_checkpoint_ids:
            current_narrator_context = None
            pending_checkpoint_id = completed_checkpoint_ids[step_id]

def _execution_totals(invocations: list[dict[str, Any]]) -> dict[str, Any]:
    def total(field: str) -> tuple[int, bool]:
        values = [item[field] for item in invocations]
        complete = all(value is not None for value in values)
        return sum(int(value) for value in values if value is not None), complete

    duration, duration_complete = total("duration_ms")
    input_tokens, input_complete = total("input_tokens")
    output_tokens, output_complete = total("output_tokens")
    cost, cost_complete = total("cost_microusd")
    return {
        "invocation_count": len(invocations),
        "accepted_invocations": sum(item["outcome"] == "accepted" for item in invocations),
        "failed_invocations": sum(item["outcome"] == "failed" for item in invocations),
        "duration_ms": duration,
        "duration_complete": duration_complete,
        "input_tokens": input_tokens,
        "input_tokens_complete": input_complete,
        "output_tokens": output_tokens,
        "output_tokens_complete": output_complete,
        "cost_microusd": cost,
        "cost_complete": cost_complete,
    }


def _enforce_budget(
    totals: dict[str, Any],
    *,
    budget: dict[str, Any],
) -> None:
    if totals["invocation_count"] > budget["max_invocations_per_cell"]:
        _fail(
            "scenario-budget-exceeded",
            "cell invocation count exceeds the fixed capsule budget",
            {
                "actual": totals["invocation_count"],
                "limit": budget["max_invocations_per_cell"],
            },
        )
    mapping = {
        "max_duration_ms_per_cell": ("duration_ms", "duration_complete"),
        "max_input_tokens_per_cell": ("input_tokens", "input_tokens_complete"),
        "max_output_tokens_per_cell": ("output_tokens", "output_tokens_complete"),
        "max_cost_microusd_per_cell": ("cost_microusd", "cost_complete"),
    }
    for limit_field, (value_field, complete_field) in mapping.items():
        limit = budget[limit_field]
        if limit is None:
            continue
        if not totals[complete_field]:
            _fail(
                "scenario-budget-metric-missing",
                f"{limit_field} is fixed, so every invocation must declare {value_field}",
            )
        if totals[value_field] > limit:
            _fail(
                "scenario-budget-exceeded",
                f"cell {value_field} exceeds the fixed capsule budget",
                {"actual": totals[value_field], "limit": limit},
            )


def validate_scenario_cell_return(
    value: Any,
    *,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    cell: dict[str, Any],
    condition: str,
) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario cell return",
        fields=CELL_RETURN_FIELDS,
        code="bad-scenario-cell-return",
    )
    if document.get("event") != "lacuna.scenario.cell-return" or document.get("schema") != SCENARIO_CELL_RETURN_SCHEMA:
        _fail("bad-scenario-cell-return", "unsupported scenario cell return contract")
    expected_identity = (manifest["run_id"], capsule["capsule_id"], cell["label"])
    actual_identity = (
        document.get("run_id"),
        document.get("capsule_id"),
        document.get("cell_label"),
    )
    if actual_identity != expected_identity:
        _fail(
            "scenario-cell-return-identity-mismatch",
            "cell return identity does not match the active scenario cell",
            {"expected": expected_identity, "actual": actual_identity},
        )
    status = document.get("status")
    if status not in {"completed", "refused", "failed"}:
        _fail("bad-scenario-cell-return", "status must be completed, refused, or failed")
    try:
        transcript_values = require_list(document.get("transcript"), "transcript")
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
    if len(transcript_values) > len(capsule["script"]):
        _fail("bad-scenario-cell-return", "transcript cannot exceed the scripted step count")
    normalized_transcript: list[dict[str, Any]] = []
    for index, value_item in enumerate(transcript_values):
        item = _strict(
            value_item,
            label=f"transcript[{index}]",
            fields=TRANSCRIPT_ITEM_FIELDS,
            code="bad-scenario-cell-return",
        )
        expected_step = capsule["script"][index]["step_id"]
        if item.get("step_id") != expected_step:
            _fail(
                "bad-scenario-cell-return",
                "transcript steps must be an exact prefix of the capsule script",
                {"index": index, "expected": expected_step, "actual": item.get("step_id")},
            )
        try:
            narration = require_string(
                item.get("narration"),
                f"transcript[{index}].narration",
                max_len=200000,
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
        normalized_transcript.append({"step_id": expected_step, "narration": narration})
    if status == "completed" and len(normalized_transcript) != len(capsule["script"]):
        _fail(
            "bad-scenario-cell-return",
            "a completed cell must return narration for every scripted step",
        )

    try:
        invocation_values = require_list(document.get("invocations"), "invocations")
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
    if len(invocation_values) > 1000:
        _fail("bad-scenario-cell-return", "a cell return may retain at most 1000 invocations")
    checkpoint_steps = set(_checkpoint_step_ids(capsule))
    invocations = [
        _validate_invocation(
            item,
            index=index,
            capsule=capsule,
            checkpoint_steps=checkpoint_steps,
        )
        for index, item in enumerate(invocation_values)
    ]
    if status == "completed" and not any(item["outcome"] == "accepted" for item in invocations):
        _fail("bad-scenario-cell-return", "a completed cell requires at least one accepted invocation")
    _validate_condition_topology(
        condition=condition,
        capsule=capsule,
        invocations=invocations,
        transcript_step_ids=[item["step_id"] for item in normalized_transcript],
        completed=status == "completed",
    )
    totals = _execution_totals(invocations)
    _enforce_budget(totals, budget=capsule["budget"])

    failure_value = document.get("failure")
    if status == "completed":
        if failure_value is not None:
            _fail("bad-scenario-cell-return", "completed cells must have null failure")
        failure = None
    else:
        failure_doc = _strict(
            failure_value,
            label="failure",
            fields=FAILURE_FIELDS,
            code="bad-scenario-cell-return",
        )
        if failure_doc.get("class") not in SCENARIO_FAILURE_CLASSES:
            _fail("bad-scenario-cell-return", "failure.class is unsupported")
        try:
            failure_message = require_string(
                failure_doc.get("message"), "failure.message", max_len=10000
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-cell-return", str(exc)) from exc
        failure = {"class": failure_doc["class"], "message": failure_message}
    completed_at = _optional_string(
        document.get("completed_at"), "completed_at", max_len=128
    )
    operator_notes = _optional_string(
        document.get("operator_notes"), "operator_notes", max_len=20000
    )
    if document.get("declaration") != "host-declared":
        _fail("bad-scenario-cell-return", "declaration must be host-declared")
    if document.get("nonclaims") != CELL_RETURN_NONCLAIMS:
        _fail("bad-scenario-cell-return", "cell return nonclaims were changed")
    return {
        "event": "lacuna.scenario.cell-return",
        "schema": SCENARIO_CELL_RETURN_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": capsule["capsule_id"],
        "cell_label": cell["label"],
        "status": status,
        "transcript": normalized_transcript,
        "invocations": invocations,
        "failure": failure,
        "completed_at": completed_at,
        "operator_notes": operator_notes,
        "declaration": "host-declared",
        "nonclaims": list(CELL_RETURN_NONCLAIMS),
    }


def _observe_cell_cube(
    run_path: Path,
    manifest: dict[str, Any],
    cell: dict[str, Any],
) -> dict[str, Any]:
    expected_relative = f"cells/{cell['label']}/cube"
    if cell["cube_path"] != expected_relative:
        _fail(
            "scenario-cell-cube-path-mismatch",
            "cell cube path does not match its fixed run topology",
            {"cell_label": cell["label"]},
        )
    resolved = resolve_sidecar_member_directory(
        run_path,
        expected_relative,
        error_prefix="scenario-run",
        label="scenario cell cube",
    )
    with Cube.open(resolved) as cube:
        if cube.meta("cube_id") != manifest["seed"]["cube_id"]:
            _fail(
                "scenario-cell-cube-identity-mismatch",
                "cell cube no longer has the seed cube identity",
                {"cell_label": cell["label"]},
            )
        verification = cube.verify()
        if verification["overall_status"] != "pass":
            _fail(
                "scenario-cell-cube-verification-failed",
                "cell cube fails deterministic verification",
                {"cell_label": cell["label"], "verification": verification},
            )
        final_event_count = cube.event_count()
        return {
            "cube_id": cube.meta("cube_id"),
            "seed_head": manifest["seed"]["head"],
            "final_head": cube.head(),
            "seed_event_count": manifest["seed"]["event_count"],
            "final_event_count": final_event_count,
            "event_count_delta": final_event_count - manifest["seed"]["event_count"],
            "verification_sha256": _digest(
                verification, label="scenario cell verification"
            ),
            "overall_status": "pass",
        }


def _build_cell_receipt(
    *,
    run_path: Path,
    manifest: dict[str, Any],
    cell: dict[str, Any],
    cell_return: dict[str, Any],
    return_ref: dict[str, Any],
    observed_cube: dict[str, Any],
    accepted_at: str,
) -> dict[str, Any]:
    totals = _execution_totals(cell_return["invocations"])
    return {
        "event": "lacuna.scenario.cell-recorded",
        "schema": SCENARIO_CELL_RECEIPT_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": cell_return["capsule_id"],
        "cell_label": cell["label"],
        "assignment_sha256": manifest["assignment"]["sha256"],
        "driver_sha256": cell["driver"]["sha256"],
        "return_artifact": copy.deepcopy(return_ref),
        "return_sha256": _digest(cell_return, label="scenario cell return"),
        "transcript_sha256": _digest(
            cell_return["transcript"], label="scenario cell transcript"
        ),
        "observed_cube": observed_cube,
        "execution_totals": totals,
        "accepted_at": accepted_at,
        "nonclaims": list(CELL_RECEIPT_NONCLAIMS),
    }


def _validate_cell_receipt(
    value: Any,
    *,
    run_path: Path,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    cell: dict[str, Any],
    condition: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = _strict(
        value,
        label="scenario cell receipt",
        fields=RECEIPT_FIELDS,
        code="bad-scenario-cell-receipt",
    )
    if receipt.get("event") != "lacuna.scenario.cell-recorded" or receipt.get("schema") != SCENARIO_CELL_RECEIPT_SCHEMA:
        _fail("bad-scenario-cell-receipt", "unsupported scenario cell receipt contract")
    if (
        receipt.get("run_id") != manifest["run_id"]
        or receipt.get("capsule_id") != capsule["capsule_id"]
        or receipt.get("cell_label") != cell["label"]
    ):
        _fail("bad-scenario-cell-receipt", "cell receipt identity mismatch")
    if receipt.get("assignment_sha256") != manifest["assignment"]["sha256"] or receipt.get("driver_sha256") != cell["driver"]["sha256"]:
        _fail("bad-scenario-cell-receipt", "cell receipt authority digests mismatch")
    return_path = f"cells/{cell['label']}/40-cell-return.json"
    return_ref = _validate_ref(
        run_path,
        receipt.get("return_artifact"),
        expected_path=return_path,
        expected_schema=SCENARIO_CELL_RETURN_SCHEMA,
        expected_role="cell-operator",
        label="return_artifact",
    )
    cell_return_raw = _read_ref_json(run_path, return_ref, label="scenario cell return")
    cell_return = validate_scenario_cell_return(
        cell_return_raw,
        manifest=manifest,
        capsule=capsule,
        cell=cell,
        condition=condition,
    )
    if receipt.get("return_sha256") != _digest(cell_return, label="scenario cell return"):
        _fail("bad-scenario-cell-receipt", "return_sha256 mismatch")
    if receipt.get("transcript_sha256") != _digest(cell_return["transcript"], label="scenario cell transcript"):
        _fail("bad-scenario-cell-receipt", "transcript_sha256 mismatch")
    observed = _strict(
        receipt.get("observed_cube"),
        label="observed_cube",
        fields=OBSERVED_CUBE_FIELDS,
        code="bad-scenario-cell-receipt",
    )
    current_observed = _observe_cell_cube(run_path, manifest, cell)
    if observed != current_observed:
        _fail(
            "scenario-cell-frozen-state-mismatch",
            "recorded cell cube changed after its accepted receipt",
            {"cell_label": cell["label"]},
        )
    totals = _strict(
        receipt.get("execution_totals"),
        label="execution_totals",
        fields=EXECUTION_TOTAL_FIELDS,
        code="bad-scenario-cell-receipt",
    )
    expected_totals = _execution_totals(cell_return["invocations"])
    if totals != expected_totals:
        _fail("bad-scenario-cell-receipt", "execution totals do not match the retained invocation ledger")
    try:
        require_string(receipt.get("accepted_at"), "accepted_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-cell-receipt", str(exc)) from exc
    if receipt.get("nonclaims") != CELL_RECEIPT_NONCLAIMS:
        _fail("bad-scenario-cell-receipt", "cell receipt nonclaims were changed")
    return copy.deepcopy(receipt), cell_return


def _build_blind_packet(
    *,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    cell_returns: dict[str, dict[str, Any]],
    receipts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    created_at = max(receipt["accepted_at"] for receipt in receipts.values())
    cells = []
    for label in sorted(cell_returns):
        cell_return = cell_returns[label]
        receipt = receipts[label]
        cells.append(
            {
                "cell_label": label,
                "status": cell_return["status"],
                "transcript": copy.deepcopy(cell_return["transcript"]),
                "transcript_sha256": receipt["transcript_sha256"],
            }
        )
    return {
        "event": "lacuna.scenario.blind-rating-packet",
        "schema": SCENARIO_BLIND_PACKET_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": capsule["capsule_id"],
        "title": capsule["title"],
        "research_question": capsule["research_question"],
        "created_at": created_at,
        "rubric": copy.deepcopy(capsule["rating"]),
        "cells": cells,
        "instructions": [
            "Read only this packet while rating; do not inspect the scenario run, private drivers, assignment, or cell cubes.",
            "Score every dimension for every opaque cell label using the fixed integer scale.",
            "Assign unique preference ranks from 1 (best) through the number of cells.",
            "Ground comments in concrete transcript evidence and record uncertainty rather than guessing condition identity.",
        ],
        "nonclaims": list(BLIND_PACKET_NONCLAIMS),
    }


def _validate_blind_packet(
    value: Any,
    *,
    expected: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(
        value,
        label="blind rating packet",
        fields=BLIND_PACKET_FIELDS,
        code="bad-scenario-blind-packet",
    )
    for index, item in enumerate(document.get("cells") if isinstance(document.get("cells"), list) else []):
        _strict(
            item,
            label=f"cells[{index}]",
            fields=BLIND_CELL_FIELDS,
            code="bad-scenario-blind-packet",
        )
    if document != expected:
        _fail(
            "scenario-blind-packet-mismatch",
            "blind rating packet is not the deterministic transcript-only projection",
        )
    return copy.deepcopy(document)


def validate_scenario_rating(
    value: Any,
    *,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    blind_packet: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario rating",
        fields=RATING_FIELDS,
        code="bad-scenario-rating",
    )
    if document.get("event") != "lacuna.scenario.rating" or document.get("schema") != SCENARIO_RATING_SCHEMA:
        _fail("bad-scenario-rating", "unsupported scenario rating contract")
    if document.get("run_id") != manifest["run_id"] or document.get("capsule_id") != capsule["capsule_id"]:
        _fail("bad-scenario-rating", "rating identity does not match this scenario run")
    try:
        rating_id = require_id(document.get("rating_id"), "rating_id")
        rater_id = require_id(document.get("rater_id"), "rater_id")
        require_string(document.get("declared_at"), "declared_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-rating", str(exc)) from exc
    packet_digest = _digest(blind_packet, label="blind rating packet")
    if document.get("blind_packet_sha256") != packet_digest:
        _fail("bad-scenario-rating", "rating is not bound to the current blind packet")
    try:
        rating_values = require_list(document.get("ratings"), "ratings")
    except ValueError as exc:
        raise LacunaError("bad-scenario-rating", str(exc)) from exc
    labels = [cell["cell_label"] for cell in blind_packet["cells"]]
    if len(rating_values) != len(labels):
        _fail("bad-scenario-rating", "rating must score every blind cell exactly once")
    normalized_items: list[dict[str, Any]] = []
    seen_labels: list[str] = []
    ranks: list[int] = []
    scale_min = capsule["rating"]["scale_min"]
    scale_max = capsule["rating"]["scale_max"]
    for index, value_item in enumerate(rating_values):
        item = _strict(
            value_item,
            label=f"ratings[{index}]",
            fields=RATING_ITEM_FIELDS,
            code="bad-scenario-rating",
        )
        label = item.get("cell_label")
        if label != labels[index]:
            _fail(
                "bad-scenario-rating",
                "ratings must follow the blind packet's lexical cell order",
                {"index": index, "expected": labels[index], "actual": label},
            )
        scores = _strict(
            item.get("scores"),
            label=f"ratings[{index}].scores",
            fields=set(HUMAN_RATING_DIMENSIONS),
            code="bad-scenario-rating",
        )
        normalized_scores: dict[str, int] = {}
        for dimension in HUMAN_RATING_DIMENSIONS:
            score = _bounded_int(
                scores.get(dimension),
                f"ratings[{index}].scores.{dimension}",
                minimum=scale_min,
                maximum=scale_max,
                code="bad-scenario-rating",
            )
            assert isinstance(score, int)
            normalized_scores[dimension] = score
        rank = _bounded_int(
            item.get("preference_rank"),
            f"ratings[{index}].preference_rank",
            minimum=1,
            maximum=len(labels),
            code="bad-scenario-rating",
        )
        assert isinstance(rank, int)
        comments = _optional_string(
            item.get("comments"),
            f"ratings[{index}].comments",
            max_len=20000,
        )
        seen_labels.append(label)
        ranks.append(rank)
        normalized_items.append(
            {
                "cell_label": label,
                "scores": normalized_scores,
                "preference_rank": rank,
                "comments": comments,
            }
        )
    if seen_labels != labels or sorted(ranks) != list(range(1, len(labels) + 1)):
        _fail(
            "bad-scenario-rating",
            "cell labels must be exact and preference ranks must be unique 1..N",
        )
    if document.get("declaration") != "blind-packet-only":
        _fail("bad-scenario-rating", "declaration must be blind-packet-only")
    if document.get("nonclaims") != RATING_NONCLAIMS:
        _fail("bad-scenario-rating", "rating nonclaims were changed")
    return {
        "event": "lacuna.scenario.rating",
        "schema": SCENARIO_RATING_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": capsule["capsule_id"],
        "rating_id": rating_id,
        "rater_id": rater_id,
        "blind_packet_sha256": packet_digest,
        "ratings": normalized_items,
        "declared_at": document["declared_at"],
        "declaration": "blind-packet-only",
        "nonclaims": list(RATING_NONCLAIMS),
    }


def build_scenario_rating_template(
    manifest: dict[str, Any],
    blind_packet: dict[str, Any],
    *,
    rater_id: str = "rater.replace-me",
) -> dict[str, Any]:
    try:
        rater_id = require_id(rater_id, "rater_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-rating", str(exc)) from exc
    rubric = blind_packet["rubric"]
    return {
        "event": "lacuna.scenario.rating",
        "schema": SCENARIO_RATING_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": blind_packet["capsule_id"],
        "rating_id": new_id("rating"),
        "rater_id": rater_id,
        "blind_packet_sha256": _digest(blind_packet, label="blind rating packet"),
        "ratings": [
            {
                "cell_label": cell["cell_label"],
                "scores": {
                    dimension: rubric["scale_min"]
                    for dimension in HUMAN_RATING_DIMENSIONS
                },
                "preference_rank": index,
                "comments": None,
            }
            for index, cell in enumerate(blind_packet["cells"], start=1)
        ],
        "declared_at": utc_now(),
        "declaration": "blind-packet-only",
        "nonclaims": list(RATING_NONCLAIMS),
    }


def _rating_refs_sha256s(manifest: dict[str, Any]) -> list[str]:
    return [ref["sha256"] for ref in manifest["ratings"]]


def validate_scenario_masking_assessment(
    value: Any,
    *,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    blind_packet: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario masking assessment",
        fields=MASKING_FIELDS,
        code="bad-scenario-masking-assessment",
    )
    if (
        document.get("event") != "lacuna.scenario.masking-assessment"
        or document.get("schema") != SCENARIO_MASKING_SCHEMA
    ):
        _fail("bad-scenario-masking-assessment", "unsupported scenario masking assessment contract")
    if document.get("run_id") != manifest["run_id"] or document.get("capsule_id") != capsule["capsule_id"]:
        _fail("bad-scenario-masking-assessment", "masking assessment identity does not match this scenario run")
    try:
        masking_id = require_id(document.get("masking_id"), "masking_id")
        assessor_id = require_id(document.get("assessor_id"), "assessor_id")
        require_string(document.get("declared_at"), "declared_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-masking-assessment", str(exc)) from exc
    packet_digest = _digest(blind_packet, label="blind rating packet")
    if document.get("blind_packet_sha256") != packet_digest:
        _fail("bad-scenario-masking-assessment", "masking assessment is not bound to the current blind packet")
    primary_hashes = document.get("primary_rating_sha256s")
    if primary_hashes != _rating_refs_sha256s(manifest):
        _fail(
            "bad-scenario-masking-assessment",
            "masking assessment must bind the complete frozen primary-rating artifact list",
        )
    try:
        assessment_values = require_list(document.get("assessments"), "assessments")
    except ValueError as exc:
        raise LacunaError("bad-scenario-masking-assessment", str(exc)) from exc
    labels = [cell["cell_label"] for cell in blind_packet["cells"]]
    if len(assessment_values) != len(labels):
        _fail("bad-scenario-masking-assessment", "masking assessment must cover every blind cell exactly once")
    normalized_items: list[dict[str, Any]] = []
    for index, raw in enumerate(assessment_values):
        item = _strict(
            raw,
            label=f"assessments[{index}]",
            fields=MASKING_ITEM_FIELDS,
            code="bad-scenario-masking-assessment",
        )
        label = item.get("cell_label")
        if label != labels[index]:
            _fail(
                "bad-scenario-masking-assessment",
                "masking assessments must follow the blind packet's lexical cell order",
                {"index": index, "expected": labels[index], "actual": label},
            )
        guess = item.get("guessed_condition")
        if guess not in MASKING_GUESSES:
            _fail(
                "bad-scenario-masking-assessment",
                "guessed_condition must be one canonical condition or unknown",
                {"index": index, "actual": guess},
            )
        confidence = _bounded_int(
            item.get("confidence"),
            f"assessments[{index}].confidence",
            minimum=0,
            maximum=100,
            code="bad-scenario-masking-assessment",
        )
        assert isinstance(confidence, int)
        try:
            cues_raw = require_list(item.get("cues"), f"assessments[{index}].cues")
        except ValueError as exc:
            raise LacunaError("bad-scenario-masking-assessment", str(exc)) from exc
        if len(cues_raw) > 16:
            _fail("bad-scenario-masking-assessment", "at most 16 cue strings may be listed per cell")
        cues: list[str] = []
        for cue_index, cue in enumerate(cues_raw):
            try:
                cues.append(require_string(cue, f"assessments[{index}].cues[{cue_index}]", max_len=500))
            except ValueError as exc:
                raise LacunaError("bad-scenario-masking-assessment", str(exc)) from exc
        familiarity = item.get("familiarity")
        if familiarity not in MASKING_FAMILIARITY:
            _fail(
                "bad-scenario-masking-assessment",
                "familiarity must be none, low, medium, or high",
                {"index": index, "actual": familiarity},
            )
        recognized = _require_bool(
            item.get("recognized_method"),
            f"assessments[{index}].recognized_method",
            code="bad-scenario-masking-assessment",
        )
        notes = _optional_string(
            item.get("notes"),
            f"assessments[{index}].notes",
            max_len=4000,
        )
        normalized_items.append(
            {
                "cell_label": label,
                "guessed_condition": guess,
                "confidence": confidence,
                "cues": cues,
                "familiarity": familiarity,
                "recognized_method": recognized,
                "notes": notes,
            }
        )
    if document.get("declaration") != "post-primary-rating-blind-packet-only-method-assessment":
        _fail(
            "bad-scenario-masking-assessment",
            "declaration must be post-primary-rating-blind-packet-only-method-assessment",
        )
    if document.get("nonclaims") != MASKING_NONCLAIMS:
        _fail("bad-scenario-masking-assessment", "masking assessment nonclaims were changed")
    return {
        "event": "lacuna.scenario.masking-assessment",
        "schema": SCENARIO_MASKING_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": capsule["capsule_id"],
        "masking_id": masking_id,
        "assessor_id": assessor_id,
        "blind_packet_sha256": packet_digest,
        "primary_rating_sha256s": list(primary_hashes),
        "assessments": normalized_items,
        "declared_at": document["declared_at"],
        "declaration": "post-primary-rating-blind-packet-only-method-assessment",
        "nonclaims": list(MASKING_NONCLAIMS),
    }


def build_scenario_masking_template(
    manifest: dict[str, Any],
    blind_packet: dict[str, Any],
    *,
    assessor_id: str = "rater.replace-me",
) -> dict[str, Any]:
    try:
        assessor_id = require_id(assessor_id, "assessor_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-masking-assessment", str(exc)) from exc
    return {
        "event": "lacuna.scenario.masking-assessment",
        "schema": SCENARIO_MASKING_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": blind_packet["capsule_id"],
        "masking_id": new_id("mask"),
        "assessor_id": assessor_id,
        "blind_packet_sha256": _digest(blind_packet, label="blind rating packet"),
        "primary_rating_sha256s": _rating_refs_sha256s(manifest),
        "assessments": [
            {
                "cell_label": cell["cell_label"],
                "guessed_condition": "unknown",
                "confidence": 0,
                "cues": [],
                "familiarity": "none",
                "recognized_method": False,
                "notes": None,
            }
            for cell in blind_packet["cells"]
        ],
        "declared_at": utc_now(),
        "declaration": "post-primary-rating-blind-packet-only-method-assessment",
        "nonclaims": list(MASKING_NONCLAIMS),
    }


def _validate_unblind_gate(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    gate = _strict(
        value,
        label="unblind_gate",
        fields=UNBLIND_GATE_FIELDS,
        code="bad-scenario-run",
    )
    if gate.get("kind") != "scenario-bundle-child-unblind-gate.v1":
        _fail("bad-scenario-run", "unsupported scenario unblind gate kind")
    try:
        require_id(gate.get("bundle_id"), "unblind_gate.bundle_id")
        require_id(gate.get("block_id"), "unblind_gate.block_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    if gate.get("status") not in {"closed", "open"}:
        _fail("bad-scenario-run", "unblind gate status must be closed or open")
    if gate.get("status") == "closed":
        if gate.get("opened_at") is not None or gate.get("opening_sha256") is not None:
            _fail("bad-scenario-run", "closed unblind gate cannot have opening custody")
    else:
        try:
            require_string(gate.get("opened_at"), "unblind_gate.opened_at", max_len=128)
        except ValueError as exc:
            raise LacunaError("bad-scenario-run", str(exc)) from exc
        _require_sha256(gate.get("opening_sha256"), "unblind_gate.opening_sha256", code="bad-scenario-run")
    if gate.get("nonclaims") != UNBLIND_GATE_NONCLAIMS:
        _fail("bad-scenario-run", "unblind gate nonclaims were changed")
    return copy.deepcopy(gate)


def open_scenario_unblind_gate(
    value: str | Path,
    *,
    bundle_id: str,
    block_id: str,
    opening_sha256: str,
) -> dict[str, Any]:
    """Open a bundle-staged child run for unblinding.

    This is intentionally not exposed as a public standalone CLI command.  The
    scenario bundle parent calls it only after every block has been sealed and
    the bundle has durably entered unblinding.
    """
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        gate = _validate_unblind_gate(manifest.get("unblind_gate"))
        if gate is None:
            return manifest
        try:
            bundle_id = require_id(bundle_id, "bundle_id")
            block_id = require_id(block_id, "block_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-run", str(exc)) from exc
        _require_sha256(opening_sha256, "opening_sha256", code="bad-scenario-run")
        if gate["bundle_id"] != bundle_id or gate["block_id"] != block_id:
            _fail("scenario-unblind-gate-binding-mismatch", "unblind gate opening does not match this child")
        if gate["status"] == "open":
            if gate["opening_sha256"] != opening_sha256:
                _fail("scenario-unblind-gate-opening-mismatch", "unblind gate was opened with a different digest")
            return manifest
        manifest["unblind_gate"] = {
            **gate,
            "status": "open",
            "opened_at": utc_now(),
            "opening_sha256": opening_sha256,
        }
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(run_path, manifest)
        _write_manifest(run_path, manifest)
        return _audit_scenario_run_unlocked(run_path)


def _build_report(
    *,
    manifest: dict[str, Any],
    capsule: dict[str, Any],
    assignment: dict[str, Any],
    receipts: dict[str, dict[str, Any]],
    cell_returns: dict[str, dict[str, Any]],
    ratings: list[dict[str, Any]],
    masking_assessments: list[dict[str, Any]],
    contamination_scan: dict[str, Any] | None,
    unblinded_at: str,
) -> dict[str, Any]:
    if contamination_scan is None:
        _fail(
            "bad-scenario-report",
            "unblinded report requires the preregistered pre-rating contamination scan",
        )
    label_to_condition = {
        item["cell_label"]: item["condition"] for item in assignment["assignments"]
    }
    scan_by_label = {
        item["cell_label"]: item for item in contamination_scan["cell_summaries"]
    }
    contamination_cells: list[dict[str, Any]] = []
    cell_records: list[dict[str, Any]] = []
    mechanical: list[dict[str, Any]] = []
    for condition in SCENARIO_CONDITIONS:
        label = next(
            label for label, assigned in label_to_condition.items() if assigned == condition
        )
        receipt = receipts[label]
        cell_return = cell_returns[label]
        scan_cell = scan_by_label[label]
        cell_record = {
            "condition": condition,
            "cell_label": label,
            "status": cell_return["status"],
            "transcript_sha256": receipt["transcript_sha256"],
            "return_sha256": receipt["return_sha256"],
            "receipt_sha256": _digest(receipt, label="scenario cell receipt"),
            "contamination_status": scan_cell["status"],
            "contamination_unexpected_match_count": scan_cell[
                "unexpected_match_count"
            ],
        }
        contamination_cells.append(
            {
                "condition": condition,
                "cell_label": label,
                "status": scan_cell["status"],
                "own_canary_leaks": scan_cell["own_canary_leaks"],
                "foreign_canary_leaks": scan_cell["foreign_canary_leaks"],
                "unexpected_match_count": scan_cell["unexpected_match_count"],
            }
        )
        cell_records.append(cell_record)
        mechanical.append(
            {
                "condition": condition,
                "cell_label": label,
                "final_head": receipt["observed_cube"]["final_head"],
                "event_count_delta": receipt["observed_cube"]["event_count_delta"],
                "execution_totals": copy.deepcopy(receipt["execution_totals"]),
            }
        )

    dimension_summary: dict[str, dict[str, dict[str, int]]] = {
        dimension: {
            condition: {"score_sum": 0, "score_count": 0}
            for condition in SCENARIO_CONDITIONS
        }
        for dimension in HUMAN_RATING_DIMENSIONS
    }
    rank_summary = {
        condition: {"score_sum": 0, "score_count": 0}
        for condition in SCENARIO_CONDITIONS
    }
    for rating in ratings:
        for item in rating["ratings"]:
            condition = label_to_condition[item["cell_label"]]
            for dimension in HUMAN_RATING_DIMENSIONS:
                dimension_summary[dimension][condition]["score_sum"] += item["scores"][dimension]
                dimension_summary[dimension][condition]["score_count"] += 1
            rank_summary[condition]["score_sum"] += item["preference_rank"]
            rank_summary[condition]["score_count"] += 1
    confusion: dict[str, dict[str, dict[str, int]]] = {
        condition: {
            guess: {
                "guess_count": 0,
                "correct_guess_count": 0,
                "confidence_sum": 0,
                "recognized_method_count": 0,
            }
            for guess in MASKING_GUESSES
        }
        for condition in SCENARIO_CONDITIONS
    }
    correct_guess_count = 0
    nonunknown_guess_count = 0
    confidence_sum = 0
    for masking in masking_assessments:
        for item in masking["assessments"]:
            condition = label_to_condition[item["cell_label"]]
            guess = item["guessed_condition"]
            bucket = confusion[condition][guess]
            bucket["guess_count"] += 1
            bucket["confidence_sum"] += item["confidence"]
            confidence_sum += item["confidence"]
            if item["recognized_method"]:
                bucket["recognized_method_count"] += 1
            if guess != "unknown":
                nonunknown_guess_count += 1
            if guess == condition:
                correct_guess_count += 1
                bucket["correct_guess_count"] += 1
    return {
        "event": "lacuna.scenario.unblinded",
        "schema": SCENARIO_REPORT_SCHEMA,
        "run_id": manifest["run_id"],
        "capsule_id": capsule["capsule_id"],
        "title": capsule["title"],
        "research_question": capsule["research_question"],
        "assignment_sha256": manifest["assignment"]["sha256"],
        "blind_packet_sha256": manifest["blind_packet"]["sha256"],
        "contamination_scan_sha256": manifest["contamination_scan"]["sha256"],
        "contamination_summary": {
            "overall_status": contamination_scan["overall_status"],
            "unexpected_match_count": sum(
                item["occurrence_count"]
                for item in contamination_scan["unexpected_matches"]
            ),
            "cells": contamination_cells,
        },
        "rating_artifact_sha256s": [ref["sha256"] for ref in manifest["ratings"]],
        "masking_artifact_sha256s": [ref["sha256"] for ref in manifest["masking_assessments"]],
        "cell_records": cell_records,
        "mechanical_outcomes": mechanical,
        "human_rating_summary": {
            "dimensions": dimension_summary,
            "preference_rank": rank_summary,
        },
        "method_identifiability_summary": {
            "assessor_count": len(masking_assessments),
            "cell_count": len(masking_assessments) * len(SCENARIO_CONDITIONS),
            "correct_guess_count": correct_guess_count,
            "nonunknown_guess_count": nonunknown_guess_count,
            "confidence_sum": confidence_sum,
            "confusion": confusion,
        },
        "unblinded_at": unblinded_at,
        "separation": {
            "mechanical": "cube identity, deterministic verification, final head, and event-count delta derived by Lacuna",
            "host_declared": "provider/model/context/digest/timing/token/cost/failure invocation records supplied by the operator",
            "human": "blind integer ratings and preference ranks authored by declared raters",
            "masking": "post-primary-rating method guesses and cue reports are joined to true condition identity only after unblinding",
        },
        "nonclaims": list(REPORT_NONCLAIMS),
    }


def _validate_report(value: Any, *, expected: dict[str, Any]) -> dict[str, Any]:
    document = _strict(
        value,
        label="scenario report",
        fields=REPORT_FIELDS,
        code="bad-scenario-report",
    )
    for index, item in enumerate(document.get("cell_records") if isinstance(document.get("cell_records"), list) else []):
        _strict(
            item,
            label=f"cell_records[{index}]",
            fields=REPORT_CELL_FIELDS,
            code="bad-scenario-report",
        )
    for index, item in enumerate(document.get("mechanical_outcomes") if isinstance(document.get("mechanical_outcomes"), list) else []):
        mechanical = _strict(
            item,
            label=f"mechanical_outcomes[{index}]",
            fields=MECHANICAL_OUTCOME_FIELDS,
            code="bad-scenario-report",
        )
        _strict(
            mechanical.get("execution_totals"),
            label=f"mechanical_outcomes[{index}].execution_totals",
            fields=EXECUTION_TOTAL_FIELDS,
            code="bad-scenario-report",
        )
    contamination_summary = _strict(
        document.get("contamination_summary"),
        label="contamination_summary",
        fields=CONTAMINATION_SUMMARY_FIELDS,
        code="bad-scenario-report",
    )
    for index, item in enumerate(
        contamination_summary.get("cells")
        if isinstance(contamination_summary.get("cells"), list)
        else []
    ):
        _strict(
            item,
            label=f"contamination_summary.cells[{index}]",
            fields=CONTAMINATION_CELL_SUMMARY_FIELDS,
            code="bad-scenario-report",
        )
    summary = _strict(
        document.get("human_rating_summary"),
        label="human_rating_summary",
        fields=SUMMARY_FIELDS,
        code="bad-scenario-report",
    )
    dimensions = _strict(
        summary.get("dimensions"),
        label="human_rating_summary.dimensions",
        fields=set(HUMAN_RATING_DIMENSIONS),
        code="bad-scenario-report",
    )
    for dimension in HUMAN_RATING_DIMENSIONS:
        conditions = _strict(
            dimensions[dimension],
            label=f"human_rating_summary.dimensions.{dimension}",
            fields=set(SCENARIO_CONDITIONS),
            code="bad-scenario-report",
        )
        for condition in SCENARIO_CONDITIONS:
            _strict(
                conditions[condition],
                label=f"human_rating_summary.dimensions.{dimension}.{condition}",
                fields=SUMMARY_VALUE_FIELDS,
                code="bad-scenario-report",
            )
    ranks = _strict(
        summary.get("preference_rank"),
        label="human_rating_summary.preference_rank",
        fields=set(SCENARIO_CONDITIONS),
        code="bad-scenario-report",
    )
    for condition in SCENARIO_CONDITIONS:
        _strict(
            ranks[condition],
            label=f"human_rating_summary.preference_rank.{condition}",
            fields=SUMMARY_VALUE_FIELDS,
            code="bad-scenario-report",
        )
    masking_summary = _strict(
        document.get("method_identifiability_summary"),
        label="method_identifiability_summary",
        fields=METHOD_IDENTIFIABILITY_FIELDS,
        code="bad-scenario-report",
    )
    _strict(
        masking_summary.get("confusion"),
        label="method_identifiability_summary.confusion",
        fields=set(SCENARIO_CONDITIONS),
        code="bad-scenario-report",
    )
    for condition in SCENARIO_CONDITIONS:
        by_guess = _strict(
            masking_summary["confusion"][condition],
            label=f"method_identifiability_summary.confusion.{condition}",
            fields=set(MASKING_GUESSES),
            code="bad-scenario-report",
        )
        for guess in MASKING_GUESSES:
            _strict(
                by_guess[guess],
                label=f"method_identifiability_summary.confusion.{condition}.{guess}",
                fields=CONFUSION_VALUE_FIELDS,
                code="bad-scenario-report",
            )
    if document != expected:
        _fail(
            "scenario-report-mismatch",
            "unblinded report is not the deterministic join of retained experiment artifacts",
        )
    return copy.deepcopy(document)


def _read_manifest(run_path: Path) -> dict[str, Any]:
    return read_sidecar_json_object(
        run_path / RUN_MANIFEST_FILE,
        label="scenario run manifest",
        error_prefix="scenario-run",
        root_error_code="bad-scenario-run",
    )


def _audit_next(run_path: Path, manifest: dict[str, Any]) -> None:
    text = read_sidecar_text(
        run_path / NEXT_FILE,
        label="scenario next-action pointer",
        error_prefix="scenario-run",
    )
    expected = _render_next(manifest)
    if text != expected:
        _fail(
            "scenario-run-next-pointer-mismatch",
            "NEXT.md is missing, stale, or edited; run scenario recover after authoritative audit",
        )


def _register_invocation_custody(
    *,
    cell_label: str,
    invocations: list[dict[str, Any]],
    context_owners: dict[str, str],
    invocation_owners: dict[str, str],
) -> None:
    for invocation in invocations:
        context_id = invocation["context_id"]
        prior_context_owner = context_owners.get(context_id)
        if prior_context_owner is not None and prior_context_owner != cell_label:
            _fail(
                "scenario-cross-cell-context-reuse",
                "a declared model context_id cannot be reused across experimental conditions",
                {
                    "context_id": context_id,
                    "first_cell_label": prior_context_owner,
                    "second_cell_label": cell_label,
                },
            )
        context_owners[context_id] = cell_label
        invocation_id = invocation["invocation_id"]
        if invocation_id is not None:
            prior_invocation_owner = invocation_owners.get(invocation_id)
            if prior_invocation_owner is not None:
                _fail(
                    "scenario-duplicate-invocation-id",
                    "a non-null provider invocation_id must identify exactly one retained attempt",
                    {
                        "invocation_id": invocation_id,
                        "first_cell_label": prior_invocation_owner,
                        "second_cell_label": cell_label,
                    },
                )
            invocation_owners[invocation_id] = cell_label


def _preflight_candidate_invocation_separation(
    run_path: Path,
    manifest: dict[str, Any],
    *,
    cell_label: str,
    invocations: list[dict[str, Any]],
) -> None:
    context_owners: dict[str, str] = {}
    invocation_owners: dict[str, str] = {}
    for prior_cell in manifest["cells"]:
        if prior_cell["status"] != "recorded":
            continue
        receipt = _read_ref_json(
            run_path, prior_cell["result"], label="scenario cell receipt"
        )
        prior_return = _read_ref_json(
            run_path, receipt["return_artifact"], label="scenario cell return"
        )
        _register_invocation_custody(
            cell_label=prior_cell["label"],
            invocations=prior_return["invocations"],
            context_owners=context_owners,
            invocation_owners=invocation_owners,
        )
    _register_invocation_custody(
        cell_label=cell_label,
        invocations=invocations,
        context_owners=context_owners,
        invocation_owners=invocation_owners,
    )


def _audit_scenario_run_unlocked(
    run_path: Path,
    *,
    audit_next: bool = True,
    authority_path: Path | None = None,
) -> dict[str, Any]:
    authority_path = run_path if authority_path is None else Path(authority_path)
    manifest = _strict(
        _read_manifest(run_path),
        label="scenario run manifest",
        fields=MANIFEST_FIELDS,
        code="bad-scenario-run",
    )
    if manifest.get("event") != SCENARIO_RUN_EVENT or manifest.get("schema") != SCENARIO_RUN_SCHEMA:
        _fail("bad-scenario-run", "unsupported scenario run manifest")
    if manifest.get("project_version") != __version__:
        _fail(
            "scenario-run-version-mismatch",
            "scenario runs are interpreted only by their creating Lacuna version",
            {"created_by": manifest.get("project_version"), "runtime": __version__},
        )
    try:
        require_id(manifest.get("run_id"), "run_id")
        require_string(manifest.get("created_at"), "created_at", max_len=128)
        require_string(manifest.get("updated_at"), "updated_at", max_len=128)
        require_string(manifest.get("reference"), "reference", max_len=4096)
        require_string(
            manifest.get("resolved_seed_cube_path"),
            "resolved_seed_cube_path",
            max_len=4096,
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    if (
        manifest.get("run_path") != str(authority_path)
        or authority_path.name != manifest["run_id"]
    ):
        _fail("scenario-run-path-mismatch", "manifest path or run ID does not match its authority directory")
    if manifest.get("nonclaims") != SCENARIO_RUN_NONCLAIMS:
        _fail("bad-scenario-run", "scenario run nonclaims were changed")
    unblind_gate = _validate_unblind_gate(manifest.get("unblind_gate"))
    seed = _strict(
        manifest.get("seed"),
        label="seed",
        fields=MANIFEST_SEED_FIELDS,
        code="bad-scenario-run",
    )
    try:
        require_id(seed.get("cube_id"), "seed.cube_id")
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    _require_sha256(seed.get("head"), "seed.head", code="bad-scenario-run")
    _require_sha256(
        seed.get("snapshot_sha256"), "seed.snapshot_sha256", code="bad-scenario-run"
    )
    _bounded_int(
        seed.get("event_count"),
        "seed.event_count",
        minimum=1,
        code="bad-scenario-run",
    )

    capsule_ref = _validate_ref(
        run_path,
        manifest.get("capsule"),
        expected_path=CAPSULE_FILE,
        expected_schema=SCENARIO_CAPSULE_SCHEMA,
        expected_role="experiment-owner",
        label="capsule",
    )
    capsule = validate_scenario_capsule(
        _read_ref_json(run_path, capsule_ref, label="scenario capsule")
    )
    if capsule["seed"] != {"cube_id": seed["cube_id"], "head": seed["head"]}:
        _fail("scenario-seed-mismatch", "manifest seed and capsule seed disagree")
    assignment_ref = _validate_ref(
        run_path,
        manifest.get("assignment"),
        expected_path=ASSIGNMENT_FILE,
        expected_schema=SCENARIO_ASSIGNMENT_SCHEMA,
        expected_role="experiment-owner-private",
        label="assignment",
    )
    assignment = _validate_assignment(
        _read_ref_json(run_path, assignment_ref, label="scenario assignment"),
        run_id=manifest["run_id"],
        capsule=capsule,
    )
    contamination_plan_ref = _validate_ref(
        run_path,
        manifest.get("contamination_plan"),
        expected_path=CONTAMINATION_PLAN_FILE,
        expected_schema=SCENARIO_CONTAMINATION_PLAN_SCHEMA,
        expected_role="experiment-owner-private",
        label="contamination_plan",
    )
    contamination_plan = validate_scenario_contamination_plan(
        _read_ref_json(
            run_path, contamination_plan_ref, label="scenario contamination plan"
        )
    )
    expected_contamination_plan = build_scenario_contamination_plan(
        run_id=manifest["run_id"],
        capsule_id=capsule["capsule_id"],
        assignment=assignment,
        assignment_sha256=assignment_ref["sha256"],
        created_at=manifest["created_at"],
    )
    if contamination_plan != expected_contamination_plan:
        _fail(
            "scenario-contamination-plan-mismatch",
            "contamination plan is not the deterministic preregistration for this assignment",
        )
    assignment_by_label = {
        item["cell_label"]: item for item in assignment["assignments"]
    }

    try:
        cell_values = require_list(manifest.get("cells"), "cells")
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    if len(cell_values) != len(SCENARIO_CONDITIONS):
        _fail("bad-scenario-run", "scenario run must contain exactly four cells")
    cells: list[dict[str, Any]] = []
    receipts: dict[str, dict[str, Any]] = {}
    cell_returns: dict[str, dict[str, Any]] = {}
    declared_context_owners: dict[str, str] = {}
    declared_invocation_owners: dict[str, str] = {}
    seen_active = 0
    phase = "recorded"
    for index, value_item in enumerate(cell_values):
        cell = _strict(
            value_item,
            label=f"cells[{index}]",
            fields=CELL_FIELDS,
            code="bad-scenario-run",
        )
        assignment_item = assignment["assignments"][index]
        if cell.get("ordinal") != index + 1 or cell.get("label") != assignment_item["cell_label"]:
            _fail("scenario-run-cell-topology-mismatch", "cell order/label differs from committed assignment")
        if cell.get("status") not in CELL_STATUSES:
            _fail("bad-scenario-run", f"unsupported cell status {cell.get('status')!r}")
        if cell["status"] == "recorded":
            if phase != "recorded":
                _fail("scenario-run-cell-topology-mismatch", "recorded cells must form a prefix")
        elif cell["status"] == "active":
            seen_active += 1
            if seen_active > 1 or phase == "pending":
                _fail("scenario-run-cell-topology-mismatch", "at most one active cell may follow the recorded prefix")
            phase = "active"
        else:
            phase = "pending"
        expected_cube_path = f"cells/{cell['label']}/cube"
        if cell.get("cube_path") != expected_cube_path:
            _fail("scenario-run-cell-topology-mismatch", "cell cube path is not fixed")
        driver_path = f"cells/{cell['label']}/30-driver.json"
        driver_ref = _validate_ref(
            run_path,
            cell.get("driver"),
            expected_path=driver_path,
            expected_schema=SCENARIO_DRIVER_SCHEMA,
            expected_role="experiment-owner-private",
            label=f"cells[{index}].driver",
        )
        expected_driver = _build_driver(
            run_id=manifest["run_id"],
            run_path=authority_path,
            capsule=capsule,
            assignment=assignment_item,
            contamination_plan=contamination_plan,
        )
        _validate_driver(
            _read_ref_json(run_path, driver_ref, label="scenario cell driver"),
            expected=expected_driver,
        )
        expected_canary_text = filesystem_canary_text(
            contamination_plan, cell_label=cell["label"]
        )
        actual_canary_text = read_sidecar_text(
            run_path / "cells" / cell["label"] / FILESYSTEM_CANARY_FILE,
            label="scenario filesystem contamination canary",
            error_prefix="scenario-contamination",
        )
        if actual_canary_text != expected_canary_text:
            _fail(
                "scenario-contamination-source-mismatch",
                "filesystem contamination canary source was changed",
                {"cell_label": cell["label"]},
            )
        observed = _observe_cell_cube(run_path, manifest, cell)
        if cell["status"] == "pending":
            if (
                observed["final_head"] != seed["head"]
                or observed["final_event_count"] != seed["event_count"]
            ):
                _fail(
                    "scenario-pending-cell-contaminated",
                    "a pending cell changed before activation",
                    {"cell_label": cell["label"]},
                )
            if cell.get("result") is not None:
                _fail("bad-scenario-run", "pending cells cannot have a result")
        elif cell["status"] == "active":
            if cell.get("result") is not None:
                _fail("bad-scenario-run", "active cells cannot have a retained result")
        else:
            result_path = f"cells/{cell['label']}/50-cell-receipt.json"
            result_ref = _validate_ref(
                run_path,
                cell.get("result"),
                expected_path=result_path,
                expected_schema=SCENARIO_CELL_RECEIPT_SCHEMA,
                expected_role="lacuna-scenario-runner",
                label=f"cells[{index}].result",
            )
            receipt, cell_return = _validate_cell_receipt(
                _read_ref_json(run_path, result_ref, label="scenario cell receipt"),
                run_path=run_path,
                manifest=manifest,
                capsule=capsule,
                cell=cell,
                condition=assignment_item["condition"],
            )
            receipts[cell["label"]] = receipt
            cell_returns[cell["label"]] = cell_return
            _register_invocation_custody(
                cell_label=cell["label"],
                invocations=cell_return["invocations"],
                context_owners=declared_context_owners,
                invocation_owners=declared_invocation_owners,
            )
        cells.append(copy.deepcopy(cell))

    all_recorded = all(cell["status"] == "recorded" for cell in cells)
    contamination_scan: dict[str, Any] | None = None
    blind_packet: dict[str, Any] | None = None
    if all_recorded:
        scan_ref = _validate_ref(
            run_path,
            manifest.get("contamination_scan"),
            expected_path=CONTAMINATION_SCAN_FILE,
            expected_schema=SCENARIO_CONTAMINATION_SCAN_SCHEMA,
            expected_role="lacuna-scenario-runner-private",
            label="contamination_scan",
        )
        contamination_scan = authenticate_scenario_contamination_scan(
            run_path,
            _read_ref_json(
                run_path, scan_ref, label="scenario contamination scan"
            ),
            plan_value=contamination_plan,
        )
        blind_ref = _validate_ref(
            run_path,
            manifest.get("blind_packet"),
            expected_path=BLIND_PACKET_FILE,
            expected_schema=SCENARIO_BLIND_PACKET_SCHEMA,
            expected_role="lacuna-scenario-runner",
            label="blind_packet",
        )
        expected_blind = _build_blind_packet(
            manifest=manifest,
            capsule=capsule,
            cell_returns=cell_returns,
            receipts=receipts,
        )
        blind_packet = _validate_blind_packet(
            _read_ref_json(run_path, blind_ref, label="blind rating packet"),
            expected=expected_blind,
        )
    else:
        if manifest.get("contamination_scan") is not None:
            _fail(
                "bad-scenario-run",
                "contamination scan cannot exist before every cell is recorded",
            )
        if manifest.get("blind_packet") is not None:
            _fail(
                "bad-scenario-run",
                "blind packet cannot exist before every cell is recorded",
            )

    try:
        rating_refs_raw = require_list(manifest.get("ratings"), "ratings")
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    ratings: list[dict[str, Any]] = []
    rater_ids: set[str] = set()
    rating_ids: set[str] = set()
    if rating_refs_raw and blind_packet is None:
        _fail("bad-scenario-run", "ratings require a complete blind packet")
    for index, ref_value in enumerate(rating_refs_raw):
        expected_path_prefix = f"ratings/rating-{index + 1:04d}-"
        ref = _strict(
            ref_value,
            label=f"ratings[{index}]",
            fields=RATING_REF_FIELDS,
            code="bad-scenario-run",
        )
        if not isinstance(ref.get("path"), str) or not ref["path"].startswith(expected_path_prefix) or not ref["path"].endswith(".json"):
            _fail("scenario-run-path-mismatch", "rating path is not sequence-bound")
        _require_sha256(ref.get("sha256"), f"ratings[{index}].sha256", code="bad-scenario-run")
        if ref.get("schema") != SCENARIO_RATING_SCHEMA or ref.get("role") != "blind-rater":
            _fail("scenario-run-artifact-metadata-mismatch", "rating metadata mismatch")
        try:
            require_id(ref.get("rating_id"), f"ratings[{index}].rating_id")
            require_id(ref.get("rater_id"), f"ratings[{index}].rater_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-run", str(exc)) from exc
        if ref["rating_id"] in rating_ids or ref["rater_id"] in rater_ids:
            _fail("bad-scenario-run", "rating and rater IDs must be unique")
        rating_ids.add(ref["rating_id"])
        rater_ids.add(ref["rater_id"])
        assert blind_packet is not None
        rating = validate_scenario_rating(
            _read_ref_json(run_path, ref, label="scenario rating"),
            manifest=manifest,
            capsule=capsule,
            blind_packet=blind_packet,
        )
        if rating["rating_id"] != ref["rating_id"] or rating["rater_id"] != ref["rater_id"]:
            _fail("bad-scenario-run", "rating reference identity mismatch")
        ratings.append(rating)
    if len(ratings) > capsule["rating"]["rater_count"]:
        _fail("bad-scenario-run", "rating count exceeds the capsule's fixed rater count")

    try:
        masking_refs_raw = require_list(
            manifest.get("masking_assessments"), "masking_assessments"
        )
    except ValueError as exc:
        raise LacunaError("bad-scenario-run", str(exc)) from exc
    masking_assessments: list[dict[str, Any]] = []
    masking_ids: set[str] = set()
    assessor_ids: set[str] = set()
    if masking_refs_raw and len(ratings) != capsule["rating"]["rater_count"]:
        _fail("bad-scenario-run", "masking assessments require all primary ratings to be frozen first")
    for index, ref_value in enumerate(masking_refs_raw):
        expected_path_prefix = f"ratings/masking-{index + 1:04d}-"
        ref = _strict(
            ref_value,
            label=f"masking_assessments[{index}]",
            fields=MASKING_REF_FIELDS,
            code="bad-scenario-run",
        )
        if not isinstance(ref.get("path"), str) or not ref["path"].startswith(expected_path_prefix) or not ref["path"].endswith(".json"):
            _fail("scenario-run-path-mismatch", "masking assessment path is sequence-bound")
        _require_sha256(ref.get("sha256"), f"masking_assessments[{index}].sha256", code="bad-scenario-run")
        if ref.get("schema") != SCENARIO_MASKING_SCHEMA or ref.get("role") != "blind-rater-post-primary-masking":
            _fail("scenario-run-artifact-metadata-mismatch", "masking assessment metadata mismatch")
        try:
            require_id(ref.get("masking_id"), f"masking_assessments[{index}].masking_id")
            require_id(ref.get("assessor_id"), f"masking_assessments[{index}].assessor_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-run", str(exc)) from exc
        if ref["masking_id"] in masking_ids or ref["assessor_id"] in assessor_ids:
            _fail("bad-scenario-run", "masking IDs and assessor IDs must be unique")
        if ref["assessor_id"] not in rater_ids:
            _fail("bad-scenario-run", "masking assessor IDs must match retained primary rater IDs")
        masking_ids.add(ref["masking_id"])
        assessor_ids.add(ref["assessor_id"])
        assert blind_packet is not None
        masking = validate_scenario_masking_assessment(
            _read_ref_json(run_path, ref, label="scenario masking assessment"),
            manifest=manifest,
            capsule=capsule,
            blind_packet=blind_packet,
        )
        if masking["masking_id"] != ref["masking_id"] or masking["assessor_id"] != ref["assessor_id"]:
            _fail("bad-scenario-run", "masking assessment reference identity mismatch")
        masking_assessments.append(masking)
    if len(masking_assessments) > capsule["rating"]["rater_count"]:
        _fail("bad-scenario-run", "masking assessment count exceeds the capsule's fixed rater count")

    report: dict[str, Any] | None = None
    if manifest.get("report") is not None:
        if len(ratings) != capsule["rating"]["rater_count"]:
            _fail("bad-scenario-run", "report requires every fixed blind rating")
        if len(masking_assessments) != capsule["rating"]["rater_count"]:
            _fail("bad-scenario-run", "report requires every fixed post-rating masking assessment")
        unblinded_at = manifest.get("unblinded_at")
        try:
            unblinded_at = require_string(unblinded_at, "unblinded_at", max_len=128)
        except ValueError as exc:
            raise LacunaError("bad-scenario-run", str(exc)) from exc
        report_ref = _validate_ref(
            run_path,
            manifest.get("report"),
            expected_path=REPORT_FILE,
            expected_schema=SCENARIO_REPORT_SCHEMA,
            expected_role="lacuna-scenario-runner",
            label="report",
        )
        assert blind_packet is not None
        expected_report = _build_report(
            manifest=manifest,
            capsule=capsule,
            assignment=assignment,
            receipts=receipts,
            cell_returns=cell_returns,
            ratings=ratings,
            masking_assessments=masking_assessments,
            contamination_scan=contamination_scan,
            unblinded_at=unblinded_at,
        )
        report = _validate_report(
            _read_ref_json(run_path, report_ref, label="scenario report"),
            expected=expected_report,
        )
    elif manifest.get("unblinded_at") is not None:
        _fail("bad-scenario-run", "unblinded_at requires a report")

    if report is not None:
        expected_status = "unblinded"
    elif all_recorded and len(masking_assessments) == capsule["rating"]["rater_count"]:
        expected_status = "ready-to-unblind"
    elif all_recorded and len(ratings) == capsule["rating"]["rater_count"]:
        expected_status = "awaiting-masking"
    elif all_recorded:
        expected_status = "awaiting-ratings"
    else:
        expected_status = "collecting-results"
    if unblind_gate is not None and unblind_gate["status"] == "open" and expected_status not in {"ready-to-unblind", "unblinded"}:
        _fail("bad-scenario-run", "unblind gate cannot be opened before ratings and masking are complete")
    if manifest.get("status") != expected_status:
        _fail(
            "scenario-run-state-mismatch",
            "manifest status does not match retained cell/rating/report topology",
            {"expected": expected_status, "actual": manifest.get("status")},
        )
    if manifest["status"] not in RUN_STATUSES:
        _fail("bad-scenario-run", "unsupported run status")
    expected_next = _next_action(authority_path, manifest)
    next_action = _strict(
        manifest.get("next_action"),
        label="next_action",
        fields=NEXT_ACTION_FIELDS,
        code="bad-scenario-run",
    )
    if next_action != expected_next:
        _fail("scenario-run-next-action-mismatch", "next_action is not deterministic")
    if audit_next:
        _audit_next(run_path, manifest)
    return copy.deepcopy(manifest)


def audit_scenario_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        return _audit_scenario_run_unlocked(run_path)


def recover_scenario_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path, audit_next=False)
        atomic_write_text(run_path / NEXT_FILE, _render_next(manifest))
        return _audit_scenario_run_unlocked(run_path)


def scenario_contamination_scan(value: str | Path) -> dict[str, Any]:
    """Return the authenticated preregistered scan after all cells are frozen."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["contamination_scan"] is None:
            _fail(
                "scenario-contamination-scan-not-ready",
                "contamination scan becomes available only after all four cell results are frozen",
                {"status": manifest["status"]},
            )
        plan = validate_scenario_contamination_plan(
            _read_ref_json(
                run_path,
                manifest["contamination_plan"],
                label="scenario contamination plan",
            )
        )
        return authenticate_scenario_contamination_scan(
            run_path,
            _read_ref_json(
                run_path,
                manifest["contamination_scan"],
                label="scenario contamination scan",
            ),
            plan_value=plan,
        )


def scenario_contamination_scan_markdown(value: str | Path) -> str:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["contamination_scan"] is None:
            _fail(
                "scenario-contamination-scan-not-ready",
                "contamination scan becomes available only after all four cell results are frozen",
                {"status": manifest["status"]},
            )
        plan = validate_scenario_contamination_plan(
            _read_ref_json(
                run_path,
                manifest["contamination_plan"],
                label="scenario contamination plan",
            )
        )
        scan = authenticate_scenario_contamination_scan(
            run_path,
            _read_ref_json(
                run_path,
                manifest["contamination_scan"],
                label="scenario contamination scan",
            ),
            plan_value=plan,
        )
        return render_contamination_scan_markdown(scan, plan_value=plan)


def dispatch_scenario_cell(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "collecting-results":
            _fail(
                "scenario-run-not-collecting-results",
                "only a collecting scenario can dispatch a cell",
                {"status": manifest["status"]},
            )
        active = [cell for cell in manifest["cells"] if cell["status"] == "active"]
        if active:
            cell = active[0]
        else:
            pending = [cell for cell in manifest["cells"] if cell["status"] == "pending"]
            if not pending:
                _fail("scenario-run-no-pending-cell", "scenario has no pending cell")
            cell = pending[0]
            cell["status"] = "active"
            manifest["updated_at"] = utc_now()
            manifest["next_action"] = _next_action(run_path, manifest)
            _write_manifest(run_path, manifest)
            manifest = _audit_scenario_run_unlocked(run_path)
            cell = next(item for item in manifest["cells"] if item["status"] == "active")
        return _read_ref_json(run_path, cell["driver"], label="scenario cell driver")


def record_scenario_cell(
    value: str | Path,
    cell_return_value: dict[str, Any],
) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "collecting-results":
            _fail(
                "scenario-run-not-collecting-results",
                "only a collecting scenario can accept a cell return",
                {"status": manifest["status"]},
            )
        active = [cell for cell in manifest["cells"] if cell["status"] == "active"]
        if len(active) != 1:
            _fail(
                "scenario-run-no-active-cell",
                "dispatch exactly one cell before recording its return",
            )
        cell = active[0]
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assignment = _validate_assignment(
            _read_ref_json(run_path, manifest["assignment"], label="scenario assignment"),
            run_id=manifest["run_id"],
            capsule=capsule,
        )
        condition = next(
            item["condition"]
            for item in assignment["assignments"]
            if item["cell_label"] == cell["label"]
        )
        accepted = validate_scenario_cell_return(
            cell_return_value,
            manifest=manifest,
            capsule=capsule,
            cell=cell,
            condition=condition,
        )
        _preflight_candidate_invocation_separation(
            run_path,
            manifest,
            cell_label=cell["label"],
            invocations=accepted["invocations"],
        )
        observed = _observe_cell_cube(run_path, manifest, cell)
        accepted_at = utc_now()
        return_path = f"cells/{cell['label']}/40-cell-return.json"
        return_ref = _write_json_ref(
            run_path,
            relative_path=return_path,
            value=accepted,
            schema=SCENARIO_CELL_RETURN_SCHEMA,
            role="cell-operator",
        )
        receipt = _build_cell_receipt(
            run_path=run_path,
            manifest=manifest,
            cell=cell,
            cell_return=accepted,
            return_ref=return_ref,
            observed_cube=observed,
            accepted_at=accepted_at,
        )
        receipt_path = f"cells/{cell['label']}/50-cell-receipt.json"
        receipt_ref = _write_json_ref(
            run_path,
            relative_path=receipt_path,
            value=receipt,
            schema=SCENARIO_CELL_RECEIPT_SCHEMA,
            role="lacuna-scenario-runner",
        )
        cell["status"] = "recorded"
        cell["result"] = receipt_ref
        all_recorded = all(item["status"] == "recorded" for item in manifest["cells"])
        if all_recorded:
            contamination_plan = validate_scenario_contamination_plan(
                _read_ref_json(
                    run_path,
                    manifest["contamination_plan"],
                    label="scenario contamination plan",
                )
            )
            contamination_scan = build_scenario_contamination_scan(
                run_path, contamination_plan, scanned_at=accepted_at
            )
            manifest["contamination_scan"] = _write_json_ref(
                run_path,
                relative_path=CONTAMINATION_SCAN_FILE,
                value=contamination_scan,
                schema=SCENARIO_CONTAMINATION_SCAN_SCHEMA,
                role="lacuna-scenario-runner-private",
            )
            receipts: dict[str, dict[str, Any]] = {}
            returns: dict[str, dict[str, Any]] = {}
            for item in manifest["cells"]:
                result_ref = item["result"]
                assert isinstance(result_ref, dict)
                retained_receipt = _read_ref_json(
                    run_path, result_ref, label="scenario cell receipt"
                )
                return_ref_value = retained_receipt["return_artifact"]
                retained_return = _read_ref_json(
                    run_path, return_ref_value, label="scenario cell return"
                )
                receipts[item["label"]] = retained_receipt
                returns[item["label"]] = retained_return
            blind_packet = _build_blind_packet(
                manifest=manifest,
                capsule=capsule,
                cell_returns=returns,
                receipts=receipts,
            )
            manifest["blind_packet"] = _write_json_ref(
                run_path,
                relative_path=BLIND_PACKET_FILE,
                value=blind_packet,
                schema=SCENARIO_BLIND_PACKET_SCHEMA,
                role="lacuna-scenario-runner",
            )
            manifest["status"] = "awaiting-ratings"
        manifest["updated_at"] = accepted_at
        manifest["next_action"] = _next_action(run_path, manifest)
        _write_manifest(run_path, manifest)
        return _audit_scenario_run_unlocked(run_path)


def scenario_rating_template(value: str | Path, *, rater_id: str = "rater.replace-me") -> dict[str, Any]:
    """Return the exact blind-rating contract for an audited awaiting-ratings run."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "awaiting-ratings":
            _fail(
                "scenario-run-not-awaiting-ratings",
                "a rating template is available only after every cell result and before the fixed rating count is complete",
                {"status": manifest["status"]},
            )
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assert manifest["blind_packet"] is not None
        blind_packet = _read_ref_json(
            run_path, manifest["blind_packet"], label="blind rating packet"
        )
        return build_scenario_rating_template(
            manifest, blind_packet, rater_id=rater_id
        )


def record_scenario_rating(
    value: str | Path,
    rating_value: dict[str, Any],
) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "awaiting-ratings":
            _fail(
                "scenario-run-not-awaiting-ratings",
                "ratings are accepted only after every cell result and before unblinding",
                {"status": manifest["status"]},
            )
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assert manifest["blind_packet"] is not None
        blind_packet = _read_ref_json(
            run_path, manifest["blind_packet"], label="blind rating packet"
        )
        rating = validate_scenario_rating(
            rating_value,
            manifest=manifest,
            capsule=capsule,
            blind_packet=blind_packet,
        )
        if any(ref["rater_id"] == rating["rater_id"] for ref in manifest["ratings"]):
            _fail(
                "duplicate-scenario-rater",
                "one rater_id may submit only one complete rating artifact",
                {"rater_id": rating["rater_id"]},
            )
        if any(ref["rating_id"] == rating["rating_id"] for ref in manifest["ratings"]):
            _fail(
                "duplicate-scenario-rating",
                "rating_id is already retained",
                {"rating_id": rating["rating_id"]},
            )
        sequence = len(manifest["ratings"]) + 1
        relative_path = f"ratings/rating-{sequence:04d}-{rating['rating_id']}.json"
        ref = _write_json_ref(
            run_path,
            relative_path=relative_path,
            value=rating,
            schema=SCENARIO_RATING_SCHEMA,
            role="blind-rater",
        )
        ref["rating_id"] = rating["rating_id"]
        ref["rater_id"] = rating["rater_id"]
        manifest["ratings"].append(ref)
        if len(manifest["ratings"]) == capsule["rating"]["rater_count"]:
            manifest["status"] = "awaiting-masking"
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(run_path, manifest)
        _write_manifest(run_path, manifest)
        return _audit_scenario_run_unlocked(run_path)


def scenario_masking_template(value: str | Path, *, assessor_id: str = "rater.replace-me") -> dict[str, Any]:
    """Return the exact post-primary-rating method-identifiability contract."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "awaiting-masking":
            _fail(
                "scenario-run-not-awaiting-masking",
                "a masking template is available only after every primary blind rating is frozen and before unblinding",
                {"status": manifest["status"]},
            )
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assert manifest["blind_packet"] is not None
        blind_packet = _read_ref_json(
            run_path, manifest["blind_packet"], label="blind rating packet"
        )
        return build_scenario_masking_template(
            manifest, blind_packet, assessor_id=assessor_id
        )


def record_scenario_masking(
    value: str | Path,
    masking_value: dict[str, Any],
) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        if manifest["status"] != "awaiting-masking":
            _fail(
                "scenario-run-not-awaiting-masking",
                "masking assessments are accepted only after every primary blind rating is frozen and before unblinding",
                {"status": manifest["status"]},
            )
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assert manifest["blind_packet"] is not None
        blind_packet = _read_ref_json(
            run_path, manifest["blind_packet"], label="blind rating packet"
        )
        masking = validate_scenario_masking_assessment(
            masking_value,
            manifest=manifest,
            capsule=capsule,
            blind_packet=blind_packet,
        )
        rater_ids = {ref["rater_id"] for ref in manifest["ratings"]}
        if masking["assessor_id"] not in rater_ids:
            _fail(
                "scenario-masking-assessor-not-primary-rater",
                "masking assessor_id must match one retained primary rater_id",
                {"assessor_id": masking["assessor_id"]},
            )
        if any(ref["assessor_id"] == masking["assessor_id"] for ref in manifest["masking_assessments"]):
            _fail(
                "duplicate-scenario-masking-assessor",
                "one assessor_id may submit only one masking assessment",
                {"assessor_id": masking["assessor_id"]},
            )
        if any(ref["masking_id"] == masking["masking_id"] for ref in manifest["masking_assessments"]):
            _fail(
                "duplicate-scenario-masking-assessment",
                "masking_id is already retained",
                {"masking_id": masking["masking_id"]},
            )
        sequence = len(manifest["masking_assessments"]) + 1
        relative_path = f"ratings/masking-{sequence:04d}-{masking['masking_id']}.json"
        ref = _write_json_ref(
            run_path,
            relative_path=relative_path,
            value=masking,
            schema=SCENARIO_MASKING_SCHEMA,
            role="blind-rater-post-primary-masking",
        )
        ref["masking_id"] = masking["masking_id"]
        ref["assessor_id"] = masking["assessor_id"]
        manifest["masking_assessments"].append(ref)
        if len(manifest["masking_assessments"]) == capsule["rating"]["rater_count"]:
            manifest["status"] = "ready-to-unblind"
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(run_path, manifest)
        _write_manifest(run_path, manifest)
        return _audit_scenario_run_unlocked(run_path)


def unblind_scenario_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_scenario_run_unlocked(run_path)
        gate = _validate_unblind_gate(manifest.get("unblind_gate"))
        if gate is not None and gate["status"] != "open":
            _fail(
                "scenario-unblind-gate-closed",
                "bundle-staged child scenario cannot be unblinded until the bundle opens its digest-bound gate",
            )
        if manifest["status"] == "unblinded":
            assert manifest["report"] is not None
            return _read_ref_json(run_path, manifest["report"], label="scenario report")
        if manifest["status"] != "ready-to-unblind":
            _fail(
                "scenario-run-not-ready-to-unblind",
                "all required blind ratings and masking assessments must be frozen before unblinding",
                {"status": manifest["status"]},
            )
        capsule = validate_scenario_capsule(
            _read_ref_json(run_path, manifest["capsule"], label="scenario capsule")
        )
        assignment = _validate_assignment(
            _read_ref_json(run_path, manifest["assignment"], label="scenario assignment"),
            run_id=manifest["run_id"],
            capsule=capsule,
        )
        receipts: dict[str, dict[str, Any]] = {}
        returns: dict[str, dict[str, Any]] = {}
        for cell in manifest["cells"]:
            receipt = _read_ref_json(run_path, cell["result"], label="scenario cell receipt")
            receipts[cell["label"]] = receipt
            returns[cell["label"]] = _read_ref_json(
                run_path, receipt["return_artifact"], label="scenario cell return"
            )
        ratings = [
            _read_ref_json(run_path, ref, label="scenario rating")
            for ref in manifest["ratings"]
        ]
        masking_assessments = [
            _read_ref_json(run_path, ref, label="scenario masking assessment")
            for ref in manifest["masking_assessments"]
        ]
        contamination_plan = validate_scenario_contamination_plan(
            _read_ref_json(
                run_path,
                manifest["contamination_plan"],
                label="scenario contamination plan",
            )
        )
        contamination_scan = authenticate_scenario_contamination_scan(
            run_path,
            _read_ref_json(
                run_path,
                manifest["contamination_scan"],
                label="scenario contamination scan",
            ),
            plan_value=contamination_plan,
        )
        unblinded_at = utc_now()
        report = _build_report(
            manifest=manifest,
            capsule=capsule,
            assignment=assignment,
            receipts=receipts,
            cell_returns=returns,
            ratings=ratings,
            masking_assessments=masking_assessments,
            contamination_scan=contamination_scan,
            unblinded_at=unblinded_at,
        )
        manifest["report"] = _write_json_ref(
            run_path,
            relative_path=REPORT_FILE,
            value=report,
            schema=SCENARIO_REPORT_SCHEMA,
            role="lacuna-scenario-runner",
        )
        manifest["unblinded_at"] = unblinded_at
        manifest["status"] = "unblinded"
        manifest["updated_at"] = unblinded_at
        manifest["next_action"] = _next_action(run_path, manifest)
        _write_manifest(run_path, manifest)
        _audit_scenario_run_unlocked(run_path)
        return report


def scenario_driver_markdown(driver: dict[str, Any]) -> str:
    lines = [
        "# Lacuna comparative scenario cell",
        "",
        "**Private operator handoff: do not share this document with blind raters.**",
        "",
        f"- Opaque cell: `{driver['cell_label']}`",
        f"- Condition: **{driver['condition']}**",
        f"- Cell cube: `{driver['resolved_cube_path']}`",
        f"- Provider/model: **{driver['model_policy']['provider']} / {driver['model_policy']['model']}**",
        f"- Sampling seed: **{driver['model_policy']['sampling_seed'] if driver['model_policy']['sampling_seed'] is not None else 'unavailable / null'}**",
        f"- Checkpoint mode: **{driver['condition_contract']['checkpoint_mode']}**",
        "",
        "## Preregistered contamination controls",
        "",
        f"- Operator-only token: `{driver['contamination_controls']['operator_canary']['token']}`",
        f"- Filesystem-only source: `{driver['contamination_controls']['filesystem_canary']['path']}`",
        f"- Filesystem token SHA-256: `{driver['contamination_controls']['filesystem_canary']['token_sha256']}`",
        "",
        "Keep this complete driver at the private cell-coordinator boundary. For delegated roles, transmit only the minimum generated card or prompt; never forward the driver to a blind rater.",
        "",
        "## Instructions",
        "",
    ]
    lines.extend(
        f"{index}. {instruction}"
        for index, instruction in enumerate(driver["instructions"], start=1)
    )
    lines.extend(["", "## Script", ""])
    for step in driver["script"]:
        lines.extend(
            [
                f"### {step['step_id']}",
                "",
                step["player_input"],
                "",
                f"Checkpoint after step: **{str(step['checkpoint_after']).lower()}**",
            ]
        )
        if step["checkpoint_trigger"] is not None:
            lines.append(f"Trigger: {step['checkpoint_trigger']}")
        lines.append("")
    lines.extend(
        [
            "## Exact return",
            "",
            f"Return one `{SCENARIO_CELL_RETURN_SCHEMA}` JSON object. Start from this template:",
            "",
            "```json",
            pretty_json(driver["return_contract"]["template"]),
            "```",
            "",
            "Then record it with:",
            "",
            "```bash",
            driver["return_contract"]["record_command"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def scenario_run_markdown(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    recorded = sum(cell["status"] == "recorded" for cell in manifest["cells"])
    lines = [
        "# Lacuna comparative scenario",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Path: `{manifest['run_path']}`",
        f"- Status: **{manifest['status']}**",
        f"- Cells recorded: **{recorded}/{len(manifest['cells'])}**",
        f"- Blind ratings recorded: **{len(manifest['ratings'])}**",
        f"- Assignment commitment: `{manifest['assignment']['sha256']}`",
        f"- Contamination plan: `{manifest['contamination_plan']['sha256']}`",
        f"- Contamination scan: `{manifest['contamination_scan']['sha256'] if manifest['contamination_scan'] is not None else 'pending'}`",
        "",
        "## Next action",
        "",
        f"Owner: **{action['owner']}**",
        "",
        action["action"],
    ]
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.append("")
    return "\n".join(lines)


def scenario_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Lacuna comparative scenario — unblinded descriptive report",
        "",
        report["research_question"],
        "",
        "## Condition cells",
        "",
        "| Condition | Opaque label | Status | Event delta | Invocations | Canary scan |",
        "|---|---|---:|---:|---:|---:|",
    ]
    mechanical_by_condition = {
        item["condition"]: item for item in report["mechanical_outcomes"]
    }
    for record in report["cell_records"]:
        mechanical = mechanical_by_condition[record["condition"]]
        lines.append(
            f"| {record['condition']} | `{record['cell_label']}` | {record['status']} | "
            f"{mechanical['event_count_delta']} | {mechanical['execution_totals']['invocation_count']} | "
            f"{record['contamination_status']} ({record['contamination_unexpected_match_count']}) |"
        )
    lines.extend(
        [
            "",
            f"Contamination scan overall status: **{report['contamination_summary']['overall_status']}** with **{report['contamination_summary']['unexpected_match_count']}** unexpected exact-token occurrence(s).",
            "",
            "Human scores remain integer sums and counts in the JSON report; they are not automatically converted into causal claims or objective utilities.",
            "",
        ]
    )
    return "\n".join(lines)

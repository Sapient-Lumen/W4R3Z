from __future__ import annotations

import copy
import csv
import io
import os
from pathlib import Path, PurePosixPath
from typing import Any, ContextManager

from . import __version__
from .errors import LacunaError
from .scenarios import (
    ASSIGNMENT_FILE,
    HUMAN_RATING_DIMENSIONS,
    SCENARIO_CELL_RETURN_SCHEMA,
    SCENARIO_CONDITIONS,
    SCENARIO_DRIVER_SCHEMA,
    SCENARIO_MASKING_SCHEMA,
    SCENARIO_RATING_SCHEMA,
    _audit_scenario_run_unlocked,
    _run_lock as _scenario_run_lock,
    dispatch_scenario_cell,
    record_scenario_cell,
    UNBLIND_GATE_NONCLAIMS,
    open_scenario_unblind_gate,
    record_scenario_masking,
    record_scenario_rating,
    scenario_masking_template,
    scenario_rating_template,
    stage_scenario_run,
    unblind_scenario_run,
    validate_scenario_capsule,
)
from .sidecars import (
    canonical_json_digest,
    ensure_sidecar_lock,
    make_private_directory,
    publish_private_directory,
    read_sidecar_json_object,
    read_sidecar_text,
    resolve_sidecar_directory,
    resolve_sidecar_member_directory,
    shell_command,
    sidecar_lock,
    write_sidecar_json_once_or_verify,
)
from .store import Cube
from .util import (
    SHA256_RE,
    atomic_write_json,
    atomic_write_text,
    new_id,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

BUNDLE_PLAN_SCHEMA = "lacuna.scenario-bundle-plan.v1"
BUNDLE_SCHEDULE_SCHEMA = "lacuna.scenario-bundle-schedule.v1"
BUNDLE_COMMITMENT_SCHEMA = "lacuna.scenario-bundle-commitment.v1"
BUNDLE_SCHEMA = "lacuna.scenario-bundle.v2"
BUNDLE_WITNESS_SCHEMA = "lacuna.scenario-bundle-witness.v1"
BUNDLE_BLOCK_SEAL_SCHEMA = "lacuna.scenario-bundle-block-seal.v3"
BUNDLE_REPORT_SCHEMA = "lacuna.scenario-bundle-report.v3"

BUNDLE_EVENT = "lacuna.scenario.bundle"
BUNDLE_MANIFEST_FILE = "bundle.json"
BUNDLE_NEXT_FILE = "NEXT.md"
BUNDLE_LOCK_FILE = ".bundle.lock"
PLAN_FILE = "10-preregistration.json"
SCHEDULE_FILE = "20-PRIVATE-schedule.json"
COMMITMENT_FILE = "30-public-commitment.json"
BUNDLE_REPORT_FILE = "90-bundle-report.json"

MAX_BUNDLE_WITNESSES = 64

BUNDLE_STATUSES = (
    "awaiting-witnesses",
    "block-active",
    "block-ready-to-seal",
    "ready-to-unblind",
    "unblinding",
    "unblinded",
)
BLOCK_STATUSES = ("pending", "active", "sealed", "unblinded")
WITNESS_KINDS = (
    "external-retention",
    "timestamp",
    "transparency-log",
    "signature",
    "human-cosignature",
    "other",
)

PLAN_FIELDS = {
    "schema",
    "bundle_id",
    "title",
    "research_question",
    "blocks",
    "registration",
    "witness_policy",
    "notes",
    "nonclaims",
}
PLAN_BLOCK_FIELDS = {
    "block_id",
    "reference",
    "resolved_seed_cube_path",
    "capsule",
    "story_stratum",
    "model_stratum",
    "replicate",
    "tags",
}
REGISTRATION_FIELDS = {
    "primary_dimensions",
    "primary_preference_rank",
    "block_inclusion",
    "terminal_failures",
    "analysis_unit",
    "ordinal_policy",
    "analysis_notes",
}
WITNESS_POLICY_FIELDS = {"minimum_receipts_before_execution"}
SCHEDULE_FIELDS = {
    "event",
    "schema",
    "bundle_id",
    "method",
    "randomization_seed",
    "blocks",
    "created_at",
    "nonclaims",
}
SCHEDULE_BLOCK_FIELDS = {
    "ordinal",
    "block_id",
    "block_label",
    "scenario_run_id",
    "assignment_seed",
}
ARTIFACT_REF_FIELDS = {"path", "sha256", "schema", "role"}
WITNESS_REF_FIELDS = ARTIFACT_REF_FIELDS | {"witness_id", "external_receipt_id"}
MANIFEST_FIELDS = {
    "event",
    "schema",
    "project_version",
    "bundle_id",
    "bundle_path",
    "created_at",
    "updated_at",
    "status",
    "plan",
    "schedule",
    "commitment",
    "blocks",
    "witnesses",
    "report",
    "unblinded_at",
    "next_action",
    "nonclaims",
}
MANIFEST_BLOCK_FIELDS = {
    "ordinal",
    "label",
    "block_id",
    "status",
    "scenario_run",
    "seal",
    "scenario_report_sha256",
}
RUN_BINDING_FIELDS = {
    "path",
    "run_id",
    "capsule_sha256",
    "assignment_sha256",
    "seed",
}
RUN_SEED_FIELDS = {"cube_id", "head", "event_count", "snapshot_sha256"}
NEXT_ACTION_FIELDS = {
    "owner",
    "action",
    "input_path",
    "expected_schema",
    "command",
    "blind",
}
COMMITMENT_FIELDS = {
    "event",
    "schema",
    "bundle_id",
    "plan_sha256",
    "schedule_sha256",
    "block_count",
    "blocks",
    "created_at",
    "hash_contract",
    "nonclaims",
}
COMMITMENT_BLOCK_FIELDS = {
    "ordinal",
    "block_id",
    "block_label",
    "scenario_run_id",
    "seed",
    "capsule_sha256",
    "assignment_sha256",
}
WITNESS_FIELDS = {
    "event",
    "schema",
    "bundle_id",
    "witness_id",
    "commitment_sha256",
    "kind",
    "service",
    "external_receipt_id",
    "external_receipt_sha256",
    "external_locator",
    "witnessed_at",
    "recorded_at",
    "declaration",
    "notes",
    "nonclaims",
}
SEAL_FIELDS = {
    "event",
    "schema",
    "bundle_id",
    "block_id",
    "block_label",
    "ordinal",
    "scenario_run_id",
    "scenario_run_path",
    "capsule_sha256",
    "assignment_sha256",
    "blind_packet_sha256",
    "contamination_scan_sha256",
    "rating_artifact_sha256s",
    "masking_artifact_sha256s",
    "sealed_at",
    "nonclaims",
}
REPORT_FIELDS = {
    "event",
    "schema",
    "bundle_id",
    "title",
    "research_question",
    "commitment_sha256",
    "witness_artifact_sha256s",
    "registration",
    "block_records",
    "observations",
    "descriptive_summary",
    "unblinded_at",
    "separation",
    "nonclaims",
}
REPORT_BLOCK_FIELDS = {
    "ordinal",
    "block_id",
    "story_stratum",
    "model_stratum",
    "replicate",
    "scenario_run_id",
    "capsule_sha256",
    "assignment_sha256",
    "contamination_scan_sha256",
    "contamination_status",
    "contamination_unexpected_match_count",
    "seal_sha256",
    "scenario_report_sha256",
    "rater_count",
    "included",
}
OBSERVATION_FIELDS = {
    "block_ordinal",
    "block_id",
    "story_stratum",
    "model_stratum",
    "replicate",
    "scenario_run_id",
    "rater_id",
    "condition",
    "cell_label",
    "cell_status",
    "contamination_status",
    "contamination_unexpected_match_count",
    "scores",
    "preference_rank",
    "method_guess",
    "method_guess_correct",
    "method_guess_confidence",
    "method_guess_recognized",
    "method_guess_familiarity",
    "method_guess_cues",
    "comments",
    "transcript_sha256",
    "final_head",
    "event_count_delta",
    "execution_totals",
}
SUMMARY_FIELDS = {"block_count", "observation_count", "dimensions", "preference_rank", "method_identifiability", "cell_status", "contamination"}
SUMMARY_VALUE_FIELDS = {"score_sum", "score_count"}
STATUS_COUNT_FIELDS = {"completed", "refused", "failed"}
CONTAMINATION_SUMMARY_FIELDS = {"clean_blocks", "leak_detected_blocks", "unexpected_match_count"}
METHOD_SUMMARY_FIELDS = {"assessor_count", "observation_count", "correct_guess_count", "nonunknown_guess_count", "confidence_sum"}

PLAN_NONCLAIMS = [
    "A bundle plan preregisters local block custody and descriptive endpoints; it is not a statistical power analysis, ethics review, or causal guarantee.",
    "Absolute seed paths are machine-local operator inputs. Bundle publication later contains exact child clones, but the plan itself is not portable across hosts.",
    "All scheduled blocks and terminal cell failures are retained; this contract intentionally provides no post hoc block-exclusion mechanism.",
]
SCHEDULE_NONCLAIMS = [
    "The private schedule fixes block order, scenario run identities, and assignment seeds before bundle execution.",
    "The host-generated master seed is not an external randomization oracle; a witness can retain the resulting commitment without proving randomness quality.",
    "Do not disclose this schedule to blind raters before bundle unblinding.",
]
COMMITMENT_NONCLAIMS = [
    "This artifact commits the exact private preregistration, schedule, seed boundaries, capsule digests, and assignment digests without revealing condition mappings.",
    "External retention can make later edits or whole-bundle disappearance detectable to that witness; Lacuna cannot prove that an unwitnessed earlier bundle never existed.",
    "SHA-256 custody detects retained-byte changes under canonical JSON; it does not prove truth, authorship, randomness, or provider independence.",
]
BUNDLE_NONCLAIMS = [
    "A scenario bundle is a private experiment sidecar containing precreated child runs; it is not story canon, a provider invoker, or a distributed transaction.",
    "All child assignments and exact seed clones publish together before execution, but a same-host owner can still discard the whole unpublished bundle unless an external party retains its commitment.",
    "Witness receipts are operator-supplied records. Lacuna binds them to the commitment but does not verify external signatures, timestamps, services, or locator availability.",
    "Declared model contexts and invocation IDs are checked for cross-block reuse; they remain host declarations rather than proof of fresh or independent provider memory.",
    "All blocks remain structurally blind until every scheduled block is sealed. Semantic method leakage through prose is still possible.",
    "Rater-level ordinal observations, host-declared execution measures, and Lacuna-derived cube outcomes remain separate evidence classes; no significance or causal claim is computed.",
    "The bundle lock coordinates cooperative same-host callers only and is not hostile-user, mount-namespace, or distributed confinement.",
]
WITNESS_NONCLAIMS = [
    "This is an operator-supplied description of an external receipt, not a Lacuna-verified signature, timestamp, transparency-log inclusion proof, or availability proof.",
    "The exact bundle commitment digest is bound; the external service's identity and semantics remain outside Lacuna's trust boundary.",
]
SEAL_NONCLAIMS = [
    "This seal freezes one child run at ready-to-unblind after every required blind rating is retained.",
    "Post-primary-rating masking assessments are frozen separately from primary ratings before this seal is issued.",
    "It prevents the bundle workflow from replacing or omitting that retained block or its preregistered contamination scan without detection; it does not prove provider or rater independence.",
]
REPORT_NONCLAIMS = [
    "The report includes every preregistered block and terminal cell failure; it performs no post hoc exclusion, significance test, multiplicity correction, or causal estimation.",
    "Integer scores and preference ranks are exported at rater level and summarized only by sums and counts; sums are descriptive and are not asserted to be interval utility.",
    "Provider, model, context, timing, token, cost, and failure records remain host declarations unless independently attested.",
    "Exact seed cloning controls durable Lacuna state, not hidden provider prompts, system state, tools, model updates, or external memory.",
    "Exact canary findings are retained as falsification evidence; clean scans do not prove isolation or forgetting.",
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
        _fail(code, f"{label} has an invalid field set", {"unexpected": unexpected, "missing": missing})
    return document


def _digest(value: Any, *, label: str) -> str:
    return canonical_json_digest(value, error_code="bad-scenario-bundle-artifact", label=label)


def _require_sha256(value: Any, field: str, *, code: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(code, f"{field} must be a lowercase SHA-256 digest")
    return value


def _bounded_int(value: Any, field: str, *, minimum: int, maximum: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum or value > maximum:
        _fail(code, f"{field} must be an integer between {minimum} and {maximum}")
    return value


def _optional_string(value: Any, field: str, *, max_len: int = 4096) -> str | None:
    if value is None:
        return None
    try:
        return require_string(value, field, allow_empty=True, max_len=max_len)
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-artifact", str(exc)) from exc


def _artifact_ref(*, path: str, value: dict[str, Any], schema: str, role: str) -> dict[str, Any]:
    return {"path": path, "sha256": _digest(value, label=path), "schema": schema, "role": role}


def _write_json_ref(
    root: Path,
    *,
    relative_path: str,
    value: dict[str, Any],
    schema: str,
    role: str,
) -> dict[str, Any]:
    atomic_write_json(root / PurePosixPath(relative_path), value)
    return _artifact_ref(path=relative_path, value=value, schema=schema, role=role)


def _validate_ref(
    value: Any,
    *,
    expected_path: str,
    expected_schema: str,
    expected_role: str,
    label: str,
    fields: set[str] = ARTIFACT_REF_FIELDS,
) -> dict[str, Any]:
    document = _strict(value, label=label, fields=fields, code="bad-scenario-bundle")
    if document.get("path") != expected_path:
        _fail("scenario-bundle-path-mismatch", f"{label}.path must be {expected_path!r}")
    _require_sha256(document.get("sha256"), f"{label}.sha256", code="bad-scenario-bundle")
    if document.get("schema") != expected_schema or document.get("role") != expected_role:
        _fail("scenario-bundle-artifact-metadata-mismatch", f"{label} metadata does not match its fixed contract")
    return document


def _read_ref_json(root: Path, ref: dict[str, Any], *, label: str) -> dict[str, Any]:
    document = read_sidecar_json_object(
        root / PurePosixPath(ref["path"]),
        label=label,
        error_prefix="scenario-bundle",
        root_error_code="bad-scenario-bundle-artifact",
    )
    if _digest(document, label=label) != ref["sha256"]:
        _fail("scenario-bundle-artifact-digest-mismatch", f"{label} no longer matches its retained digest", {"path": ref["path"]})
    return document


def _read_child_ref(run_path: Path, ref: dict[str, Any], *, label: str) -> dict[str, Any]:
    document = read_sidecar_json_object(
        run_path / PurePosixPath(ref["path"]),
        label=label,
        error_prefix="scenario-bundle-child",
        root_error_code="bad-scenario-bundle-child-artifact",
    )
    if _digest(document, label=label) != ref["sha256"]:
        _fail("scenario-bundle-child-artifact-digest-mismatch", f"{label} no longer matches the child run digest")
    return document


def build_scenario_bundle_plan(
    blocks: list[dict[str, Any]],
    *,
    title: str = "Replicated retcon-planning comparison",
    research_question: str = "Across preregistered blocks, how do forward-only, prompt-only retcon, Lacuna serial, and Lacuna role-separated continuations compare?",
    primary_dimensions: list[str] | None = None,
    minimum_receipts_before_execution: int = 0,
    notes: str | None = None,
) -> dict[str, Any]:
    try:
        title = require_string(title, "title", max_len=512)
        research_question = require_string(research_question, "research_question", max_len=4000)
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
    if primary_dimensions is None:
        primary_dimensions = [
            "agency",
            "coincidence_restraint",
            "mystery_fairness",
            "seam_invisibility",
        ]
    normalized_blocks: list[dict[str, Any]] = []
    for index, raw in enumerate(blocks):
        try:
            source = require_mapping(raw, f"blocks[{index}]")
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        capsule = validate_scenario_capsule(source.get("capsule"))
        reference = source.get("reference")
        resolved = source.get("resolved_seed_cube_path")
        try:
            reference = require_string(reference, f"blocks[{index}].reference", max_len=4096)
            resolved = require_string(resolved, f"blocks[{index}].resolved_seed_cube_path", max_len=4096)
            story = require_string(
                source.get("story_stratum", capsule["capsule_id"]),
                f"blocks[{index}].story_stratum",
                max_len=512,
            )
            model = require_string(
                source.get("model_stratum", f"{capsule['model_policy']['model_family']}::{capsule['model_policy']['model']}"),
                f"blocks[{index}].model_stratum",
                max_len=512,
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        replicate = source.get("replicate", index + 1)
        if isinstance(replicate, bool) or not isinstance(replicate, int) or replicate < 1:
            _fail("bad-scenario-bundle-plan", f"blocks[{index}].replicate must be a positive integer")
        tags = source.get("tags", [])
        try:
            tags = require_list(tags, f"blocks[{index}].tags")
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        normalized_tags: list[str] = []
        for tag_index, tag in enumerate(tags):
            try:
                normalized_tags.append(require_id(tag, f"blocks[{index}].tags[{tag_index}]"))
            except ValueError as exc:
                raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        normalized_blocks.append(
            {
                "block_id": source.get("block_id") or new_id("blk"),
                "reference": reference,
                "resolved_seed_cube_path": str(Path(resolved).expanduser().resolve()),
                "capsule": capsule,
                "story_stratum": story,
                "model_stratum": model,
                "replicate": replicate,
                "tags": normalized_tags,
            }
        )
    plan = {
        "schema": BUNDLE_PLAN_SCHEMA,
        "bundle_id": new_id("bnd"),
        "title": title,
        "research_question": research_question,
        "blocks": normalized_blocks,
        "registration": {
            "primary_dimensions": list(primary_dimensions),
            "primary_preference_rank": True,
            "block_inclusion": "all-scheduled-blocks",
            "terminal_failures": "include",
            "analysis_unit": "rater-by-condition-within-block",
            "ordinal_policy": "retain-integers-and-ranks-no-automatic-interval-or-significance-claim",
            "analysis_notes": None,
        },
        "witness_policy": {
            "minimum_receipts_before_execution": minimum_receipts_before_execution,
        },
        "notes": notes,
        "nonclaims": list(PLAN_NONCLAIMS),
    }
    return validate_scenario_bundle_plan(plan)


def validate_scenario_bundle_plan(value: Any) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle plan", fields=PLAN_FIELDS, code="bad-scenario-bundle-plan")
    if document.get("schema") != BUNDLE_PLAN_SCHEMA:
        _fail("bad-scenario-bundle-plan", "unsupported scenario bundle plan schema")
    try:
        bundle_id = require_id(document.get("bundle_id"), "bundle_id")
        title = require_string(document.get("title"), "title", max_len=512)
        question = require_string(document.get("research_question"), "research_question", max_len=4000)
        blocks_raw = require_list(document.get("blocks"), "blocks")
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
    if len(blocks_raw) < 2 or len(blocks_raw) > 128:
        _fail("bad-scenario-bundle-plan", "blocks must contain between 2 and 128 preregistered blocks")
    blocks: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(blocks_raw):
        item = _strict(raw, label=f"blocks[{index}]", fields=PLAN_BLOCK_FIELDS, code="bad-scenario-bundle-plan")
        try:
            block_id = require_id(item.get("block_id"), f"blocks[{index}].block_id")
            reference = require_string(item.get("reference"), f"blocks[{index}].reference", max_len=4096)
            resolved = require_string(item.get("resolved_seed_cube_path"), f"blocks[{index}].resolved_seed_cube_path", max_len=4096)
            story = require_string(item.get("story_stratum"), f"blocks[{index}].story_stratum", max_len=512)
            model = require_string(item.get("model_stratum"), f"blocks[{index}].model_stratum", max_len=512)
            tags_raw = require_list(item.get("tags"), f"blocks[{index}].tags")
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        if block_id in seen_ids:
            _fail("bad-scenario-bundle-plan", "block_id values must be unique", {"block_id": block_id})
        seen_ids.add(block_id)
        path = Path(resolved)
        if not path.is_absolute() or str(path) != resolved:
            _fail("bad-scenario-bundle-plan", f"blocks[{index}].resolved_seed_cube_path must be one normalized absolute path")
        replicate = _bounded_int(item.get("replicate"), f"blocks[{index}].replicate", minimum=1, maximum=1000000, code="bad-scenario-bundle-plan")
        tags: list[str] = []
        for tag_index, tag in enumerate(tags_raw):
            try:
                tags.append(require_id(tag, f"blocks[{index}].tags[{tag_index}]"))
            except ValueError as exc:
                raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
        if len(tags) != len(set(tags)):
            _fail("bad-scenario-bundle-plan", f"blocks[{index}].tags must be unique")
        blocks.append(
            {
                "block_id": block_id,
                "reference": reference,
                "resolved_seed_cube_path": resolved,
                "capsule": validate_scenario_capsule(item.get("capsule")),
                "story_stratum": story,
                "model_stratum": model,
                "replicate": replicate,
                "tags": tags,
            }
        )
    rating_contract = blocks[0]["capsule"]["rating"]
    for index, block in enumerate(blocks[1:], start=1):
        if block["capsule"]["rating"] != rating_contract:
            _fail(
                "scenario-bundle-rating-policy-mismatch",
                "every block must use the same fixed rating scale, prompts, and rater count",
                {"block_index": index},
            )
    registration = _strict(document.get("registration"), label="registration", fields=REGISTRATION_FIELDS, code="bad-scenario-bundle-plan")
    try:
        primary_raw = require_list(registration.get("primary_dimensions"), "registration.primary_dimensions")
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-plan", str(exc)) from exc
    if not primary_raw:
        _fail("bad-scenario-bundle-plan", "registration.primary_dimensions must not be empty")
    primary: list[str] = []
    for dimension in primary_raw:
        if dimension not in HUMAN_RATING_DIMENSIONS:
            _fail("bad-scenario-bundle-plan", f"unsupported primary rating dimension {dimension!r}")
        primary.append(dimension)
    if len(primary) != len(set(primary)):
        _fail("bad-scenario-bundle-plan", "primary rating dimensions must be unique")
    if registration.get("primary_preference_rank") is not True:
        _fail("bad-scenario-bundle-plan", "primary_preference_rank must be true in v1")
    fixed_registration = {
        "block_inclusion": "all-scheduled-blocks",
        "terminal_failures": "include",
        "analysis_unit": "rater-by-condition-within-block",
        "ordinal_policy": "retain-integers-and-ranks-no-automatic-interval-or-significance-claim",
    }
    for field, expected in fixed_registration.items():
        if registration.get(field) != expected:
            _fail("bad-scenario-bundle-plan", f"registration.{field} must be {expected!r}")
    analysis_notes = _optional_string(registration.get("analysis_notes"), "registration.analysis_notes", max_len=20000)
    witness_policy = _strict(document.get("witness_policy"), label="witness_policy", fields=WITNESS_POLICY_FIELDS, code="bad-scenario-bundle-plan")
    minimum = _bounded_int(
        witness_policy.get("minimum_receipts_before_execution"),
        "witness_policy.minimum_receipts_before_execution",
        minimum=0,
        maximum=MAX_BUNDLE_WITNESSES,
        code="bad-scenario-bundle-plan",
    )
    notes = _optional_string(document.get("notes"), "notes", max_len=20000)
    if document.get("nonclaims") != PLAN_NONCLAIMS:
        _fail("bad-scenario-bundle-plan", "bundle plan nonclaims were changed")
    return {
        "schema": BUNDLE_PLAN_SCHEMA,
        "bundle_id": bundle_id,
        "title": title,
        "research_question": question,
        "blocks": blocks,
        "registration": {
            "primary_dimensions": primary,
            "primary_preference_rank": True,
            **fixed_registration,
            "analysis_notes": analysis_notes,
        },
        "witness_policy": {"minimum_receipts_before_execution": minimum},
        "notes": notes,
        "nonclaims": list(PLAN_NONCLAIMS),
    }


def _build_schedule(plan: dict[str, Any], *, randomization_seed: str, created_at: str) -> dict[str, Any]:
    ordered = sorted(
        plan["blocks"],
        key=lambda block: (sha256_text(f"{randomization_seed}:block:{block['block_id']}"), block["block_id"]),
    )
    blocks: list[dict[str, Any]] = []
    for ordinal, block in enumerate(ordered, start=1):
        block_id = block["block_id"]
        blocks.append(
            {
                "ordinal": ordinal,
                "block_id": block_id,
                "block_label": "block_" + sha256_text(f"{randomization_seed}:label:{ordinal}:{block_id}")[:12],
                "scenario_run_id": "scr_" + sha256_text(f"{randomization_seed}:run:{block_id}")[:24],
                "assignment_seed": sha256_text(f"{randomization_seed}:assignment:{block_id}"),
            }
        )
    return {
        "event": "lacuna.scenario.bundle.schedule",
        "schema": BUNDLE_SCHEDULE_SCHEMA,
        "bundle_id": plan["bundle_id"],
        "method": "host-random-seed-sha256-sort-v1",
        "randomization_seed": randomization_seed,
        "blocks": blocks,
        "created_at": created_at,
        "nonclaims": list(SCHEDULE_NONCLAIMS),
    }


def _validate_schedule(value: Any, *, plan: dict[str, Any]) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle schedule", fields=SCHEDULE_FIELDS, code="bad-scenario-bundle-schedule")
    if document.get("event") != "lacuna.scenario.bundle.schedule" or document.get("schema") != BUNDLE_SCHEDULE_SCHEMA:
        _fail("bad-scenario-bundle-schedule", "unsupported scenario bundle schedule")
    if document.get("bundle_id") != plan["bundle_id"] or document.get("method") != "host-random-seed-sha256-sort-v1":
        _fail("bad-scenario-bundle-schedule", "schedule identity or method mismatch")
    seed = _require_sha256(document.get("randomization_seed"), "randomization_seed", code="bad-scenario-bundle-schedule")
    try:
        created_at = require_string(document.get("created_at"), "created_at", max_len=128)
        blocks_raw = require_list(document.get("blocks"), "blocks")
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-schedule", str(exc)) from exc
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(blocks_raw):
        item = _strict(raw, label=f"blocks[{index}]", fields=SCHEDULE_BLOCK_FIELDS, code="bad-scenario-bundle-schedule")
        try:
            block_id = require_id(item.get("block_id"), f"blocks[{index}].block_id")
            block_label = require_id(item.get("block_label"), f"blocks[{index}].block_label")
            run_id = require_id(item.get("scenario_run_id"), f"blocks[{index}].scenario_run_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-schedule", str(exc)) from exc
        normalized.append(
            {
                "ordinal": _bounded_int(item.get("ordinal"), f"blocks[{index}].ordinal", minimum=1, maximum=len(plan["blocks"]), code="bad-scenario-bundle-schedule"),
                "block_id": block_id,
                "block_label": block_label,
                "scenario_run_id": run_id,
                "assignment_seed": _require_sha256(item.get("assignment_seed"), f"blocks[{index}].assignment_seed", code="bad-scenario-bundle-schedule"),
            }
        )
    expected = _build_schedule(plan, randomization_seed=seed, created_at=created_at)
    if document != expected or normalized != expected["blocks"]:
        _fail("scenario-bundle-schedule-mismatch", "private block order and assignment seeds do not reconstruct from the committed master seed")
    return copy.deepcopy(expected)


def _build_commitment(
    *,
    plan_ref: dict[str, Any],
    schedule_ref: dict[str, Any],
    plan: dict[str, Any],
    blocks: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    return {
        "event": "lacuna.scenario.bundle.committed",
        "schema": BUNDLE_COMMITMENT_SCHEMA,
        "bundle_id": plan["bundle_id"],
        "plan_sha256": plan_ref["sha256"],
        "schedule_sha256": schedule_ref["sha256"],
        "block_count": len(blocks),
        "blocks": [
            {
                "ordinal": block["ordinal"],
                "block_id": block["block_id"],
                "block_label": block["label"],
                "scenario_run_id": block["scenario_run"]["run_id"],
                "seed": copy.deepcopy(block["scenario_run"]["seed"]),
                "capsule_sha256": block["scenario_run"]["capsule_sha256"],
                "assignment_sha256": block["scenario_run"]["assignment_sha256"],
            }
            for block in blocks
        ],
        "created_at": created_at,
        "hash_contract": "sha256-canonical-json-utf8-v1",
        "nonclaims": list(COMMITMENT_NONCLAIMS),
    }


def _validate_commitment(value: Any, *, expected: dict[str, Any]) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle commitment", fields=COMMITMENT_FIELDS, code="bad-scenario-bundle-commitment")
    blocks = document.get("blocks")
    if not isinstance(blocks, list):
        _fail("bad-scenario-bundle-commitment", "commitment.blocks must be an array")
    for index, item in enumerate(blocks):
        block = _strict(item, label=f"blocks[{index}]", fields=COMMITMENT_BLOCK_FIELDS, code="bad-scenario-bundle-commitment")
        _strict(block.get("seed"), label=f"blocks[{index}].seed", fields=RUN_SEED_FIELDS, code="bad-scenario-bundle-commitment")
    if document != expected:
        _fail("scenario-bundle-commitment-mismatch", "public commitment is not the deterministic digest join of the retained preregistration, schedule, and child run boundaries")
    return copy.deepcopy(document)


def begin_scenario_bundle(plan_value: dict[str, Any], *, root: str | Path) -> dict[str, Any]:
    plan = validate_scenario_bundle_plan(plan_value)
    root_path = Path(root).expanduser().resolve()
    try:
        root_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise LacunaError("scenario-bundle-create-failed", f"cannot create scenario bundle root {root_path}: {exc}") from exc
    if not root_path.is_dir():
        _fail("scenario-bundle-create-failed", f"scenario bundle root is not a directory: {root_path}")
    bundle_path = root_path / plan["bundle_id"]
    created_at = utc_now()
    schedule = _build_schedule(plan, randomization_seed=os.urandom(32).hex(), created_at=created_at)
    plan_by_id = {block["block_id"]: block for block in plan["blocks"]}

    with publish_private_directory(bundle_path, error_code="scenario-bundle-create-failed", kind_label="scenario bundle") as staging_path:
        ensure_sidecar_lock(staging_path, lock_file=BUNDLE_LOCK_FILE, error_prefix="scenario-bundle", kind_label="scenario bundle")
        plan_ref = _write_json_ref(staging_path, relative_path=PLAN_FILE, value=plan, schema=BUNDLE_PLAN_SCHEMA, role="experiment-owner")
        schedule_ref = _write_json_ref(staging_path, relative_path=SCHEDULE_FILE, value=schedule, schema=BUNDLE_SCHEDULE_SCHEMA, role="experiment-owner-private")
        make_private_directory(staging_path / "blocks")
        make_private_directory(staging_path / "witnesses")
        manifest_blocks: list[dict[str, Any]] = []
        child_manifests: dict[str, dict[str, Any]] = {}
        for schedule_item in schedule["blocks"]:
            plan_block = plan_by_id[schedule_item["block_id"]]
            label = schedule_item["block_label"]
            block_root = staging_path / "blocks" / label
            make_private_directory(block_root)
            runs_root = block_root / "scenario-runs"
            make_private_directory(runs_root)
            run_storage = runs_root / schedule_item["scenario_run_id"]
            make_private_directory(run_storage)
            run_relative = f"blocks/{label}/scenario-runs/{schedule_item['scenario_run_id']}"
            run_authority = bundle_path / PurePosixPath(run_relative)
            try:
                source_path = Path(plan_block["resolved_seed_cube_path"]).resolve(strict=True)
            except OSError as exc:
                raise LacunaError("scenario-bundle-seed-missing", f"cannot resolve block seed cube: {exc}", {"block_id": plan_block["block_id"]}) from exc
            if str(source_path) != plan_block["resolved_seed_cube_path"]:
                _fail("scenario-bundle-seed-path-mismatch", "block seed path changed after preregistration", {"block_id": plan_block["block_id"]})
            with Cube.open(source_path) as cube:
                verification = cube.verify()
                if verification["overall_status"] != "pass":
                    _fail("cube-verification-failed", "refusing to stage a bundle block from a cube that fails verification", {"block_id": plan_block["block_id"], "verification": verification})
                capsule = plan_block["capsule"]
                if capsule["seed"] != {"cube_id": cube.meta("cube_id"), "head": cube.head()}:
                    _fail("scenario-bundle-seed-mismatch", "block capsule does not match the exact preregistered seed boundary", {"block_id": plan_block["block_id"]})
                snapshot_sha256 = _digest(cube.snapshot(), label=f"bundle block {plan_block['block_id']} seed snapshot")
                child = stage_scenario_run(
                    cube,
                    capsule,
                    reference=f"bundle:{plan['bundle_id']}:{plan_block['block_id']}",
                    resolved_seed_cube_path=source_path,
                    storage_path=run_storage,
                    authority_path=run_authority,
                    run_id=schedule_item["scenario_run_id"],
                    created_at=created_at,
                    randomization_seed=schedule_item["assignment_seed"],
                    assignment_method="bundle-precommitted-seed-sha256-sort-v1",
                    snapshot_sha256=snapshot_sha256,
                    seed_event_count=cube.event_count(),
                    unblind_gate={
                        "kind": "scenario-bundle-child-unblind-gate.v1",
                        "bundle_id": plan["bundle_id"],
                        "block_id": plan_block["block_id"],
                        "status": "closed",
                        "opened_at": None,
                        "opening_sha256": None,
                        "nonclaims": list(UNBLIND_GATE_NONCLAIMS),
                    },
                )
            child_manifests[plan_block["block_id"]] = child
            manifest_blocks.append(
                {
                    "ordinal": schedule_item["ordinal"],
                    "label": label,
                    "block_id": plan_block["block_id"],
                    "status": "active" if schedule_item["ordinal"] == 1 else "pending",
                    "scenario_run": {
                        "path": run_relative,
                        "run_id": child["run_id"],
                        "capsule_sha256": child["capsule"]["sha256"],
                        "assignment_sha256": child["assignment"]["sha256"],
                        "seed": copy.deepcopy(child["seed"]),
                    },
                    "seal": None,
                    "scenario_report_sha256": None,
                }
            )
        commitment = _build_commitment(plan_ref=plan_ref, schedule_ref=schedule_ref, plan=plan, blocks=manifest_blocks, created_at=created_at)
        commitment_ref = _write_json_ref(staging_path, relative_path=COMMITMENT_FILE, value=commitment, schema=BUNDLE_COMMITMENT_SCHEMA, role="public-witness-input")
        status = "awaiting-witnesses" if plan["witness_policy"]["minimum_receipts_before_execution"] else "block-active"
        manifest: dict[str, Any] = {
            "event": BUNDLE_EVENT,
            "schema": BUNDLE_SCHEMA,
            "project_version": __version__,
            "bundle_id": plan["bundle_id"],
            "bundle_path": str(bundle_path),
            "created_at": created_at,
            "updated_at": created_at,
            "status": status,
            "plan": plan_ref,
            "schedule": schedule_ref,
            "commitment": commitment_ref,
            "blocks": manifest_blocks,
            "witnesses": [],
            "report": None,
            "unblinded_at": None,
            "next_action": {},
            "nonclaims": list(BUNDLE_NONCLAIMS),
        }
        _write_bundle_manifest(
            staging_path,
            manifest,
            authority_path=bundle_path,
            child_manifests=child_manifests,
        )
    return audit_scenario_bundle(bundle_path)


def _bundle_directory(value: str | Path) -> Path:
    return resolve_sidecar_directory(
        value,
        manifest_file=BUNDLE_MANIFEST_FILE,
        unknown_code="unknown-scenario-bundle",
        kind_label="scenario bundle",
    )


def _bundle_lock(bundle_path: Path) -> ContextManager[None]:
    return sidecar_lock(
        bundle_path,
        lock_file=BUNDLE_LOCK_FILE,
        error_prefix="scenario-bundle",
        kind_label="scenario bundle",
        busy_message="another process is already advancing this scenario bundle",
    )


def _render_next(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    lines = [
        "# Lacuna scenario bundle — next action",
        "",
        f"- Bundle: `{manifest['bundle_id']}`",
        f"- Status: **{manifest['status']}**",
        f"- Owner: **{action['owner']}**",
        f"- Blind handoff: **{'yes' if action['blind'] else 'no'}**",
        "",
        action["action"],
    ]
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["expected_schema"] is not None:
        lines.extend(["", f"Expected schema: `{action['expected_schema']}`"])
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.extend(
        [
            "",
            "`bundle.json` is authoritative. This file is a deterministic pointer and may be regenerated only after the complete bundle audits.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_bundle_manifest(
    storage_path: Path,
    manifest: dict[str, Any],
    *,
    authority_path: Path,
    child_manifests: dict[str, dict[str, Any]],
) -> None:
    manifest["next_action"] = _next_action(authority_path, manifest, child_manifests=child_manifests)
    atomic_write_json(storage_path / BUNDLE_MANIFEST_FILE, manifest)
    atomic_write_text(storage_path / BUNDLE_NEXT_FILE, _render_next(manifest))


def _next_action(
    bundle_path: Path,
    manifest: dict[str, Any],
    *,
    child_manifests: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    status = manifest["status"]
    if status == "awaiting-witnesses":
        return {
            "owner": "experiment-owner",
            "action": "Retain the public commitment with the required external witness or witnesses, then record each exact receipt before any child run is advanced.",
            "input_path": str(bundle_path / COMMITMENT_FILE),
            "expected_schema": BUNDLE_WITNESS_SCHEMA,
            "command": shell_command(
                [
                    "./lacuna",
                    "scenario",
                    "bundle",
                    "witness-template",
                    str(bundle_path),
                    "--witness-id",
                    "witness.replace-me",
                ]
            ),
            "blind": False,
        }
    if status == "block-active":
        active = [block for block in manifest["blocks"] if block["status"] == "active"]
        if len(active) != 1:
            _fail("bad-scenario-bundle", "block-active requires exactly one active block")
        block = active[0]
        child = child_manifests[block["block_id"]]
        child_action = child["next_action"]
        expected = child_action["expected_schema"]
        if expected == SCENARIO_DRIVER_SCHEMA:
            command = shell_command(["./lacuna", "scenario", "bundle", "dispatch", str(bundle_path), "--format", "markdown"])
        elif expected == SCENARIO_CELL_RETURN_SCHEMA:
            command = shell_command(["./lacuna", "scenario", "bundle", "record", str(bundle_path), "CELL_RETURN.json"])
        elif expected == SCENARIO_RATING_SCHEMA:
            command = shell_command(["./lacuna", "scenario", "bundle", "rate", str(bundle_path), "RATING.json"])
        elif expected == SCENARIO_MASKING_SCHEMA:
            command = shell_command(["./lacuna", "scenario", "bundle", "mask", str(bundle_path), "MASKING.json"])
        else:
            _fail("scenario-bundle-child-state-mismatch", "active child has an unsupported next-action contract", {"expected_schema": expected})
        return {
            "owner": child_action["owner"],
            "action": f"Advance preregistered block {block['ordinal']} of {len(manifest['blocks'])}: {child_action['action']}",
            "input_path": child_action["input_path"],
            "expected_schema": expected,
            "command": command,
            "blind": child_action["blind"],
        }
    if status == "block-ready-to-seal":
        active = [block for block in manifest["blocks"] if block["status"] == "active"]
        if len(active) != 1:
            _fail("bad-scenario-bundle", "block-ready-to-seal requires exactly one active block")
        block = active[0]
        return {
            "owner": "experiment-owner",
            "action": f"Every primary rating and post-rating masking assessment for block {block['ordinal']} is frozen. Seal the block without unblinding it; the next preregistered block will then become active.",
            "input_path": str(bundle_path / block["scenario_run"]["path"] / ASSIGNMENT_FILE),
            "expected_schema": BUNDLE_BLOCK_SEAL_SCHEMA,
            "command": shell_command(["./lacuna", "scenario", "bundle", "seal", str(bundle_path)]),
            "blind": False,
        }
    if status == "ready-to-unblind":
        return {
            "owner": "experiment-owner",
            "action": "All preregistered blocks and blind ratings are sealed. Unblind every child exactly once and build the rater-level bundle report.",
            "input_path": str(bundle_path / SCHEDULE_FILE),
            "expected_schema": BUNDLE_REPORT_SCHEMA,
            "command": shell_command(["./lacuna", "scenario", "bundle", "unblind", str(bundle_path)]),
            "blind": False,
        }
    if status == "unblinding":
        return {
            "owner": "experiment-owner",
            "action": "Bundle unblinding was durably entered. Re-run the idempotent unblind command to complete any child reports and publish the deterministic aggregate.",
            "input_path": str(bundle_path / SCHEDULE_FILE),
            "expected_schema": BUNDLE_REPORT_SCHEMA,
            "command": shell_command(["./lacuna", "scenario", "bundle", "unblind", str(bundle_path)]),
            "blind": False,
        }
    if status == "unblinded":
        return {
            "owner": "experiment-owner",
            "action": "The complete preregistered bundle report is frozen. Preserve the private bundle and share only deliberately selected public artifacts.",
            "input_path": str(bundle_path / BUNDLE_REPORT_FILE),
            "expected_schema": None,
            "command": None,
            "blind": False,
        }
    _fail("bad-scenario-bundle", f"unsupported bundle status {status!r}")


def build_scenario_bundle_witness_template(
    value: str | Path,
    *,
    witness_id: str,
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        manifest = inspection["manifest"]
        if any(block["status"] != ("active" if block["ordinal"] == 1 else "pending") for block in manifest["blocks"]):
            _fail("scenario-bundle-witness-window-closed", "witness receipts must be recorded before any block execution or sealing")
        for child in inspection["children"].values():
            if not _scenario_is_pristine(child):
                _fail("scenario-bundle-witness-window-closed", "witness receipts must be recorded before any child run changes")
        try:
            witness_id = require_id(witness_id, "witness_id")
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle-witness", str(exc)) from exc
        return {
            "event": "lacuna.scenario.bundle.witness-recorded",
            "schema": BUNDLE_WITNESS_SCHEMA,
            "bundle_id": manifest["bundle_id"],
            "witness_id": witness_id,
            "commitment_sha256": manifest["commitment"]["sha256"],
            "kind": "external-retention",
            "service": "replace-with-witness-or-service-name",
            "external_receipt_id": "replace-with-external-receipt-id",
            "external_receipt_sha256": None,
            "external_locator": None,
            "witnessed_at": "replace-with-external-witness-time",
            "recorded_at": utc_now(),
            "declaration": "operator-supplied-unverified-external-receipt",
            "notes": None,
            "nonclaims": list(WITNESS_NONCLAIMS),
        }


def _validate_witness(
    value: Any,
    *,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle witness", fields=WITNESS_FIELDS, code="bad-scenario-bundle-witness")
    if document.get("event") != "lacuna.scenario.bundle.witness-recorded" or document.get("schema") != BUNDLE_WITNESS_SCHEMA:
        _fail("bad-scenario-bundle-witness", "unsupported scenario bundle witness contract")
    if document.get("bundle_id") != manifest["bundle_id"] or document.get("commitment_sha256") != manifest["commitment"]["sha256"]:
        _fail("scenario-bundle-witness-binding-mismatch", "witness does not bind the exact retained bundle commitment")
    try:
        witness_id = require_id(document.get("witness_id"), "witness_id")
        service = require_string(document.get("service"), "service", max_len=512)
        receipt_id = require_string(document.get("external_receipt_id"), "external_receipt_id", max_len=1024)
        witnessed_at = require_string(document.get("witnessed_at"), "witnessed_at", max_len=256)
        recorded_at = require_string(document.get("recorded_at"), "recorded_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-witness", str(exc)) from exc
    placeholders = ("replace-", "replace.", "replace_")
    if any(value.lower().startswith(placeholders) for value in (service, receipt_id, witnessed_at)):
        _fail("bad-scenario-bundle-witness", "witness template placeholders must be replaced")
    kind = document.get("kind")
    if kind not in WITNESS_KINDS:
        _fail("bad-scenario-bundle-witness", f"unsupported witness kind {kind!r}")
    receipt_sha = document.get("external_receipt_sha256")
    if receipt_sha is not None:
        receipt_sha = _require_sha256(receipt_sha, "external_receipt_sha256", code="bad-scenario-bundle-witness")
    locator = _optional_string(document.get("external_locator"), "external_locator", max_len=4096)
    if receipt_sha is None and not locator:
        _fail("bad-scenario-bundle-witness", "a witness must retain an external receipt digest or locator in addition to its receipt ID")
    if document.get("declaration") != "operator-supplied-unverified-external-receipt":
        _fail("bad-scenario-bundle-witness", "witness declaration was changed")
    notes = _optional_string(document.get("notes"), "notes", max_len=20000)
    if document.get("nonclaims") != WITNESS_NONCLAIMS:
        _fail("bad-scenario-bundle-witness", "witness nonclaims were changed")
    return {
        "event": "lacuna.scenario.bundle.witness-recorded",
        "schema": BUNDLE_WITNESS_SCHEMA,
        "bundle_id": manifest["bundle_id"],
        "witness_id": witness_id,
        "commitment_sha256": manifest["commitment"]["sha256"],
        "kind": kind,
        "service": service,
        "external_receipt_id": receipt_id,
        "external_receipt_sha256": receipt_sha,
        "external_locator": locator,
        "witnessed_at": witnessed_at,
        "recorded_at": recorded_at,
        "declaration": "operator-supplied-unverified-external-receipt",
        "notes": notes,
        "nonclaims": list(WITNESS_NONCLAIMS),
    }


def _scenario_is_pristine(child: dict[str, Any]) -> bool:
    return (
        child.get("status") == "collecting-results"
        and all(cell.get("status") == "pending" and cell.get("result") is None for cell in child.get("cells", []))
        and child.get("ratings") == []
        and child.get("masking_assessments") == []
        and child.get("blind_packet") is None
        and child.get("report") is None
        and child.get("unblinded_at") is None
    )


def _require_sealed_child_still_blind(
    block: dict[str, Any],
    child: dict[str, Any],
    *,
    message: str,
) -> None:
    """Enforce the bundle's seal-before-any-unblind boundary.

    A direct child command can bypass the parent CLI, so the parent audit must
    distinguish premature unblinding from ordinary block-order drift.  This
    helper is shared by the completed-prefix and all-blocks-sealed checks.
    """
    if block["status"] != "sealed":
        _fail(
            "scenario-bundle-block-order-mismatch",
            message,
            {"block_id": block["block_id"]},
        )
    if child["status"] == "unblinded":
        _fail(
            "scenario-bundle-premature-unblinding",
            "a child was unblinded before the bundle durably entered its all-block unblinding phase",
            {"block_id": block["block_id"]},
        )
    if child["status"] != "ready-to-unblind":
        _fail(
            "scenario-bundle-block-order-mismatch",
            message,
            {"block_id": block["block_id"]},
        )


def _validate_run_binding(
    value: Any,
    *,
    bundle_path: Path,
    block: dict[str, Any],
    schedule_item: dict[str, Any],
    child: dict[str, Any],
) -> dict[str, Any]:
    binding = _strict(value, label=f"block {block['block_id']} scenario_run", fields=RUN_BINDING_FIELDS, code="bad-scenario-bundle")
    expected_path = f"blocks/{block['label']}/scenario-runs/{schedule_item['scenario_run_id']}"
    if binding.get("path") != expected_path:
        _fail("scenario-bundle-path-mismatch", "child scenario path does not match the fixed bundle topology", {"block_id": block["block_id"]})
    if binding.get("run_id") != schedule_item["scenario_run_id"] or child.get("run_id") != schedule_item["scenario_run_id"]:
        _fail("scenario-bundle-child-binding-mismatch", "child scenario run identity does not match the private schedule", {"block_id": block["block_id"]})
    expected_authority = bundle_path / PurePosixPath(expected_path)
    if child.get("run_path") != str(expected_authority):
        _fail("scenario-bundle-child-binding-mismatch", "child run authority path does not match the bundle path", {"block_id": block["block_id"]})
    for field, child_ref_name in (("capsule_sha256", "capsule"), ("assignment_sha256", "assignment")):
        _require_sha256(binding.get(field), f"scenario_run.{field}", code="bad-scenario-bundle")
        if binding[field] != child[child_ref_name]["sha256"]:
            _fail("scenario-bundle-child-binding-mismatch", f"child {child_ref_name} digest changed", {"block_id": block["block_id"]})
    seed = _strict(binding.get("seed"), label="scenario_run.seed", fields=RUN_SEED_FIELDS, code="bad-scenario-bundle")
    if seed != child.get("seed"):
        _fail("scenario-bundle-child-binding-mismatch", "child seed boundary changed", {"block_id": block["block_id"]})
    return copy.deepcopy(binding)


def _validate_child_assignment(
    run_path: Path,
    child: dict[str, Any],
    *,
    schedule_item: dict[str, Any],
) -> dict[str, Any]:
    assignment = _read_child_ref(run_path, child["assignment"], label="bundle child assignment")
    if (
        assignment.get("method") != "bundle-precommitted-seed-sha256-sort-v1"
        or assignment.get("randomization_seed") != schedule_item["assignment_seed"]
        or assignment.get("run_id") != schedule_item["scenario_run_id"]
    ):
        _fail("scenario-bundle-assignment-mismatch", "child assignment does not use the preregistered bundle seed and run identity", {"block_id": schedule_item["block_id"]})
    return assignment


def _collect_child_invocations(
    run_path: Path,
    child: dict[str, Any],
) -> list[dict[str, Any]]:
    invocations: list[dict[str, Any]] = []
    for cell in child["cells"]:
        if cell["status"] != "recorded":
            continue
        receipt = _read_child_ref(run_path, cell["result"], label="bundle child cell receipt")
        returned = _read_child_ref(run_path, receipt["return_artifact"], label="bundle child cell return")
        invocations.extend(copy.deepcopy(returned["invocations"]))
    return invocations


def _build_block_seal(
    *,
    manifest: dict[str, Any],
    block: dict[str, Any],
    child: dict[str, Any],
    sealed_at: str,
) -> dict[str, Any]:
    if child["status"] != "ready-to-unblind":
        _fail("scenario-bundle-block-not-ready", "a block can be sealed only after every fixed blind rating and masking assessment is retained")
    return {
        "event": "lacuna.scenario.bundle.block-sealed",
        "schema": BUNDLE_BLOCK_SEAL_SCHEMA,
        "bundle_id": manifest["bundle_id"],
        "block_id": block["block_id"],
        "block_label": block["label"],
        "ordinal": block["ordinal"],
        "scenario_run_id": child["run_id"],
        "scenario_run_path": child["run_path"],
        "capsule_sha256": child["capsule"]["sha256"],
        "assignment_sha256": child["assignment"]["sha256"],
        "blind_packet_sha256": child["blind_packet"]["sha256"],
        "contamination_scan_sha256": child["contamination_scan"]["sha256"],
        "rating_artifact_sha256s": [ref["sha256"] for ref in child["ratings"]],
        "masking_artifact_sha256s": [ref["sha256"] for ref in child["masking_assessments"]],
        "sealed_at": sealed_at,
        "nonclaims": list(SEAL_NONCLAIMS),
    }


def _validate_block_seal(
    value: Any,
    *,
    manifest: dict[str, Any],
    block: dict[str, Any],
    child: dict[str, Any],
) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle block seal", fields=SEAL_FIELDS, code="bad-scenario-bundle-block-seal")
    try:
        sealed_at = require_string(document.get("sealed_at"), "sealed_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle-block-seal", str(exc)) from exc
    expected_child = copy.deepcopy(child)
    # The child may already be unblinded during the bundle's explicitly entered
    # unblinding phase; the seal binds only artifacts that existed beforehand.
    if expected_child["status"] == "unblinded":
        expected_child["status"] = "ready-to-unblind"
    expected = _build_block_seal(
        manifest=manifest,
        block=block,
        child=expected_child,
        sealed_at=sealed_at,
    )
    if document != expected:
        _fail("scenario-bundle-block-seal-mismatch", "block seal is not the exact join of the retained ready-to-unblind child artifacts", {"block_id": block["block_id"]})
    return copy.deepcopy(document)


def _empty_summary() -> dict[str, Any]:
    return {
        "block_count": 0,
        "observation_count": 0,
        "dimensions": {
            dimension: {
                condition: {"score_sum": 0, "score_count": 0}
                for condition in SCENARIO_CONDITIONS
            }
            for dimension in HUMAN_RATING_DIMENSIONS
        },
        "preference_rank": {
            condition: {"score_sum": 0, "score_count": 0}
            for condition in SCENARIO_CONDITIONS
        },
        "method_identifiability": {
            condition: {
                "assessor_count": 0,
                "observation_count": 0,
                "correct_guess_count": 0,
                "nonunknown_guess_count": 0,
                "confidence_sum": 0,
            }
            for condition in SCENARIO_CONDITIONS
        },
        "cell_status": {
            condition: {"completed": 0, "refused": 0, "failed": 0}
            for condition in SCENARIO_CONDITIONS
        },
        "contamination": {
            "clean_blocks": 0,
            "leak_detected_blocks": 0,
            "unexpected_match_count": 0,
        },
    }


def _build_bundle_report(
    *,
    manifest: dict[str, Any],
    plan: dict[str, Any],
    commitment: dict[str, Any],
    witnesses: list[dict[str, Any]],
    seals: dict[str, dict[str, Any]],
    children: dict[str, dict[str, Any]],
    child_paths: dict[str, Path],
    unblinded_at: str,
) -> dict[str, Any]:
    plan_by_id = {block["block_id"]: block for block in plan["blocks"]}
    block_records: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    summary = _empty_summary()
    summary["block_count"] = len(manifest["blocks"])

    for block in manifest["blocks"]:
        block_id = block["block_id"]
        plan_block = plan_by_id[block_id]
        child = children[block_id]
        run_path = child_paths[block_id]
        if child["status"] != "unblinded" or child["report"] is None:
            _fail("scenario-bundle-child-not-unblinded", "every child must have a deterministic report before aggregate publication", {"block_id": block_id})
        scenario_report = _read_child_ref(run_path, child["report"], label="bundle child scenario report")
        label_to_condition = {
            record["cell_label"]: record["condition"]
            for record in scenario_report["cell_records"]
        }
        records_by_condition = {
            record["condition"]: record for record in scenario_report["cell_records"]
        }
        mechanics_by_condition = {
            record["condition"]: record for record in scenario_report["mechanical_outcomes"]
        }
        ratings = [
            _read_child_ref(run_path, ref, label="bundle child scenario rating")
            for ref in child["ratings"]
        ]
        masking_by_assessor = {
            masking["assessor_id"]: masking
            for masking in (
                _read_child_ref(run_path, ref, label="bundle child scenario masking assessment")
                for ref in child["masking_assessments"]
            )
        }
        seal = seals[block_id]
        block_records.append(
            {
                "ordinal": block["ordinal"],
                "block_id": block_id,
                "story_stratum": plan_block["story_stratum"],
                "model_stratum": plan_block["model_stratum"],
                "replicate": plan_block["replicate"],
                "scenario_run_id": child["run_id"],
                "capsule_sha256": child["capsule"]["sha256"],
                "assignment_sha256": child["assignment"]["sha256"],
                "contamination_scan_sha256": child["contamination_scan"]["sha256"],
                "contamination_status": scenario_report["contamination_summary"]["overall_status"],
                "contamination_unexpected_match_count": scenario_report["contamination_summary"]["unexpected_match_count"],
                "seal_sha256": _digest(seal, label="bundle block seal"),
                "scenario_report_sha256": child["report"]["sha256"],
                "rater_count": len(ratings),
                "included": True,
            }
        )
        contamination_summary = scenario_report["contamination_summary"]
        if contamination_summary["overall_status"] == "clean":
            summary["contamination"]["clean_blocks"] += 1
        else:
            summary["contamination"]["leak_detected_blocks"] += 1
        summary["contamination"]["unexpected_match_count"] += contamination_summary["unexpected_match_count"]
        for condition in SCENARIO_CONDITIONS:
            status = records_by_condition[condition]["status"]
            summary["cell_status"][condition][status] += 1
        for rating in ratings:
            masking = masking_by_assessor.get(rating["rater_id"])
            if masking is None:
                _fail(
                    "scenario-bundle-report-masking-missing",
                    "every rater-level observation requires its paired post-rating masking assessment",
                    {"block_id": block_id, "rater_id": rating["rater_id"]},
                )
            mask_by_label = {item["cell_label"]: item for item in masking["assessments"]}
            for item in rating["ratings"]:
                condition = label_to_condition[item["cell_label"]]
                cell_record = records_by_condition[condition]
                mechanical = mechanics_by_condition[condition]
                mask_item = mask_by_label[item["cell_label"]]
                guess = mask_item["guessed_condition"]
                correct = guess == condition
                observation = {
                    "block_ordinal": block["ordinal"],
                    "block_id": block_id,
                    "story_stratum": plan_block["story_stratum"],
                    "model_stratum": plan_block["model_stratum"],
                    "replicate": plan_block["replicate"],
                    "scenario_run_id": child["run_id"],
                    "rater_id": rating["rater_id"],
                    "condition": condition,
                    "cell_label": item["cell_label"],
                    "cell_status": cell_record["status"],
                    "contamination_status": cell_record["contamination_status"],
                    "contamination_unexpected_match_count": cell_record["contamination_unexpected_match_count"],
                    "scores": copy.deepcopy(item["scores"]),
                    "preference_rank": item["preference_rank"],
                    "method_guess": guess,
                    "method_guess_correct": correct,
                    "method_guess_confidence": mask_item["confidence"],
                    "method_guess_recognized": mask_item["recognized_method"],
                    "method_guess_familiarity": mask_item["familiarity"],
                    "method_guess_cues": copy.deepcopy(mask_item["cues"]),
                    "comments": item["comments"],
                    "transcript_sha256": cell_record["transcript_sha256"],
                    "final_head": mechanical["final_head"],
                    "event_count_delta": mechanical["event_count_delta"],
                    "execution_totals": copy.deepcopy(mechanical["execution_totals"]),
                }
                observations.append(observation)
                summary["observation_count"] += 1
                for dimension in HUMAN_RATING_DIMENSIONS:
                    summary["dimensions"][dimension][condition]["score_sum"] += item["scores"][dimension]
                    summary["dimensions"][dimension][condition]["score_count"] += 1
                summary["preference_rank"][condition]["score_sum"] += item["preference_rank"]
                summary["preference_rank"][condition]["score_count"] += 1
                method = summary["method_identifiability"][condition]
                method["assessor_count"] += 1
                method["observation_count"] += 1
                method["confidence_sum"] += mask_item["confidence"]
                if guess != "unknown":
                    method["nonunknown_guess_count"] += 1
                if correct:
                    method["correct_guess_count"] += 1

    return {
        "event": "lacuna.scenario.bundle.unblinded",
        "schema": BUNDLE_REPORT_SCHEMA,
        "bundle_id": manifest["bundle_id"],
        "title": plan["title"],
        "research_question": plan["research_question"],
        "commitment_sha256": _digest(
            commitment,
            label="scenario bundle public commitment",
        ),
        "witness_artifact_sha256s": [
            _digest(witness, label=f"scenario bundle witness {index}")
            for index, witness in enumerate(witnesses, start=1)
        ],
        "registration": copy.deepcopy(plan["registration"]),
        "block_records": block_records,
        "observations": observations,
        "descriptive_summary": summary,
        "unblinded_at": unblinded_at,
        "separation": {
            "mechanical": "cube identity, verification, final head, and event-count delta derived by Lacuna for each child",
            "host_declared": "provider/model/context/digest/timing/token/cost/failure records supplied by the operator",
            "human": "blind rater-level integer scores, preference ranks, and comments authored before bundle unblinding",
            "masking": "post-primary-rating method guesses are paired by rater_id and evaluated only after condition identity is joined",
            "witness": "operator-supplied external receipt descriptions bound to the public commitment",
        },
        "nonclaims": list(REPORT_NONCLAIMS),
    }


def _validate_bundle_report(value: Any, *, expected: dict[str, Any]) -> dict[str, Any]:
    document = _strict(value, label="scenario bundle report", fields=REPORT_FIELDS, code="bad-scenario-bundle-report")
    if not isinstance(document.get("block_records"), list) or not isinstance(document.get("observations"), list):
        _fail("bad-scenario-bundle-report", "block_records and observations must be arrays")
    for index, item in enumerate(document["block_records"]):
        _strict(item, label=f"block_records[{index}]", fields=REPORT_BLOCK_FIELDS, code="bad-scenario-bundle-report")
    for index, item in enumerate(document["observations"]):
        observation = _strict(item, label=f"observations[{index}]", fields=OBSERVATION_FIELDS, code="bad-scenario-bundle-report")
        _strict(observation.get("scores"), label=f"observations[{index}].scores", fields=set(HUMAN_RATING_DIMENSIONS), code="bad-scenario-bundle-report")
    summary = _strict(document.get("descriptive_summary"), label="descriptive_summary", fields=SUMMARY_FIELDS, code="bad-scenario-bundle-report")
    dimensions = _strict(summary.get("dimensions"), label="descriptive_summary.dimensions", fields=set(HUMAN_RATING_DIMENSIONS), code="bad-scenario-bundle-report")
    for dimension in HUMAN_RATING_DIMENSIONS:
        conditions = _strict(dimensions[dimension], label=f"dimensions.{dimension}", fields=set(SCENARIO_CONDITIONS), code="bad-scenario-bundle-report")
        for condition in SCENARIO_CONDITIONS:
            _strict(conditions[condition], label=f"dimensions.{dimension}.{condition}", fields=SUMMARY_VALUE_FIELDS, code="bad-scenario-bundle-report")
    ranks = _strict(summary.get("preference_rank"), label="descriptive_summary.preference_rank", fields=set(SCENARIO_CONDITIONS), code="bad-scenario-bundle-report")
    method = _strict(summary.get("method_identifiability"), label="descriptive_summary.method_identifiability", fields=set(SCENARIO_CONDITIONS), code="bad-scenario-bundle-report")
    statuses = _strict(summary.get("cell_status"), label="descriptive_summary.cell_status", fields=set(SCENARIO_CONDITIONS), code="bad-scenario-bundle-report")
    _strict(
        summary.get("contamination"),
        label="descriptive_summary.contamination",
        fields=CONTAMINATION_SUMMARY_FIELDS,
        code="bad-scenario-bundle-report",
    )
    for condition in SCENARIO_CONDITIONS:
        _strict(ranks[condition], label=f"preference_rank.{condition}", fields=SUMMARY_VALUE_FIELDS, code="bad-scenario-bundle-report")
        _strict(method[condition], label=f"method_identifiability.{condition}", fields=METHOD_SUMMARY_FIELDS, code="bad-scenario-bundle-report")
        _strict(statuses[condition], label=f"cell_status.{condition}", fields=STATUS_COUNT_FIELDS, code="bad-scenario-bundle-report")
    if document != expected:
        _fail("scenario-bundle-report-mismatch", "bundle report is not the deterministic rater-level join of every preregistered child")
    return copy.deepcopy(document)


def _read_bundle_manifest(storage_path: Path) -> dict[str, Any]:
    return read_sidecar_json_object(
        storage_path / BUNDLE_MANIFEST_FILE,
        label="scenario bundle manifest",
        error_prefix="scenario-bundle",
        root_error_code="bad-scenario-bundle",
    )


def _seal_relative_path(block: dict[str, Any]) -> str:
    return f"blocks/{block['label']}/60-block-seal.json"


def _witness_relative_path(sequence: int) -> str:
    """Return the immutable publication slot for one ordered witness receipt.

    The witness identity belongs inside the digest-bound artifact and manifest
    reference, not in the filename.  A sequence-only slot makes a crash after
    artifact publication deterministic: an exact retry reuses the slot and a
    different retry cannot route around the first bytes by changing witness_id.
    """
    return f"witnesses/witness-{sequence:04d}.json"


def _audit_bundle_next(storage_path: Path, manifest: dict[str, Any]) -> None:
    actual = read_sidecar_text(
        storage_path / BUNDLE_NEXT_FILE,
        label="scenario bundle next-action pointer",
        error_prefix="scenario-bundle",
    )
    expected = _render_next(manifest)
    if actual != expected:
        _fail(
            "scenario-bundle-next-pointer-mismatch",
            "NEXT.md is missing, stale, or edited; run scenario bundle recover after authoritative custody passes",
        )


def _validate_manifest_block(
    value: Any,
    *,
    index: int,
    schedule_item: dict[str, Any],
) -> dict[str, Any]:
    block = _strict(
        value,
        label=f"blocks[{index}]",
        fields=MANIFEST_BLOCK_FIELDS,
        code="bad-scenario-bundle",
    )
    if (
        block.get("ordinal") != index + 1
        or block.get("ordinal") != schedule_item["ordinal"]
        or block.get("label") != schedule_item["block_label"]
        or block.get("block_id") != schedule_item["block_id"]
    ):
        _fail(
            "scenario-bundle-block-topology-mismatch",
            "manifest block order, label, or identity differs from the private schedule",
            {"ordinal": index + 1},
        )
    if block.get("status") not in BLOCK_STATUSES:
        _fail("bad-scenario-bundle", f"unsupported block status {block.get('status')!r}")
    report_sha = block.get("scenario_report_sha256")
    if report_sha is not None:
        _require_sha256(
            report_sha,
            f"blocks[{index}].scenario_report_sha256",
            code="bad-scenario-bundle",
        )
    return copy.deepcopy(block)


def _inspect_bundle_unlocked(
    storage_path: Path,
    *,
    authority_path: Path | None = None,
    audit_next: bool = True,
    strict_cached_state: bool = True,
) -> dict[str, Any]:
    authority_path = storage_path if authority_path is None else Path(authority_path)
    manifest = _strict(
        _read_bundle_manifest(storage_path),
        label="scenario bundle manifest",
        fields=MANIFEST_FIELDS,
        code="bad-scenario-bundle",
    )
    if manifest.get("event") != BUNDLE_EVENT or manifest.get("schema") != BUNDLE_SCHEMA:
        _fail("bad-scenario-bundle", "unsupported scenario bundle manifest")
    if manifest.get("project_version") != __version__:
        _fail(
            "scenario-bundle-version-mismatch",
            "scenario bundles are interpreted only by their creating Lacuna version",
            {"created_by": manifest.get("project_version"), "runtime": __version__},
        )
    try:
        bundle_id = require_id(manifest.get("bundle_id"), "bundle_id")
        require_string(manifest.get("created_at"), "created_at", max_len=128)
        require_string(manifest.get("updated_at"), "updated_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle", str(exc)) from exc
    if manifest.get("bundle_path") != str(authority_path) or authority_path.name != bundle_id:
        _fail(
            "scenario-bundle-path-mismatch",
            "manifest bundle_path and bundle_id must match the exact authority directory",
        )
    if manifest.get("status") not in BUNDLE_STATUSES:
        _fail("bad-scenario-bundle", f"unsupported bundle status {manifest.get('status')!r}")
    if manifest.get("nonclaims") != BUNDLE_NONCLAIMS:
        _fail("bad-scenario-bundle", "bundle nonclaims were changed")

    plan_ref = _validate_ref(
        manifest.get("plan"),
        expected_path=PLAN_FILE,
        expected_schema=BUNDLE_PLAN_SCHEMA,
        expected_role="experiment-owner",
        label="plan",
    )
    plan = validate_scenario_bundle_plan(
        _read_ref_json(storage_path, plan_ref, label="scenario bundle preregistration")
    )
    if plan["bundle_id"] != bundle_id:
        _fail("scenario-bundle-plan-binding-mismatch", "plan bundle_id differs from the manifest")

    schedule_ref = _validate_ref(
        manifest.get("schedule"),
        expected_path=SCHEDULE_FILE,
        expected_schema=BUNDLE_SCHEDULE_SCHEMA,
        expected_role="experiment-owner-private",
        label="schedule",
    )
    schedule = _validate_schedule(
        _read_ref_json(storage_path, schedule_ref, label="private scenario bundle schedule"),
        plan=plan,
    )
    if schedule["created_at"] != manifest["created_at"]:
        _fail("scenario-bundle-schedule-mismatch", "schedule and bundle creation times differ")

    commitment_ref = _validate_ref(
        manifest.get("commitment"),
        expected_path=COMMITMENT_FILE,
        expected_schema=BUNDLE_COMMITMENT_SCHEMA,
        expected_role="public-witness-input",
        label="commitment",
    )
    commitment_value = _read_ref_json(
        storage_path, commitment_ref, label="scenario bundle public commitment"
    )

    try:
        block_values = require_list(manifest.get("blocks"), "blocks")
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle", str(exc)) from exc
    if len(block_values) != len(schedule["blocks"]):
        _fail("bad-scenario-bundle", "manifest block count differs from the private schedule")
    blocks = [
        _validate_manifest_block(value, index=index, schedule_item=schedule["blocks"][index])
        for index, value in enumerate(block_values)
    ]
    plan_by_id = {block["block_id"]: block for block in plan["blocks"]}
    children: dict[str, dict[str, Any]] = {}
    child_paths: dict[str, Path] = {}
    assignments: dict[str, dict[str, Any]] = {}

    for index, block in enumerate(blocks):
        schedule_item = schedule["blocks"][index]
        plan_block = plan_by_id[block["block_id"]]
        expected_relative = (
            f"blocks/{block['label']}/scenario-runs/{schedule_item['scenario_run_id']}"
        )
        run_storage = resolve_sidecar_member_directory(
            storage_path,
            expected_relative,
            error_prefix="scenario-bundle",
            label=f"scenario child for block {block['block_id']}",
        )
        run_authority = authority_path / PurePosixPath(expected_relative)
        with _scenario_run_lock(run_storage):
            child = _audit_scenario_run_unlocked(
                run_storage,
                authority_path=run_authority,
            )
        _validate_run_binding(
            block.get("scenario_run"),
            bundle_path=authority_path,
            block=block,
            schedule_item=schedule_item,
            child=child,
        )
        if child.get("reference") != f"bundle:{bundle_id}:{block['block_id']}":
            _fail(
                "scenario-bundle-child-binding-mismatch",
                "child reference differs from its bundle/block identity",
                {"block_id": block["block_id"]},
            )
        if child.get("resolved_seed_cube_path") != plan_block["resolved_seed_cube_path"]:
            _fail(
                "scenario-bundle-child-binding-mismatch",
                "child seed source path differs from the preregistered path",
                {"block_id": block["block_id"]},
            )
        child_capsule = validate_scenario_capsule(
            _read_child_ref(run_storage, child["capsule"], label="bundle child capsule")
        )
        if child_capsule != plan_block["capsule"]:
            _fail(
                "scenario-bundle-capsule-mismatch",
                "child capsule differs from the preregistered block capsule",
                {"block_id": block["block_id"]},
            )
        assignment = _validate_child_assignment(
            run_storage,
            child,
            schedule_item=schedule_item,
        )
        children[block["block_id"]] = child
        child_paths[block["block_id"]] = run_storage
        assignments[block["block_id"]] = assignment

    expected_commitment = _build_commitment(
        plan_ref=plan_ref,
        schedule_ref=schedule_ref,
        plan=plan,
        blocks=blocks,
        created_at=manifest["created_at"],
    )
    commitment = _validate_commitment(commitment_value, expected=expected_commitment)

    try:
        witness_refs_raw = require_list(manifest.get("witnesses"), "witnesses")
    except ValueError as exc:
        raise LacunaError("bad-scenario-bundle", str(exc)) from exc
    if len(witness_refs_raw) > MAX_BUNDLE_WITNESSES:
        _fail("bad-scenario-bundle", "witness count exceeds the v1 custody limit")
    witnesses: list[dict[str, Any]] = []
    witness_ids: set[str] = set()
    receipt_ids: set[str] = set()
    normalized_witness_refs: list[dict[str, Any]] = []
    for index, value in enumerate(witness_refs_raw, start=1):
        document = _strict(
            value,
            label=f"witnesses[{index - 1}]",
            fields=WITNESS_REF_FIELDS,
            code="bad-scenario-bundle",
        )
        try:
            witness_id = require_id(document.get("witness_id"), "witness_id")
            receipt_id = require_string(
                document.get("external_receipt_id"),
                "external_receipt_id",
                max_len=1024,
            )
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle", str(exc)) from exc
        ref = _validate_ref(
            document,
            expected_path=_witness_relative_path(index),
            expected_schema=BUNDLE_WITNESS_SCHEMA,
            expected_role="external-witness-record",
            label=f"witnesses[{index - 1}]",
            fields=WITNESS_REF_FIELDS,
        )
        witness = _validate_witness(
            _read_ref_json(storage_path, ref, label=f"scenario bundle witness {witness_id}"),
            manifest=manifest,
        )
        if witness["witness_id"] != witness_id or witness["external_receipt_id"] != receipt_id:
            _fail("scenario-bundle-witness-binding-mismatch", "witness reference metadata changed")
        if witness_id in witness_ids:
            _fail("duplicate-scenario-bundle-witness", "witness_id values must be unique")
        if receipt_id in receipt_ids:
            _fail(
                "duplicate-scenario-bundle-witness-receipt",
                "external_receipt_id values must be unique",
            )
        witness_ids.add(witness_id)
        receipt_ids.add(receipt_id)
        witnesses.append(witness)
        normalized_witness_refs.append(copy.deepcopy(document))

    seals: dict[str, dict[str, Any]] = {}
    context_owners: dict[str, str] = {}
    invocation_owners: dict[str, str] = {}
    for block in blocks:
        child = children[block["block_id"]]
        run_storage = child_paths[block["block_id"]]
        for invocation in _collect_child_invocations(run_storage, child):
            context_id = invocation["context_id"]
            prior_context = context_owners.get(context_id)
            if prior_context is not None and prior_context != block["block_id"]:
                _fail(
                    "scenario-bundle-cross-block-context-reuse",
                    "a declared model context_id cannot be reused across bundle blocks",
                    {
                        "context_id": context_id,
                        "first_block": prior_context,
                        "second_block": block["block_id"],
                    },
                )
            context_owners[context_id] = block["block_id"]
            invocation_id = invocation["invocation_id"]
            if invocation_id is not None:
                prior_invocation = invocation_owners.get(invocation_id)
                if prior_invocation is not None:
                    _fail(
                        "scenario-bundle-duplicate-invocation-id",
                        "a non-null invocation_id must be unique across the whole bundle",
                        {
                            "invocation_id": invocation_id,
                            "first_block": prior_invocation,
                            "second_block": block["block_id"],
                        },
                    )
                invocation_owners[invocation_id] = block["block_id"]

        seal_value = block.get("seal")
        if block["status"] in {"sealed", "unblinded"}:
            seal_ref = _validate_ref(
                seal_value,
                expected_path=_seal_relative_path(block),
                expected_schema=BUNDLE_BLOCK_SEAL_SCHEMA,
                expected_role="lacuna-scenario-bundle-runner",
                label=f"block {block['block_id']} seal",
            )
            seal = _validate_block_seal(
                _read_ref_json(storage_path, seal_ref, label="scenario bundle block seal"),
                manifest=manifest,
                block=block,
                child=child,
            )
            seals[block["block_id"]] = seal
        elif seal_value is not None:
            _fail("bad-scenario-bundle", "only sealed or unblinded blocks may retain a seal")

        if block["status"] == "unblinded":
            if child["status"] != "unblinded" or child["report"] is None:
                if strict_cached_state:
                    _fail(
                        "scenario-bundle-cached-state-stale",
                        "outer unblinded block state differs from its child run",
                        {"block_id": block["block_id"]},
                    )
            elif block["scenario_report_sha256"] != child["report"]["sha256"]:
                _fail(
                    "scenario-bundle-child-report-mismatch",
                    "child scenario report commitment changed",
                    {"block_id": block["block_id"]},
                )
        elif block["scenario_report_sha256"] is not None:
            _fail("bad-scenario-bundle", "only an unblinded block may retain scenario_report_sha256")

    minimum_witnesses = plan["witness_policy"]["minimum_receipts_before_execution"]
    enough_witnesses = len(witnesses) >= minimum_witnesses
    status = manifest["status"]
    expected_status = status

    if status == "awaiting-witnesses":
        if enough_witnesses:
            expected_status = "block-active"
            if strict_cached_state:
                _fail(
                    "scenario-bundle-cached-state-stale",
                    "the witness gate is satisfied but the outer status was not advanced; run scenario bundle recover",
                )
        for index, block in enumerate(blocks):
            expected_block = "active" if index == 0 else "pending"
            if block["status"] != expected_block or not _scenario_is_pristine(children[block["block_id"]]):
                _fail(
                    "scenario-bundle-witness-gate-bypassed",
                    "no child may advance before the preregistered witness threshold is met",
                    {"block_id": block["block_id"]},
                )
    elif status in {"block-active", "block-ready-to-seal"}:
        if not enough_witnesses:
            _fail("scenario-bundle-witness-gate-bypassed", "bundle execution began before enough witness receipts were retained")
        active_indices = [index for index, block in enumerate(blocks) if block["status"] == "active"]
        if len(active_indices) != 1:
            _fail("scenario-bundle-block-order-mismatch", "an executing bundle requires exactly one active block")
        active_index = active_indices[0]
        for index, block in enumerate(blocks):
            child = children[block["block_id"]]
            if index < active_index:
                _require_sealed_child_still_blind(
                    block,
                    child,
                    message="sealed blocks must form the completed prefix and remain blinded",
                )
            elif index == active_index:
                if child["status"] == "unblinded":
                    _fail("scenario-bundle-premature-unblinding", "an active child was unblinded before every block was sealed")
                child_ready = child["status"] == "ready-to-unblind"
                expected_status = "block-ready-to-seal" if child_ready else "block-active"
                if status != expected_status and strict_cached_state:
                    _fail(
                        "scenario-bundle-cached-state-stale",
                        "outer bundle status differs from the active child; run scenario bundle recover",
                        {"expected": expected_status, "actual": status},
                    )
            else:
                if block["status"] != "pending" or not _scenario_is_pristine(child):
                    _fail(
                        "scenario-bundle-future-block-contaminated",
                        "a future child changed before every earlier block was sealed",
                        {"block_id": block["block_id"]},
                    )
    elif status == "ready-to-unblind":
        if not enough_witnesses:
            _fail("scenario-bundle-witness-gate-bypassed", "bundle reached unblinding without enough witnesses")
        for block in blocks:
            child = children[block["block_id"]]
            _require_sealed_child_still_blind(
                block,
                child,
                message="ready-to-unblind requires every block to be sealed and every child to remain structurally blind",
            )
    elif status == "unblinding":
        if not enough_witnesses:
            _fail("scenario-bundle-witness-gate-bypassed", "bundle entered unblinding without enough witnesses")
        try:
            require_string(manifest.get("unblinded_at"), "unblinded_at", max_len=128)
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle", str(exc)) from exc
        for block in blocks:
            child = children[block["block_id"]]
            if block["status"] == "sealed":
                if child["status"] == "unblinded":
                    if strict_cached_state:
                        _fail(
                            "scenario-bundle-cached-state-stale",
                            "a child completed unblinding before the outer block cache advanced; run scenario bundle recover or unblind",
                            {"block_id": block["block_id"]},
                        )
                elif child["status"] != "ready-to-unblind":
                    _fail("scenario-bundle-unblinding-state-mismatch", "a sealed child is neither ready nor unblinded")
            elif block["status"] == "unblinded":
                if child["status"] != "unblinded":
                    _fail("scenario-bundle-unblinding-state-mismatch", "an outer unblinded block has no unblinded child")
            else:
                _fail("scenario-bundle-unblinding-state-mismatch", "unblinding permits only sealed or unblinded blocks")
    elif status == "unblinded":
        if not all(block["status"] == "unblinded" for block in blocks):
            _fail("scenario-bundle-unblinding-state-mismatch", "unblinded bundle requires every child report")
        if not all(children[block["block_id"]]["status"] == "unblinded" for block in blocks):
            _fail("scenario-bundle-unblinding-state-mismatch", "unblinded bundle contains a blinded child")

    report: dict[str, Any] | None = None
    report_ref_value = manifest.get("report")
    if report_ref_value is not None:
        if status != "unblinded":
            _fail("bad-scenario-bundle", "bundle report may be referenced only after complete unblinding")
        try:
            unblinded_at = require_string(manifest.get("unblinded_at"), "unblinded_at", max_len=128)
        except ValueError as exc:
            raise LacunaError("bad-scenario-bundle", str(exc)) from exc
        report_ref = _validate_ref(
            report_ref_value,
            expected_path=BUNDLE_REPORT_FILE,
            expected_schema=BUNDLE_REPORT_SCHEMA,
            expected_role="lacuna-scenario-bundle-runner",
            label="report",
        )
        expected_report = _build_bundle_report(
            manifest={**copy.deepcopy(manifest), "blocks": blocks},
            plan=plan,
            commitment=commitment,
            witnesses=witnesses,
            seals=seals,
            children=children,
            child_paths=child_paths,
            unblinded_at=unblinded_at,
        )
        report = _validate_bundle_report(
            _read_ref_json(storage_path, report_ref, label="scenario bundle report"),
            expected=expected_report,
        )
    elif status == "unblinded":
        _fail("bad-scenario-bundle", "unblinded bundle is missing its deterministic report")
    elif status != "unblinding" and manifest.get("unblinded_at") is not None:
        _fail("bad-scenario-bundle", "unblinded_at is permitted only during or after bundle unblinding")

    next_action = _strict(
        manifest.get("next_action"),
        label="next_action",
        fields=NEXT_ACTION_FIELDS,
        code="bad-scenario-bundle",
    )
    if strict_cached_state:
        normalized_manifest = copy.deepcopy(manifest)
        normalized_manifest["blocks"] = blocks
        normalized_manifest["witnesses"] = normalized_witness_refs
        normalized_manifest["status"] = expected_status
        expected_next = _next_action(
            authority_path,
            normalized_manifest,
            child_manifests=children,
        )
        if next_action != expected_next:
            _fail("scenario-bundle-next-action-mismatch", "next_action is not deterministic")
        if audit_next:
            _audit_bundle_next(storage_path, manifest)

    return {
        "manifest": copy.deepcopy(manifest),
        "plan": plan,
        "schedule": schedule,
        "commitment": commitment,
        "witnesses": witnesses,
        "seals": seals,
        "children": children,
        "child_paths": child_paths,
        "assignments": assignments,
        "expected_status": expected_status,
    }


def audit_scenario_bundle(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        return _inspect_bundle_unlocked(bundle_path)["manifest"]


def _reconcile_bundle_manifest_unlocked(
    storage_path: Path,
    inspection: dict[str, Any],
    *,
    touch: bool,
) -> dict[str, Any]:
    manifest = copy.deepcopy(inspection["manifest"])
    children = inspection["children"]
    if manifest["status"] in {"awaiting-witnesses", "block-active", "block-ready-to-seal"}:
        manifest["status"] = inspection["expected_status"]
    elif manifest["status"] == "unblinding":
        for block in manifest["blocks"]:
            child = children[block["block_id"]]
            if child["status"] == "unblinded":
                if block["status"] not in {"sealed", "unblinded"}:
                    _fail(
                        "scenario-bundle-premature-unblinding",
                        "cannot recover an unblinded child that was not first sealed",
                        {"block_id": block["block_id"]},
                    )
                block["status"] = "unblinded"
                block["scenario_report_sha256"] = child["report"]["sha256"]
    if touch:
        manifest["updated_at"] = utc_now()
    _write_bundle_manifest(
        storage_path,
        manifest,
        authority_path=Path(manifest["bundle_path"]),
        child_manifests=children,
    )
    return manifest


def recover_scenario_bundle(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(
            bundle_path,
            audit_next=False,
            strict_cached_state=False,
        )
        _reconcile_bundle_manifest_unlocked(bundle_path, inspection, touch=True)
        return _inspect_bundle_unlocked(bundle_path)["manifest"]


def scenario_bundle_commitment(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        return _inspect_bundle_unlocked(bundle_path)["commitment"]


def record_scenario_bundle_witness(
    value: str | Path,
    witness_value: dict[str, Any],
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        manifest = copy.deepcopy(inspection["manifest"])
        if any(not _scenario_is_pristine(child) for child in inspection["children"].values()):
            _fail("scenario-bundle-witness-window-closed", "witness receipts must be recorded before any child advances")
        if any(block["status"] != ("active" if block["ordinal"] == 1 else "pending") for block in manifest["blocks"]):
            _fail("scenario-bundle-witness-window-closed", "witness receipts must be recorded before block sealing")
        if len(manifest["witnesses"]) >= MAX_BUNDLE_WITNESSES:
            _fail(
                "scenario-bundle-witness-limit",
                f"scenario bundle v1 retains at most {MAX_BUNDLE_WITNESSES} witness receipts",
            )
        witness = _validate_witness(witness_value, manifest=manifest)
        if any(ref["witness_id"] == witness["witness_id"] for ref in manifest["witnesses"]):
            _fail("duplicate-scenario-bundle-witness", "witness_id is already retained")
        if any(
            ref["external_receipt_id"] == witness["external_receipt_id"]
            for ref in manifest["witnesses"]
        ):
            _fail(
                "duplicate-scenario-bundle-witness-receipt",
                "external_receipt_id is already retained",
            )
        sequence = len(manifest["witnesses"]) + 1
        relative = _witness_relative_path(sequence)
        write_sidecar_json_once_or_verify(
            bundle_path / PurePosixPath(relative),
            witness,
            label="scenario bundle witness",
            error_prefix="scenario-bundle",
            mismatch_code="scenario-bundle-witness-publication-mismatch",
        )
        ref = _artifact_ref(
            path=relative,
            value=witness,
            schema=BUNDLE_WITNESS_SCHEMA,
            role="external-witness-record",
        )
        ref["witness_id"] = witness["witness_id"]
        ref["external_receipt_id"] = witness["external_receipt_id"]
        manifest["witnesses"].append(ref)
        minimum = inspection["plan"]["witness_policy"]["minimum_receipts_before_execution"]
        if len(manifest["witnesses"]) >= minimum:
            manifest["status"] = "block-active"
        manifest["updated_at"] = utc_now()
        _write_bundle_manifest(
            bundle_path,
            manifest,
            authority_path=bundle_path,
            child_manifests=inspection["children"],
        )
        _inspect_bundle_unlocked(bundle_path)
        return witness


def _active_bundle_block(inspection: dict[str, Any]) -> tuple[dict[str, Any], Path]:
    active = [block for block in inspection["manifest"]["blocks"] if block["status"] == "active"]
    if len(active) != 1:
        _fail("scenario-bundle-no-active-block", "bundle has no unique active block")
    block = active[0]
    return block, inspection["child_paths"][block["block_id"]]


def _refresh_after_child_transition(
    bundle_path: Path,
) -> dict[str, Any]:
    inspection = _inspect_bundle_unlocked(
        bundle_path,
        audit_next=False,
        strict_cached_state=False,
    )
    _reconcile_bundle_manifest_unlocked(bundle_path, inspection, touch=True)
    return _inspect_bundle_unlocked(bundle_path)["manifest"]


def dispatch_scenario_bundle_cell(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail(
                "scenario-bundle-not-block-active",
                "a child cell can be dispatched only while one preregistered block is active",
                {"status": inspection["manifest"]["status"]},
            )
        _, child_path = _active_bundle_block(inspection)
        driver = dispatch_scenario_cell(child_path)
        _refresh_after_child_transition(bundle_path)
        return driver


def _preflight_bundle_invocation_custody(
    inspection: dict[str, Any],
    *,
    active_block_id: str,
    cell_return: dict[str, Any],
) -> None:
    prior_contexts: dict[str, str] = {}
    prior_invocations: dict[str, str] = {}
    for block in inspection["manifest"]["blocks"]:
        if block["block_id"] == active_block_id:
            continue
        child = inspection["children"][block["block_id"]]
        child_path = inspection["child_paths"][block["block_id"]]
        for invocation in _collect_child_invocations(child_path, child):
            prior_contexts[invocation["context_id"]] = block["block_id"]
            if invocation["invocation_id"] is not None:
                prior_invocations[invocation["invocation_id"]] = block["block_id"]
    invocations = cell_return.get("invocations")
    if not isinstance(invocations, list):
        return
    seen_candidate_invocations: set[str] = set()
    for value_item in invocations:
        if not isinstance(value_item, dict):
            continue
        context_id = value_item.get("context_id")
        if isinstance(context_id, str) and context_id in prior_contexts:
            _fail(
                "scenario-bundle-cross-block-context-reuse",
                "candidate cell return reuses a declared model context_id from an earlier block",
                {
                    "context_id": context_id,
                    "first_block": prior_contexts[context_id],
                    "second_block": active_block_id,
                },
            )
        invocation_id = value_item.get("invocation_id")
        if isinstance(invocation_id, str):
            if invocation_id in prior_invocations:
                _fail(
                    "scenario-bundle-duplicate-invocation-id",
                    "candidate cell return reuses an invocation_id from an earlier block",
                    {
                        "invocation_id": invocation_id,
                        "first_block": prior_invocations[invocation_id],
                        "second_block": active_block_id,
                    },
                )
            if invocation_id in seen_candidate_invocations:
                _fail(
                    "scenario-bundle-duplicate-invocation-id",
                    "candidate cell return repeats a non-null invocation_id",
                    {"invocation_id": invocation_id},
                )
            seen_candidate_invocations.add(invocation_id)


def record_scenario_bundle_cell(
    value: str | Path,
    cell_return: dict[str, Any],
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail("scenario-bundle-not-block-active", "cell returns are accepted only for the active block")
        block, child_path = _active_bundle_block(inspection)
        _preflight_bundle_invocation_custody(
            inspection,
            active_block_id=block["block_id"],
            cell_return=cell_return,
        )
        record_scenario_cell(child_path, cell_return)
        return _refresh_after_child_transition(bundle_path)


def scenario_bundle_rating_template(
    value: str | Path,
    *,
    rater_id: str = "rater.replace-me",
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail("scenario-bundle-not-awaiting-ratings", "the active block is not accepting blind ratings")
        _, child_path = _active_bundle_block(inspection)
        return scenario_rating_template(child_path, rater_id=rater_id)


def record_scenario_bundle_rating(
    value: str | Path,
    rating: dict[str, Any],
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail("scenario-bundle-not-awaiting-ratings", "ratings are accepted only for the active block")
        _, child_path = _active_bundle_block(inspection)
        record_scenario_rating(child_path, rating)
        return _refresh_after_child_transition(bundle_path)


def scenario_bundle_masking_template(
    value: str | Path,
    *,
    assessor_id: str = "rater.replace-me",
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail("scenario-bundle-not-awaiting-masking", "the active block is not accepting masking assessments")
        _, child_path = _active_bundle_block(inspection)
        return scenario_masking_template(child_path, assessor_id=assessor_id)


def record_scenario_bundle_masking(
    value: str | Path,
    masking: dict[str, Any],
) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "block-active":
            _fail("scenario-bundle-not-awaiting-masking", "masking assessments are accepted only for the active block")
        _, child_path = _active_bundle_block(inspection)
        record_scenario_masking(child_path, masking)
        return _refresh_after_child_transition(bundle_path)


def seal_scenario_bundle_block(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        manifest = copy.deepcopy(inspection["manifest"])
        if manifest["status"] != "block-ready-to-seal":
            _fail(
                "scenario-bundle-block-not-ready",
                "the active block can be sealed only after every fixed blind rating is retained",
                {"status": manifest["status"]},
            )
        block, _ = _active_bundle_block(inspection)
        child = inspection["children"][block["block_id"]]
        relative = _seal_relative_path(block)
        seal_path = bundle_path / PurePosixPath(relative)
        if os.path.lexists(seal_path):
            seal = _validate_block_seal(
                read_sidecar_json_object(
                    seal_path,
                    label="scenario bundle block seal",
                    error_prefix="scenario-bundle",
                    root_error_code="bad-scenario-bundle-block-seal",
                ),
                manifest=manifest,
                block=block,
                child=child,
            )
        else:
            seal = _build_block_seal(
                manifest=manifest,
                block=block,
                child=child,
                sealed_at=utc_now(),
            )
            write_sidecar_json_once_or_verify(
                seal_path,
                seal,
                label="scenario bundle block seal",
                error_prefix="scenario-bundle",
                mismatch_code="scenario-bundle-block-seal-publication-mismatch",
            )
        target = next(item for item in manifest["blocks"] if item["block_id"] == block["block_id"])
        target["status"] = "sealed"
        target["seal"] = _artifact_ref(
            path=relative,
            value=seal,
            schema=BUNDLE_BLOCK_SEAL_SCHEMA,
            role="lacuna-scenario-bundle-runner",
        )
        next_pending = next((item for item in manifest["blocks"] if item["status"] == "pending"), None)
        if next_pending is None:
            manifest["status"] = "ready-to-unblind"
        else:
            next_pending["status"] = "active"
            manifest["status"] = "block-active"
        manifest["updated_at"] = utc_now()
        _write_bundle_manifest(
            bundle_path,
            manifest,
            authority_path=bundle_path,
            child_manifests=inspection["children"],
        )
        _inspect_bundle_unlocked(bundle_path)
        return seal


def unblind_scenario_bundle(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(
            bundle_path,
            audit_next=False,
            strict_cached_state=False,
        )
        manifest = _reconcile_bundle_manifest_unlocked(bundle_path, inspection, touch=False)
        inspection = _inspect_bundle_unlocked(
            bundle_path,
            audit_next=False,
            strict_cached_state=False,
        )
        manifest = copy.deepcopy(inspection["manifest"])
        if manifest["status"] == "unblinded":
            if manifest["report"] is None:
                _fail(
                    "bad-scenario-bundle",
                    "unblinded bundle is missing its deterministic report reference",
                )
            return _read_ref_json(bundle_path, manifest["report"], label="scenario bundle report")
        if manifest["status"] == "ready-to-unblind":
            manifest["status"] = "unblinding"
            manifest["unblinded_at"] = utc_now()
            manifest["updated_at"] = manifest["unblinded_at"]
            _write_bundle_manifest(
                bundle_path,
                manifest,
                authority_path=bundle_path,
                child_manifests=inspection["children"],
            )
        elif manifest["status"] != "unblinding":
            _fail(
                "scenario-bundle-not-ready-to-unblind",
                "all preregistered blocks must be sealed before bundle unblinding",
                {"status": manifest["status"]},
            )

        for block_index in range(len(manifest["blocks"])):
            inspection = _inspect_bundle_unlocked(
                bundle_path,
                audit_next=False,
                strict_cached_state=False,
            )
            manifest = copy.deepcopy(inspection["manifest"])
            block = manifest["blocks"][block_index]
            child = inspection["children"][block["block_id"]]
            child_path = inspection["child_paths"][block["block_id"]]
            if child["status"] != "unblinded":
                if block["status"] != "sealed" or child["status"] != "ready-to-unblind":
                    _fail(
                        "scenario-bundle-unblinding-state-mismatch",
                        "only a previously sealed ready child can be unblinded",
                        {"block_id": block["block_id"]},
                    )
                seal = inspection["seals"].get(block["block_id"])
                if seal is None:
                    _fail("scenario-bundle-unblinding-state-mismatch", "sealed block is missing its block-seal custody", {"block_id": block["block_id"]})
                open_scenario_unblind_gate(
                    child_path,
                    bundle_id=manifest["bundle_id"],
                    block_id=block["block_id"],
                    opening_sha256=_digest(seal, label="scenario bundle block seal"),
                )
                unblind_scenario_run(child_path)
                with _scenario_run_lock(child_path):
                    child = _audit_scenario_run_unlocked(child_path)
            block["status"] = "unblinded"
            block["scenario_report_sha256"] = child["report"]["sha256"]
            manifest["updated_at"] = utc_now()
            child_manifests = copy.deepcopy(inspection["children"])
            child_manifests[block["block_id"]] = child
            _write_bundle_manifest(
                bundle_path,
                manifest,
                authority_path=bundle_path,
                child_manifests=child_manifests,
            )

        inspection = _inspect_bundle_unlocked(
            bundle_path,
            audit_next=False,
            strict_cached_state=False,
        )
        manifest = copy.deepcopy(inspection["manifest"])
        if manifest["unblinded_at"] is None:
            _fail(
                "bad-scenario-bundle",
                "unblinding bundle is missing its fixed unblinded_at timestamp",
            )
        report = _build_bundle_report(
            manifest=manifest,
            plan=inspection["plan"],
            commitment=inspection["commitment"],
            witnesses=inspection["witnesses"],
            seals=inspection["seals"],
            children=inspection["children"],
            child_paths=inspection["child_paths"],
            unblinded_at=manifest["unblinded_at"],
        )
        _validate_bundle_report(report, expected=report)
        write_sidecar_json_once_or_verify(
            bundle_path / BUNDLE_REPORT_FILE,
            report,
            label="scenario bundle report",
            error_prefix="scenario-bundle",
            mismatch_code="scenario-bundle-report-publication-mismatch",
        )
        manifest["report"] = _artifact_ref(
            path=BUNDLE_REPORT_FILE,
            value=report,
            schema=BUNDLE_REPORT_SCHEMA,
            role="lacuna-scenario-bundle-runner",
        )
        manifest["status"] = "unblinded"
        manifest["updated_at"] = utc_now()
        _write_bundle_manifest(
            bundle_path,
            manifest,
            authority_path=bundle_path,
            child_manifests=inspection["children"],
        )
        _inspect_bundle_unlocked(bundle_path)
        return report


def scenario_bundle_run_markdown(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    sealed = sum(block["status"] in {"sealed", "unblinded"} for block in manifest["blocks"])
    lines = [
        "# Lacuna preregistered scenario bundle",
        "",
        f"- Bundle: `{manifest['bundle_id']}`",
        f"- Path: `{manifest['bundle_path']}`",
        f"- Status: **{manifest['status']}**",
        f"- Blocks sealed: **{sealed}/{len(manifest['blocks'])}**",
        f"- Witness receipts: **{len(manifest['witnesses'])}**",
        f"- Commitment: `{manifest['commitment']['sha256']}`",
        "",
        "## Next action",
        "",
        f"Owner: **{action['owner']}**",
        "",
        action["action"],
    ]
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["expected_schema"] is not None:
        lines.extend(["", f"Expected schema: `{action['expected_schema']}`"])
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.append("")
    return "\n".join(lines)


def scenario_bundle_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Lacuna scenario bundle — unblinded descriptive report",
        "",
        report["research_question"],
        "",
        f"- Blocks: **{report['descriptive_summary']['block_count']}**",
        f"- Rater-level condition observations: **{report['descriptive_summary']['observation_count']}**",
        f"- Commitment: `{report['commitment_sha256']}`",
        f"- Canary-clean blocks: **{report['descriptive_summary']['contamination']['clean_blocks']}**",
        f"- Canary-leak blocks: **{report['descriptive_summary']['contamination']['leak_detected_blocks']}**",
        f"- Unexpected exact-token matches: **{report['descriptive_summary']['contamination']['unexpected_match_count']}**",
        "",
        "## Retained cell outcomes",
        "",
        "| Condition | Completed | Refused | Failed |",
        "|---|---:|---:|---:|",
    ]
    status = report["descriptive_summary"]["cell_status"]
    for condition in SCENARIO_CONDITIONS:
        lines.append(
            f"| `{condition}` | {status[condition]['completed']} | {status[condition]['refused']} | {status[condition]['failed']} |"
        )
    lines.extend(
        [
            "",
            "The JSON and CSV retain rater-level ordinal scores, preference ranks, strata, failures, and mechanical outcomes. No significance or causal claim is computed by this artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def scenario_bundle_report_csv(report: dict[str, Any]) -> str:
    if report.get("schema") != BUNDLE_REPORT_SCHEMA:
        _fail("bad-scenario-bundle-report", "CSV export requires the current lacuna.scenario-bundle-report object")

    def spreadsheet_safe(value: Any) -> Any:
        """Keep CSV text inert when a human opens it in spreadsheet software.

        JSON remains the exact canonical export.  CSV is a convenience view, so
        prefix text whose first non-space character can be interpreted as a
        spreadsheet formula.  RFC 4180 quoting alone does not neutralize those
        formulas in common spreadsheet programs.
        """
        if not isinstance(value, str) or not value:
            return value
        stripped = value.lstrip()
        if value[0] in {"\t", "\r", "\n"} or (
            stripped and stripped[0] in {"=", "+", "-", "@"}
        ):
            return "'" + value
        return value

    total_fields = [
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
    ]
    base_fields = [
        "block_ordinal",
        "block_id",
        "story_stratum",
        "model_stratum",
        "replicate",
        "scenario_run_id",
        "rater_id",
        "condition",
        "cell_label",
        "cell_status",
        "contamination_status",
        "contamination_unexpected_match_count",
    ]
    tail_fields = [
        "preference_rank",
        "method_guess",
        "method_guess_correct",
        "method_guess_confidence",
        "method_guess_recognized",
        "method_guess_familiarity",
        "method_guess_cues",
        "comments",
        "transcript_sha256",
        "final_head",
        "event_count_delta",
    ]
    fieldnames = base_fields + list(HUMAN_RATING_DIMENSIONS) + tail_fields + total_fields
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for observation in report["observations"]:
        row = {field: observation[field] for field in base_fields}
        row.update(observation["scores"])
        row.update(
            {
                field: (
                    " | ".join(observation[field])
                    if field == "method_guess_cues"
                    else observation[field]
                )
                for field in tail_fields
            }
        )
        row.update({field: observation["execution_totals"][field] for field in total_fields})
        writer.writerow({field: spreadsheet_safe(value) for field, value in row.items()})
    return output.getvalue()


def scenario_bundle_report(value: str | Path) -> dict[str, Any]:
    bundle_path = _bundle_directory(value)
    with _bundle_lock(bundle_path):
        inspection = _inspect_bundle_unlocked(bundle_path)
        if inspection["manifest"]["status"] != "unblinded":
            _fail("scenario-bundle-not-unblinded", "bundle report is available only after complete unblinding")
        report_ref = inspection["manifest"]["report"]
        if report_ref is None:
            _fail(
                "bad-scenario-bundle",
                "unblinded bundle is missing its deterministic report reference",
            )
        return _read_ref_json(bundle_path, report_ref, label="scenario bundle report")

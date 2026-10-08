from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, ContextManager

from . import __version__
from .checkpoints import (
    CHECKPOINT_CANDIDATES_SCHEMA,
    CHECKPOINT_COMMIT_SCHEMA,
    CHECKPOINT_COMPRESSION_SCHEMA,
    CHECKPOINT_JUDGMENT_SCHEMA,
    CHECKPOINT_REQUEST_SCHEMA,
    CHECKPOINT_REVIEW_SCHEMA,
    CHECKPOINT_ROLE_OUTPUT_SCHEMAS,
    CHECKPOINT_ROLES,
    CHECKPOINT_TASK_CARD_SCHEMA,
    CHECKPOINT_VERIFIER_SCHEMA,
    assemble_checkpoint_proposal,
    build_checkpoint_request,
    build_checkpoint_task_card,
    checkpoint_task_card_sha256,
    commit_checkpoint,
    review_checkpoint,
    validate_checkpoint_candidates,
    _validate_checkpoint_commit_receipt_document,
    validate_checkpoint_compression,
    validate_checkpoint_judgment,
    validate_checkpoint_request,
    validate_checkpoint_review,
    validate_checkpoint_task_card,
    validate_checkpoint_verifier,
)
from .continuation import (
    CHECKPOINT_CONTINUATION_DISPATCH_SCHEMA,
    build_checkpoint_continuation_dispatch as build_continuation_dispatch_document,
    build_checkpoint_narrator_capsule,
)
from .errors import LacunaError
from .orchestration import validate_turn_packet
from .providers import PROVIDERS, provider_alias
from .public_history import authenticate_public_history
from .sidecars import (
    canonical_json_digest,
    ensure_sidecar_lock,
    publish_private_directory,
    read_sidecar_json_object,
    read_sidecar_text,
    resolve_sidecar_directory,
    shell_command,
    sidecar_lock,
)
from .store import Cube
from .turnruns import (
    ARTIFACT_FILES as TURN_RUN_ARTIFACT_FILES,
    _audit_turn_run_unlocked,
    begin_turn_run,
    _run_directory as _turn_run_directory,
    _run_lock as _turn_run_lock,
)
from .util import (
    SHA256_RE,
    atomic_write_json,
    atomic_write_text,
    new_id,
    pretty_json,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

CHECKPOINT_RUN_SCHEMA = "lacuna.checkpoint-run.v1"
CHECKPOINT_RUN_EVENT = "lacuna.checkpoint.run"
CHECKPOINT_RUN_DISPATCH_SCHEMA = "lacuna.checkpoint-run-agent-dispatch.v1"
CHECKPOINT_INVOCATION_RECEIPT_SCHEMA = "lacuna.checkpoint-invocation-receipt.v1"

CHECKPOINT_RUN_STATUSES = (
    "awaiting-generator",
    "awaiting-judge",
    "awaiting-compressor",
    "awaiting-verifier",
    "verifier-refused",
    "ready-to-commit",
    "committed",
)

RUN_MANIFEST_FILE = "run.json"
NEXT_FILE = "NEXT.md"
RUN_LOCK_FILE = ".run.lock"
ARTIFACT_FILES = {
    "trigger": "00-trigger.txt",
    "request": "10-checkpoint-request.json",
    "generator_card": "20-generator-card.json",
    "candidates": "21-candidates.json",
    "judge_card": "30-judge-card.json",
    "judgment": "31-judgment.json",
    "compressor_card": "40-compressor-card.json",
    "compression": "41-compression.json",
    "proposal": "50-checkpoint-proposal.json",
    "verifier_card": "60-verifier-card.json",
    "verifier_return": "61-verifier-return.json",
    "review": "70-checkpoint-review.json",
    "receipt": "80-checkpoint-receipt.json",
}
ARTIFACT_KEYS = tuple(ARTIFACT_FILES)

ROLE_STAGE = {
    "lacuna-retcon-generator": "awaiting-generator",
    "lacuna-retcon-judge": "awaiting-judge",
    "lacuna-retcon-compressor": "awaiting-compressor",
    "lacuna-retcon-verifier": "awaiting-verifier",
}
ROLE_CARD_KEY = {
    "lacuna-retcon-generator": "generator_card",
    "lacuna-retcon-judge": "judge_card",
    "lacuna-retcon-compressor": "compressor_card",
    "lacuna-retcon-verifier": "verifier_card",
}
ROLE_OUTPUT_KEY = {
    "lacuna-retcon-generator": "candidates",
    "lacuna-retcon-judge": "judgment",
    "lacuna-retcon-compressor": "compression",
    "lacuna-retcon-verifier": "verifier_return",
}
ROLE_SLUG = {
    "lacuna-retcon-generator": "generator",
    "lacuna-retcon-judge": "judge",
    "lacuna-retcon-compressor": "compressor",
    "lacuna-retcon-verifier": "verifier",
}
ROLE_ORDER = {role: index for index, role in enumerate(CHECKPOINT_ROLES)}
STATUS_ROLE = {stage: role for role, stage in ROLE_STAGE.items()}

ARTIFACT_METADATA = {
    "trigger": ("text/plain; charset=utf-8", None, "parent-coordinator"),
    "request": ("application/json", CHECKPOINT_REQUEST_SCHEMA, "parent-coordinator"),
    "generator_card": ("application/json", CHECKPOINT_TASK_CARD_SCHEMA, "lacuna-retcon-generator"),
    "candidates": ("application/json", CHECKPOINT_CANDIDATES_SCHEMA, "lacuna-retcon-generator"),
    "judge_card": ("application/json", CHECKPOINT_TASK_CARD_SCHEMA, "lacuna-retcon-judge"),
    "judgment": ("application/json", CHECKPOINT_JUDGMENT_SCHEMA, "lacuna-retcon-judge"),
    "compressor_card": ("application/json", CHECKPOINT_TASK_CARD_SCHEMA, "lacuna-retcon-compressor"),
    "compression": ("application/json", CHECKPOINT_COMPRESSION_SCHEMA, "lacuna-retcon-compressor"),
    "proposal": ("application/json", "lacuna.checkpoint-proposal.v1", "parent-coordinator"),
    "verifier_card": ("application/json", CHECKPOINT_TASK_CARD_SCHEMA, "lacuna-retcon-verifier"),
    "verifier_return": ("application/json", CHECKPOINT_VERIFIER_SCHEMA, "lacuna-retcon-verifier"),
    "review": ("application/json", CHECKPOINT_REVIEW_SCHEMA, "lacuna-kernel"),
    "receipt": ("application/json", CHECKPOINT_COMMIT_SCHEMA, "parent-coordinator"),
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
    "resolved_cube_path",
    "cube_id",
    "status",
    "provider_routes",
    "checkpoint_identity",
    "artifacts",
    "invocations",
    "next_action",
    "nonclaims",
}
ARTIFACT_FIELDS = {"path", "sha256", "media_type", "schema", "role"}
CHECKPOINT_IDENTITY_FIELDS = {
    "checkpoint_id",
    "expected_head",
    "trigger_sha256",
    "request_sha256",
    "turn_packet_sha256",
}
NEXT_ACTION_FIELDS = {
    "owner",
    "provider",
    "agent_name",
    "action",
    "input_path",
    "expected_schema",
    "command",
    "player_visibility",
}
INVOCATION_FIELDS = {
    "event",
    "schema",
    "run_id",
    "checkpoint_id",
    "sequence",
    "attempt",
    "role",
    "provider",
    "agent_name",
    "card_sha256",
    "dispatch_sha256",
    "expected_output_schema",
    "model",
    "model_version",
    "invocation_id",
    "started_at",
    "completed_at",
    "duration_ms",
    "outcome",
    "output_artifact",
    "failure_class",
    "failure_message",
    "recorded_at",
    "declaration",
    "nonclaims",
}
INVOCATION_OUTPUT_FIELDS = {"path", "sha256", "schema"}
MAX_INVOCATIONS = 1000
INVOCATION_FAILURE_CLASSES = {
    "provider-error",
    "timeout",
    "transport-error",
    "invalid-output",
    "worker-refusal",
    "interrupted",
    "other",
}
INVOCATION_FILENAME_RE = re.compile(
    r"^invocation-(?P<sequence>[0-9]{4})-(?P<role>generator|judge|compressor|verifier)\.json$"
)
INVOCATION_NONCLAIMS = [
    "This receipt is a host declaration, not a provider-signed attestation of model identity, isolation, timing, or execution.",
    "The dispatch and output digests prove retained byte-equivalent JSON custody under Lacuna canonicalization, not that the worker followed the prompt.",
    "A failed invocation record does not advance the checkpoint; only one validated accepted output can advance its role.",
]
CHECKPOINT_RUN_NONCLAIMS = [
    "The checkpoint run is a private host sidecar, not a ledger event, provider invocation, authority grant, or proof of worker isolation.",
    "Provider routes are fixed routing metadata; invocation receipts remain host declarations rather than vendor attestations.",
    "Candidate rollouts, judgments, compression, and rejected futures remain noncanon unless the exact reviewed checkpoint commits.",
    "Only the parent coordinator may accept outputs, assemble the proposal, run kernel review, commit or recover, and present narration.",
    "Ready-to-commit means exact rollback preparation passed; it is not commitment and does not reserve the source head.",
    "The sidecar lock coordinates cooperative same-host callers only and does not create a hostile-user or distributed security boundary.",
    "The run retains privileged hidden futures outside the event ledger and supplies no bundled encryption, archival, redaction, or deletion guarantee.",
]


def _fail(code: str, message: str, details: dict[str, Any] | None = None) -> None:
    raise LacunaError(code, message, details)


def _digest(value: Any, *, label: str = "checkpoint run artifact") -> str:
    return canonical_json_digest(
        value,
        error_code="bad-checkpoint-run-artifact",
        label=label,
    )


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


def _optional_string(value: Any, field: str, *, max_len: int = 4096) -> str | None:
    if value is None:
        return None
    try:
        return require_string(value, field, allow_empty=True, max_len=max_len)
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-invocation-receipt", str(exc)) from exc


def _artifact_ref(
    *,
    filename: str,
    sha256: str,
    media_type: str,
    schema: str | None,
    role: str | None,
) -> dict[str, Any]:
    return {
        "path": filename,
        "sha256": sha256,
        "media_type": media_type,
        "schema": schema,
        "role": role,
    }


def _write_json_artifact(run_path: Path, key: str, value: dict[str, Any]) -> dict[str, Any]:
    filename = ARTIFACT_FILES[key]
    atomic_write_json(run_path / filename, value)
    media_type, schema, role = ARTIFACT_METADATA[key]
    return _artifact_ref(
        filename=filename,
        sha256=_digest(value),
        media_type=media_type,
        schema=schema,
        role=role,
    )


def _write_trigger(run_path: Path, trigger: str) -> dict[str, Any]:
    filename = ARTIFACT_FILES["trigger"]
    atomic_write_text(run_path / filename, trigger)
    media_type, schema, role = ARTIFACT_METADATA["trigger"]
    return _artifact_ref(
        filename=filename,
        sha256=sha256_text(trigger),
        media_type=media_type,
        schema=schema,
        role=role,
    )


def _read_json(run_path: Path, key: str, *, label: str | None = None) -> dict[str, Any]:
    return read_sidecar_json_object(
        run_path / ARTIFACT_FILES[key],
        label=label or key.replace("_", " "),
        error_prefix="checkpoint-run",
        root_error_code="bad-checkpoint-run-artifact",
    )


def _run_directory(value: str | Path) -> Path:
    return resolve_sidecar_directory(
        value,
        manifest_file=RUN_MANIFEST_FILE,
        unknown_code="unknown-checkpoint-run",
        kind_label="checkpoint run",
    )


def _run_lock(run_path: Path) -> ContextManager[None]:
    return sidecar_lock(
        run_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="checkpoint-run",
        kind_label="checkpoint run",
        busy_message="another coordinator is advancing this checkpoint run",
    )


def normalize_checkpoint_provider_routes(
    *,
    provider: str = "portable",
    generator_provider: str | None = None,
    judge_provider: str | None = None,
    compressor_provider: str | None = None,
    verifier_provider: str | None = None,
) -> dict[str, str]:
    values = {
        "lacuna-retcon-generator": generator_provider if generator_provider is not None else provider,
        "lacuna-retcon-judge": judge_provider if judge_provider is not None else provider,
        "lacuna-retcon-compressor": compressor_provider if compressor_provider is not None else provider,
        "lacuna-retcon-verifier": verifier_provider if verifier_provider is not None else provider,
    }
    bad = {role: value for role, value in values.items() if value not in PROVIDERS}
    if bad:
        _fail(
            "unknown-checkpoint-provider",
            f"every provider route must be one of {list(PROVIDERS)}",
            {"invalid_routes": bad},
        )
    return values


def _validate_provider_routes(value: Any) -> dict[str, str]:
    routes = _strict(
        value,
        label="provider_routes",
        fields=set(CHECKPOINT_ROLES),
        code="bad-checkpoint-run",
    )
    normalized: dict[str, str] = {}
    for role in CHECKPOINT_ROLES:
        provider = routes.get(role)
        if provider not in PROVIDERS:
            _fail(
                "bad-checkpoint-run",
                f"provider_routes.{role} must be one of {list(PROVIDERS)}",
            )
        normalized[role] = provider
    return normalized


def _current_stage(status: str) -> tuple[str, str, str, str] | None:
    role = STATUS_ROLE.get(status)
    if role is None:
        return None
    return role, ROLE_CARD_KEY[role], ROLE_OUTPUT_KEY[role], CHECKPOINT_ROLE_OUTPUT_SCHEMAS[role]


def _checkpoint_run_dispatch_document(
    manifest: dict[str, Any],
    card: dict[str, Any],
) -> dict[str, Any]:
    role = card["role"]
    provider = manifest["provider_routes"][role]
    status = ROLE_STAGE[role]
    save_path = str(Path(manifest["run_path"]) / "MODEL_RETURN.json")
    accept_command = shell_command(
        [
            "./lacuna",
            "checkpoint",
            "run",
            "accept",
            manifest["run_path"],
            save_path,
            "--model",
            "unknown",
        ]
    )
    failure_command = shell_command(
        [
            "./lacuna",
            "checkpoint",
            "run",
            "record-failure",
            manifest["run_path"],
            "--failure-class",
            "other",
            "--model",
            "unknown",
        ]
    )
    return {
        "event": "lacuna.checkpoint.run.agent-dispatch",
        "schema": CHECKPOINT_RUN_DISPATCH_SCHEMA,
        "run_id": manifest["run_id"],
        "run_path": manifest["run_path"],
        "status": status,
        "checkpoint_id": manifest["checkpoint_identity"]["checkpoint_id"],
        "task_id": card["task_id"],
        "provider": provider,
        "role": role,
        "agent_name": provider_alias(role, provider),
        "input_card_sha256": checkpoint_task_card_sha256(card),
        "input_card": card,
        "return_contract": {
            "schema": card["output_contract"]["schema"],
            "format": "one exact JSON object; no prose, Markdown, or code fence",
            "save_path": save_path,
            "accept_command": accept_command,
        },
        "invocation_contract": {
            "declaration": "host-declared",
            "accepted_command_records": [
                "provider route fixed by run.json",
                "model and optional model version",
                "optional provider invocation identifier",
                "optional start, completion, and duration metadata",
                "exact card, dispatch, and accepted output digests",
            ],
            "failure_command": failure_command,
        },
        "instructions": [
            f"Act as exactly one {role} context using provider alias {provider_alias(role, provider)!r}; perform the task rather than summarizing this handoff.",
            "The complete and exact task card is input_card in this envelope; do not ask for local files or reconstruct omitted context.",
            "Use the card's already-sized output template: fill every required candidate, rollout beat, score, check, or list exactly as specified.",
            "Return one JSON object matching return_contract.schema with no prose, Markdown, code fence, or second root.",
            "Do not read other run artifacts, edit the sidecar, select a later role, accept your own output, review, commit, or present narration.",
            "The parent coordinator alone saves the exact return, records host-declared invocation metadata, validates it, and manufactures the next least-context card.",
        ],
        "authority": card["authority"],
        "nonclaims": [
            "This envelope does not invoke, authenticate, isolate, or attest any provider, model, or subagent.",
            "The configured route and agent name are routing metadata, not evidence of worker identity or independence.",
            "A valid-looking return remains untrusted until checkpoint run accept validates it against the retained exact chain.",
            "Only checkpoint run commit can mutate or recover the cube transition; worker contexts have no such authority.",
        ],
    }


def _next_action(run_path: Path, status: str, artifacts: dict[str, Any], routes: dict[str, str]) -> dict[str, Any]:
    stage = _current_stage(status)
    hidden = "Keep every checkpoint artifact backstage; only accepted receipt narration may become player-visible."
    if stage is not None:
        role, card_key, _output_key, output_schema = stage
        provider = routes[role]
        return {
            "owner": role,
            "provider": provider,
            "agent_name": provider_alias(role, provider),
            "action": (
                "Render the exact self-contained dispatch, give it to one role-dedicated context, "
                "save only the returned JSON object, then run the dispatch's parent accept command."
            ),
            "input_path": str(run_path / ARTIFACT_FILES[card_key]),
            "expected_schema": output_schema,
            "command": shell_command(
                ["./lacuna", "checkpoint", "run", "dispatch", str(run_path), "--format", "markdown"]
            ),
            "player_visibility": hidden,
        }
    if status == "verifier-refused":
        return {
            "owner": "parent-coordinator",
            "provider": None,
            "agent_name": None,
            "action": "Do not commit. Inspect the retained verifier findings and begin a fresh source-bound checkpoint after correcting the process or proposal.",
            "input_path": str(run_path / ARTIFACT_FILES["verifier_return"]),
            "expected_schema": None,
            "command": None,
            "player_visibility": hidden,
        }
    if status == "ready-to-commit":
        return {
            "owner": "parent-coordinator",
            "provider": None,
            "agent_name": None,
            "action": "Commit or exactly recover the already-reviewed checkpoint. Readiness is not a head reservation.",
            "input_path": str(run_path / ARTIFACT_FILES["review"]),
            "expected_schema": CHECKPOINT_COMMIT_SCHEMA,
            "command": shell_command(["./lacuna", "checkpoint", "run", "commit", str(run_path)]),
            "player_visibility": hidden,
        }
    if status == "committed":
        return {
            "owner": "parent-coordinator",
            "provider": None,
            "agent_name": None,
            "action": (
                "The exact checkpoint receipt is durable and audited. When the next player message arrives, "
                "pass its exact UTF-8 text on standard input to the one-command fresh continuation. Lacuna "
                "will open an audience-only solo turn at this checkpoint head and emit one capsule-bound "
                "fresh-narrator handoff. For the strongest local prose-coverage claim, first run "
                "`lacuna history complete CHECKPOINT_RUN --run-root TURN_RUNS` and add `--public-history PATH`; "
                "use `lacuna history build` only for an explicitly partial ordered run list. "
                "Use narrator-capsule separately only when the reusable capsule itself is needed."
            ),
            "input_path": str(run_path / ARTIFACT_FILES["receipt"]),
            "expected_schema": CHECKPOINT_CONTINUATION_DISPATCH_SCHEMA,
            "command": shell_command(
                [
                    "./lacuna",
                    "checkpoint",
                    "run",
                    "next-turn",
                    str(run_path),
                    "--player-input-file",
                    "-",
                    "--provider",
                    "portable",
                    "--format",
                    "markdown",
                ]
            ),
            "player_visibility": "Only the accepted receipt's top-level narration is eligible for player presentation.",
        }
    _fail("bad-checkpoint-run", f"unsupported checkpoint run status {status!r}")


def _render_next(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    lines = [
        "# Lacuna checkpoint run — exact next action",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Checkpoint: `{manifest['checkpoint_identity']['checkpoint_id']}`",
        f"- Status: **{manifest['status']}**",
        f"- Owner: **{action['owner']}**",
    ]
    if action["provider"] is not None:
        lines.extend(
            [
                f"- Provider route: **{action['provider']}**",
                f"- Agent/context name: `{action['agent_name']}`",
            ]
        )
    lines.extend(["", action["action"]])
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["expected_schema"] is not None:
        lines.append(f"Expected artifact: `{action['expected_schema']}`")
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.extend(
        [
            "",
            f"Player visibility: {action['player_visibility']}",
            "",
            "`run.json` is authoritative. This file is a deterministic pointer only.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(run_path: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
    atomic_write_text(run_path / NEXT_FILE, _render_next(manifest))


def begin_checkpoint_run(
    cube: Cube,
    *,
    reference: str,
    resolved_cube_path: str,
    root: str | Path,
    audience_id: str,
    actor_id: str,
    trigger: str,
    candidate_count: int = 4,
    rollout_horizon_turns: int = 4,
    compression_max_chars: int = 6000,
    max_operations: int = 32,
    provider_routes: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        reference = require_string(reference, "reference", max_len=4096)
        resolved_cube_path = require_string(resolved_cube_path, "resolved_cube_path", max_len=4096)
        trigger = require_string(trigger, "trigger", max_len=50000)
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-run-input", str(exc)) from exc
    routes = _validate_provider_routes(
        provider_routes if provider_routes is not None else normalize_checkpoint_provider_routes()
    )
    try:
        bound_cube_path = cube.root.resolve(strict=True)
        supplied_cube_path = Path(resolved_cube_path).expanduser().resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            "bad-checkpoint-run-input",
            f"cannot resolve the checkpoint cube path: {exc}",
        ) from exc
    if supplied_cube_path != bound_cube_path:
        _fail(
            "checkpoint-run-cube-path-mismatch",
            "resolved_cube_path must name the exact Cube object used to freeze the checkpoint",
            {
                "expected": str(bound_cube_path),
                "actual": str(supplied_cube_path),
            },
        )
    resolved_cube_path = str(bound_cube_path)
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        _fail(
            "cube-verification-failed",
            "refusing to open a checkpoint run from a cube that fails deterministic verification",
            verification,
        )
    # Manufacture every source-bound object before creating the sidecar
    # directory. Ordinary validation failures should not leave a run-shaped
    # orphan; only an actual interruption during publication can do that.
    request = build_checkpoint_request(
        cube,
        audience_id=audience_id,
        actor_id=actor_id,
        trigger=trigger,
        candidate_count=candidate_count,
        rollout_horizon_turns=rollout_horizon_turns,
        compression_max_chars=compression_max_chars,
        max_operations=max_operations,
    )
    generator_card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
    root_path = Path(root).expanduser().resolve()
    try:
        root_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise LacunaError(
            "checkpoint-run-create-failed",
            f"cannot create checkpoint run root {root_path}: {exc}",
        ) from exc
    if not root_path.is_dir():
        _fail("checkpoint-run-create-failed", f"checkpoint run root is not a directory: {root_path}")
    run_id = new_id("ckr")
    run_path = root_path / run_id
    created_at = utc_now()
    with publish_private_directory(
        run_path,
        error_code="checkpoint-run-create-failed",
        kind_label="checkpoint run",
    ) as staging_path:
        ensure_sidecar_lock(
            staging_path,
            lock_file=RUN_LOCK_FILE,
            error_prefix="checkpoint-run",
            kind_label="checkpoint run",
        )
        artifacts: dict[str, Any] = {key: None for key in ARTIFACT_KEYS}
        artifacts["trigger"] = _write_trigger(staging_path, trigger)
        artifacts["request"] = _write_json_artifact(staging_path, "request", request)
        artifacts["generator_card"] = _write_json_artifact(
            staging_path, "generator_card", generator_card
        )
        manifest: dict[str, Any] = {
            "event": CHECKPOINT_RUN_EVENT,
            "schema": CHECKPOINT_RUN_SCHEMA,
            "project_version": __version__,
            "run_id": run_id,
            "run_path": str(run_path),
            "created_at": created_at,
            "updated_at": created_at,
            "reference": reference,
            "resolved_cube_path": resolved_cube_path,
            "cube_id": request["cube_id"],
            "status": "awaiting-generator",
            "provider_routes": routes,
            "checkpoint_identity": {
                "checkpoint_id": request["checkpoint_id"],
                "expected_head": request["expected_head"],
                "trigger_sha256": request["trigger_sha256"],
                "request_sha256": _digest(request, label="checkpoint request"),
                "turn_packet_sha256": request["turn_packet_sha256"],
            },
            "artifacts": artifacts,
            "invocations": [],
            "next_action": {},
            "nonclaims": list(CHECKPOINT_RUN_NONCLAIMS),
        }
        manifest["next_action"] = _next_action(
            run_path, manifest["status"], artifacts, routes
        )
        _write_manifest(staging_path, manifest)
    return audit_checkpoint_run(run_path)


def _validate_artifact_ref(run_path: Path, key: str, value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    document = _strict(
        value,
        label=f"artifacts.{key}",
        fields=ARTIFACT_FIELDS,
        code="bad-checkpoint-run",
    )
    filename = ARTIFACT_FILES[key]
    if document.get("path") != filename:
        _fail(
            "checkpoint-run-path-mismatch",
            f"artifacts.{key}.path must be {filename!r}",
            {"actual": document.get("path")},
        )
    digest = document.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        _fail("bad-checkpoint-run", f"artifacts.{key}.sha256 must be a lowercase SHA-256 digest")
    expected_metadata = ARTIFACT_METADATA[key]
    actual_metadata = (
        document.get("media_type"),
        document.get("schema"),
        document.get("role"),
    )
    if actual_metadata != expected_metadata:
        _fail(
            "checkpoint-run-artifact-metadata-mismatch",
            f"artifact {key!r} metadata does not match its fixed contract",
            {"expected": expected_metadata, "actual": actual_metadata},
        )
    path = run_path / filename
    if key == "trigger":
        actual = sha256_text(
            read_sidecar_text(path, label="checkpoint trigger", error_prefix="checkpoint-run")
        )
    else:
        actual = _digest(
            read_sidecar_json_object(
                path,
                label=key.replace("_", " "),
                error_prefix="checkpoint-run",
                root_error_code="bad-checkpoint-run-artifact",
            )
        )
    if actual != digest:
        _fail(
            "checkpoint-run-artifact-digest-mismatch",
            f"artifact {key!r} no longer matches run.json",
            {"expected": digest, "actual": actual, "path": str(path)},
        )
    return document


def _expected_artifact_keys(status: str) -> set[str]:
    base = {"trigger", "request", "generator_card"}
    if status == "awaiting-generator":
        return base
    base |= {"candidates", "judge_card"}
    if status == "awaiting-judge":
        return base
    base |= {"judgment", "compressor_card"}
    if status == "awaiting-compressor":
        return base
    base |= {"compression", "proposal", "verifier_card"}
    if status == "awaiting-verifier":
        return base
    base.add("verifier_return")
    if status == "verifier-refused":
        return base
    base.add("review")
    if status == "ready-to-commit":
        return base
    if status == "committed":
        base.add("receipt")
        return base
    _fail("bad-checkpoint-run", f"unsupported checkpoint run status {status!r}")


def _invocation_filename(sequence: int, role: str) -> str:
    return f"invocation-{sequence:04d}-{ROLE_SLUG[role]}.json"


def _invocation_output(ref: dict[str, Any]) -> dict[str, Any]:
    return {"path": ref["path"], "sha256": ref["sha256"], "schema": ref["schema"]}


def _validate_invocation_receipt(
    value: Any,
    *,
    manifest: dict[str, Any],
    card: dict[str, Any],
    output_ref: dict[str, Any] | None,
    expected_sequence: int,
    expected_attempt: int,
) -> dict[str, Any]:
    code = "bad-checkpoint-invocation-receipt"
    receipt = _strict(value, label="checkpoint invocation receipt", fields=INVOCATION_FIELDS, code=code)
    role = card["role"]
    provider = manifest["provider_routes"][role]
    expected_dispatch = _checkpoint_run_dispatch_document(manifest, card)
    expected = {
        "event": "lacuna.checkpoint.invocation-recorded",
        "schema": CHECKPOINT_INVOCATION_RECEIPT_SCHEMA,
        "run_id": manifest["run_id"],
        "checkpoint_id": manifest["checkpoint_identity"]["checkpoint_id"],
        "sequence": expected_sequence,
        "attempt": expected_attempt,
        "role": role,
        "provider": provider,
        "agent_name": provider_alias(role, provider),
        "card_sha256": checkpoint_task_card_sha256(card),
        "dispatch_sha256": _digest(expected_dispatch, label="checkpoint run dispatch"),
        "expected_output_schema": card["output_contract"]["schema"],
        "declaration": "host-declared",
        "nonclaims": INVOCATION_NONCLAIMS,
    }
    mismatches = {
        field: {"expected": expected_value, "actual": receipt.get(field)}
        for field, expected_value in expected.items()
        if receipt.get(field) != expected_value
    }
    if mismatches:
        _fail(code, "invocation receipt does not bind the exact run stage", {"mismatches": mismatches})
    try:
        require_string(receipt.get("model"), "model", max_len=512)
        require_string(receipt.get("recorded_at"), "recorded_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    _optional_string(receipt.get("model_version"), "model_version", max_len=512)
    _optional_string(receipt.get("invocation_id"), "invocation_id", max_len=512)
    started = _optional_string(receipt.get("started_at"), "started_at", max_len=128)
    completed = _optional_string(receipt.get("completed_at"), "completed_at", max_len=128)
    if (started is None) != (completed is None):
        _fail(code, "started_at and completed_at must both be present or both be null")
    duration = receipt.get("duration_ms")
    if duration is not None and (isinstance(duration, bool) or not isinstance(duration, int) or duration < 0):
        _fail(code, "duration_ms must be a nonnegative integer or null")
    outcome = receipt.get("outcome")
    if outcome not in {"accepted", "failed"}:
        _fail(code, "outcome must be accepted or failed")
    failure_class = receipt.get("failure_class")
    failure_message = _optional_string(receipt.get("failure_message"), "failure_message", max_len=10000)
    raw_output = receipt.get("output_artifact")
    if outcome == "accepted":
        if output_ref is None:
            _fail(code, "accepted invocation requires its retained output artifact")
        output = _strict(raw_output, label="output_artifact", fields=INVOCATION_OUTPUT_FIELDS, code=code)
        expected_output = _invocation_output(output_ref)
        if output != expected_output:
            _fail(
                code,
                "accepted invocation output does not match the retained role artifact",
                {"expected": expected_output, "actual": output},
            )
        if failure_class is not None or failure_message is not None:
            _fail(code, "accepted invocation cannot contain failure metadata")
    else:
        if raw_output is not None:
            _fail(code, "failed invocation cannot claim an accepted output artifact")
        if failure_class not in INVOCATION_FAILURE_CLASSES:
            _fail(code, f"failure_class must be one of {sorted(INVOCATION_FAILURE_CLASSES)}")
    result = copy.deepcopy(receipt)
    _digest(result, label="checkpoint invocation receipt")
    return result


def _write_invocation_receipt(run_path: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    filename = _invocation_filename(receipt["sequence"], receipt["role"])
    atomic_write_json(run_path / filename, receipt)
    return _artifact_ref(
        filename=filename,
        sha256=_digest(receipt, label="checkpoint invocation receipt"),
        media_type="application/json",
        schema=CHECKPOINT_INVOCATION_RECEIPT_SCHEMA,
        role=receipt["role"],
    )


def _read_invocation_ref(
    run_path: Path,
    value: Any,
    *,
    index: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    ref = _strict(
        value,
        label=f"invocations[{index}]",
        fields=ARTIFACT_FIELDS,
        code="bad-checkpoint-run",
    )
    match = INVOCATION_FILENAME_RE.fullmatch(str(ref.get("path")))
    if match is None:
        _fail("checkpoint-run-path-mismatch", "invocation receipt path is not canonical", {"path": ref.get("path")})
    if (
        ref.get("media_type") != "application/json"
        or ref.get("schema") != CHECKPOINT_INVOCATION_RECEIPT_SCHEMA
        or ref.get("role") not in CHECKPOINT_ROLES
    ):
        _fail("checkpoint-run-artifact-metadata-mismatch", "invocation receipt metadata is invalid")
    if match.group("role") != ROLE_SLUG[ref["role"]] or int(match.group("sequence")) != index + 1:
        _fail("checkpoint-run-path-mismatch", "invocation receipt path does not match its sequence and role")
    digest = ref.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        _fail("bad-checkpoint-run", "invocation receipt sha256 is invalid")
    document = read_sidecar_json_object(
        run_path / ref["path"],
        label=f"invocation receipt {index + 1}",
        error_prefix="checkpoint-run",
        root_error_code="bad-checkpoint-run-artifact",
    )
    actual = _digest(document, label="checkpoint invocation receipt")
    if actual != digest:
        _fail(
            "checkpoint-run-artifact-digest-mismatch",
            "invocation receipt no longer matches run.json",
            {"expected": digest, "actual": actual, "path": str(run_path / ref["path"])},
        )
    return ref, document


def _audit_invocations(
    run_path: Path,
    manifest: dict[str, Any],
    refs: dict[str, dict[str, Any] | None],
    cards: dict[str, dict[str, Any]],
) -> None:
    try:
        raw = require_list(manifest.get("invocations"), "invocations")
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-run", str(exc)) from exc
    if len(raw) > MAX_INVOCATIONS:
        _fail("bad-checkpoint-run", f"invocations exceeds {MAX_INVOCATIONS} entries")
    attempts = {role: 0 for role in CHECKPOINT_ROLES}
    accepted = {role: 0 for role in CHECKPOINT_ROLES}
    last_role_index = -1
    accepted_seen: set[str] = set()
    for index, raw_ref in enumerate(raw):
        ref, document = _read_invocation_ref(run_path, raw_ref, index=index)
        role = ref["role"]
        role_index = ROLE_ORDER[role]
        if role_index < last_role_index:
            _fail("checkpoint-run-invocation-order-mismatch", "invocation roles are not in checkpoint stage order")
        last_role_index = role_index
        if role in accepted_seen:
            _fail("checkpoint-run-invocation-order-mismatch", "no invocation may follow an accepted output for the same role")
        attempts[role] += 1
        card = cards.get(role)
        if card is None:
            _fail("checkpoint-run-invocation-order-mismatch", "invocation receipt exists before its exact role card")
        output_ref = refs[ROLE_OUTPUT_KEY[role]]
        validated = _validate_invocation_receipt(
            document,
            manifest=manifest,
            card=card,
            output_ref=output_ref,
            expected_sequence=index + 1,
            expected_attempt=attempts[role],
        )
        if validated["outcome"] == "accepted":
            accepted[role] += 1
            accepted_seen.add(role)
    for role in CHECKPOINT_ROLES:
        output_present = refs[ROLE_OUTPUT_KEY[role]] is not None
        if output_present and accepted[role] != 1:
            _fail(
                "checkpoint-run-invocation-custody-mismatch",
                "every retained role output requires exactly one accepted invocation receipt",
                {"role": role, "accepted_receipts": accepted[role]},
            )
        if not output_present and accepted[role] != 0:
            _fail(
                "checkpoint-run-invocation-custody-mismatch",
                "an accepted invocation receipt cannot exist without its retained role output",
                {"role": role},
            )


def _audit_next_pointer(run_path: Path, manifest: dict[str, Any]) -> None:
    actual = read_sidecar_text(
        run_path / NEXT_FILE,
        label="checkpoint run next pointer",
        error_prefix="checkpoint-run",
    )
    expected = _render_next(manifest)
    if actual != expected:
        _fail(
            "checkpoint-run-next-pointer-mismatch",
            "NEXT.md does not match the deterministic action in run.json",
            {"expected_sha256": sha256_text(expected), "actual_sha256": sha256_text(actual)},
        )


def _audit_checkpoint_run_unlocked(run_path: Path, *, audit_next: bool = True) -> dict[str, Any]:
    manifest = _strict(
        read_sidecar_json_object(
            run_path / RUN_MANIFEST_FILE,
            label="checkpoint run manifest",
            error_prefix="checkpoint-run",
            root_error_code="bad-checkpoint-run",
        ),
        label="checkpoint run manifest",
        fields=MANIFEST_FIELDS,
        code="bad-checkpoint-run",
    )
    if manifest.get("event") != CHECKPOINT_RUN_EVENT or manifest.get("schema") != CHECKPOINT_RUN_SCHEMA:
        _fail("bad-checkpoint-run", "checkpoint run event or schema is invalid")
    if manifest.get("project_version") != __version__:
        _fail(
            "checkpoint-run-version-mismatch",
            "checkpoint run was created by a different Lacuna version",
            {"expected": __version__, "actual": manifest.get("project_version")},
        )
    try:
        require_id(manifest.get("run_id"), "run_id")
        require_id(manifest.get("cube_id"), "cube_id")
        require_string(manifest.get("created_at"), "created_at", max_len=128)
        require_string(manifest.get("updated_at"), "updated_at", max_len=128)
        require_string(manifest.get("reference"), "reference", max_len=4096)
        require_string(manifest.get("resolved_cube_path"), "resolved_cube_path", max_len=4096)
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-run", str(exc)) from exc
    if manifest.get("run_path") != str(run_path):
        _fail(
            "checkpoint-run-path-mismatch",
            "run_path does not name the directory containing run.json",
            {"expected": str(run_path), "actual": manifest.get("run_path")},
        )
    status = manifest.get("status")
    if status not in CHECKPOINT_RUN_STATUSES:
        _fail("bad-checkpoint-run", f"status must be one of {list(CHECKPOINT_RUN_STATUSES)}")
    if manifest.get("nonclaims") != CHECKPOINT_RUN_NONCLAIMS:
        _fail("bad-checkpoint-run", "checkpoint run nonclaims differ from the fixed trust boundary")
    routes = _validate_provider_routes(manifest.get("provider_routes"))
    identity = _strict(
        manifest.get("checkpoint_identity"),
        label="checkpoint_identity",
        fields=CHECKPOINT_IDENTITY_FIELDS,
        code="bad-checkpoint-run",
    )
    try:
        require_id(identity.get("checkpoint_id"), "checkpoint_identity.checkpoint_id")
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-run", str(exc)) from exc
    for field in ("expected_head", "trigger_sha256", "request_sha256", "turn_packet_sha256"):
        if not isinstance(identity.get(field), str) or not SHA256_RE.fullmatch(identity[field]):
            _fail("bad-checkpoint-run", f"checkpoint_identity.{field} must be a lowercase SHA-256 digest")
    artifacts = _strict(
        manifest.get("artifacts"),
        label="artifacts",
        fields=set(ARTIFACT_KEYS),
        code="bad-checkpoint-run",
    )
    refs = {key: _validate_artifact_ref(run_path, key, artifacts[key]) for key in ARTIFACT_KEYS}
    actual_present = {key for key, ref in refs.items() if ref is not None}
    expected_present = _expected_artifact_keys(status)
    if actual_present != expected_present:
        _fail(
            "checkpoint-run-artifact-topology-mismatch",
            "referenced artifacts do not match the exact checkpoint state",
            {"missing": sorted(expected_present - actual_present), "unexpected": sorted(actual_present - expected_present)},
        )

    trigger = read_sidecar_text(
        run_path / ARTIFACT_FILES["trigger"],
        label="checkpoint trigger",
        error_prefix="checkpoint-run",
    )
    request = validate_checkpoint_request(_read_json(run_path, "request"))
    request_sha = _digest(request, label="checkpoint request")
    expected_identity = {
        "checkpoint_id": request["checkpoint_id"],
        "expected_head": request["expected_head"],
        "trigger_sha256": request["trigger_sha256"],
        "request_sha256": request_sha,
        "turn_packet_sha256": request["turn_packet_sha256"],
    }
    if identity != expected_identity:
        _fail(
            "checkpoint-run-identity-mismatch",
            "checkpoint_identity does not bind the retained request",
            {"expected": expected_identity, "actual": identity},
        )
    if sha256_text(trigger) != request["trigger_sha256"] or trigger != request["turn_packet"]["player_input"]:
        _fail("checkpoint-run-trigger-mismatch", "retained trigger differs from the source-bound request")
    if request["cube_id"] != manifest["cube_id"]:
        _fail("checkpoint-run-cube-mismatch", "checkpoint request belongs to another cube")

    cards: dict[str, dict[str, Any]] = {}
    expected_generator = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
    actual_generator = validate_checkpoint_task_card(_read_json(run_path, "generator_card"))
    if actual_generator != expected_generator:
        _fail("checkpoint-run-artifact-mismatch", "generator card is not the exact card for this request")
    cards["lacuna-retcon-generator"] = actual_generator

    candidates: dict[str, Any] | None = None
    judgment: dict[str, Any] | None = None
    compression: dict[str, Any] | None = None
    proposal: dict[str, Any] | None = None
    verifier: dict[str, Any] | None = None
    review: dict[str, Any] | None = None

    if refs["candidates"] is not None:
        candidates = validate_checkpoint_candidates(_read_json(run_path, "candidates"), request)
        expected_judge = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-judge",
            candidates_value=candidates,
        )
        actual_judge = validate_checkpoint_task_card(_read_json(run_path, "judge_card"))
        if actual_judge != expected_judge:
            _fail("checkpoint-run-artifact-mismatch", "judge card is not bound to the accepted candidates")
        cards["lacuna-retcon-judge"] = actual_judge
    if refs["judgment"] is not None:
        if candidates is None:
            _fail("bad-checkpoint-run", "judgment requires candidates")
        judgment = validate_checkpoint_judgment(_read_json(run_path, "judgment"), request, candidates)
        expected_compressor = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-compressor",
            candidates_value=candidates,
            judgment_value=judgment,
        )
        actual_compressor = validate_checkpoint_task_card(_read_json(run_path, "compressor_card"))
        if actual_compressor != expected_compressor:
            _fail("checkpoint-run-artifact-mismatch", "compressor card is not bound to the accepted judgment")
        cards["lacuna-retcon-compressor"] = actual_compressor
    if refs["compression"] is not None:
        if candidates is None or judgment is None:
            _fail("bad-checkpoint-run", "compression requires candidates and judgment")
        compression = validate_checkpoint_compression(
            _read_json(run_path, "compression"),
            request,
            candidates,
            judgment,
        )
        expected_proposal = assemble_checkpoint_proposal(request, candidates, judgment, compression)
        proposal = _read_json(run_path, "proposal")
        if proposal != expected_proposal:
            _fail("checkpoint-run-artifact-mismatch", "proposal is not the exact parent assembly for retained artifacts")
        expected_verifier = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-verifier",
            proposal_value=proposal,
        )
        actual_verifier_card = validate_checkpoint_task_card(_read_json(run_path, "verifier_card"))
        if actual_verifier_card != expected_verifier:
            _fail("checkpoint-run-artifact-mismatch", "verifier card is not bound to the exact assembled proposal")
        cards["lacuna-retcon-verifier"] = actual_verifier_card
    if refs["verifier_return"] is not None:
        if proposal is None:
            _fail("bad-checkpoint-run", "verifier return requires an assembled proposal")
        verifier = validate_checkpoint_verifier(
            _read_json(run_path, "verifier_return"),
            request,
            proposal,
        )
        if status == "verifier-refused" and verifier["status"] != "refuse":
            _fail("checkpoint-run-state-mismatch", "verifier-refused status requires a refusal")
        if status in {"ready-to-commit", "committed"} and verifier["status"] != "pass":
            _fail("checkpoint-run-state-mismatch", "ready or committed checkpoint requires a passing verifier")
    with Cube.open(manifest["resolved_cube_path"]) as cube:
        if cube.meta("cube_id") != manifest["cube_id"]:
            _fail("checkpoint-run-cube-mismatch", "resolved cube path no longer names this checkpoint's cube")
        if refs["review"] is not None:
            if candidates is None or judgment is None or proposal is None or verifier is None:
                _fail("bad-checkpoint-run", "checkpoint review requires the complete accepted chain")
            review = validate_checkpoint_review(
                _read_json(run_path, "review"),
                request,
                candidates,
                judgment,
                proposal,
                verifier,
                cube=cube,
            )
        if refs["receipt"] is not None:
            if candidates is None or judgment is None or proposal is None or verifier is None or review is None:
                _fail("bad-checkpoint-run", "checkpoint receipt requires the complete reviewed chain")
            _validate_checkpoint_commit_receipt_document(
                _read_json(run_path, "receipt"),
                request,
                proposal,
                review,
                cube=cube,
            )

    _audit_invocations(run_path, manifest, refs, cards)
    expected_next = _next_action(run_path, status, artifacts, routes)
    next_action = _strict(
        manifest.get("next_action"),
        label="next_action",
        fields=NEXT_ACTION_FIELDS,
        code="bad-checkpoint-run",
    )
    if next_action != expected_next:
        _fail("checkpoint-run-next-action-mismatch", "next_action is not deterministic for this checkpoint state")
    if audit_next:
        _audit_next_pointer(run_path, manifest)
    return copy.deepcopy(manifest)


def audit_checkpoint_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        return _audit_checkpoint_run_unlocked(run_path)


def committed_checkpoint_history_boundary(value: str | Path) -> dict[str, Any]:
    """Return the exact committed checkpoint boundary for history census.

    The checkpoint sidecar supplies run/checkpoint identity while the immutable
    ledger supplies the request event position.  The result contains no private
    candidate, score, state-card, verifier, or filesystem-path material.
    """
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        if manifest["status"] != "committed":
            _fail(
                "checkpoint-history-boundary-not-committed",
                "complete public history requires a committed checkpoint run",
                {"status": manifest["status"]},
            )
        request = validate_checkpoint_request(_read_json(run_path, "request"))
        with Cube.open(manifest["resolved_cube_path"]) as cube:
            if cube.meta("cube_id") != manifest["cube_id"]:
                _fail(
                    "checkpoint-history-boundary-cube-mismatch",
                    "the checkpoint run no longer resolves to its retained cube",
                )
            request_event_seq = cube.event_sequence(request["expected_head"])
        packet = request["turn_packet"]
        return {
            "checkpoint_run_id": manifest["run_id"],
            "checkpoint_id": request["checkpoint_id"],
            "request_source_id": packet["request_source_id"],
            "request_head": request["expected_head"],
            "request_event_seq": request_event_seq,
            "cube_id": manifest["cube_id"],
            "audience_id": packet["audience_id"],
        }


def _build_checkpoint_run_narrator_capsule_unlocked(
    run_path: Path,
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = manifest or _audit_checkpoint_run_unlocked(run_path)
    if manifest["status"] != "committed":
        _fail(
            "checkpoint-run-not-committed",
            "a fresh-narrator capsule is available only after the exact checkpoint is committed",
            {"status": manifest["status"]},
        )
    request_ref = manifest["artifacts"]["request"]
    proposal_ref = manifest["artifacts"]["proposal"]
    receipt_ref = manifest["artifacts"]["receipt"]
    assert isinstance(request_ref, dict)
    assert isinstance(proposal_ref, dict)
    assert isinstance(receipt_ref, dict)
    return build_checkpoint_narrator_capsule(
        run_id=manifest["run_id"],
        request=_read_json(run_path, "request"),
        proposal=_read_json(run_path, "proposal"),
        receipt=_read_json(run_path, "receipt"),
        request_sha256=request_ref["sha256"],
        proposal_sha256=proposal_ref["sha256"],
        receipt_sha256=receipt_ref["sha256"],
    )


def build_checkpoint_run_narrator_capsule(value: str | Path) -> dict[str, Any]:
    """Compile the committed checkpoint's exact least-context continuation capsule."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        return _build_checkpoint_run_narrator_capsule_unlocked(run_path, manifest)


def recover_checkpoint_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path, audit_next=False)
        atomic_write_text(run_path / NEXT_FILE, _render_next(manifest))
        return _audit_checkpoint_run_unlocked(run_path)


def _invocation_receipt(
    manifest: dict[str, Any],
    card: dict[str, Any],
    *,
    outcome: str,
    output_ref: dict[str, Any] | None,
    model: str,
    model_version: str | None,
    invocation_id: str | None,
    started_at: str | None,
    completed_at: str | None,
    duration_ms: int | None,
    failure_class: str | None,
    failure_message: str | None,
) -> dict[str, Any]:
    role = card["role"]
    if len(manifest["invocations"]) >= MAX_INVOCATIONS:
        _fail(
            "checkpoint-run-invocation-limit",
            f"checkpoint run already retains the maximum {MAX_INVOCATIONS} invocation receipts",
            {"role": role, "invocation_count": len(manifest["invocations"])},
        )
    sequence = len(manifest["invocations"]) + 1
    attempt = 1
    for ref in manifest["invocations"]:
        if ref["role"] == role:
            attempt += 1
    provider = manifest["provider_routes"][role]
    dispatch = _checkpoint_run_dispatch_document(manifest, card)
    receipt = {
        "event": "lacuna.checkpoint.invocation-recorded",
        "schema": CHECKPOINT_INVOCATION_RECEIPT_SCHEMA,
        "run_id": manifest["run_id"],
        "checkpoint_id": manifest["checkpoint_identity"]["checkpoint_id"],
        "sequence": sequence,
        "attempt": attempt,
        "role": role,
        "provider": provider,
        "agent_name": provider_alias(role, provider),
        "card_sha256": checkpoint_task_card_sha256(card),
        "dispatch_sha256": _digest(dispatch, label="checkpoint run dispatch"),
        "expected_output_schema": card["output_contract"]["schema"],
        "model": model,
        "model_version": model_version,
        "invocation_id": invocation_id,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "outcome": outcome,
        "output_artifact": _invocation_output(output_ref) if output_ref is not None else None,
        "failure_class": failure_class,
        "failure_message": failure_message,
        "recorded_at": utc_now(),
        "declaration": "host-declared",
        "nonclaims": list(INVOCATION_NONCLAIMS),
    }
    return _validate_invocation_receipt(
        receipt,
        manifest=manifest,
        card=card,
        output_ref=output_ref,
        expected_sequence=sequence,
        expected_attempt=attempt,
    )


def _validate_invocation_metadata(
    *,
    model: str,
    model_version: str | None,
    invocation_id: str | None,
    started_at: str | None,
    completed_at: str | None,
    duration_ms: int | None,
) -> tuple[str, str | None, str | None, str | None, str | None, int | None]:
    try:
        model = require_string(model, "model", max_len=512)
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-invocation-receipt", str(exc)) from exc
    model_version = _optional_string(model_version, "model_version", max_len=512)
    invocation_id = _optional_string(invocation_id, "invocation_id", max_len=512)
    started_at = _optional_string(started_at, "started_at", max_len=128)
    completed_at = _optional_string(completed_at, "completed_at", max_len=128)
    if (started_at is None) != (completed_at is None):
        _fail("bad-checkpoint-invocation-receipt", "started_at and completed_at must both be present or both be null")
    if duration_ms is not None and (isinstance(duration_ms, bool) or not isinstance(duration_ms, int) or duration_ms < 0):
        _fail("bad-checkpoint-invocation-receipt", "duration_ms must be a nonnegative integer or null")
    return model, model_version, invocation_id, started_at, completed_at, duration_ms


def accept_checkpoint_run_artifact(
    value: str | Path,
    artifact: dict[str, Any],
    *,
    model: str = "unknown",
    model_version: str | None = None,
    invocation_id: str | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    metadata = _validate_invocation_metadata(
        model=model,
        model_version=model_version,
        invocation_id=invocation_id,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
    )
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        stage = _current_stage(manifest["status"])
        if stage is None:
            _fail(
                "checkpoint-run-not-awaiting-worker",
                "the checkpoint run is not awaiting a worker return",
                {"status": manifest["status"]},
            )
        role, card_key, output_key, _output_schema = stage
        request = validate_checkpoint_request(_read_json(run_path, "request"))
        card = validate_checkpoint_task_card(_read_json(run_path, card_key))
        if card["role"] != role:
            _fail("checkpoint-run-state-mismatch", "current card role differs from run status")
        candidates = _read_json(run_path, "candidates") if manifest["artifacts"]["candidates"] else None
        judgment = _read_json(run_path, "judgment") if manifest["artifacts"]["judgment"] else None
        proposal = _read_json(run_path, "proposal") if manifest["artifacts"]["proposal"] else None
        if role == "lacuna-retcon-generator":
            accepted = validate_checkpoint_candidates(artifact, request)
        elif role == "lacuna-retcon-judge":
            if candidates is None:
                _fail("bad-checkpoint-run", "judge return requires candidates")
            accepted = validate_checkpoint_judgment(artifact, request, candidates)
        elif role == "lacuna-retcon-compressor":
            if candidates is None or judgment is None:
                _fail("bad-checkpoint-run", "compressor return requires candidates and judgment")
            accepted = validate_checkpoint_compression(artifact, request, candidates, judgment)
        else:
            if proposal is None:
                _fail("bad-checkpoint-run", "verifier return requires proposal")
            accepted = validate_checkpoint_verifier(artifact, request, proposal)
        output_ref = _write_json_artifact(run_path, output_key, accepted)
        manifest["artifacts"][output_key] = output_ref
        receipt = _invocation_receipt(
            manifest,
            card,
            outcome="accepted",
            output_ref=output_ref,
            model=metadata[0],
            model_version=metadata[1],
            invocation_id=metadata[2],
            started_at=metadata[3],
            completed_at=metadata[4],
            duration_ms=metadata[5],
            failure_class=None,
            failure_message=None,
        )
        manifest["invocations"].append(_write_invocation_receipt(run_path, receipt))

        if role == "lacuna-retcon-generator":
            next_card = build_checkpoint_task_card(
                request,
                role="lacuna-retcon-judge",
                candidates_value=accepted,
            )
            manifest["artifacts"]["judge_card"] = _write_json_artifact(run_path, "judge_card", next_card)
            status = "awaiting-judge"
        elif role == "lacuna-retcon-judge":
            assert candidates is not None
            next_card = build_checkpoint_task_card(
                request,
                role="lacuna-retcon-compressor",
                candidates_value=candidates,
                judgment_value=accepted,
            )
            manifest["artifacts"]["compressor_card"] = _write_json_artifact(run_path, "compressor_card", next_card)
            status = "awaiting-compressor"
        elif role == "lacuna-retcon-compressor":
            assert candidates is not None and judgment is not None
            assembled = assemble_checkpoint_proposal(request, candidates, judgment, accepted)
            manifest["artifacts"]["proposal"] = _write_json_artifact(run_path, "proposal", assembled)
            verifier_card = build_checkpoint_task_card(
                request,
                role="lacuna-retcon-verifier",
                proposal_value=assembled,
            )
            manifest["artifacts"]["verifier_card"] = _write_json_artifact(run_path, "verifier_card", verifier_card)
            status = "awaiting-verifier"
        else:
            assert candidates is not None and judgment is not None and proposal is not None
            if accepted["status"] == "refuse":
                status = "verifier-refused"
            else:
                with Cube.open(manifest["resolved_cube_path"]) as cube:
                    reviewed = review_checkpoint(
                        cube,
                        request,
                        candidates,
                        judgment,
                        proposal,
                        accepted,
                    )
                manifest["artifacts"]["review"] = _write_json_artifact(run_path, "review", reviewed)
                status = "ready-to-commit"
        manifest["status"] = status
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(
            run_path,
            status,
            manifest["artifacts"],
            manifest["provider_routes"],
        )
        _write_manifest(run_path, manifest)
        return _audit_checkpoint_run_unlocked(run_path)


def record_checkpoint_run_failure(
    value: str | Path,
    *,
    failure_class: str,
    failure_message: str | None = None,
    model: str = "unknown",
    model_version: str | None = None,
    invocation_id: str | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    if failure_class not in INVOCATION_FAILURE_CLASSES:
        _fail(
            "bad-checkpoint-invocation-receipt",
            f"failure_class must be one of {sorted(INVOCATION_FAILURE_CLASSES)}",
        )
    metadata = _validate_invocation_metadata(
        model=model,
        model_version=model_version,
        invocation_id=invocation_id,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
    )
    failure_message = _optional_string(failure_message, "failure_message", max_len=10000)
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        stage = _current_stage(manifest["status"])
        if stage is None:
            _fail(
                "checkpoint-run-not-awaiting-worker",
                "only the current delegated stage can receive a failed invocation record",
                {"status": manifest["status"]},
            )
        role, card_key, _output_key, _output_schema = stage
        card = validate_checkpoint_task_card(_read_json(run_path, card_key))
        if card["role"] != role:
            _fail("checkpoint-run-state-mismatch", "current card role differs from run status")
        receipt = _invocation_receipt(
            manifest,
            card,
            outcome="failed",
            output_ref=None,
            model=metadata[0],
            model_version=metadata[1],
            invocation_id=metadata[2],
            started_at=metadata[3],
            completed_at=metadata[4],
            duration_ms=metadata[5],
            failure_class=failure_class,
            failure_message=failure_message,
        )
        manifest["invocations"].append(_write_invocation_receipt(run_path, receipt))
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(
            run_path,
            manifest["status"],
            manifest["artifacts"],
            manifest["provider_routes"],
        )
        _write_manifest(run_path, manifest)
        return _audit_checkpoint_run_unlocked(run_path)


def commit_checkpoint_run(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        if manifest["status"] == "committed":
            return _read_json(run_path, "receipt")
        if manifest["status"] != "ready-to-commit":
            _fail(
                "checkpoint-run-not-ready",
                "checkpoint run is not ready to commit",
                {"status": manifest["status"]},
            )
        request = _read_json(run_path, "request")
        candidates = _read_json(run_path, "candidates")
        judgment = _read_json(run_path, "judgment")
        proposal = _read_json(run_path, "proposal")
        verifier = _read_json(run_path, "verifier_return")
        review = _read_json(run_path, "review")
        with Cube.open(manifest["resolved_cube_path"]) as cube:
            receipt = commit_checkpoint(
                cube,
                request,
                candidates,
                judgment,
                proposal,
                verifier,
                review,
            )
        manifest["artifacts"]["receipt"] = _write_json_artifact(run_path, "receipt", receipt)
        manifest["status"] = "committed"
        manifest["updated_at"] = utc_now()
        manifest["next_action"] = _next_action(
            run_path,
            "committed",
            manifest["artifacts"],
            manifest["provider_routes"],
        )
        _write_manifest(run_path, manifest)
        _audit_checkpoint_run_unlocked(run_path)
        return receipt



def _checkpoint_continuation_event_custody(
    cube: Cube,
    *,
    checkpoint_manifest: dict[str, Any],
    checkpoint_request: dict[str, Any],
    capsule: dict[str, Any],
    public_history: dict[str, Any] | None,
) -> tuple[int, int, dict[str, Any] | None]:
    """Authenticate checkpoint chronology and any explicitly supplied public history."""
    checkpoint_request_event_seq = cube.event_sequence(checkpoint_request["expected_head"])
    checkpoint_post_commit_event_seq = cube.event_sequence(capsule["post_commit_head"])
    if checkpoint_post_commit_event_seq <= checkpoint_request_event_seq:
        _fail(
            "bad-checkpoint-continuation",
            "checkpoint post-commit head does not follow its request head",
        )
    history = authenticate_public_history(cube, public_history) if public_history is not None else None
    if history is None:
        return checkpoint_request_event_seq, checkpoint_post_commit_event_seq, None
    if history["cube_id"] != checkpoint_manifest["cube_id"]:
        _fail(
            "checkpoint-continuation-public-history-cube-mismatch",
            "public history and checkpoint run belong to different cubes",
        )
    if history["audience_id"] != capsule["audience_id"]:
        _fail(
            "checkpoint-continuation-public-history-audience-mismatch",
            "public history and checkpoint capsule name different audiences",
        )
    last_commit_event_seq = history["coverage"]["last_commit_event_seq"]
    if (
        last_commit_event_seq is not None
        and last_commit_event_seq >= checkpoint_request_event_seq
    ):
        _fail(
            "checkpoint-continuation-public-history-order-mismatch",
            "public history must end before the checkpoint request event",
            {
                "public_history_last_commit_event_seq": last_commit_event_seq,
                "checkpoint_request_event_seq": checkpoint_request_event_seq,
            },
        )
    if history["coverage"]["mode"] == "complete-before-checkpoint":
        boundary = history["coverage"]["boundary"]
        expected_boundary = {
            "checkpoint_run_id": checkpoint_manifest["run_id"],
            "checkpoint_id": checkpoint_request["checkpoint_id"],
            "request_source_id": checkpoint_request["turn_packet"]["request_source_id"],
            "request_head": checkpoint_request["expected_head"],
            "request_event_seq": checkpoint_request_event_seq,
        }
        mismatch = {
            field: {"expected": expected, "actual": boundary.get(field)}
            for field, expected in expected_boundary.items()
            if boundary.get(field) != expected
        }
        if mismatch:
            _fail(
                "checkpoint-continuation-public-history-boundary-mismatch",
                "complete public history is bound to a different checkpoint run",
                {"mismatched": mismatch},
            )
    return checkpoint_request_event_seq, checkpoint_post_commit_event_seq, history


def build_checkpoint_continuation_dispatch(
    checkpoint_value: str | Path,
    turn_value: str | Path,
    *,
    provider: str = "portable",
    public_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Join one committed checkpoint to one fresh audience-only solo turn.

    Both sidecars remain authoritative in their own domains. This bridge holds
    their locks in checkpoint-then-turn order, authenticates both chains, and
    emits a deterministic least-context dispatch. It does not persist the
    dispatch, invoke a model, accept a proposal, or mutate the cube.
    """
    if provider not in PROVIDERS:
        _fail("unknown-provider", f"provider must be one of {list(PROVIDERS)}")
    checkpoint_path = _run_directory(checkpoint_value)
    turn_path = _turn_run_directory(turn_value)
    with _run_lock(checkpoint_path):
        with _turn_run_lock(turn_path):
            checkpoint_manifest = _audit_checkpoint_run_unlocked(checkpoint_path)
            turn_manifest = _audit_turn_run_unlocked(turn_path)
            if checkpoint_manifest["status"] != "committed":
                _fail(
                    "checkpoint-continuation-not-committed",
                    "a fresh continuation dispatch requires a committed checkpoint run",
                    {"status": checkpoint_manifest["status"]},
                )
            if turn_manifest["selected_mode"] != "solo":
                _fail(
                    "checkpoint-continuation-turn-not-solo",
                    "the continuation turn must be opened in solo mode so one fresh narrator returns the exact proposal",
                    {"selected_mode": turn_manifest["selected_mode"]},
                )
            if turn_manifest["status"] != "awaiting-solo-proposal":
                _fail(
                    "checkpoint-continuation-turn-not-fresh",
                    "the continuation turn must still be awaiting its first solo proposal",
                    {"status": turn_manifest["status"]},
                )
            if checkpoint_manifest["cube_id"] != turn_manifest["cube_id"]:
                _fail(
                    "checkpoint-continuation-cube-mismatch",
                    "checkpoint and continuation turn must belong to the same cube",
                )
            if checkpoint_manifest["resolved_cube_path"] != turn_manifest["resolved_cube_path"]:
                _fail(
                    "checkpoint-continuation-cube-mismatch",
                    "checkpoint and continuation turn must resolve to the same cube path",
                )

            packet_ref = turn_manifest["artifacts"]["packet"]
            if not isinstance(packet_ref, dict):
                _fail("bad-checkpoint-continuation", "continuation turn is missing its packet")
            packet = validate_turn_packet(
                read_sidecar_json_object(
                    turn_path / TURN_RUN_ARTIFACT_FILES["packet"],
                    label="continuation turn packet",
                    error_prefix="checkpoint-continuation",
                    root_error_code="bad-checkpoint-continuation",
                )
            )
            capsule = _build_checkpoint_run_narrator_capsule_unlocked(
                checkpoint_path, checkpoint_manifest
            )
            checkpoint_request = validate_checkpoint_request(
                _read_json(checkpoint_path, "request")
            )
            history = public_history

            with Cube.open(turn_manifest["resolved_cube_path"]) as cube:
                if cube.meta("cube_id") != turn_manifest["cube_id"]:
                    _fail(
                        "checkpoint-continuation-cube-mismatch",
                        "the resolved cube no longer matches the continuation turn",
                    )
                source_row = cube.conn.execute(
                    "SELECT metadata_json FROM sources WHERE source_id = ? AND retired_seq IS NULL",
                    (packet["request_source_id"],),
                ).fetchone()
                if source_row is None:
                    _fail(
                        "checkpoint-continuation-turn-request-missing",
                        "the continuation turn request source is no longer active",
                    )
                try:
                    request_metadata = require_mapping(
                        json.loads(source_row["metadata_json"]),
                        "continuation turn request metadata",
                    )
                except (TypeError, ValueError, json.JSONDecodeError) as exc:
                    raise LacunaError(
                        "checkpoint-continuation-turn-request-invalid",
                        "the continuation turn request metadata is not valid JSON",
                    ) from exc
                if request_metadata.get("base_head") != capsule["post_commit_head"]:
                    _fail(
                        "checkpoint-continuation-head-mismatch",
                        "the continuation turn request was not opened directly from the committed checkpoint head",
                        {
                            "checkpoint_head": capsule["post_commit_head"],
                            "turn_request_base_head": request_metadata.get("base_head"),
                        },
                    )
                (
                    checkpoint_request_event_seq,
                    checkpoint_post_commit_event_seq,
                    history,
                ) = _checkpoint_continuation_event_custody(
                    cube,
                    checkpoint_manifest=checkpoint_manifest,
                    checkpoint_request=checkpoint_request,
                    capsule=capsule,
                    public_history=history,
                )
                if cube.head() != packet["expected_head"]:
                    _fail(
                        "checkpoint-continuation-stale-head",
                        "the cube advanced after the continuation turn was opened; begin a fresh turn at the current head",
                        {"expected_head": packet["expected_head"], "actual_head": cube.head()},
                    )

            return build_continuation_dispatch_document(
                checkpoint_run_id=checkpoint_manifest["run_id"],
                checkpoint_run_path=str(checkpoint_path),
                capsule_value=capsule,
                checkpoint_request_head=checkpoint_request["expected_head"],
                checkpoint_request_event_seq=checkpoint_request_event_seq,
                checkpoint_post_commit_event_seq=checkpoint_post_commit_event_seq,
                turn_run_id=turn_manifest["run_id"],
                turn_run_path=str(turn_path),
                turn_packet_value=packet,
                turn_packet_sha256=packet_ref["sha256"],
                provider=provider,
                public_history_value=history,
            )


def begin_checkpoint_continuation_turn(
    checkpoint_value: str | Path,
    *,
    player_input: str,
    root: str | Path | None = None,
    provider: str = "portable",
    public_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Open the exact fresh solo turn after a committed checkpoint and dispatch it.

    This is the human/weak-coordinator entrance. It derives audience, actor,
    cube, and least-authority settings from the authenticated checkpoint,
    retains the exact next player input in a normal turn run, and then emits
    the same deterministic continuation envelope as the lower-level two-run
    bridge. Model invocation and acceptance remain external and parent-owned.
    """
    if provider not in PROVIDERS:
        _fail("unknown-provider", f"provider must be one of {list(PROVIDERS)}")
    checkpoint_path = _run_directory(checkpoint_value)
    with _run_lock(checkpoint_path):
        checkpoint_manifest = _audit_checkpoint_run_unlocked(checkpoint_path)
        if checkpoint_manifest["status"] != "committed":
            _fail(
                "checkpoint-continuation-not-committed",
                "a fresh continuation turn requires a committed checkpoint run",
                {"status": checkpoint_manifest["status"]},
            )
        capsule = _build_checkpoint_run_narrator_capsule_unlocked(
            checkpoint_path, checkpoint_manifest
        )
        checkpoint_request = validate_checkpoint_request(
            _read_json(checkpoint_path, "request")
        )
        turn_root = (
            Path(root).expanduser().resolve()
            if root is not None
            else (checkpoint_path.parent / "continuation-turns").resolve()
        )
        with Cube.open(checkpoint_manifest["resolved_cube_path"]) as cube:
            if cube.head() != capsule["post_commit_head"]:
                _fail(
                    "checkpoint-continuation-checkpoint-not-current",
                    "the cube advanced after the checkpoint; the one-command continuation must begin directly at its accepted head",
                    {
                        "checkpoint_head": capsule["post_commit_head"],
                        "actual_head": cube.head(),
                    },
                )
            _checkpoint_continuation_event_custody(
                cube,
                checkpoint_manifest=checkpoint_manifest,
                checkpoint_request=checkpoint_request,
                capsule=capsule,
                public_history=public_history,
            )
            turn_manifest = begin_turn_run(
                cube,
                reference=checkpoint_manifest["reference"],
                resolved_cube_path=checkpoint_manifest["resolved_cube_path"],
                root=turn_root,
                player_input=player_input,
                input_kind="play-turn",
                audience_id=capsule["audience_id"],
                actor_id=capsule["actor_id"],
                director=False,
                world_id=None,
                allow_anchor=False,
                mode="solo",
                include_planner_context_on_commit=False,
            )
    return build_checkpoint_continuation_dispatch(
        checkpoint_path,
        turn_manifest["run_path"],
        provider=provider,
        public_history=public_history,
    )


def build_checkpoint_run_dispatch(value: str | Path) -> dict[str, Any]:
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_checkpoint_run_unlocked(run_path)
        stage = _current_stage(manifest["status"])
        if stage is None:
            _fail(
                "checkpoint-run-not-delegated-stage",
                "the current checkpoint run state has no worker dispatch",
                {"status": manifest["status"], "next_action": manifest["next_action"]},
            )
        _role, card_key, _output_key, _output_schema = stage
        card = validate_checkpoint_task_card(_read_json(run_path, card_key))
        return _checkpoint_run_dispatch_document(manifest, card)


def checkpoint_run_dispatch_markdown(dispatch: dict[str, Any]) -> str:
    lines = [
        "# Lacuna managed checkpoint handoff",
        "",
        "**Operational instruction:** perform the named role; do not summarize this handoff.",
        "",
        f"- Run: `{dispatch['run_id']}`",
        f"- Checkpoint: `{dispatch['checkpoint_id']}`",
        f"- Provider route: **{dispatch['provider']}**",
        f"- Role: **{dispatch['role']}**",
        f"- Agent/context name: `{dispatch['agent_name']}`",
        f"- Card SHA-256: `{dispatch['input_card_sha256']}`",
        f"- Required return schema: `{dispatch['return_contract']['schema']}`",
        "",
        "## Worker instructions",
        "",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(dispatch["instructions"], start=1))
    lines.extend(
        [
            "",
            "## Complete task card",
            "",
            "This JSON object is the worker's complete input. A chat context does not need filesystem access or any other cube artifact.",
            "",
            "```json",
            pretty_json(dispatch["input_card"]),
            "```",
            "",
            "## Exact worker return",
            "",
            f"Return one `{dispatch['return_contract']['schema']}` JSON object only—no prose or code fence.",
            "",
            f"The parent saves the exact object to `{dispatch['return_contract']['save_path']}` and runs:",
            "",
            "```bash",
            dispatch["return_contract"]["accept_command"],
            "```",
            "",
            "For a provider, transport, timeout, interruption, invalid-output, or worker-refusal attempt, the parent may record the failed attempt without advancing the role:",
            "",
            "```bash",
            dispatch["invocation_contract"]["failure_command"],
            "```",
            "",
            "The parent may replace `unknown` with an honest model declaration and add optional version, invocation ID, and timing fields. Those values remain host-declared.",
            "",
            "## Boundary reminders",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in dispatch["nonclaims"])
    lines.append("")
    return "\n".join(lines)


def checkpoint_run_markdown(manifest: dict[str, Any]) -> str:
    action = manifest["next_action"]
    lines = [
        "# Lacuna checkpoint run",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Path: `{manifest['run_path']}`",
        f"- Status: **{manifest['status']}**",
        f"- Checkpoint: `{manifest['checkpoint_identity']['checkpoint_id']}`",
        f"- Request SHA-256: `{manifest['checkpoint_identity']['request_sha256']}`",
        f"- Invocation records: **{len(manifest['invocations'])}**",
        "",
        "## Next action",
        "",
        f"Owner: **{action['owner']}**",
    ]
    if action["provider"] is not None:
        lines.extend(
            [
                f"Provider: **{action['provider']}**",
                f"Agent/context: `{action['agent_name']}`",
            ]
        )
    lines.extend(["", action["action"]])
    if action["input_path"] is not None:
        lines.extend(["", f"Input: `{action['input_path']}`"])
    if action["expected_schema"] is not None:
        lines.append(f"Expected artifact: `{action['expected_schema']}`")
    if action["command"] is not None:
        lines.extend(["", "```bash", action["command"], "```"])
    lines.extend(["", action["player_visibility"], ""])
    return "\n".join(lines)


def checkpoint_run_receipt_markdown(receipt: dict[str, Any]) -> str:
    delivery = receipt["turn_receipt"]["delivery"]
    return "\n".join(
        [
            "# Lacuna checkpoint committed",
            "",
            f"- Checkpoint: `{receipt['checkpoint_id']}`",
            f"- Selected candidate: `{receipt['selected_candidate_id']}`",
            f"- Delivery: **{delivery['mode']}**",
            f"- Historical snapshot used: **{str(delivery['historical_snapshot_used']).lower()}**",
            f"- Selection evidence SHA-256: `{receipt['selection_evidence_sha256']}`",
            "",
            "## Player-visible narration",
            "",
            receipt["narration"],
            "",
            "All candidates, scores, state cards, reviews, and invocation records remain backstage.",
            "",
        ]
    )

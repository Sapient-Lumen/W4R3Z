from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, ContextManager

from . import __version__
from .entrance import TURN_NARRATION_PLACEHOLDER
from .errors import LacunaError
from .orchestration import (
    NARRATOR_RETURN_SCHEMA,
    ORCHESTRATION_MODES,
    ORCHESTRATION_PLAN_SCHEMA,
    PLANNER_RETURN_SCHEMA,
    TURN_TASK_CARD_SCHEMA,
    VERIFIER_RETURN_SCHEMA,
    build_orchestration_plan,
    build_turn_task_card,
    turn_packet_input_kind,
    turn_packet_sha256,
    validate_narrator_return,
    validate_planner_return,
    validate_proposal_binding,
    validate_turn_packet,
    validate_verifier_return,
)
from .store import Cube
from .providers import PROVIDER_AGENT_ALIASES, PROVIDERS, provider_alias
from .sidecars import (
    canonical_json_digest,
    ensure_sidecar_lock,
    open_sidecar_lock,
    publish_private_directory,
    read_sidecar_json_object,
    read_sidecar_member_bytes,
    read_sidecar_text,
    resolve_sidecar_directory,
    shell_command,
    sidecar_lock,
)
from .turns import (
    TURN_PREPARATION_SCHEMA,
    TURN_PROPOSAL_SCHEMA,
    TURN_RECEIPT_SCHEMA,
    SUPPORTED_TURN_REQUEST_SCHEMAS,
    build_turn_packet,
    commit_prepared_turn,
    prepare_turn_proposal,
    recover_prepared_turn_receipt,
    validate_turn_preparation,
    validate_turn_receipt,
)
from .util import (
    SHA256_RE,
    atomic_write_json,
    atomic_write_text,
    canonical_json,
    new_id,
    pretty_json,
    require_id,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

TURN_RUN_SCHEMA = "lacuna.turn-run.v2"
TURN_RUN_EVENT = "lacuna.turn.run"
AGENT_DISPATCH_SCHEMA = "lacuna.agent-dispatch.v1"
TURN_RUN_PROVIDERS = PROVIDERS
TURN_RUN_STATUSES = (
    "awaiting-solo-proposal",
    "awaiting-planner",
    "awaiting-narrator",
    "awaiting-pair-proposal",
    "awaiting-proposal-builder",
    "awaiting-verifier",
    "verifier-refused",
    "ready-to-commit",
    "committed",
)

RUN_MANIFEST_FILE = "run.json"
NEXT_FILE = "NEXT.md"
RUN_LOCK_FILE = ".run.lock"
ARTIFACT_FILES = {
    "player_input": "00-player-input.txt",
    "packet": "10-turn-packet.json",
    "plan": "11-orchestration-plan.json",
    "planner_card": "20-planner-card.json",
    "planner_return": "21-planner-return.json",
    "narrator_card": "30-narrator-card.json",
    "narrator_return": "31-narrator-return.json",
    "proposal_builder_card": "40-proposal-builder-card.json",
    "proposal_draft": "41-proposal-draft.json",
    "proposal": "42-turn-proposal.json",
    "preparation": "43-turn-preparation.json",
    "verifier_card": "50-verifier-card.json",
    "verifier_return": "51-verifier-return.json",
    "receipt": "60-turn-receipt.json",
}
ARTIFACT_KEYS = tuple(ARTIFACT_FILES)
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
    "requested_mode",
    "selected_mode",
    "include_planner_context_on_commit",
    "status",
    "turn_identity",
    "artifacts",
    "next_action",
    "nonclaims",
}
ARTIFACT_FIELDS = {"path", "sha256", "media_type", "schema", "role"}
NEXT_ACTION_FIELDS = {
    "owner",
    "action",
    "input_path",
    "expected_schema",
    "command",
    "player_visibility",
}
TURN_IDENTITY_FIELDS = {
    "request_id",
    "request_source_id",
    "proposal_id",
    "expected_head",
    "player_input_sha256",
    "packet_sha256",
}

ARTIFACT_METADATA = {
    "player_input": ("text/plain; charset=utf-8", None, None),
    "packet": ("application/json", None, None),
    "plan": ("application/json", ORCHESTRATION_PLAN_SCHEMA, None),
    "planner_card": ("application/json", TURN_TASK_CARD_SCHEMA, "lacuna-planner"),
    "planner_return": ("application/json", PLANNER_RETURN_SCHEMA, "lacuna-planner"),
    "narrator_card": ("application/json", TURN_TASK_CARD_SCHEMA, "lacuna-narrator"),
    "narrator_return": ("application/json", NARRATOR_RETURN_SCHEMA, "lacuna-narrator"),
    "proposal_builder_card": (
        "application/json",
        TURN_TASK_CARD_SCHEMA,
        "lacuna-proposal-builder",
    ),
    "proposal_draft": ("application/json", TURN_PROPOSAL_SCHEMA, "parent-coordinator"),
    "preparation": ("application/json", TURN_PREPARATION_SCHEMA, "lacuna-kernel"),
    "verifier_card": ("application/json", TURN_TASK_CARD_SCHEMA, "lacuna-verifier"),
    "verifier_return": ("application/json", VERIFIER_RETURN_SCHEMA, "lacuna-verifier"),
    "receipt": ("application/json", TURN_RECEIPT_SCHEMA, "parent-coordinator"),
}


def _fail(code: str, message: str, details: dict[str, Any] | None = None) -> None:
    raise LacunaError(code, message, details)


def _json_digest(value: Any) -> str:
    return canonical_json_digest(
        value,
        error_code="bad-turn-run-artifact",
        label="artifact",
    )


def _read_run_member_bytes(
    path: Path,
    *,
    label: str,
    max_bytes: int = 16 * 1024 * 1024,
) -> bytes:
    return read_sidecar_member_bytes(
        path,
        label=label,
        error_prefix="turn-run",
        max_bytes=max_bytes,
    )


def _read_json_object(path: Path, *, label: str) -> dict[str, Any]:
    return read_sidecar_json_object(
        path,
        label=label,
        error_prefix="turn-run",
        root_error_code="bad-turn-run-artifact",
    )


def _read_text(path: Path, *, label: str) -> str:
    return read_sidecar_text(path, label=label, error_prefix="turn-run")


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


def _write_json_artifact(
    run_path: Path,
    key: str,
    value: dict[str, Any],
    *,
    schema: str | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    filename = ARTIFACT_FILES[key]
    atomic_write_json(run_path / filename, value)
    return _artifact_ref(
        filename=filename,
        sha256=_json_digest(value),
        media_type="application/json",
        schema=schema if schema is not None else value.get("schema"),
        role=role,
    )


def _write_text_artifact(run_path: Path, key: str, value: str) -> dict[str, Any]:
    filename = ARTIFACT_FILES[key]
    atomic_write_text(run_path / filename, value)
    return _artifact_ref(
        filename=filename,
        sha256=sha256_text(value),
        media_type="text/plain; charset=utf-8",
        schema=None,
        role=None,
    )


def _strict_mapping(value: Any, *, label: str, fields: set[str], code: str) -> dict[str, Any]:
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


def _run_directory(value: str | Path) -> Path:
    return resolve_sidecar_directory(
        value,
        manifest_file=RUN_MANIFEST_FILE,
        unknown_code="unknown-turn-run",
        kind_label="turn run",
    )


def _open_run_lock(run_path: Path, *, create: bool) -> int:
    return open_sidecar_lock(
        run_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="turn-run",
        kind_label="turn run",
        create=create,
    )


def _ensure_run_lock(run_path: Path) -> None:
    ensure_sidecar_lock(
        run_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="turn-run",
        kind_label="turn run",
    )


def _run_lock(run_path: Path) -> ContextManager[None]:
    return sidecar_lock(
        run_path,
        lock_file=RUN_LOCK_FILE,
        error_prefix="turn-run",
        kind_label="turn run",
        busy_message="another coordinator is advancing this turn run",
    )


def _shell(parts: list[str]) -> str:
    return shell_command(parts)


def _next_action(run_path: Path, status: str, artifacts: dict[str, Any]) -> dict[str, Any]:
    accept = _shell(["./lacuna", "turn", "run", "accept", str(run_path), "MODEL_RETURN.json"])
    commit = _shell(["./lacuna", "turn", "run", "commit", str(run_path)])
    visibility = "Do not present proposed narration as having happened; only a passing commit receipt is player-visible."
    if status == "awaiting-solo-proposal":
        return {
            "owner": "parent-coordinator",
            "action": "Use the complete packet and its response_contract proposal template to produce one exact turn proposal. Replace the narration placeholder; empty operations are valid.",
            "input_path": str(run_path / ARTIFACT_FILES["packet"]),
            "expected_schema": TURN_PROPOSAL_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "awaiting-planner":
        aliases = PROVIDER_AGENT_ALIASES["lacuna-planner"]
        return {
            "owner": "lacuna-planner",
            "action": (
                "Spawn or invoke exactly one configured planner role and give it the complete card unchanged "
                f"(Codex `{aliases['codex']}`; Claude Code/Gemini CLI `{aliases['claude-code']}`; "
                "ChatGPT: a role-dedicated planner context). Save only its exact JSON object, without prose or code fences."
            ),
            "input_path": str(run_path / ARTIFACT_FILES["planner_card"]),
            "expected_schema": PLANNER_RETURN_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "awaiting-narrator":
        aliases = PROVIDER_AGENT_ALIASES["lacuna-narrator"]
        return {
            "owner": "lacuna-narrator",
            "action": (
                "Spawn or invoke exactly one audience-only narrator role and give it the complete card unchanged "
                f"(Codex `{aliases['codex']}`; Claude Code/Gemini CLI `{aliases['claude-code']}`; "
                "ChatGPT: a role-dedicated narrator context). Save only its exact JSON object."
            ),
            "input_path": str(run_path / ARTIFACT_FILES["narrator_card"]),
            "expected_schema": NARRATOR_RETURN_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "awaiting-pair-proposal":
        return {
            "owner": "parent-coordinator",
            "action": "Review the safe narration-only proposal draft. Add only justified typed custody, then submit the exact proposal object.",
            "input_path": str(run_path / ARTIFACT_FILES["proposal_draft"]),
            "expected_schema": TURN_PROPOSAL_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "awaiting-proposal-builder":
        aliases = PROVIDER_AGENT_ALIASES["lacuna-proposal-builder"]
        return {
            "owner": "lacuna-proposal-builder",
            "action": (
                "Spawn or invoke exactly one proposal-builder role and give it the complete card unchanged "
                f"(Codex `{aliases['codex']}`; Claude Code/Gemini CLI `{aliases['claude-code']}`; "
                "ChatGPT: a role-dedicated proposal-builder context). Save only its exact JSON proposal object."
            ),
            "input_path": str(run_path / ARTIFACT_FILES["proposal_builder_card"]),
            "expected_schema": TURN_PROPOSAL_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "awaiting-verifier":
        aliases = PROVIDER_AGENT_ALIASES["lacuna-verifier"]
        return {
            "owner": "lacuna-verifier",
            "action": (
                "Spawn or invoke exactly one independent verifier role and give it the complete fail-closed card unchanged "
                f"(Codex `{aliases['codex']}`; Claude Code/Gemini CLI `{aliases['claude-code']}`; "
                "ChatGPT: an independent role-dedicated verifier context). Save only its exact JSON object."
            ),
            "input_path": str(run_path / ARTIFACT_FILES["verifier_card"]),
            "expected_schema": VERIFIER_RETURN_SCHEMA,
            "command": accept,
            "player_visibility": visibility,
        }
    if status == "verifier-refused":
        return {
            "owner": "parent-coordinator",
            "action": "Do not commit. Inspect the verifier findings and start a fresh run from the same exact player input after correcting the host policy or proposal process.",
            "input_path": str(run_path / ARTIFACT_FILES["verifier_return"]),
            "expected_schema": None,
            "command": None,
            "player_visibility": visibility,
        }
    if status == "ready-to-commit":
        return {
            "owner": "parent-coordinator",
            "action": "Review the accepted proposal and its exact rollback preparation, then ask the Lacuna kernel to replay that frozen envelope atomically.",
            "input_path": str(run_path / ARTIFACT_FILES["preparation"]),
            "expected_schema": TURN_PREPARATION_SCHEMA,
            "command": commit,
            "player_visibility": visibility,
        }
    if status == "committed":
        return {
            "owner": "parent-coordinator",
            "action": "Present only the top-level narration from the passing turn receipt, then retain the run directory for replay or audit.",
            "input_path": str(run_path / ARTIFACT_FILES["receipt"]),
            "expected_schema": TURN_RECEIPT_SCHEMA,
            "command": None,
            "player_visibility": "The passing receipt narration may now be presented to the player.",
        }
    raise LacunaError("bad-turn-run", f"unknown turn run status {status!r}")


def _render_next(manifest: dict[str, Any]) -> str:
    next_action = manifest["next_action"]
    lines = [
        "# Lacuna turn run — next action",
        "",
        f"Run: `{manifest['run_id']}`",
        f"Status: **{manifest['status']}**",
        f"Selected topology: **{manifest['selected_mode']}**",
        f"Owner: **{next_action['owner']}**",
        "",
        next_action["action"],
        "",
    ]
    if next_action["input_path"] is not None:
        lines.append(f"Complete input artifact: `{next_action['input_path']}`")
    if next_action["owner"] in PROVIDER_AGENT_ALIASES:
        lines.extend(
            [
                "",
                "Render a complete provider/chat handoff before delegation:",
                "",
                "```bash",
                _shell(
                    [
                        "./lacuna",
                        "turn",
                        "run",
                        "dispatch",
                        manifest["run_path"],
                        "--provider",
                        "portable",
                        "--format",
                        "markdown",
                    ]
                ),
                "```",
            ]
        )
    if next_action["expected_schema"] is not None:
        lines.append(f"Required return schema: `{next_action['expected_schema']}`")
    if next_action["command"] is not None:
        lines.extend(["", "After saving the exact return:", "", "```bash", next_action["command"], "```"])
    lines.extend(
        [
            "",
            f"Player-visibility rule: {next_action['player_visibility']}",
            "",
            "`run.json` is authoritative. This file is a human-readable pointer only.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(run_path: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
    atomic_write_text(run_path / NEXT_FILE, _render_next(manifest))


def _safe_proposal_draft(packet: dict[str, Any], *, narration: str | None = None) -> dict[str, Any]:
    proposal = copy.deepcopy(packet["response_contract"]["proposal_template"])
    if narration is not None:
        proposal["narration"] = narration
    proposal["operations"] = []
    proposal["revealed_assertion_ids"] = []
    return proposal


def begin_turn_run(
    cube: Cube,
    *,
    reference: str,
    resolved_cube_path: str,
    root: str | Path,
    player_input: str,
    input_kind: str = "play-turn",
    audience_id: str,
    actor_id: str,
    director: bool,
    world_id: str | None,
    allow_anchor: bool,
    mode: str,
    include_planner_context_on_commit: bool,
) -> dict[str, Any]:
    """Open one source-bound turn and materialize a resumable sidecar run.

    The run directory is a host artifact, not an event-ledger projection. It
    preserves exact prompt/return bytes across separate model and CLI calls and
    keeps commit authority with the parent coordinator.
    """
    if mode not in ORCHESTRATION_MODES:
        raise LacunaError("unknown-orchestration-mode", f"mode must be one of {list(ORCHESTRATION_MODES)}")
    if include_planner_context_on_commit and not director:
        raise LacunaError(
            "planner-context-not-granted",
            "an audience-profile run cannot request privileged planner context on commit",
        )
    try:
        reference = require_string(reference, "reference", max_len=4096)
        resolved_cube_path = require_string(resolved_cube_path, "resolved_cube_path", max_len=4096)
        player_input = require_string(player_input, "player_input", max_len=50000)
    except ValueError as exc:
        raise LacunaError("bad-turn-run-input", str(exc)) from exc
    try:
        bound_cube_path = cube.root.resolve(strict=True)
        supplied_cube_path = Path(resolved_cube_path).expanduser().resolve(strict=True)
    except OSError as exc:
        raise LacunaError(
            "bad-turn-run-input",
            f"cannot resolve the turn cube path: {exc}",
        ) from exc
    if supplied_cube_path != bound_cube_path:
        _fail(
            "turn-run-cube-path-mismatch",
            "resolved_cube_path must name the exact Cube object used to freeze the turn",
            {"expected": str(bound_cube_path), "actual": str(supplied_cube_path)},
        )
    resolved_cube_path = str(bound_cube_path)
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        raise LacunaError(
            "cube-verification-failed",
            "refusing to open a turn run from a cube that does not pass deterministic verification",
        )

    # Manufacture all source-bound exchange objects before creating any visible
    # run directory. Validation errors therefore leave no run-shaped orphan.
    packet = build_turn_packet(
        cube,
        audience_id=audience_id,
        actor_id=actor_id,
        player_input=player_input,
        input_kind=input_kind,
        director=director,
        world_id=world_id,
        allow_anchor=allow_anchor,
    )
    packet_digest = turn_packet_sha256(packet)
    plan = build_orchestration_plan(packet, mode=mode)
    selected_mode = plan["selected_mode"]
    draft = _safe_proposal_draft(packet) if selected_mode == "solo" else None
    planner_card = (
        build_turn_task_card(packet, role="lacuna-planner")
        if selected_mode != "solo"
        else None
    )
    status = "awaiting-solo-proposal" if selected_mode == "solo" else "awaiting-planner"

    root_path = Path(root).expanduser().resolve()
    try:
        root_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise LacunaError("turn-run-create-failed", f"cannot create turn run root {root_path}: {exc}") from exc
    if not root_path.is_dir():
        raise LacunaError("turn-run-create-failed", f"turn run root is not a directory: {root_path}")

    run_id = new_id("run")
    run_path = root_path / run_id
    created_at = utc_now()
    with publish_private_directory(
        run_path,
        error_code="turn-run-create-failed",
        kind_label="turn run",
    ) as staging_path:
        _ensure_run_lock(staging_path)
        artifacts: dict[str, Any] = {key: None for key in ARTIFACT_KEYS}
        artifacts["player_input"] = _write_text_artifact(
            staging_path, "player_input", player_input
        )
        artifacts["packet"] = _write_json_artifact(
            staging_path,
            "packet",
            packet,
            schema=packet["schema"],
        )
        artifacts["plan"] = _write_json_artifact(
            staging_path,
            "plan",
            plan,
            schema=plan["schema"],
        )
        if selected_mode == "solo":
            assert draft is not None
            artifacts["proposal_draft"] = _write_json_artifact(
                staging_path,
                "proposal_draft",
                draft,
                schema=TURN_PROPOSAL_SCHEMA,
                role="parent-coordinator",
            )
        else:
            assert planner_card is not None
            artifacts["planner_card"] = _write_json_artifact(
                staging_path,
                "planner_card",
                planner_card,
                schema=TURN_TASK_CARD_SCHEMA,
                role="lacuna-planner",
            )
        manifest: dict[str, Any] = {
            "event": TURN_RUN_EVENT,
            "schema": TURN_RUN_SCHEMA,
            "project_version": __version__,
            "run_id": run_id,
            "run_path": str(run_path),
            "created_at": created_at,
            "updated_at": created_at,
            "reference": reference,
            "resolved_cube_path": resolved_cube_path,
            "cube_id": packet["cube_id"],
            "requested_mode": mode,
            "selected_mode": selected_mode,
            "include_planner_context_on_commit": bool(include_planner_context_on_commit),
            "status": status,
            "turn_identity": {
                "request_id": packet["request_id"],
                "request_source_id": packet["request_source_id"],
                "proposal_id": packet["response_contract"]["proposal_template"]["proposal_id"],
                "expected_head": packet["expected_head"],
                "player_input_sha256": packet["player_input_sha256"],
                "packet_sha256": packet_digest,
            },
            "artifacts": artifacts,
            "next_action": {},
            "nonclaims": [
                "The turn run is a sidecar directory, not a ledger event, authority grant, provider attestation, or proof of model isolation.",
                "Task cards and verifier returns are advisory; only a passing kernel commit receipt changes the cube.",
                "The run retains exact player input and model artifacts outside the cube; protect the directory according to its most privileged card.",
                "A generated proposal draft is not approved merely because it is well-formed.",
                "Ready-to-commit means the exact envelope passed a local rollback rehearsal; it is neither committed nor a reservation of the request head.",
                "The .run.lock file coordinates cooperative same-host callers only; it is not a distributed lock or a hostile-host security boundary.",
            ],
        }
        manifest["next_action"] = _next_action(run_path, status, artifacts)
        _write_manifest(staging_path, manifest)
    return audit_turn_run(run_path)


def _validate_artifact_ref(run_path: Path, key: str, value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    document = _strict_mapping(
        value,
        label=f"artifacts.{key}",
        fields=ARTIFACT_FIELDS,
        code="bad-turn-run",
    )
    expected_filename = ARTIFACT_FILES[key]
    if document.get("path") != expected_filename:
        _fail(
            "turn-run-path-mismatch",
            f"artifacts.{key}.path must be {expected_filename!r}",
            {"actual": document.get("path")},
        )
    digest = document.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        _fail("bad-turn-run", f"artifacts.{key}.sha256 must be a lowercase SHA-256 digest")
    if key == "packet":
        actual_metadata = (
            document.get("media_type"),
            document.get("schema"),
            document.get("role"),
        )
        if (
            document.get("media_type") != "application/json"
            or document.get("schema") not in SUPPORTED_TURN_REQUEST_SCHEMAS
            or document.get("role") is not None
        ):
            _fail(
                "turn-run-artifact-metadata-mismatch",
                "packet artifact metadata is not a supported turn-request exchange contract",
                {
                    "supported_schemas": list(SUPPORTED_TURN_REQUEST_SCHEMAS),
                    "actual": actual_metadata,
                },
            )
    elif key == "proposal":
        expected_media_type = "application/json"
        expected_schema = TURN_PROPOSAL_SCHEMA
        if document.get("media_type") != expected_media_type or document.get("schema") != expected_schema:
            _fail(
                "turn-run-artifact-metadata-mismatch",
                "proposal artifact metadata does not match its fixed exchange contract",
                {
                    "expected_media_type": expected_media_type,
                    "actual_media_type": document.get("media_type"),
                    "expected_schema": expected_schema,
                    "actual_schema": document.get("schema"),
                },
            )
    else:
        expected_media_type, expected_schema, expected_role = ARTIFACT_METADATA[key]
        actual_metadata = (
            document.get("media_type"),
            document.get("schema"),
            document.get("role"),
        )
        expected_metadata = (expected_media_type, expected_schema, expected_role)
        if actual_metadata != expected_metadata:
            _fail(
                "turn-run-artifact-metadata-mismatch",
                f"artifact {key!r} metadata does not match its fixed role and schema",
                {"expected": expected_metadata, "actual": actual_metadata},
            )
    path = run_path / expected_filename
    if key == "player_input":
        actual = sha256_text(_read_text(path, label=key))
    else:
        artifact_document = _read_json_object(path, label=key)
        if key == "packet" and artifact_document.get("schema") != document.get("schema"):
            _fail(
                "turn-run-artifact-metadata-mismatch",
                "packet artifact schema metadata differs from the retained packet",
                {"metadata": document.get("schema"), "artifact": artifact_document.get("schema")},
            )
        actual = _json_digest(artifact_document)
    if actual != digest:
        _fail(
            "turn-run-artifact-digest-mismatch",
            f"artifact {key!r} no longer matches run.json",
            {"expected": digest, "actual": actual, "path": str(path)},
        )
    return document


def _validate_final_proposal(value: Any, packet: dict[str, Any]) -> dict[str, Any]:
    proposal = validate_proposal_binding(value, packet)
    if proposal["narration"] == TURN_NARRATION_PLACEHOLDER:
        raise LacunaError(
            "unreplaced-narration-template",
            "turn proposal still contains the fail-closed narration placeholder",
        )
    return proposal


def _expected_status(
    *,
    selected_mode: str,
    planner_return: dict[str, Any] | None,
    narrator_return: dict[str, Any] | None,
    proposal: dict[str, Any] | None,
    verifier_return: dict[str, Any] | None,
    receipt: dict[str, Any] | None,
) -> str:
    if receipt is not None:
        return "committed"
    if verifier_return is not None:
        return "ready-to-commit" if verifier_return["status"] == "pass" else "verifier-refused"
    if proposal is not None:
        return "awaiting-verifier" if selected_mode == "full" else "ready-to-commit"
    if selected_mode == "solo":
        return "awaiting-solo-proposal"
    if narrator_return is not None:
        return "awaiting-proposal-builder" if selected_mode == "full" else "awaiting-pair-proposal"
    if planner_return is not None:
        return "awaiting-narrator"
    return "awaiting-planner"


def _expected_artifact_keys(*, selected_mode: str, status: str) -> set[str]:
    base = {"player_input", "packet", "plan"}
    if selected_mode == "solo":
        expected = base | {"proposal_draft"}
        if status in {"ready-to-commit", "committed"}:
            expected |= {"proposal", "preparation"}
        if status == "committed":
            expected.add("receipt")
        return expected

    expected = base | {"planner_card"}
    if status != "awaiting-planner":
        expected |= {"planner_return", "narrator_card"}
    if status not in {"awaiting-planner", "awaiting-narrator"}:
        expected.add("narrator_return")
    if selected_mode == "pair":
        if status not in {"awaiting-planner", "awaiting-narrator"}:
            expected.add("proposal_draft")
        if status in {"ready-to-commit", "committed"}:
            expected |= {"proposal", "preparation"}
        if status == "committed":
            expected.add("receipt")
        return expected

    if status not in {"awaiting-planner", "awaiting-narrator"}:
        expected.add("proposal_builder_card")
    if status in {"awaiting-verifier", "verifier-refused", "ready-to-commit", "committed"}:
        expected |= {"proposal", "verifier_card"}
    if status in {"verifier-refused", "ready-to-commit", "committed"}:
        expected.add("verifier_return")
    if status in {"ready-to-commit", "committed"}:
        expected.add("preparation")
    if status == "committed":
        expected.add("receipt")
    return expected


def _audit_next_pointer(run_path: Path, manifest: dict[str, Any]) -> None:
    path = run_path / NEXT_FILE
    actual = _read_text(path, label="turn run next pointer")
    expected = _render_next(manifest)
    if actual != expected:
        _fail(
            "turn-run-next-pointer-mismatch",
            "NEXT.md does not match the deterministic action in run.json",
            {"path": str(path)},
        )


def _audit_turn_run_unlocked(
    value: str | Path,
    *,
    audit_next: bool = True,
) -> dict[str, Any]:
    """Strictly audit a sidecar run while its caller holds .run.lock."""
    run_path = _run_directory(value)
    manifest = _read_json_object(run_path / RUN_MANIFEST_FILE, label="turn run manifest")
    manifest = _strict_mapping(
        manifest,
        label="turn run manifest",
        fields=MANIFEST_FIELDS,
        code="bad-turn-run",
    )
    if manifest.get("event") != TURN_RUN_EVENT or manifest.get("schema") != TURN_RUN_SCHEMA:
        _fail("bad-turn-run", f"turn run must use event {TURN_RUN_EVENT!r} and schema {TURN_RUN_SCHEMA!r}")
    try:
        require_string(manifest.get("project_version"), "project_version", max_len=128)
        require_id(manifest.get("run_id"), "run_id")
        require_string(manifest.get("created_at"), "created_at", max_len=128)
        require_string(manifest.get("updated_at"), "updated_at", max_len=128)
        require_string(manifest.get("reference"), "reference", max_len=4096)
        require_string(manifest.get("resolved_cube_path"), "resolved_cube_path", max_len=4096)
        require_id(manifest.get("cube_id"), "cube_id")
    except ValueError as exc:
        raise LacunaError("bad-turn-run", str(exc)) from exc
    if manifest.get("run_path") != str(run_path):
        _fail(
            "turn-run-path-mismatch",
            "run_path does not name the directory containing run.json",
            {"expected": str(run_path), "actual": manifest.get("run_path")},
        )
    requested_mode = manifest.get("requested_mode")
    selected_mode = manifest.get("selected_mode")
    if requested_mode not in ORCHESTRATION_MODES or selected_mode not in {"solo", "pair", "full"}:
        _fail("bad-turn-run", "requested_mode or selected_mode is invalid")
    if not isinstance(manifest.get("include_planner_context_on_commit"), bool):
        _fail("bad-turn-run", "include_planner_context_on_commit must be boolean")
    if manifest.get("status") not in TURN_RUN_STATUSES:
        _fail("bad-turn-run", "status is invalid")

    identity = _strict_mapping(
        manifest.get("turn_identity"),
        label="turn_identity",
        fields=TURN_IDENTITY_FIELDS,
        code="bad-turn-run",
    )
    for field in ("request_id", "request_source_id", "proposal_id"):
        try:
            require_id(identity.get(field), field)
        except ValueError as exc:
            raise LacunaError("bad-turn-run", str(exc)) from exc
    for field in ("expected_head", "player_input_sha256", "packet_sha256"):
        digest = identity.get(field)
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            _fail("bad-turn-run", f"turn_identity.{field} must be a lowercase SHA-256 digest")

    artifacts = _strict_mapping(
        manifest.get("artifacts"),
        label="artifacts",
        fields=set(ARTIFACT_KEYS),
        code="bad-turn-run",
    )
    refs = {key: _validate_artifact_ref(run_path, key, artifacts[key]) for key in ARTIFACT_KEYS}
    if refs["player_input"] is None or refs["packet"] is None or refs["plan"] is None:
        _fail("bad-turn-run", "player_input, packet, and plan artifacts are mandatory")

    player_input = _read_text(run_path / ARTIFACT_FILES["player_input"], label="player input")
    packet = validate_turn_packet(_read_json_object(run_path / ARTIFACT_FILES["packet"], label="turn packet"))
    if packet["player_input"] != player_input:
        _fail("turn-run-input-mismatch", "retained player input differs from the packet body")
    packet_digest = turn_packet_sha256(packet)
    if packet_digest != identity["packet_sha256"]:
        _fail("turn-run-identity-mismatch", "packet digest differs from turn_identity.packet_sha256")
    expected_identity = {
        "request_id": packet["request_id"],
        "request_source_id": packet["request_source_id"],
        "proposal_id": packet["response_contract"]["proposal_template"]["proposal_id"],
        "expected_head": packet["expected_head"],
        "player_input_sha256": packet["player_input_sha256"],
        "packet_sha256": packet_digest,
    }
    mismatches = {
        key: {"expected": expected, "actual": identity.get(key)}
        for key, expected in expected_identity.items()
        if identity.get(key) != expected
    }
    if mismatches:
        _fail("turn-run-identity-mismatch", "turn_identity is not bound to the retained packet", {"mismatches": mismatches})
    if packet["cube_id"] != manifest["cube_id"]:
        _fail("turn-run-identity-mismatch", "manifest cube_id differs from the packet")

    plan = _read_json_object(run_path / ARTIFACT_FILES["plan"], label="orchestration plan")
    expected_plan = build_orchestration_plan(packet, mode=requested_mode)
    if plan != expected_plan:
        _fail("turn-run-plan-mismatch", "retained orchestration plan is not the deterministic plan for this packet")
    if expected_plan["selected_mode"] != selected_mode:
        _fail("turn-run-plan-mismatch", "manifest selected_mode differs from the deterministic plan")

    planner_return: dict[str, Any] | None = None
    narrator_return: dict[str, Any] | None = None
    proposal: dict[str, Any] | None = None
    preparation: dict[str, Any] | None = None
    verifier_return: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None

    if selected_mode == "solo":
        if refs["planner_card"] is not None or refs["planner_return"] is not None or refs["narrator_card"] is not None or refs["narrator_return"] is not None or refs["proposal_builder_card"] is not None or refs["verifier_card"] is not None or refs["verifier_return"] is not None:
            _fail("bad-turn-run", "solo runs must not contain delegated-role artifacts")
        expected_draft = _safe_proposal_draft(packet)
        actual_draft = _read_json_object(run_path / ARTIFACT_FILES["proposal_draft"], label="proposal draft")
        if refs["proposal_draft"] is None or actual_draft != expected_draft:
            _fail("turn-run-artifact-mismatch", "solo proposal draft is not the safe packet template")
    else:
        expected_planner_card = build_turn_task_card(packet, role="lacuna-planner")
        actual_planner_card = _read_json_object(run_path / ARTIFACT_FILES["planner_card"], label="planner card")
        if refs["planner_card"] is None or actual_planner_card != expected_planner_card:
            _fail("turn-run-artifact-mismatch", "planner card is not the deterministic card for this packet")
        if refs["planner_return"] is not None:
            planner_return = validate_planner_return(
                _read_json_object(run_path / ARTIFACT_FILES["planner_return"], label="planner return"),
                packet,
            )
        if refs["narrator_card"] is not None:
            if planner_return is None:
                _fail("bad-turn-run", "narrator card requires an accepted planner return")
            expected_card = build_turn_task_card(packet, role="lacuna-narrator", planner_return=planner_return)
            actual_card = _read_json_object(run_path / ARTIFACT_FILES["narrator_card"], label="narrator card")
            if actual_card != expected_card:
                _fail("turn-run-artifact-mismatch", "narrator card is not bound to the accepted planner return")
        if refs["narrator_return"] is not None:
            if planner_return is None:
                _fail("bad-turn-run", "narrator return requires an accepted planner return")
            narrator_return = validate_narrator_return(
                _read_json_object(run_path / ARTIFACT_FILES["narrator_return"], label="narrator return"),
                packet,
                planner_return,
            )
        if selected_mode == "pair" and refs["proposal_draft"] is not None:
            if narrator_return is None:
                _fail("bad-turn-run", "pair proposal draft requires an accepted narrator return")
            expected_draft = _safe_proposal_draft(packet, narration=narrator_return["narration"])
            actual_draft = _read_json_object(run_path / ARTIFACT_FILES["proposal_draft"], label="proposal draft")
            if actual_draft != expected_draft:
                _fail("turn-run-artifact-mismatch", "pair proposal draft is not the safe narration-only draft")
        if selected_mode == "full" and refs["proposal_builder_card"] is not None:
            if planner_return is None or narrator_return is None:
                _fail("bad-turn-run", "proposal-builder card requires accepted planner and narrator returns")
            expected_card = build_turn_task_card(
                packet,
                role="lacuna-proposal-builder",
                planner_return=planner_return,
                narrator_return=narrator_return,
            )
            actual_card = _read_json_object(run_path / ARTIFACT_FILES["proposal_builder_card"], label="proposal-builder card")
            if actual_card != expected_card:
                _fail("turn-run-artifact-mismatch", "proposal-builder card is not bound to accepted upstream returns")

    if refs["proposal"] is not None:
        proposal = _validate_final_proposal(
            _read_json_object(run_path / ARTIFACT_FILES["proposal"], label="turn proposal"),
            packet,
        )
    if refs["preparation"] is not None:
        if proposal is None:
            _fail("bad-turn-run", "turn preparation requires an accepted proposal")
        raw_preparation = _read_json_object(
            run_path / ARTIFACT_FILES["preparation"],
            label="turn preparation",
        )
        with Cube.open(manifest["resolved_cube_path"]) as cube:
            if cube.meta("cube_id") != manifest["cube_id"]:
                _fail("turn-run-cube-mismatch", "resolved cube no longer matches this run's cube_id")
            preparation = validate_turn_preparation(
                cube,
                raw_preparation,
                proposal,
                include_planner_context=manifest["include_planner_context_on_commit"],
            )

    if refs["verifier_card"] is not None:
        if selected_mode != "full" or proposal is None:
            _fail("bad-turn-run", "verifier card is valid only for a full run with an accepted proposal")
        expected_card = build_turn_task_card(packet, role="lacuna-verifier", proposal=proposal)
        actual_card = _read_json_object(run_path / ARTIFACT_FILES["verifier_card"], label="verifier card")
        if actual_card != expected_card:
            _fail("turn-run-artifact-mismatch", "verifier card is not bound to the accepted proposal")
    if refs["verifier_return"] is not None:
        if proposal is None:
            _fail("bad-turn-run", "verifier return requires an accepted proposal")
        verifier_return = validate_verifier_return(
            _read_json_object(run_path / ARTIFACT_FILES["verifier_return"], label="verifier return"),
            packet,
            proposal,
        )
    if refs["receipt"] is not None:
        if proposal is None or preparation is None:
            _fail("bad-turn-run", "turn receipt requires an accepted proposal and preparation")
        receipt = validate_turn_receipt(
            _read_json_object(run_path / ARTIFACT_FILES["receipt"], label="turn receipt"),
            proposal,
            preparation,
        )
        with Cube.open(manifest["resolved_cube_path"]) as cube:
            if cube.meta("cube_id") != manifest["cube_id"]:
                _fail("turn-run-cube-mismatch", "resolved cube no longer matches this run's cube_id")
            verification = cube.verify()
            if verification["overall_status"] != "pass":
                raise LacunaError(
                    "cube-verification-failed",
                    "committed turn run points at a cube that fails verification",
                    verification,
                )
            committed = cube.committed_change(preparation["proposal_id"])
            if committed is None:
                _fail("turn-run-receipt-mismatch", "receipt names a change absent from the durable ledger")
            durable_expected = {
                "payload_sha256": preparation["change_payload_sha256"],
                "change": preparation["change"],
                "event_chain": preparation["event_chain"],
            }
            if canonical_json(committed) != canonical_json(durable_expected):
                _fail(
                    "turn-run-receipt-mismatch",
                    "durable change differs from the exact preparation",
                    {
                        "expected_sha256": _json_digest(durable_expected),
                        "actual_sha256": _json_digest(committed),
                    },
                )

    expected_status = _expected_status(
        selected_mode=selected_mode,
        planner_return=planner_return,
        narrator_return=narrator_return,
        proposal=proposal,
        verifier_return=verifier_return,
        receipt=receipt,
    )
    if manifest["status"] != expected_status:
        _fail(
            "turn-run-state-mismatch",
            "manifest status does not match its accepted artifacts",
            {"expected": expected_status, "actual": manifest["status"]},
        )
    expected_present = _expected_artifact_keys(
        selected_mode=selected_mode,
        status=expected_status,
    )
    actual_present = {key for key, ref in refs.items() if ref is not None}
    if actual_present != expected_present:
        _fail(
            "turn-run-artifact-topology-mismatch",
            "referenced artifacts do not match the exact topology and state",
            {
                "missing": sorted(expected_present - actual_present),
                "unexpected": sorted(actual_present - expected_present),
            },
        )
    if refs["proposal"] is not None:
        expected_proposal_role = (
            "lacuna-proposal-builder" if selected_mode == "full" else "parent-coordinator"
        )
        if refs["proposal"].get("role") != expected_proposal_role:
            _fail(
                "turn-run-artifact-metadata-mismatch",
                "proposal artifact role does not match the selected topology",
                {
                    "expected": expected_proposal_role,
                    "actual": refs["proposal"].get("role"),
                },
            )
    expected_next = _next_action(run_path, expected_status, artifacts)
    next_action = _strict_mapping(
        manifest.get("next_action"),
        label="next_action",
        fields=NEXT_ACTION_FIELDS,
        code="bad-turn-run",
    )
    if next_action != expected_next:
        _fail("turn-run-next-action-mismatch", "next_action is not the deterministic action for this run state")
    if audit_next:
        _audit_next_pointer(run_path, manifest)
    return copy.deepcopy(manifest)


def audit_turn_run(value: str | Path) -> dict[str, Any]:
    """Take the run lock, then audit the complete sidecar chain."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        return _audit_turn_run_unlocked(run_path)


def committed_turn_public_record(value: str | Path) -> dict[str, Any]:
    """Export one exact player-visible pair from a committed managed turn.

    Extraction happens under the run lock after full audit. Private planner,
    proposal, verifier, and preparation material stays out of the returned
    object; immutable ledger positions and retained digests remain available
    for chronological public-history compilation.
    """
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_turn_run_unlocked(run_path)
        if manifest["status"] != "committed":
            _fail(
                "turn-run-not-committed",
                "public history can be compiled only from committed managed turn runs",
                {"run_id": manifest["run_id"], "status": manifest["status"]},
            )
        packet = _read_json_object(run_path / ARTIFACT_FILES["packet"], label="turn packet")
        receipt = _read_json_object(run_path / ARTIFACT_FILES["receipt"], label="turn receipt")
        player_input = _read_text(run_path / ARTIFACT_FILES["player_input"], label="player input")
        input_sha256 = sha256_text(player_input)
        if input_sha256 != packet["player_input_sha256"] or input_sha256 != receipt["player_input_sha256"]:
            _fail(
                "turn-run-public-record-mismatch",
                "retained player input no longer matches the audited packet and receipt",
                {"run_id": manifest["run_id"]},
            )
        if sha256_text(receipt["narration"]) != receipt["narration_sha256"]:
            _fail(
                "turn-run-public-record-mismatch",
                "accepted narration no longer matches its receipt digest",
                {"run_id": manifest["run_id"]},
            )
        receipt_ref = manifest["artifacts"]["receipt"]
        packet_ref = manifest["artifacts"]["packet"]
        assert isinstance(receipt_ref, dict)
        assert isinstance(packet_ref, dict)
        with Cube.open(manifest["resolved_cube_path"]) as cube:
            if cube.meta("cube_id") != manifest["cube_id"]:
                _fail("turn-run-cube-mismatch", "resolved cube no longer matches this run's cube_id")
            request_event_seq = cube.event_sequence(receipt["request_head"])
            commit_event_seq = cube.event_sequence(receipt["head"])
        if commit_event_seq <= request_event_seq:
            _fail(
                "turn-run-public-record-mismatch",
                "committed narration must follow its source-bound request in ledger order",
                {
                    "run_id": manifest["run_id"],
                    "request_event_seq": request_event_seq,
                    "commit_event_seq": commit_event_seq,
                },
            )
        return {
            "run_id": manifest["run_id"],
            "cube_id": manifest["cube_id"],
            "audience_id": receipt["audience_id"],
            "actor_id": receipt["actor_id"],
            "request_id": receipt["request_id"],
            "request_source_id": receipt["request_source_id"],
            "narration_source_id": receipt["narration_source_id"],
            "proposal_id": receipt["proposal_id"],
            "input_kind": packet["input_kind"],
            "request_purpose": packet.get("request_purpose", "play"),
            "player_input": player_input,
            "player_input_sha256": input_sha256,
            "narration": receipt["narration"],
            "narration_sha256": receipt["narration_sha256"],
            "request_head": receipt["request_head"],
            "post_commit_head": receipt["head"],
            "request_event_seq": request_event_seq,
            "commit_event_seq": commit_event_seq,
            "packet_sha256": packet_ref["sha256"],
            "receipt_sha256": receipt_ref["sha256"],
        }


def recover_turn_run(value: str | Path) -> dict[str, Any]:
    """Repair only deterministic NEXT.md after all authoritative members pass."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_turn_run_unlocked(run_path, audit_next=False)
        atomic_write_text(run_path / NEXT_FILE, _render_next(manifest))
        return _audit_turn_run_unlocked(run_path)


def _prepare_proposal_for_run(
    manifest: dict[str, Any],
    proposal: dict[str, Any],
) -> dict[str, Any]:
    with Cube.open(manifest["resolved_cube_path"]) as cube:
        if cube.meta("cube_id") != manifest["cube_id"]:
            _fail("turn-run-cube-mismatch", "resolved cube no longer matches this run's cube_id")
        verification = cube.verify()
        if verification["overall_status"] != "pass":
            raise LacunaError(
                "cube-verification-failed",
                "refusing to prepare a turn against a cube that fails verification",
                verification,
            )
        return prepare_turn_proposal(
            cube,
            proposal,
            include_planner_context=manifest["include_planner_context_on_commit"],
        )


def _accept_turn_run_artifact_unlocked(
    value: str | Path,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Advance one sidecar chain while its caller holds .run.lock."""
    run_path = _run_directory(value)
    manifest = _audit_turn_run_unlocked(run_path)
    packet = validate_turn_packet(_read_json_object(run_path / ARTIFACT_FILES["packet"], label="turn packet"))
    status = manifest["status"]
    artifacts = manifest["artifacts"]
    schema = artifact.get("schema") if isinstance(artifact, dict) else None

    if status == "awaiting-planner":
        if schema != PLANNER_RETURN_SCHEMA:
            _fail("unexpected-turn-run-artifact", f"this run expects {PLANNER_RETURN_SCHEMA!r}", {"actual_schema": schema})
        planner = validate_planner_return(artifact, packet)
        artifacts["planner_return"] = _write_json_artifact(
            run_path,
            "planner_return",
            planner,
            schema=PLANNER_RETURN_SCHEMA,
            role="lacuna-planner",
        )
        narrator_card = build_turn_task_card(packet, role="lacuna-narrator", planner_return=planner)
        artifacts["narrator_card"] = _write_json_artifact(
            run_path,
            "narrator_card",
            narrator_card,
            schema=TURN_TASK_CARD_SCHEMA,
            role="lacuna-narrator",
        )
        new_status = "awaiting-narrator"
    elif status == "awaiting-narrator":
        if schema != NARRATOR_RETURN_SCHEMA:
            _fail("unexpected-turn-run-artifact", f"this run expects {NARRATOR_RETURN_SCHEMA!r}", {"actual_schema": schema})
        planner = validate_planner_return(
            _read_json_object(run_path / ARTIFACT_FILES["planner_return"], label="planner return"),
            packet,
        )
        narrator = validate_narrator_return(artifact, packet, planner)
        artifacts["narrator_return"] = _write_json_artifact(
            run_path,
            "narrator_return",
            narrator,
            schema=NARRATOR_RETURN_SCHEMA,
            role="lacuna-narrator",
        )
        if manifest["selected_mode"] == "pair":
            draft = _safe_proposal_draft(packet, narration=narrator["narration"])
            artifacts["proposal_draft"] = _write_json_artifact(
                run_path,
                "proposal_draft",
                draft,
                schema=TURN_PROPOSAL_SCHEMA,
                role="parent-coordinator",
            )
            new_status = "awaiting-pair-proposal"
        else:
            builder_card = build_turn_task_card(
                packet,
                role="lacuna-proposal-builder",
                planner_return=planner,
                narrator_return=narrator,
            )
            artifacts["proposal_builder_card"] = _write_json_artifact(
                run_path,
                "proposal_builder_card",
                builder_card,
                schema=TURN_TASK_CARD_SCHEMA,
                role="lacuna-proposal-builder",
            )
            new_status = "awaiting-proposal-builder"
    elif status in {"awaiting-solo-proposal", "awaiting-pair-proposal", "awaiting-proposal-builder"}:
        if schema != TURN_PROPOSAL_SCHEMA:
            _fail("unexpected-turn-run-artifact", f"this run expects {TURN_PROPOSAL_SCHEMA!r}", {"actual_schema": schema})
        proposal = _validate_final_proposal(artifact, packet)
        preparation = (
            None
            if manifest["selected_mode"] == "full"
            else _prepare_proposal_for_run(manifest, proposal)
        )
        artifacts["proposal"] = _write_json_artifact(
            run_path,
            "proposal",
            proposal,
            schema=TURN_PROPOSAL_SCHEMA,
            role=("lacuna-proposal-builder" if status == "awaiting-proposal-builder" else "parent-coordinator"),
        )
        if manifest["selected_mode"] == "full":
            verifier_card = build_turn_task_card(packet, role="lacuna-verifier", proposal=proposal)
            artifacts["verifier_card"] = _write_json_artifact(
                run_path,
                "verifier_card",
                verifier_card,
                schema=TURN_TASK_CARD_SCHEMA,
                role="lacuna-verifier",
            )
            new_status = "awaiting-verifier"
        else:
            assert preparation is not None
            artifacts["preparation"] = _write_json_artifact(
                run_path,
                "preparation",
                preparation,
                schema=TURN_PREPARATION_SCHEMA,
                role="lacuna-kernel",
            )
            new_status = "ready-to-commit"
    elif status == "awaiting-verifier":
        if schema != VERIFIER_RETURN_SCHEMA:
            _fail("unexpected-turn-run-artifact", f"this run expects {VERIFIER_RETURN_SCHEMA!r}", {"actual_schema": schema})
        proposal = _validate_final_proposal(
            _read_json_object(run_path / ARTIFACT_FILES["proposal"], label="turn proposal"),
            packet,
        )
        verifier = validate_verifier_return(artifact, packet, proposal)
        preparation = (
            _prepare_proposal_for_run(manifest, proposal)
            if verifier["status"] == "pass"
            else None
        )
        artifacts["verifier_return"] = _write_json_artifact(
            run_path,
            "verifier_return",
            verifier,
            schema=VERIFIER_RETURN_SCHEMA,
            role="lacuna-verifier",
        )
        if preparation is not None:
            artifacts["preparation"] = _write_json_artifact(
                run_path,
                "preparation",
                preparation,
                schema=TURN_PREPARATION_SCHEMA,
                role="lacuna-kernel",
            )
        new_status = "ready-to-commit" if verifier["status"] == "pass" else "verifier-refused"
    elif status == "verifier-refused":
        raise LacunaError(
            "turn-run-verifier-refused",
            "this run is closed after a verifier refusal; start a fresh run from the retained exact player input",
        )
    elif status == "ready-to-commit":
        raise LacunaError("turn-run-ready", "the run already has an accepted proposal; commit it or start a fresh run")
    else:
        raise LacunaError("turn-run-closed", "the turn run is already committed")

    manifest["status"] = new_status
    manifest["updated_at"] = utc_now()
    manifest["artifacts"] = artifacts
    manifest["next_action"] = _next_action(run_path, new_status, artifacts)
    _write_manifest(run_path, manifest)
    return _audit_turn_run_unlocked(run_path)


def accept_turn_run_artifact(value: str | Path, artifact: dict[str, Any]) -> dict[str, Any]:
    """Take the run lock and accept one exact return artifact."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        return _accept_turn_run_artifact_unlocked(run_path, artifact)


def _commit_turn_run_unlocked(value: str | Path) -> dict[str, Any]:
    """Commit or recover one ready run while its caller holds .run.lock."""
    run_path = _run_directory(value)
    manifest = _audit_turn_run_unlocked(run_path)
    if manifest["status"] != "ready-to-commit":
        raise LacunaError(
            "turn-run-not-ready",
            "turn run is not ready to commit",
            {"status": manifest["status"], "next_action": manifest["next_action"]},
        )
    packet = validate_turn_packet(
        _read_json_object(run_path / ARTIFACT_FILES["packet"], label="turn packet")
    )
    proposal = _validate_final_proposal(
        _read_json_object(run_path / ARTIFACT_FILES["proposal"], label="turn proposal"),
        packet,
    )
    preparation = _read_json_object(
        run_path / ARTIFACT_FILES["preparation"],
        label="turn preparation",
    )
    if manifest["selected_mode"] == "full":
        verifier = validate_verifier_return(
            _read_json_object(
                run_path / ARTIFACT_FILES["verifier_return"],
                label="verifier return",
            ),
            packet,
            proposal,
        )
        if verifier["status"] != "pass":
            raise LacunaError(
                "turn-run-verifier-refused",
                "full runs require a passing verifier return before commit",
            )

    with Cube.open(manifest["resolved_cube_path"]) as cube:
        if cube.meta("cube_id") != manifest["cube_id"]:
            _fail("turn-run-cube-mismatch", "resolved cube no longer matches this run's cube_id")
        if cube.committed_change(proposal["proposal_id"]) is None:
            receipt = commit_prepared_turn(
                cube,
                proposal,
                preparation,
                include_planner_context=manifest["include_planner_context_on_commit"],
            )
        else:
            receipt = recover_prepared_turn_receipt(
                cube,
                proposal,
                preparation,
                include_planner_context=manifest["include_planner_context_on_commit"],
            )
    manifest["artifacts"]["receipt"] = _write_json_artifact(
        run_path,
        "receipt",
        receipt,
        schema=receipt["schema"],
        role="parent-coordinator",
    )
    manifest["status"] = "committed"
    manifest["updated_at"] = utc_now()
    manifest["next_action"] = _next_action(run_path, "committed", manifest["artifacts"])
    _write_manifest(run_path, manifest)
    _audit_turn_run_unlocked(run_path)
    return receipt


def commit_turn_run(value: str | Path) -> dict[str, Any]:
    """Take the run lock, then commit or recover its exact preparation."""
    run_path = _run_directory(value)
    with _run_lock(run_path):
        return _commit_turn_run_unlocked(run_path)


def build_turn_run_dispatch(
    value: str | Path,
    *,
    provider: str = "portable",
) -> dict[str, Any]:
    """Build one self-contained delegated-stage envelope without invoking a model."""
    if provider not in TURN_RUN_PROVIDERS:
        raise LacunaError(
            "unknown-turn-run-provider",
            f"provider must be one of {list(TURN_RUN_PROVIDERS)}",
        )
    run_path = _run_directory(value)
    with _run_lock(run_path):
        manifest = _audit_turn_run_unlocked(run_path)
        stage = {
            "awaiting-planner": ("lacuna-planner", "planner_card", PLANNER_RETURN_SCHEMA),
            "awaiting-narrator": ("lacuna-narrator", "narrator_card", NARRATOR_RETURN_SCHEMA),
            "awaiting-proposal-builder": (
                "lacuna-proposal-builder",
                "proposal_builder_card",
                TURN_PROPOSAL_SCHEMA,
            ),
            "awaiting-verifier": ("lacuna-verifier", "verifier_card", VERIFIER_RETURN_SCHEMA),
        }.get(manifest["status"])
        if stage is None:
            raise LacunaError(
                "turn-run-not-delegated-stage",
                "the current run state is parent-owned and has no worker dispatch",
                {"status": manifest["status"], "next_action": manifest["next_action"]},
            )
        role, artifact_key, return_schema = stage
        ref = manifest["artifacts"][artifact_key]
        if not isinstance(ref, dict):
            _fail("bad-turn-run", f"delegated stage is missing artifact {artifact_key!r}")
        input_path = run_path / ref["path"]
        input_document = _read_json_object(input_path, label=f"{role} task card")
        actual_digest = _json_digest(input_document)
        if actual_digest != ref["sha256"]:
            _fail(
                "turn-run-artifact-digest-mismatch",
                "delegated task card changed while the dispatch was built",
                {"expected": ref["sha256"], "actual": actual_digest, "path": str(input_path)},
            )
        packet = validate_turn_packet(
            _read_json_object(run_path / ARTIFACT_FILES["packet"], label="turn packet")
        )
        alias = provider_alias(role, provider)
        save_path = str(run_path / "MODEL_RETURN.json")
        accept_command = _shell(
            ["./lacuna", "turn", "run", "accept", str(run_path), save_path]
        )
        return {
            "event": "lacuna.turn.agent-dispatch",
            "schema": AGENT_DISPATCH_SCHEMA,
            "run_id": manifest["run_id"],
            "run_path": str(run_path),
            "status": manifest["status"],
            "provider": provider,
            "role": role,
            "agent_name": alias,
            "input_kind": turn_packet_input_kind(packet),
            "input_artifact": {
                "path": str(input_path),
                "sha256": ref["sha256"],
                "media_type": ref["media_type"],
                "schema": ref["schema"],
                "role": ref["role"],
            },
            "input_document": input_document,
            "return_contract": {
                "schema": return_schema,
                "format": "one exact JSON object; no prose, markdown, or code fence",
                "save_path": save_path,
                "accept_command": accept_command,
            },
            "instructions": [
                f"Act as exactly one {role} context using provider alias {alias!r}; perform the task rather than summarizing this handoff.",
                "Your complete and exact task card is input_document in this envelope; do not ask for the local path and do not reconstruct omitted context.",
                "Treat the task card's authority, context boundary, output_contract, and nonclaims as controlling instructions.",
                "Return only one JSON object matching return_contract.schema, with no prose, Markdown, or code fence.",
                "Do not read unrelated run artifacts, edit the sidecar, accept your own return, call commit, or mutate the cube.",
                "The parent coordinator alone saves and accepts the exact return, follows the newly audited state, and commits only when the run says ready-to-commit.",
            ],
            "authority": {
                "worker_may": [
                    "read the complete embedded task card",
                    "reason within that card's least-context boundary",
                    "produce one exact return matching return_contract.schema",
                    "use the card's structured refusal path when safe completion is impossible",
                ],
                "worker_may_not": [
                    "request hidden or unrelated run artifacts merely because a path exists",
                    "edit run.json, NEXT.md, or any retained card",
                    "accept its own artifact",
                    "commit a turn or mutate the cube",
                    "treat provider routing or subagent identity as an authority grant",
                ],
                "parent_only": [
                    "choose whether and where to invoke the worker",
                    "save and accept the worker's exact return",
                    "review readiness and independent verification",
                    "commit the frozen prepared turn",
                    "present accepted receipt narration",
                ],
            },
            "nonclaims": [
                "This envelope does not invoke, authenticate, isolate, or attest any provider, model, or subagent.",
                "The provider alias is routing metadata, not authority and not proof of model identity.",
                "Embedding the exact card prevents a missing-local-file handoff; it does not prove the worker followed the card.",
                "Only turn run accept may advance the sidecar, and only turn run commit may mutate the cube.",
            ],
        }


def turn_run_dispatch_markdown(dispatch: dict[str, Any]) -> str:
    """Render a self-contained handoff legible to chat models and coordinators."""
    lines = [
        "# Lacuna delegated-stage handoff",
        "",
        "**Operational instruction:** perform the named role; do not summarize this handoff.",
        "",
        f"- Run: `{dispatch['run_id']}`",
        f"- Provider route: **{dispatch['provider']}**",
        f"- Role: **{dispatch['role']}**",
        f"- Agent/context name: `{dispatch['agent_name']}`",
        f"- Input kind: **{dispatch['input_kind']}**",
        f"- Card SHA-256: `{dispatch['input_artifact']['sha256']}`",
        f"- Required return schema: `{dispatch['return_contract']['schema']}`",
        "",
        "## Worker instructions",
        "",
    ]
    lines.extend(
        f"{index}. {item}"
        for index, item in enumerate(dispatch["instructions"], start=1)
    )
    lines.extend(
        [
            "",
            "## Complete task card",
            "",
            "This JSON object is the worker's complete input. It is embedded so a ChatGPT-style context does not need local file access.",
            "",
            "```json",
            pretty_json(dispatch["input_document"]),
            "```",
            "",
            "## Exact worker return",
            "",
            f"Return one `{dispatch['return_contract']['schema']}` JSON object only—no prose or code fence.",
            "",
            f"The parent saves those exact bytes to `{dispatch['return_contract']['save_path']}`.",
            "",
            "## Parent coordinator only",
            "",
            "After saving the worker return, the parent—not the worker—runs:",
            "",
            "```bash",
            dispatch["return_contract"]["accept_command"],
            "```",
            "",
            "The worker has no accept or commit authority.",
            "",
            "## Boundary reminders",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in dispatch["nonclaims"])
    lines.append("")
    return "\n".join(lines)


def turn_run_markdown(manifest: dict[str, Any]) -> str:
    """Render the compact resumable state; task cards remain separate artifacts."""
    lines = [
        "# Lacuna turn run",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Path: `{manifest['run_path']}`",
        f"- Status: **{manifest['status']}**",
        f"- Topology: **{manifest['requested_mode']} → {manifest['selected_mode']}**",
        f"- Request: `{manifest['turn_identity']['request_id']}`",
        f"- Packet SHA-256: `{manifest['turn_identity']['packet_sha256']}`",
        "",
        "## Next action",
        "",
        f"Owner: **{manifest['next_action']['owner']}**",
        "",
        manifest["next_action"]["action"],
    ]
    if manifest["next_action"]["input_path"] is not None:
        lines.extend(["", f"Input: `{manifest['next_action']['input_path']}`"])
    if manifest["next_action"]["expected_schema"] is not None:
        lines.append(f"Expected return: `{manifest['next_action']['expected_schema']}`")
    if manifest["next_action"]["command"] is not None:
        lines.extend(["", "```bash", manifest["next_action"]["command"], "```"])
    lines.extend(
        [
            "",
            manifest["next_action"]["player_visibility"],
            "",
            "## Machine-readable run",
            "",
            "```json",
            pretty_json(manifest),
            "```",
            "",
        ]
    )
    return "\n".join(lines)

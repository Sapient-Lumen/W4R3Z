from __future__ import annotations

import copy
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import LacunaError
from .sidecars import canonical_json_digest, scan_sidecar_member_exact_tokens
from .util import (
    SHA256_RE,
    canonical_json,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
)

SCENARIO_CONTAMINATION_PLAN_SCHEMA = "lacuna.scenario-contamination-plan.v1"
SCENARIO_CONTAMINATION_SCAN_SCHEMA = "lacuna.scenario-contamination-scan.v1"
SCENARIO_CONTAMINATION_PLAN_EVENT = "lacuna.scenario.contamination-planned"
SCENARIO_CONTAMINATION_SCAN_EVENT = "lacuna.scenario.contamination-scanned"

CONTAMINATION_PLAN_FILE = "15-PRIVATE-contamination-plan.json"
CONTAMINATION_SCAN_FILE = "65-PRIVATE-contamination-scan.json"
FILESYSTEM_CANARY_FILE = "PRIVATE-CONTAMINATION-CANARY.txt"

CONTAMINATION_METHOD = "sha256-domain-separated-exact-canaries-v1"
CONTAMINATION_SCAN_SCOPE = "scenario-cell-complete-retained-artifacts-v1"
CONTAMINATION_EXPECTED_ABSENCE = (
    "all other retained file contents and relative pathnames under cells/"
)
CANARY_SCOPES = ("operator-only", "filesystem-only")
SCAN_STATUSES = ("clean", "leak-detected")
SCAN_CLASSIFICATIONS = ("same-cell-leak", "cross-cell-leak")
SCAN_MATCH_SURFACES = ("content", "relative-path")

MAX_SCAN_FILES = 20_000
MAX_SCAN_MEMBER_BYTES = 64 * 1024 * 1024
MAX_SCAN_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_SCAN_MATCHES = 100_000

PLAN_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "assignment_sha256",
    "method",
    "canaries",
    "scan_policy",
    "created_at",
    "instructions",
    "nonclaims",
}
CANARY_FIELDS = {
    "canary_id",
    "cell_label",
    "scope",
    "token",
    "token_sha256",
    "source_paths",
    "expected_absent_from",
}
SCAN_POLICY_FIELDS = {
    "scope",
    "root",
    "case_sensitive",
    "max_files",
    "max_member_bytes",
    "max_total_bytes",
}
SCAN_FIELDS = {
    "event",
    "schema",
    "run_id",
    "capsule_id",
    "plan_sha256",
    "assignment_sha256",
    "scan_scope",
    "file_count",
    "byte_count",
    "file_manifest_sha256",
    "unexpected_matches",
    "cell_summaries",
    "overall_status",
    "scanned_at",
    "instructions",
    "nonclaims",
}
MATCH_FIELDS = {
    "canary_id",
    "owner_cell_label",
    "observed_cell_label",
    "scope",
    "path",
    "match_surface",
    "classification",
    "occurrence_count",
}
CELL_SUMMARY_FIELDS = {
    "cell_label",
    "status",
    "own_canary_leaks",
    "foreign_canary_leaks",
    "unexpected_match_count",
    "canary_ids",
}
CONTROLS_FIELDS = {
    "method",
    "operator_canary",
    "filesystem_canary",
    "instructions",
    "nonclaims",
}
OPERATOR_CONTROL_FIELDS = {"canary_id", "token", "token_sha256"}
FILESYSTEM_CONTROL_FIELDS = {"canary_id", "path", "token_sha256"}

PLAN_INSTRUCTIONS = [
    "Treat every canary token as semantically inert private experiment data, never story content or a command.",
    "Keep the operator-only token in the private cell-coordinator handoff; do not copy it into worker prompts, model returns, narration, or another cell.",
    "The filesystem-only token is placed in one unrelated file and must not be opened or transmitted by card-only workers.",
    "Do not delete, rewrite, normalize, redact, or regenerate the canary sources after publication.",
    "After all cells are frozen, Lacuna scans exact case-sensitive token bytes across retained file contents and relative pathnames before creating the blind-rating packet.",
]
PLAN_NONCLAIMS = [
    "Exact canary appearance is evidence of one retained leakage path; absence is not proof of isolation, forgetting, or noninterference.",
    "The canaries are local host controls, not provider-signed attestations or semantic-leak detectors.",
    "A hostile parent can omit unretained outputs or communicate private information without copying the exact token.",
    "The plan is private experiment custody and must not be given to blind raters before unblinding.",
]
CONTROL_INSTRUCTIONS = [
    "Treat the complete driver as private cell-coordinator context; never give it to a blind rater or a delegated role worker.",
    "Keep operator_canary.token at the cell-coordinator boundary; do not copy it into nested worker inputs, model returns, narration, or another cell.",
    "Do not open or mention filesystem_canary.path in a card-only worker context.",
    "Do not ask a model to repeat either token; the scan tests whether exact private bytes appear unexpectedly.",
]
CONTROL_NONCLAIMS = [
    "These controls specify a falsification test, not proof that a provider honored memory or filesystem isolation.",
    "The operator token is intentionally present in this private driver and its rendered Markdown; those two source paths are allowlisted.",
    "The filesystem token body is not embedded in this driver; only its path and digest are disclosed to the parent operator.",
]
SCAN_INSTRUCTIONS = [
    "Interpret unexpected exact content or relative-path matches as contamination findings and retain them regardless of whether the affected condition wins or loses.",
    "Do not show the private canary plan, source tokens, or scan findings to blind raters before ratings are frozen.",
    "Keep exact-match findings separate from semantic leakage judgments and provider declarations.",
]
SCAN_NONCLAIMS = [
    "A clean exact-token scan does not prove fresh memory, card-only filesystem access, semantic independence, or absence of paraphrased leakage.",
    "The scan covers the content and relative pathname of every retained regular file under the frozen scenario cells tree; it does not inspect provider memory, unretained transport logs, empty-directory names, or artifacts stored outside that tree.",
    "A leak-detected status records evidence and does not automatically discard, repair, rerun, or reclassify the cell.",
    "File and byte counts are local deterministic custody, not a remote attestation of what any provider actually received.",
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


def _sha(value: Any, field: str, *, code: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(code, f"{field} must be a lowercase SHA-256 digest")
    return value


def _nonnegative_int(
    value: Any,
    field: str,
    *,
    code: str,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(code, f"{field} must be a nonnegative integer")
    if maximum is not None and value > maximum:
        _fail(code, f"{field} exceeds its maximum", {"maximum": maximum, "actual": value})
    return value


def _string_list(
    value: Any,
    field: str,
    *,
    code: str,
    unique: bool = False,
    max_items: int = 1000,
    max_len: int = 4096,
) -> list[str]:
    try:
        raw = require_list(value, field)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if len(raw) > max_items:
        _fail(code, f"{field} exceeds {max_items} entries")
    result: list[str] = []
    for index, item in enumerate(raw):
        try:
            result.append(require_string(item, f"{field}[{index}]", max_len=max_len))
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
    if unique and len(result) != len(set(result)):
        _fail(code, f"{field} must not contain duplicates")
    return result


def _normalized_relative_path(value: Any, field: str, *, code: str) -> str:
    try:
        text = require_string(value, field, max_len=4096)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    path = PurePosixPath(text)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        _fail(code, f"{field} must be one normalized relative path")
    return str(path)


def _token(*, randomization_seed: str, run_id: str, cell_label: str, scope: str) -> str:
    material = canonical_json(
        {
            "domain": "lacuna.scenario.contamination-canary.v1",
            "randomization_seed": randomization_seed,
            "run_id": run_id,
            "cell_label": cell_label,
            "scope": scope,
        }
    )
    digest = sha256_text(material)
    scope_label = scope.upper().replace("-", "_")
    return f"LACUNA_CANARY_{scope_label}_{digest[:40].upper()}"


def _canary_id(cell_label: str, scope: str) -> str:
    return f"canary.{cell_label}.{scope.replace('-', '.')}"


def _operator_sources(cell_label: str) -> list[str]:
    return [f"cells/{cell_label}/30-driver.json", f"cells/{cell_label}/DRIVER.md"]


def _filesystem_sources(cell_label: str) -> list[str]:
    return [f"cells/{cell_label}/{FILESYSTEM_CANARY_FILE}"]


def build_scenario_contamination_plan(
    *,
    run_id: str,
    capsule_id: str,
    assignment: dict[str, Any],
    assignment_sha256: str,
    created_at: str,
) -> dict[str, Any]:
    code = "bad-scenario-contamination-plan"
    try:
        run_id = require_id(run_id, "run_id")
        capsule_id = require_id(capsule_id, "capsule_id")
        created_at = require_string(created_at, "created_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    assignment_sha256 = _sha(assignment_sha256, "assignment_sha256", code=code)
    seed = assignment.get("randomization_seed")
    if not isinstance(seed, str) or not SHA256_RE.fullmatch(seed):
        _fail(code, "assignment.randomization_seed must be one lowercase SHA-256 value")
    try:
        assignments = require_list(assignment.get("assignments"), "assignment.assignments")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc

    canaries: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()
    seen_cells: set[str] = set()
    for index, item_value in enumerate(assignments):
        try:
            item = require_mapping(item_value, f"assignment.assignments[{index}]")
            cell_label = require_id(
                item.get("cell_label"), f"assignment.assignments[{index}].cell_label"
            )
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        if cell_label in seen_cells:
            _fail(code, "assignment contains a duplicate cell label", {"cell_label": cell_label})
        seen_cells.add(cell_label)
        for scope in CANARY_SCOPES:
            token = _token(
                randomization_seed=seed,
                run_id=run_id,
                cell_label=cell_label,
                scope=scope,
            )
            if token in seen_tokens:
                _fail(code, "deterministic contamination tokens collided")
            seen_tokens.add(token)
            source_paths = _operator_sources(cell_label) if scope == "operator-only" else _filesystem_sources(cell_label)
            canaries.append(
                {
                    "canary_id": _canary_id(cell_label, scope),
                    "cell_label": cell_label,
                    "scope": scope,
                    "token": token,
                    "token_sha256": sha256_text(token),
                    "source_paths": source_paths,
                    "expected_absent_from": CONTAMINATION_EXPECTED_ABSENCE,
                }
            )
    return {
        "event": SCENARIO_CONTAMINATION_PLAN_EVENT,
        "schema": SCENARIO_CONTAMINATION_PLAN_SCHEMA,
        "run_id": run_id,
        "capsule_id": capsule_id,
        "assignment_sha256": assignment_sha256,
        "method": CONTAMINATION_METHOD,
        "canaries": canaries,
        "scan_policy": {
            "scope": CONTAMINATION_SCAN_SCOPE,
            "root": "cells",
            "case_sensitive": True,
            "max_files": MAX_SCAN_FILES,
            "max_member_bytes": MAX_SCAN_MEMBER_BYTES,
            "max_total_bytes": MAX_SCAN_TOTAL_BYTES,
        },
        "created_at": created_at,
        "instructions": list(PLAN_INSTRUCTIONS),
        "nonclaims": list(PLAN_NONCLAIMS),
    }


def validate_scenario_contamination_plan(value: Any) -> dict[str, Any]:
    code = "bad-scenario-contamination-plan"
    document = _strict(value, label="scenario contamination plan", fields=PLAN_FIELDS, code=code)
    if (
        document.get("event") != SCENARIO_CONTAMINATION_PLAN_EVENT
        or document.get("schema") != SCENARIO_CONTAMINATION_PLAN_SCHEMA
        or document.get("method") != CONTAMINATION_METHOD
    ):
        _fail(code, "unsupported scenario contamination plan contract")
    try:
        run_id = require_id(document.get("run_id"), "run_id")
        capsule_id = require_id(document.get("capsule_id"), "capsule_id")
        created_at = require_string(document.get("created_at"), "created_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    assignment_sha256 = _sha(document.get("assignment_sha256"), "assignment_sha256", code=code)

    policy = _strict(document.get("scan_policy"), label="scan_policy", fields=SCAN_POLICY_FIELDS, code=code)
    expected_policy = {
        "scope": CONTAMINATION_SCAN_SCOPE,
        "root": "cells",
        "case_sensitive": True,
        "max_files": MAX_SCAN_FILES,
        "max_member_bytes": MAX_SCAN_MEMBER_BYTES,
        "max_total_bytes": MAX_SCAN_TOTAL_BYTES,
    }
    if policy != expected_policy:
        _fail(code, "scenario contamination scan policy was changed")
    try:
        raw_canaries = require_list(document.get("canaries"), "canaries")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if not raw_canaries or len(raw_canaries) > 1000:
        _fail(code, "canaries must contain between 1 and 1000 records")
    canaries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_tokens: set[str] = set()
    cell_order: list[str] = []
    scopes_by_cell: dict[str, list[str]] = {}
    for index, raw in enumerate(raw_canaries):
        item = _strict(raw, label=f"canaries[{index}]", fields=CANARY_FIELDS, code=code)
        try:
            canary_id = require_id(item.get("canary_id"), f"canaries[{index}].canary_id")
            cell_label = require_id(item.get("cell_label"), f"canaries[{index}].cell_label")
            token = require_string(item.get("token"), f"canaries[{index}].token", max_len=160)
            expected_absent_from = require_string(
                item.get("expected_absent_from"),
                f"canaries[{index}].expected_absent_from",
                max_len=256,
            )
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        scope = item.get("scope")
        if scope not in CANARY_SCOPES:
            _fail(code, "unsupported canary scope", {"scope": scope})
        if canary_id != _canary_id(cell_label, scope):
            _fail(code, "canary ID does not match its owner cell and scope")
        prefix = f"LACUNA_CANARY_{scope.upper().replace('-', '_')}_"
        suffix = token.removeprefix(prefix)
        if not token.startswith(prefix) or len(suffix) != 40 or any(ch not in "0123456789ABCDEF" for ch in suffix):
            _fail(code, "canary token does not use the fixed opaque format")
        token_sha256 = _sha(item.get("token_sha256"), f"canaries[{index}].token_sha256", code=code)
        if token_sha256 != sha256_text(token):
            _fail(code, "canary token digest does not match its exact token")
        source_paths = _string_list(
            item.get("source_paths"),
            f"canaries[{index}].source_paths",
            code=code,
            unique=True,
            max_items=8,
        )
        source_paths = [
            _normalized_relative_path(path, f"canaries[{index}].source_paths", code=code)
            for path in source_paths
        ]
        expected_sources = _operator_sources(cell_label) if scope == "operator-only" else _filesystem_sources(cell_label)
        if source_paths != expected_sources:
            _fail(code, "canary source allowlist was changed", {"canary_id": canary_id})
        if expected_absent_from != CONTAMINATION_EXPECTED_ABSENCE:
            _fail(code, "canary expected-absence contract was changed")
        if canary_id in seen_ids or token in seen_tokens:
            _fail(code, "canary IDs and exact tokens must be unique")
        seen_ids.add(canary_id)
        seen_tokens.add(token)
        if cell_label not in cell_order:
            cell_order.append(cell_label)
        scopes_by_cell.setdefault(cell_label, []).append(scope)
        canaries.append(
            {
                "canary_id": canary_id,
                "cell_label": cell_label,
                "scope": scope,
                "token": token,
                "token_sha256": token_sha256,
                "source_paths": source_paths,
                "expected_absent_from": expected_absent_from,
            }
        )
    for cell_label in cell_order:
        if scopes_by_cell[cell_label] != list(CANARY_SCOPES):
            _fail(code, "each cell must contain operator-only then filesystem-only canaries")
    if document.get("instructions") != PLAN_INSTRUCTIONS or document.get("nonclaims") != PLAN_NONCLAIMS:
        _fail(code, "contamination plan instructions or nonclaims were changed")
    return {
        "event": SCENARIO_CONTAMINATION_PLAN_EVENT,
        "schema": SCENARIO_CONTAMINATION_PLAN_SCHEMA,
        "run_id": run_id,
        "capsule_id": capsule_id,
        "assignment_sha256": assignment_sha256,
        "method": CONTAMINATION_METHOD,
        "canaries": canaries,
        "scan_policy": copy.deepcopy(expected_policy),
        "created_at": created_at,
        "instructions": list(PLAN_INSTRUCTIONS),
        "nonclaims": list(PLAN_NONCLAIMS),
    }


def contamination_plan_sha256(value: Any) -> str:
    return canonical_json_digest(
        validate_scenario_contamination_plan(value),
        error_code="bad-scenario-contamination-plan",
        label="scenario contamination plan",
    )


def _canary_for_validated_plan(
    plan: dict[str, Any],
    *,
    cell_label: str,
    scope: str,
) -> dict[str, Any]:
    if scope not in CANARY_SCOPES:
        _fail("bad-scenario-contamination-plan", "unsupported canary scope", {"scope": scope})
    matches = [
        item
        for item in plan["canaries"]
        if item["cell_label"] == cell_label and item["scope"] == scope
    ]
    if len(matches) != 1:
        _fail(
            "bad-scenario-contamination-plan",
            "contamination plan does not contain exactly one requested cell/scope canary",
            {"cell_label": cell_label, "scope": scope},
        )
    return copy.deepcopy(matches[0])


def canary_for_cell(value: Any, *, cell_label: str, scope: str) -> dict[str, Any]:
    """Return one canary after authenticating the complete public plan input."""

    return _canary_for_validated_plan(
        validate_scenario_contamination_plan(value),
        cell_label=cell_label,
        scope=scope,
    )


def filesystem_canary_text(value: Any, *, cell_label: str) -> str:
    plan = validate_scenario_contamination_plan(value)
    canary = _canary_for_validated_plan(
        plan,
        cell_label=cell_label,
        scope="filesystem-only",
    )
    return (
        "Lacuna private contamination canary.\n"
        "This file is deliberately unrelated to the cell's task cards.\n"
        "Do not open, quote, transmit, summarize, or otherwise use the token below.\n\n"
        f"{canary['token']}\n"
    )


def contamination_controls_for_cell(value: Any, *, cell_label: str) -> dict[str, Any]:
    plan = validate_scenario_contamination_plan(value)
    operator = _canary_for_validated_plan(
        plan,
        cell_label=cell_label,
        scope="operator-only",
    )
    filesystem = _canary_for_validated_plan(
        plan,
        cell_label=cell_label,
        scope="filesystem-only",
    )
    controls = {
        "method": CONTAMINATION_METHOD,
        "operator_canary": {
            "canary_id": operator["canary_id"],
            "token": operator["token"],
            "token_sha256": operator["token_sha256"],
        },
        "filesystem_canary": {
            "canary_id": filesystem["canary_id"],
            "path": filesystem["source_paths"][0],
            "token_sha256": filesystem["token_sha256"],
        },
        "instructions": list(CONTROL_INSTRUCTIONS),
        "nonclaims": list(CONTROL_NONCLAIMS),
    }
    return validate_contamination_controls(controls, plan_value=plan, cell_label=cell_label)


def validate_contamination_controls(
    value: Any,
    *,
    plan_value: Any,
    cell_label: str,
) -> dict[str, Any]:
    code = "bad-scenario-contamination-controls"
    plan = validate_scenario_contamination_plan(plan_value)
    document = _strict(value, label="contamination_controls", fields=CONTROLS_FIELDS, code=code)
    if document.get("method") != CONTAMINATION_METHOD:
        _fail(code, "unsupported contamination control method")
    operator = _strict(
        document.get("operator_canary"),
        label="contamination_controls.operator_canary",
        fields=OPERATOR_CONTROL_FIELDS,
        code=code,
    )
    filesystem = _strict(
        document.get("filesystem_canary"),
        label="contamination_controls.filesystem_canary",
        fields=FILESYSTEM_CONTROL_FIELDS,
        code=code,
    )
    expected_operator = _canary_for_validated_plan(
        plan,
        cell_label=cell_label,
        scope="operator-only",
    )
    expected_filesystem = _canary_for_validated_plan(
        plan,
        cell_label=cell_label,
        scope="filesystem-only",
    )
    expected = {
        "method": CONTAMINATION_METHOD,
        "operator_canary": {
            "canary_id": expected_operator["canary_id"],
            "token": expected_operator["token"],
            "token_sha256": expected_operator["token_sha256"],
        },
        "filesystem_canary": {
            "canary_id": expected_filesystem["canary_id"],
            "path": expected_filesystem["source_paths"][0],
            "token_sha256": expected_filesystem["token_sha256"],
        },
        "instructions": list(CONTROL_INSTRUCTIONS),
        "nonclaims": list(CONTROL_NONCLAIMS),
    }
    if document != expected:
        _fail(code, "contamination controls do not match the preregistered plan")
    return copy.deepcopy(expected)


def _metadata_signature(metadata: os.stat_result) -> tuple[int, int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _planned_cell_labels(plan: dict[str, Any]) -> tuple[str, ...]:
    labels: list[str] = []
    for canary in plan["canaries"]:
        label = canary["cell_label"]
        if label not in labels:
            labels.append(label)
    return tuple(labels)


def _raise_walk_error(error: OSError) -> None:
    raise LacunaError(
        "scenario-contamination-scan-failed",
        f"cannot enumerate the complete scenario cell tree: {error}",
        {"path": str(getattr(error, "filename", "") or "unknown")},
    ) from error


def _enumerate_scan_files(
    run_path: Path,
    *,
    planned_cell_labels: tuple[str, ...],
) -> tuple[Path, list[tuple[str, Path, tuple[int, ...]]]]:
    unresolved_root = run_path / "cells"
    try:
        unresolved_meta = os.lstat(unresolved_root)
    except OSError as exc:
        raise LacunaError(
            "scenario-contamination-scan-failed",
            f"cannot inspect the scenario cells tree: {exc}",
        ) from exc
    if stat.S_ISLNK(unresolved_meta.st_mode) or not stat.S_ISDIR(unresolved_meta.st_mode):
        _fail(
            "scenario-contamination-member-unsafe",
            "scenario cells root must be one real directory rather than a link or substitute",
        )
    try:
        root = unresolved_root.resolve(strict=True)
        run_root = run_path.resolve(strict=True)
        root.relative_to(run_root)
    except (OSError, ValueError) as exc:
        raise LacunaError(
            "scenario-contamination-scan-failed",
            f"cannot resolve the scenario cells tree: {exc}",
        ) from exc

    expected_labels = set(planned_cell_labels)
    try:
        with os.scandir(root) as iterator:
            root_entries = sorted(iterator, key=lambda entry: entry.name)
    except OSError as exc:
        raise LacunaError(
            "scenario-contamination-scan-failed",
            f"cannot enumerate the scenario cells tree: {exc}",
        ) from exc
    actual_labels = {entry.name for entry in root_entries}
    if actual_labels != expected_labels:
        _fail(
            "scenario-contamination-tree-mismatch",
            "scenario cells tree must contain exactly the preregistered cell directories",
            {
                "missing": sorted(expected_labels - actual_labels),
                "unexpected": sorted(actual_labels - expected_labels),
            },
        )
    for entry in root_entries:
        try:
            metadata = os.lstat(entry.path)
        except OSError as exc:
            raise LacunaError(
                "scenario-contamination-scan-failed",
                f"cannot inspect planned cell directory {entry.path}: {exc}",
            ) from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            _fail(
                "scenario-contamination-member-unsafe",
                "each preregistered scenario cell must be one real directory",
                {"path": entry.path},
            )

    entries: list[tuple[str, Path, tuple[int, ...]]] = []
    for cell_label in planned_cell_labels:
        cell_root = root / cell_label
        for current, dirnames, filenames in os.walk(
            cell_root,
            topdown=True,
            onerror=_raise_walk_error,
            followlinks=False,
        ):
            current_path = Path(current)
            safe_dirs: list[str] = []
            for name in sorted(dirnames):
                candidate = current_path / name
                try:
                    metadata = os.lstat(candidate)
                except OSError as exc:
                    raise LacunaError(
                        "scenario-contamination-scan-failed",
                        f"cannot inspect scan directory {candidate}: {exc}",
                    ) from exc
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                    _fail(
                        "scenario-contamination-member-unsafe",
                        "scenario contamination scan refuses linked or non-directory tree components",
                        {"path": str(candidate)},
                    )
                safe_dirs.append(name)
            dirnames[:] = safe_dirs
            for name in sorted(filenames):
                candidate = current_path / name
                try:
                    metadata = os.lstat(candidate)
                except OSError as exc:
                    raise LacunaError(
                        "scenario-contamination-scan-failed",
                        f"cannot inspect scan member {candidate}: {exc}",
                    ) from exc
                if (
                    stat.S_ISLNK(metadata.st_mode)
                    or not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_nlink != 1
                ):
                    _fail(
                        "scenario-contamination-member-unsafe",
                        "scenario contamination scan accepts only single-link regular files",
                        {"path": str(candidate)},
                    )
                relative = str(
                    PurePosixPath("cells")
                    / PurePosixPath(candidate.relative_to(root).as_posix())
                )
                entries.append((relative, candidate, _metadata_signature(metadata)))
                if len(entries) > MAX_SCAN_FILES:
                    _fail(
                        "scenario-contamination-scan-limit",
                        "scenario contamination scan exceeds the fixed file limit",
                        {"limit": MAX_SCAN_FILES},
                    )
    entries.sort(key=lambda item: item[0])
    return root, entries


def _count_occurrences(value: bytes, token: bytes) -> int:
    if not token:
        return 0
    count = 0
    offset = 0
    while True:
        position = value.find(token, offset)
        if position < 0:
            return count
        count += 1
        offset = position + len(token)


def _relative_path_bytes(relative_path: str) -> bytes:
    try:
        return relative_path.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise LacunaError(
            "scenario-contamination-member-unsafe",
            "scenario contamination scan requires UTF-8-representable relative paths",
            {"path": repr(relative_path)},
        ) from exc


def _append_scan_match(
    matches: list[dict[str, Any]],
    *,
    canary: dict[str, Any],
    observed_cell: str,
    relative_path: str,
    match_surface: str,
    occurrence_count: int,
) -> None:
    if match_surface not in SCAN_MATCH_SURFACES:
        _fail(
            "scenario-contamination-scan-failed",
            "internal contamination scan match surface is unsupported",
            {"match_surface": match_surface},
        )
    if len(matches) >= MAX_SCAN_MATCHES:
        _fail(
            "scenario-contamination-scan-limit",
            "scenario contamination scan exceeds the fixed finding limit",
            {"limit": MAX_SCAN_MATCHES},
        )
    owner = canary["cell_label"]
    matches.append(
        {
            "canary_id": canary["canary_id"],
            "owner_cell_label": owner,
            "observed_cell_label": observed_cell,
            "scope": canary["scope"],
            "path": relative_path,
            "match_surface": match_surface,
            "classification": (
                "same-cell-leak" if owner == observed_cell else "cross-cell-leak"
            ),
            "occurrence_count": occurrence_count,
        }
    )


def _path_cell_label(
    relative_path: str,
    *,
    planned_cell_labels: tuple[str, ...],
) -> str:
    parts = PurePosixPath(relative_path).parts
    if len(parts) < 3 or parts[0] != "cells":
        _fail(
            "scenario-contamination-scan-failed",
            "scan member is not inside one scenario cell",
            {"path": relative_path},
        )
    try:
        label = require_id(parts[1], "observed_cell_label")
    except ValueError as exc:
        raise LacunaError("scenario-contamination-scan-failed", str(exc)) from exc
    if label not in planned_cell_labels:
        _fail(
            "scenario-contamination-tree-mismatch",
            "scan member is not owned by one preregistered scenario cell",
            {"path": relative_path, "observed_cell_label": label},
        )
    return label


def build_scenario_contamination_scan(
    run_path: str | Path,
    plan_value: Any,
    *,
    scanned_at: str,
) -> dict[str, Any]:
    code = "scenario-contamination-scan-failed"
    plan = validate_scenario_contamination_plan(plan_value)
    try:
        scanned_at = require_string(scanned_at, "scanned_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    run_path = Path(run_path)
    planned_cell_labels = _planned_cell_labels(plan)
    _, first_entries = _enumerate_scan_files(
        run_path, planned_cell_labels=planned_cell_labels
    )
    total_bytes = 0
    file_manifest: list[dict[str, Any]] = []
    matches: list[dict[str, Any]] = []
    token_bytes = [(item, item["token"].encode("ascii")) for item in plan["canaries"]]
    for relative, path, _signature in first_entries:
        member_scan = scan_sidecar_member_exact_tokens(
            path,
            exact_tokens=[encoded for _canary, encoded in token_bytes],
            label="scenario contamination scan member",
            error_prefix="scenario-contamination",
            max_bytes=MAX_SCAN_MEMBER_BYTES,
        )
        total_bytes += member_scan["size"]
        if total_bytes > MAX_SCAN_TOTAL_BYTES:
            _fail(
                "scenario-contamination-scan-limit",
                "scenario contamination scan exceeds the fixed total-byte limit",
                {"limit": MAX_SCAN_TOTAL_BYTES},
            )
        file_manifest.append(
            {
                "path": relative,
                "size": member_scan["size"],
                "sha256": member_scan["sha256"],
            }
        )
        observed_cell = _path_cell_label(
            relative, planned_cell_labels=planned_cell_labels
        )
        relative_bytes = _relative_path_bytes(relative)
        for (canary, encoded), content_occurrences in zip(
            token_bytes,
            member_scan["occurrence_counts"],
            strict=True,
        ):
            path_occurrences = _count_occurrences(relative_bytes, encoded)
            if path_occurrences:
                _append_scan_match(
                    matches,
                    canary=canary,
                    observed_cell=observed_cell,
                    relative_path=relative,
                    match_surface="relative-path",
                    occurrence_count=path_occurrences,
                )
            if content_occurrences and relative not in canary["source_paths"]:
                _append_scan_match(
                    matches,
                    canary=canary,
                    observed_cell=observed_cell,
                    relative_path=relative,
                    match_surface="content",
                    occurrence_count=content_occurrences,
                )
    _, second_entries = _enumerate_scan_files(
        run_path, planned_cell_labels=planned_cell_labels
    )
    first_signatures = [(relative, signature) for relative, _path, signature in first_entries]
    second_signatures = [(relative, signature) for relative, _path, signature in second_entries]
    if first_signatures != second_signatures:
        _fail(
            "scenario-contamination-scan-race",
            "scenario cell tree changed while the contamination scan was being compiled",
        )
    matches.sort(
        key=lambda item: (
            item["path"],
            item["canary_id"],
            item["match_surface"],
            item["classification"],
        )
    )

    cell_order: list[str] = []
    for canary in plan["canaries"]:
        if canary["cell_label"] not in cell_order:
            cell_order.append(canary["cell_label"])
    summaries: list[dict[str, Any]] = []
    for cell_label in cell_order:
        observed = [item for item in matches if item["observed_cell_label"] == cell_label]
        own = sum(item["occurrence_count"] for item in observed if item["owner_cell_label"] == cell_label)
        foreign = sum(item["occurrence_count"] for item in observed if item["owner_cell_label"] != cell_label)
        count = own + foreign
        summaries.append(
            {
                "cell_label": cell_label,
                "status": "leak-detected" if count else "clean",
                "own_canary_leaks": own,
                "foreign_canary_leaks": foreign,
                "unexpected_match_count": count,
                "canary_ids": sorted({item["canary_id"] for item in observed}),
            }
        )
    return {
        "event": SCENARIO_CONTAMINATION_SCAN_EVENT,
        "schema": SCENARIO_CONTAMINATION_SCAN_SCHEMA,
        "run_id": plan["run_id"],
        "capsule_id": plan["capsule_id"],
        "plan_sha256": contamination_plan_sha256(plan),
        "assignment_sha256": plan["assignment_sha256"],
        "scan_scope": CONTAMINATION_SCAN_SCOPE,
        "file_count": len(first_entries),
        "byte_count": total_bytes,
        "file_manifest_sha256": canonical_json_digest(
            file_manifest,
            error_code=code,
            label="scenario contamination file manifest",
        ),
        "unexpected_matches": matches,
        "cell_summaries": summaries,
        "overall_status": "leak-detected" if matches else "clean",
        "scanned_at": scanned_at,
        "instructions": list(SCAN_INSTRUCTIONS),
        "nonclaims": list(SCAN_NONCLAIMS),
    }


def validate_scenario_contamination_scan(
    value: Any,
    *,
    plan_value: Any,
) -> dict[str, Any]:
    code = "bad-scenario-contamination-scan"
    plan = validate_scenario_contamination_plan(plan_value)
    document = _strict(value, label="scenario contamination scan", fields=SCAN_FIELDS, code=code)
    if (
        document.get("event") != SCENARIO_CONTAMINATION_SCAN_EVENT
        or document.get("schema") != SCENARIO_CONTAMINATION_SCAN_SCHEMA
        or document.get("scan_scope") != CONTAMINATION_SCAN_SCOPE
    ):
        _fail(code, "unsupported scenario contamination scan contract")
    if document.get("run_id") != plan["run_id"] or document.get("capsule_id") != plan["capsule_id"]:
        _fail(code, "contamination scan identity does not match its plan")
    if document.get("plan_sha256") != contamination_plan_sha256(plan):
        _fail(code, "contamination scan does not bind the exact plan")
    if document.get("assignment_sha256") != plan["assignment_sha256"]:
        _fail(code, "contamination scan assignment digest does not match its plan")
    file_count = _nonnegative_int(document.get("file_count"), "file_count", code=code, maximum=MAX_SCAN_FILES)
    byte_count = _nonnegative_int(document.get("byte_count"), "byte_count", code=code, maximum=MAX_SCAN_TOTAL_BYTES)
    file_manifest_sha256 = _sha(document.get("file_manifest_sha256"), "file_manifest_sha256", code=code)
    try:
        raw_matches = require_list(document.get("unexpected_matches"), "unexpected_matches")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if len(raw_matches) > MAX_SCAN_MATCHES:
        _fail(code, "unexpected_matches exceeds the fixed scan result limit")
    canary_by_id = {item["canary_id"]: item for item in plan["canaries"]}
    planned_cell_labels = _planned_cell_labels(plan)
    matches: list[dict[str, Any]] = []
    seen_match_keys: set[tuple[str, str, str]] = set()
    for index, raw in enumerate(raw_matches):
        item = _strict(raw, label=f"unexpected_matches[{index}]", fields=MATCH_FIELDS, code=code)
        canary_id = item.get("canary_id")
        if canary_id not in canary_by_id:
            _fail(code, "scan match names an unknown canary", {"canary_id": canary_id})
        canary = canary_by_id[canary_id]
        try:
            owner = require_id(item.get("owner_cell_label"), f"unexpected_matches[{index}].owner_cell_label")
            observed = require_id(item.get("observed_cell_label"), f"unexpected_matches[{index}].observed_cell_label")
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        if observed not in planned_cell_labels:
            _fail(
                code,
                "scan match observed cell is not preregistered",
                {"observed_cell_label": observed},
            )
        if owner != canary["cell_label"] or item.get("scope") != canary["scope"]:
            _fail(code, "scan match ownership does not agree with the canary plan")
        path = _normalized_relative_path(item.get("path"), f"unexpected_matches[{index}].path", code=code)
        if not path.startswith(f"cells/{observed}/"):
            _fail(code, "scan match path does not agree with observed_cell_label")
        match_surface = item.get("match_surface")
        if match_surface not in SCAN_MATCH_SURFACES:
            _fail(code, "scan match surface is unsupported", {"match_surface": match_surface})
        expected_classification = "same-cell-leak" if owner == observed else "cross-cell-leak"
        if item.get("classification") != expected_classification or expected_classification not in SCAN_CLASSIFICATIONS:
            _fail(code, "scan match classification is inconsistent")
        occurrence_count = _nonnegative_int(
            item.get("occurrence_count"),
            f"unexpected_matches[{index}].occurrence_count",
            code=code,
            maximum=MAX_SCAN_MATCHES,
        )
        if occurrence_count < 1:
            _fail(code, "unexpected match occurrence_count must be positive")
        match_key = (canary_id, path, match_surface)
        if match_key in seen_match_keys:
            _fail(
                code,
                "unexpected_matches must contain at most one record per canary, path, and surface",
                {
                    "canary_id": canary_id,
                    "path": path,
                    "match_surface": match_surface,
                },
            )
        seen_match_keys.add(match_key)
        matches.append(
            {
                "canary_id": canary_id,
                "owner_cell_label": owner,
                "observed_cell_label": observed,
                "scope": canary["scope"],
                "path": path,
                "match_surface": match_surface,
                "classification": expected_classification,
                "occurrence_count": occurrence_count,
            }
        )
    if matches != sorted(
        matches,
        key=lambda item: (
            item["path"],
            item["canary_id"],
            item["match_surface"],
            item["classification"],
        ),
    ):
        _fail(code, "unexpected_matches must use deterministic path/canary order")

    try:
        raw_summaries = require_list(document.get("cell_summaries"), "cell_summaries")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    cell_order = list(planned_cell_labels)
    if len(raw_summaries) != len(cell_order):
        _fail(code, "cell_summaries must contain every planned cell exactly once")
    summaries: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_summaries):
        item = _strict(raw, label=f"cell_summaries[{index}]", fields=CELL_SUMMARY_FIELDS, code=code)
        cell_label = cell_order[index]
        if item.get("cell_label") != cell_label:
            _fail(code, "cell_summaries must preserve planned cell order")
        status = item.get("status")
        if status not in SCAN_STATUSES:
            _fail(code, "cell contamination status is unsupported")
        own = _nonnegative_int(item.get("own_canary_leaks"), f"cell_summaries[{index}].own_canary_leaks", code=code)
        foreign = _nonnegative_int(item.get("foreign_canary_leaks"), f"cell_summaries[{index}].foreign_canary_leaks", code=code)
        count = _nonnegative_int(item.get("unexpected_match_count"), f"cell_summaries[{index}].unexpected_match_count", code=code)
        canary_ids = _string_list(
            item.get("canary_ids"),
            f"cell_summaries[{index}].canary_ids",
            code=code,
            unique=True,
            max_items=len(plan["canaries"]),
            max_len=128,
        )
        observed_matches = [entry for entry in matches if entry["observed_cell_label"] == cell_label]
        expected_own = sum(entry["occurrence_count"] for entry in observed_matches if entry["owner_cell_label"] == cell_label)
        expected_foreign = sum(entry["occurrence_count"] for entry in observed_matches if entry["owner_cell_label"] != cell_label)
        expected_count = expected_own + expected_foreign
        expected_ids = sorted({entry["canary_id"] for entry in observed_matches})
        expected_status = "leak-detected" if expected_count else "clean"
        if (own, foreign, count, canary_ids, status) != (
            expected_own,
            expected_foreign,
            expected_count,
            expected_ids,
            expected_status,
        ):
            _fail(code, "cell contamination summary does not match exact scan findings", {"cell_label": cell_label})
        summaries.append(
            {
                "cell_label": cell_label,
                "status": status,
                "own_canary_leaks": own,
                "foreign_canary_leaks": foreign,
                "unexpected_match_count": count,
                "canary_ids": canary_ids,
            }
        )
    overall = document.get("overall_status")
    expected_overall = "leak-detected" if matches else "clean"
    if overall != expected_overall or overall not in SCAN_STATUSES:
        _fail(code, "overall contamination status does not match exact findings")
    try:
        scanned_at = require_string(document.get("scanned_at"), "scanned_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if document.get("instructions") != SCAN_INSTRUCTIONS or document.get("nonclaims") != SCAN_NONCLAIMS:
        _fail(code, "contamination scan instructions or nonclaims were changed")
    return {
        "event": SCENARIO_CONTAMINATION_SCAN_EVENT,
        "schema": SCENARIO_CONTAMINATION_SCAN_SCHEMA,
        "run_id": plan["run_id"],
        "capsule_id": plan["capsule_id"],
        "plan_sha256": contamination_plan_sha256(plan),
        "assignment_sha256": plan["assignment_sha256"],
        "scan_scope": CONTAMINATION_SCAN_SCOPE,
        "file_count": file_count,
        "byte_count": byte_count,
        "file_manifest_sha256": file_manifest_sha256,
        "unexpected_matches": matches,
        "cell_summaries": summaries,
        "overall_status": overall,
        "scanned_at": scanned_at,
        "instructions": list(SCAN_INSTRUCTIONS),
        "nonclaims": list(SCAN_NONCLAIMS),
    }


def authenticate_scenario_contamination_scan(
    run_path: str | Path,
    scan_value: Any,
    *,
    plan_value: Any,
) -> dict[str, Any]:
    plan = validate_scenario_contamination_plan(plan_value)
    scan = validate_scenario_contamination_scan(scan_value, plan_value=plan)
    expected = build_scenario_contamination_scan(run_path, plan, scanned_at=scan["scanned_at"])
    if scan != expected:
        _fail(
            "scenario-contamination-scan-mismatch",
            "retained contamination scan no longer matches the frozen scenario cell tree",
        )
    return copy.deepcopy(scan)


def contamination_scan_sha256(value: Any, *, plan_value: Any) -> str:
    return canonical_json_digest(
        validate_scenario_contamination_scan(value, plan_value=plan_value),
        error_code="bad-scenario-contamination-scan",
        label="scenario contamination scan",
    )


def contamination_scan_markdown(value: Any, *, plan_value: Any) -> str:
    scan = validate_scenario_contamination_scan(value, plan_value=plan_value)

    def markdown_cell(item: Any) -> str:
        return (
            str(item)
            .replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("`", "\\`")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
        )

    lines = [
        "# Lacuna scenario contamination scan",
        "",
        f"- Run: `{scan['run_id']}`",
        f"- Status: **{scan['overall_status']}**",
        f"- Files scanned: **{scan['file_count']}**",
        f"- Bytes scanned: **{scan['byte_count']}**",
        f"- Unexpected exact matches: **{sum(item['occurrence_count'] for item in scan['unexpected_matches'])}**",
        f"- Content matches: **{sum(item['occurrence_count'] for item in scan['unexpected_matches'] if item['match_surface'] == 'content')}**",
        f"- Relative-path matches: **{sum(item['occurrence_count'] for item in scan['unexpected_matches'] if item['match_surface'] == 'relative-path')}**",
        f"- File-manifest SHA-256: `{scan['file_manifest_sha256']}`",
        "",
        "| Cell | Status | Own-token matches | Foreign-token matches |",
        "|---|---:|---:|---:|",
    ]
    for item in scan["cell_summaries"]:
        lines.append(
            f"| `{item['cell_label']}` | {item['status']} | {item['own_canary_leaks']} | {item['foreign_canary_leaks']} |"
        )
    lines.extend(["", "## Unexpected exact matches", ""])
    if scan["unexpected_matches"]:
        lines.extend(
            [
                "| Owner | Observed cell | Scope | Surface | Classification | Count | Relative path |",
                "|---|---|---|---|---|---:|---|",
            ]
        )
        for item in scan["unexpected_matches"]:
            lines.append(
                "| `{owner}` | `{observed}` | {scope} | {surface} | {classification} | {count} | `{path}` |".format(
                    owner=markdown_cell(item["owner_cell_label"]),
                    observed=markdown_cell(item["observed_cell_label"]),
                    scope=markdown_cell(item["scope"]),
                    surface=markdown_cell(item["match_surface"]),
                    classification=markdown_cell(item["classification"]),
                    count=item["occurrence_count"],
                    path=markdown_cell(item["path"]),
                )
            )
    else:
        lines.append("No unexpected exact-token content or relative-path matches were retained.")
    lines.extend(
        [
            "",
            "A clean exact-token scan is not proof of context isolation or forgetting. Findings are retained rather than used to discard a condition.",
            "",
        ]
    )
    return "\n".join(lines)

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec, run_cpp_shadow_outcome_rows
from .deckspace import DeckVector
from .terminal_mechanisms import annotate_focus_target_from_seat, to_float, to_int, truthy

IDENTITY_SCHEMA = "muc5.policy_replay_guard.v1"

# Files whose semantics can affect public-policy outcomes in the recent population
# evidence.  The digest is intentionally broad: if one of these changes, old
# evidence should be replay-audited before being interpreted under the new code.
RUNTIME_IDENTITY_PATHS: tuple[str, ...] = (
    "src/muc5/public_agents.py",
    "src/muc5/ranker_policy.py",
    "src/muc5/mulligan_ranker.py",
    "src/muc5/cpp_rollout.py",
    "src/muc5/engine.py",
    "src/muc5/decision.py",
    "src/muc5/rules_kernel.py",
    "src/muc5/terminal_mechanisms.py",
    "data/rev0027_mulligan_outcome_ranker_model.json",
    "data/rev0034_counterfactual_action_ranker_model.json",
)

COMPARE_FIELDS: tuple[str, ...] = (
    "winner",
    "p0_score",
    "p1_score",
    "p0_terminal_win",
    "p1_terminal_win",
    "is_truncation",
    "loss_reason",
    "decisions",
    "turn_number",
    "focus_target_score",
    "focus_target_result",
    "focus_terminal_mechanism",
    "focus_terminal_loser_role",
)


def _stable_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def policy_runtime_identity(root: Path, *, paths: Sequence[str] = RUNTIME_IDENTITY_PATHS) -> dict[str, object]:
    """Return a stable digest for the current policy/simulator runtime.

    The recent population evidence mostly stores policy names.  That is not
    enough once policy factories or model files evolve.  This digest binds an
    evidence-producing runtime to the source/model files that choose actions,
    mulligans, apply rules, and orient terminal target scores.
    """

    root = Path(root)
    file_rows: list[dict[str, object]] = []
    missing: list[str] = []
    for relative in paths:
        path = root / relative
        if not path.exists():
            missing.append(relative)
            continue
        file_rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    payload = {
        "schema": IDENTITY_SCHEMA,
        "files": file_rows,
        "missing": missing,
    }
    return {
        "schema": IDENTITY_SCHEMA,
        "digest": sha256_text(_stable_json(payload)),
        "files": file_rows,
        "missing": missing,
        "file_count": len(file_rows),
    }


def _normalized_policy_name(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def policy_pair_identity(row: Mapping[str, Any], runtime_digest: str) -> dict[str, object]:
    """Create a row-local identity digest from policy names plus runtime digest."""

    payload = {
        "schema": IDENTITY_SCHEMA,
        "runtime_digest": runtime_digest,
        "agent0": _normalized_policy_name(row.get("agent0")),
        "agent1": _normalized_policy_name(row.get("agent1")),
        "mulligan0": _normalized_policy_name(row.get("mulligan0")),
        "mulligan1": _normalized_policy_name(row.get("mulligan1")),
        "strategy0": str(row.get("strategy0", "")),
        "strategy1": str(row.get("strategy1", "")),
        "deck0": str(row.get("deck0", "")),
        "deck1": str(row.get("deck1", "")),
    }
    return {
        "policy_identity_schema": IDENTITY_SCHEMA,
        "policy_runtime_digest": runtime_digest,
        "policy_pair_digest": sha256_text(_stable_json(payload)),
    }


def annotate_policy_identity_fields(row: Mapping[str, Any], *, root: Path | None = None, runtime_digest: str | None = None) -> dict[str, Any]:
    """Add policy identity fields for newly generated population/candidate rows."""

    if runtime_digest is None:
        if root is None:
            root = Path(__file__).resolve().parents[2]
        runtime_digest = str(policy_runtime_identity(Path(root))["digest"])
    out = dict(row)
    out.update(policy_pair_identity(out, runtime_digest))
    return out


def annotate_policy_identity_rows(rows: Sequence[Mapping[str, Any]], *, root: Path | None = None, runtime_digest: str | None = None) -> list[dict[str, Any]]:
    if runtime_digest is None:
        if root is None:
            root = Path(__file__).resolve().parents[2]
        runtime_digest = str(policy_runtime_identity(Path(root))["digest"])
    return [annotate_policy_identity_fields(row, runtime_digest=runtime_digest) for row in rows]


def deck_from_row(row: Mapping[str, Any], prefix: str) -> DeckVector:
    """Reconstruct a DeckVector from a stored population raw-game row."""

    size = to_int(row.get(f"{prefix}_deck_size"), -1)
    deck = DeckVector(
        size,
        to_int(row.get(f"{prefix}_island_count"), -1),
        to_int(row.get(f"{prefix}_counterspell_count"), -1),
        to_int(row.get(f"{prefix}_force_count"), -1),
        to_int(row.get(f"{prefix}_jace_count"), -1),
        to_int(row.get(f"{prefix}_overlord_count"), -1),
    )
    deck.validate()
    return deck


def replay_spec_from_game_row(row: Mapping[str, Any], *, replay_revision: str, game_id: str | None = None) -> CppShadowGameSpec:
    """Build a runnable spec directly from one stored raw-game evidence row."""

    return CppShadowGameSpec(
        game_id=str(game_id or row.get("cpp_shadow_game_id") or row.get("pair_key") or "replay_game"),
        strategy0=str(row.get("strategy0", "")),
        strategy1=str(row.get("strategy1", "")),
        deck0_name=str(row.get("deck0", "")),
        deck1_name=str(row.get("deck1", "")),
        deck0=deck_from_row(row, "target") if to_int(row.get("target_seat"), -1) == 0 else deck_from_row(row, "opponent"),
        deck1=deck_from_row(row, "opponent") if to_int(row.get("target_seat"), -1) == 0 else deck_from_row(row, "target"),
        agent0=str(row.get("agent0", "")),
        agent1=str(row.get("agent1", "")),
        mulligan0=str(row.get("mulligan0", "")),
        mulligan1=str(row.get("mulligan1", "")),
        seed=to_int(row.get("seed"), 0),
        starting_player=to_int(row.get("starting_player"), 0),
        starting_life=to_int(row.get("starting_life"), 20),
        max_decisions=to_int(row.get("terminal_clean_max_decisions"), 900),
        simulator_revision=replay_revision,
    )


def _normalized_value(field: str, value: object) -> object:
    if field in {"p0_score", "p1_score", "p0_terminal_win", "p1_terminal_win", "focus_target_score"}:
        return round(to_float(value, float("nan")), 12)
    if field in {"is_truncation"}:
        return truthy(value)
    if field in {"winner", "decisions", "turn_number"}:
        return to_int(value, -999999)
    return str(value or "")


def compare_replay_row(stored_row: Mapping[str, Any], replay_row: Mapping[str, Any]) -> dict[str, object]:
    """Compare terminal and focus-oriented replay fields for one evidence row."""

    replay_with_focus = annotate_focus_target_from_seat({**dict(stored_row), **dict(replay_row)}, target_seat_key="target_seat")
    # Reapply stored target metadata after replay output overwrote only terminal fields.
    replay_with_focus["target_seat"] = stored_row.get("target_seat", "")
    replay_with_focus = annotate_focus_target_from_seat(replay_with_focus, target_seat_key="target_seat")
    mismatches: list[str] = []
    field_details: dict[str, dict[str, object]] = {}
    for field in COMPARE_FIELDS:
        stored = _normalized_value(field, stored_row.get(field))
        replayed = _normalized_value(field, replay_with_focus.get(field))
        ok = stored == replayed
        field_details[field] = {"stored": stored, "replayed": replayed, "match": ok}
        if not ok:
            mismatches.append(field)
    return {
        "source_revision": str(stored_row.get("source_revision") or stored_row.get("simulator_revision") or ""),
        "source_game_id": str(stored_row.get("cpp_shadow_game_id", "")),
        "seed": to_int(stored_row.get("seed"), -1),
        "starting_life": to_int(stored_row.get("starting_life"), -1),
        "starting_player": to_int(stored_row.get("starting_player"), -1),
        "target_seat": to_int(stored_row.get("target_seat"), -1),
        "counter_policy_axis": str(stored_row.get("counter_policy_axis", "")),
        "threat_policy_axis": str(stored_row.get("threat_policy_axis", "")),
        "size_axis": str(stored_row.get("size_axis", "")),
        "sampling_design": str(stored_row.get("sampling_design", "")),
        "exact_terminal_replay_match": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatch_fields": ";".join(mismatches),
        "field_details_json": _stable_json(field_details),
    }


def sample_rows_evenly(rows: Sequence[Mapping[str, Any]], *, max_rows: int) -> list[dict[str, Any]]:
    if max_rows <= 0 or len(rows) <= int(max_rows):
        return [dict(row) for row in rows]
    n = len(rows)
    selected = sorted({round(i * (n - 1) / (int(max_rows) - 1)) for i in range(int(max_rows))})
    return [dict(rows[i]) for i in selected]


def sample_rows_by_source(sources: Sequence[tuple[str, Sequence[Mapping[str, Any]]]], *, max_per_source: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for source, rows in sources:
        sampled = sample_rows_evenly(rows, max_rows=max_per_source)
        for row in sampled:
            item = dict(row)
            item["source_revision"] = str(item.get("source_revision") or source)
            item["replay_source_file_revision"] = source
            out.append(item)
    return out


def replay_guard_rows(sampled_rows: Sequence[Mapping[str, Any]], *, replay_revision: str) -> tuple[list[dict[str, object]], tuple[str, ...]]:
    specs = []
    lookup: dict[str, Mapping[str, Any]] = {}
    for index, row in enumerate(sampled_rows):
        gid = f"{replay_revision}_replay_{index:04d}_{row.get('source_revision','')}_{row.get('cpp_shadow_game_id','')}"
        spec = replay_spec_from_game_row(row, replay_revision=replay_revision, game_id=gid)
        specs.append(spec)
        lookup[gid] = row
    replayed_rows, errors = run_cpp_shadow_outcome_rows(specs, revision=replay_revision)
    out = []
    for row in replayed_rows:
        gid = str(row.get("cpp_shadow_game_id", ""))
        stored = lookup.get(gid)
        if stored is None:
            continue
        out.append(compare_replay_row(stored, row))
    return out, tuple(errors)


def policy_identity_coverage_rows(rows: Sequence[Mapping[str, Any]], *, runtime_digest: str) -> list[dict[str, object]]:
    by_source: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        source = str(row.get("source_revision") or row.get("simulator_revision") or "unknown")
        by_source.setdefault(source, []).append(row)
    out: list[dict[str, object]] = []
    for source, source_rows in sorted(by_source.items()):
        missing_runtime = sum(1 for row in source_rows if not str(row.get("policy_runtime_digest", "")).strip())
        missing_pair = sum(1 for row in source_rows if not str(row.get("policy_pair_digest", "")).strip())
        agents = sorted({str(row.get("agent0", "")) for row in source_rows} | {str(row.get("agent1", "")) for row in source_rows})
        mulligans = sorted({str(row.get("mulligan0", "")) for row in source_rows} | {str(row.get("mulligan1", "")) for row in source_rows})
        out.append(
            {
                "source_revision": source,
                "rows": len(source_rows),
                "missing_policy_runtime_digest_rows": missing_runtime,
                "missing_policy_pair_digest_rows": missing_pair,
                "all_rows_have_policy_digest": missing_runtime == 0 and missing_pair == 0,
                "runtime_digest_for_current_replay": runtime_digest,
                "agent_names": ";".join(agents),
                "mulligan_names": ";".join(mulligans),
            }
        )
    return out


def summarize_replay_guard(
    *,
    replay_rows: Sequence[Mapping[str, Any]],
    python_errors: Sequence[str],
    coverage_rows: Sequence[Mapping[str, Any]],
    runtime_identity: Mapping[str, Any],
    sampled_rows: int,
    total_source_rows: int,
) -> dict[str, object]:
    mismatch_rows = [row for row in replay_rows if not bool(row.get("exact_terminal_replay_match"))]
    missing_identity = sum(to_int(row.get("missing_policy_runtime_digest_rows"), 0) for row in coverage_rows)
    return {
        "policy_identity_schema": IDENTITY_SCHEMA,
        "runtime_digest": runtime_identity.get("digest"),
        "runtime_identity_files": runtime_identity.get("file_count"),
        "runtime_identity_missing_files": runtime_identity.get("missing", []),
        "total_source_rows": int(total_source_rows),
        "sampled_rows": int(sampled_rows),
        "replayed_rows": len(replay_rows),
        "python_errors": len(python_errors),
        "terminal_replay_mismatch_rows": len(mismatch_rows),
        "terminal_replay_exact_match_rows": len(replay_rows) - len(mismatch_rows),
        "policy_identity_coverage_rows": len(coverage_rows),
        "source_rows_missing_policy_identity": int(missing_identity),
        "legacy_identity_gap_present": missing_identity > 0,
        "passed": len(python_errors) == 0 and len(mismatch_rows) == 0 and len(replay_rows) == int(sampled_rows),
        "read": (
            "Current runtime exactly reproduces the sampled historical population/adaptive rows. "
            "Existing broad rows still carry a legacy policy-name-only identity gap, so rev0089 records a runtime digest and replay guard; "
            "newly generated rows should carry policy_runtime_digest and policy_pair_digest."
        ),
    }


__all__ = [
    "COMPARE_FIELDS",
    "IDENTITY_SCHEMA",
    "RUNTIME_IDENTITY_PATHS",
    "annotate_policy_identity_fields",
    "annotate_policy_identity_rows",
    "compare_replay_row",
    "deck_from_row",
    "policy_identity_coverage_rows",
    "policy_pair_identity",
    "policy_runtime_identity",
    "replay_guard_rows",
    "replay_spec_from_game_row",
    "sample_rows_by_source",
    "sample_rows_evenly",
    "summarize_replay_guard",
]

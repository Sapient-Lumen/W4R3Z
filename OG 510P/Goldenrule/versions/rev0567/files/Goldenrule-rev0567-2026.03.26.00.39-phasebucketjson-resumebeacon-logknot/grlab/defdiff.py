from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class DefinitionDiff:
    changed: bool
    definitions_hash_changed: bool
    a_definitions_hash: str | None
    b_definitions_hash: str | None
    experiment_changed: bool
    world_changed: bool
    strategies_added: list[str]
    strategies_removed: list[str]
    strategies_changed: list[str]


def _get(d: Any, *path: str) -> Any:
    cur: Any = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _hash_obj(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(b).hexdigest()


def compute_definitions_hash(manifest: dict[str, Any]) -> str | None:
    exp_hash = _get(manifest, "experiment_hash")
    world_hash = _get(manifest, "definitions", "world", "hash")
    strategies = _get(manifest, "definitions", "strategies")
    if not isinstance(exp_hash, str) or not exp_hash:
        return None
    if not isinstance(world_hash, str) or not world_hash:
        return None
    if not isinstance(strategies, list):
        return None

    strat_rows: list[tuple[str, str]] = []
    for r in strategies:
        if not isinstance(r, dict):
            return None
        sid = r.get("id")
        sh = r.get("hash")
        if not isinstance(sid, str) or not sid:
            return None
        if not isinstance(sh, str) or not sh:
            return None
        strat_rows.append((sid, sh))
    strat_rows.sort()

    payload = {
        "experiment_hash": exp_hash,
        "world_hash": world_hash,
        "strategies": [{"id": sid, "hash": sh} for (sid, sh) in strat_rows],
    }
    return _hash_obj(payload)


def diff_manifests(a: dict[str, Any], b: dict[str, Any]) -> DefinitionDiff:
    a_def_hash = _get(a, "definitions_hash")
    if not isinstance(a_def_hash, str) or not a_def_hash:
        a_def_hash = compute_definitions_hash(a)
    b_def_hash = _get(b, "definitions_hash")
    if not isinstance(b_def_hash, str) or not b_def_hash:
        b_def_hash = compute_definitions_hash(b)

    definitions_hash_changed = (
        (a_def_hash is not None or b_def_hash is not None) and a_def_hash != b_def_hash
    )

    a_exp = _get(a, "experiment_hash")
    b_exp = _get(b, "experiment_hash")
    experiment_changed = (a_exp is not None or b_exp is not None) and a_exp != b_exp

    a_world = _get(a, "definitions", "world", "hash")
    b_world = _get(b, "definitions", "world", "hash")
    world_changed = (a_world is not None or b_world is not None) and a_world != b_world

    def _strategy_map(m: dict[str, Any]) -> dict[str, str]:
        out: dict[str, str] = {}
        rows = _get(m, "definitions", "strategies")
        if not isinstance(rows, list):
            return out
        for r in rows:
            if not isinstance(r, dict):
                continue
            sid = r.get("id")
            sh = r.get("hash")
            if isinstance(sid, str) and sid and isinstance(sh, str) and sh:
                out[sid] = sh
        return out

    a_strats = _strategy_map(a)
    b_strats = _strategy_map(b)
    a_ids = set(a_strats.keys())
    b_ids = set(b_strats.keys())

    strategies_added = sorted(b_ids - a_ids)
    strategies_removed = sorted(a_ids - b_ids)
    strategies_changed = sorted([sid for sid in sorted(a_ids & b_ids) if a_strats[sid] != b_strats[sid]])

    changed = (
        definitions_hash_changed
        or experiment_changed
        or world_changed
        or bool(strategies_added)
        or bool(strategies_removed)
        or bool(strategies_changed)
    )
    return DefinitionDiff(
        changed=changed,
        definitions_hash_changed=definitions_hash_changed,
        a_definitions_hash=a_def_hash,
        b_definitions_hash=b_def_hash,
        experiment_changed=experiment_changed,
        world_changed=world_changed,
        strategies_added=strategies_added,
        strategies_removed=strategies_removed,
        strategies_changed=strategies_changed,
    )

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


def dump_json(path: str | Path, obj: object) -> None:
    """Write stable JSON evidence with parent creation and trailing newline."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rectangular_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Return rows with a common sorted header for CSV emission."""

    material = [dict(row) for row in rows]
    fields = sorted({key for row in material for key in row})
    return [{key: row.get(key, "") for key in fields} for row in material]


def flatten_score_rows(rows: Sequence[Mapping[str, object]], *, stage: str) -> list[dict[str, object]]:
    """Flatten nested response-estimate rows into audit-friendly CSV rows."""

    out: list[dict[str, object]] = []
    for row in rows:
        flat = {key: value for key, value in row.items() if key not in {"opponent_scores", "deck", "mixture_support"}}
        flat["stage"] = stage
        flat["opponent_scores_json"] = json.dumps(row.get("opponent_scores", {}), sort_keys=True)
        flat["deck_json"] = json.dumps(row.get("deck", {}), sort_keys=True)
        flat["mixture_support_json"] = json.dumps(row.get("mixture_support", {}), sort_keys=True)
        out.append(flat)
    return out


def stage_seed_overlaps(rows: Sequence[Mapping[str, object]]) -> dict[str, int]:
    """Count seed reuse across named stages.

    Seed separation is one of the cheapest ways a response-oracle screen can
    accidentally overstate itself.  Keep this helper shared so every new oracle
    reports the same disjointness evidence.
    """

    seeds_by_stage: dict[str, set[int]] = {}
    for row in rows:
        seeds_by_stage.setdefault(str(row["stage"]), set()).add(int(row["seed"]))
    stages = sorted(seeds_by_stage)
    return {
        f"{left}|{right}": len(seeds_by_stage[left] & seeds_by_stage[right])
        for i, left in enumerate(stages)
        for right in stages[i + 1 :]
    }


def stage_counts(rows: Sequence[Mapping[str, object]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row["stage"]) for row in rows).items()))

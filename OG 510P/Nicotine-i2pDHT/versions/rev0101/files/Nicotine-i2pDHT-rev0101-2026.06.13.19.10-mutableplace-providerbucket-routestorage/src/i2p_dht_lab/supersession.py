"""Historical surface supersession helpers for cube audit/refactor.

The cube is intentionally append-heavy, so duplicate numeric ADR/doc prefixes and
near-duplicate modules can be historical accidents rather than active ambiguity.
rev0014 adds an explicit supersession map instead of silently renaming old files.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SupersessionEntry:
    old_path: str
    superseded_by: str
    reason: str


@dataclass(frozen=True)
class SupersessionMap:
    entries: tuple[SupersessionEntry, ...]

    @property
    def old_paths(self) -> frozenset[str]:
        return frozenset(entry.old_path for entry in self.entries)

    @property
    def by_old_path(self) -> dict[str, SupersessionEntry]:
        return {entry.old_path: entry for entry in self.entries}

    def covers_any(self, paths: tuple[str, ...] | list[str]) -> bool:
        old = self.old_paths
        return any(path in old for path in paths)


def load_supersession_map(root: str | Path, *, filename: str = "HISTORICAL_SUPERSESSION.json") -> SupersessionMap:
    path = Path(root) / filename
    if not path.exists():
        return SupersessionMap(())
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = tuple(
        SupersessionEntry(str(item["old_path"]), str(item["superseded_by"]), str(item.get("reason", "")))
        for item in payload.get("entries", [])
    )
    return SupersessionMap(entries)

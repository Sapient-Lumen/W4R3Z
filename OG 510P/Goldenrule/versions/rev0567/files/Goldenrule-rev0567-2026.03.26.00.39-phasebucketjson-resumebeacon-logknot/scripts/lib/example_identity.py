#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExampleIdentity:
    example_id: str
    source: str


def _surrogate_example_id(root: Path, path: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel.endswith('.json'):
        rel = rel[:-5]
    return f"example::{rel}"


def extract_example_identity(root: Path, path: Path, obj: object) -> ExampleIdentity | None:
    if not isinstance(obj, dict):
        return None
    sid = str(obj.get('id', '')).strip()
    if sid:
        return ExampleIdentity(example_id=sid, source='explicit')
    return ExampleIdentity(example_id=_surrogate_example_id(root, path), source='surrogate_path')

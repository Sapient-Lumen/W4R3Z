from __future__ import annotations

"""Helpers for reading/writing macro files inside a project.

Motivation
----------
VHK ships a few "codegen"-style commands (recorders, optimizers, scaffolders).
Mature automation ecosystems make it easy to generate scripts directly into a
project folder and keep them discoverable.

This module provides a tiny, testable filesystem layer for that workflow:

- resolve a macro name to a path (prefer project.yaml's explicit mapping)
- write steps into a macro file while preserving other top-level fields
- optionally register the macro in project.yaml
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


Step = dict[str, Any]


@dataclass(frozen=True)
class MacroWriteResult:
    macro_path: Path
    created: bool
    registered: bool
    appended: bool


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    doc = yaml.safe_load(path.read_text())
    if doc is None:
        return {}
    if not isinstance(doc, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return doc


def resolve_macro_path(project_dir: Path, macro_name: str) -> tuple[Path, str]:
    """Return (absolute_path, relative_path_for_manifest).

    If project.yaml contains an explicit `macros:` mapping for macro_name, that
    path is preferred. Otherwise we fall back to `macros/<name>.yaml`.
    """

    project_dir = project_dir.expanduser().resolve()
    manifest = project_dir / "project.yaml"
    rel_path = f"macros/{macro_name}.yaml"
    if manifest.exists():
        try:
            doc = _load_yaml_mapping(manifest)
            macros = doc.get("macros")
            if isinstance(macros, dict):
                v = macros.get(str(macro_name))
                if isinstance(v, str) and v.strip():
                    rel_path = v.strip()
        except Exception:
            # Best-effort: don't block codegen output when the manifest is
            # partially broken; validation/linting can catch this later.
            pass

    abs_path = (project_dir / rel_path).resolve()
    return abs_path, rel_path


def register_macro(project_dir: Path, macro_name: str, macro_rel_path: str) -> bool:
    """Register/overwrite macro_name in project.yaml.

    Returns True when the manifest was modified.
    """

    project_dir = project_dir.expanduser().resolve()
    manifest = project_dir / "project.yaml"
    if not manifest.exists():
        raise FileNotFoundError(f"Missing project.yaml in {project_dir}")
    doc = _load_yaml_mapping(manifest)
    macros = doc.get("macros") or {}
    if not isinstance(macros, dict):
        raise ValueError("project.yaml 'macros' must be a mapping when present")
    before = macros.get(str(macro_name))
    if before == macro_rel_path:
        return False
    macros[str(macro_name)] = str(macro_rel_path)
    doc["macros"] = macros
    manifest.write_text(yaml.safe_dump(doc, sort_keys=False))
    return True


def write_macro_steps(
    project_dir: Path,
    *,
    macro_name: str,
    steps: list[Step],
    register: bool = True,
    append: bool = False,
) -> MacroWriteResult:
    """Write steps into a macro file inside a project.

    Notes
    -----
    - Preserves any existing top-level keys in the macro YAML and only updates
      `steps` (and ensures `name`).
    - If the macro file exists but is not a mapping, it will be replaced.
    """

    macro_path, rel = resolve_macro_path(project_dir, macro_name)
    created = not macro_path.exists()

    payload: dict[str, Any]
    if macro_path.exists():
        try:
            payload = _load_yaml_mapping(macro_path)
        except Exception:
            payload = {}
    else:
        payload = {}

    payload.setdefault("name", str(macro_name))

    if append and isinstance(payload.get("steps"), list):
        existing_steps = payload.get("steps")
        assert isinstance(existing_steps, list)
        payload["steps"] = list(existing_steps) + list(steps)
    else:
        payload["steps"] = list(steps)

    macro_path.parent.mkdir(parents=True, exist_ok=True)
    macro_path.write_text(yaml.safe_dump(payload, sort_keys=False))

    registered = False
    if register:
        registered = register_macro(project_dir, macro_name, rel)

    return MacroWriteResult(
        macro_path=macro_path,
        created=created,
        registered=registered,
        appended=append and not created,
    )

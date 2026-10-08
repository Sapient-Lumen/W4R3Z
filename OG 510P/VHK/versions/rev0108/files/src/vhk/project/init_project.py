from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import json
import yaml

from vhk.project.schema import write_default_schemas


ProjectTemplate = Literal["minimal", "demo", "vision"]


_PNG_1X1_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wwAAgMBAp1RXr8AAAAASUVORK5CYII="
)


@dataclass
class InitResult:
    project_dir: Path
    created_files: list[Path]
    created_dirs: list[Path]


def _ensure_empty_dir(path: Path, *, force: bool) -> None:
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"Project path exists and is not a directory: {path}")
        # Allow empty directories.
        if any(path.iterdir()) and not force:
            raise ValueError(
                f"Project directory is not empty: {path}. Use --force to overwrite files in-place."
            )
    else:
        path.mkdir(parents=True, exist_ok=True)


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _yaml_with_modeline(modeline: str | None, payload: dict) -> str:
    """Serialize YAML with an optional yaml-language-server modeline."""

    body = yaml.safe_dump(payload, sort_keys=False)
    if not modeline:
        return body
    # Modeline must be on the first line.
    return f"# yaml-language-server: $schema={modeline}\n" + body


def _macro_template(name: str, template: ProjectTemplate) -> dict:
    if template == "minimal":
        return {
            "name": name,
            "steps": [
                {"type": "Log", "message": "Hello from VHK."},
                {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
            ],
        }

    if template == "demo":
        return {
            "name": name,
            "steps": [
                {"type": "Notify", "title": "VHK", "message": "Demo macro started"},
                {"type": "Delay", "ms": 250},
                {"type": "TypeText", "text": "Hello, world!", "backend": "native", "delay_ms_per_char": 12},
                {"type": "Key", "keys": "enter"},
                {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
            ],
        }

    # vision
    return {
        "name": name,
        "steps": [
            {
                "type": "WaitForImage",
                "enabled": False,
                "comment": "TODO: capture a needle and enable this wait (avoid fixed sleeps)",
                "needle_path": "assets/TODO.png",
                "timeout_ms": 5000,
            },
            {
                "type": "ClickNeedle",
                "enabled": False,
                "comment": "TODO: replace with your own captured needle",
                "needle_path": "assets/TODO.png",
            },
            {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
        ],
    }


def init_project(
    project_dir: Path,
    *,
    name: str | None = None,
    template: ProjectTemplate = "minimal",
    with_schemas: bool = True,
    with_vscode_settings: bool = True,
    force: bool = False,
) -> InitResult:
    """Create a new VHK project skeleton."""

    project_dir = project_dir.expanduser().resolve()
    _ensure_empty_dir(project_dir, force=force)

    created_files: list[Path] = []
    created_dirs: list[Path] = []

    # Standard folders.
    for rel in [
        Path("macros"),
        Path("assets"),
        Path("assets/needles"),
        Path("assets/baselines"),
        Path("logs"),
    ]:
        p = project_dir / rel
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            created_dirs.append(p)

    # A tiny placeholder PNG that scaffolding/vision templates can reference.
    todo_png = project_dir / "assets" / "TODO.png"
    _write_if_allowed(todo_png, base64.b64decode(_PNG_1X1_B64), force=force)
    created_files.append(todo_png)

    todo_json = project_dir / "assets" / "TODO.json"
    _write_if_allowed(
        todo_json,
        json.dumps(
            {
                "tags": ["todo"],
                "area": [
                    {
                        "type": "match",
                        "xpos": 0,
                        "ypos": 0,
                        "width": 1,
                        "height": 1,
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        force=force,
    )
    created_files.append(todo_json)

    if with_schemas:
        created = write_default_schemas(project_dir, force=force, with_vscode_settings=with_vscode_settings)
        created_files.extend(created)

    # Starter macro.
    macro_name = "main"
    macro_path = project_dir / "macros" / f"{macro_name}.yaml"
    macro_payload = _macro_template(macro_name, template)
    macro_modeline = "../schemas/vhk_macro.schema.json" if with_schemas else None
    _write_if_allowed(macro_path, _yaml_with_modeline(macro_modeline, macro_payload), force=force)
    created_files.append(macro_path)

    project_name = name or project_dir.name
    project_yaml = project_dir / "project.yaml"
    project_payload = {
        "name": project_name,
        "macros": {macro_name: f"macros/{macro_name}.yaml"},
        "regions": {},
        "bindings": [],
        "hotstrings": [],
        "clipboard_watchers": [],
        "window_watchers": [],
    }
    proj_modeline = "schemas/vhk_project.schema.json" if with_schemas else None
    _write_if_allowed(project_yaml, _yaml_with_modeline(proj_modeline, project_payload), force=force)
    created_files.append(project_yaml)

    gitignore = project_dir / ".gitignore"
    _write_if_allowed(
        gitignore,
        """# VHK project artifacts\nlogs/\n__pycache__/\n*.pyc\n.DS_Store\n""",
        force=force,
    )
    created_files.append(gitignore)

    return InitResult(project_dir=project_dir, created_files=created_files, created_dirs=created_dirs)


def add_macro(
    project_dir: Path,
    *,
    macro_name: str,
    template: ProjectTemplate = "minimal",
    register: bool = True,
    force: bool = False,
) -> Path:
    """Create a new macro file under macros/ and optionally register in project.yaml."""

    project_dir = project_dir.expanduser().resolve()
    manifest = project_dir / "project.yaml"
    if not manifest.exists():
        raise FileNotFoundError(f"Missing project.yaml in {project_dir}")

    # Write macro file.
    macros_dir = project_dir / "macros"
    macros_dir.mkdir(parents=True, exist_ok=True)
    macro_path = macros_dir / f"{macro_name}.yaml"
    payload = _macro_template(macro_name, template)
    schema_path = project_dir / "schemas" / "vhk_macro.schema.json"
    modeline = "../schemas/vhk_macro.schema.json" if schema_path.exists() else None
    _write_if_allowed(macro_path, _yaml_with_modeline(modeline, payload), force=force)

    if register:
        doc = yaml.safe_load(manifest.read_text()) or {}
        if not isinstance(doc, dict):
            raise ValueError("project.yaml must be a mapping")
        macros = doc.get("macros") or {}
        if not isinstance(macros, dict):
            raise ValueError("project.yaml 'macros' must be a mapping when present")
        macros[str(macro_name)] = f"macros/{macro_name}.yaml"
        doc["macros"] = macros
        # Force overwrite: we are intentionally updating the manifest.
        _write_if_allowed(manifest, yaml.safe_dump(doc, sort_keys=False), force=True)

    return macro_path

from __future__ import annotations

"""JSON Schema generation for VHK YAML files.

Why this exists
--------------
Many editors (VS Code + Red Hat YAML, Neovim yamlls, etc.) can provide
autocompletion and validation for YAML files when you associate them with a JSON
schema.

VHK uses pydantic models for its project/macro format, so we can generate the
schemas directly.

Important compatibility note
----------------------------
The popular YAML language server (yamlls) is commonly used with JSON Schema Draft
7. We therefore convert pydantic's v2 output (which uses `$defs`) into a Draft 7
compatible structure (`definitions`).
"""

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import TypeAdapter

from vhk.core.models import I3WindowSelector, Macro, Project, Region, Step


SchemaKind = Literal["project", "macro", "step", "selector", "region"]
SchemaDraft = Literal["7", "pydantic"]


def _convert_pydantic_to_draft7(obj: Any) -> Any:
    """Recursively convert pydantic's `$defs` structure to Draft 7 `definitions`.

    This is intentionally minimal: it primarily rewrites `$defs` -> `definitions`
    and updates `$ref` pointers.
    """

    if isinstance(obj, list):
        return [_convert_pydantic_to_draft7(x) for x in obj]

    if not isinstance(obj, dict):
        return obj

    out: dict[str, Any] = {}
    for k, v in obj.items():
        nk = "definitions" if k == "$defs" else k
        out[nk] = _convert_pydantic_to_draft7(v)

    ref = out.get("$ref")
    if isinstance(ref, str) and "#/$defs/" in ref:
        out["$ref"] = ref.replace("#/$defs/", "#/definitions/")

    return out


def generate_schema(kind: SchemaKind, *, draft: SchemaDraft = "7") -> dict[str, Any]:
    """Generate a JSON schema for a VHK file kind."""

    if kind == "project":
        schema = Project.model_json_schema()
    elif kind == "macro":
        schema = Macro.model_json_schema()
    elif kind == "step":
        schema = TypeAdapter(Step).json_schema()
    elif kind == "selector":
        schema = I3WindowSelector.model_json_schema()
    elif kind == "region":
        schema = Region.model_json_schema()
    else:
        raise ValueError(f"Unknown schema kind: {kind}")

    if draft == "pydantic":
        return schema

    converted = _convert_pydantic_to_draft7(schema)
    if isinstance(converted, dict):
        converted.setdefault("$schema", "http://json-schema.org/draft-07/schema#")
    return converted


def write_default_schemas(
    project_dir: Path,
    *,
    force: bool = False,
    with_vscode_settings: bool = True,
) -> list[Path]:
    """Write schema files into `<project>/schemas/` and optional VS Code settings."""

    project_dir = project_dir.expanduser().resolve()
    out_dir = project_dir / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []

    def write(p: Path, payload: dict[str, Any]) -> None:
        if p.exists() and not force:
            return
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        created.append(p)

    write(out_dir / "vhk_project.schema.json", generate_schema("project"))
    write(out_dir / "vhk_macro.schema.json", generate_schema("macro"))

    if with_vscode_settings:
        vs_dir = project_dir / ".vscode"
        vs_dir.mkdir(parents=True, exist_ok=True)
        settings = vs_dir / "settings.json"
        if not settings.exists() or force:
            # Paths are workspace-relative, matching yaml-language-server guidance.
            settings_payload = {
                "yaml.schemas": {
                    "schemas/vhk_project.schema.json": ["/project.yaml"],
                    "schemas/vhk_macro.schema.json": ["/macros/*.yaml"],
                }
            }
            settings.write_text(json.dumps(settings_payload, ensure_ascii=False, indent=2) + "\n")
            created.append(settings)

    return created

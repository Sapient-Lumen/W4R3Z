from __future__ import annotations

"""micromax_editor.plugin_meta

A tiny, explicit `plugin.json` schema + validator.

Why explicit?
  - keep the plugin manager dependency-free (no jsonschema package)
  - make error messages predictable (and easy for humans/LLMs to act on)
  - allow forward-compatible extra keys (we preserve unknown fields)

This is intentionally *not* a full package manager. It's a metadata contract.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import re

from micromax.vm import MicromaxError


_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class PluginMeta:
    name: str
    version: str | None
    description: str | None
    entry: str | None
    requires: list[str]
    raw: dict[str, Any]


def _expect_type(obj: dict[str, Any], key: str, t: type, *, allow_none: bool = False) -> Any:
    if key not in obj:
        return None
    v = obj[key]
    if v is None and allow_none:
        return None
    if not isinstance(v, t):
        raise MicromaxError(f"plugin.json: {key} must be {t.__name__}")
    return v


def _expect_list_of_str(obj: dict[str, Any], key: str) -> list[str]:
    if key not in obj:
        return []
    v = obj[key]
    if not isinstance(v, list) or any(not isinstance(x, str) for x in v):
        raise MicromaxError(f"plugin.json: {key} must be a list of strings")
    out = [str(x).strip() for x in v if str(x).strip() != ""]
    # de-dupe while preserving order
    seen: set[str] = set()
    dedup: list[str] = []
    for x in out:
        if x in seen:
            continue
        seen.add(x)
        dedup.append(x)
    return dedup


def load_plugin_meta(plugin_name: str, root: Path) -> PluginMeta:
    """Load and validate plugin.json for a plugin directory.

    The file is optional: absence returns an empty meta record.
    """
    meta_path = root / "plugin.json"
    if not meta_path.exists():
        return PluginMeta(name=str(plugin_name), version=None, description=None, entry=None, requires=[], raw={})

    try:
        obj = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise MicromaxError(f"plugin.json: invalid JSON: {e}")

    if not isinstance(obj, dict):
        raise MicromaxError("plugin.json: must be a JSON object")

    # name (optional): if present, must match directory name.
    name = _expect_type(obj, "name", str, allow_none=True) or str(plugin_name)
    if str(name) != str(plugin_name):
        raise MicromaxError(f"plugin.json: name mismatch: {name!r} (directory is {plugin_name!r})")

    version = _expect_type(obj, "version", str, allow_none=True)
    if version is not None and not _SEMVER_RE.match(str(version).strip()):
        raise MicromaxError(f"plugin.json: version must look like semver (e.g. 0.1.0), got: {version!r}")

    description = _expect_type(obj, "description", str, allow_none=True)

    # entry (optional): allow init.mx/init.mmx/init.mf default, but entry can override.
    entry = _expect_type(obj, "entry", str, allow_none=True)
    if entry is not None:
        ep = Path(str(entry))
        if ep.is_absolute() or ".." in ep.parts:
            raise MicromaxError(f"plugin.json: entry must be a relative path inside the plugin dir, got: {entry!r}")
        if not (root / ep).exists():
            raise MicromaxError(f"plugin.json: entry file not found: {entry!r}")

    # dependencies
    requires = _expect_list_of_str(obj, "requires")
    # Back-compat alias: dependencies
    if not requires:
        requires = _expect_list_of_str(obj, "dependencies")

    return PluginMeta(
        name=str(name),
        version=str(version) if version is not None else None,
        description=str(description) if description is not None else None,
        entry=str(entry) if entry is not None else None,
        requires=requires,
        raw=dict(obj),
    )

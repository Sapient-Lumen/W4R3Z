from __future__ import annotations

from pathlib import Path

import yaml

from vhk.core.models import BusWatcher, ClipboardWatcher, FileWatcher, HotkeyBinding, HotstringBinding, Macro, Project, ProjectSettings, Region, WindowWatcher


def load_project(project_dir: Path) -> Project:
    """Load a VHK project from a folder."""

    project_dir = project_dir.resolve()
    manifest_path = project_dir / "project.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing project.yaml in {project_dir}")

    manifest = yaml.safe_load(manifest_path.read_text()) or {}
    name = manifest.get("name") or project_dir.name

    # Settings + bindings are optional.
    settings = ProjectSettings.model_validate(manifest.get("settings") or {})
    bindings_raw = manifest.get("bindings") or []
    bindings = [HotkeyBinding.model_validate(b) for b in bindings_raw]
    hotstrings_raw = manifest.get("hotstrings") or []
    hotstrings = [HotstringBinding.model_validate(h) for h in hotstrings_raw]
    watchers_raw = manifest.get("clipboard_watchers") or []
    clipboard_watchers = [ClipboardWatcher.model_validate(w) for w in watchers_raw]
    file_watchers_raw = manifest.get("file_watchers") or []
    file_watchers = [FileWatcher.model_validate(w) for w in file_watchers_raw]
    window_watchers_raw = manifest.get("window_watchers") or []
    window_watchers = [WindowWatcher.model_validate(w) for w in window_watchers_raw]

    bus_watchers_raw = manifest.get("bus_watchers") or []
    bus_watchers = [BusWatcher.model_validate(w) for w in bus_watchers_raw]

    regions_raw = manifest.get("regions") or {}
    regions: dict[str, Region] = {}
    if isinstance(regions_raw, dict):
        for k, v in regions_raw.items():
            if k is None:
                continue
            regions[str(k)] = Region.model_validate(v)

    macros_map: dict[str, str] = manifest.get("macros") or {}
    macros: dict[str, Macro] = {}
    for macro_name, rel_path in macros_map.items():
        macro_path = project_dir / rel_path
        data = yaml.safe_load(macro_path.read_text()) or {}
        data.setdefault("name", macro_name)
        macro = Macro.model_validate(data)
        macros[macro_name] = macro

    if not macros:
        # Fallback: load all .yaml files under macros/
        macros_dir = project_dir / "macros"
        if macros_dir.exists():
            for p in sorted(macros_dir.glob("*.yaml")):
                data = yaml.safe_load(p.read_text()) or {}
                macro_name = data.get("name") or p.stem
                data.setdefault("name", macro_name)
                macro = Macro.model_validate(data)
                macros[macro_name] = macro

    if not macros:
        raise ValueError("No macros found. Define macros in project.yaml or add macros/*.yaml")

    return Project(
        name=name,
        macros=macros,
        root_dir=str(project_dir),
        regions=regions,
        bindings=bindings,
        hotstrings=hotstrings,
        clipboard_watchers=clipboard_watchers,
        file_watchers=file_watchers,
        bus_watchers=bus_watchers,
        window_watchers=window_watchers,
        settings=settings,
    )

#!/usr/bin/env python3
"""Emit compact, repeatable structural metrics for Micromax.

This command is deliberately descriptive rather than a policy engine.  It makes
large seams, documentation growth, lifecycle-snapshot pressure, and release
hygiene visible without requiring each cloudtainer pass to rediscover them by
hand.

Usage:
  python tools/mxaudit.py
  python tools/mxaudit.py --json
  python tools/mxaudit.py --check
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import sys
import tomllib
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
LOCK_NAMES = {
    "Pipfile.lock",
    "poetry.lock",
    "pylock.toml",
    "requirements.lock",
    "uv.lock",
}


def _is_ignored(path: Path) -> bool:
    return bool(IGNORED_PARTS.intersection(path.parts)) or path.suffix in {".pyc", ".pyo"}


def _files(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return [path for path in base.rglob("*") if path.is_file() and not _is_ignored(path)]


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _line_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def _tree_stats(rel: str) -> dict[str, int]:
    paths = _files(ROOT / rel)
    return {
        "files": len(paths),
        "bytes": sum(path.stat().st_size for path in paths),
        "lines": sum(_line_count(path) for path in paths if path.suffix in {".py", ".md", ".mx"}),
    }


def _manifest_rows() -> list[str]:
    path = ROOT / "docs" / "installed-help-manifest.txt"
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _pyproject() -> dict[str, Any]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _revision_index() -> dict[str, Any]:
    try:
        data = json.loads((ROOT / "docs" / "revision-index.json").read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _current_rev() -> int | None:
    value = _revision_index().get("current_rev")
    if isinstance(value, int):
        return value
    first = (ROOT / "TODO.md").read_text(encoding="utf-8", errors="replace").splitlines()[:1]
    match = re.search(r"rev\s*(\d+)", first[0], flags=re.IGNORECASE) if first else None
    return int(match.group(1)) if match else None


def _numbered_docs() -> dict[str, Any]:
    root_docs = sorted((ROOT / "docs").glob("*.md"))
    by_prefix: dict[int, list[str]] = defaultdict(list)
    for path in root_docs:
        match = re.match(r"^(\d+)-", path.name)
        if match:
            by_prefix[int(match.group(1))].append(_relative(path))
    duplicates = {
        str(prefix): names
        for prefix, names in sorted(by_prefix.items())
        if len(names) > 1
    }
    return {
        "root_markdown_files": len(root_docs),
        "numbered_root_docs": sum(len(names) for names in by_prefix.values()),
        "numbered_root_docs_ge_100": sum(
            len(names) for prefix, names in by_prefix.items() if prefix >= 100
        ),
        "duplicate_numeric_prefixes": duplicates,
    }


class _DefinitionCollector(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.stack: list[str] = []
        self.rows: list[dict[str, Any]] = []

    def _record(self, node: ast.AST, *, name: str, kind: str) -> None:
        line = int(getattr(node, "lineno", 0) or 0)
        end_line = int(getattr(node, "end_lineno", line) or line)
        self.rows.append(
            {
                "path": _relative(self.path),
                "qualified_name": ".".join([*self.stack, name]),
                "kind": kind,
                "line": line,
                "end_line": end_line,
                "lines": max(0, end_line - line + 1),
            }
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record(node, name=node.name, kind="class")
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record(node, name=node.name, kind="function")
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record(node, name=node.name, kind="async-function")
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()


def _parse_python(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return None


def _python_metrics(*, limit: int) -> dict[str, Any]:
    paths = sorted(
        [
            *_files(ROOT / "src"),
            *_files(ROOT / "tools"),
            *_files(ROOT / "tests"),
        ],
        key=lambda path: _relative(path),
    )
    python_paths = [path for path in paths if path.suffix == ".py"]
    file_rows = [
        {"path": _relative(path), "lines": _line_count(path), "bytes": path.stat().st_size}
        for path in python_paths
    ]
    definitions: list[dict[str, Any]] = []
    parse_failures: list[str] = []
    for path in python_paths:
        tree = _parse_python(path)
        if tree is None:
            parse_failures.append(_relative(path))
            continue
        collector = _DefinitionCollector(path)
        collector.visit(tree)
        definitions.extend(collector.rows)

    file_rows.sort(key=lambda row: (-int(row["lines"]), str(row["path"])))
    definitions.sort(key=lambda row: (-int(row["lines"]), str(row["path"]), int(row["line"])))
    return {
        "python_files": len(python_paths),
        "parse_failures": parse_failures,
        "top_files": file_rows[:limit],
        "top_definitions": definitions[:limit],
    }


def _self_attributes(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    attrs: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            continue
        targets: Iterable[ast.expr]
        if isinstance(node, ast.Assign):
            targets = node.targets
        else:
            targets = [node.target]
        for target in targets:
            for child in ast.walk(target):
                if (
                    isinstance(child, ast.Attribute)
                    and isinstance(child.value, ast.Name)
                    and child.value.id == "self"
                ):
                    attrs.add(child.attr)
    return sorted(attrs)


def _class_node(path: Path, name: str) -> ast.ClassDef | None:
    tree = _parse_python(path)
    if tree is None:
        return None
    return next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name), None)


def _editor_metrics() -> dict[str, Any]:
    path = ROOT / "src" / "micromax_editor" / "editor.py"
    node = _class_node(path, "Editor")
    if node is None:
        return {"path": _relative(path), "found": False}
    methods = [item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
    init = next((item for item in methods if item.name == "__init__"), None)
    attrs = _self_attributes(init) if init is not None else []
    authority_attrs = [name for name in attrs if "authority" in name]
    lifecycle_methods = [
        item.name
        for item in methods
        if item.name.startswith(("remove_", "retag_", "restore_", "snapshot_", "_restore_", "_snapshot_"))
        and any(token in item.name for token in ("group", "plugin", "state", "authority"))
    ]
    line = int(getattr(node, "lineno", 0) or 0)
    end_line = int(getattr(node, "end_lineno", line) or line)
    return {
        "path": _relative(path),
        "found": True,
        "file_lines": _line_count(path),
        "class_lines": max(0, end_line - line + 1),
        "method_count": len(methods),
        "init_state_attributes": len(attrs),
        "init_authority_attributes": authority_attrs,
        "lifecycle_helper_count": len(lifecycle_methods),
        "lifecycle_helpers": sorted(lifecycle_methods),
    }


def _snapshot_metrics() -> dict[str, Any]:
    path = ROOT / "src" / "micromax_editor" / "plugin_runtime.py"
    node = _class_node(path, "RuntimeRegistrationSnapshot")
    if node is None:
        return {"path": _relative(path), "found": False}
    fields = [item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
    return {
        "path": _relative(path),
        "found": True,
        "field_count": len(fields),
        "fields": fields,
    }


def _recent_lifecycle_revisions() -> list[dict[str, Any]]:
    entries = _revision_index().get("entries")
    if not isinstance(entries, list):
        return []
    rows: list[dict[str, Any]] = []
    for entry in entries[:12]:
        if not isinstance(entry, dict):
            continue
        intent = [str(value) for value in (entry.get("intent") or [])]
        tag = str(entry.get("tag") or "")
        if "plugin-lifecycle" not in intent and not any(
            token in tag for token in ("plugin-", "rollback", "unload-cleanup")
        ):
            continue
        rows.append({"rev": entry.get("rev"), "tag": tag})
    return rows


def _typecheck_metrics() -> dict[str, Any]:
    path = ROOT / "scripts" / "typecheck.sh"
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    targets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("mypy "):
            continue
        try:
            targets.extend(shlex.split(stripped)[1:])
        except ValueError:
            continue
    return {
        "script": _relative(path),
        "targets": targets,
        "covers_editor_package": any(
            target == "src/micromax_editor" or target.startswith("src/micromax_editor/")
            for target in targets
        ),
        "skips_when_mypy_missing": "Skipping" in text and "mypy not installed" in text,
    }




def _runtime_group_policy_metrics() -> dict[str, Any]:
    runtime_path = ROOT / "src" / "micromax_editor" / "plugin_runtime.py"
    manager_path = ROOT / "src" / "micromax_editor" / "plugins.py"
    editor_path = ROOT / "src" / "micromax_editor" / "editor.py"
    commands_path = ROOT / "src" / "micromax_editor" / "plugin_commands.py"
    prompt_path = ROOT / "src" / "micromax_editor" / "prompt_suggestions.py"
    bridge_path = ROOT / "src" / "micromax_editor" / "micromax_bridge.py"
    registry_path = ROOT / "src" / "micromax_editor" / "editor_hostcall_registry.py"
    vm_path = ROOT / "src" / "micromax" / "vm.py"
    runtime_text = runtime_path.read_text(encoding="utf-8", errors="replace") if runtime_path.exists() else ""
    manager_text = manager_path.read_text(encoding="utf-8", errors="replace") if manager_path.exists() else ""
    editor_text = editor_path.read_text(encoding="utf-8", errors="replace") if editor_path.exists() else ""
    commands_text = commands_path.read_text(encoding="utf-8", errors="replace") if commands_path.exists() else ""
    prompt_text = prompt_path.read_text(encoding="utf-8", errors="replace") if prompt_path.exists() else ""
    bridge_text = bridge_path.read_text(encoding="utf-8", errors="replace") if bridge_path.exists() else ""
    registry_text = registry_path.read_text(encoding="utf-8", errors="replace") if registry_path.exists() else ""
    vm_text = vm_path.read_text(encoding="utf-8", errors="replace") if vm_path.exists() else ""
    options_text = (ROOT / "src" / "micromax_editor" / "options_default.py").read_text(encoding="utf-8", errors="replace")
    guard_match = re.search(
        r"def _group_operation_or_restore\b(?P<body>.*?)(?:\n    def |\nclass |\Z)",
        manager_text,
        flags=re.DOTALL,
    )
    guard_body = guard_match.group("body") if guard_match else ""
    generation_guard_match = re.search(
        r"def _cleanup_plugin_generation_or_restore\b(?P<body>.*?)(?:\n    def |\nclass |\Z)",
        manager_text,
        flags=re.DOTALL,
    )
    generation_guard_body = generation_guard_match.group("body") if generation_guard_match else ""
    loaded_cleanup_match = re.search(
        r"def _cleanup_loaded_plugin_state_or_restore\b(?P<body>.*?)(?:\n    def |\nclass |\Z)",
        manager_text,
        flags=re.DOTALL,
    )
    loaded_cleanup_body = loaded_cleanup_match.group("body") if loaded_cleanup_match else ""
    runtime_snapshot_match = re.search(
        r"def snapshot_runtime_group_state\b(?P<body>.*?)(?:\ndef restore_runtime_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    runtime_snapshot_body = runtime_snapshot_match.group("body") if runtime_snapshot_match else ""
    runtime_restore_match = re.search(
        r"def restore_runtime_group_state\b(?P<body>.*?)(?:\ndef snapshot_runtime_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    runtime_restore_body = runtime_restore_match.group("body") if runtime_restore_match else ""
    return {
        "operation_error_class_present": "class RuntimeGroupOperationError" in runtime_text,
        "narrow_group_snapshot_present": (
            "class RuntimeGroupStateSnapshot" in runtime_text
            and "def snapshot_runtime_group_state" in runtime_text
            and "def restore_runtime_group_state" in runtime_text
        ),
        "narrow_generation_snapshot_present": (
            "class RuntimeGenerationStateSnapshot" in runtime_text
            and "def snapshot_runtime_generation_state" in runtime_text
            and "def restore_runtime_generation_state" in runtime_text
        ),
        "generation_cleanup_report_present": "def cleanup_plugin_generation_state" in runtime_text,
        "manager_retains_reports": "runtime_group_reports" in manager_text and "runtime_group_failures" in manager_text,
        "manager_exposes_failure_rows": "def runtime_group_failure_rows" in manager_text,
        "editor_exposes_cleanup_failure_rows": "def plugin_cleanup_failure_rows" in editor_text,
        "plugin_cleanup_command_present": "plugin cleanup" in commands_text and "_cleanup_failure_line" in commands_text,
        "plugin_cleanup_hostcall_present": (
            "ed.plugin-cleanup-failure-rows" in registry_text
            and "hc_ed_plugin_cleanup_failure_rows" in bridge_text
        ),
        "plugin_cleanup_completion_present": "cleanup" in prompt_text and "_prompt_plugin_target_row" in prompt_text,
        "plugin_cleanup_durable_log_present": (
            "plugin.cleanup-log.persist" in options_text
            and "plugin.cleanup-log.file" in options_text
            and "plugin.cleanup-log.limit" in options_text
            and "def record_plugin_cleanup_report" in editor_text
            and "def plugin_cleanup_log_rows" in editor_text
            and "record_plugin_cleanup_report" in manager_text
            and "rows.extend(self.plugin_cleanup_log_rows(flt))" in editor_text
        ),
        "unload_uses_cleanup_commit_guard": "_cleanup_loaded_plugin_state_or_restore(" in manager_text and "plugin unload cleanup" in manager_text,
        "reload_uses_cleanup_commit_guard": "plugin reload cleanup old generation" in manager_text,
        "reload_uses_retag_commit_guard": "_retag_group_or_restore(" in manager_text and "plugin reload promote staged generation" in manager_text,
        "reload_uses_prestage_generation_guard": "plugin reload pre-stage generation cleanup" in manager_text,
        "commit_guard_uses_narrow_group_snapshot": (
            "snapshot_runtime_group_state(self.vm, groups=snapshot_groups)" in guard_body
            and "restore_runtime_group_state(self.vm, group_snapshot)" in guard_body
        ),
        "command_group_snapshot_present": (
            "class RuntimeCommandGroupSnapshot" in runtime_text
            and "def snapshot_command_group_state" in runtime_text
            and "def restore_command_group_state" in runtime_text
        ),
        "action_keymap_timer_group_snapshots_present": (
            "class RuntimeActionGroupSnapshot" in runtime_text
            and "def snapshot_action_group_state" in runtime_text
            and "def restore_action_group_state" in runtime_text
            and "class RuntimeKeymapGroupSnapshot" in runtime_text
            and "def snapshot_keymap_group_state" in runtime_text
            and "def restore_keymap_group_state" in runtime_text
            and "class RuntimeTimerGroupSnapshot" in runtime_text
            and "def snapshot_timer_group_state" in runtime_text
            and "def restore_timer_group_state" in runtime_text
        ),
        "hook_mark_group_snapshots_present": (
            "class RuntimeHookGroupSnapshot" in runtime_text
            and "def snapshot_hook_group_state" in runtime_text
            and "def restore_hook_group_state" in runtime_text
            and "class RuntimeMarkGroupSnapshot" in runtime_text
            and "def snapshot_mark_group_state" in runtime_text
            and "def restore_mark_group_state" in runtime_text
        ),
        "hook_snapshots_clone_mutable_handlers": (
            "def _clone_hook_handler" in runtime_text
            and "replace(handler) if isinstance(handler, HookHandler)" in runtime_text
            and "_clone_hook_handler(handler) for handler in list(word.handlers)" in runtime_text
        ),
        "delayed_group_snapshots_present": (
            "class RuntimeRecentFilesGroupSnapshot" in runtime_text
            and "def snapshot_recent_files_group_state" in runtime_text
            and "def restore_recent_files_group_state" in runtime_text
            and "class RuntimePaletteRecentGroupSnapshot" in runtime_text
            and "def snapshot_palette_recent_group_state" in runtime_text
            and "def restore_palette_recent_group_state" in runtime_text
            and "class RuntimePromptHistoryGroupSnapshot" in runtime_text
            and "def snapshot_prompt_history_group_state" in runtime_text
            and "def restore_prompt_history_group_state" in runtime_text
            and "class RuntimeSavedCursorGroupSnapshot" in runtime_text
            and "def snapshot_saved_cursor_group_state" in runtime_text
            and "def restore_saved_cursor_group_state" in runtime_text
        ),
        "runtime_group_snapshot_uses_touched_registry_surfaces": (
            "snapshot_action_group_state(ed, groups=groups)" in runtime_text
            and "snapshot_keymap_group_state(ed, groups=groups)" in runtime_text
            and "snapshot_timer_group_state(ed, groups=groups)" in runtime_text
            and "restore_action_group_state(ed, snap.action_state)" in runtime_text
            and "restore_keymap_group_state(ed, snap.keymap_state)" in runtime_text
            and "restore_timer_group_state(ed, snap.timer_state)" in runtime_text
            and "snapshot_hook_group_state(vm, groups=groups)" in runtime_text
            and "restore_hook_group_state(vm, snap.hook_state)" in runtime_text
            and "snapshot_mark_group_state(ed, groups=groups)" in runtime_text
            and "restore_mark_group_state(ed, snap.mark_state)" in runtime_text
        ),
        "runtime_group_snapshot_uses_touched_delayed_surfaces": (
            "snapshot_recent_files_group_state(ed, groups=groups)" in runtime_text
            and "restore_recent_files_group_state(ed, snap.recent_files_state)" in runtime_text
            and "snapshot_palette_recent_group_state(ed, groups=groups)" in runtime_text
            and "restore_palette_recent_group_state(ed, snap.palette_recent_state)" in runtime_text
            and "snapshot_prompt_history_group_state(ed, groups=groups)" in runtime_text
            and "restore_prompt_history_group_state(ed, snap.prompt_history_state)" in runtime_text
            and "snapshot_saved_cursor_group_state(ed, groups=groups)" in runtime_text
            and "restore_saved_cursor_group_state(ed, snap.saved_cursors_state)" in runtime_text
        ),
        "singleton_help_group_snapshots_present": (
            "class RuntimeClipboardGroupSnapshot" in runtime_text
            and "def snapshot_clipboard_group_state" in runtime_text
            and "def restore_clipboard_group_state" in runtime_text
            and "class RuntimeSearchGroupSnapshot" in runtime_text
            and "def snapshot_search_group_state" in runtime_text
            and "def restore_search_group_state" in runtime_text
            and "class RuntimeHelpHistoryGroupSnapshot" in runtime_text
            and "def snapshot_help_history_group_state" in runtime_text
            and "def restore_help_history_group_state" in runtime_text
        ),
        "runtime_group_snapshot_uses_touched_singleton_help_surfaces": (
            "snapshot_clipboard_group_state(ed, groups=groups)" in runtime_text
            and "restore_clipboard_group_state(ed, snap.clipboard_state)" in runtime_text
            and "snapshot_search_group_state(ed, groups=groups)" in runtime_text
            and "restore_search_group_state(ed, snap.search_state)" in runtime_text
            and "snapshot_help_history_group_state(ed, groups=groups)" in runtime_text
            and "restore_help_history_group_state(ed, snap.help_history_state)" in runtime_text
        ),
        "recovery_interaction_group_snapshots_present": (
            "class RuntimeRecoveryGroupSnapshot" in runtime_text
            and "def snapshot_recovery_group_state" in runtime_text
            and "def restore_recovery_group_state" in runtime_text
            and "class RuntimeInteractionGroupSnapshot" in runtime_text
            and "def snapshot_interaction_group_state" in runtime_text
            and "def restore_interaction_group_state" in runtime_text
        ),
        "runtime_group_snapshot_uses_touched_recovery_interaction_surfaces": (
            "snapshot_recovery_group_state(ed, groups=groups)" in runtime_text
            and "restore_recovery_group_state(ed, snap.recovery_state)" in runtime_text
            and "snapshot_interaction_group_state(ed, groups=groups)" in runtime_text
            and "restore_interaction_group_state(ed, snap.interaction_state)" in runtime_text
        ),
        "runtime_group_snapshot_avoids_full_cursor_interaction_restore": (
            "capture_cursor_state(ed)" not in runtime_snapshot_body
            and "snapshot_editor_interaction_state(ed)" not in runtime_snapshot_body
            and "restore_editor_interaction_state(ed, snap.interaction_state)" not in runtime_restore_body
        ),
        "commit_guard_passes_command_groups": (
            "snapshot_groups=(str(group),)" in manager_text
            and "snapshot_groups=(str(old), str(new))" in manager_text
        ),
        "loaded_cleanup_passes_command_group": (
            "runtime_group = self._plugin_group(plugin)" in loaded_cleanup_body
            and "snapshot_runtime_group_state(self.vm, groups=(runtime_group,))" in loaded_cleanup_body
        ),
        "commit_guard_avoids_full_registration_snapshot": "_snapshot_registrations" not in guard_body,
        "generation_guard_uses_narrow_snapshot": (
            "snapshot_runtime_generation_state(" in generation_guard_body
            and "plugin_load_root=plugin.root" in generation_guard_body
            and "plugin_generation=plugin.generation" in generation_guard_body
            and "restore_runtime_generation_state(self.vm, snapshot)" in generation_guard_body
        ),
        "generation_nonmacro_snapshots_present": (
            "class RuntimeAuthorityListGenerationSnapshot" in runtime_text
            and "class RuntimeRecoveryGenerationSnapshot" in runtime_text
            and "class RuntimePromptHistoryGenerationSnapshot" in runtime_text
            and "class RuntimeSavedCursorGenerationSnapshot" in runtime_text
            and "class RuntimeClipboardGenerationSnapshot" in runtime_text
            and "class RuntimeSearchGenerationSnapshot" in runtime_text
            and "class RuntimeHelpHistoryGenerationSnapshot" in runtime_text
            and "class RuntimeInteractionGenerationSnapshot" in runtime_text
        ),
        "generation_interaction_snapshot_present": (
            "class RuntimeInteractionGenerationSnapshot" in runtime_text
            and "def snapshot_interaction_generation_state" in runtime_text
            and "def restore_interaction_generation_state" in runtime_text
            and "def remove_plugin_interaction_generation" in editor_text
        ),
        "generation_snapshot_uses_scoped_nonmacro_surfaces": (
            "snapshot_recovery_generation_state(" in runtime_text
            and "restore_recovery_generation_state(ed, snap.recovery_generation_state" in runtime_text
            and "snapshot_recent_files_generation_state(" in runtime_text
            and "restore_recent_files_generation_state(ed, snap.recent_files_generation_state" in runtime_text
            and "snapshot_palette_recent_generation_state(" in runtime_text
            and "restore_palette_recent_generation_state(ed, snap.palette_recent_generation_state" in runtime_text
            and "snapshot_prompt_history_generation_state(" in runtime_text
            and "restore_prompt_history_generation_state(ed, snap.prompt_history_generation_state" in runtime_text
            and "snapshot_saved_cursor_generation_state(" in runtime_text
            and "restore_saved_cursor_generation_state(ed, snap.saved_cursors_generation_state" in runtime_text
            and "snapshot_clipboard_generation_state(" in runtime_text
            and "restore_clipboard_generation_state(ed, snap.clipboard_generation_state" in runtime_text
            and "snapshot_search_generation_state(" in runtime_text
            and "restore_search_generation_state(ed, snap.search_generation_state" in runtime_text
            and "snapshot_help_history_generation_state(" in runtime_text
            and "restore_help_history_generation_state(ed, snap.help_history_generation_state" in runtime_text
            and "snapshot_interaction_generation_state(" in runtime_text
            and "restore_interaction_generation_state(ed, snap.interaction_generation_state" in runtime_text
        ),
        "generation_macro_snapshot_present": (
            "class RuntimeMacroGenerationSnapshot" in runtime_text
            and "class RuntimeMacroSlotGenerationEntry" in runtime_text
            and "class RuntimeMacroRecordingGenerationSnapshot" in runtime_text
            and "def snapshot_macro_generation_state" in runtime_text
            and "def restore_macro_generation_state" in runtime_text
        ),
        "generation_snapshot_uses_scoped_macro_surface": (
            "macro_generation_state = snapshot_macro_generation_state(" in runtime_text
            and "restore_macro_generation_state(ed, snap.macro_generation_state" in runtime_text
            and "macro_generation_state=macro_generation_state" in runtime_text
        ),
        "scoped_generation_snapshot_avoids_broad_macro_restore": (
            "if snap.macro_recording is not None:" in runtime_text
            and "macro_default = [replace(step)" in runtime_text
            and "macro_generation_state = snapshot_macro_generation_state(" in runtime_text
        ),
        "loaded_cleanup_restores_group_and_generation": (
            "snapshot_runtime_group_state(self.vm, groups=(runtime_group,))" in loaded_cleanup_body
            and "snapshot_runtime_generation_state(" in loaded_cleanup_body
            and "plugin_load_root=plugin.root" in loaded_cleanup_body
            and "plugin_generation=plugin.generation" in loaded_cleanup_body
            and "restore_runtime_group_state(self.vm, group_snapshot)" in loaded_cleanup_body
            and "restore_runtime_generation_state(self.vm, generation_snapshot)" in loaded_cleanup_body
        ),
        "plugin_callback_scoped_snapshot_present": (
            "def snapshot_plugin_callback_state(" in runtime_text
            and "group_state = snapshot_runtime_group_state(vm, groups=(group_text,))" in runtime_text
            and "generation_state = snapshot_runtime_generation_state(" in runtime_text
            and "option_state = snapshot_options() if callable(snapshot_options) else None" in runtime_text
            and "registrations = snapshot_runtime_registrations(vm)" in runtime_text
        ),
        "plugin_callback_restore_uses_scoped_snapshots": (
            "restore_runtime_group_state(vm, snap.group_state)" in runtime_text
            and "restore_runtime_generation_state(vm, snap.generation_state)" in runtime_text
            and "_restore_option_state" in runtime_text
        ),
        "editor_passes_plugin_identity_to_callback_snapshot": (
            "return snapshot_plugin_callback_state(" in editor_text
            and 'plugin_load_root=getattr(plugin, "root", None)' in editor_text
            and 'plugin_generation=getattr(plugin, "generation", None)' in editor_text
            and "group=stable_group" in editor_text
        ),
        "dictionary_snapshot_restores_word_authority": (
            "word_authority: Any | None = None" in runtime_text
            and 'snapshot_word_authority = getattr(ed, "_snapshot_word_authority", None)' in runtime_text
            and "word_authority=(" in runtime_text
            and 'restore_word_authority = getattr(ed, "_restore_word_authority", None)' in runtime_text
            and "restore_word_authority(snap.word_authority)" in runtime_text
        ),
        "committed_plugin_wordlists_are_tombstoned": (
            "class PluginWordlistTombstone" in manager_text
            and "self.retired_wordlists: list[PluginWordlistTombstone]" in manager_text
            and "def _retire_plugin_wordlist" in manager_text
            and 'self._retire_plugin_wordlist(pl, reason="unload")' in manager_text
            and 'self._retire_plugin_wordlist(old_plugin, reason="reload")' in manager_text
            and "def _forget_wordlist_authority" in editor_text
        ),
        "retired_direct_xts_reject_execution": (
            "def _mark_retired_wordlist_words" in manager_text
            and "_micromax_retired_reason" in manager_text
            and "_micromax_retired_reason" in vm_text
            and "Retired execution token" in vm_text
        ),
        "retired_deferred_callbacks_reject_execution": (
            "def _stale_plugin_callback_reason" in editor_text
            and "stale plugin callback:" in editor_text
            and "run_script_origin_callback" in vm_text
            and "lambda t=t: self.vm.exec_xt(t.xt)" in editor_text
        ),
        "retired_interactions_reject_response": (
            "def _stale_plugin_authority_reason" in editor_text
            and "def _drop_stale_plugin_interaction" in editor_text
            and "stale plugin {kind}:" in editor_text
            and "self._drop_stale_plugin_interaction(authority)" in editor_text
            and 'stale_reason = self._stale_plugin_authority_reason(authority, label="prompt")' in editor_text
        ),
        "retired_macros_reject_playback": (
            "def _stale_plugin_macro_reason" in editor_text
            and "def _drop_stale_plugin_macro" in editor_text
            and "def _prune_stale_plugin_macros" in editor_text
            and "macro play: {stale_reason}" in editor_text
            and "self._clear_macro_slot(str(name))" in editor_text
        ),
        "timer_pending_work_budget": (
            "max_pending_timers" in editor_text
            and "def schedule_timer_checked" in editor_text
            and "pending timer budget exceeded" in editor_text
            and "ed.schedule_timer_checked(" in bridge_text
        ),
        "plugin_package_fingerprint_budgets": (
            "PLUGIN_PACKAGE_MAX_FILES" in manager_text
            and "PLUGIN_PACKAGE_MAX_TOTAL_BYTES" in manager_text
            and "package_fingerprint_max_files" in manager_text
            and "package_fingerprint_max_total_bytes" in manager_text
            and "plugin fingerprint: too many files" in manager_text
            and "plugin fingerprint: package too large" in manager_text
        ),
    }


def _release_hygiene() -> dict[str, Any]:
    locks = sorted(
        _relative(path)
        for path in ROOT.rglob("*")
        if path.is_file() and path.name in LOCK_NAMES and not _is_ignored(path)
    )
    workflows_root = ROOT / ".github" / "workflows"
    workflows = sorted(
        _relative(path)
        for path in _files(workflows_root)
        if path.suffix.lower() in {".yaml", ".yml"}
    )
    artifacts_root = ROOT / ".artifacts"
    manifests = sorted(
        _relative(path)
        for path in _files(artifacts_root)
        if path.name.startswith("mxtest-all") and path.suffix == ".json"
    )
    return {
        "lock_files": locks,
        "ci_workflows": workflows,
        "aggregate_evidence_manifests": manifests,
        "context_snapshot_present": (ROOT / "MICROMAX-CONTEXT.json").is_file(),
    }


def payload(*, limit: int = 10) -> dict[str, Any]:
    project = _pyproject()
    manifest = _manifest_rows()
    packaged = (
        project.get("tool", {})
        .get("setuptools", {})
        .get("data-files", {})
        .get("share/micromax/docs", [])
    )
    packaged_rows = [str(value) for value in packaged] if isinstance(packaged, list) else []
    revision_index = _revision_index()
    docs = _numbered_docs()
    docs.update(
        {
            "revision_index_entries": len(revision_index.get("entries") or []),
            "installed_help_docs": len(manifest),
            "installed_help_matches_pyproject": manifest == packaged_rows,
            "security_boundaries_installed": "docs/security-boundaries.md" in manifest,
        }
    )
    return {
        "schema": "micromax.audit-metrics.v1",
        "project": "micromax",
        "rev": _current_rev(),
        "version": str(project.get("project", {}).get("version", "")),
        "inventory": {
            "docs": _tree_stats("docs"),
            "source": _tree_stats("src"),
            "tests": _tree_stats("tests"),
            "tools": _tree_stats("tools"),
        },
        "python": _python_metrics(limit=max(1, int(limit))),
        "editor": _editor_metrics(),
        "plugin_runtime_snapshot": _snapshot_metrics(),
        "runtime_group_policy": _runtime_group_policy_metrics(),
        "recent_lifecycle_revisions": _recent_lifecycle_revisions(),
        "docs": docs,
        "typecheck": _typecheck_metrics(),
        "release_hygiene": _release_hygiene(),
    }


def check(data: dict[str, Any]) -> list[str]:
    """Return hard audit-integrity errors, not structural-debt warnings."""

    errors: list[str] = []
    docs = data.get("docs") or {}
    python = data.get("python") or {}
    if docs.get("installed_help_matches_pyproject") is not True:
        errors.append("installed help manifest does not match pyproject data-files")
    if docs.get("security_boundaries_installed") is not True:
        errors.append("living security contract is absent from installed help")
    for rel in python.get("parse_failures") or []:
        errors.append(f"could not parse Python source: {rel}")
    runtime_group_policy = data.get("runtime_group_policy") or {}
    for key in [
        "operation_error_class_present",
        "narrow_group_snapshot_present",
        "narrow_generation_snapshot_present",
        "generation_cleanup_report_present",
        "manager_retains_reports",
        "manager_exposes_failure_rows",
        "editor_exposes_cleanup_failure_rows",
        "plugin_cleanup_command_present",
        "plugin_cleanup_hostcall_present",
        "plugin_cleanup_completion_present",
        "plugin_cleanup_durable_log_present",
        "unload_uses_cleanup_commit_guard",
        "reload_uses_cleanup_commit_guard",
        "reload_uses_retag_commit_guard",
        "reload_uses_prestage_generation_guard",
        "commit_guard_uses_narrow_group_snapshot",
        "command_group_snapshot_present",
        "action_keymap_timer_group_snapshots_present",
        "hook_mark_group_snapshots_present",
        "hook_snapshots_clone_mutable_handlers",
        "delayed_group_snapshots_present",
        "runtime_group_snapshot_uses_touched_delayed_surfaces",
        "singleton_help_group_snapshots_present",
        "runtime_group_snapshot_uses_touched_singleton_help_surfaces",
        "recovery_interaction_group_snapshots_present",
        "runtime_group_snapshot_uses_touched_recovery_interaction_surfaces",
        "runtime_group_snapshot_avoids_full_cursor_interaction_restore",
        "runtime_group_snapshot_uses_touched_registry_surfaces",
        "commit_guard_passes_command_groups",
        "loaded_cleanup_passes_command_group",
        "commit_guard_avoids_full_registration_snapshot",
        "generation_guard_uses_narrow_snapshot",
        "generation_nonmacro_snapshots_present",
        "generation_interaction_snapshot_present",
        "generation_snapshot_uses_scoped_nonmacro_surfaces",
        "generation_macro_snapshot_present",
        "generation_snapshot_uses_scoped_macro_surface",
        "scoped_generation_snapshot_avoids_broad_macro_restore",
        "loaded_cleanup_restores_group_and_generation",
        "plugin_callback_scoped_snapshot_present",
        "plugin_callback_restore_uses_scoped_snapshots",
        "editor_passes_plugin_identity_to_callback_snapshot",
        "dictionary_snapshot_restores_word_authority",
        "committed_plugin_wordlists_are_tombstoned",
        "retired_direct_xts_reject_execution",
        "retired_deferred_callbacks_reject_execution",
        "retired_interactions_reject_response",
        "retired_macros_reject_playback",
        "timer_pending_work_budget",
        "plugin_package_fingerprint_budgets",
    ]:
        if runtime_group_policy.get(key) is not True:
            errors.append(f"runtime group policy check failed: {key}")
    if data.get("rev") is None:
        errors.append("could not infer current revision")
    return errors


def _human(data: dict[str, Any], *, errors: list[str]) -> str:
    inventory = data["inventory"]
    editor = data["editor"]
    snapshot = data["plugin_runtime_snapshot"]
    docs = data["docs"]
    release = data["release_hygiene"]
    typecheck = data["typecheck"]
    runtime_group_policy = data["runtime_group_policy"]
    lines = [
        f"Micromax audit metrics (rev{int(data['rev'] or 0):04d})",
        "",
        "Inventory:",
    ]
    for name in ("docs", "source", "tests", "tools"):
        row = inventory[name]
        lines.append(
            f"  {name:6s} {row['files']:4d} files  {row['lines']:7d} text lines  {row['bytes']:9d} bytes"
        )
    lines.extend(
        [
            "",
            "Structural hotspots:",
            *[
                f"  {row['lines']:6d}  {row['path']}"
                for row in data["python"]["top_files"]
            ],
            "",
            "Plugin lifecycle pressure:",
            f"  Editor: {editor.get('file_lines', 0)} file lines, {editor.get('method_count', 0)} methods, "
            f"{editor.get('init_state_attributes', 0)} __init__ state attributes",
            f"  RuntimeRegistrationSnapshot: {snapshot.get('field_count', 0)} fields",
            f"  lifecycle-heavy recent revisions: {len(data['recent_lifecycle_revisions'])}/12",
            f"  runtime cleanup guards: unload={runtime_group_policy['unload_uses_cleanup_commit_guard']} "
            f"reload-cleanup={runtime_group_policy['reload_uses_cleanup_commit_guard']} "
            f"reload-retag={runtime_group_policy['reload_uses_retag_commit_guard']} "
            f"group-snapshot={runtime_group_policy['commit_guard_uses_narrow_group_snapshot']} "
            f"command-group={runtime_group_policy['command_group_snapshot_present']} "
            f"registry-groups={runtime_group_policy['action_keymap_timer_group_snapshots_present']} "
            f"hook-mark-groups={runtime_group_policy['hook_mark_group_snapshots_present']} "
            f"hook-clones={runtime_group_policy['hook_snapshots_clone_mutable_handlers']} "
            f"delayed-groups={runtime_group_policy['delayed_group_snapshots_present']} "
            f"singleton-help={runtime_group_policy['singleton_help_group_snapshots_present']} "
            f"recovery-interaction={runtime_group_policy['recovery_interaction_group_snapshots_present']} "
            f"generation-snapshot={runtime_group_policy['generation_guard_uses_narrow_snapshot']} "
            f"generation-rows={runtime_group_policy['generation_nonmacro_snapshots_present']} "
            f"generation-macros={runtime_group_policy['generation_macro_snapshot_present']} "
            f"generation-interactions={runtime_group_policy['generation_interaction_snapshot_present']} "
            f"diagnostics={runtime_group_policy['plugin_cleanup_command_present']} "
            f"durable-log={runtime_group_policy['plugin_cleanup_durable_log_present']} "
            f"callback-scope={runtime_group_policy['plugin_callback_scoped_snapshot_present']} "
            f"dictionary-provenance={runtime_group_policy['dictionary_snapshot_restores_word_authority']} "
            f"wordlist-tombstones={runtime_group_policy['committed_plugin_wordlists_are_tombstoned']} "
            f"retired-xt-guard={runtime_group_policy['retired_direct_xts_reject_execution']} "
            f"retired-callback-guard={runtime_group_policy['retired_deferred_callbacks_reject_execution']} "
            f"retired-interaction-guard={runtime_group_policy['retired_interactions_reject_response']} "
            f"retired-macro-guard={runtime_group_policy['retired_macros_reject_playback']} "
            f"timer-budget={runtime_group_policy['timer_pending_work_budget']} "
            f"package-budgets={runtime_group_policy['plugin_package_fingerprint_budgets']}",
            "",
            "Docs and release hygiene:",
            f"  root markdown docs: {docs['root_markdown_files']} "
            f"({docs['numbered_root_docs_ge_100']} numbered >=100)",
            f"  duplicate numeric prefixes: {len(docs['duplicate_numeric_prefixes'])}",
            f"  installed help: {docs['installed_help_docs']} docs; "
            f"security contract installed={docs['security_boundaries_installed']}",
            f"  lock files: {len(release['lock_files'])}; CI workflows: {len(release['ci_workflows'])}; "
            f"aggregate manifests: {len(release['aggregate_evidence_manifests'])}",
            f"  typecheck covers editor package={typecheck['covers_editor_package']}",
        ]
    )
    if errors:
        lines.extend(["", "Audit integrity errors:", *[f"  - {error}" for error in errors]])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--check", action="store_true", help="fail on audit-integrity errors")
    parser.add_argument("--limit", type=int, default=10, help="number of top files/definitions")
    args = parser.parse_args(argv)

    data = payload(limit=args.limit)
    errors = check(data)
    if args.json:
        emitted = dict(data)
        emitted["checks"] = {"ok": not errors, "errors": errors}
        print(json.dumps(emitted, indent=2, sort_keys=True))
    else:
        sys.stdout.write(_human(data, errors=errors))
    return 1 if args.check and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

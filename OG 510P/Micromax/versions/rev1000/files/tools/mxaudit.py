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
SRC = ROOT / "src"
TOOLS = ROOT / "tools"
for import_root in (SRC, TOOLS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import mxrelease  # noqa: E402
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
# One source of truth: release lock discovery must agree with mxrelease rather
# than maintaining a stale second registry here.
LOCK_NAMES = set(mxrelease.LOCK_FILE_NAMES)

CURATED_REV_ENTRYPOINTS = (
    "README.md",
    "TODO.md",
    "docs/01-llm-start-here.md",
    "docs/02-repo-map.md",
    "docs/40-roadmap.md",
    "docs/41-decisions-log.md",
    "docs/43-worklist.md",
)


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


def _read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


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



def _rev_marker_for_file(rel: str) -> int | None:
    """Return the first revision marker in a curated human entrypoint."""

    path = ROOT / rel
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[:12]
    for line in lines:
        match = re.search(r"rev\s*(\d+)", line, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _curated_entrypoint_revisions(current_rev: int | None) -> dict[str, Any]:
    """Report whether high-signal handoff docs point at the current revision."""

    revisions = {rel: _rev_marker_for_file(rel) for rel in CURATED_REV_ENTRYPOINTS}
    stale = [
        {"path": rel, "rev": rev}
        for rel, rev in revisions.items()
        if current_rev is None or rev != current_rev
    ]
    return {
        "curated_entrypoint_revs": revisions,
        "curated_entrypoint_stale": stale,
        "curated_entrypoints_match_current": not stale,
    }

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


def _function_node(
    path: Path,
    name: str,
    *,
    class_name: str | None = None,
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return one top-level function or direct class method from ``path``."""

    tree = _parse_python(path)
    if tree is None:
        return None
    body: list[ast.stmt]
    if class_name is None:
        body = tree.body
    else:
        cls = next(
            (
                node
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name == class_name
            ),
            None,
        )
        if cls is None:
            return None
        body = cls.body
    return next(
        (
            node
            for node in body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ),
        None,
    )


def _call_leaf_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _function_routes_call_result_to_keywords(
    path: Path,
    *,
    function_name: str,
    producer_name: str,
    sink_names: set[str],
    keyword_name: str,
    class_name: str | None = None,
) -> bool:
    """Recognize a bounded value routed directly or through a local alias.

    Structural audits should survive harmless formatting and a useful local
    variable.  This intentionally performs only one-function, one-assignment
    data flow: values returned by ``producer_name`` may be passed directly or
    assigned to a local name that is then supplied as ``keyword_name`` to every
    named sink.  It does not try to be a general static analyzer.
    """

    function = _function_node(path, function_name, class_name=class_name)
    if function is None:
        return False

    aliases: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or _call_leaf_name(value) != producer_name:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        aliases.update(target.id for target in targets if isinstance(target, ast.Name))

    def _is_producer_value(value: ast.expr) -> bool:
        return (
            isinstance(value, ast.Call)
            and _call_leaf_name(value) == producer_name
        ) or (isinstance(value, ast.Name) and value.id in aliases)

    matched: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        sink = _call_leaf_name(node)
        if sink not in sink_names:
            continue
        if any(
            keyword.arg == keyword_name and _is_producer_value(keyword.value)
            for keyword in node.keywords
        ):
            matched.add(str(sink))
    return matched == sink_names


def _function_docstring_contains(
    path: Path,
    function_name: str,
    *fragments: str,
) -> bool:
    function = _function_node(path, function_name)
    if function is None:
        return False
    doc = ast.get_docstring(function, clean=True) or ""
    return all(fragment in doc for fragment in fragments)


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


def _editor_trust_metrics() -> dict[str, Any]:
    """Report the small startup and destructive-exit trust boundaries.

    These are structural guardrails, not behavioral proof. Focused tests still
    carry the behavior; the audit keeps future refactors from silently routing
    one front end around the shared owner or reviving mutable double-tap bits.
    """

    editor_text = _read("src/micromax_editor/editor.py")
    discard_text = _read("src/micromax_editor/discard_guard.py")
    startup_text = _read("src/micromax_editor/startup.py")
    main_text = _read("src/micromax_editor/__main__.py")
    tui_text = _read("src/micromax_editor/tui.py")
    session_text = _read("src/micromax_editor/session_commands.py")
    buffer_commands_text = _read("src/micromax_editor/buffer_commands.py")
    tests_text = _read("tests/test_editor_startup_discard_trust.py")
    editor_source = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((ROOT / "src" / "micromax_editor").glob("*.py"))
    )
    legacy_assignment = re.compile(
        r"(?:self|ed)\._(?:quit_armed|close_armed|close_armed_name|closeall_armed|only_armed)\s*=(?!=)"
    )

    return {
        "state_bound_discard_guard_present": (
            "class DiscardConfirmationGuard" in discard_text
            and "class DiscardBufferWitness" in discard_text
            and "version=int(getattr(buf, \"version\", 0))" in discard_text
            and "_ref=weakref.ref(editor_buffer)" in discard_text
            and "self._discard_confirmation = DiscardConfirmationGuard()" in editor_text
        ),
        "legacy_mutable_discard_flags_absent": legacy_assignment.search(editor_source) is None,
        "discard_commands_share_guard": (
            'ed._discard_confirmation_request("quit")' in session_text
            and 'self._discard_confirmation_request("close", target=target)' in editor_text
            and 'ed._discard_confirmation_request("closeall")' in buffer_commands_text
            and 'ed._discard_confirmation_request("only", keep=keep)' in buffer_commands_text
            and "format_discard_warning" in session_text
            and "format_discard_warning" in buffer_commands_text
            and "format_discard_warning" in editor_text
        ),
        "same_name_replacement_identity_present": (
            "class DiscardIdentityWitness" in discard_text
            and "anchors.append((keep_name, self.buffers[keep_name]))" in editor_text
            and "test_close_confirmation_rearms_for_same_name_buffer_replacement" in tests_text
            and "test_only_confirmation_rearms_for_same_name_keep_replacement" in tests_text
        ),
        "shared_initial_buffer_boundary_present": (
            "class InitialBufferResult" in startup_text
            and "def open_initial_buffer(" in startup_text
            and "def _ensure_active_buffer(" in startup_text
            and "open_initial_buffer(" in main_text
            and "open_initial_buffer(" in tui_text
        ),
        "failed_startup_remains_renderable": (
            'ed.new_buffer("*scratch*", "")' in startup_text
            and "ed.screen_model(lines=8, cols=40)" in tests_text
            and "test_dump_screen_failed_initial_path_returns_json_and_nonzero" in tests_text
        ),
        "headless_exit_uses_editor_quit_policy": (
            "def run_headless_repl(" in main_text
            and 'if line in {":q", ":q!"}:' in main_text
            and "ed.exec_command_line(command)" in main_text
            and 'ed.exec_command_line("quit")' in main_text
            and 'if line == ":q":' not in main_text
        ),
        "dirty_noninteractive_eof_is_nonzero": (
            "EOF refused a clean shutdown" in main_text
            and "return 2" in main_text
            and "test_headless_repl_noninteractive_eof_refuses_clean_success" in tests_text
            and "test_headless_repl_tty_eof_returns_to_prompt_without_arming" in tests_text
        ),
        "trusted_and_restricted_journeys_present": (
            "test_trusted_startup_edit_conflict_recovery_and_close_journey" in tests_text
            and "test_restricted_startup_keeps_host_defaults_and_user_file_flow" in tests_text
        ),
    }


def _buffer_creation_metrics() -> dict[str, Any]:
    """Report ownership and no-clobber guards around editor buffer creation."""

    editor_path = ROOT / "src" / "micromax_editor" / "editor.py"
    names_text = _read("src/micromax_editor/buffer_names.py")
    commands_text = _read("src/micromax_editor/buffer_commands.py")
    dispatcher_text = _read("src/micromax_editor/command_dispatcher.py")
    actions_text = _read("src/micromax_editor/actions_default.py")
    tests_text = _read("tests/test_editor_buffer_creation.py")

    cls = _class_node(editor_path, "Editor")
    methods = {
        item.name: item
        for item in (cls.body if cls is not None else [])
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    source = editor_path.read_text(encoding="utf-8", errors="replace")

    def _method_text(name: str) -> str:
        node = methods.get(name)
        if node is None:
            return ""
        return str(ast.get_source_segment(source, node) or "")

    def _self_attribute(node: ast.AST, name: str) -> bool:
        return (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and node.attr == name
        )

    def _self_buffers_attribute(node: ast.AST) -> bool:
        return _self_attribute(node, "buffers")

    def _self_marks_attribute(node: ast.AST) -> bool:
        return _self_attribute(node, "marks")

    new_node = methods.get("new_buffer")
    collision_guard_line = 0
    allocation_line = 0
    strict_write_line = 0
    assignment_sites: list[dict[str, object]] = []
    deletion_sites: list[dict[str, object]] = []
    registry_assignment_sites: list[dict[str, object]] = []
    insertion_call_sites: list[dict[str, object]] = []
    removal_call_sites: list[dict[str, object]] = []
    clear_call_sites: list[dict[str, object]] = []
    mark_registry_assignment_sites: list[dict[str, object]] = []
    mark_insertion_call_sites: list[dict[str, object]] = []
    mark_clear_call_sites: list[dict[str, object]] = []

    if new_node is not None:
        for item in ast.walk(new_node):
            if isinstance(item, ast.If):
                try:
                    test = ast.unparse(item.test)
                except Exception:
                    test = ""
                raises_collision = any(
                    isinstance(child, ast.Raise)
                    and isinstance(child.exc, ast.Call)
                    and isinstance(child.exc.func, ast.Name)
                    and child.exc.func.id == "BufferNameCollisionError"
                    for child in ast.walk(item)
                )
                if test == "name in self.buffers" and raises_collision:
                    collision_guard_line = int(getattr(item, "lineno", 0) or 0)
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
                if (
                    isinstance(item.func.value, ast.Name)
                    and item.func.value.id == "self"
                    and item.func.attr == "_alloc_cursor_id"
                ):
                    allocation_line = int(getattr(item, "lineno", 0) or 0)

    if cls is not None:
        for method in methods.values():
            for item in ast.walk(method):
                # Any subscript in Store context catches ordinary, annotated,
                # and augmented assignment forms without relying on parent shape.
                if isinstance(item, ast.Subscript) and _self_buffers_attribute(item.value):
                    line = int(getattr(item, "lineno", 0) or 0)
                    if isinstance(item.ctx, ast.Store):
                        assignment_sites.append({"method": method.name, "line": line})
                        if method.name == "new_buffer":
                            strict_write_line = line
                    elif isinstance(item.ctx, ast.Del):
                        deletion_sites.append({"method": method.name, "line": line})

                targets: list[ast.AST] = []
                if isinstance(item, ast.Assign):
                    targets = list(item.targets)
                elif isinstance(item, ast.AnnAssign):
                    targets = [item.target]
                elif isinstance(item, ast.AugAssign):
                    targets = [item.target]
                for target in targets:
                    row = {
                        "method": method.name,
                        "line": int(getattr(item, "lineno", 0) or 0),
                    }
                    if _self_buffers_attribute(target):
                        registry_assignment_sites.append(row)
                    elif _self_marks_attribute(target):
                        mark_registry_assignment_sites.append(row)

                if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Attribute):
                    continue
                row = {
                    "method": method.name,
                    "operation": str(item.func.attr),
                    "line": int(getattr(item, "lineno", 0) or 0),
                }
                if _self_buffers_attribute(item.func.value):
                    if item.func.attr in {"update", "setdefault", "__setitem__", "__ior__"}:
                        insertion_call_sites.append(row)
                    elif item.func.attr in {"pop", "popitem", "__delitem__"}:
                        removal_call_sites.append(row)
                    elif item.func.attr == "clear":
                        clear_call_sites.append(row)
                elif _self_marks_attribute(item.func.value):
                    if item.func.attr in {"update", "setdefault", "__setitem__", "__ior__"}:
                        mark_insertion_call_sites.append(row)
                    elif item.func.attr == "clear":
                        mark_clear_call_sites.append(row)

    for rows in (
        assignment_sites,
        deletion_sites,
        registry_assignment_sites,
        insertion_call_sites,
        removal_call_sites,
        clear_call_sites,
        mark_registry_assignment_sites,
        mark_insertion_call_sites,
        mark_clear_call_sites,
    ):
        rows.sort(key=lambda row: (int(row["line"]), str(row["method"])))

    owners = [str(row["method"]) for row in assignment_sites]
    deletion_owners = [str(row["method"]) for row in deletion_sites]
    registry_assignment_owners = [
        str(row["method"]) for row in registry_assignment_sites
    ]
    insertion_call_owners = [str(row["method"]) for row in insertion_call_sites]
    removal_call_owners = [str(row["method"]) for row in removal_call_sites]
    clear_call_owners = [str(row["method"]) for row in clear_call_sites]
    mark_registry_assignment_owners = [
        str(row["method"]) for row in mark_registry_assignment_sites
    ]
    mark_insertion_call_owners = [
        str(row["method"]) for row in mark_insertion_call_sites
    ]
    mark_clear_call_owners = [str(row["method"]) for row in mark_clear_call_sites]

    unique_text = _method_text("new_buffer_unique")
    untitled_text = _method_text("create_untitled_buffer")
    open_text = _method_text("open_file")
    help_text = _method_text("open_help_doc")
    rename_text = _method_text("rename_buffer")
    restore_text = _method_text("_restore_buffer_identity")
    transaction_restore_text = _method_text("_restore_macro_replay_snapshot")

    return {
        "unique_name_owner_present": (
            "class BufferNameCollisionError" in names_text
            and "def unique_buffer_name(" in names_text
            and "range(2, len(occupied) + 2)" in names_text
        ),
        "strict_creation_guard_precedes_state_mutation": (
            collision_guard_line > 0
            and allocation_line > collision_guard_line
            and strict_write_line > allocation_line
        ),
        "human_creation_routes_through_unique_owner": (
            "unique_buffer_name(name, self.buffers.keys())" in unique_text
            and "self.new_buffer_unique" in untitled_text
            and "self.new_buffer_unique" in open_text
            and "self.new_buffer_unique" in help_text
        ),
        "interactive_surface_present": (
            "def c_new(" in commands_text
            and 'd.register("new", c_new' in dispatcher_text
            and "def a_new_buffer(" in actions_text
            and 'self.actions.register("NewBuffer", a_new_buffer' in actions_text
        ),
        "script_creation_denial_present": (
            "self.in_script_context()" in untitled_text
            and "interactive buffer creation only" in untitled_text
            and "test_new_command_and_action_are_interactive_only" in tests_text
            and "test_script_origin_binding_cannot_launder_new_buffer_authority"
            in tests_text
            and "test_trusted_user_binding_can_invoke_new_buffer_action" in tests_text
        ),
        "focused_collision_regressions_present": all(
            name in tests_text
            for name in (
                "test_strict_new_buffer_collision_is_side_effect_free",
                "test_open_file_disambiguates_pathless_same_name_buffer",
                "test_help_open_disambiguates_pathless_same_name_buffer",
                "test_new_command_uses_collision_free_names",
                "test_failed_macro_creation_rollback_preserves_public_registry_identity",
                "test_buffer_transaction_undo_redo_preserves_public_registry_identity",
            )
        ),
        "runtime_registry_replacement_absent": registry_assignment_owners == ["__init__"],
        "mark_registry_replacement_absent": mark_registry_assignment_owners == ["__init__"],
        "transactional_restore_preserves_registry_identity": (
            insertion_call_owners == ["_restore_macro_replay_snapshot"]
            and clear_call_owners == ["_restore_macro_replay_snapshot"]
            and "self.buffers.clear()" in transaction_restore_text
            and "self.buffers.update(restored)" in transaction_restore_text
            and "self.marks.clear()" in transaction_restore_text
            and "self.marks.update(restored_marks)" in transaction_restore_text
            and "test_failed_macro_creation_rollback_preserves_public_registry_identity"
            in tests_text
            and "test_buffer_transaction_undo_redo_preserves_public_registry_identity"
            in tests_text
        ),
        "mark_restores_preserve_registry_identity": (
            mark_insertion_call_owners
            == [
                "_restore_mark_entries",
                "_restore_buffer_identity",
                "_restore_macro_replay_snapshot",
            ]
            and mark_clear_call_owners
            == [
                "_restore_mark_entries",
                "_restore_buffer_identity",
                "_restore_macro_replay_snapshot",
            ]
        ),
        "direct_buffer_mutations_have_explicit_owners": (
            owners == ["new_buffer", "_restore_buffer_identity", "rename_buffer"]
            and deletion_owners
            == ["_restore_buffer_identity", "close_buffer", "close_buffers"]
            and registry_assignment_owners == ["__init__"]
            and insertion_call_owners == ["_restore_macro_replay_snapshot"]
            and removal_call_owners == ["rename_buffer"]
            and clear_call_owners == ["_restore_macro_replay_snapshot"]
            and "if n in self.buffers" in rename_text
            and "self.buffers[str(snap.name)] = eb" in restore_text
        ),
        # Compatibility key retained for existing audit consumers. It now means
        # the stronger all-mutations inventory, not only assignment stores.
        "direct_buffer_writes_have_explicit_owners": (
            owners == ["new_buffer", "_restore_buffer_identity", "rename_buffer"]
            and deletion_owners
            == ["_restore_buffer_identity", "close_buffer", "close_buffers"]
            and registry_assignment_owners == ["__init__"]
            and insertion_call_owners == ["_restore_macro_replay_snapshot"]
            and removal_call_owners == ["rename_buffer"]
            and clear_call_owners == ["_restore_macro_replay_snapshot"]
        ),
        "direct_buffer_assignment_sites": assignment_sites,
        "direct_buffer_deletion_sites": deletion_sites,
        "registry_assignment_sites": registry_assignment_sites,
        "insertion_call_sites": insertion_call_sites,
        "removal_call_sites": removal_call_sites,
        "clear_call_sites": clear_call_sites,
        "mark_registry_assignment_sites": mark_registry_assignment_sites,
        "mark_insertion_call_sites": mark_insertion_call_sites,
        "mark_clear_call_sites": mark_clear_call_sites,
        "collision_guard_line": collision_guard_line,
        "first_allocation_line": allocation_line,
        "strict_write_line": strict_write_line,
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
    buffer_path = ROOT / "src" / "micromax_editor" / "buffer.py"
    query_replace_path = ROOT / "src" / "micromax_editor" / "query_replace.py"
    commands_path = ROOT / "src" / "micromax_editor" / "plugin_commands.py"
    prompt_path = ROOT / "src" / "micromax_editor" / "prompt_suggestions.py"
    prompt_completion_path = ROOT / "src" / "micromax_editor" / "prompt_completion.py"
    bridge_path = ROOT / "src" / "micromax_editor" / "micromax_bridge.py"
    boundary_path = ROOT / "src" / "micromax_editor" / "hostcall_boundary.py"
    host_process_path = ROOT / "src" / "micromax_editor" / "host_process.py"
    open_url_process_path = ROOT / "src" / "micromax_editor" / "open_url_process.py"
    open_url_child_path = ROOT / "src" / "micromax_editor" / "open_url_child.py"
    worker_process_path = ROOT / "src" / "micromax" / "worker_process.py"
    load_policy_path = ROOT / "src" / "micromax_editor" / "vm_load_policy.py"
    fs_hostcalls_path = ROOT / "src" / "micromax_editor" / "fs_hostcalls.py"
    file_access_path = ROOT / "src" / "micromax_editor" / "file_access.py"
    file_write_path = ROOT / "src" / "micromax_editor" / "file_write.py"
    file_recovery_path = ROOT / "src" / "micromax_editor" / "file_recovery.py"
    file_scriptops_path = ROOT / "src" / "micromax_editor" / "file_scriptops.py"
    docs_index_path = ROOT / "src" / "micromax_editor" / "docs_index.py"
    project_files_path = ROOT / "src" / "micromax_editor" / "project_files.py"
    commandbar_path = ROOT / "src" / "micromax_editor" / "commandbar.py"
    actions_path = ROOT / "src" / "micromax_editor" / "actions_default.py"
    dispatcher_path = ROOT / "src" / "micromax_editor" / "command_dispatcher.py"
    picker_commands_path = ROOT / "src" / "micromax_editor" / "picker_commands.py"
    default_keybindings_path = ROOT / "src" / "micromax_editor" / "default_keybindings.py"
    core_plugin_path = ROOT / "plugins" / "core" / "init.mx"
    plugin_meta_path = ROOT / "src" / "micromax_editor" / "plugin_meta.py"
    plugin_io_path = ROOT / "src" / "micromax_editor" / "plugin_io.py"
    plugin_package_path = ROOT / "src" / "micromax_editor" / "plugin_package.py"
    registry_path = ROOT / "src" / "micromax_editor" / "editor_hostcall_registry.py"
    vm_path = ROOT / "src" / "micromax" / "vm.py"
    stdlib_resource_path = ROOT / "src" / "micromax" / "stdlib_resource.py"
    timers_path = ROOT / "src" / "micromax_editor" / "timers.py"
    core_path = ROOT / "src" / "micromax" / "core.py"
    host_limits_path = ROOT / "src" / "micromax" / "host_limits.py"
    host_regex_path = ROOT / "src" / "micromax" / "host_regex.py"
    regex_runtime_path = ROOT / "src" / "micromax" / "regex_runtime.py"
    regex_child_path = ROOT / "src" / "micromax" / "regex_worker_child.py"
    editor_search_path = ROOT / "src" / "micromax_editor" / "search.py"
    editor_replace_path = ROOT / "src" / "micromax_editor" / "replace_plan.py"
    runtime_text = runtime_path.read_text(encoding="utf-8", errors="replace") if runtime_path.exists() else ""
    manager_text = manager_path.read_text(encoding="utf-8", errors="replace") if manager_path.exists() else ""
    editor_text = editor_path.read_text(encoding="utf-8", errors="replace") if editor_path.exists() else ""
    buffer_text = buffer_path.read_text(encoding="utf-8", errors="replace") if buffer_path.exists() else ""
    query_replace_text = (
        query_replace_path.read_text(encoding="utf-8", errors="replace")
        if query_replace_path.exists()
        else ""
    )
    commands_text = commands_path.read_text(encoding="utf-8", errors="replace") if commands_path.exists() else ""
    prompt_text = prompt_path.read_text(encoding="utf-8", errors="replace") if prompt_path.exists() else ""
    prompt_completion_text = prompt_completion_path.read_text(encoding="utf-8", errors="replace") if prompt_completion_path.exists() else ""
    bridge_text = bridge_path.read_text(encoding="utf-8", errors="replace") if bridge_path.exists() else ""
    boundary_text = boundary_path.read_text(encoding="utf-8", errors="replace") if boundary_path.exists() else ""
    host_process_text = host_process_path.read_text(encoding="utf-8", errors="replace") if host_process_path.exists() else ""
    open_url_process_text = (
        open_url_process_path.read_text(encoding="utf-8", errors="replace")
        if open_url_process_path.exists()
        else ""
    )
    open_url_child_text = (
        open_url_child_path.read_text(encoding="utf-8", errors="replace")
        if open_url_child_path.exists()
        else ""
    )
    worker_process_text = (
        worker_process_path.read_text(encoding="utf-8", errors="replace")
        if worker_process_path.exists()
        else ""
    )
    load_policy_text = load_policy_path.read_text(encoding="utf-8", errors="replace") if load_policy_path.exists() else ""
    fs_hostcalls_text = fs_hostcalls_path.read_text(encoding="utf-8", errors="replace") if fs_hostcalls_path.exists() else ""
    file_access_text = file_access_path.read_text(encoding="utf-8", errors="replace") if file_access_path.exists() else ""
    file_write_text = file_write_path.read_text(encoding="utf-8", errors="replace") if file_write_path.exists() else ""
    file_recovery_text = file_recovery_path.read_text(encoding="utf-8", errors="replace") if file_recovery_path.exists() else ""
    file_scriptops_text = file_scriptops_path.read_text(encoding="utf-8", errors="replace") if file_scriptops_path.exists() else ""
    docs_index_text = docs_index_path.read_text(encoding="utf-8", errors="replace") if docs_index_path.exists() else ""
    project_files_text = project_files_path.read_text(encoding="utf-8", errors="replace") if project_files_path.exists() else ""
    commandbar_text = commandbar_path.read_text(encoding="utf-8", errors="replace") if commandbar_path.exists() else ""
    actions_text = actions_path.read_text(encoding="utf-8", errors="replace") if actions_path.exists() else ""
    dispatcher_text = dispatcher_path.read_text(encoding="utf-8", errors="replace") if dispatcher_path.exists() else ""
    picker_commands_text = picker_commands_path.read_text(encoding="utf-8", errors="replace") if picker_commands_path.exists() else ""
    default_keybindings_text = default_keybindings_path.read_text(encoding="utf-8", errors="replace") if default_keybindings_path.exists() else ""
    core_plugin_text = core_plugin_path.read_text(encoding="utf-8", errors="replace") if core_plugin_path.exists() else ""
    project_picker_tests_text = _read("tests/test_editor_project_file_picker.py")
    plugin_meta_text = plugin_meta_path.read_text(encoding="utf-8", errors="replace") if plugin_meta_path.exists() else ""
    plugin_io_text = plugin_io_path.read_text(encoding="utf-8", errors="replace") if plugin_io_path.exists() else ""
    plugin_package_text = (
        plugin_package_path.read_text(encoding="utf-8", errors="replace")
        if plugin_package_path.exists()
        else ""
    )
    registry_text = registry_path.read_text(encoding="utf-8", errors="replace") if registry_path.exists() else ""
    vm_text = vm_path.read_text(encoding="utf-8", errors="replace") if vm_path.exists() else ""
    stdlib_resource_text = stdlib_resource_path.read_text(encoding="utf-8", errors="replace") if stdlib_resource_path.exists() else ""
    timers_text = timers_path.read_text(encoding="utf-8", errors="replace") if timers_path.exists() else ""
    core_text = core_path.read_text(encoding="utf-8", errors="replace") if core_path.exists() else ""
    host_limits_text = host_limits_path.read_text(encoding="utf-8", errors="replace") if host_limits_path.exists() else ""
    host_regex_text = host_regex_path.read_text(encoding="utf-8", errors="replace") if host_regex_path.exists() else ""
    regex_runtime_text = (
        regex_runtime_path.read_text(encoding="utf-8", errors="replace")
        if regex_runtime_path.exists()
        else ""
    )
    regex_child_text = (
        regex_child_path.read_text(encoding="utf-8", errors="replace")
        if regex_child_path.exists()
        else ""
    )
    editor_search_text = (
        editor_search_path.read_text(encoding="utf-8", errors="replace")
        if editor_search_path.exists()
        else ""
    )
    editor_replace_text = (
        editor_replace_path.read_text(encoding="utf-8", errors="replace")
        if editor_replace_path.exists()
        else ""
    )
    options_text = (ROOT / "src" / "micromax_editor" / "options_default.py").read_text(encoding="utf-8", errors="replace")
    option_policy_text = (ROOT / "src" / "micromax_editor" / "option_policy.py").read_text(encoding="utf-8", errors="replace")
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
    registration_snapshot_match = re.search(
        r"def snapshot_runtime_registrations\b(?P<body>.*?)(?:\ndef snapshot_editor_interaction_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    registration_snapshot_body = (
        registration_snapshot_match.group("body") if registration_snapshot_match else ""
    )
    registration_restore_match = re.search(
        r"def restore_runtime_registrations\b(?P<body>.*?)(?:\ndef _callback_context_tokens|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    registration_restore_body = (
        registration_restore_match.group("body") if registration_restore_match else ""
    )
    registration_palette_recent_owner_prefix = registration_snapshot_body.split(
        "if palette_recent_state is None", 1
    )[0]
    recent_files_group_snapshot_match = re.search(
        r"def snapshot_recent_files_group_state\b(?P<body>.*?)(?:\ndef restore_recent_files_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recent_files_group_snapshot_body = (
        recent_files_group_snapshot_match.group("body")
        if recent_files_group_snapshot_match
        else ""
    )
    recent_files_group_restore_match = re.search(
        r"def restore_recent_files_group_state\b(?P<body>.*?)(?:\ndef snapshot_palette_recent_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recent_files_group_restore_body = (
        recent_files_group_restore_match.group("body") if recent_files_group_restore_match else ""
    )
    palette_recent_group_snapshot_match = re.search(
        r"def snapshot_palette_recent_group_state\b(?P<body>.*?)(?:\ndef restore_palette_recent_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    palette_recent_group_snapshot_body = (
        palette_recent_group_snapshot_match.group("body")
        if palette_recent_group_snapshot_match
        else ""
    )
    palette_recent_group_restore_match = re.search(
        r"def restore_palette_recent_group_state\b(?P<body>.*?)(?:\ndef _saved_cursor_pos_copy|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    palette_recent_group_restore_body = (
        palette_recent_group_restore_match.group("body")
        if palette_recent_group_restore_match
        else ""
    )

    recent_files_generation_snapshot_match = re.search(
        r"def snapshot_recent_files_generation_state\b(?P<body>.*?)(?:\ndef restore_recent_files_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recent_files_generation_snapshot_body = (
        recent_files_generation_snapshot_match.group("body")
        if recent_files_generation_snapshot_match
        else ""
    )
    recent_files_generation_restore_match = re.search(
        r"def restore_recent_files_generation_state\b(?P<body>.*?)(?:\ndef snapshot_palette_recent_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recent_files_generation_restore_body = (
        recent_files_generation_restore_match.group("body")
        if recent_files_generation_restore_match
        else ""
    )
    palette_recent_generation_snapshot_match = re.search(
        r"def snapshot_palette_recent_generation_state\b(?P<body>.*?)(?:\ndef restore_palette_recent_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    palette_recent_generation_snapshot_body = (
        palette_recent_generation_snapshot_match.group("body")
        if palette_recent_generation_snapshot_match
        else ""
    )
    palette_recent_generation_restore_match = re.search(
        r"def restore_palette_recent_generation_state\b(?P<body>.*?)(?:\ndef snapshot_prompt_history_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    palette_recent_generation_restore_body = (
        palette_recent_generation_restore_match.group("body")
        if palette_recent_generation_restore_match
        else ""
    )

    saved_cursor_group_snapshot_match = re.search(
        r"def snapshot_saved_cursor_group_state\b(?P<body>.*?)(?:\ndef restore_saved_cursor_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    saved_cursor_group_snapshot_body = (
        saved_cursor_group_snapshot_match.group("body")
        if saved_cursor_group_snapshot_match
        else ""
    )
    saved_cursor_group_restore_match = re.search(
        r"def restore_saved_cursor_group_state\b(?P<body>.*?)(?:\ndef snapshot_prompt_history_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    saved_cursor_group_restore_body = (
        saved_cursor_group_restore_match.group("body") if saved_cursor_group_restore_match else ""
    )

    prompt_history_group_snapshot_match = re.search(
        r"def snapshot_prompt_history_group_state\b(?P<body>.*?)(?:\ndef restore_prompt_history_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    prompt_history_group_snapshot_body = (
        prompt_history_group_snapshot_match.group("body")
        if prompt_history_group_snapshot_match
        else ""
    )
    prompt_history_group_restore_match = re.search(
        r"def restore_prompt_history_group_state\b(?P<body>.*?)(?:\ndef snapshot_clipboard_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    prompt_history_group_restore_body = (
        prompt_history_group_restore_match.group("body") if prompt_history_group_restore_match else ""
    )
    prompt_history_generation_snapshot_match = re.search(
        r"def snapshot_prompt_history_generation_state\b(?P<body>.*?)(?:\ndef restore_prompt_history_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    prompt_history_generation_snapshot_body = (
        prompt_history_generation_snapshot_match.group("body")
        if prompt_history_generation_snapshot_match
        else ""
    )
    prompt_history_generation_restore_match = re.search(
        r"def restore_prompt_history_generation_state\b(?P<body>.*?)(?:\ndef snapshot_saved_cursor_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    prompt_history_generation_restore_body = (
        prompt_history_generation_restore_match.group("body")
        if prompt_history_generation_restore_match
        else ""
    )
    saved_cursor_generation_snapshot_match = re.search(
        r"def snapshot_saved_cursor_generation_state\b(?P<body>.*?)(?:\ndef restore_saved_cursor_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    saved_cursor_generation_snapshot_body = (
        saved_cursor_generation_snapshot_match.group("body")
        if saved_cursor_generation_snapshot_match
        else ""
    )
    saved_cursor_generation_restore_match = re.search(
        r"def restore_saved_cursor_generation_state\b(?P<body>.*?)(?:\ndef snapshot_clipboard_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    saved_cursor_generation_restore_body = (
        saved_cursor_generation_restore_match.group("body")
        if saved_cursor_generation_restore_match
        else ""
    )

    clipboard_group_snapshot_match = re.search(
        r"def snapshot_clipboard_group_state\b(?P<body>.*?)(?:\ndef _clear_clipboard_register|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    clipboard_group_snapshot_body = (
        clipboard_group_snapshot_match.group("body") if clipboard_group_snapshot_match else ""
    )
    clipboard_group_restore_match = re.search(
        r"def restore_clipboard_group_state\b(?P<body>.*?)(?:\ndef snapshot_search_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    clipboard_group_restore_body = (
        clipboard_group_restore_match.group("body") if clipboard_group_restore_match else ""
    )
    clipboard_generation_snapshot_match = re.search(
        r"def snapshot_clipboard_generation_state\b(?P<body>.*?)(?:\ndef restore_clipboard_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    clipboard_generation_snapshot_body = (
        clipboard_generation_snapshot_match.group("body") if clipboard_generation_snapshot_match else ""
    )
    clipboard_generation_restore_match = re.search(
        r"def restore_clipboard_generation_state\b(?P<body>.*?)(?:\ndef snapshot_search_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    clipboard_generation_restore_body = (
        clipboard_generation_restore_match.group("body") if clipboard_generation_restore_match else ""
    )
    search_group_snapshot_match = re.search(
        r"def snapshot_search_group_state\b(?P<body>.*?)(?:\ndef _clear_search_register|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    search_group_snapshot_body = (
        search_group_snapshot_match.group("body") if search_group_snapshot_match else ""
    )
    search_group_restore_match = re.search(
        r"def restore_search_group_state\b(?P<body>.*?)(?:\ndef _clone_help_history_entry|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    search_group_restore_body = (
        search_group_restore_match.group("body") if search_group_restore_match else ""
    )
    search_generation_snapshot_match = re.search(
        r"def snapshot_search_generation_state\b(?P<body>.*?)(?:\ndef restore_search_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    search_generation_snapshot_body = (
        search_generation_snapshot_match.group("body") if search_generation_snapshot_match else ""
    )
    search_generation_restore_match = re.search(
        r"def restore_search_generation_state\b(?P<body>.*?)(?:\ndef snapshot_help_history_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    search_generation_restore_body = (
        search_generation_restore_match.group("body") if search_generation_restore_match else ""
    )
    help_history_group_snapshot_match = re.search(
        r"def snapshot_help_history_group_state\b(?P<body>.*?)(?:\ndef _restore_help_history_lane|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    help_history_group_snapshot_body = (
        help_history_group_snapshot_match.group("body")
        if help_history_group_snapshot_match
        else ""
    )
    help_history_group_restore_match = re.search(
        r"def restore_help_history_group_state\b(?P<body>.*?)(?:\ndef _runtime_recovery_generation_rows|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    help_history_group_restore_body = (
        help_history_group_restore_match.group("body")
        if help_history_group_restore_match
        else ""
    )
    help_history_generation_snapshot_match = re.search(
        r"def snapshot_help_history_generation_state\b(?P<body>.*?)(?:\ndef _restore_help_history_generation_lane|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    help_history_generation_snapshot_body = (
        help_history_generation_snapshot_match.group("body")
        if help_history_generation_snapshot_match
        else ""
    )
    help_history_generation_restore_match = re.search(
        r"def restore_help_history_generation_state\b(?P<body>.*?)(?:\ndef snapshot_runtime_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    help_history_generation_restore_body = (
        help_history_generation_restore_match.group("body")
        if help_history_generation_restore_match
        else ""
    )
    recovery_group_snapshot_match = re.search(
        r"def snapshot_recovery_group_state\b(?P<body>.*?)(?:\ndef _runtime_recovery_rows|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recovery_group_snapshot_body = (
        recovery_group_snapshot_match.group("body") if recovery_group_snapshot_match else ""
    )
    recovery_group_restore_match = re.search(
        r"def restore_recovery_group_state\b(?P<body>.*?)(?:\ndef _snapshot_active_interaction_cursor|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recovery_group_restore_body = (
        recovery_group_restore_match.group("body") if recovery_group_restore_match else ""
    )
    recovery_generation_snapshot_match = re.search(
        r"def snapshot_recovery_generation_state\b(?P<body>.*?)(?:\ndef _restore_recovery_generation_rows|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recovery_generation_snapshot_body = (
        recovery_generation_snapshot_match.group("body")
        if recovery_generation_snapshot_match
        else ""
    )
    recovery_generation_restore_match = re.search(
        r"def restore_recovery_generation_state\b(?P<body>.*?)(?:\ndef snapshot_recent_files_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    recovery_generation_restore_body = (
        recovery_generation_restore_match.group("body")
        if recovery_generation_restore_match
        else ""
    )
    interaction_group_snapshot_match = re.search(
        r"def snapshot_interaction_group_state\b(?P<body>.*?)(?:\ndef _restore_key_mode_group_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    interaction_group_snapshot_body = (
        interaction_group_snapshot_match.group("body") if interaction_group_snapshot_match else ""
    )
    interaction_group_restore_match = re.search(
        r"def restore_interaction_group_state\b(?P<body>.*?)(?:\ndef _keymode_matches_generation|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    interaction_group_restore_body = (
        interaction_group_restore_match.group("body") if interaction_group_restore_match else ""
    )
    interaction_generation_snapshot_match = re.search(
        r"def snapshot_interaction_generation_state\b(?P<body>.*?)(?:\ndef restore_interaction_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    interaction_generation_snapshot_body = (
        interaction_generation_snapshot_match.group("body") if interaction_generation_snapshot_match else ""
    )
    interaction_generation_restore_match = re.search(
        r"def restore_interaction_generation_state\b(?P<body>.*?)(?:\ndef _clone_runtime_authority|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    interaction_generation_restore_body = (
        interaction_generation_restore_match.group("body") if interaction_generation_restore_match else ""
    )
    callback_interaction_snapshot_match = re.search(
        r"def snapshot_editor_interaction_state\b(?P<body>.*?)(?:\ndef restore_editor_interaction_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    callback_interaction_snapshot_body = (
        callback_interaction_snapshot_match.group("body") if callback_interaction_snapshot_match else ""
    )
    callback_interaction_restore_match = re.search(
        r"def restore_editor_interaction_state\b(?P<body>.*?)(?:\ndef _normalize_runtime_groups|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    callback_interaction_restore_body = (
        callback_interaction_restore_match.group("body") if callback_interaction_restore_match else ""
    )
    macro_generation_snapshot_match = re.search(
        r"def snapshot_macro_generation_state\b(?P<body>.*?)(?:\ndef restore_macro_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    macro_generation_snapshot_body = (
        macro_generation_snapshot_match.group("body") if macro_generation_snapshot_match else ""
    )
    macro_generation_restore_match = re.search(
        r"def restore_macro_generation_state\b(?P<body>.*?)(?:\ndef snapshot_runtime_generation_state|\nclass |\Z)",
        runtime_text,
        flags=re.DOTALL,
    )
    macro_generation_restore_body = (
        macro_generation_restore_match.group("body") if macro_generation_restore_match else ""
    )
    macro_generation_snapshot_owner_prefix = macro_generation_snapshot_body.split("# Fallback", 1)[0]
    macro_generation_restore_owner_prefix = macro_generation_restore_body.split("# Fallback", 1)[0]
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
        "mark_owner_snapshot_present": (
            "class MarkRegisterEntry" in editor_text
            and "class MarkRegisterSnapshot" in editor_text
            and "def snapshot_mark_group_state" in editor_text
            and "def restore_mark_group_state" in editor_text
            and 'getattr(ed, "snapshot_mark_group_state", None)' in runtime_text
            and 'getattr(ed, "restore_mark_group_state", None)' in runtime_text
            and "mark_state = snapshot_mark_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_mark_group_state(ed, snap.mark_state)" in registration_restore_body
            and "snapshot_mark_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_mark_group_state(ed, snap.mark_state)" in runtime_restore_body
            and "test_runtime_group_mark_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_mark_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
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
        "recovery_owner_snapshot_present": (
            "class RecoveryRegisterEntry" in editor_text
            and "class RecoveryBufferRegisterSnapshot" in editor_text
            and "class RecoveryRegisterSnapshot" in editor_text
            and "def snapshot_recovery_group_state" in editor_text
            and "def restore_recovery_group_state" in editor_text
            and "def snapshot_recovery_generation_state" in editor_text
            and "def restore_recovery_generation_state" in editor_text
            and 'getattr(ed, "snapshot_recovery_group_state", None)' in recovery_group_snapshot_body
            and 'getattr(ed, "restore_recovery_group_state", None)' in recovery_group_restore_body
            and 'getattr(ed, "snapshot_recovery_generation_state", None)' in recovery_generation_snapshot_body
            and 'getattr(ed, "restore_recovery_generation_state", None)' in recovery_generation_restore_body
            and "recovery_state = snapshot_recovery_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_recovery_group_state(ed, snap.recovery_state)" in registration_restore_body
            and "snapshot_recovery_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_recovery_group_state(ed, snap.recovery_state)" in runtime_restore_body
            and "snapshot_recovery_generation_state(" in runtime_text
            and "restore_recovery_generation_state(ed, snap.recovery_generation_state" in runtime_text
            and "test_runtime_group_recovery_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_recovery_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_recovery_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "keymode_owner_snapshot_present": (
            "class KeyModeInteractionRow" in editor_text
            and "class KeyModeInteractionSnapshot" in editor_text
            and "def snapshot_key_mode_group_state" in editor_text
            and "def restore_key_mode_group_state" in editor_text
            and "def snapshot_key_mode_generation_state" in editor_text
            and "def restore_key_mode_generation_state" in editor_text
            and "snapshot_key_mode_group_state" in interaction_group_snapshot_body
            and "restore_key_mode_group_state" in runtime_text
            and "snapshot_key_mode_generation_state" in interaction_generation_snapshot_body
            and "restore_key_mode_generation_state" in interaction_generation_restore_body
            and 'getattr(ed, "key_mode_stack"' not in interaction_group_snapshot_body
            and "ed.key_mode_stack" not in interaction_group_restore_body
            and 'getattr(ed, "key_mode_stack"' not in interaction_generation_snapshot_body
            and "ed.key_mode_stack" not in interaction_generation_restore_body
            and "test_runtime_group_interaction_snapshot_restore_uses_keymode_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_interaction_snapshot_restore_uses_keymode_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "prompt_owner_snapshot_present": (
            "class PromptInteractionSnapshot" in editor_text
            and "def snapshot_prompt_group_state" in editor_text
            and "def restore_prompt_group_state" in editor_text
            and "def snapshot_prompt_generation_state" in editor_text
            and "def restore_prompt_generation_state" in editor_text
            and "snapshot_prompt_group_state" in interaction_group_snapshot_body
            and "restore_prompt_group_state" in interaction_group_restore_body
            and "snapshot_prompt_generation_state" in interaction_generation_snapshot_body
            and "restore_prompt_generation_state" in interaction_generation_restore_body
            and 'getattr(ed, "prompt"' not in interaction_group_snapshot_body
            and "ed.prompt" not in interaction_group_restore_body
            and 'getattr(ed, "prompt"' not in interaction_generation_snapshot_body
            and "ed.prompt" not in interaction_generation_restore_body
            and "test_runtime_group_interaction_snapshot_restore_uses_prompt_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_interaction_snapshot_restore_uses_prompt_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "pending_open_url_owner_snapshot_present": (
            "class PendingOpenUrlInteractionSnapshot" in editor_text
            and "def snapshot_pending_open_url_group_state" in editor_text
            and "def restore_pending_open_url_group_state" in editor_text
            and "def snapshot_pending_open_url_generation_state" in editor_text
            and "def restore_pending_open_url_generation_state" in editor_text
            and "snapshot_pending_open_url_group_state" in interaction_group_snapshot_body
            and "restore_pending_open_url_group_state" in interaction_group_restore_body
            and "snapshot_pending_open_url_generation_state" in interaction_generation_snapshot_body
            and "restore_pending_open_url_generation_state" in interaction_generation_restore_body
            and 'getattr(ed, "_pending_open_url' not in interaction_group_snapshot_body
            and "ed._pending_open_url" not in interaction_group_restore_body
            and 'getattr(ed, "_pending_open_url' not in interaction_generation_snapshot_body
            and "ed._pending_open_url" not in interaction_generation_restore_body
            and "test_runtime_group_interaction_snapshot_restore_uses_open_url_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_interaction_snapshot_restore_uses_open_url_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "qreplace_owner_snapshot_present": (
            "class QueryReplaceInteractionSnapshot" in editor_text
            and "class QueryReplaceInteractionCursorSnapshot" in editor_text
            and "def snapshot_qreplace_group_state" in editor_text
            and "def restore_qreplace_group_state" in editor_text
            and "def snapshot_qreplace_generation_state" in editor_text
            and "def restore_qreplace_generation_state" in editor_text
            and "snapshot_qreplace_group_state" in interaction_group_snapshot_body
            and "restore_qreplace_group_state" in interaction_group_restore_body
            and "snapshot_qreplace_generation_state" in interaction_generation_snapshot_body
            and "restore_qreplace_generation_state" in interaction_generation_restore_body
            and 'getattr(ed, "qreplace"' not in interaction_group_snapshot_body
            and "ed.qreplace" not in interaction_group_restore_body
            and 'getattr(ed, "qreplace"' not in interaction_generation_snapshot_body
            and "ed.qreplace" not in interaction_generation_restore_body
            and "test_runtime_group_interaction_snapshot_restore_uses_qreplace_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_interaction_snapshot_restore_uses_qreplace_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "qreplace_buffer_witness_present": (
            "class QueryReplaceBufferWitness" in query_replace_text
            and "weakref.ref(editor_buffer)" in query_replace_text
            and "buffer_witness: QueryReplaceBufferWitness | None" in editor_text
            and "def _qreplace_target_buffer" in editor_text
            and "buffer_witness=QueryReplaceBufferWitness.capture" in editor_text
            and "def _qreplace_dispose" in editor_text
            and 'authority=getattr(sess, "authority", None)' in editor_text
            and "qreplace_undo_state" in runtime_text
            and "def _snapshot_qreplace_undo_state" in runtime_text
            and "def _restore_qreplace_undo_state" in runtime_text
            and "test_qreplace_buffer_switch_finalizes_original_buffer_undo" in _read("tests/test_editor_qreplace_interaction_boundary.py")
            and "test_qreplace_survives_target_rename_by_object_identity" in _read("tests/test_editor_qreplace_interaction_boundary.py")
            and "test_qreplace_runtime_cleanup_clears_only_target_and_keeps_undo" in _read("tests/test_editor_qreplace_interaction_boundary.py")
            and "test_qreplace_close_drops_identity_without_retargeting_reused_name" in _read("tests/test_editor_qreplace_interaction_boundary.py")
            and "test_qreplace_accept_marks_script_dirty_before_session_finishes" in _read("tests/test_editor_interaction_authority.py")
            and "test_failed_group_cleanup_rewinds_provisional_qreplace_undo" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_failed_generation_cleanup_rewinds_provisional_qreplace_undo" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "recent_files_owner_snapshot_present": (
            "class RecentFilesRegisterEntry" in editor_text
            and "class RecentFilesRegisterSnapshot" in editor_text
            and "def snapshot_recent_files_group_state" in editor_text
            and "def restore_recent_files_group_state" in editor_text
            and "def snapshot_recent_files_generation_state" in editor_text
            and "def restore_recent_files_generation_state" in editor_text
            and 'getattr(ed, "snapshot_recent_files_group_state", None)' in recent_files_group_snapshot_body
            and 'getattr(ed, "restore_recent_files_group_state", None)' in recent_files_group_restore_body
            and 'getattr(ed, "snapshot_recent_files_generation_state", None)' in recent_files_generation_snapshot_body
            and 'getattr(ed, "restore_recent_files_generation_state", None)' in recent_files_generation_restore_body
            and "recent_files_state = snapshot_recent_files_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_recent_files_group_state(ed, snap.recent_files_state)" in registration_restore_body
            and "snapshot_recent_files_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_recent_files_group_state(ed, snap.recent_files_state)" in runtime_restore_body
            and "snapshot_recent_files_generation_state(" in runtime_text
            and "restore_recent_files_generation_state(ed, snap.recent_files_generation_state" in runtime_text
            and "test_runtime_group_recent_files_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_recent_files_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_recent_files_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "palette_recent_owner_snapshot_present": (
            "class PaletteRecentRegisterEntry" in editor_text
            and "class PaletteRecentRegisterSnapshot" in editor_text
            and "def snapshot_palette_recent_group_state" in editor_text
            and "def restore_palette_recent_group_state" in editor_text
            and "def snapshot_palette_recent_generation_state" in editor_text
            and "def restore_palette_recent_generation_state" in editor_text
            and 'getattr(ed, "snapshot_palette_recent_group_state", None)' in palette_recent_group_snapshot_body
            and 'getattr(ed, "restore_palette_recent_group_state", None)' in palette_recent_group_restore_body
            and 'getattr(ed, "snapshot_palette_recent_generation_state", None)' in palette_recent_generation_snapshot_body
            and 'getattr(ed, "restore_palette_recent_generation_state", None)' in palette_recent_generation_restore_body
            and "palette_recent_state = snapshot_palette_recent_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_palette_recent_group_state(ed, snap.palette_recent_state)" in registration_restore_body
            and "snapshot_palette_recent_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_palette_recent_group_state(ed, snap.palette_recent_state)" in runtime_restore_body
            and "snapshot_palette_recent_generation_state(" in runtime_text
            and "restore_palette_recent_generation_state(ed, snap.palette_recent_generation_state" in runtime_text
            and 'getattr(ed, "_palette_recent", [])' not in registration_palette_recent_owner_prefix
            and "test_runtime_group_palette_recent_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_palette_recent_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_palette_recent_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "prompt_history_owner_snapshot_present": (
            "class PromptHistoryRegisterEntry" in editor_text
            and "class PromptHistoryRegisterSnapshot" in editor_text
            and "def snapshot_prompt_history_group_state" in editor_text
            and "def restore_prompt_history_group_state" in editor_text
            and "def snapshot_prompt_history_generation_state" in editor_text
            and "def restore_prompt_history_generation_state" in editor_text
            and 'getattr(ed, "snapshot_prompt_history_group_state", None)' in prompt_history_group_snapshot_body
            and 'getattr(ed, "restore_prompt_history_group_state", None)' in prompt_history_group_restore_body
            and 'getattr(ed, "snapshot_prompt_history_generation_state", None)' in prompt_history_generation_snapshot_body
            and 'getattr(ed, "restore_prompt_history_generation_state", None)' in prompt_history_generation_restore_body
            and "prompt_history_state = snapshot_prompt_history_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_prompt_history_group_state(ed, snap.prompt_history_state)" in registration_restore_body
            and "snapshot_prompt_history_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_prompt_history_group_state(ed, snap.prompt_history_state)" in runtime_restore_body
            and "snapshot_prompt_history_generation_state(" in runtime_text
            and "restore_prompt_history_generation_state(ed, snap.prompt_history_generation_state" in runtime_text
            and 'getattr(ed, "history", {})' not in registration_snapshot_body
            and "test_runtime_group_prompt_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_prompt_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_prompt_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "saved_cursor_owner_snapshot_present": (
            "class SavedCursorRegisterEntry" in editor_text
            and "class SavedCursorRegisterSnapshot" in editor_text
            and "def snapshot_saved_cursor_group_state" in editor_text
            and "def restore_saved_cursor_group_state" in editor_text
            and "def snapshot_saved_cursor_generation_state" in editor_text
            and "def restore_saved_cursor_generation_state" in editor_text
            and 'getattr(ed, "snapshot_saved_cursor_group_state", None)' in saved_cursor_group_snapshot_body
            and 'getattr(ed, "restore_saved_cursor_group_state", None)' in saved_cursor_group_restore_body
            and 'getattr(ed, "snapshot_saved_cursor_generation_state", None)' in saved_cursor_generation_snapshot_body
            and 'getattr(ed, "restore_saved_cursor_generation_state", None)' in saved_cursor_generation_restore_body
            and "saved_cursors_state = snapshot_saved_cursor_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_saved_cursor_group_state(ed, snap.saved_cursors_state)" in registration_restore_body
            and "snapshot_saved_cursor_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_saved_cursor_group_state(ed, snap.saved_cursors_state)" in runtime_restore_body
            and "snapshot_saved_cursor_generation_state(" in runtime_text
            and "restore_saved_cursor_generation_state(ed, snap.saved_cursors_generation_state" in runtime_text
            and 'getattr(ed, "_saved_cursors", {})' not in registration_snapshot_body
            and "test_runtime_group_saved_cursor_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_saved_cursor_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_saved_cursor_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "clipboard_owner_snapshot_present": (
            "class ClipboardRegisterSnapshot" in editor_text
            and "def snapshot_clipboard_group_state" in editor_text
            and "def restore_clipboard_group_state" in editor_text
            and "def snapshot_clipboard_generation_state" in editor_text
            and "def restore_clipboard_generation_state" in editor_text
            and 'getattr(ed, "snapshot_clipboard_group_state", None)' in clipboard_group_snapshot_body
            and 'getattr(ed, "restore_clipboard_group_state", None)' in clipboard_group_restore_body
            and 'getattr(ed, "snapshot_clipboard_generation_state", None)' in clipboard_generation_snapshot_body
            and 'getattr(ed, "restore_clipboard_generation_state", None)' in clipboard_generation_restore_body
            and "snapshot_clipboard_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_clipboard_group_state(ed, snap.clipboard_state)" in registration_restore_body
            and "snapshot_clipboard_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_clipboard_group_state(ed, snap.clipboard_state)" in runtime_restore_body
            and "snapshot_clipboard_generation_state(" in runtime_text
            and "restore_clipboard_generation_state(ed, snap.clipboard_generation_state" in runtime_text
            and 'getattr(ed, "clipboard_items"' not in registration_snapshot_body
            and "test_runtime_group_clipboard_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_clipboard_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_clipboard_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "active_search_owner_snapshot_present": (
            "class ActiveSearchRegisterSnapshot" in editor_text
            and "def snapshot_search_group_state" in editor_text
            and "def restore_search_group_state" in editor_text
            and "def snapshot_search_generation_state" in editor_text
            and "def restore_search_generation_state" in editor_text
            and 'getattr(ed, "snapshot_search_group_state", None)' in search_group_snapshot_body
            and 'getattr(ed, "restore_search_group_state", None)' in search_group_restore_body
            and 'getattr(ed, "snapshot_search_generation_state", None)' in search_generation_snapshot_body
            and 'getattr(ed, "restore_search_generation_state", None)' in search_generation_restore_body
            and "snapshot_search_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_search_group_state(ed, snap.search_state)" in registration_restore_body
            and "snapshot_search_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_search_group_state(ed, snap.search_state)" in runtime_restore_body
            and "snapshot_search_generation_state(" in runtime_text
            and "restore_search_generation_state(ed, snap.search_generation_state" in runtime_text
            and 'getattr(ed, "_snapshot_search_state", None)' not in registration_snapshot_body
            and 'getattr(ed, "_restore_search_state", None)' not in registration_restore_body
            and "test_runtime_group_search_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_search_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_search_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
        ),
        "help_history_owner_snapshot_present": (
            "class HelpHistoryRegisterEntry" in editor_text
            and "class HelpHistoryRegisterSnapshot" in editor_text
            and "def snapshot_help_history_group_state" in editor_text
            and "def restore_help_history_group_state" in editor_text
            and "def snapshot_help_history_generation_state" in editor_text
            and "def restore_help_history_generation_state" in editor_text
            and 'getattr(ed, "snapshot_help_history_group_state", None)' in help_history_group_snapshot_body
            and 'getattr(ed, "restore_help_history_group_state", None)' in help_history_group_restore_body
            and 'getattr(ed, "snapshot_help_history_generation_state", None)' in help_history_generation_snapshot_body
            and 'getattr(ed, "restore_help_history_generation_state", None)' in help_history_generation_restore_body
            and "help_history_state = snapshot_help_history_group_state(ed, groups=None)" in registration_snapshot_body
            and "restore_help_history_group_state(ed, snap.help_history_state)" in registration_restore_body
            and "snapshot_help_history_group_state(ed, groups=groups)" in runtime_snapshot_body
            and "restore_help_history_group_state(ed, snap.help_history_state)" in runtime_restore_body
            and "snapshot_help_history_generation_state(" in runtime_text
            and "restore_help_history_generation_state(ed, snap.help_history_generation_state" in runtime_text
            and 'getattr(ed, "_snapshot_help_history_state", None)' not in registration_snapshot_body
            and 'getattr(ed, "_restore_help_history_state", None)' not in registration_restore_body
            and "test_runtime_group_help_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_runtime_generation_help_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
            and "test_broad_registration_help_history_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
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
        "macro_owner_generation_snapshot_present": (
            "class MacroGenerationSnapshot" in editor_text
            and "class MacroGenerationSlotSnapshot" in editor_text
            and "class MacroGenerationRecordingSnapshot" in editor_text
            and "def snapshot_macro_generation_state" in editor_text
            and "def restore_macro_generation_state" in editor_text
            and 'getattr(ed, "snapshot_macro_generation_state", None)' in macro_generation_snapshot_body
            and 'getattr(ed, "restore_macro_generation_state", None)' in macro_generation_restore_body
            and 'getattr(ed, "macros"' not in macro_generation_snapshot_owner_prefix
            and "ed.macros" not in macro_generation_restore_owner_prefix
            and "test_runtime_generation_macro_snapshot_restore_uses_editor_owner" in _read("tests/test_plugin_runtime_group_policy.py")
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
            and "option_state = snapshot_option_state(ed)" in runtime_text
            and "registrations = snapshot_runtime_registrations(vm)" in runtime_text
        ),
        "plugin_callback_interaction_owner_present": (
            "class PluginCallbackInteractionSnapshot" in editor_text
            and "def snapshot_plugin_callback_interaction_state" in editor_text
            and "def restore_plugin_callback_interaction_state" in editor_text
            and "snapshot_key_mode_group_state(None)" in editor_text
            and "snapshot_prompt_group_state(None)" in editor_text
            and "snapshot_qreplace_group_state(None)" in editor_text
            and "snapshot_pending_open_url_group_state(None)" in editor_text
            and 'getattr(ed, "snapshot_plugin_callback_interaction_state", None)' in callback_interaction_snapshot_body
            and 'getattr(ed, "restore_plugin_callback_interaction_state", None)' in callback_interaction_restore_body
            and 'getattr(ed, "prompt"' not in callback_interaction_snapshot_body
            and 'getattr(ed, "qreplace"' not in callback_interaction_snapshot_body
            and 'getattr(ed, "key_mode_stack"' not in callback_interaction_snapshot_body
            and 'getattr(ed, "_pending_open_url' not in callback_interaction_snapshot_body
            and "ed.prompt" not in callback_interaction_restore_body
            and "ed.qreplace" not in callback_interaction_restore_body
            and "ed.key_mode_stack" not in callback_interaction_restore_body
            and "ed._pending_open_url" not in callback_interaction_restore_body
            and "test_failed_plugin_callback_rollback_routes_interactions_through_editor_owner" in _read("tests/test_plugin_callback_scoped_snapshot.py")
        ),
        "option_state_owner_snapshot_present": (
            "class BufferLocalOptionSnapshot" in editor_text
            and "class OptionStateSnapshot" in editor_text
            and "def snapshot_option_state" in editor_text
            and "def restore_option_state" in editor_text
            and 'getattr(ed, "snapshot_option_state", None)' in runtime_text
            and 'getattr(ed, "restore_option_state", None)' in runtime_text
            and 'getattr(ed, "_snapshot_option_state", None)' in runtime_text
            and 'getattr(ed, "_restore_option_state", None)' in runtime_text
            and "option_state = snapshot_option_state(ed)" in registration_snapshot_body
            and "restore_option_state(ed, snap.option_state)" in registration_restore_body
            and "option_state = snapshot_option_state(ed)" in runtime_text
            and "restore_option_state(ed_for_options, snap.option_state)" in runtime_text
            and "test_broad_registration_option_snapshot_restore_uses_editor_owner" in _read("tests/test_editor_plugin_option_rollback.py")
            and "test_scoped_plugin_callback_option_snapshot_restore_uses_editor_owner" in _read("tests/test_editor_plugin_option_rollback.py")
        ),
        "plugin_callback_restore_uses_scoped_snapshots": (
            "restore_runtime_group_state(vm, snap.group_state)" in runtime_text
            and "restore_runtime_generation_state(vm, snap.generation_state)" in runtime_text
            and "restore_option_state" in runtime_text
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
            and "def _run_timer(t=t) -> None:" in editor_text
            and "self.vm.exec_xt(t.xt)" in editor_text
            and 'plugin_generation=getattr(t, "plugin_generation", None)' in editor_text
            and "test_reinserted_hook_handler_from_retired_generation_does_not_run"
            in _read("tests/test_plugin_retired_wordlists.py")
            and "test_reinserted_timer_from_retired_generation_does_not_run"
            in _read("tests/test_plugin_retired_wordlists.py")
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
        "qreplace_all_replacement_budget": (
            "qreplace.max" in options_text
            and "def _qreplace_all_replacement_limit" in editor_text
            and "stopped at qreplace.max" in editor_text
            and "applied >= limit" in editor_text
            and "test_qreplace_all_stops_at_configured_replacement_budget_and_keeps_session_active" in _read("tests/test_editor_query_replace.py")
            and "test_qreplace_all_zero_budget_preserves_unbounded_explicit_opt_in" in _read("tests/test_editor_query_replace.py")
        ),
        "timer_pending_work_budget": (
            "max_pending_timers" in editor_text
            and "def schedule_timer_checked" in editor_text
            and "pending timer budget exceeded" in editor_text
            and "ed.schedule_timer_checked(" in bridge_text
        ),
        "timer_cancellation_releases_tasks": (
            "def retained_task_count" in timers_text
            and "def heap_entry_count" in timers_text
            and "def snapshot_state" in timers_text
            and "def restore_state" in timers_text
            and "def snapshot_group_tasks" in timers_text
            and "def restore_group_tasks" in timers_text
            and "self._tasks.pop(int(tid), None)" in timers_text
            and "def _maybe_compact_heap" in timers_text
            and "timers.snapshot_state()" in runtime_text
            and "timers.restore_state(" in runtime_text
            and "timers.snapshot_group_tasks(normalized)" in runtime_text
            and "timers.restore_group_tasks(snap.groups, snap.tasks)" in runtime_text
            and "test_cancel_timer_releases_callback_payload_and_task_row" in _read("tests/test_editor_timer_authority.py")
            and "test_repeated_schedule_cancel_keeps_stale_heap_entries_bounded" in _read("tests/test_editor_timer_authority.py")
        ),
        "vm_hostcall_result_budget": (
            "DEFAULT_HOSTCALL_RESULT_MAX_BYTES" in host_limits_text
            and "def hostcall_result_budget_violation" in host_limits_text
            and "def changed_stack_suffix" in host_limits_text
            and "self.hostcall_result_max_bytes" in vm_text
            and "self.hostcall_result_max_cells" in vm_text
            and "changed_stack_suffix(before_stack, vm.stack)" in core_text
            and "hostcall_result_budget_violation(" in core_text
            and "vm.stack[:] = before_stack" in core_text
        ),
        "stdlib_resource_contract_present": (
            "STDLIB_RESOURCE_SCHEMA" in stdlib_resource_text
            and "STDLIB_RESOURCE_MAX_BYTES" in stdlib_resource_text
            and "def read_stdlib_resource_bounded" in stdlib_resource_text
            and '.open("rb")' in stdlib_resource_text
            and "read(int(max_bytes) + 1)" in stdlib_resource_text
            and "StdlibResourceLimitError" in stdlib_resource_text
            and "hashlib.sha256" in stdlib_resource_text
            and "stdlib_resource_contract()" in vm_text
            and "resource_contract" in vm_text
            and "read_stdlib_resource_bounded()" in vm_text
            and "importlib_resources.files" not in vm_text
            and "test_stdlib_resource_reader_rejects_oversize_budget" in _read("tests/test_stdlib_startup.py")
        ),
        "regex_hostcall_input_budget": (
            "DEFAULT_REGEX_HAYSTACK_MAX_BYTES" in host_regex_text
            and "def _preflight_search_args" in host_regex_text
            and "def _preflight_sub_args" in host_regex_text
            and "hostcall_regex_max_haystack_bytes" in host_regex_text
            and "hostcall_regex_max_pattern_bytes" in host_regex_text
            and "hostcall_regex_max_replacement_bytes" in host_regex_text
            and "self.hostcall_regex_max_haystack_bytes" in vm_text
            and "self.hostcall_regex_max_pattern_bytes" in vm_text
            and "self.hostcall_regex_max_replacement_bytes" in vm_text
        ),
        "regex_hostcall_timeout_worker": (
            "DEFAULT_REGEX_TIMEOUT_SECONDS" in host_regex_text
            and "if timeout > 0:" in host_regex_text
            and "return run_regex_worker(" in host_regex_text
            and "def run_regex_worker(" in regex_runtime_text
            and "DEFAULT_REGEX_WORKER_STARTUP_TIMEOUT_SECONDS"
            in regex_runtime_text
            and "def _wait_for_subprocess_ready(" in regex_runtime_text
            and 'return [executable, "-I", "-S", str(child), HANDSHAKE_ARGUMENT]'
            in regex_runtime_text
            and 'HANDSHAKE_ARGUMENT = "--handshake"' in regex_child_text
            and "process.communicate(input=encoded_request, timeout=timeout)"
            in regex_runtime_text
            and "process.kill()" in regex_runtime_text
            and "bounded_regex_spans(" in editor_search_text
            and "worker_routed = bool(not state.literal)" in editor_search_text
            and "bounded_regex_replacement_rows(" in editor_replace_text
            and 'if action == "re.search":' in regex_child_text
            and 'elif action == "re.spans":' in regex_child_text
            and 'elif action == "re.replace-rows":' in regex_child_text
            and "except RecursionError as exc:" in regex_child_text
            and "if _timeout_seconds(v) > 0:" in host_regex_text
            and "test_deep_pattern_compile_failure_is_classified_inside_worker"
            in _read("tests/test_regex_containment.py")
            and "test_editor_search_and_replace_do_not_compile_deep_regex_in_foreground"
            in _read("tests/test_regex_containment.py")
            and "test_positive_timeout_vm_search_and_sub_skip_foreground_regex_compile"
            in _read("tests/test_regex_containment.py")
            and "test_historical_highlight_helper_fails_closed_on_deep_regex_syntax"
            in _read("tests/test_regex_containment.py")
            and "test_catastrophic_regex_is_killed_at_wall_clock_deadline"
            in _read("tests/test_regex_containment.py")
            and "test_delayed_startup_does_not_consume_match_deadline"
            in _read("tests/test_regex_containment.py")
            and "test_startup_deadline_kills_child_that_never_becomes_ready"
            in _read("tests/test_regex_containment.py")
            and "test_compatibility_match_helper_cannot_reenter_local_backtracking"
            in _read("tests/test_regex_containment.py")
            and "self.hostcall_regex_timeout_seconds" in vm_text
        ),
        "editor_model_dimension_budget": (
            "DEFAULT_EDITOR_MODEL_MAX_LINES" in boundary_text
            and "DEFAULT_EDITOR_MODEL_MAX_CELLS" in boundary_text
            and "def require_editor_model_budget" in boundary_text
            and "def pop_model_dimensions_arg" in boundary_text
            and "def pop_model_width_arg" in boundary_text
            and "editor_hostcall_model_max_lines" in bridge_text
            and "pop_model_dimensions_arg(vm, \"ed.screen-rows\")" in bridge_text
            and "pop_model_dimensions_arg(vm, \"ed.docs-cues\")" in bridge_text
            and "pop_model_width_arg(vm, \"ed.bottom-rows\")" in bridge_text
            and "pop_model_lines_arg(vm, \"ed.prompt-window\")" in bridge_text
        ),
        "editor_query_input_budget": (
            "DEFAULT_EDITOR_QUERY_MAX_BYTES" in boundary_text
            and "def require_editor_query_budget" in boundary_text
            and "def pop_query_arg" in boundary_text
            and "editor_hostcall_query_max_bytes" in bridge_text
            and "pop_query_arg(vm, \"ed.doc-section-rows\")" in bridge_text
            and "pop_query_arg(vm, \"ed.command-palette-rows\")" in bridge_text
            and "peek_query_arg(vm, \"ed.find\")" in bridge_text
        ),
        "fs_read_preflight_byte_budget": (
            "DEFAULT_FS_READ_MAX_BYTES" in boundary_text
            and "def effective_fs_read_max_bytes" in boundary_text
            and "editor_hostcall_fs_read_max_bytes" in bridge_text
            and "effective_fs_read_max_bytes(vm)" in bridge_text
            and "def preflight_file_read_size_contained" in file_access_text
            and "preflight_file_read_size_contained(" in file_access_text
            and "read_file_bytes_contained(" in file_access_text
        ),
        "fs_read_timeout_worker": (
            "DEFAULT_FS_READ_TIMEOUT_SECONDS" in boundary_text
            and "def effective_fs_read_timeout_seconds" in boundary_text
            and "editor_hostcall_fs_read_timeout_seconds" in bridge_text
            and "effective_fs_read_timeout_seconds(vm)" in bridge_text
            and "class FilesystemOperationTimeoutError" in file_access_text
            and "def read_file_bytes_contained_bounded" in file_access_text
            and "filesystem read timed out after" in file_access_text
            and "read_file_bytes_contained_bounded(" in fs_hostcalls_text
        ),
        "editor_open_read_timeout_boundary": (
            "effective_fs_read_timeout_seconds" in editor_text
            and "effective_fs_stat_timeout_seconds" in editor_text
            and "timeout_seconds=effective_fs_read_timeout_seconds" in editor_text
            and "stat_path_contained_bounded(" in editor_text
            and "timeout_seconds: float | None = None" in file_recovery_text
            and "read_file_bytes_contained_bounded(" in file_recovery_text
            and "timeout_seconds=effective_fs_read_timeout_seconds(vm)" in bridge_text
            and "timeout_seconds=effective_fs_read_timeout_seconds(vm_arg)" in load_policy_text
        ),

        "fs_list_timeout_worker": (
            "DEFAULT_FS_LIST_TIMEOUT_SECONDS" in boundary_text
            and "def effective_fs_list_timeout_seconds" in boundary_text
            and "editor_hostcall_fs_list_timeout_seconds" in bridge_text
            and "effective_fs_list_timeout_seconds(vm)" in bridge_text
            and "class FilesystemOperationTimeoutError" in file_access_text
            and "def list_dir_contained_bounded" in file_access_text
            and "filesystem list timed out after" in file_access_text
            and "list_dir_contained_bounded(" in fs_hostcalls_text
        ),
        "fs_stat_timeout_worker": (
            "DEFAULT_FS_STAT_TIMEOUT_SECONDS" in boundary_text
            and "def effective_fs_stat_timeout_seconds" in boundary_text
            and "editor_hostcall_fs_stat_timeout_seconds" in bridge_text
            and "effective_fs_stat_timeout_seconds(vm)" in bridge_text
            and "class FilesystemOperationTimeoutError" in file_access_text
            and "def stat_path_contained_bounded" in file_access_text
            and "filesystem stat timed out after" in file_access_text
            and "stat_path_contained_bounded(" in fs_hostcalls_text
        ),
        "editor_scan_row_budget": (
            "DEFAULT_EDITOR_SCAN_MAX_ROWS" in boundary_text
            and "DEFAULT_FS_LIST_MAX_ROWS" in boundary_text
            and "def effective_editor_scan_max_rows" in boundary_text
            and "def effective_fs_list_max_rows" in boundary_text
            and "editor_hostcall_scan_max_rows" in bridge_text
            and "editor_hostcall_fs_list_max_rows" in bridge_text
            and "def _scan_limit" in bridge_text
            and "limit=_scan_limit()" in bridge_text
            and "effective_fs_list_max_rows(vm)" in bridge_text
            and "effective_editor_scan_max_rows" in editor_text
            and "os.scandir(fd)" in file_access_text
        ),
        "prompt_path_completion_scan_budget": (
            "scan_limit: int | None = None" in prompt_completion_text
            and "contained_limit = scan_cap if scan_cap is not None else max_items" in prompt_completion_text
            and "limit=contained_limit" in prompt_completion_text
            and "list_dir_contained_bounded(" in prompt_completion_text
            and "Path.iterdir" not in prompt_completion_text
            and "base.exists()" not in prompt_completion_text
            and "child.is_dir()" not in prompt_completion_text
            and "path_completion_candidates(" in editor_text
            and "scan_limit=scan_limit" in editor_text
            and "contained_limit = scan_limit if scan_limit is not None else 1000" in editor_text
        ),
        "prompt_path_completion_timeout_worker": (
            "timeout_seconds: float | None = None" in prompt_completion_text
            and "list_dir_contained_bounded(" in prompt_completion_text
            and "timeout_seconds=effective_fs_list_timeout_seconds" in editor_text
            and "list_dir_contained_bounded(" in editor_text
            and "def list_dir_contained_bounded" in file_access_text
            and "filesystem list timed out after" in file_access_text
        ),
        "editor_user_init_timeout_boundary": (
            "def load_user_init" in editor_text
            and "read_file_for_editor(" in editor_text
            and "self.vm.eval(str(disk.text), filename=str(disk.path or p))" in editor_text
            and "timeout_seconds=effective_fs_read_timeout_seconds" in editor_text
        ),
        "source_load_stat_timeout_boundary": (
            "def _source_candidate_stat" in load_policy_text
            and "stat_path_contained_bounded(" in load_policy_text
            and "effective_fs_stat_timeout_seconds" in load_policy_text
            and "_source_candidate_stat(vm, cand, root)" in load_policy_text
        ),
        "editor_atomic_write_timeout_boundary": (
            "DEFAULT_FILE_WRITE_TIMEOUT_SECONDS" in boundary_text
            and "def effective_file_write_timeout_seconds" in boundary_text
            and "editor_file_write_timeout_seconds" in bridge_text
            and _function_routes_call_result_to_keywords(
                editor_path,
                class_name="Editor",
                function_name="_save_buffer",
                producer_name="effective_file_write_timeout_seconds",
                sink_names={"plan_atomic_write_bounded", "write_file_bytes"},
                keyword_name="timeout_seconds",
            )
            and "timeout_seconds=effective_file_write_timeout_seconds" in (ROOT / "src" / "micromax_editor" / "persist_io.py").read_text(encoding="utf-8", errors="replace")
            and "class FileWriteTimeoutError" in file_write_text
            and "def _write_file_bytes_bounded" in file_write_text
            and "filesystem write timed out after" in file_write_text
            and "_cleanup_atomic_write_temps_for_worker" in file_write_text
            and _function_docstring_contains(
                file_write_path,
                "write_file_bytes",
                "Direct writes",
                "remain in-process",
                "partially written",
            )
        ),
        "editor_save_freshness_timeout_boundary": (
            "DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS" in boundary_text
            and "DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS" in boundary_text
            and "def effective_file_freshness_timeout_seconds" in boundary_text
            and "def effective_file_mkparents_timeout_seconds" in boundary_text
            and "editor_file_freshness_timeout_seconds" in bridge_text
            and "editor_file_mkparents_timeout_seconds" in bridge_text
            and "capture_file_freshness_bounded(" in editor_text
            and "ensure_parent_directory_bounded(" in editor_text
            and "include_hash" in editor_text
            and "class FileFreshnessTimeoutError" in file_write_text
            and "class FileMkparentsTimeoutError" in file_write_text
            and "def capture_file_freshness_bounded" in file_write_text
            and "def ensure_parent_directory_bounded" in file_write_text
            and "filesystem freshness check timed out after" in file_write_text
            and "filesystem parent creation timed out after" in file_write_text
            and "_capture_file_freshness_worker" in file_write_text
            and "_ensure_parent_directory_worker" in file_write_text
            and "st = self._bounded_fs_stat(p" in editor_text
        ),
        "editor_disk_state_cache_boundary": (
            "diskstate.cachems" in options_text
            and "diskstate.refreshms" in options_text
            and "disk_state_cache" in editor_text
            and "def invalidate_disk_state_cache" in editor_text
            and "def _disk_state_refresh_seconds" in editor_text
            and "refresh_at" in editor_text
            and "disk_status_stale" in editor_text
            and "_seed_fresh_disk_state_cache_from_signature" in editor_text
            and "refresh: bool = False" in editor_text
            and "state = self.buffer_disk_state(eb, refresh=True)" in editor_text
            and "disk_state = self.buffer_disk_state(eb)" in editor_text
            and "def _status_file_readonly" in editor_text
            and "ed._bounded_fs_stat(nominal, containment_root=containment_root)" in file_scriptops_text
        ),

        "worker_result_frame_deadline_boundary": (
            "class WorkerResultSender" in worker_process_text
            and "class WorkerResultChannel" in worker_process_text
            and "socket.socketpair()" in worker_process_text
            and "_WORKER_RESULT_HEADER = struct.Struct(\"!4sQ\")" in worker_process_text
            and "select.select([sock]" in worker_process_text
            and "if expected > max_bytes" in worker_process_text
            and "pickle.Unpickler(stream).load()" in worker_process_text
            and "def create_one_shot_worker" in worker_process_text
            and "def collect_worker_result" in worker_process_text
            and "channel.close_parent_sender()" in worker_process_text
            and "test_worker_result_channel_round_trips_payload_larger_than_socket_buffer"
            in _read("tests/test_worker_process.py")
            and "test_partial_worker_frame_cannot_outlive_parent_deadline"
            in _read("tests/test_worker_process.py")
            and "test_oversized_declared_result_is_rejected_before_body_read"
            in _read("tests/test_worker_process.py")
            and "test_invalid_or_trailing_pickle_data_fails_closed"
            in _read("tests/test_worker_process.py")
            and "test_worker_crash_is_classified_from_eof_without_spending_deadline"
            in _read("tests/test_worker_process.py")
            and "Queue(maxsize=1)" not in file_access_text
            and "Queue(maxsize=1)" not in file_write_text
            and "Queue(maxsize=1)" not in manager_text
            and "Queue(maxsize=1)" not in docs_index_text
            and "Queue(maxsize=1)" not in project_files_text
            and "create_one_shot_worker(" in regex_runtime_text
            and "collect_worker_result(" in regex_runtime_text
            and "context.Pipe(" not in regex_runtime_text
            and "parent_conn.recv()" not in regex_runtime_text
            and "_FILE_WRITE_RESULT_MAX_BYTES" in file_write_text
            and "max_result_bytes=_FILE_WRITE_RESULT_MAX_BYTES" in file_write_text
            and "test_injected_multiprocessing_regex_adapter_uses_full_frame_channel"
            in _read("tests/test_regex_containment.py")
        ),
        "worker_start_deadline_boundary": (
            "DEFAULT_WORKER_START_TIMEOUT_SECONDS = 5.0" in worker_process_text
            and "class WorkerResultStartTimeoutError" in worker_process_text
            and "class _DeferredWorkerProcess" in worker_process_text
            and "class _WorkerStartAttempt" in worker_process_text
            and "_WORKER_START_GATE = threading.Lock()" in worker_process_text
            and "startup_timeout_seconds" in worker_process_text
            and "self._completed_at" in worker_process_text
            and "self._caller_owns = False" in worker_process_text
            and "worker cannot use fork with a deadline-owned" in worker_process_text
            and "process_thread_count" not in worker_process_text
            and "test_blocked_worker_construction_times_out_and_late_child_is_reclaimed"
            in _read("tests/test_worker_process.py")
            and "test_blocked_process_start_times_out_without_leaking_caller_ownership"
            in _read("tests/test_worker_process.py")
            and "test_startup_budget_is_one_absolute_deadline_across_gate_and_start"
            in _read("tests/test_worker_process.py")
            and "test_start_completion_after_absolute_deadline_is_not_accepted"
            in _read("tests/test_worker_process.py")
            and "test_deadline_owned_starter_rejects_explicit_fork_context"
            in _read("tests/test_worker_process.py")
        ),
        "filesystem_worker_result_drain_boundary": (
            "def _collect_filesystem_worker_result" in file_access_text
            and "collect_worker_result(" in file_access_text
            and "create_one_shot_worker(" in file_access_text
            and "WorkerResultTimeoutError" in file_access_text
            and "WorkerResultTooLargeError" in file_access_text
            and "queue.get(" not in file_access_text
            and "test_direct_filesystem_worker_api_replaces_infinite_deadline"
            in _read("tests/test_worker_process.py")
            and "test_worker_crash_is_classified_from_eof_without_spending_deadline"
            in _read("tests/test_worker_process.py")
        ),
        "large_buffer_dirty_tracking_boundary": (
            "FASTDIRTY_AUTO_BYTES = 1024 * 1024" in buffer_text
            and "_SIGNATURE_CHUNK_CHARS = 64 * 1024" in buffer_text
            and "return self._text_signature(self.get_text())" in buffer_text
            and "for start in range(0, len(value), _SIGNATURE_CHUNK_CHARS)" in buffer_text
            and "def baseline_byte_size" in buffer_text
            and "buf.baseline_byte_size >= FASTDIRTY_AUTO_BYTES" in editor_text
            and 'local_options["fastdirty"] = True' in editor_text
            and "test_bounded_encoded_buffer_signature_matches_canonical_lf_text"
            in _read("tests/test_editor_fastdirty.py")
            and "test_large_buffer_auto_fastdirty_is_visible_and_reversible"
            in _read("tests/test_editor_fastdirty.py")
            and "test_buffer_below_auto_fastdirty_threshold_remains_exact"
            in _read("tests/test_editor_fastdirty.py")
        ),
        "palette_recent_stat_batch_boundary": (
            "def stat_paths_contained_bounded" in file_access_text
            and "filesystem stat batch timed out after" in file_access_text
            and "_palette_fs_stat_cache" in editor_text
            and "def _seed_palette_fs_stat_cache" in editor_text
            and "stat_paths_contained_bounded(" in editor_text
            and "self._seed_palette_fs_stat_cache(str(raw) for raw in visible)" in editor_text
            and "known_raws: list[str]" in editor_text
            and "known-path completion should use the preseeded batch cache" in _read("tests/test_command_palette_path_completion.py")
        ),
        "status_readonly_parsecursor_bounded": (
            "class ContainedAccessResult" in file_access_text
            and "def access_path_contained_bounded" in file_access_text
            and "filesystem access timed out after" in file_access_text
            and "access_path_contained_bounded(" in editor_text
            and "self._bounded_fs_stat(literal, containment_root=fs_sandbox_root(self))" in editor_text
            and "use_palette_stat_cache: bool = False" in editor_text
            and "st = self._palette_fs_stat_cache.get(key)" in editor_text
            and "test_status_readonly_refresh_uses_bounded_access_probe" in _read("tests/test_editor_fs_open_save.py")
            and "test_parsecursor_existing_literal_path_uses_bounded_stat" in _read("tests/test_editor_fs_open_save.py")
            and "test_parsecursor_palette_literal_check_uses_preseeded_stat_cache" in _read("tests/test_editor_fs_open_save.py")
            and "stat_path_contained(literal)" not in editor_text
            and "p.exists() and (not p.is_dir()) and (not os.access" not in editor_text
        ),
        "process_capture_pipe_owner_boundary": (
            "def _join_threads_until" in host_process_text
            and "def _process_pipe_ids" in host_process_text
            and "def _linux_pipe_holder_pids" in host_process_text
            and "def _linux_pid_start_time" in host_process_text
            and "def _signal_pipe_holder_pid" in host_process_text
            and "pidfd_open" in host_process_text
            and "pidfd_send_signal" in host_process_text
            and "def _terminate_lingering_capture_owners" in host_process_text
            and "micromax-process-stdout" in host_process_text
            and "micromax-process-stderr" in host_process_text
            and "test_run_argv_bounded_kills_background_descendant_holding_capture_pipes"
            in _read("tests/test_editor_host_process.py")
            and "test_run_argv_bounded_kills_new_session_descendant_holding_capture_pipes"
            in _read("tests/test_editor_host_process.py")
            and "test_run_argv_bounded_leaves_stdio_detached_background_descendant_alive"
            in _read("tests/test_editor_host_process.py")
            and "test_run_argv_bounded_preserves_detached_sibling_of_capture_pipe_holder"
            in _read("tests/test_editor_host_process.py")
            and "test_exact_pipe_holder_signal_uses_pidfd_identity"
            in _read("tests/test_editor_host_process.py")
            and "test_exact_linux_cleanup_does_not_broaden_empty_scan_to_process_group"
            in _read("tests/test_editor_host_process.py")
            and "test_bounded_shell_success_reaps_background_pipe_owner"
            in _read("tests/test_editor_shell_hostcall_budget.py")
        ),
        "shell_output_timeout_budget": (
            "DEFAULT_SHELL_COMMAND_MAX_BYTES" in boundary_text
            and "DEFAULT_SHELL_OUTPUT_MAX_BYTES" in boundary_text
            and "DEFAULT_SHELL_TIMEOUT_SECONDS" in boundary_text
            and "def pop_shell_command_arg" in boundary_text
            and "def effective_shell_output_max_bytes" in boundary_text
            and "def effective_shell_timeout_seconds" in boundary_text
            and "editor_shell_command_max_bytes" in bridge_text
            and "run_shell_command_bounded(" in bridge_text
            and "class ShellCommandResult" in host_process_text
            and "def run_shell_command_bounded" in host_process_text
            and "def _capture_started_process" in host_process_text
            and "def _join_threads_until" in host_process_text
            and "def _linux_pipe_holder_pids" in host_process_text
            and "def _terminate_lingering_capture_owners" in host_process_text
            and "terminate_process_tree(" in host_process_text
            and 'output_budget_name="shell output budget"' in host_process_text
            and "test_bounded_shell_success_reaps_background_pipe_owner"
            in _read("tests/test_editor_shell_hostcall_budget.py")
            and "test_run_argv_bounded_kills_background_descendant_holding_capture_pipes"
            in _read("tests/test_editor_host_process.py")
            and "test_run_argv_bounded_kills_new_session_descendant_holding_capture_pipes"
            in _read("tests/test_editor_host_process.py")
            and "test_run_argv_bounded_releases_blocked_stdin_writer_after_parent_exit"
            in _read("tests/test_editor_host_process.py")
        ),
        "external_clipboard_process_budget": (
            "class BoundedProcessResult" in host_process_text
            and "def run_argv_bounded" in host_process_text
            and "def _capture_started_process" in host_process_text
            and 'output_budget_name="process output budget"' in host_process_text
            and "clipboard.external.inputmax" in options_text
            and "clipboard.external.outputmax" in options_text
            and "clipboard.external.inputmax" in option_policy_text
            and "clipboard.external.outputmax" in option_policy_text
            and "run_argv_bounded(" in editor_text
            and "clipboard export too large" in editor_text
            and "clipboard read tool" in editor_text
        ),
        "open_url_process_timeout_boundary": (
            "DEFAULT_OPEN_URL_TIMEOUT_SECONDS" in open_url_process_text
            and "def open_external_url_bounded" in open_url_process_text
            and "run_argv_bounded(" in open_url_process_text
            and '"-I"' in open_url_process_text
            and '"-S"' in open_url_process_text
            and "webbrowser.open(url, new=2)" in open_url_child_text
            and "def _browser_stdio_detached" in open_url_child_text
            and "open_external_url_bounded(" in editor_text
            and "self._open_url_fn = None" in editor_text
            and "test_open_url_hostcall_times_out_browser_process_and_keeps_vm_live"
            in _read("tests/test_editor_open_url_process.py")
            and "test_successful_background_browser_does_not_inherit_capture_pipes"
            in _read("tests/test_editor_open_url_process.py")
            and "test_open_url_parent_deadline_contains_desktop_controller_discovery"
            in _read("tests/test_editor_open_url_process.py")
        ),
        "finite_worker_deadline_normalization": (
            "def normalize_worker_timeout_seconds" in worker_process_text
            and "math.isfinite(parsed)" in worker_process_text
            and "normalize_worker_timeout_seconds(join_timeout" in worker_process_text
            and "normalize_worker_timeout_seconds(timeout_seconds" in worker_process_text
            and "def _finite_timeout_seconds" in host_process_text
            and "math.isfinite(parsed)" in host_process_text
            and "def _optional_positive_float_limit" in boundary_text
            and "normalize_worker_timeout_seconds(" in file_access_text
            and "def _collect_filesystem_worker_result" in file_access_text
            and "collect_worker_result(" in file_access_text
            and "test_direct_filesystem_worker_api_replaces_infinite_deadline"
            in _read("tests/test_worker_process.py")
            and "test_worker_crash_is_classified_from_eof_without_spending_deadline"
            in _read("tests/test_worker_process.py")
            and "test_partial_worker_frame_cannot_outlive_parent_deadline"
            in _read("tests/test_worker_process.py")
            and "normalize_worker_timeout_seconds(" in file_write_text
            and "normalize_worker_timeout_seconds(" in manager_text
            and "collect_worker_result(" in file_write_text
            and "collect_worker_result(" in manager_text
            and "test_public_atomic_writer_replaces_infinite_deadline"
            in _read("tests/test_file_write_worker_lifecycle.py")
            and "test_plugin_worker_collector_replaces_infinite_deadline"
            in _read("tests/test_plugin_package_fingerprint_budgets.py")
        ),
        "source_load_eval_budget": (
            "DEFAULT_SOURCE_LOAD_MAX_BYTES" in boundary_text
            and "DEFAULT_SOURCE_EVAL_STEP_BUDGET" in boundary_text
            and "def effective_source_load_max_bytes" in boundary_text
            and "def effective_source_eval_step_budget" in boundary_text
            and "editor_source_load_max_bytes" in bridge_text
            and "editor_source_eval_step_budget" in bridge_text
            and "max_bytes=effective_source_load_max_bytes(vm)" in bridge_text
            and "step_budget=effective_source_eval_step_budget(vm)" in bridge_text
            and "max_bytes=effective_source_load_max_bytes(vm_arg)" in load_policy_text
            and "editor_source_eval_step_budget" in core_text
        ),
        "source_load_graph_budget": (
            "DEFAULT_SOURCE_LOAD_MAX_DEPTH" in boundary_text
            and "DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES" in boundary_text
            and "def effective_source_load_max_depth" in boundary_text
            and "def effective_source_load_max_total_bytes" in boundary_text
            and "editor_source_load_max_depth" in bridge_text
            and "editor_source_load_max_total_bytes" in bridge_text
            and 'source_load_graph_frame(vm, \"ed.require\"' in bridge_text
            and 'source_load_record_bytes(vm, \"ed.require\"' in bridge_text
            and "def source_load_graph_frame" in core_text
            and "def source_load_record_bytes" in core_text
            and 'source_load_graph_frame(vm, \"include\"' in core_text
            and 'source_load_graph_frame(vm, \"require\"' in core_text
            and 'source_load_graph_frame(vm, \"reload\"' in core_text
        ),
        "plugin_package_fingerprint_budgets": (
            "PLUGIN_PACKAGE_MAX_FILES" in plugin_package_text
            and "PLUGIN_PACKAGE_MAX_TOTAL_BYTES" in plugin_package_text
            and "package_fingerprint_max_files" in manager_text
            and "package_fingerprint_max_total_bytes" in manager_text
            and "plugin fingerprint: too many files" in plugin_package_text
            and "plugin fingerprint: package too large" in plugin_package_text
        ),
        "plugin_optional_meta_exists_contained": (
            'meta_path = root / "plugin.json"' in plugin_meta_text
            and "plugin_file_exists(meta_path, root)" in plugin_meta_text
            and "meta_path.exists()" not in plugin_meta_text
            and "except FileContainmentError as e:" in plugin_io_text
            and "cannot be silently bypassed" in plugin_io_text
            and "test_optional_plugin_json_absence_uses_contained_probe" in _read("tests/test_plugin_json_schema.py")
            and "test_plugin_json_symlink_escape_is_not_read" in _read("tests/test_plugin_containment_and_caps.py")
        ),
        "plugin_discovery_fingerprint_timeout_boundary": (
            "PLUGIN_DISCOVERY_TIMEOUT_SECONDS" in manager_text
            and "PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS" in manager_text
            and "plugin_discovery_timeout_seconds" in manager_text
            and "package_fingerprint_timeout_seconds" in manager_text
            and "def _candidate_directories" in manager_text
            and "list_dir_contained_bounded(" in manager_text
            and "def plugin_package_fingerprint_worker" in plugin_package_text
            and "def plugin_package_snapshot_worker" in plugin_package_text
            and "target=_plugin_package_fingerprint_worker" in manager_text
            and "target=_plugin_package_snapshot_worker" in manager_text
            and "create_one_shot_worker(" in manager_text
            and "collect_worker_result(" in manager_text
            and 'f"{operation} timed out after' in manager_text
            and 'operation="plugin fingerprint"' in manager_text
            and 'operation="plugin snapshot"' in manager_text
            and "test_plugin_discovery_uses_bounded_list_probe" in _read("tests/test_plugin_package_fingerprint_budgets.py")
            and "test_plugin_snapshot_timeout_worker_fails_closed" in _read("tests/test_plugin_package_fingerprint_budgets.py")
            and "test_plugin_worker_missing_frame_terminates_child_and_closes_channel" in _read("tests/test_plugin_package_fingerprint_budgets.py")
            and "rootp.iterdir()" not in manager_text
        ),
        "docs_catalog_scan_timeout_boundary": (
            "DOCS_SCAN_TIMEOUT_SECONDS" in docs_index_text
            and "DOCS_SCAN_MAX_FILES" in docs_index_text
            and "DOCS_SCAN_MAX_FILE_BYTES" in docs_index_text
            and "def _docs_scan_worker" in docs_index_text
            and "target=_docs_scan_worker" in docs_index_text
            and "create_one_shot_worker(" in docs_index_text
            and "collect_worker_result(" in docs_index_text
            and "docs catalog scan timed out after" in docs_index_text
            and "list_dir_contained(" in docs_index_text
            and "read_file_prefix_contained(" in docs_index_text
            and "def read_file_prefix_contained" in file_access_text
            and "scan_docs`` uses bounded scan records" in docs_index_text
            and "reviving ambient ``Path.read_text``" in docs_index_text
            and "txt = path.read_text" not in docs_index_text
            and "def _large_docs_fingerprint_is_fresh" in docs_index_text
            and "record_cached = _DOC_RECORD_CACHE.get(key)" in docs_index_text
            and "test_scan_docs_avoids_direct_glob_and_read_text" in _read("tests/test_docs_index.py")
            and "test_private_scan_doc_file_uses_contained_prefix_read" in _read("tests/test_docs_index.py")
            and "test_scan_docs_uses_prefix_budget_without_dropping_large_docs" in _read("tests/test_docs_index.py")
            and "test_scan_docs_reuses_recent_large_scan_records_between_token_and_rows" in _read("tests/test_docs_index.py")
        ),
        "help_doc_read_timeout_boundary": (
            "def _read_help_doc_text" in editor_text
            and "read_file_bytes_contained_bounded(" in editor_text
            and "max_bytes=int(DOCS_SCAN_MAX_FILE_BYTES)" in editor_text
            and "def _docs_containment_root" in editor_text
            and "self._bounded_fs_stat(" in editor_text
            and "def _contained_doc_path_from_explicit_target" in editor_text
            and "Path(path).read_text(encoding=\"utf-8\")" not in editor_text
            and "if not resolved.is_file()" not in editor_text
            and "cand.exists() and cand.is_file()" not in editor_text
            and "test_help_doc_open_uses_bounded_read_not_path_read_text" in _read("tests/test_editor_help_docs_boundary.py")
            and "test_help_explicit_path_and_relative_follow_avoid_direct_is_file" in _read("tests/test_editor_help_docs_boundary.py")
            and "test_help_target_heading_titles_use_bounded_read_not_path_read_text" in _read("tests/test_editor_help_docs_boundary.py")
        ),
        "project_root_marker_batch_boundary": (
            "class ProjectRootLocator" in project_files_text
            and "PROJECT_ROOT_MARKERS" in project_files_text
            and "PROJECT_ROOT_MARKER_BATCH_LIMIT" in project_files_text
            and "PROJECT_ROOT_CACHE_TTL_SECONDS" in project_files_text
            and "stat_paths_contained_bounded(" in project_files_text
            and "worker_context=isolated_filesystem_worker_context()" in project_files_text
            and "self._project_roots = ProjectRootLocator()" in editor_text
            and "return self._project_roots.root_for_path(" in editor_text
            and "p.is_file() else p" not in editor_text
            and "(cur / '.git').exists()" not in editor_text
            and "(cur / 'pyproject.toml').exists()" not in editor_text
            and "test_project_root_detection_uses_bounded_marker_batch" in _read("tests/test_editor_buffer_lifecycle_recent.py")
            and "test_recent_project_rows_seed_project_root_cache_once" in _read("tests/test_editor_buffer_lifecycle_recent.py")
        ),
        "bounded_project_file_picker_boundary": (
            "class ProjectFileScanLimits" in project_files_text
            and "class ProjectFileScan" in project_files_text
            and "def scan_project_files(" in project_files_text
            and "isolated_filesystem_worker_context()" in project_files_text
            and "O_NOFOLLOW" in project_files_text
            and "hard_exhausted" in project_files_text
            and "create_one_shot_worker(" in project_files_text
            and "collect_worker_result(" in project_files_text
            and "WorkerResultTimeoutError" in project_files_text
            and "queue.get(" not in project_files_text
            and "DEFAULT_PROJECT_FILE_MAX_FILES" in boundary_text
            and "effective_project_file_timeout_seconds" in boundary_text
            and "editor_project_file_max_files" in bridge_text
            and "editor_project_file_timeout_seconds" in bridge_text
            and "picker_root: str" in commandbar_text
            and "picker_items: list[str]" in commandbar_text
            and "picker_meta: dict[str, object]" in commandbar_text
            and "def enter_file_prompt(" in editor_text
            and "cap.fs-list" in editor_text
            and "def _submit_project_file_prompt(" in editor_text
            and "cap.fs-open" in editor_text
            and "snapshot path now traverses a symlink" in editor_text
            and "def a_file_picker(" in actions_text
            and '"FilePicker"' in actions_text
            and '"filepick"' in dispatcher_text
            and "def c_filepick(" in picker_commands_text
            and '"filepicker.hidden"' in options_text
            and "key='Ctrl-o', action_spec='FilePicker'" in default_keybindings_text
            and '"Ctrl-o" "FilePicker" "ed.bind" hostcall' in core_plugin_text
            and "test_scan_is_deterministic_hidden_aware_and_never_follows_symlinks" in project_picker_tests_text
            and "test_depth_truncation_does_not_disable_a_later_terminal_entry_budget" in project_picker_tests_text
            and "test_script_bound_picker_cannot_borrow_later_interactive_open_authority" in project_picker_tests_text
            and "test_prompt_lifecycle_snapshot_detaches_project_inventory" in project_picker_tests_text
            and "test_scan_timeout_is_transactional_and_leaves_no_partial_snapshot" in project_picker_tests_text
            and "test_scan_accepts_one_complete_framed_worker_snapshot" in project_picker_tests_text
        ),
    }



def _effect_contract_metrics(*, current_rev: int | None, runtime_group_policy: dict[str, Any]) -> dict[str, Any]:
    try:
        from micromax_editor.effect_contracts import (
            EFFECT_CONTRACT_HELP_DOC,
            effect_contract_help_markdown,
            effect_resource_contract,
            validate_effect_resource_contract,
        )
    except Exception as e:
        return {
            "schema": "micromax.effect-contract-audit.v1",
            "present": False,
            "ok": False,
            "row_count": 0,
            "errors": [f"could not import effect contract generator: {e}"],
        }
    audit_payload = {"runtime_group_policy": runtime_group_policy}
    try:
        contract = effect_resource_contract(rev=current_rev, audit_payload=audit_payload)
        errors = validate_effect_resource_contract(contract)
        generated_help = effect_contract_help_markdown(contract)
    except Exception as e:
        return {
            "schema": "micromax.effect-contract-audit.v1",
            "present": True,
            "ok": False,
            "row_count": 0,
            "errors": [f"could not generate effect contract: {e}"],
        }
    rows = contract.get("rows") if isinstance(contract, dict) else []
    names = [str(row.get("name")) for row in rows if isinstance(row, dict) and row.get("name")]
    help_doc_path = ROOT / EFFECT_CONTRACT_HELP_DOC
    current_help = help_doc_path.read_text(encoding="utf-8") if help_doc_path.exists() else ""
    manifest = _manifest_rows()
    help_doc_present = help_doc_path.is_file()
    help_doc_installed = EFFECT_CONTRACT_HELP_DOC in manifest
    help_doc_matches_generated = bool(current_help) and current_help == generated_help
    help_errors = []
    if not help_doc_present:
        help_errors.append(f"missing generated help doc: {EFFECT_CONTRACT_HELP_DOC}")
    if not help_doc_installed:
        help_errors.append(f"generated help doc is absent from installed help: {EFFECT_CONTRACT_HELP_DOC}")
    if not help_doc_matches_generated:
        help_errors.append(f"generated help doc is stale: {EFFECT_CONTRACT_HELP_DOC}")
    all_errors = [*errors, *help_errors]
    return {
        "schema": "micromax.effect-contract-audit.v1",
        "present": True,
        "ok": not all_errors,
        "row_count": int(contract.get("row_count") or 0),
        "names": names,
        "errors": all_errors,
        "help_doc_path": EFFECT_CONTRACT_HELP_DOC,
        "help_doc_present": help_doc_present,
        "help_doc_installed": help_doc_installed,
        "help_doc_matches_generated": help_doc_matches_generated,
    }



def _release_suite_manifest_rows(release_manifests: list[str]) -> list[dict[str, Any]]:
    """Describe carried full-suite evidence without turning partial work into failure.

    A runnable release lane and a completed, current receipt are different facts.
    Keep partial checkpoints useful, but make source/test drift, completeness, and
    passing state visible to humans and machine consumers of ``mxaudit``.
    """

    if not release_manifests:
        return []
    try:
        current_source = mxrelease.source_manifest_payload()
        current_test_files = mxrelease.discover_test_files()
    except Exception as exc:
        return [
            {
                "path": rel,
                "schema": None,
                "status": "unreadable",
                "complete": False,
                "ok": False,
                "current": False,
                "source_current": False,
                "test_inventory_current": False,
                "internally_consistent": False,
                "issue_count": 1,
                "issues": [f"could not compute current release inventory: {exc}"],
                "batch_status_counts": {},
                "test_status_counts": {},
                "pytest_counts": {},
                "test_batch_count": 0,
                "test_file_count": 0,
                "source_digest": None,
            }
            for rel in release_manifests
        ]

    rows: list[dict[str, Any]] = []
    current_issue_prefixes = (
        "batches do not match current ",
        "test_files do not match current ",
        "source_digest does not match current ",
    )
    for rel in release_manifests:
        manifest_path = ROOT / rel
        try:
            payload = mxrelease.load_manifest(manifest_path)
        except (OSError, UnicodeError, json.JSONDecodeError, SystemExit) as exc:
            payload = None
            load_issue = f"could not load release manifest: {exc}"
        else:
            load_issue = "release manifest is absent" if payload is None else ""

        if payload is None:
            issues = [load_issue]
            rows.append(
                {
                    "path": rel,
                    "schema": None,
                    "status": "unreadable",
                    "complete": False,
                    "ok": False,
                    "current": False,
                    "source_current": False,
                    "test_inventory_current": False,
                    "internally_consistent": False,
                    "issue_count": len(issues),
                    "issues": issues,
                    "batch_status_counts": {},
                    "test_status_counts": {},
                    "pytest_counts": {},
                    "test_batch_count": 0,
                    "test_file_count": 0,
                    "source_digest": None,
                }
            )
            continue

        batches_obj = payload.get("batches")
        batches = (
            [row for row in batches_obj if isinstance(row, dict)]
            if isinstance(batches_obj, list)
            else []
        )
        try:
            issues = mxrelease.manifest_issues(payload, current_source=current_source)
        except (Exception, SystemExit) as exc:
            issues = [f"release manifest inspection failed: {exc}"]
        source_current = payload.get("source_digest") == current_source.get("digest")
        test_inventory_current = (
            payload.get("test_files") == current_test_files
            and mxrelease.flatten_batch_files(batches) == current_test_files
        )
        internal_issues = [
            issue
            for issue in issues
            if not str(issue).startswith(current_issue_prefixes)
        ]
        batch_counts = mxrelease.status_counts_for_batches(batches)
        file_counts = mxrelease.status_counts_for_files(batches)
        pytest_counts = mxrelease.aggregate_pytest_counts(batches)
        rows.append(
            {
                "path": rel,
                "schema": payload.get("schema"),
                "status": str(payload.get("status") or "unknown"),
                "complete": payload.get("complete") is True,
                "ok": payload.get("ok") is True,
                "current": bool(source_current and test_inventory_current),
                "source_current": bool(source_current),
                "test_inventory_current": bool(test_inventory_current),
                "internally_consistent": not internal_issues,
                "issue_count": len(issues),
                "issues": list(issues),
                "batch_status_counts": batch_counts,
                "test_status_counts": file_counts,
                "pytest_counts": pytest_counts,
                "test_batch_count": len(batches),
                "test_file_count": len(mxrelease.flatten_batch_files(batches)),
                "source_digest": payload.get("source_digest"),
            }
        )
    return rows


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
    release_manifests = sorted(
        _relative(path)
        for path in _files(artifacts_root)
        if path.name.startswith("mxrelease-full-suite") and path.suffix == ".json"
    )
    release_evidence_rows = _release_suite_manifest_rows(release_manifests)
    makefile = _read("Makefile")
    context = _read("tools/mxcontext.py")
    timely_text = _read("tools/mxtimely.py")
    timely_tests = _read("tests/test_mxtimely.py")
    mkrevzip_text = _read("tools/mkrevzip.py")
    mkrevzip_tests = _read("tests/test_mkrevzip.py")
    mxbuilder_text = _read("tools/mxbuilder.py")
    workflow_text = _read(".github/workflows/reproducible-release.yml")

    shared_toolrun_present = (
        (ROOT / "tools" / "mxtoolrun.py").is_file()
        and "from mxtoolrun import" in _read("tools/mxtimely.py")
        and "from mxtoolrun import" in _read("tools/mxrelease.py")
    )
    timely_present = (
        (ROOT / "tools" / "mxtimely.py").is_file()
        and shared_toolrun_present
        and "timely:" in makefile
        and "make timely" in context
    )
    timely_summary_incremental = (
        'summary_path = str(args.summary_json or "")' in timely_text
        and "Persist after each bounded child" in timely_text
        and "previous revision's summary" in timely_text
        and timely_text.count("write_summary(summary_path, results, planned_steps=steps)") >= 2
        and "test_main_writes_summary_after_each_step_before_interruption" in timely_tests
    )
    timely_summary_completion_honest = (
        '"schema": "micromax.mxtimely.summary.v3"' in timely_text
        and '"status": status' in timely_text
        and '"complete": bool(complete)' in timely_text
        and '"planned_steps": planned_names' in timely_text
        and '"pending_steps": planned_names[len(results) :]' in timely_text
        and "without making a completed-lane success claim" in timely_text
        and "test_write_summary_marks_incomplete_prefix_partial" in timely_tests
        and 'payload["ok"] is False' in timely_tests
        and 'payload["status"] == "partial"' in timely_tests
    )
    full_suite_runway_present = (
        (ROOT / "tools" / "mxrelease.py").is_file()
        and shared_toolrun_present
        and "release-suite:" in makefile
        and "release-verify:" in makefile
        and "release-next:" in makefile
        and "make release-suite" in context
        and "make release-verify" in context
        and "make release-next" in context
    )
    mkrevzip_provenance_present = (
        "ARCHIVE_PROVENANCE_SCHEMA" in mkrevzip_text
        and "def archive_member_rows" in mkrevzip_text
        and "def archive_member_provenance" in mkrevzip_text
        and 'archive["provenance"] = provenance' in mkrevzip_text
        and "test_mkrevzip_embeds_archive_member_provenance" in mkrevzip_tests
    )
    mkrevzip_verifier_present = (
        "ARCHIVE_VERIFICATION_SCHEMA" in mkrevzip_text
        and "class ArchiveVerificationError" in mkrevzip_text
        and "def verify_archive" in mkrevzip_text
        and "zf.testzip()" in mkrevzip_text
        and "DEFAULT_VERIFY_MAX_UNCOMPRESSED_BYTES" in mkrevzip_text
        and "--verify-archive" in mkrevzip_text
        and "verify_archive(candidate" in mkrevzip_text
        and "revzip-verify:" in makefile
        and "test_mkrevzip_verifies_generated_archive" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_member_digest_mismatch" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_duplicate_members" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_unsafe_members" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_uncompressed_budget_overflow" in mkrevzip_tests
    )
    mkrevzip_revision_lineage_present = (
        "class RevisionLineageError" in mkrevzip_text
        and "def parse_archive_name" in mkrevzip_text
        and "def _revision_evidence" in mkrevzip_text
        and "def _archive_revision_lineage" in mkrevzip_text
        and "requested revision" in mkrevzip_text
        and "tempfile.TemporaryDirectory" in mkrevzip_text
        and "os.replace(candidate, outpath)" in mkrevzip_text
        and "test_infer_rev_rejects_disagreeing_repository_breadcrumbs" in mkrevzip_tests
        and "test_mkrevzip_rev_argument_is_assertion_not_override" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_filename_context_revision_alias" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_archived_source_revision_mismatch" in mkrevzip_tests
        and "test_mkrevzip_rejects_noncanonical_archive_tag_before_writing" in mkrevzip_tests
        and 'name.split("/")' in mkrevzip_text
        and "ZoneInfo(timezone_name)" in mkrevzip_text
        and "test_unsafe_member_reason_rejects_raw_path_aliases" in mkrevzip_tests
        and "test_mkrevzip_verifier_rejects_invalid_manifest_timezone" in mkrevzip_tests
        and "test_mkrevzip_rejects_invalid_timezone_before_writing" in mkrevzip_tests
    )

    # Consume the executable package-input report instead of inferring policy
    # from duplicated strings and historical test names.  This closes the stale
    # rev0995 audit seam that still expected "unlocked-dev-only" after the
    # release path had moved to a hash-locked builder.
    try:
        package_inputs = mxrelease.package_input_report(ROOT)
    except Exception as exc:  # audit output should report, not crash
        package_inputs = {"ok": False, "issues": [f"package input report failed: {exc}"]}
    package_input_policy_present = (
        package_inputs.get("ok") is True
        and package_inputs.get("dependency_policy")
        == mxrelease.PACKAGE_INPUT_POLICY_HASH_LOCKED_BUILDER
        and package_inputs.get("package_version_policy")
        == mxrelease.PACKAGE_VERSION_POLICY_ARCHIVE_REV_INDEPENDENT
        and isinstance(package_inputs.get("builder_lock"), dict)
        and "--package-inputs" in _read("tools/mxrelease.py")
        and "release-inputs:" in makefile
        and "make release-inputs" in context
        and "def package_input_snapshot" in mkrevzip_text
        and '"package_inputs": package_input_snapshot(root)' in mkrevzip_text
        and "test_mkrevzip_embeds_package_input_policy_report" in mkrevzip_tests
    )
    hash_locked_builder_present = (
        package_input_policy_present
        and mxrelease.BUILDER_LOCK_PATH in locks
        and (ROOT / "tools" / "mxbuilder.py").is_file()
        and "def verify_wheelhouse" in mxbuilder_text
        and "identical-before-bootstrap-and-after-install" in mxbuilder_text
        and "MICROMAX_BUILDER_RECEIPT_DIGEST" in mxbuilder_text
        and "python tools/mxbuilder.py" in makefile
    )
    unprivileged_job = (
        workflow_text.split("verify-unprivileged:", 1)[1].split("build-and-attest:", 1)[0]
        if "verify-unprivileged:" in workflow_text and "build-and-attest:" in workflow_text
        else ""
    )
    attestation_job = (
        workflow_text.split("build-and-attest:", 1)[1]
        if "build-and-attest:" in workflow_text
        else ""
    )
    hosted_attestation_present = (
        hash_locked_builder_present
        and "id-token: write" not in unprivileged_job
        and "attestations: write" not in unprivileged_job
        and "artifact-metadata: write" not in unprivileged_job
        and "!startsWith(github.ref, 'refs/tags/')" in unprivileged_job
        and "github.event_name == 'workflow_dispatch'" in attestation_job
        and "startsWith(github.ref, 'refs/tags/')" in attestation_job
        and "id-token: write" in attestation_job
        and "attestations: write" in attestation_job
        and "artifact-metadata: write" in attestation_job
        and "actions/attest@f7c74d28b9d84cb8768d0b8ca14a4bac6ef463e6" in attestation_job
        and ".artifacts/mxrepro/micromax-release-receipt.json" in attestation_job
        and ".artifacts/mxrepro/Micromax-rev*.zip" in attestation_job
    )
    retained_attested_outputs_present = (
        hosted_attestation_present
        and "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in attestation_job
        and "name: micromax-attested-release-${{ github.run_id }}-${{ github.run_attempt }}" in attestation_job
        and "if-no-files-found: error" in attestation_job
        and "include-hidden-files: true" in attestation_job
        and "retention-days: 30" in attestation_job
        and attestation_job.count(".artifacts/mxrepro/micromax-release-receipt.json") == 2
        and attestation_job.count(".artifacts/mxrepro/Micromax-rev*.zip") == 2
    )
    issues = package_inputs.get("issues")
    return {
        "lock_files": locks,
        "ci_workflows": workflows,
        "aggregate_evidence_manifests": manifests,
        "release_suite_manifests": release_manifests,
        "release_suite_evidence_rows": release_evidence_rows,
        "release_suite_evidence_present": bool(release_evidence_rows),
        "release_suite_evidence_current_count": sum(
            1
            for row in release_evidence_rows
            if row.get("current") is True and row.get("internally_consistent") is True
        ),
        "release_suite_evidence_complete_current_count": sum(
            1
            for row in release_evidence_rows
            if row.get("current") is True
            and row.get("internally_consistent") is True
            and row.get("complete") is True
        ),
        "release_suite_evidence_ok_current_count": sum(
            1
            for row in release_evidence_rows
            if row.get("current") is True
            and row.get("internally_consistent") is True
            and row.get("ok") is True
            and not row.get("issues")
        ),
        "context_snapshot_present": (ROOT / "MICROMAX-CONTEXT.json").is_file(),
        "shared_toolrun_present": shared_toolrun_present,
        "timely_runway_present": timely_present,
        "timely_summary_incremental": timely_summary_incremental,
        "timely_summary_completion_honest": timely_summary_completion_honest,
        "full_suite_runway_present": full_suite_runway_present,
        "mkrevzip_provenance_present": mkrevzip_provenance_present,
        "mkrevzip_verifier_present": mkrevzip_verifier_present,
        "mkrevzip_revision_lineage_present": mkrevzip_revision_lineage_present,
        "package_input_report_ok": package_inputs.get("ok") is True,
        "package_input_issues": list(issues) if isinstance(issues, list) else [],
        "package_input_policy_present": package_input_policy_present,
        "hash_locked_builder_present": hash_locked_builder_present,
        "hosted_attestation_present": hosted_attestation_present,
        "retained_attested_outputs_present": retained_attested_outputs_present,
    }


def payload(*, limit: int = 10) -> dict[str, Any]:
    project = _pyproject()
    current_rev = _current_rev()
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
    docs.update(_curated_entrypoint_revisions(current_rev))
    runtime_group_policy = _runtime_group_policy_metrics()
    return {
        "schema": "micromax.audit-metrics.v1",
        "project": "micromax",
        "rev": current_rev,
        "version": str(project.get("project", {}).get("version", "")),
        "inventory": {
            "docs": _tree_stats("docs"),
            "source": _tree_stats("src"),
            "tests": _tree_stats("tests"),
            "tools": _tree_stats("tools"),
        },
        "python": _python_metrics(limit=max(1, int(limit))),
        "editor": _editor_metrics(),
        "editor_trust": _editor_trust_metrics(),
        "buffer_creation": _buffer_creation_metrics(),
        "plugin_runtime_snapshot": _snapshot_metrics(),
        "runtime_group_policy": runtime_group_policy,
        "effect_contracts": _effect_contract_metrics(
            current_rev=current_rev, runtime_group_policy=runtime_group_policy
        ),
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
    if docs.get("curated_entrypoints_match_current") is not True:
        errors.append("curated entrypoint revisions do not match current revision")
    for rel in python.get("parse_failures") or []:
        errors.append(f"could not parse Python source: {rel}")
    effects = data.get("effect_contracts") or {}
    if effects.get("ok") is not True:
        for error in effects.get("errors") or ["effect/resource contract is absent"]:
            errors.append(f"effect/resource contract check failed: {error}")
    release = data.get("release_hygiene") or {}
    if release.get("shared_toolrun_present") is not True:
        errors.append("shared tool-runner timing/teardown seam is absent")
    if release.get("timely_runway_present") is not True:
        errors.append("bounded timely handoff runway is absent")
    if release.get("timely_summary_incremental") is not True:
        errors.append("timely summary is not persisted incrementally")
    if release.get("timely_summary_completion_honest") is not True:
        errors.append("timely summary can claim success before all planned steps complete")
    if release.get("full_suite_runway_present") is not True:
        errors.append("bounded full-suite release runway is absent")
    if release.get("mkrevzip_provenance_present") is not True:
        errors.append("mkrevzip archive-member provenance is absent")
    if release.get("mkrevzip_verifier_present") is not True:
        errors.append("mkrevzip archive verifier is absent")
    if release.get("mkrevzip_revision_lineage_present") is not True:
        errors.append("mkrevzip revision-lineage and atomic-publication guard is absent")
    if release.get("package_input_policy_present") is not True:
        errors.append("package input policy verifier is absent")
    if release.get("hash_locked_builder_present") is not True:
        errors.append("hash-locked byte-verified release builder is absent")
    if release.get("hosted_attestation_present") is not True:
        errors.append("least-authority hosted release attestation is absent")
    editor_trust = data.get("editor_trust") or {}
    for key in [
        "state_bound_discard_guard_present",
        "legacy_mutable_discard_flags_absent",
        "discard_commands_share_guard",
        "same_name_replacement_identity_present",
        "shared_initial_buffer_boundary_present",
        "failed_startup_remains_renderable",
        "headless_exit_uses_editor_quit_policy",
        "dirty_noninteractive_eof_is_nonzero",
        "trusted_and_restricted_journeys_present",
    ]:
        if editor_trust.get(key) is not True:
            errors.append(f"editor trust boundary check failed: {key}")
    buffer_creation = data.get("buffer_creation") or {}
    for key in [
        "unique_name_owner_present",
        "strict_creation_guard_precedes_state_mutation",
        "human_creation_routes_through_unique_owner",
        "interactive_surface_present",
        "script_creation_denial_present",
        "focused_collision_regressions_present",
        "runtime_registry_replacement_absent",
        "transactional_restore_preserves_registry_identity",
        "direct_buffer_writes_have_explicit_owners",
    ]:
        if buffer_creation.get(key) is not True:
            errors.append(f"buffer creation boundary check failed: {key}")
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
        "mark_owner_snapshot_present",
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
        "recovery_owner_snapshot_present",
        "keymode_owner_snapshot_present",
        "prompt_owner_snapshot_present",
        "recent_files_owner_snapshot_present",
        "palette_recent_owner_snapshot_present",
        "prompt_history_owner_snapshot_present",
        "saved_cursor_owner_snapshot_present",
        "pending_open_url_owner_snapshot_present",
        "qreplace_owner_snapshot_present",
        "qreplace_buffer_witness_present",
        "clipboard_owner_snapshot_present",
        "active_search_owner_snapshot_present",
        "help_history_owner_snapshot_present",
        "generation_snapshot_uses_scoped_nonmacro_surfaces",
        "generation_macro_snapshot_present",
        "macro_owner_generation_snapshot_present",
        "generation_snapshot_uses_scoped_macro_surface",
        "scoped_generation_snapshot_avoids_broad_macro_restore",
        "loaded_cleanup_restores_group_and_generation",
        "plugin_callback_scoped_snapshot_present",
        "plugin_callback_interaction_owner_present",
        "option_state_owner_snapshot_present",
        "plugin_callback_restore_uses_scoped_snapshots",
        "editor_passes_plugin_identity_to_callback_snapshot",
        "dictionary_snapshot_restores_word_authority",
        "committed_plugin_wordlists_are_tombstoned",
        "retired_direct_xts_reject_execution",
        "retired_deferred_callbacks_reject_execution",
        "retired_interactions_reject_response",
        "retired_macros_reject_playback",
        "qreplace_all_replacement_budget",
        "timer_pending_work_budget",
        "timer_cancellation_releases_tasks",
        "vm_hostcall_result_budget",
        "stdlib_resource_contract_present",
        "regex_hostcall_input_budget",
        "regex_hostcall_timeout_worker",
        "editor_model_dimension_budget",
        "editor_query_input_budget",
        "fs_read_preflight_byte_budget",
        "fs_read_timeout_worker",
        "editor_open_read_timeout_boundary",
        "fs_list_timeout_worker",
        "fs_stat_timeout_worker",
        "editor_scan_row_budget",
        "prompt_path_completion_scan_budget",
        "prompt_path_completion_timeout_worker",
        "editor_user_init_timeout_boundary",
        "source_load_stat_timeout_boundary",
        "editor_atomic_write_timeout_boundary",
        "editor_save_freshness_timeout_boundary",
        "editor_disk_state_cache_boundary",
        "worker_result_frame_deadline_boundary",
        "worker_start_deadline_boundary",
        "filesystem_worker_result_drain_boundary",
        "large_buffer_dirty_tracking_boundary",
        "palette_recent_stat_batch_boundary",
        "status_readonly_parsecursor_bounded",
        "shell_output_timeout_budget",
        "external_clipboard_process_budget",
        "open_url_process_timeout_boundary",
        "finite_worker_deadline_normalization",
        "source_load_eval_budget",
        "source_load_graph_budget",
        "plugin_package_fingerprint_budgets",
        "plugin_optional_meta_exists_contained",
        "plugin_discovery_fingerprint_timeout_boundary",
        "docs_catalog_scan_timeout_boundary",
        "help_doc_read_timeout_boundary",
        "project_root_marker_batch_boundary",
        "bounded_project_file_picker_boundary",
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
    effect_contracts = data["effect_contracts"]
    typecheck = data["typecheck"]
    editor_trust = data["editor_trust"]
    buffer_creation = data["buffer_creation"]
    runtime_group_policy = data["runtime_group_policy"]
    release_rows = [
        row
        for row in release.get("release_suite_evidence_rows") or []
        if isinstance(row, dict)
    ]
    release_evidence_lines = [
        "  release-suite evidence "
        f"current={release.get('release_suite_evidence_current_count', 0)}/{len(release_rows)} "
        f"complete-current={release.get('release_suite_evidence_complete_current_count', 0)} "
        f"passed-current={release.get('release_suite_evidence_ok_current_count', 0)}"
    ]
    for row in release_rows:
        counts = row.get("batch_status_counts")
        batch_counts = counts if isinstance(counts, dict) else {}
        digest = row.get("source_digest")
        digest_text = str(digest)[:12] if isinstance(digest, str) else "none"
        release_evidence_lines.append(
            f"  release manifest {row.get('path')}: status={row.get('status')} "
            f"current={row.get('current')} complete={row.get('complete')} ok={row.get('ok')} "
            f"batches={batch_counts.get('passed', 0)}/{row.get('test_batch_count', 0)} "
            f"source={digest_text} issues={row.get('issue_count', 0)}"
        )
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
            f"mark-owner={runtime_group_policy['mark_owner_snapshot_present']} "
            f"hook-clones={runtime_group_policy['hook_snapshots_clone_mutable_handlers']} "
            f"delayed-groups={runtime_group_policy['delayed_group_snapshots_present']} "
            f"singleton-help={runtime_group_policy['singleton_help_group_snapshots_present']} "
            f"recovery-interaction={runtime_group_policy['recovery_interaction_group_snapshots_present']} "
            f"generation-snapshot={runtime_group_policy['generation_guard_uses_narrow_snapshot']} "
            f"generation-rows={runtime_group_policy['generation_nonmacro_snapshots_present']} "
            f"generation-macros={runtime_group_policy['generation_macro_snapshot_present']} "
            f"macro-owner={runtime_group_policy['macro_owner_generation_snapshot_present']} "
            f"generation-interactions={runtime_group_policy['generation_interaction_snapshot_present']} "
            f"recovery-owner={runtime_group_policy['recovery_owner_snapshot_present']} "
            f"keymode-owner={runtime_group_policy['keymode_owner_snapshot_present']} "
            f"prompt-owner={runtime_group_policy['prompt_owner_snapshot_present']} "
            f"recent-files-owner={runtime_group_policy['recent_files_owner_snapshot_present']} "
            f"palette-recent-owner={runtime_group_policy['palette_recent_owner_snapshot_present']} "
            f"prompt-history-owner={runtime_group_policy['prompt_history_owner_snapshot_present']} "
            f"saved-cursor-owner={runtime_group_policy['saved_cursor_owner_snapshot_present']} "
            f"open-url-owner={runtime_group_policy['pending_open_url_owner_snapshot_present']} "
            f"qreplace-owner={runtime_group_policy['qreplace_owner_snapshot_present']} "
            f"qreplace-buffer-witness={runtime_group_policy['qreplace_buffer_witness_present']} "
            f"clipboard-owner={runtime_group_policy['clipboard_owner_snapshot_present']} "
            f"active-search-owner={runtime_group_policy['active_search_owner_snapshot_present']} "
            f"help-history-owner={runtime_group_policy['help_history_owner_snapshot_present']} "
            f"diagnostics={runtime_group_policy['plugin_cleanup_command_present']} "
            f"durable-log={runtime_group_policy['plugin_cleanup_durable_log_present']} "
            f"callback-scope={runtime_group_policy['plugin_callback_scoped_snapshot_present']} "
            f"callback-interaction-owner={runtime_group_policy['plugin_callback_interaction_owner_present']} "
            f"option-owner={runtime_group_policy['option_state_owner_snapshot_present']} "
            f"dictionary-provenance={runtime_group_policy['dictionary_snapshot_restores_word_authority']} "
            f"wordlist-tombstones={runtime_group_policy['committed_plugin_wordlists_are_tombstoned']} "
            f"retired-xt-guard={runtime_group_policy['retired_direct_xts_reject_execution']} "
            f"retired-callback-guard={runtime_group_policy['retired_deferred_callbacks_reject_execution']} "
            f"retired-interaction-guard={runtime_group_policy['retired_interactions_reject_response']} "
            f"retired-macro-guard={runtime_group_policy['retired_macros_reject_playback']} "
            f"qreplace-all-budget={runtime_group_policy['qreplace_all_replacement_budget']} "
            f"timer-budget={runtime_group_policy['timer_pending_work_budget']} "
            f"timer-release={runtime_group_policy['timer_cancellation_releases_tasks']} "
            f"hostcall-result-budget={runtime_group_policy['vm_hostcall_result_budget']} "
            f"stdlib-resource-contract={runtime_group_policy['stdlib_resource_contract_present']} "
            f"regex-input-budget={runtime_group_policy['regex_hostcall_input_budget']} "
            f"regex-timeout-worker={runtime_group_policy['regex_hostcall_timeout_worker']} "
            f"model-dim-budget={runtime_group_policy['editor_model_dimension_budget']} "
            f"query-budget={runtime_group_policy['editor_query_input_budget']} "
            f"fs-read-budget={runtime_group_policy['fs_read_preflight_byte_budget']} "
            f"fs-read-timeout={runtime_group_policy['fs_read_timeout_worker']} "
            f"open-read-timeout={runtime_group_policy['editor_open_read_timeout_boundary']} "
            f"fs-list-timeout={runtime_group_policy['fs_list_timeout_worker']} "
            f"fs-stat-timeout={runtime_group_policy['fs_stat_timeout_worker']} "
            f"scan-row-budget={runtime_group_policy['editor_scan_row_budget']} "
            f"path-completion-scan-budget={runtime_group_policy['prompt_path_completion_scan_budget']} "
            f"path-completion-timeout={runtime_group_policy['prompt_path_completion_timeout_worker']} "
            f"user-init-timeout={runtime_group_policy['editor_user_init_timeout_boundary']} "
            f"source-stat-timeout={runtime_group_policy['source_load_stat_timeout_boundary']} "
            f"atomic-write-timeout={runtime_group_policy['editor_atomic_write_timeout_boundary']} "
            f"save-freshness-timeout={runtime_group_policy['editor_save_freshness_timeout_boundary']} "
            f"disk-state-cache={runtime_group_policy['editor_disk_state_cache_boundary']} "
            f"worker-full-frame={runtime_group_policy['worker_result_frame_deadline_boundary']} "
            f"worker-start-deadline={runtime_group_policy['worker_start_deadline_boundary']} "
            f"filesystem-channel={runtime_group_policy['filesystem_worker_result_drain_boundary']} "
            f"large-buffer-dirty={runtime_group_policy['large_buffer_dirty_tracking_boundary']} "
            f"palette-stat-batch={runtime_group_policy['palette_recent_stat_batch_boundary']} "
            f"status-access-bounded={runtime_group_policy['status_readonly_parsecursor_bounded']} "
            f"shell-budget={runtime_group_policy['shell_output_timeout_budget']} "
            f"clipboard-process-budget={runtime_group_policy['external_clipboard_process_budget']} "
            f"open-url-process={runtime_group_policy['open_url_process_timeout_boundary']} "
            f"finite-worker-deadlines={runtime_group_policy['finite_worker_deadline_normalization']} "
            f"source-load-budget={runtime_group_policy['source_load_eval_budget']} "
            f"source-graph-budget={runtime_group_policy['source_load_graph_budget']} "
            f"package-budgets={runtime_group_policy['plugin_package_fingerprint_budgets']} "
            f"plugin-meta-contained={runtime_group_policy['plugin_optional_meta_exists_contained']} "
            f"plugin-discovery-timeout={runtime_group_policy['plugin_discovery_fingerprint_timeout_boundary']} "
            f"docs-catalog-timeout={runtime_group_policy['docs_catalog_scan_timeout_boundary']} "
            f"project-root-batch={runtime_group_policy['project_root_marker_batch_boundary']} "
            f"project-file-picker={runtime_group_policy['bounded_project_file_picker_boundary']} "
            f"help-doc-read-timeout={runtime_group_policy['help_doc_read_timeout_boundary']}",
            "",
            "Editor trust boundaries:",
            f"  discard-state-bound={editor_trust['state_bound_discard_guard_present']} "
            f"legacy-sticky-absent={editor_trust['legacy_mutable_discard_flags_absent']} "
            f"shared-discard-owner={editor_trust['discard_commands_share_guard']} "
            f"same-name-identity={editor_trust['same_name_replacement_identity_present']}",
            f"  shared-startup={editor_trust['shared_initial_buffer_boundary_present']} "
            f"renderable-fallback={editor_trust['failed_startup_remains_renderable']} "
            f"headless-safe-exit={editor_trust['headless_exit_uses_editor_quit_policy']} "
            f"dirty-eof-nonzero={editor_trust['dirty_noninteractive_eof_is_nonzero']} "
            f"journey-tests={editor_trust['trusted_and_restricted_journeys_present']}",
            f"  buffer-no-clobber={buffer_creation['strict_creation_guard_precedes_state_mutation']} "
            f"unique-owner={buffer_creation['unique_name_owner_present']} "
            f"human-routing={buffer_creation['human_creation_routes_through_unique_owner']} "
            f"interactive-surface={buffer_creation['interactive_surface_present']} "
            f"script-denial={buffer_creation['script_creation_denial_present']} "
            f"registry-stable={buffer_creation['transactional_restore_preserves_registry_identity']} "
            f"mark-registry-stable={buffer_creation['mark_restores_preserve_registry_identity']} "
            f"mutation-owners={buffer_creation['direct_buffer_mutations_have_explicit_owners']} "
            f"write-owners={buffer_creation['direct_buffer_writes_have_explicit_owners']}",
            "",
            "Docs and release hygiene:",
            f"  root markdown docs: {docs['root_markdown_files']} "
            f"({docs['numbered_root_docs_ge_100']} numbered >=100)",
            f"  duplicate numeric prefixes: {len(docs['duplicate_numeric_prefixes'])}",
            f"  curated entrypoints current={docs['curated_entrypoints_match_current']}",
            f"  installed help: {docs['installed_help_docs']} docs; "
            f"security contract installed={docs['security_boundaries_installed']}",
            f"  lock files: {len(release['lock_files'])}; CI workflows: {len(release['ci_workflows'])}; "
            f"aggregate manifests: {len(release['aggregate_evidence_manifests'])}; "
            f"release-suite manifests: {len(release['release_suite_manifests'])}",
            *release_evidence_lines,
            f"  shared tool-runner present={release['shared_toolrun_present']}; "
            f"timely runway present={release['timely_runway_present']}; "
            f"timely summary incremental={release['timely_summary_incremental']}; "
            f"timely summary complete-honest={release['timely_summary_completion_honest']}; "
            f"full-suite runway present={release['full_suite_runway_present']}; "
            f"mkrevzip provenance present={release['mkrevzip_provenance_present']}; "
            f"mkrevzip verifier present={release['mkrevzip_verifier_present']}; "
            f"mkrevzip lineage present={release['mkrevzip_revision_lineage_present']}; "
            f"package-input policy present={release['package_input_policy_present']}; "
            f"hash-locked builder present={release['hash_locked_builder_present']}; "
            f"hosted attestation present={release['hosted_attestation_present']}",
            f"  effect/resource contract: present={effect_contracts['present']} "
            f"ok={effect_contracts['ok']} rows={effect_contracts['row_count']} "
            f"help-doc-current={effect_contracts.get('help_doc_matches_generated')}",
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

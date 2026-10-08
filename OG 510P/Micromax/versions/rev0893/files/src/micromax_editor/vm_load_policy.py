from __future__ import annotations

"""Editor policy hooks for the core Micromax include/require/reload words.

Rev0771 made ``ed.require`` capability-aware, but the core VM loader words still
read directly from disk.  This module lets an editor-owned VM keep normal
standalone behavior outside script-originated execution while applying the same
``cap.fs-require`` / ``cap.fs-root`` discipline whenever a script tries to load
more source through ``include``, ``require``, or ``reload``.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from micromax import VM
from micromax.vm import MicromaxError, Span

from .file_recovery import read_file_for_editor
from .file_scriptops import fs_cap_root
from .file_write import FileContainmentError, assert_path_within_root




def _root_path(root: str | Path) -> Path:
    p = Path(root).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.resolve()
    except OSError:
        return p.absolute()


@contextmanager
def plugin_load_root_context(
    vm: VM,
    root: str | Path,
    *,
    generation: int | None = None,
    replaces_generation: int | None = None,
) -> Iterator[None]:
    """Temporarily allow plugin-private source loads under one plugin root.

    Plugin source/lifecycle/command callbacks run as editor script context so
    they cannot grant themselves ``cap.*`` options.  This scope grants only
    package-local Micromax source loading; arbitrary script loads still require
    explicit ``cap.fs-require`` authority.
    """

    attr = "current_plugin_load_root"
    gen_attr = "current_plugin_generation"
    replace_attr = "current_plugin_replaces_generation"
    previous = getattr(vm, attr, None)
    previous_generation = getattr(vm, gen_attr, None)
    previous_replaces_generation = getattr(vm, replace_attr, None)
    setattr(vm, attr, str(_root_path(root)))
    if generation is None:
        try:
            delattr(vm, gen_attr)
        except AttributeError:
            pass
    else:
        setattr(vm, gen_attr, int(generation))
    if replaces_generation is None:
        try:
            delattr(vm, replace_attr)
        except AttributeError:
            pass
    else:
        setattr(vm, replace_attr, int(replaces_generation))
    try:
        yield
    finally:
        if previous is None:
            try:
                delattr(vm, attr)
            except AttributeError:
                pass
        else:
            setattr(vm, attr, previous)
        if previous_generation is None:
            try:
                delattr(vm, gen_attr)
            except AttributeError:
                pass
        else:
            setattr(vm, gen_attr, previous_generation)
        if previous_replaces_generation is None:
            try:
                delattr(vm, replace_attr)
            except AttributeError:
                pass
        else:
            setattr(vm, replace_attr, previous_replaces_generation)


def _plugin_load_root(ed: Any) -> Path | None:
    raw = getattr(getattr(ed, "vm", None), "current_plugin_load_root", None)
    if raw is None or str(raw).strip() == "":
        return None
    return _root_path(str(raw))


def _script_policy_active(ed: Any) -> bool:
    try:
        return bool(ed.in_script_context())
    except Exception:
        return False


def _abs(path: str | Path) -> Path:
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.absolute()
    except OSError:
        return p


def _concrete_span_dir(span: Span | None) -> Path | None:
    if span is None:
        return None
    filename = str(getattr(span, "filename", "") or "")
    if not filename or filename.startswith("<"):
        return None
    try:
        return _abs(filename).parent
    except Exception:
        return None


def _load_path_candidates(vm: VM, raw: str, span: Span | None, root: Path | None) -> list[Path]:
    raw_path = Path(str(raw)).expanduser()
    if raw_path.is_absolute():
        return [_abs(raw_path)]

    candidates: list[Path] = []
    span_dir = _concrete_span_dir(span)
    if span_dir is not None:
        candidates.append(_abs(span_dir / raw_path))
    if root is not None:
        candidates.append(_abs(root / raw_path))

    # Keep the standalone VM's search convention, but root-active policy below
    # will skip outside candidates for relative paths rather than granting ambient
    # cwd / load-path / environment authority.
    candidates.append(_abs(raw_path))
    for d in list(getattr(vm, "load_paths", []) or []):
        dd = str(d).strip()
        if dd:
            candidates.append(_abs(Path(dd).expanduser() / raw_path))
    env = os.environ.get("MICROMAX_PATH", "")
    if env:
        for d in env.split(os.pathsep):
            dd = d.strip()
            if dd:
                candidates.append(_abs(Path(dd).expanduser() / raw_path))
    return candidates


def _within_root(path: Path, root: Path | None) -> bool:
    if root is None:
        return True
    try:
        assert_path_within_root(path, root)
        return True
    except FileContainmentError:
        return False


def _resolve_script_load_path(vm: VM, raw: str, span: Span | None, root: Path | None) -> str:
    candidates = _load_path_candidates(vm, raw, span, root)
    raw_is_abs = Path(str(raw)).expanduser().is_absolute()
    searched: list[str] = []
    skipped_outside = False
    for cand in candidates:
        if root is not None and not _within_root(cand, root):
            skipped_outside = True
            if raw_is_abs:
                assert_path_within_root(cand, root)
            continue
        searched.append(str(cand))
        try:
            if cand.is_file():
                return str(_abs(cand))
        except OSError:
            continue

    preview = ", ".join(searched[:6])
    more = max(0, len(searched) - 6)
    suffix = f" ... (+{more} more)" if more else ""
    root_note = f" under cap.fs-root {root}" if root is not None else ""
    outside_note = "; outside-root search candidates were ignored" if skipped_outside else ""
    raise MicromaxError(f"file not found{root_note}: {raw} (searched: {preview}{suffix}{outside_note})", span=span)


def _normalize_script_load_path(vm: VM, raw: str, span: Span | None, root: Path | None) -> str:
    candidates = _load_path_candidates(vm, raw, span, root)
    raw_is_abs = Path(str(raw)).expanduser().is_absolute()
    first_inside: Path | None = None
    for cand in candidates:
        if root is not None and not _within_root(cand, root):
            if raw_is_abs:
                assert_path_within_root(cand, root)
            continue
        if first_inside is None:
            first_inside = cand
        try:
            if cand.is_file():
                return str(_abs(cand))
        except OSError:
            continue
    if first_inside is not None:
        return str(_abs(first_inside))
    # All candidates were outside an active root.  Re-run the assertion on the
    # first candidate for a precise capability error.
    if candidates:
        assert_path_within_root(candidates[0], root)
    return str(_abs(raw))




def _resolve_plugin_load_path(vm: VM, raw: str, span: Span | None, root: Path) -> str:
    """Resolve a plugin-private include/require path under one plugin root."""

    raw_path = Path(str(raw)).expanduser()
    if raw_path.is_absolute():
        cand = _abs(raw_path)
        assert_path_within_root(cand, root)
        if cand.is_file():
            return str(cand)
        raise FileNotFoundError(f"file not found under plugin root {root}: {raw}")

    candidates: list[Path] = []
    span_dir = _concrete_span_dir(span)
    if span_dir is not None and _within_root(span_dir, root):
        candidates.append(_abs(span_dir / raw_path))
    candidates.append(_abs(root / raw_path))

    searched: list[str] = []
    for cand in candidates:
        assert_path_within_root(cand, root)
        searched.append(str(cand))
        try:
            if cand.is_file():
                return str(cand)
            if cand.exists() or cand.is_symlink():
                raise MicromaxError(f"not a plugin source file: {cand}", span=span)
        except OSError:
            continue
    preview = ", ".join(searched[:4])
    raise FileNotFoundError(f"file not found under plugin root {root}: {raw} (searched: {preview})")


def install_editor_vm_load_policy(ed: Any) -> None:
    """Install capability-aware loader hooks on ``ed.vm``.

    The hooks are intentionally inactive outside ``ed.script_context()`` so user
    init files, trusted plugin manager loads, and ordinary standalone VM usage do
    not inherit script capability restrictions accidentally.
    """

    vm: VM = ed.vm

    def resolve_policy(vm_arg: VM, op: str, raw_path: str, span: Span | None) -> str | None:
        if not _script_policy_active(ed):
            return None
        plugin_root = _plugin_load_root(ed)
        cap_require = bool(ed.options.get("cap.fs-require"))
        if plugin_root is not None and str(op) != "unrequire":
            try:
                return _resolve_plugin_load_path(vm_arg, str(raw_path), span, plugin_root)
            except FileNotFoundError:
                if not cap_require:
                    raise
            except FileContainmentError:
                # Absolute paths are not package-local.  If the user also granted
                # script load authority, let cap.fs-root decide; relative
                # package paths that escape remain denied.
                if not (cap_require and Path(str(raw_path)).expanduser().is_absolute()):
                    raise
        if not cap_require:
            raise MicromaxError(f"{op} disabled in script context (set cap.fs-require true)", span=span)
        root = fs_cap_root(ed)
        if str(op) == "unrequire":
            return _normalize_script_load_path(vm_arg, str(raw_path), span, root)
        return _resolve_script_load_path(vm_arg, str(raw_path), span, root)

    def read_policy(vm_arg: VM, op: str, path: str, span: Span | None) -> str | None:
        del vm_arg, op, span
        if not _script_policy_active(ed):
            return None
        plugin_root = _plugin_load_root(ed)
        containment_root = fs_cap_root(ed)
        if plugin_root is not None and _within_root(Path(path), plugin_root):
            containment_root = plugin_root
        try:
            return read_file_for_editor(path, encoding="utf-8", containment_root=containment_root).text
        except FileNotFoundError as e:
            raise MicromaxError(f"file not found: {path}") from e
        except IsADirectoryError as e:
            raise MicromaxError(f"not a file: {path}") from e
        except Exception as e:
            raise MicromaxError(str(e)) from e

    vm.load_path_policy = resolve_policy
    vm.load_source_reader = read_policy

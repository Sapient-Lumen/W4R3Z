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
from typing import Any, Callable, Iterator

from micromax import VM
from micromax.vm import MicromaxError, Span, WordlistAccessScope

from .file_access import stat_path_contained_bounded
from .file_recovery import read_file_for_editor
from .file_scriptops import fs_cap_root
from .file_write import FileContainmentError, assert_path_within_root
from .hostcall_boundary import (
    effective_fs_read_timeout_seconds,
    effective_fs_stat_timeout_seconds,
    effective_source_load_max_bytes,
)
from .plugin_package import PluginPackageSnapshot




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
    source_authorizer: Callable[[], str] | None = None,
    package_snapshot: PluginPackageSnapshot | None = None,
    plugin_name: str | None = None,
    readable_wids: tuple[int, ...] | list[int] | None = None,
    writable_wids: tuple[int, ...] | list[int] | None = None,
    allow_wordlist_creation: bool = False,
) -> Iterator[None]:
    """Temporarily allow plugin-private source loads under one plugin root.

    Plugin source/lifecycle/command callbacks run as editor script context so
    they cannot grant themselves ``cap.*`` options.  This scope grants only
    package-local Micromax source loading; arbitrary script loads still require
    explicit ``cap.fs-require`` authority.  Deferred callbacks may also provide
    a lazy authorizer.  It is called only when package source bytes are about to
    be consumed, not for callbacks that use already-evaluated words only.
    """

    attr = "current_plugin_load_root"
    gen_attr = "current_plugin_generation"
    replace_attr = "current_plugin_replaces_generation"
    authorizer_attr = "current_plugin_source_authorizer"
    snapshot_attr = "current_plugin_package_snapshot"
    name_attr = "current_plugin_name"
    normalized_name = str(plugin_name or "").strip()
    has_readable = readable_wids is not None
    has_writable = writable_wids is not None
    if normalized_name and not (has_readable and has_writable):
        raise ValueError(
            "plugin_name requires explicit readable_wids and writable_wids"
        )
    if not normalized_name and (has_readable or has_writable or allow_wordlist_creation):
        raise ValueError(
            "plugin namespace scope requires a non-empty plugin_name"
        )

    namespace_scope: WordlistAccessScope | None = None
    if normalized_name:
        namespace_scope = WordlistAccessScope(
            label=f"plugin {normalized_name}",
            readable_wids=frozenset(int(wid) for wid in readable_wids or ()),
            writable_wids=frozenset(int(wid) for wid in writable_wids or ()),
            allow_create=bool(allow_wordlist_creation),
        )
        unknown = sorted(
            (namespace_scope.readable_wids | namespace_scope.writable_wids)
            - {int(wid) for wid in vm.wordlists}
        )
        if unknown:
            raise MicromaxError(
                f"plugin {normalized_name}: unknown wordlist ids in execution scope: {unknown}"
            )

    missing = object()
    previous = getattr(vm, attr, None)
    previous_generation = getattr(vm, gen_attr, None)
    previous_replaces_generation = getattr(vm, replace_attr, None)
    previous_authorizer = getattr(vm, authorizer_attr, missing)
    previous_snapshot = getattr(vm, snapshot_attr, missing)
    previous_name = getattr(vm, name_attr, missing)
    previous_scope = getattr(vm, "wordlist_access_scope", None)
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
    if source_authorizer is None:
        try:
            delattr(vm, authorizer_attr)
        except AttributeError:
            pass
    else:
        setattr(vm, authorizer_attr, source_authorizer)
    if package_snapshot is None:
        try:
            delattr(vm, snapshot_attr)
        except AttributeError:
            pass
    else:
        setattr(vm, snapshot_attr, package_snapshot)

    if normalized_name:
        setattr(vm, name_attr, normalized_name)
        vm.wordlist_access_scope = namespace_scope
    else:
        try:
            delattr(vm, name_attr)
        except AttributeError:
            pass
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
        if previous_authorizer is missing:
            try:
                delattr(vm, authorizer_attr)
            except AttributeError:
                pass
        else:
            setattr(vm, authorizer_attr, previous_authorizer)
        if previous_snapshot is missing:
            try:
                delattr(vm, snapshot_attr)
            except AttributeError:
                pass
        else:
            setattr(vm, snapshot_attr, previous_snapshot)
        if previous_name is missing:
            try:
                delattr(vm, name_attr)
            except AttributeError:
                pass
        else:
            setattr(vm, name_attr, previous_name)
        vm.wordlist_access_scope = previous_scope


def _plugin_load_root(ed: Any) -> Path | None:
    raw = getattr(getattr(ed, "vm", None), "current_plugin_load_root", None)
    if raw is None or str(raw).strip() == "":
        return None
    return _root_path(str(raw))


def _plugin_package_snapshot(ed: Any) -> PluginPackageSnapshot | None:
    snapshot = getattr(getattr(ed, "vm", None), "current_plugin_package_snapshot", None)
    return snapshot if isinstance(snapshot, PluginPackageSnapshot) else None


def _plugin_source_load_denial(vm: VM) -> str:
    """Return a deferred plugin source-load denial, failing closed on errors."""

    authorizer = getattr(vm, "current_plugin_source_authorizer", None)
    if not callable(authorizer):
        return ""
    try:
        return str(authorizer() or "")
    except Exception as e:
        return f"plugin source load denied: authorization check failed: {e}"


def _snapshot_path_is_package_local(
    snapshot: PluginPackageSnapshot,
    path: str | Path,
) -> bool:
    """Classify a snapshot path without consulting the mutable namespace.

    A captured package member can later be replaced by a symlink.  Resolving the
    live path to decide whether it is package-local would let that symlink
    retarget the source reader away from the immutable snapshot.  Lexical
    containment against the snapshot's frozen root is the relevant authority
    boundary here; membership is checked by ``read_text`` itself.
    """

    try:
        snapshot.relative_name(path)
    except FileContainmentError:
        return False
    return True


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


def _source_candidate_stat(vm: VM, path: Path, root: Path | None):
    """Return bounded stat info for one executable-source load candidate."""

    return stat_path_contained_bounded(
        path,
        containment_root=root,
        timeout_seconds=effective_fs_stat_timeout_seconds(vm),
    )


def _candidate_stat_timeout(exc: BaseException) -> bool:
    text = f"{type(exc).__name__}: {exc}"
    return "FilesystemOperationTimeoutError" in text or "filesystem stat timed out" in text


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
            st = _source_candidate_stat(vm, cand, root)
            if st.exists and st.kind == "file":
                return str(_abs(cand))
        except Exception as e:
            if _candidate_stat_timeout(e):
                raise
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
            st = _source_candidate_stat(vm, cand, root)
            if st.exists and st.kind == "file":
                return str(_abs(cand))
        except Exception as e:
            if _candidate_stat_timeout(e):
                raise
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
        st = _source_candidate_stat(vm, cand, root)
        if st.exists and st.kind == "file":
            return str(cand)
        if st.exists:
            raise MicromaxError(f"not a plugin source file: {cand}", span=span)
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
            st = _source_candidate_stat(vm, cand, root)
            if st.exists and st.kind == "file":
                return str(cand)
            if st.exists:
                raise MicromaxError(f"not a plugin source file: {cand}", span=span)
        except MicromaxError:
            raise
        except Exception as e:
            if _candidate_stat_timeout(e):
                raise
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
        package_snapshot = _plugin_package_snapshot(ed)
        cap_require = bool(ed.options.get("cap.fs-require"))
        if plugin_root is not None and str(op) != "unrequire":
            try:
                if package_snapshot is not None:
                    filename = str(getattr(span, "filename", "") or "") if span is not None else ""
                    return str(
                        package_snapshot.resolve_source(
                            str(raw_path),
                            span_filename=filename,
                        )
                    )
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
        del op
        if not _script_policy_active(ed):
            return None
        plugin_root = _plugin_load_root(ed)
        package_snapshot = _plugin_package_snapshot(ed)
        containment_root = fs_cap_root(ed)
        if package_snapshot is not None:
            package_local = _snapshot_path_is_package_local(package_snapshot, path)
        else:
            package_local = plugin_root is not None and _within_root(Path(path), plugin_root)
        if package_local:
            denial = _plugin_source_load_denial(vm_arg)
            if denial:
                raise MicromaxError(denial, span=span)
            if package_snapshot is not None:
                return package_snapshot.read_text(
                    path,
                    max_bytes=effective_source_load_max_bytes(vm_arg),
                )
            containment_root = plugin_root
        try:
            return read_file_for_editor(
                path,
                encoding="utf-8",
                containment_root=containment_root,
                max_bytes=effective_source_load_max_bytes(vm_arg),
                timeout_seconds=effective_fs_read_timeout_seconds(vm_arg),
            ).text
        except FileNotFoundError as e:
            raise MicromaxError(f"file not found: {path}") from e
        except IsADirectoryError as e:
            raise MicromaxError(f"not a file: {path}") from e
        except Exception as e:
            raise MicromaxError(str(e)) from e

    vm.load_path_policy = resolve_policy
    vm.load_source_reader = read_policy

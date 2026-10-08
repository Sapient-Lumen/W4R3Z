#!/usr/bin/env python3
"""Build a deterministic release ZIP of the repository.

Why:
- makes releases reproducible (stable file order + stable timestamps + canonical file modes)
- avoids compressor-runtime drift by storing member bytes without DEFLATE
- reduces noisy diffs in downstream distribution channels

This script is intentionally stdlib-only.

NOTE: This does not run the full release gate. Run `scripts/release_gate.py` first.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import stat
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True

import build_manifest
import release_control_files
import release_path_policy

FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
MANIFEST_NAME = "MANIFEST.sha256"


def _decode_pathlike(path: pathlib.Path | str) -> str:
    """Return the raw operator-supplied path string for output preflight."""

    raw = os.fspath(path)
    if isinstance(raw, bytes):  # pragma: no cover - uncommon for repo tooling callers
        raw = raw.decode(sys.getfilesystemencoding(), "surrogateescape")
    return raw


def _output_path_lexical_problems(path: pathlib.Path | str) -> list[str]:
    """Return problems for ambiguous release ZIP builder output spellings.

    The artifact verifier now treats release ZIP carrier names and paths as
    evidence-bearing metadata.  The builder should therefore fail closed before
    creating an artifact through a raw output spelling that the verifier or safe
    extractor would later reject: empty paths, NUL bytes, ``.``, ``..``, repeated
    separators, or trailing separators.
    """

    raw = _decode_pathlike(path)
    if raw == "":
        return ["release ZIP output path must not be empty"]
    if "\x00" in raw:
        return ["release ZIP output path must not contain NUL bytes"]

    seps = [os.sep]
    if os.altsep and os.altsep not in seps:
        seps.append(os.altsep)

    if len(raw) > 1 and any(raw.endswith(sep) for sep in seps):
        return [f"release ZIP output path must identify a file without a trailing separator: {raw!r}"]

    normalized = raw
    for sep in seps:
        if sep != "/":
            normalized = normalized.replace(sep, "/")

    parts = normalized.split("/")
    for idx, part in enumerate(parts):
        if idx == 0 and part == "":
            continue
        if part == "":
            return [f"release ZIP output path must not contain empty separator components: {raw!r}"]
        if part in {".", ".."}:
            return [f"release ZIP output path must not contain current/parent traversal components: {raw!r}"]
    return []


def _absolute_lexical_path(path: pathlib.Path) -> pathlib.Path:
    """Return an absolute path without resolving symlinks in an audited route."""

    return path if path.is_absolute() else pathlib.Path.cwd() / path


def _root_path_lexical_problems(path: pathlib.Path | str) -> list[str]:
    """Return problems for ambiguous release builder source-root spellings.

    Release construction should identify the repository tree through the same
    concrete-path discipline now used for release ZIP inputs and outputs.  A
    source root supplied as ``.``, ``..``, ``repo//tree``, or ``repo/`` can be
    normalized by ``pathlib`` before the audit-visible route is checked, so the
    builder rejects those raw spellings and asks the operator to use a concrete
    absolute or simple relative directory path instead.
    """

    raw = _decode_pathlike(path)
    if raw == "":
        return ["release ZIP source root path must not be empty"]
    if "\x00" in raw:
        return ["release ZIP source root path must not contain NUL bytes"]

    seps = [os.sep]
    if os.altsep and os.altsep not in seps:
        seps.append(os.altsep)

    if len(raw) > 1 and any(raw.endswith(sep) for sep in seps):
        return [f"release ZIP source root path must not have a trailing separator: {raw!r}"]

    normalized = raw
    for sep in seps:
        if sep != "/":
            normalized = normalized.replace(sep, "/")

    parts = normalized.split("/")
    for idx, part in enumerate(parts):
        if idx == 0 and part == "":
            continue
        if part == "":
            return [f"release ZIP source root path must not contain empty separator components: {raw!r}"]
        if part in {".", ".."}:
            return [f"release ZIP source root path must not contain current/parent traversal components: {raw!r}"]
    return []


def _root_path_ancestry_problems(path: pathlib.Path | str) -> list[str]:
    """Return problems if a source root is missing or symlink-routed."""

    raw = pathlib.Path(path)
    lexical = _absolute_lexical_path(raw)
    problems: list[str] = []

    try:
        final_st = lexical.lstat()
    except FileNotFoundError:
        return [f"release ZIP source root path does not exist: {str(raw)!r}"]
    except OSError as exc:
        return [f"could not stat release ZIP source root path {str(raw)!r}: {exc}"]

    if stat.S_ISLNK(final_st.st_mode):
        problems.append(f"release ZIP source root path must not be a symlink: {str(raw)!r}")
    elif not stat.S_ISDIR(final_st.st_mode):
        problems.append(f"release ZIP source root path must be a directory: {str(raw)!r}")

    parts = lexical.parts
    if lexical.is_absolute():
        cur = pathlib.Path(parts[0])
        rest = parts[1:-1]
    else:  # pragma: no cover - lexical is absolute for normal callers
        cur = pathlib.Path()
        rest = parts[:-1]

    for part in rest:
        cur = cur / part
        try:
            ast = cur.lstat()
        except OSError as exc:
            problems.append(f"could not stat release ZIP source root ancestor {str(cur)!r}: {exc}")
            break
        if stat.S_ISLNK(ast.st_mode):
            problems.append(f"release ZIP source root ancestry must not contain symlink component: {str(cur)!r}")
            break
        if not stat.S_ISDIR(ast.st_mode):
            problems.append(f"release ZIP source root ancestor is not a directory: {str(cur)!r}")
            break

    return problems


def _preflight_repo_root_path(path: pathlib.Path | str) -> pathlib.Path:
    """Validate and return an absolute non-resolved release source root."""

    problems = _root_path_lexical_problems(path)
    raw = pathlib.Path(_decode_pathlike(path))
    if not problems:
        problems.extend(_root_path_ancestry_problems(raw))
    if problems:
        raise SystemExit("\n".join(problems[:20]))
    return _absolute_lexical_path(raw)


def _output_path_ancestry_problems(path: pathlib.Path | str) -> list[str]:
    """Return problems if an output path would publish through symlinks.

    Non-existing parent directories are allowed; existing components must be
    concrete directories, and an existing final path must be a regular file.
    This keeps builder publication aligned with verifier/extractor carrier-path
    firewalls without forbidding first-time creation under a concrete parent.
    """

    raw = pathlib.Path(path)
    lexical = _absolute_lexical_path(raw)
    problems: list[str] = []

    parts = lexical.parts
    if not parts:
        return ["release ZIP output path must not be empty"]
    if lexical.is_absolute():
        cur = pathlib.Path(parts[0])
        rest = parts[1:-1]
    else:  # pragma: no cover - lexical is absolute for normal callers
        cur = pathlib.Path()
        rest = parts[:-1]

    for part in rest:
        cur = cur / part
        try:
            st = cur.lstat()
        except FileNotFoundError:
            break
        except OSError as exc:
            problems.append(f"could not stat release ZIP output path ancestor {str(cur)!r}: {exc}")
            break
        if stat.S_ISLNK(st.st_mode):
            problems.append(f"release ZIP output path ancestry must not contain symlink component: {str(cur)!r}")
            break
        if not stat.S_ISDIR(st.st_mode):
            problems.append(f"release ZIP output path ancestor is not a directory: {str(cur)!r}")
            break

    try:
        final_st = lexical.lstat()
    except FileNotFoundError:
        return problems
    except OSError as exc:
        problems.append(f"could not stat release ZIP output path {str(raw)!r}: {exc}")
        return problems

    if stat.S_ISLNK(final_st.st_mode):
        problems.append(f"release ZIP output path must not be a symlink: {str(raw)!r}")
    elif not stat.S_ISREG(final_st.st_mode):
        problems.append(f"release ZIP output path must be a regular file when it already exists: {str(raw)!r}")
    return problems


def _preflight_output_path(path: pathlib.Path | str) -> pathlib.Path:
    """Validate and return an absolute non-resolved release ZIP output path."""

    problems = _output_path_lexical_problems(path)
    if not problems:
        problems.extend(_output_path_ancestry_problems(pathlib.Path(_decode_pathlike(path))))
    if problems:
        raise SystemExit("\n".join(problems[:20]))
    return _absolute_lexical_path(pathlib.Path(_decode_pathlike(path)))


def preflight_output_path(path: pathlib.Path | str) -> pathlib.Path:
    """Public preflight used by the lock-held release-gate build path.

    The release gate must reject an unsafe carrier path before spending time on
    the full semantic gate.  Keep the path policy single-sourced here so the
    standalone builder and the one-command release path cannot disagree.
    """

    return _preflight_output_path(path)


def _supports_openat_no_follow() -> bool:
    """Return whether this runtime can walk relative paths with directory fds."""

    return os.open in getattr(os, "supports_dir_fd", set()) and hasattr(os, "O_DIRECTORY")


def _open_directory_route_no_symlinks(path: pathlib.Path, label: str) -> int:
    """Open a directory route component-by-component without following symlinks."""

    lexical = _absolute_lexical_path(path)
    flags = getattr(os, "O_PATH", os.O_RDONLY)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    if not _supports_openat_no_follow():  # pragma: no cover - fallback for non-POSIX runtimes
        problems = _root_path_ancestry_problems(lexical)
        if problems:
            raise SystemExit("\n".join(problems[:20]))
        try:
            fd = os.open(lexical, flags)
        except OSError as exc:
            raise SystemExit(f"{label}: could not open directory route: {exc}") from exc
        try:
            st = os.fstat(fd)
        except OSError as exc:
            os.close(fd)
            raise SystemExit(f"{label}: could not stat directory route: {exc}") from exc
        if not stat.S_ISDIR(st.st_mode):
            os.close(fd)
            raise SystemExit(f"{label}: route component is not a directory")
        return fd

    parts = lexical.parts
    if not parts:
        raise SystemExit(f"{label}: empty directory route")

    fd = -1
    try:
        fd = os.open(parts[0], flags)
        st = os.fstat(fd)
        if not stat.S_ISDIR(st.st_mode):
            raise SystemExit(f"{label}: route component {parts[0]!r} is not a directory")
        for part in parts[1:]:
            try:
                child_fd = os.open(part, flags, dir_fd=fd)
            except OSError as exc:
                raise SystemExit(
                    f"{label}: could not open directory route component {part!r} without following symlinks: {exc}"
                ) from exc
            os.close(fd)
            fd = child_fd
            try:
                st = os.fstat(fd)
            except OSError as exc:
                raise SystemExit(f"{label}: could not stat directory route component {part!r}: {exc}") from exc
            if not stat.S_ISDIR(st.st_mode):
                raise SystemExit(f"{label}: route component {part!r} is not a directory")
        out = fd
        fd = -1
        return out
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass


def _open_source_member_fd(repo_root: pathlib.Path, rel: str) -> tuple[int, os.stat_result]:
    """Open one release source member through a no-symlink ancestry route."""

    rel_problem = release_path_policy.release_path_problem(rel)
    if rel_problem:
        raise SystemExit(f"{rel}: unsafe release source member path at read time: {rel_problem}")
    parts = rel.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise SystemExit(f"{rel}: unsafe release source member path at read time")

    dir_fd = _open_directory_route_no_symlinks(repo_root, f"{rel}: release source root ancestry")
    try:
        if not _supports_openat_no_follow():  # pragma: no cover - fallback for non-POSIX runtimes
            src = repo_root / rel
            flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            if hasattr(os, "O_NONBLOCK"):
                flags |= os.O_NONBLOCK
            try:
                fd = os.open(src, flags)
            except OSError as exc:
                raise SystemExit(f"{rel}: could not open release source member without following symlinks: {exc}") from exc
            try:
                st = os.fstat(fd)
            except OSError as exc:
                os.close(fd)
                raise SystemExit(f"{rel}: could not stat open release source member: {exc}") from exc
            if not stat.S_ISREG(st.st_mode):
                os.close(fd)
                raise SystemExit(f"{rel}: release source member did not open as a regular file")
            return fd, st

        dir_flags = getattr(os, "O_PATH", os.O_RDONLY)
        if hasattr(os, "O_DIRECTORY"):
            dir_flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            dir_flags |= os.O_NOFOLLOW
        for part in parts[:-1]:
            try:
                child_fd = os.open(part, dir_flags, dir_fd=dir_fd)
            except OSError as exc:
                raise SystemExit(
                    f"{rel}: release source member ancestry component {part!r} could not be opened without following symlinks: {exc}"
                ) from exc
            os.close(dir_fd)
            dir_fd = child_fd
            try:
                st = os.fstat(dir_fd)
            except OSError as exc:
                raise SystemExit(f"{rel}: could not stat release source member ancestry component {part!r}: {exc}") from exc
            if not stat.S_ISDIR(st.st_mode):
                raise SystemExit(f"{rel}: release source member ancestry component {part!r} is not a directory")

        file_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            file_flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            file_flags |= os.O_NONBLOCK
        try:
            fd = os.open(parts[-1], file_flags, dir_fd=dir_fd)
        except OSError as exc:
            raise SystemExit(f"{rel}: could not open release source member without following symlinks: {exc}") from exc
        try:
            st = os.fstat(fd)
        except OSError as exc:
            os.close(fd)
            raise SystemExit(f"{rel}: could not stat open release source member: {exc}") from exc
        if not stat.S_ISREG(st.st_mode):
            os.close(fd)
            raise SystemExit(f"{rel}: release source member did not open as a regular file")
        return fd, st
    finally:
        try:
            os.close(dir_fd)
        except OSError:
            pass


def _read_source_member_bytes(repo_root: pathlib.Path, rel: str) -> bytes:
    """Read one source member through a no-symlink ancestry and leaf-file route.

    Release member discovery rejects symlinks and special files before returning
    the file list, but ZIP construction reads bytes later.  Re-open the source
    root and every member parent directory component without following symlinks,
    then open the final member through a regular-file descriptor.  This closes
    the remaining gap where a parent directory could be swapped to a symlink
    after discovery and before the member bytes were read.
    """

    fd, open_stat = _open_source_member_fd(repo_root, rel)
    try:
        with os.fdopen(fd, "rb") as f:
            fd = -1
            data = f.read()
            try:
                read_stat = os.fstat(f.fileno())
            except OSError as exc:
                raise SystemExit(f"{rel}: could not restat release source member after read: {exc}") from exc
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass

    if (read_stat.st_dev, read_stat.st_ino) != (open_stat.st_dev, open_stat.st_ino):
        raise SystemExit(f"{rel}: release source member identity changed while being read")
    if open_stat.st_size != read_stat.st_size or read_stat.st_size != len(data):
        raise SystemExit(
            f"{rel}: release source member changed size while being read "
            f"(before={open_stat.st_size}, after={read_stat.st_size}, read={len(data)})"
        )
    return data


def _write_zip_bytes(repo_root: pathlib.Path, rel_files: list[str], out_path: pathlib.Path) -> None:
    """Write canonical release ZIP bytes to ``out_path``."""

    with zipfile.ZipFile(
        out_path,
        "w",
        compression=zipfile.ZIP_STORED,
        strict_timestamps=False,
    ) as zf:
        for rel in rel_files:
            src = repo_root / rel
            zi = _zipinfo_for(rel, src)
            zf.writestr(zi, _read_source_member_bytes(repo_root, rel))



def _normalize_rel(p: pathlib.Path) -> str:
    return release_path_policy.normalize_release_rel(p.as_posix())


def _should_include(rel_posix: str) -> bool:
    """Return whether a repo-relative file path belongs in the release ZIP.

    The release ZIP and MANIFEST.sha256 must have the same scope, except that
    the ZIP includes MANIFEST.sha256 itself while the manifest intentionally does
    not hash itself.  Keep this as a thin wrapper over build_manifest's predicate
    so release packaging cannot drift by maintaining two independent exclude
    lists.
    """

    rel = release_path_policy.normalize_release_rel(rel_posix)
    if release_path_policy.release_path_problem(rel):
        return False
    if rel == MANIFEST_NAME:
        return True
    return build_manifest.should_include_rel(rel)


def canonical_mode_for(rel_posix: str) -> int:
    """Return the canonical file mode stored in release ZIP entries.

    The archive is reconstructed from extracted trees as well as from source
    working trees.  Local executable bits are not sealed by MANIFEST.sha256 and
    are not reliably preserved by all ZIP extractors, so they must not influence
    the release artifact.  Tools are invoked as ``python3 scripts/name.py``; the
    ZIP payload stores every file as a regular 0644 data file.
    """

    return 0o644


def _zipinfo_for(rel_posix: str, src_path: pathlib.Path) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(rel_posix)
    zi.compress_type = zipfile.ZIP_STORED
    zi.date_time = FIXED_ZIP_DT
    # Pin ZIP creator/extractor metadata for cross-platform byte stability.
    # 0x03 is Unix, 0x14 is ZIP 2.0; stored entries avoid compressor-runtime drift.
    zi.create_system = 3
    zi.create_version = 20
    zi.extract_version = 20
    zi.flag_bits = 0
    zi.external_attr = (canonical_mode_for(rel_posix) & 0xFFFF) << 16
    return zi


def release_file_names(repo_root: pathlib.Path | str, out_zip: pathlib.Path | str | None = None) -> list[str]:
    """Return deterministic repo-relative file names selected for the release ZIP.

    If an output ZIP path is supplied, skip only that exact lexical source path.
    Do not use ``Path.resolve()`` for this exclusion: resolving source members
    before file-type checks can hide a governed symlink by treating it as an
    alias for the output artifact instead of reporting it as forbidden source
    material.
    """

    repo_root = _preflight_repo_root_path(repo_root)
    out_lexical = _preflight_output_path(out_zip) if out_zip is not None else None

    rel_files: list[str] = []
    file_type_problems: list[str] = []
    for p in sorted(repo_root.rglob("*")):
        rel = _normalize_rel(p.relative_to(repo_root))
        if out_lexical is not None and _absolute_lexical_path(p) == out_lexical:
            continue
        path_problem = build_manifest.governed_path_problem(rel)
        if path_problem:
            file_type_problems.append(f"unsafe release-scope path cannot be packaged: {rel}: {path_problem}")
            continue
        if p.is_symlink():
            if _should_include(rel):
                file_type_problems.append(f"release-scope symlink cannot be packaged: {rel}")
            continue
        if p.is_dir():
            continue
        if not _should_include(rel):
            continue
        if not p.is_file():
            file_type_problems.append(f"release-scope path is not a regular file: {rel}")
            continue
        rel_files.append(rel)

    if file_type_problems:
        raise SystemExit("\n".join(file_type_problems[:20]))

    collisions = release_path_policy.find_portable_path_collisions(rel_files)
    if collisions:
        details = "; ".join(
            f"{key}: {', '.join(vals)}"
            for key, vals in sorted(collisions.items())[:10]
        )
        raise SystemExit(f"Portable release-path collision(s) detected: {details}")

    shape_conflicts = release_path_policy.find_extraction_shape_conflicts(rel_files)
    if shape_conflicts:
        details = "; ".join(
            f"{prefix}: {', '.join(children)}"
            for prefix, children in sorted(shape_conflicts.items())[:10]
        )
        raise SystemExit(f"Release extraction shape conflict(s) detected: {details}")
    return rel_files


def build_zip(repo_root: pathlib.Path | str, out_zip: pathlib.Path | str) -> None:
    repo_root = _preflight_repo_root_path(repo_root)
    out_root = _preflight_output_path(out_zip)

    try:
        out_root.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SystemExit(f"could not create release ZIP output parent directory: {exc}") from exc

    # Recheck after parent creation so a newly materialized route still obeys the
    # same concrete-output policy before bytes are written.
    problems = _output_path_ancestry_problems(out_root)
    if problems:
        raise SystemExit("\n".join(problems[:20]))

    rel_files = release_file_names(repo_root, out_root)

    tmp_path: pathlib.Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{out_root.name}.tmp.",
            suffix=".zip",
            dir=out_root.parent,
            delete=False,
        ) as tmp:
            tmp_path = pathlib.Path(tmp.name)
        _write_zip_bytes(repo_root, rel_files, tmp_path)

        # Recheck immediately before publish so a local symlink swap between the
        # initial preflight and final replacement cannot silently become the
        # builder's publication route.
        problems = _output_path_ancestry_problems(out_root)
        if problems:
            raise SystemExit("\n".join(problems[:20]))
        os.replace(tmp_path, out_root)
        tmp_path = None
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass


def _default_out_zip(repo_root: pathlib.Path) -> pathlib.Path:
    version_file = repo_root / "VERSION"
    version = "unknown"
    if version_file.exists():
        parsed, problems = release_control_files.parse_version_bytes(version_file.read_bytes())
        if problems or parsed is None:
            detail = "; ".join(problems) or "unknown VERSION parse failure"
            raise SystemExit(f"VERSION is not canonical; refusing default release ZIP name: {detail}")
        version = parsed
    return repo_root / "dist" / f"The-Election-Stack_{version}.zip"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default=None,
        help="Repo root (default: current working directory; explicit values are audited before normalization)",
    )
    ap.add_argument("--out", default=None, help="Output zip path (default: dist/The-Election-Stack_<VERSION>.zip)")
    args = ap.parse_args()

    repo_root: pathlib.Path | str = pathlib.Path.cwd() if args.root is None else args.root
    default_root = _preflight_repo_root_path(repo_root)
    out_zip = args.out if args.out else _default_out_zip(default_root)

    build_zip(repo_root, out_zip)
    print(_absolute_lexical_path(pathlib.Path(_decode_pathlike(out_zip))))


if __name__ == "__main__":
    main()

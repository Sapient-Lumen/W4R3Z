#!/usr/bin/env python3
"""Build MANIFEST.sha256 for the archive.

This is a low-tech integrity layer: it helps detect accidental edits, partial zips,
or malicious tampering in redistribution.

By default this script *writes* MANIFEST.sha256.
Use --check to fail if the working tree does not match the existing manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

import release_path_policy
import release_control_files

ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
OUT = ROOT / release_control_files.MANIFEST_NAME

EXCLUDE = {
    "MANIFEST.sha256",
}

# Never ship interpreter/build caches inside the archive.
EXCLUDE_DIR_PARTS = {
    "tmp_emit_pvr",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

EXCLUDE_FILENAMES = {
    ".DS_Store",
}

# Directories that may contain operator-local state or downloaded third-party bytes.
# These MUST NOT affect the archive manifest.
EXCLUDE_PREFIXES = {
    "evidence/cache/",
    # Local release outputs. Normative bundles are built via scripts/build_release_zip.py
    # and distributed out-of-tree; keep dist/ out of the integrity manifest to prevent
    # size growth from accumulating release artifacts.
    "dist/",
}


def file_sha256(p: Path) -> str:
    """Return the SHA-256 for a concrete path.

    Kept for compatibility with older callers that already hold an audited
    file path. Release manifest construction uses ``file_sha256_for_rel()`` so
    hashing reopens each governed member through a no-symlink route.
    """

    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _absolute_lexical_path(path: Path) -> Path:
    """Return an absolute path without resolving symlink components."""

    return path if path.is_absolute() else Path.cwd() / path


def _decode_pathlike(path: Path | str) -> str:
    """Return a raw path string without pathlib normalization where possible."""

    raw = os.fspath(path)
    if isinstance(raw, bytes):  # pragma: no cover - uncommon for repo tooling callers
        raw = raw.decode(sys.getfilesystemencoding(), "surrogateescape")
    return raw


def _manifest_root_lexical_problems(path: Path | str) -> list[str]:
    """Return problems for ambiguous manifest-builder source-root spellings."""

    raw = _decode_pathlike(path)
    if raw == "":
        return ["manifest source root path must not be empty"]
    if "\x00" in raw:
        return ["manifest source root path must not contain NUL bytes"]

    seps = [os.sep]
    if os.altsep and os.altsep not in seps:
        seps.append(os.altsep)

    if len(raw) > 1 and any(raw.endswith(sep) for sep in seps):
        return [f"manifest source root path must not have a trailing separator: {raw!r}"]

    normalized = raw
    for sep in seps:
        if sep != "/":
            normalized = normalized.replace(sep, "/")

    parts = normalized.split("/")
    for idx, part in enumerate(parts):
        if idx == 0 and part == "":
            continue
        if part == "":
            return [f"manifest source root path must not contain empty separator components: {raw!r}"]
        if part in {".", ".."}:
            return [f"manifest source root path must not contain current/parent traversal components: {raw!r}"]
    return []


def _manifest_root_ancestry_problems(path: Path | str) -> list[str]:
    """Return problems if the manifest source root is missing or symlink-routed."""

    raw_path = Path(_decode_pathlike(path))
    lexical = _absolute_lexical_path(raw_path)
    problems: list[str] = []

    try:
        final_st = lexical.lstat()
    except FileNotFoundError:
        return [f"manifest source root path does not exist: {str(raw_path)!r}"]
    except OSError as exc:
        return [f"could not stat manifest source root path {str(raw_path)!r}: {exc}"]

    if stat.S_ISLNK(final_st.st_mode):
        problems.append(f"manifest source root path must not be a symlink: {str(raw_path)!r}")
    elif not stat.S_ISDIR(final_st.st_mode):
        problems.append(f"manifest source root path must be a directory: {str(raw_path)!r}")

    parts = lexical.parts
    if lexical.is_absolute():
        cur = Path(parts[0])
        rest = parts[1:-1]
    else:  # pragma: no cover - lexical is absolute for normal callers
        cur = Path()
        rest = parts[:-1]

    for part in rest:
        cur = cur / part
        try:
            ast = cur.lstat()
        except OSError as exc:
            problems.append(f"could not stat manifest source root ancestor {str(cur)!r}: {exc}")
            break
        if stat.S_ISLNK(ast.st_mode):
            problems.append(f"manifest source root ancestry must not contain symlink component: {str(cur)!r}")
            break
        if not stat.S_ISDIR(ast.st_mode):
            problems.append(f"manifest source root ancestor is not a directory: {str(cur)!r}")
            break

    return problems


def _preflight_manifest_root_path(path: Path | str) -> Path:
    """Validate and return an absolute non-resolved manifest source root."""

    problems = _manifest_root_lexical_problems(path)
    if not problems:
        problems.extend(_manifest_root_ancestry_problems(path))
    if problems:
        raise SystemExit("\n".join(problems[:20]))
    return _absolute_lexical_path(Path(_decode_pathlike(path)))


def _supports_openat_no_follow() -> bool:
    """Return whether this runtime supports directory-fd no-follow walks."""

    return os.open in getattr(os, "supports_dir_fd", set()) and hasattr(os, "O_DIRECTORY")


def _open_directory_route_no_symlinks(path: Path, label: str) -> int:
    """Open a directory route component-by-component without following symlinks."""

    lexical = _absolute_lexical_path(path)
    flags = getattr(os, "O_PATH", os.O_RDONLY)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    if not _supports_openat_no_follow():  # pragma: no cover - fallback for non-POSIX runtimes
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


def _open_manifest_member_fd(root: Path, rel: str) -> tuple[int, os.stat_result]:
    """Open one manifest-governed member through a no-symlink route."""

    rel = release_path_policy.normalize_release_rel(rel)
    rel_problem = release_path_policy.release_path_problem(rel)
    if rel_problem:
        raise SystemExit(f"{rel}: unsafe manifest member path at hash time: {rel_problem}")
    parts = rel.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise SystemExit(f"{rel}: unsafe manifest member path at hash time")

    dir_fd = _open_directory_route_no_symlinks(root, f"{rel}: manifest root ancestry")
    try:
        if not _supports_openat_no_follow():  # pragma: no cover - fallback for non-POSIX runtimes
            src = root / rel
            flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            if hasattr(os, "O_NONBLOCK"):
                flags |= os.O_NONBLOCK
            try:
                fd = os.open(src, flags)
            except OSError as exc:
                raise SystemExit(f"{rel}: could not open manifest member without following symlinks: {exc}") from exc
            try:
                st = os.fstat(fd)
            except OSError as exc:
                os.close(fd)
                raise SystemExit(f"{rel}: could not stat open manifest member: {exc}") from exc
            if not stat.S_ISREG(st.st_mode):
                os.close(fd)
                raise SystemExit(f"{rel}: manifest member did not open as a regular file")
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
                    f"{rel}: manifest member ancestry component {part!r} could not be opened without following symlinks: {exc}"
                ) from exc
            os.close(dir_fd)
            dir_fd = child_fd
            try:
                st = os.fstat(dir_fd)
            except OSError as exc:
                raise SystemExit(f"{rel}: could not stat manifest member ancestry component {part!r}: {exc}") from exc
            if not stat.S_ISDIR(st.st_mode):
                raise SystemExit(f"{rel}: manifest member ancestry component {part!r} is not a directory")

        file_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            file_flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            file_flags |= os.O_NONBLOCK
        try:
            fd = os.open(parts[-1], file_flags, dir_fd=dir_fd)
        except OSError as exc:
            raise SystemExit(f"{rel}: could not open manifest member without following symlinks: {exc}") from exc
        try:
            st = os.fstat(fd)
        except OSError as exc:
            os.close(fd)
            raise SystemExit(f"{rel}: could not stat open manifest member: {exc}") from exc
        if not stat.S_ISREG(st.st_mode):
            os.close(fd)
            raise SystemExit(f"{rel}: manifest member did not open as a regular file")
        return fd, st
    finally:
        try:
            os.close(dir_fd)
        except OSError:
            pass


def read_manifest_member_bytes(root: Path, rel: str) -> bytes:
    """Read a release member through a no-symlink route with drift checks."""

    fd, open_stat = _open_manifest_member_fd(root, rel)
    total = 0
    chunks: list[bytes] = []
    try:
        with os.fdopen(fd, "rb") as f:
            fd = -1
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                chunks.append(chunk)
                total += len(chunk)
            try:
                read_stat = os.fstat(f.fileno())
            except OSError as exc:
                raise SystemExit(f"{rel}: could not restat manifest member after read: {exc}") from exc
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass

    if (read_stat.st_dev, read_stat.st_ino) != (open_stat.st_dev, open_stat.st_ino):
        raise SystemExit(f"{rel}: manifest member identity changed while being read")
    if open_stat.st_size != read_stat.st_size or read_stat.st_size != total:
        raise SystemExit(
            f"{rel}: manifest member changed size while being read "
            f"(before={open_stat.st_size}, after={read_stat.st_size}, read={total})"
        )
    return b"".join(chunks)


def file_sha256_for_rel(root: Path, rel: str) -> str:
    """Return SHA-256 for ``rel`` read through a no-symlink route under ``root``."""

    h = hashlib.sha256()
    h.update(read_manifest_member_bytes(root, rel))
    return h.hexdigest()


def is_local_only_rel(rel: str) -> bool:
    """Return whether ``rel`` is explicitly outside release scope.

    This predicate deliberately does *not* apply the release path-syntax
    firewall.  Callers use it first to separate known local-only debris
    (``dist/``, caches, top-level diagnostic logs, VCS metadata) from paths
    that are intended to be governed by the release.  Unsafe governed paths
    must fail closed instead of being silently omitted merely because
    ``should_include_rel()`` cannot include them.
    """

    rel = release_path_policy.normalize_release_rel(rel)

    # Explicit exclude list and VCS dirs.
    if rel in EXCLUDE or rel == ".git" or rel.startswith(".git/"):
        return True

    # Top-level *.log files are local diagnostic transcripts, not release
    # content. Normative evidence logs, if any, should live under a named
    # artifact/evidence directory and be governed there.
    if "/" not in rel and rel.endswith(".log"):
        return True

    # Prefix excludes.
    if any(rel.startswith(pfx) for pfx in EXCLUDE_PREFIXES):
        return True

    # Release names are POSIX-style; use slash splitting here so this local-only
    # classifier remains meaningful even when a path is syntactically unsafe.
    parts = set(rel.split("/"))
    if parts.intersection(EXCLUDE_DIR_PARTS):
        return True

    path = Path(rel)

    # Exclude unwanted file suffixes / names.
    if path.suffix in EXCLUDE_SUFFIXES or path.name in EXCLUDE_FILENAMES:
        return True

    return False


def should_include_rel(rel: str) -> bool:
    """Return whether a repo-relative file path belongs in MANIFEST.sha256.

    Exposed as a small predicate so release packaging can be checked against
    manifest scope directly instead of relying on parallel hand-maintained
    exclude lists. ``rel`` must be a POSIX-style path relative to the repo root.
    """

    rel = release_path_policy.normalize_release_rel(rel)
    if is_local_only_rel(rel):
        return False
    if release_path_policy.release_path_problem(rel):
        return False
    return True


def governed_path_problem(rel: str) -> str | None:
    """Return a release-path problem for non-local-only paths, if any."""

    rel = release_path_policy.normalize_release_rel(rel)
    if is_local_only_rel(rel):
        return None
    return release_path_policy.release_path_problem(rel)



def _manifest_control_path(path: Path | str | None = None) -> Path:
    """Return the manifest control-file path without resolving symlinks."""

    if path is not None:
        return _absolute_lexical_path(Path(_decode_pathlike(path)))
    repo_root = _preflight_manifest_root_path(ROOT)
    return repo_root / release_control_files.MANIFEST_NAME


def _manifest_control_target_problems(path: Path | str, *, allow_missing: bool) -> list[str]:
    """Return problems for the MANIFEST.sha256 control-file route."""

    lexical = _absolute_lexical_path(Path(_decode_pathlike(path)))
    problems: list[str] = []

    try:
        parent_fd = _open_directory_route_no_symlinks(
            lexical.parent,
            f"{release_control_files.MANIFEST_NAME}: manifest control parent ancestry",
        )
    except SystemExit as exc:
        return [str(exc)]
    else:
        try:
            os.close(parent_fd)
        except OSError:
            pass

    try:
        st = lexical.lstat()
    except FileNotFoundError:
        if allow_missing:
            return []
        return [f"{release_control_files.MANIFEST_NAME} missing"]
    except OSError as exc:
        return [f"could not stat {release_control_files.MANIFEST_NAME}: {exc}"]

    if stat.S_ISLNK(st.st_mode):
        problems.append(f"{release_control_files.MANIFEST_NAME} control file must not be a symlink: {lexical}")
    elif not stat.S_ISREG(st.st_mode):
        problems.append(f"{release_control_files.MANIFEST_NAME} control file must be a regular file: {lexical}")
    return problems


def _open_manifest_control_fd(path: Path | str) -> tuple[int, os.stat_result]:
    """Open MANIFEST.sha256 through a no-symlink route and return its fd/stat."""

    lexical = _absolute_lexical_path(Path(_decode_pathlike(path)))
    problems = _manifest_control_target_problems(lexical, allow_missing=False)
    if problems:
        raise SystemExit("\n".join(problems[:20]))

    parent_fd = _open_directory_route_no_symlinks(
        lexical.parent,
        f"{release_control_files.MANIFEST_NAME}: manifest control parent ancestry",
    )
    fd = -1
    try:
        before = lexical.lstat()
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        if hasattr(os, "O_NONBLOCK"):
            flags |= os.O_NONBLOCK
        try:
            if os.open in getattr(os, "supports_dir_fd", set()):
                fd = os.open(lexical.name, flags, dir_fd=parent_fd)
            else:  # pragma: no cover - fallback for runtimes without dir_fd support
                fd = os.open(lexical, flags)
        except OSError as exc:
            raise SystemExit(
                f"{release_control_files.MANIFEST_NAME} control file could not be opened without following symlinks: {exc}"
            ) from exc
        try:
            opened = os.fstat(fd)
        except OSError as exc:
            os.close(fd)
            fd = -1
            raise SystemExit(f"could not stat open {release_control_files.MANIFEST_NAME}: {exc}") from exc
        if not stat.S_ISREG(opened.st_mode):
            os.close(fd)
            fd = -1
            raise SystemExit(f"{release_control_files.MANIFEST_NAME} control file did not open as a regular file")
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            os.close(fd)
            fd = -1
            raise SystemExit(f"{release_control_files.MANIFEST_NAME} control file changed before open")
        out = fd
        fd = -1
        return out, opened
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.close(parent_fd)
        except OSError:
            pass


def read_manifest_control_bytes(path: Path | str | None = None) -> bytes:
    """Read MANIFEST.sha256 through the same no-symlink boundary as members."""

    control_path = _manifest_control_path(path)
    fd, open_stat = _open_manifest_control_fd(control_path)
    chunks: list[bytes] = []
    total = 0
    try:
        with os.fdopen(fd, "rb") as f:
            fd = -1
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                chunks.append(chunk)
                total += len(chunk)
            try:
                read_stat = os.fstat(f.fileno())
            except OSError as exc:
                raise SystemExit(f"could not restat {release_control_files.MANIFEST_NAME} after read: {exc}") from exc
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass

    if (open_stat.st_dev, open_stat.st_ino) != (read_stat.st_dev, read_stat.st_ino):
        raise SystemExit(f"{release_control_files.MANIFEST_NAME} control file identity changed while being read")
    if open_stat.st_size != read_stat.st_size or read_stat.st_size != total:
        raise SystemExit(
            f"{release_control_files.MANIFEST_NAME} control file changed size while being read "
            f"(before={open_stat.st_size}, after={read_stat.st_size}, read={total})"
        )
    return b"".join(chunks)


def write_manifest_control_bytes(data: bytes, path: Path | str | None = None) -> Path:
    """Atomically publish MANIFEST.sha256 without following control-file symlinks."""

    control_path = _manifest_control_path(path)
    problems = _manifest_control_target_problems(control_path, allow_missing=True)
    if problems:
        raise SystemExit("\n".join(problems[:20]))

    parent_fd = _open_directory_route_no_symlinks(
        control_path.parent,
        f"{release_control_files.MANIFEST_NAME}: manifest control parent ancestry",
    )
    tmp_name = ""
    tmp_fd = -1
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        for candidate in tempfile._get_candidate_names():  # noqa: SLF001 - stdlib temp names, no third-party dependency
            name = f".{control_path.name}.tmp.{candidate}"
            try:
                if os.open in getattr(os, "supports_dir_fd", set()):
                    tmp_fd = os.open(name, flags, 0o644, dir_fd=parent_fd)
                else:  # pragma: no cover - fallback for runtimes without dir_fd support
                    tmp_fd = os.open(control_path.parent / name, flags, 0o644)
            except FileExistsError:
                continue
            tmp_name = name
            break
        if tmp_fd < 0 or not tmp_name:
            raise SystemExit(f"could not create temporary {release_control_files.MANIFEST_NAME} sibling")

        with os.fdopen(tmp_fd, "wb") as f:
            tmp_fd = -1
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass

        problems = _manifest_control_target_problems(control_path, allow_missing=True)
        if problems:
            raise SystemExit("\n".join(problems[:20]))

        if os.replace in getattr(os, "supports_dir_fd", set()) or "src_dir_fd" in getattr(os.replace, "__text_signature__", ""):
            os.replace(tmp_name, control_path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        else:  # pragma: no cover - fallback for runtimes without dir_fd support
            os.replace(control_path.parent / tmp_name, control_path)
        tmp_name = ""
        try:
            final = control_path.lstat()
        except OSError as exc:
            raise SystemExit(f"could not stat written {release_control_files.MANIFEST_NAME}: {exc}") from exc
        if not stat.S_ISREG(final.st_mode) or stat.S_ISLNK(final.st_mode):
            raise SystemExit(f"written {release_control_files.MANIFEST_NAME} control file is not a regular file")
        try:
            control_path.chmod(0o644, follow_symlinks=False)
        except TypeError:  # pragma: no cover - older Python without follow_symlinks argument
            control_path.chmod(0o644)
        return control_path
    finally:
        if tmp_fd >= 0:
            try:
                os.close(tmp_fd)
            except OSError:
                pass
        if tmp_name:
            try:
                if os.unlink in getattr(os, "supports_dir_fd", set()):
                    os.unlink(tmp_name, dir_fd=parent_fd)
                else:  # pragma: no cover
                    (control_path.parent / tmp_name).unlink()
            except FileNotFoundError:
                pass
            except OSError:
                pass
        try:
            os.close(parent_fd)
        except OSError:
            pass


def build_manifest_entries() -> dict[str, str]:
    """Return the manifest entry map, rejecting unsafe release-scope file types.

    Path.rglob()/Path.is_file() follow symlinks by default.  Release artifacts
    must be self-contained ordinary files, so the builder itself must fail
    closed on release-scope symlinks or special files rather than relying only
    on a separate gate step.
    """

    repo_root = _preflight_manifest_root_path(ROOT)

    entries: dict[str, str] = {}
    candidate_rels: list[str] = []
    file_type_problems: list[str] = []
    for p in repo_root.rglob("*"):
        try:
            rel = p.relative_to(repo_root).as_posix()
        except ValueError:  # pragma: no cover - defensive for unusual roots
            continue
        rel = release_path_policy.normalize_release_rel(rel)
        path_problem = governed_path_problem(rel)
        if path_problem:
            file_type_problems.append(f"unsafe release-scope path cannot be manifested: {rel}: {path_problem}")
            continue
        if p.is_symlink():
            if should_include_rel(rel):
                file_type_problems.append(f"release-scope symlink cannot be manifested: {rel}")
            continue
        if p.is_dir():
            continue
        if not should_include_rel(rel):
            continue
        if not p.is_file():
            file_type_problems.append(f"release-scope path is not a regular file: {rel}")
            continue
        candidate_rels.append(rel)

    # Fail before hashing ordinary members when any governed special file,
    # symlink, or unsafe path is present.  The old path eventually failed too,
    # but it wasted time hashing the whole cube during negative-control probes
    # and made the filesystem-policy gate look hung on large revisions.
    if file_type_problems:
        raise SystemExit("\n".join(file_type_problems[:20]))

    for rel in candidate_rels:
        entries[rel] = file_sha256_for_rel(repo_root, rel)

    collisions = release_path_policy.find_portable_path_collisions(entries)
    if collisions:
        details = "; ".join(
            f"{key}: {', '.join(vals)}"
            for key, vals in sorted(collisions.items())[:10]
        )
        raise SystemExit(f"Portable release-path collision(s) detected: {details}")

    shape_conflicts = release_path_policy.find_extraction_shape_conflicts(entries)
    if shape_conflicts:
        details = "; ".join(
            f"{prefix}: {', '.join(children)}"
            for prefix, children in sorted(shape_conflicts.items())[:10]
        )
        raise SystemExit(f"Release extraction shape conflict(s) detected: {details}")

    return entries


def build_manifest_text() -> str:
    return release_control_files.format_manifest_text(build_manifest_entries())


def build_manifest_bytes() -> bytes:
    """Return canonical LF-only MANIFEST.sha256 bytes.

    Keep this as bytes so checks/writes never depend on platform text newline
    translation.
    """

    return build_manifest_text().encode("utf-8")


def check_manifest_bytes() -> tuple[bool, bytes, bytes, list[str]]:
    """Compare the checked-in manifest to the expected canonical bytes."""

    expected = build_manifest_bytes()
    try:
        current = read_manifest_control_bytes()
    except SystemExit as exc:
        return False, expected, b"", [str(exc)]
    except FileNotFoundError:
        return False, expected, b"", ["MANIFEST.sha256 missing"]
    _entries, problems = release_control_files.parse_manifest_bytes(current)
    if current != expected and not problems:
        problems = ["MANIFEST.sha256 bytes differ from regenerated manifest"]
    return current == expected, expected, current, problems

def main() -> int:
    ap = argparse.ArgumentParser(description="Build or check MANIFEST.sha256")
    ap.add_argument("--check", action="store_true", help="fail if MANIFEST.sha256 does not match")
    args = ap.parse_args()

    manifest_bytes = build_manifest_bytes()

    if args.check:
        ok, expected, current, problems = check_manifest_bytes()
        if ok:
            print("PASS: MANIFEST.sha256 matches")
            return 0
        # Keep output small: emit a short summary without text-mode newline
        # normalization.
        want_n = expected.count(b"\n")
        cur_n = current.count(b"\n")
        print("FAIL: MANIFEST.sha256 does not match")
        print(f"  expected_entries: {want_n}")
        print(f"  current_entries:   {cur_n}")
        if problems:
            print("  canonicality:      " + "; ".join(problems[:3]))
        print("  hint: run scripts/build_manifest.py to regenerate")
        return 2

    out_path = write_manifest_control_bytes(manifest_bytes)
    entry_count = manifest_bytes.count(b"\n")
    print(f"Wrote {out_path} with {entry_count} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

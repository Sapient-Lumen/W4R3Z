#!/usr/bin/env python3
"""Verify and safely extract an Election Stack deterministic release ZIP.

This is a stdlib-only extraction helper for recipients who want the release
checks to happen before bytes are written into an output tree. It verifies the
ZIP artifact with scripts/verify_release_zip.py, creates each regular member
through no-follow extraction-directory routes, rechecks the extracted tree
with scripts/verify_manifest.py, then rechecks the temporary tree and publication-parent identities before
publishing the directory.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True

import release_path_policy
import verify_manifest
import verify_release_zip

CANONICAL_FILE_MODE = verify_manifest.CANONICAL_FILE_MODE
CANONICAL_DIR_MODE = verify_manifest.CANONICAL_DIR_MODE


@dataclass
class ExtractResult:
    ok: bool
    zip_path: str
    output_dir: str
    version: str | None = None
    zip_sha256: str = ""
    entries: int = 0
    manifest_entries: int = 0
    problems: list[str] = field(default_factory=list)


def _dir_is_empty(path: Path) -> bool:
    try:
        next(path.iterdir())
    except StopIteration:
        return True
    return False


def _lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving symlink components."""

    # Path.resolve() follows symlinks, which is exactly what the output-target
    # firewall must not do before it has inspected the operator-supplied path.
    return Path(os.path.abspath(os.fspath(path)))


def _raw_output_path_problems(output_arg: object) -> list[str]:
    """Return lexical problems in the operator-supplied output path.

    This must inspect the raw string before ``Path`` normalization.  ``pathlib``
    collapses components such as ``./`` on construction, which would otherwise
    let a path like ``out/./tree`` pass despite the extractor's promise that
    the audited publication route is the route the OS receives.
    """

    raw = os.fspath(output_arg)
    if raw == "":
        return ["output path must not be empty"]
    if "\x00" in raw:
        return ["output path must not contain NUL bytes"]

    sep = os.sep
    drive, tail = os.path.splitdrive(raw)
    if drive and tail in {"", sep}:
        return ["output path must not be a filesystem root"]
    if not drive and tail == sep:
        return ["output path must not be a filesystem root"]

    if sep:
        # Accept one leading separator as an absolute-path anchor, then inspect
        # the remaining components exactly as supplied.  Additional leading,
        # trailing, or interior separators create empty components and are not
        # canonical publication paths.
        if tail.startswith(sep):
            tail = tail[len(sep):]
        parts = tail.split(sep)
    else:  # pragma: no cover - os.sep is always non-empty on supported Python
        parts = [tail]

    if any(part == "" for part in parts):
        return ["output path must not contain empty separator components"]
    if any(part in {".", ".."} for part in parts):
        return ["output path must not contain current/parent traversal components"]

    altsep = os.altsep
    if altsep and altsep in raw:
        return ["output path must not contain alternate path separators"]

    return []


def _output_path_component_problems(output_arg: object) -> list[str]:
    """Return problems for unsafe output path components.

    The extractor writes into a temporary sibling and then publishes a verified
    tree.  The final path itself was already checked for being a symlink, but a
    symlinked parent component can still redirect the publication target.
    Reject raw lexical ``.``/``..``/empty components before any ``Path``
    normalization, then reject existing symlink components in the audited
    ancestry.
    """

    problems = _raw_output_path_problems(output_arg)
    if problems:
        return problems

    output_path = Path(output_arg)
    absolute = _lexical_absolute(output_path)
    chain = [absolute, *absolute.parents]
    for component in reversed(chain):
        try:
            is_link = component.is_symlink()
        except OSError as exc:
            problems.append(f"could not inspect output path component {component}: {exc}")
            continue
        if is_link:
            problems.append(f"output path must not traverse symlink component: {component}")
            break
    return problems


def _preflight_output(output_arg: object, out_root: Path, *, clean: bool) -> list[str]:
    """Reject unsafe or non-consensual output targets before extraction."""

    problems = _output_path_component_problems(output_arg)
    if problems:
        return problems
    output_path = Path(output_arg)
    if output_path.is_symlink() or out_root.is_symlink():
        return ["output path must not be a symlink"]
    if not out_root.exists():
        return []
    if not out_root.is_dir():
        return ["output path exists and is not a directory"]
    if not clean and not _dir_is_empty(out_root):
        return ["output directory exists and is not empty; use --clean to replace it"]
    return []

def _remove_empty_or_clean_output(
    output_arg: object,
    out_root: Path,
    *,
    clean: bool,
    output_parent: Path | None = None,
    output_parent_identity: tuple[int, int] | None = None,
) -> list[str]:
    """Prepare ``out_root`` for atomic temp-dir rename.

    When an output-parent identity is supplied, destructive cleanup is routed
    through that already-openable parent instead of a fresh parent pathname. A
    local replacement of the publication parent between extraction and cleanup
    must not redirect ``--clean`` deletion or the final rename target.
    """

    problems: list[str] = []
    # Recheck the user-supplied path immediately before publish so a local
    # symlink replacement between preflight and final rename is not followed.
    component_problems = _output_path_component_problems(output_arg)
    if component_problems:
        return component_problems
    output_path = Path(output_arg)
    if output_path.is_symlink() or out_root.is_symlink():
        return ["output path must not be a symlink"]

    parent_fd = -1
    child_name = out_root.name
    try:
        if output_parent is not None and output_parent_identity is not None and _supports_dir_fd_no_follow():
            try:
                parent_fd = _open_directory_no_follow(
                    output_parent,
                    "output parent directory",
                    output_parent_identity,
                )
            except OSError as exc:
                return [str(exc)]
            try:
                child_st = os.stat(child_name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                return []
            except OSError as exc:
                return [f"could not stat output path through pinned parent: {exc}"]
            if stat.S_ISLNK(child_st.st_mode):
                return ["output path must not be a symlink"]
            if not stat.S_ISDIR(child_st.st_mode):
                return ["output path exists and is not a directory"]

            child_fd = -1
            try:
                list_flags = os.O_RDONLY
                if hasattr(os, "O_DIRECTORY"):
                    list_flags |= os.O_DIRECTORY
                if hasattr(os, "O_NOFOLLOW"):
                    list_flags |= os.O_NOFOLLOW
                child_fd = os.open(child_name, list_flags, dir_fd=parent_fd)
                try:
                    child_entries = os.listdir(child_fd)
                except OSError as exc:
                    return [f"could not inspect output directory through pinned parent: {exc}"]
            except OSError as exc:
                return [f"could not open output directory through pinned parent: {exc}"]
            finally:
                if child_fd >= 0:
                    try:
                        os.close(child_fd)
                    except OSError:
                        pass

            if not child_entries:
                try:
                    os.rmdir(child_name, dir_fd=parent_fd)
                except OSError as exc:
                    problems.append(f"could not remove empty output directory before rename: {exc}")
                return problems

            if not clean:
                return ["output directory exists and is not empty; use --clean to replace it"]

            try:
                shutil.rmtree(child_name, dir_fd=parent_fd)
            except OSError as exc:
                problems.append(f"could not remove existing output directory: {exc}")
            return problems

        if output_parent is not None and output_parent_identity is not None:
            identity_problems = _directory_identity_problems(
                output_parent,
                output_parent_identity,
                "output parent directory",
            )
            if identity_problems:
                return identity_problems

        if not out_root.exists():
            return []
        if not out_root.is_dir():
            return ["output path exists and is not a directory"]

        if _dir_is_empty(out_root):
            try:
                out_root.rmdir()
            except OSError as exc:
                problems.append(f"could not remove empty output directory before rename: {exc}")
            return problems

        if not clean:
            return ["output directory exists and is not empty; use --clean to replace it"]

        try:
            shutil.rmtree(out_root)
        except OSError as exc:
            problems.append(f"could not remove existing output directory: {exc}")
        return problems
    finally:
        if parent_fd >= 0:
            try:
                os.close(parent_fd)
            except OSError:
                pass


def _canonicalize_release_directory_modes(root: Path) -> list[str]:
    """Set extracted release directories below ``root`` to the canonical mode."""

    problems: list[str] = []
    dirs = [root, *sorted((item for item in root.rglob("*") if item.is_dir()), key=lambda item: item.as_posix())]
    for p in dirs:
        try:
            os.chmod(p, CANONICAL_DIR_MODE)
        except OSError as exc:
            try:
                rel = "." if p == root else p.relative_to(root).as_posix()
            except ValueError:  # pragma: no cover - defensive
                rel = str(p)
            problems.append(f"{rel}: could not set canonical directory mode: {exc}")
    return problems


def _supports_dir_fd_no_follow() -> bool:
    """Return whether member extraction can use no-follow directory fds."""

    return os.open in getattr(os, "supports_dir_fd", set()) and hasattr(os, "O_DIRECTORY")


def _supports_dir_fd_rename() -> bool:
    """Return whether final publication can rename through a pinned parent fd."""

    return _supports_dir_fd_no_follow() and os.rename in getattr(os, "supports_dir_fd", set())


def _directory_open_flags() -> int:
    flags = getattr(os, "O_PATH", os.O_RDONLY)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _file_create_flags() -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _dir_identity_from_stat(st: os.stat_result) -> tuple[int, int]:
    """Return the stable local identity tuple used for extraction temp roots."""

    return (st.st_dev, st.st_ino)


def _directory_identity_problems(path: Path, expected: tuple[int, int], label: str) -> list[str]:
    """Return problems if ``path`` no longer names the expected directory.

    The safe extractor verifies a temporary tree before publication.  A later
    local replacement of that temp root with a symlink or different directory
    must not become the published release tree.
    """

    try:
        st = path.lstat()
    except OSError as exc:
        return [f"{label}: could not stat directory identity: {exc}"]
    if stat.S_ISLNK(st.st_mode):
        return [f"{label}: directory identity changed to a symlink before publication"]
    if not stat.S_ISDIR(st.st_mode):
        return [f"{label}: directory identity changed to a non-directory before publication"]
    actual = _dir_identity_from_stat(st)
    if actual != expected:
        return [f"{label}: directory identity changed before publication"]
    return []


def _capture_directory_identity(path: Path, label: str) -> tuple[tuple[int, int] | None, list[str]]:
    """Capture a concrete directory identity without accepting final symlinks."""

    try:
        st = path.lstat()
    except OSError as exc:
        return None, [f"{label}: could not stat directory identity: {exc}"]
    if stat.S_ISLNK(st.st_mode):
        return None, [f"{label}: must not be a symlink"]
    if not stat.S_ISDIR(st.st_mode):
        return None, [f"{label}: must be a directory"]
    return _dir_identity_from_stat(st), []


def _open_directory_no_follow(path: Path, label: str, expected_identity: tuple[int, int] | None = None) -> int:
    """Open an existing directory route without following symlinks."""

    flags = _directory_open_flags()
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise OSError(f"{label}: could not open directory without following symlinks: {exc}") from exc
    try:
        st = os.fstat(fd)
    except OSError as exc:
        os.close(fd)
        raise OSError(f"{label}: could not stat opened directory: {exc}") from exc
    if not stat.S_ISDIR(st.st_mode):
        os.close(fd)
        raise OSError(f"{label}: opened route is not a directory")
    if expected_identity is not None and _dir_identity_from_stat(st) != expected_identity:
        os.close(fd)
        raise OSError(f"{label}: directory identity changed before open")
    return fd


def _open_or_create_child_dir(parent_fd: int, name: str, rel: str) -> int:
    """Create/open one extraction directory component without following links."""

    try:
        os.mkdir(name, CANONICAL_DIR_MODE, dir_fd=parent_fd)
    except FileExistsError:
        pass
    except OSError as exc:
        raise OSError(f"{rel}: could not create extraction directory component {name!r}: {exc}") from exc

    try:
        child_fd = os.open(name, _directory_open_flags(), dir_fd=parent_fd)
    except OSError as exc:
        raise OSError(
            f"{rel}: could not open extraction directory component {name!r} without following symlinks: {exc}"
        ) from exc
    try:
        st = os.fstat(child_fd)
    except OSError as exc:
        os.close(child_fd)
        raise OSError(f"{rel}: could not stat extraction directory component {name!r}: {exc}") from exc
    if not stat.S_ISDIR(st.st_mode):
        os.close(child_fd)
        raise OSError(f"{rel}: extraction directory component {name!r} is not a directory")
    try:
        os.fchmod(child_fd, CANONICAL_DIR_MODE)
    except OSError:
        pass
    return child_fd


def _open_extraction_member_fd(tmp_root: Path, rel: str, tmp_root_identity: tuple[int, int]) -> int:
    """Open one member destination through no-follow ancestry and exclusive create."""

    rel = release_path_policy.normalize_release_rel(rel)
    path_problem = release_path_policy.release_path_problem(rel)
    if path_problem:
        raise OSError(f"unsafe member path after ZIP verification: {rel!r}: {path_problem}")
    parts = rel.split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise OSError(f"unsafe member path after ZIP verification: {rel!r}")

    identity_problems = _directory_identity_problems(tmp_root, tmp_root_identity, f"{rel}: extraction root")
    if identity_problems:
        raise OSError(identity_problems[0])

    if not _supports_dir_fd_no_follow():  # pragma: no cover - fallback for non-POSIX runtimes
        dest = release_path_policy.safe_extract_destination(tmp_root, rel)
        if dest is None:
            raise OSError(f"unsafe member path after ZIP verification: {rel!r}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        flags = _file_create_flags()
        fd = os.open(dest, flags, CANONICAL_FILE_MODE)
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            os.close(fd)
            raise OSError(f"{rel}: extraction destination did not open as a regular file")
        return fd

    dir_fd = _open_directory_no_follow(tmp_root, f"{rel}: extraction root", tmp_root_identity)
    try:
        for part in parts[:-1]:
            child_fd = _open_or_create_child_dir(dir_fd, part, rel)
            os.close(dir_fd)
            dir_fd = child_fd

        try:
            fd = os.open(parts[-1], _file_create_flags(), CANONICAL_FILE_MODE, dir_fd=dir_fd)
        except FileExistsError as exc:
            raise FileExistsError(f"duplicate extraction destination: {rel}") from exc
        except OSError as exc:
            raise OSError(f"{rel}: could not create extraction member without following symlinks: {exc}") from exc

        try:
            st = os.fstat(fd)
        except OSError as exc:
            os.close(fd)
            raise OSError(f"{rel}: could not stat extraction member after create: {exc}") from exc
        if not stat.S_ISREG(st.st_mode):
            os.close(fd)
            raise OSError(f"{rel}: extraction destination did not open as a regular file")
        try:
            os.fchmod(fd, CANONICAL_FILE_MODE)
        except OSError:
            pass
        return fd
    finally:
        try:
            os.close(dir_fd)
        except OSError:
            pass


def _copy_member(zf: zipfile.ZipFile, info: zipfile.ZipInfo, tmp_root: Path, tmp_root_identity: tuple[int, int]) -> list[str]:
    problems: list[str] = []
    rel = release_path_policy.normalize_release_rel(info.filename)
    if release_path_policy.release_path_problem(rel):
        return [f"unsafe member path after ZIP verification: {info.filename!r}"]

    fd = -1
    try:
        fd = _open_extraction_member_fd(tmp_root, rel, tmp_root_identity)
        with zf.open(info, "r") as src, os.fdopen(fd, "wb") as out:
            fd = -1
            shutil.copyfileobj(src, out, length=1024 * 1024)
            out.flush()
    except FileExistsError:
        problems.append(f"duplicate extraction destination: {info.filename}")
    except (OSError, zipfile.BadZipFile) as exc:
        problems.append(f"{info.filename}: could not extract member: {exc}")
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
    return problems


def _publish_verified_tree(
    tmp_root: Path,
    out_root: Path,
    output_parent: Path,
    output_parent_identity: tuple[int, int],
) -> list[str]:
    """Rename the verified temporary tree through the pinned output parent."""

    if tmp_root.parent != output_parent or out_root.parent != output_parent:
        return ["temporary extraction root and output path must share the pinned output parent"]

    identity_problems = _directory_identity_problems(
        output_parent,
        output_parent_identity,
        "output parent directory",
    )
    if identity_problems:
        return identity_problems

    if _supports_dir_fd_rename():
        parent_fd = -1
        try:
            parent_fd = _open_directory_no_follow(
                output_parent,
                "output parent directory",
                output_parent_identity,
            )
            os.rename(tmp_root.name, out_root.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
            return []
        except OSError as exc:
            return [f"could not rename verified extraction into place through pinned output parent: {exc}"]
        finally:
            if parent_fd >= 0:
                try:
                    os.close(parent_fd)
                except OSError:
                    pass

    # Non-POSIX fallback: keep the older rename behavior, but retain an identity
    # recheck immediately before the path-based operation.
    identity_problems = _directory_identity_problems(
        output_parent,
        output_parent_identity,
        "output parent directory",
    )
    if identity_problems:
        return identity_problems
    try:
        tmp_root.rename(out_root)
    except OSError as exc:
        return [f"could not rename verified extraction into place: {exc}"]
    return []


def extract_release_zip(zip_path: Path, output_dir: object, *, clean: bool = False) -> ExtractResult:
    """Verify ``zip_path`` and safely extract it into ``output_dir``.

    The output directory is populated through a temporary sibling directory and
    renamed into place only after both artifact-level ZIP verification and
    extracted-tree manifest verification pass.
    """

    zip_arg = os.fspath(zip_path)
    output_arg = os.fspath(output_dir)
    output_path = Path(output_arg)
    # Keep the operator-supplied output path lexical until the ancestry
    # firewall has run.  ``Path.resolve()`` follows symlinks and can hide the
    # very publication route this extractor is supposed to reject.
    out_root = _lexical_absolute(output_path)
    problems: list[str] = []

    # Preserve the raw operator-supplied ZIP path for the verifier.  The
    # verifier rejects lexical ambiguity and symlink routing before it snapshots
    # bytes; resolving here would erase that audit boundary.
    zip_result = verify_release_zip.verify_zip(zip_arg)
    if not zip_result.ok:
        return ExtractResult(
            ok=False,
            zip_path=zip_arg,
            output_dir=str(out_root),
            version=zip_result.version,
            zip_sha256=zip_result.zip_sha256,
            entries=zip_result.entries,
            manifest_entries=zip_result.manifest_entries,
            problems=["release ZIP verification failed before extraction"] + zip_result.problems,
        )

    # Run output-target preflight before creating any output parent directory.
    # Earlier versions could reject a symlinked/lexically unsafe path only after
    # resolving it and attempting parent creation, which could leave local
    # directories behind on failure.  The extractor should have no filesystem
    # side effects for syntactically unsafe or symlink-routed output targets.
    problems.extend(_output_path_component_problems(output_arg))
    parent = out_root.parent
    if not problems:
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            problems.append(f"could not create output parent directory: {exc}")

    if not problems:
        problems.extend(_preflight_output(output_arg, out_root, clean=clean))

    output_parent_identity: tuple[int, int] | None = None
    if not problems:
        output_parent_identity, parent_identity_problems = _capture_directory_identity(
            parent,
            "output parent directory",
        )
        problems.extend(parent_identity_problems)

    if problems:
        return ExtractResult(False, zip_arg, str(out_root), zip_result.version, zip_result.zip_sha256, zip_result.entries, zip_result.manifest_entries, problems)

    try:
        tmp_name = tempfile.mkdtemp(prefix=f".{out_root.name}.extract.", dir=str(parent))
    except OSError as exc:
        return ExtractResult(False, zip_arg, str(out_root), zip_result.version, zip_result.zip_sha256, zip_result.entries, zip_result.manifest_entries, [f"could not create temporary extraction directory: {exc}"])

    tmp_root = _lexical_absolute(Path(tmp_name))
    tmp_root_identity, identity_problems = _capture_directory_identity(tmp_root, "temporary extraction root")
    problems.extend(identity_problems)
    if output_parent_identity is None:
        problems.append("output parent directory identity was not captured before temporary extraction")
    else:
        problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))
    committed = False
    try:
        if not problems:
            try:
                with zipfile.ZipFile(io.BytesIO(zip_result.zip_bytes)) as zf:
                    for info in zf.infolist():
                        if tmp_root_identity is None:
                            problems.append("temporary extraction root identity was not captured before member writes")
                            break
                        problems.extend(_copy_member(zf, info, tmp_root, tmp_root_identity))
            except (OSError, zipfile.BadZipFile) as exc:
                problems.append(f"could not open/read verified ZIP during extraction: {exc}")

        if not problems and tmp_root_identity is not None:
            problems.extend(_directory_identity_problems(tmp_root, tmp_root_identity, "temporary extraction root"))
        if not problems and output_parent_identity is not None:
            problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))

        if not problems:
            problems.extend(_canonicalize_release_directory_modes(tmp_root))

        if not problems and tmp_root_identity is not None:
            problems.extend(_directory_identity_problems(tmp_root, tmp_root_identity, "temporary extraction root"))
        if not problems and output_parent_identity is not None:
            problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))

        if not problems:
            tree_result = verify_manifest.verify_tree(tmp_root)
            if not tree_result.ok:
                problems.append("extracted-tree manifest verification failed after extraction")
                problems.extend(tree_result.problems)

        if not problems and tmp_root_identity is not None:
            problems.extend(_directory_identity_problems(tmp_root, tmp_root_identity, "temporary extraction root"))
        if not problems and output_parent_identity is not None:
            problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))

        if not problems:
            problems.extend(
                _remove_empty_or_clean_output(
                    output_arg,
                    out_root,
                    clean=clean,
                    output_parent=parent,
                    output_parent_identity=output_parent_identity,
                )
            )

        if not problems and tmp_root_identity is not None:
            problems.extend(_directory_identity_problems(tmp_root, tmp_root_identity, "temporary extraction root"))
        if not problems and output_parent_identity is not None:
            problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))

        if not problems and output_parent_identity is not None:
            publish_problems = _publish_verified_tree(tmp_root, out_root, parent, output_parent_identity)
            problems.extend(publish_problems)
            committed = not publish_problems

        if not problems and output_parent_identity is not None:
            problems.extend(_directory_identity_problems(parent, output_parent_identity, "output parent directory"))
        if not problems and tmp_root_identity is not None:
            problems.extend(_directory_identity_problems(out_root, tmp_root_identity, "published output root"))
    finally:
        if not committed:
            shutil.rmtree(tmp_root, ignore_errors=True)

    return ExtractResult(
        ok=not problems,
        zip_path=zip_arg,
        output_dir=str(out_root),
        version=zip_result.version,
        zip_sha256=zip_result.zip_sha256,
        entries=zip_result.entries,
        manifest_entries=zip_result.manifest_entries,
        problems=problems,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify and safely extract an Election Stack release ZIP")
    ap.add_argument("zip", help="release ZIP path")
    ap.add_argument("output_dir", help="directory to populate after verification")
    ap.add_argument("--clean", action="store_true", help="replace an existing non-empty output directory after verification succeeds")
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    args = ap.parse_args()

    # Pass the raw argparse string, not Path(args.zip), so the ZIP verifier
    # can audit lexical input spellings such as ./, ../, and repeated
    # separators before pathlib normalization.
    result = extract_release_zip(args.zip, args.output_dir, clean=args.clean)
    if args.json:
        print(json.dumps({
            "ok": result.ok,
            "zip_path": result.zip_path,
            "output_dir": result.output_dir,
            "version": result.version,
            "zip_sha256": result.zip_sha256,
            "entries": result.entries,
            "manifest_entries": result.manifest_entries,
            "problems": result.problems,
        }, sort_keys=True))
        return 0 if result.ok else 2

    if result.ok:
        if not args.quiet:
            print(
                "PASS: verified ZIP safely extracted "
                f"(version={result.version}, entries={result.entries}, "
                f"manifest_entries={result.manifest_entries}, output={result.output_dir})"
            )
        return 0

    print("FAIL: release ZIP was not extracted", file=sys.stderr)
    for problem in result.problems[:100]:
        print(f"  - {problem}", file=sys.stderr)
    if len(result.problems) > 100:
        print(f"  ... {len(result.problems) - 100} more", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

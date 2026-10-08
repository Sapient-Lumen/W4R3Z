from __future__ import annotations

"""Immutable, bounded plugin-package byte snapshots.

A restricted-workspace load grant is meaningful only when the bytes checked are
also the bytes evaluated.  This module owns the package walk, digest, and exact
byte snapshot so plugin source and package-local includes do not cross a
check-to-use gap by returning to the live filesystem after approval.
"""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Iterable

from micromax.vm import MicromaxError

from .plugin_io import DEFAULT_PLUGIN_MAX_BYTES, plugin_root_path, read_plugin_bytes
from .file_write import FileContainmentError


PLUGIN_PACKAGE_MAX_FILES = 512
PLUGIN_PACKAGE_MAX_TOTAL_BYTES = 8 * DEFAULT_PLUGIN_MAX_BYTES
PLUGIN_PACKAGE_MAX_RETAINED_BYTES = 64 * DEFAULT_PLUGIN_MAX_BYTES
PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS = 5.0


def _absolute_lexical(path: str | Path) -> Path:
    """Return a normalized absolute path without following symlink targets."""

    p = Path(path).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    # ``abspath`` collapses ``.`` and ``..`` lexically but, unlike ``resolve``,
    # never consults a namespace that may change after package capture.
    return Path(os.path.abspath(os.fspath(p)))


def plugin_package_paths(
    name: str,
    root: str | Path,
    init_path: str | Path,
    *,
    max_files: int,
) -> list[Path]:
    """Return contained regular package paths, capped by file count."""

    rootp = plugin_root_path(root)
    init = Path(init_path)
    paths: list[Path] = []
    try:
        iterator = rootp.rglob("*")
    except OSError as e:
        raise MicromaxError(f"plugin fingerprint: cannot scan {name}: {e}") from e
    for path in iterator:
        try:
            if path.is_dir():
                continue
            if not path.is_file():
                continue
            path.relative_to(rootp)
        except Exception as e:
            raise MicromaxError(f"plugin fingerprint: file outside plugin root: {path}") from e
        paths.append(path)
        if max_files >= 0 and len(paths) > max_files:
            raise MicromaxError(
                f"plugin fingerprint: too many files for {name}: {len(paths)} > {max_files}"
            )
    if init not in paths:
        paths.append(init)
        if max_files >= 0 and len(paths) > max_files:
            raise MicromaxError(
                f"plugin fingerprint: too many files for {name}: {len(paths)} > {max_files}"
            )
    return sorted(set(paths), key=lambda p: p.relative_to(rootp).as_posix())


def _package_digest(files: Iterable[tuple[str, bytes]]) -> str:
    h = hashlib.sha256()
    for rel, data in files:
        file_hash = hashlib.sha256(data).hexdigest()
        h.update(str(rel).encode("utf-8", "surrogateescape"))
        h.update(b"\0")
        h.update(str(len(data)).encode("ascii"))
        h.update(b"\0")
        h.update(file_hash.encode("ascii"))
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


@dataclass(frozen=True)
class PluginPackageSnapshot:
    """Exact package bytes approved for one plugin generation."""

    name: str
    root: str
    digest: str
    files: tuple[tuple[str, bytes], ...]
    total_bytes: int

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def root_path(self) -> Path:
        return Path(self.root)

    def relative_name(self, path: str | Path) -> str:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.root_path / p
        absolute = _absolute_lexical(p)
        try:
            return absolute.relative_to(self.root_path).as_posix()
        except Exception as e:
            raise FileContainmentError(
                f"path escapes containment root: {absolute} (root {self.root_path})"
            ) from e

    def absolute_path(self, relative: str | Path) -> Path:
        rel = Path(str(relative))
        if rel.is_absolute():
            absolute = _absolute_lexical(rel)
        else:
            absolute = _absolute_lexical(self.root_path / rel)
        try:
            absolute.relative_to(self.root_path)
        except Exception as e:
            raise FileContainmentError(
                f"path escapes containment root: {absolute} (root {self.root_path})"
            ) from e
        return absolute

    def contains_relative(self, relative: str | Path) -> bool:
        try:
            rel = self.relative_name(self.absolute_path(relative))
        except Exception:
            return False
        return any(name == rel for name, _data in self.files)

    def contains_path(self, path: str | Path) -> bool:
        try:
            rel = self.relative_name(path)
        except Exception:
            return False
        return any(name == rel for name, _data in self.files)

    def read_bytes(self, path: str | Path) -> bytes:
        rel = self.relative_name(path)
        for name, data in self.files:
            if name == rel:
                return bytes(data)
        raise FileNotFoundError(f"file not present in approved plugin snapshot: {path}")

    def read_text(
        self,
        path: str | Path,
        *,
        encoding: str = "utf-8",
        max_bytes: int | None = None,
    ) -> str:
        data = self.read_bytes(path)
        if max_bytes is not None and int(max_bytes) >= 0 and len(data) > int(max_bytes):
            raise MicromaxError(f"plugin source file too large: {path}")
        try:
            return data.decode(str(encoding))
        except UnicodeDecodeError as e:
            raise MicromaxError(f"plugin file is not {encoding}: {path}") from e

    def optional_text(self, relative: str | Path, *, encoding: str = "utf-8") -> str | None:
        path = self.absolute_path(relative)
        if not self.contains_path(path):
            return None
        return self.read_text(path, encoding=encoding)

    def resolve_source(self, raw: str | Path, *, span_filename: str = "") -> Path:
        """Resolve a package-local source request against captured files only."""

        raw_path = Path(str(raw)).expanduser()
        if raw_path.is_absolute():
            candidate = self.absolute_path(raw_path)
            if self.contains_path(candidate):
                return candidate
            raise FileNotFoundError(
                f"file not found in approved plugin snapshot {self.name}: {raw}"
            )

        candidates: list[Path] = []
        if span_filename and not str(span_filename).startswith("<"):
            try:
                span_path = self.absolute_path(span_filename)
                span_dir = span_path.parent
                span_dir.relative_to(self.root_path)
                candidates.append(self.absolute_path(span_dir / raw_path))
            except FileContainmentError:
                pass
        candidates.append(self.absolute_path(self.root_path / raw_path))

        seen: set[str] = set()
        for candidate in candidates:
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            if self.contains_path(candidate):
                return candidate
        preview = ", ".join(str(path) for path in candidates[:4])
        raise FileNotFoundError(
            f"file not found in approved plugin snapshot {self.name}: {raw} (searched: {preview})"
        )


def plugin_package_snapshot_inline(
    name: str,
    root: str | Path,
    init_path: str | Path,
    *,
    max_files: int,
    max_total_bytes: int,
) -> PluginPackageSnapshot:
    """Read one exact, bounded package generation and return its digest."""

    rootp = plugin_root_path(root)
    rows: list[tuple[str, bytes]] = []
    total_bytes = 0
    for path in plugin_package_paths(str(name), rootp, init_path, max_files=int(max_files)):
        rel = path.relative_to(rootp).as_posix()
        data = read_plugin_bytes(path, rootp)
        total_bytes += len(data)
        if max_total_bytes >= 0 and total_bytes > max_total_bytes:
            raise MicromaxError(
                f"plugin fingerprint: package too large for {name}: "
                f"{total_bytes} > {max_total_bytes} bytes"
            )
        rows.append((rel, data))
    frozen_rows = tuple(rows)
    return PluginPackageSnapshot(
        name=str(name),
        root=str(rootp),
        digest=_package_digest(frozen_rows),
        files=frozen_rows,
        total_bytes=int(total_bytes),
    )


def plugin_package_fingerprint_inline(
    name: str,
    root: str | Path,
    init_path: str | Path,
    *,
    max_files: int,
    max_total_bytes: int,
) -> tuple[str, int]:
    snapshot = plugin_package_snapshot_inline(
        name,
        root,
        init_path,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
    )
    return snapshot.digest, snapshot.file_count


def plugin_package_fingerprint_worker(
    name: str,
    root: str,
    init_path: str,
    max_files: int,
    max_total_bytes: int,
    queue: object,
) -> None:
    try:
        digest, count = plugin_package_fingerprint_inline(
            name,
            root,
            init_path,
            max_files=max_files,
            max_total_bytes=max_total_bytes,
        )
        queue.put(("ok", digest, int(count)))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


def plugin_package_snapshot_worker(
    name: str,
    root: str,
    init_path: str,
    max_files: int,
    max_total_bytes: int,
    queue: object,
) -> None:
    try:
        snapshot = plugin_package_snapshot_inline(
            name,
            root,
            init_path,
            max_files=max_files,
            max_total_bytes=max_total_bytes,
        )
        queue.put(("ok", snapshot))
    except BaseException as e:  # pragma: no cover - serialized to parent.
        queue.put(("err", type(e).__name__, str(e)))


__all__ = [
    "PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS",
    "PLUGIN_PACKAGE_MAX_FILES",
    "PLUGIN_PACKAGE_MAX_RETAINED_BYTES",
    "PLUGIN_PACKAGE_MAX_TOTAL_BYTES",
    "PluginPackageSnapshot",
    "plugin_package_fingerprint_inline",
    "plugin_package_fingerprint_worker",
    "plugin_package_paths",
    "plugin_package_snapshot_inline",
    "plugin_package_snapshot_worker",
]

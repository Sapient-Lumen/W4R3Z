from __future__ import annotations

"""Contained plugin metadata/source I/O helpers.

Plugins are extension code once the user has selected a plugin root, but plugin
loading should still not silently follow symlink escapes outside an individual
plugin directory.  Keep the read seam small and reuse the editor's fd-contained
file-access helper so metadata and source reads are bound to the opened file
before evaluation.
"""

from pathlib import Path

from micromax.vm import MicromaxError

from .file_access import FileTooLargeError, NotARegularFileError, read_file_bytes_contained, stat_path_contained
from .file_write import FileContainmentError, assert_path_within_root

DEFAULT_PLUGIN_MAX_BYTES = 1024 * 1024


def plugin_root_path(root: str | Path) -> Path:
    """Return a stable best-effort absolute plugin directory root."""

    p = Path(root).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.resolve()
    except OSError:
        return p.absolute()


def assert_plugin_path(path: str | Path, root: str | Path) -> None:
    """Raise ``MicromaxError`` if *path* is outside the plugin directory root."""

    try:
        assert_path_within_root(path, plugin_root_path(root))
    except FileContainmentError as e:
        raise MicromaxError(f"plugin file outside plugin root: {e}") from e


def plugin_file_exists(path: str | Path, root: str | Path) -> bool:
    """Return whether a contained regular plugin file exists."""

    p = Path(path)
    try:
        root_path = plugin_root_path(root)
        assert_plugin_path(p, root_path)
        row = stat_path_contained(p, containment_root=root_path)
    except MicromaxError:
        raise
    except Exception:
        return False
    return bool(row.exists and row.kind == "file")


def read_plugin_text(
    path: str | Path,
    root: str | Path,
    *,
    encoding: str = "utf-8",
    max_bytes: int = DEFAULT_PLUGIN_MAX_BYTES,
) -> str:
    """Read one plugin metadata/source file through a containment boundary."""

    p = Path(path)
    try:
        root_path = plugin_root_path(root)
        assert_plugin_path(p, root_path)
        result = read_file_bytes_contained(p, containment_root=root_path, max_bytes=int(max_bytes))
    except FileContainmentError as e:
        raise MicromaxError(f"plugin file outside plugin root: {e}") from e
    except FileTooLargeError as e:
        raise MicromaxError(f"plugin file too large: {p}") from e
    except NotARegularFileError as e:
        raise MicromaxError(f"plugin file is not a regular file: {p}") from e
    except UnicodeDecodeError:
        raise
    except MicromaxError:
        raise
    try:
        return result.data.decode(str(encoding))
    except UnicodeDecodeError as e:
        raise MicromaxError(f"plugin file is not {encoding}: {p}") from e


__all__ = [
    "DEFAULT_PLUGIN_MAX_BYTES",
    "assert_plugin_path",
    "plugin_file_exists",
    "plugin_root_path",
    "read_plugin_text",
]

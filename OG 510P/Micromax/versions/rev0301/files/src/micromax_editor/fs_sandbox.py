from __future__ import annotations

"""micromax_editor.fs_sandbox

Helpers for capability-gated filesystem surfaces.

Why this exists
--------------

Micromax's VM is intentionally tiny and portable; the editor owns the host
world. When we expose filesystem helpers (fs-read/fs-list/fs-stat) we keep them
*capability-gated* and also allow an optional **sandbox root**.

This module centralizes the "resolve path" and "is this allowed" logic so:

- hostcalls and UI helpers behave consistently
- tests can exercise the same policy
- future editors/ports can swap policy in one place

Policy
------

- If option `cap.fs-root` is empty: filesystem helpers behave like normal paths
  (relative to the current working directory).
- If `cap.fs-root` is set: relative paths are resolved relative to that root,
  and resolved absolute targets must remain within that root.

This is best-effort and intentionally conservative:
- `Path.resolve(strict=False)` is used so non-existent paths can still be checked.
- Symlinks that escape the root are treated as "outside".

The goal is not a perfect sandbox. It's a pragmatic, inspectable boundary that
makes it easier to keep "no ambient authority" discipline when capabilities are
enabled.
"""

from pathlib import Path
from typing import Any



def _get_opt(ed: Any, name: str) -> Any:
    """Best-effort option lookup that tolerates missing registries."""

    try:
        opts = getattr(ed, 'options', None)
        if opts is None:
            return ''
        return opts.get(str(name))
    except Exception:
        return ''


def fs_root(ed: Any) -> Path | None:
    """Return the configured filesystem sandbox root, or None.

    The root is expanded (`~`) and resolved to an absolute path.
    """

    raw = str(_get_opt(ed, "cap.fs-root") or "")
    raw = str(raw).strip()
    if not raw:
        return None

    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    try:
        return p.resolve()
    except Exception:
        try:
            return p.absolute()
        except Exception:
            return p


def resolve_path(ed: Any, raw_path: str) -> Path:
    """Resolve a user path according to `cap.fs-root`.

    - expands `~`
    - if `cap.fs-root` is set and the path is relative: resolve under the root
    - otherwise resolve relative to cwd
    - returns a best-effort resolved absolute path (strict=False)
    """

    s = str(raw_path or "")
    # Preserve empty/"." in a useful way for list/stat.
    if s.strip() == "":
        s = "."

    p = Path(s).expanduser()
    root = fs_root(ed)

    if root is not None and not p.is_absolute():
        p = root / p
    elif not p.is_absolute():
        p = Path.cwd() / p

    try:
        return p.resolve(strict=False)
    except TypeError:
        # Older Python fallback.
        try:
            return p.resolve()
        except Exception:
            try:
                return p.absolute()
            except Exception:
                return p


def is_allowed(ed: Any, p: Path) -> bool:
    """Return True if path p is within cap.fs-root (or no root is set)."""

    root = fs_root(ed)
    if root is None:
        return True

    try:
        pp = p.resolve(strict=False)
    except Exception:
        pp = p

    try:
        return pp.is_relative_to(root)
    except AttributeError:
        # Python <3.9 fallback.
        try:
            return str(pp).startswith(str(root))
        except Exception:
            return False
    except Exception:
        return False


def deny_reason(ed: Any, p: Path) -> str:
    root = fs_root(ed)
    if root is None:
        return ""
    return f"outside cap.fs-root ({root}): {p}"

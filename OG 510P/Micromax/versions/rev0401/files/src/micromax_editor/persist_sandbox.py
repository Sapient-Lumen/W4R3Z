from __future__ import annotations

"""micromax_editor.persist_sandbox

Helpers for editor-owned persistence files (recent/history).

Why this exists
--------------

The editor offers small opt-in persistence surfaces (e.g. recent-file MRU,
prompt history). These are extremely handy, but they touch the host filesystem.

To keep the "no ambient authority" story consistent, persistence is:

- gated by `cap.persist` (off by default)
- optionally constrained to a sandbox root `cap.persist-root`

This module centralizes the resolve + allow checks so:

- recent/history persistence share the same policy
- tests can exercise the same policy
- future hosts can swap or tighten policy in one place

Policy
------

- If `cap.persist-root` is empty: persistence paths resolve normally
  (relative to CWD).
- If `cap.persist-root` is set: relative persistence paths resolve under it,
  and resolved targets must remain within it.

As with `fs_sandbox`, this is best-effort and conservative: symlink escapes
are treated as "outside".
"""

from pathlib import Path
from typing import Any


def _get_opt(ed: Any, name: str) -> Any:
    try:
        opts = getattr(ed, 'options', None)
        if opts is None:
            return ''
        return opts.get(str(name))
    except Exception:
        return ''


def persist_root(ed: Any) -> Path | None:
    """Return the configured persistence sandbox root, or None."""

    raw = str(_get_opt(ed, 'cap.persist-root') or '')
    raw = raw.strip()
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
    """Resolve a persistence path according to `cap.persist-root`."""

    s = str(raw_path or '')
    if s.strip() == '':
        s = '.'

    p = Path(s).expanduser()
    root = persist_root(ed)

    if root is not None and not p.is_absolute():
        p = root / p
    elif not p.is_absolute():
        p = Path.cwd() / p

    try:
        return p.resolve(strict=False)
    except TypeError:
        try:
            return p.resolve()
        except Exception:
            try:
                return p.absolute()
            except Exception:
                return p


def is_allowed(ed: Any, p: Path) -> bool:
    root = persist_root(ed)
    if root is None:
        return True

    try:
        pp = p.resolve(strict=False)
    except Exception:
        pp = p

    try:
        return pp.is_relative_to(root)
    except AttributeError:
        try:
            return str(pp).startswith(str(root))
        except Exception:
            return False
    except Exception:
        return False


def deny_reason(ed: Any, p: Path) -> str:
    root = persist_root(ed)
    if root is None:
        return ''
    return f"outside cap.persist-root ({root}): {p}"

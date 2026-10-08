from __future__ import annotations

"""Runtime resource-root resolution for source checkouts and installed wheels.

Micromax's development tree keeps docs/plugins at the repository root, while a
wheel/``pip --target`` install can place those runtime files under
``share/micromax``.  Keep that distinction in one tiny module so the CLI, TUI,
and docs picker do not each invent a different fallback order.
"""

from pathlib import Path
import os
import sys
from typing import Iterable


_SHARE_ROOT = Path("share") / "micromax"


def _cwd_or_default(cwd: Path | None = None) -> Path:
    try:
        return cwd if cwd is not None else Path.cwd()
    except Exception:
        return Path(".")


def _resolve_user_path(value: str | os.PathLike[str], *, cwd: Path | None = None) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = _cwd_or_default(cwd) / p
    return p


def _dedupe(paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    for p in paths:
        try:
            key = str(p.resolve(strict=False))
        except Exception:
            key = str(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def micromax_share_roots() -> list[Path]:
    """Return plausible installed ``share/micromax`` directories.

    The first candidate handles ``pip install --target`` where the package and
    ``share/`` directory are siblings under the target root. The ``sys.prefix``
    candidates handle normal virtualenv/system installs. Finally, ``sys.path``
    entries cover explicit path-based launchers and tests that only set
    ``PYTHONPATH``.
    """

    candidates: list[Path] = []
    try:
        candidates.append(Path(__file__).resolve().parents[1] / _SHARE_ROOT)
    except Exception:
        pass

    for raw_prefix in (getattr(sys, "prefix", ""), getattr(sys, "base_prefix", "")):
        if raw_prefix:
            candidates.append(Path(str(raw_prefix)).expanduser() / _SHARE_ROOT)

    for raw in list(getattr(sys, "path", []) or []):
        if not raw:
            continue
        try:
            candidates.append(Path(str(raw)).expanduser() / _SHARE_ROOT)
        except Exception:
            continue

    return _dedupe(candidates)


def default_docs_root_candidates(*, cwd: Path | None = None) -> list[Path]:
    """Return default docs roots in precedence order, without requiring existence."""

    base = _cwd_or_default(cwd)
    candidates: list[Path] = [base / "docs"]
    candidates.extend(root / "docs" for root in micromax_share_roots())
    return _dedupe(candidates)


def default_plugins_root_candidates(*, cwd: Path | None = None) -> list[Path]:
    """Return default plugin roots in precedence order, without requiring existence."""

    base = _cwd_or_default(cwd)
    candidates: list[Path] = [base / "plugins"]
    candidates.extend(root / "plugins" for root in micromax_share_roots())
    return _dedupe(candidates)


def default_docs_root(raw: str | os.PathLike[str] | None = None, *, cwd: Path | None = None) -> Path:
    """Resolve the docs root.

    Explicit values and ``MICROMAX_DOCS`` remain literal. Only the implicit
    default falls back from ``./docs`` to an installed ``share/micromax/docs``
    resource tree.
    """

    if raw is not None:
        return _resolve_user_path(raw, cwd=cwd)
    env = os.environ.get("MICROMAX_DOCS")
    if env is not None:
        return _resolve_user_path(env, cwd=cwd)

    candidates = default_docs_root_candidates(cwd=cwd)
    for cand in candidates:
        try:
            if cand.is_dir():
                return cand
        except Exception:
            continue
    return candidates[0] if candidates else (_cwd_or_default(cwd) / "docs")


def default_plugins_root(raw: str | os.PathLike[str] | None = None, *, cwd: Path | None = None) -> Path:
    """Resolve the plugin root.

    A user-supplied ``--plugins`` path is respected exactly. The implicit default
    uses ``./plugins`` when present and otherwise falls back to an installed
    bundled plugin tree.
    """

    if raw is not None:
        return _resolve_user_path(raw, cwd=cwd)

    candidates = default_plugins_root_candidates(cwd=cwd)
    for cand in candidates:
        try:
            if cand.is_dir():
                return cand
        except Exception:
            continue
    return candidates[0] if candidates else (_cwd_or_default(cwd) / "plugins")

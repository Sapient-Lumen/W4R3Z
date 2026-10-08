from __future__ import annotations

"""Policy helpers for external URL opening.

The editor's URL-open capability is intentionally narrow: it is for ordinary
external links, not for arbitrary URI scheme dispatch.  Browsers and desktop
openers may attach powerful handlers to schemes such as ``file:``, ``ssh:``, or
application-specific custom schemes, so the editor validates the scheme before
it asks the host opener to do anything.
"""

from dataclasses import dataclass
from urllib.parse import urlsplit


DEFAULT_OPEN_URL_SCHEMES: frozenset[str] = frozenset({"http", "https", "mailto"})


@dataclass(frozen=True)
class ExternalUrlCheck:
    ok: bool
    url: str = ""
    reason: str = ""
    scheme: str = ""


def validate_external_url(
    url: object,
    *,
    allowed_schemes: frozenset[str] | set[str] | tuple[str, ...] | list[str] | None = None,
) -> ExternalUrlCheck:
    """Return a small validation witness for a URL about to leave the editor.

    The accepted set is deliberately small and documented: ``http``, ``https``,
    and ``mailto``.  The function also rejects control/whitespace characters so
    one human-visible URL cannot smuggle line-oriented prompts or logs around
    the confirmation boundary.
    """

    raw = str(url or "").strip()
    if not raw:
        return ExternalUrlCheck(False, reason="empty URL")
    if any((ord(ch) < 32 or ord(ch) == 127) for ch in raw):
        return ExternalUrlCheck(False, url=raw, reason="URL contains control characters")
    if any(ch.isspace() for ch in raw):
        return ExternalUrlCheck(False, url=raw, reason="URL contains whitespace")

    try:
        parts = urlsplit(raw)
    except Exception as e:
        return ExternalUrlCheck(False, url=raw, reason=f"invalid URL: {e}")

    scheme = str(parts.scheme or "").casefold()
    allowed = frozenset(str(s).casefold() for s in (allowed_schemes or DEFAULT_OPEN_URL_SCHEMES))
    if not scheme:
        return ExternalUrlCheck(False, url=raw, reason="URL is missing a scheme")
    if scheme not in allowed:
        return ExternalUrlCheck(False, url=raw, scheme=scheme, reason=f"unsupported URL scheme: {scheme}")

    if scheme in {"http", "https"} and not str(parts.netloc or "").strip():
        return ExternalUrlCheck(False, url=raw, scheme=scheme, reason=f"{scheme} URL is missing a host")
    if scheme == "mailto" and not (str(parts.path or "").strip() or str(parts.query or "").strip()):
        return ExternalUrlCheck(False, url=raw, scheme=scheme, reason="mailto URL is missing a recipient")

    return ExternalUrlCheck(True, url=raw, scheme=scheme)

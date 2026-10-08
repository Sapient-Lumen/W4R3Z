from __future__ import annotations

"""Process-bound identities for private save temporaries.

Atomic save residue is sensitive document data, so cleanup must be narrower
than an age-based glob.  Versioned temp names carry a random save lease plus a
Linux boot identity, PID-namespace identity, pid, and process start tick.  A
file is stale only when that tuple can be disproved from the same PID
namespace; unavailable or cross-namespace evidence stays ``unknown`` and is
never eligible for deletion.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
import errno
import hashlib
import os
from pathlib import Path
import re
import secrets
from typing import Iterator
import unicodedata


_UNKNOWN_BOOT = "x"
_UNKNOWN_PID_NAMESPACE = "x"
_DEFAULT_NAME_MAX = 255
_LEASE_RE = re.compile(r"^[0-9a-f]{32}$")
_RANDOM_RE = re.compile(r"^[0-9a-f]{16}$")
_TOKEN_RE = re.compile(r"^[0-9a-f]{16}$")
_TEMP_V3_RE = re.compile(
    r"^(?P<prefix>\..*)\.micromax-v3-"
    r"b(?P<boot>[0-9a-f]{16}|x)-"
    r"n(?P<namespace>[0-9a-f]{16}|x)-"
    r"p(?P<pid>[1-9][0-9]*)-"
    r"s(?P<start>[0-9]+)-"
    r"l(?P<lease>[0-9a-f]{32})-"
    r"r(?P<random>[0-9a-f]{16})\.tmp$"
)
_TEMP_V2_RE = re.compile(
    r"^(?P<prefix>\..*)\.micromax-v2-"
    r"b(?P<boot>[0-9a-f]{16}|x)-"
    r"p(?P<pid>[1-9][0-9]*)-"
    r"s(?P<start>[0-9]+)-"
    r"l(?P<lease>[0-9a-f]{32})-"
    r"r(?P<random>[0-9a-f]{16})\.tmp$"
)
_ACTIVE_LEASE: ContextVar[str | None] = ContextVar(
    "micromax_active_save_lease", default=None
)


class TempOwnerState(str, Enum):
    ACTIVE = "active"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProcessIdentity:
    boot_token: str
    pid: int
    start_ticks: int
    pid_namespace_token: str = _UNKNOWN_PID_NAMESPACE

    @property
    def reliable(self) -> bool:
        return (
            self.boot_token != _UNKNOWN_BOOT
            and _TOKEN_RE.fullmatch(self.boot_token) is not None
            and self.pid_namespace_token != _UNKNOWN_PID_NAMESPACE
            and _TOKEN_RE.fullmatch(self.pid_namespace_token) is not None
            and self.start_ticks > 0
            and self.pid > 0
        )


@dataclass(frozen=True)
class PrivateTempName:
    name: str
    safe_basename: str
    owner: ProcessIdentity
    lease_id: str
    random_token: str



def new_save_lease_id() -> str:
    """Return one unguessable 128-bit save transaction identifier."""

    return secrets.token_hex(16)



def normalize_save_lease_id(value: str | None, *, create: bool = False) -> str | None:
    raw = str(value or "").strip().lower()
    if not raw:
        return new_save_lease_id() if create else None
    if _LEASE_RE.fullmatch(raw) is None:
        raise ValueError("save lease id must be 32 lowercase hexadecimal characters")
    return raw


@contextmanager
def private_temp_lease(lease_id: str | None = None) -> Iterator[str]:
    """Bind every temp opened in the context to one save transaction."""

    normalized = normalize_save_lease_id(lease_id, create=True)
    assert normalized is not None
    token = _ACTIVE_LEASE.set(normalized)
    try:
        yield normalized
    finally:
        _ACTIVE_LEASE.reset(token)



def active_save_lease_id() -> str:
    current = _ACTIVE_LEASE.get()
    if current is not None:
        return current
    return new_save_lease_id()



def _boot_token() -> str:
    """Return a compact host-boot token, or ``x`` when no proof is available."""

    try:
        raw = Path("/proc/sys/kernel/random/boot_id").read_text(
            encoding="ascii", errors="strict"
        ).strip().lower()
    except (OSError, UnicodeError):
        return _UNKNOWN_BOOT
    if not raw:
        return _UNKNOWN_BOOT
    return hashlib.sha256(raw.encode("ascii")).hexdigest()[:16]



def _process_start_ticks(pid: int) -> int:
    """Read Linux ``/proc/<pid>/stat`` field 22 without trusting ``comm`` spaces."""

    raw = Path(f"/proc/{int(pid)}/stat").read_text(
        encoding="utf-8", errors="surrogateescape"
    )
    # Field 2 (comm) is parenthesized and may contain spaces.  Splitting after
    # the final ``) `` leaves field 3 (state) at index 0 and starttime at 19.
    close = raw.rfind(") ")
    if close < 0:
        raise OSError(f"unrecognized /proc/{int(pid)}/stat layout")
    fields = raw[close + 2 :].split()
    if len(fields) <= 19:
        raise OSError(f"truncated /proc/{int(pid)}/stat")
    value = int(fields[19])
    if value <= 0:
        raise OSError(f"invalid /proc/{int(pid)}/stat starttime")
    return value



def _pid_namespace_token(pid: int) -> str:
    """Return a compact identity for the process's permanent PID namespace."""

    path = f"/proc/{int(pid)}/ns/pid"
    try:
        link_value = os.readlink(path)
    except OSError:
        # On ordinary Linux, following the namespace handle yields the nsfs
        # device/inode pair documented by namespaces(7).  Some cloudtainer
        # procfs adapters synthesize a fresh stat inode on every lookup while
        # retaining the canonical ``pid:[N]`` link text, so prefer that text
        # when available and retain stat as the standards-based fallback.
        stat_result = os.stat(path, follow_symlinks=True)
        material = (
            f"{int(stat_result.st_dev)}:{int(stat_result.st_ino)}".encode("ascii")
        )
    else:
        if re.fullmatch(r"pid:\[[0-9]+\]", link_value) is None:
            raise OSError(f"unrecognized PID namespace handle: {link_value!r}")
        material = link_value.encode("ascii")
    return hashlib.sha256(material).hexdigest()[:16]



def current_process_identity() -> ProcessIdentity:
    pid = int(os.getpid())
    boot = _boot_token()
    try:
        start = _process_start_ticks(pid)
    except (OSError, ValueError):
        start = 0
    try:
        namespace = _pid_namespace_token(pid)
    except (OSError, ValueError):
        namespace = _UNKNOWN_PID_NAMESPACE
    return ProcessIdentity(
        boot_token=boot,
        pid=pid,
        start_ticks=start,
        pid_namespace_token=namespace,
    )



def temp_owner_state(identity: ProcessIdentity) -> TempOwnerState:
    """Classify one temp creator without treating missing evidence as stale."""

    if not identity.reliable:
        return TempOwnerState.UNKNOWN
    try:
        current_namespace = _pid_namespace_token(os.getpid())
    except (OSError, ValueError):
        return TempOwnerState.UNKNOWN
    if current_namespace != identity.pid_namespace_token:
        # A numeric PID is meaningful only inside its PID namespace.  A
        # different namespace may contain a live, unrelated process with the
        # same PID/start tuple, so a shared-volume cleanup must fail closed.
        return TempOwnerState.UNKNOWN
    current_boot = _boot_token()
    if current_boot == _UNKNOWN_BOOT:
        return TempOwnerState.UNKNOWN
    if current_boot != identity.boot_token:
        return TempOwnerState.STALE
    try:
        candidate_namespace = _pid_namespace_token(identity.pid)
    except FileNotFoundError:
        return TempOwnerState.STALE
    except ProcessLookupError:
        return TempOwnerState.STALE
    except (OSError, ValueError):
        return TempOwnerState.UNKNOWN
    if candidate_namespace != identity.pid_namespace_token:
        return TempOwnerState.UNKNOWN
    try:
        current_start = _process_start_ticks(identity.pid)
    except FileNotFoundError:
        return TempOwnerState.STALE
    except ProcessLookupError:
        return TempOwnerState.STALE
    except (OSError, ValueError):
        return TempOwnerState.UNKNOWN
    if current_start != identity.start_ticks:
        # The pid exists but belongs to a later process instance.
        return TempOwnerState.STALE
    return TempOwnerState.ACTIVE



def _safe_basename(value: str) -> str:
    safe = str(value or "file").replace(os.sep, "_")
    if os.altsep:
        safe = safe.replace(os.altsep, "_")
    # These names are surfaced in an interactive cleanup inventory.  Preserve
    # ordinary Unicode while preventing a hostile document basename from
    # injecting terminal/editor control lines or invisible bidirectional/format
    # state into that inventory.  Unicode format controls (category Cf) include
    # bidi overrides and isolates; surrogate code points and Unicode line/
    # paragraph separators are not safe display text either.
    unsafe_categories = {"Cc", "Cf", "Cs", "Zl", "Zp"}
    safe = "".join(
        "_" if unicodedata.category(character) in unsafe_categories else character
        for character in safe
    )
    return safe or "file"



def _name_max(parent: Path) -> int:
    try:
        value = int(os.pathconf(str(parent), "PC_NAME_MAX"))
    except (OSError, ValueError, TypeError, AttributeError):
        value = _DEFAULT_NAME_MAX
    return max(1, value)



def _truncate_component(value: str, max_bytes: int) -> str:
    encoded = os.fsencode(value)
    if len(encoded) <= max_bytes:
        return value
    digest = hashlib.sha256(encoded).hexdigest()[:12]
    tail = f"~{digest}"
    tail_bytes = os.fsencode(tail)
    if int(max_bytes) <= len(tail_bytes):
        return digest[: max(1, int(max_bytes))]
    budget = max(1, int(max_bytes) - len(tail_bytes))
    # Filesystem encodings can be multibyte.  Retain the largest character
    # prefix that fits rather than slicing encoded bytes into an invalid name.
    low = 0
    high = len(value)
    while low < high:
        middle = (low + high + 1) // 2
        if len(os.fsencode(value[:middle])) <= budget:
            low = middle
        else:
            high = middle - 1
    return value[:low] + tail



def build_private_temp_name(
    parent: str | Path,
    basename: str,
    *,
    lease_id: str | None = None,
    owner: ProcessIdentity | None = None,
    random_token: str | None = None,
) -> str:
    """Build a parseable private-temp name that fits the directory NAME_MAX."""

    identity = current_process_identity() if owner is None else owner
    lease = normalize_save_lease_id(lease_id, create=False) or active_save_lease_id()
    random_part = str(random_token or secrets.token_hex(8)).lower()
    if _RANDOM_RE.fullmatch(random_part) is None:
        raise ValueError("temp random token must be 16 lowercase hexadecimal characters")
    boot = (
        identity.boot_token
        if _TOKEN_RE.fullmatch(identity.boot_token) is not None
        else _UNKNOWN_BOOT
    )
    namespace = (
        identity.pid_namespace_token
        if _TOKEN_RE.fullmatch(identity.pid_namespace_token) is not None
        else _UNKNOWN_PID_NAMESPACE
    )
    pid = int(identity.pid)
    if pid <= 0:
        raise ValueError("temp owner pid must be a positive integer")
    start = int(identity.start_ticks) if int(identity.start_ticks) > 0 else 0
    suffix = (
        f".micromax-v3-b{boot}-n{namespace}-p{pid}-s{start}-"
        f"l{lease}-r{random_part}.tmp"
    )
    name_max = _name_max(Path(parent))
    fixed_bytes = len(os.fsencode("." + suffix))
    if fixed_bytes + 1 > name_max:
        raise OSError(
            errno.ENAMETOOLONG,
            "directory NAME_MAX cannot represent private save-temp identity",
            str(parent),
        )
    available = name_max - fixed_bytes
    safe = _truncate_component(_safe_basename(basename), max(1, available))
    result = f".{safe}{suffix}"
    if len(os.fsencode(result)) > name_max:
        raise OSError(
            errno.ENAMETOOLONG,
            "private save-temp name exceeds directory NAME_MAX",
            str(parent),
        )
    return result



def parse_private_temp_name(name: str) -> PrivateTempName | None:
    raw = str(name)
    if not raw or os.sep in raw or (os.altsep and os.altsep in raw):
        return None
    match = _TEMP_V3_RE.fullmatch(raw)
    namespace = _UNKNOWN_PID_NAMESPACE
    if match is not None:
        namespace = str(match.group("namespace"))
    else:
        # Parse the unreleased v2 grammar defensively, but never treat it as
        # cleanup proof: it omitted the PID namespace that gives a numeric PID
        # meaning on a shared container volume.
        match = _TEMP_V2_RE.fullmatch(raw)
    if match is None:
        return None
    prefix = str(match.group("prefix"))
    safe = prefix[1:]
    try:
        pid = int(match.group("pid"))
        start = int(match.group("start"))
    except ValueError:
        return None
    owner = ProcessIdentity(
        boot_token=str(match.group("boot")),
        pid=pid,
        start_ticks=start,
        pid_namespace_token=namespace,
    )
    return PrivateTempName(
        name=raw,
        safe_basename=safe,
        owner=owner,
        lease_id=str(match.group("lease")),
        random_token=str(match.group("random")),
    )

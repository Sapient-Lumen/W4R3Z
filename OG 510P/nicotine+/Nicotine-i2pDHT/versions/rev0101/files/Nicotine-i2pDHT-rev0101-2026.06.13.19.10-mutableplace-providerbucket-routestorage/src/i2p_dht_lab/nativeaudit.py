"""rev0083 source audit for tiny GCC-native leaves.

This is deliberately a small textual guard, not a C verifier.  It catches the
class of drift this cube most wants to forbid at the native boundary: turning a
leaf comparator into an allocation, I/O, process, or network surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

NATIVE_AUDIT_DOMAIN = DOMAIN + b":native-source-audit-v1:"

DANGEROUS_TOKENS = (
    "malloc", "calloc", "realloc", "free", "fopen", "fprintf", "printf", "socket", "connect(",
    "send(", "recv(", "system(", "exec", "popen", "pthread", "fork(", "mmap", "dlopen",
)


class NativeSourceAuditDecisionKind(str, Enum):
    ACCEPT_LEAF_SOURCE = "accept_leaf_source"
    QUARANTINE_DANGEROUS_TOKEN = "quarantine_dangerous_token"
    QUARANTINE_MISSING_SYMBOL = "quarantine_missing_symbol"
    QUARANTINE_SOURCE_TOO_LARGE = "quarantine_source_too_large"
    HOLD_MISSING_VERSION_COMMENT = "hold_missing_version_comment"


@dataclass(frozen=True)
class NativeSourceAuditReport:
    decision_kind: NativeSourceAuditDecisionKind
    accepted: bool
    watch: bool
    source_digest: bytes
    byte_count: int
    found_symbols: tuple[str, ...]
    dangerous_tokens: tuple[str, ...]
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_AUDIT_DOMAIN + b":report:" + bencode({
            b"decision": NativeSourceAuditDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"watch": 1 if self.watch else 0,
            b"source": self.source_digest,
            b"bytes": self.byte_count,
            b"symbols": list(self.found_symbols),
            b"danger": list(self.dangerous_tokens),
            b"obligations": list(self.obligations),
        }))


def audit_native_leaf_source(source_text: str, *, required_symbols: tuple[str, ...], max_bytes: int = 8192, require_version_comment: bool = True) -> NativeSourceAuditReport:
    encoded = source_text.encode("utf-8")
    source_digest = sha256(encoded)
    found_symbols = tuple(symbol for symbol in required_symbols if symbol in source_text)
    dangerous = tuple(token for token in DANGEROUS_TOKENS if token in source_text)

    if len(encoded) > max_bytes:
        return NativeSourceAuditReport(NativeSourceAuditDecisionKind.QUARANTINE_SOURCE_TOO_LARGE, False, False, source_digest, len(encoded), found_symbols, dangerous, ("native-leaf-source-too-large", "manual-review-required"))
    if dangerous:
        return NativeSourceAuditReport(NativeSourceAuditDecisionKind.QUARANTINE_DANGEROUS_TOKEN, False, False, source_digest, len(encoded), found_symbols, dangerous, ("remove-side-effect-token", "keep-native-leaf-pure"))
    missing = tuple(symbol for symbol in required_symbols if symbol not in found_symbols)
    if missing:
        return NativeSourceAuditReport(NativeSourceAuditDecisionKind.QUARANTINE_MISSING_SYMBOL, False, False, source_digest, len(encoded), found_symbols, dangerous, tuple("missing-symbol:" + symbol for symbol in missing))
    if require_version_comment and "i2pdht" not in source_text:
        return NativeSourceAuditReport(NativeSourceAuditDecisionKind.HOLD_MISSING_VERSION_COMMENT, False, True, source_digest, len(encoded), found_symbols, dangerous, ("add-versioned-native-boundary-comment",))
    return NativeSourceAuditReport(NativeSourceAuditDecisionKind.ACCEPT_LEAF_SOURCE, True, False, source_digest, len(encoded), found_symbols, dangerous, ("keep-source-audit-in-ci", "no-io-no-heap-no-network"))
